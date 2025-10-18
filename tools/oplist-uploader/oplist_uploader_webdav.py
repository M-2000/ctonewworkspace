#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebDAV Incremental Uploader with Safe Archive/Delete

Features
- Recursively scan source_dir, preserve remote hierarchy under dest_root
- Upload only new files; re-upload and overwrite if content at same path changed
- Fingerprints: size+mtime (default) or sha256
- State JSON tracks last uploaded fingerprint per relative path and optional history
- On successful upload, archive (default) or delete local file
- Archive retention cleanup (retention_days)
- Cleanup of previously uploaded files that still remain in original location
- Optional deletion of empty directories after move/delete
- WebDAV: MKCOL per directory level (405/409 treated as exists), PUT for upload
- Auth: basic or bearer token; verify_ssl; concurrency; retries w/ exponential backoff
- Logging to file and console

Usage
  python3 oplist_uploader_webdav.py --config /path/to/oplist_uploader_webdav.yaml

Config file (YAML or JSON)
  See tools/oplist-uploader/oplist_uploader_webdav.yaml for a full example.

Notes
- Requires the 'requests' package. If not available, install via: pip install requests
- YAML loading requires PyYAML. If not available, provide a JSON config or install via: pip install pyyaml
"""
from __future__ import annotations

import argparse
import concurrent.futures
import dataclasses
import fnmatch
import hashlib
import json
import logging
import os
import shutil
import sys
import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from urllib.parse import quote

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None  # Fallback to JSON if YAML not installed

try:
    import requests
    from requests.auth import HTTPBasicAuth
except Exception as e:  # pragma: no cover
    print("ERROR: 'requests' package is required. Install with: pip install requests", file=sys.stderr)
    raise


ISO8601 = "%Y-%m-%dT%H:%M:%S%z"


@dataclasses.dataclass
class Fingerprint:
    size: int
    mtime: float
    sha256: Optional[str] = None
    method: str = "size_mtime"  # or "sha256"

    @staticmethod
    def from_file(path: Path, method: str = "size_mtime") -> "Fingerprint":
        st = path.stat()
        if method == "sha256":
            h = hashlib.sha256()
            with path.open("rb") as f:
                for chunk in iter(lambda: f.read(1024 * 1024), b""):
                    h.update(chunk)
            return Fingerprint(size=st.st_size, mtime=st.st_mtime, sha256=h.hexdigest(), method="sha256")
        else:
            return Fingerprint(size=st.st_size, mtime=st.st_mtime, sha256=None, method="size_mtime")

    def to_dict(self) -> Dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class FileRecord:
    fingerprint: Fingerprint
    uploaded_at: str
    history: List[Dict]

    def to_dict(self) -> Dict:
        return {
            "fingerprint": self.fingerprint.to_dict(),
            "uploaded_at": self.uploaded_at,
            "history": list(self.history or []),
        }


@dataclasses.dataclass
class Config:
    source_dir: Path
    dest_root: str
    webdav_base_url: str
    auth_type: str = "basic"  # or "bearer"
    username: Optional[str] = None
    password: Optional[str] = None
    bearer_token: Optional[str] = None
    verify_ssl: bool = True
    state_file: Path = Path("")
    log_file: Optional[Path] = None
    concurrency: int = 4
    retries: int = 3
    retry_backoff_seconds: float = 1.0
    timeout_seconds: float = 30.0
    include_globs: List[str] = dataclasses.field(default_factory=lambda: ["**/*"])  # files only later
    exclude_globs: List[str] = dataclasses.field(default_factory=lambda: [])
    delete_mode: str = "archive"  # or "delete"
    archive_dir: Optional[Path] = None
    retention_days: int = 30
    clean_empty_dirs: bool = True
    fingerprint: str = "size_mtime"  # or "sha256"
    history_keep: int = 5  # keep last N history entries

    @staticmethod
    def from_dict(d: Dict) -> "Config":
        source_dir = Path(d["source_dir"]).expanduser().resolve()
        archive_dir = d.get("archive_dir")
        if not archive_dir:
            archive_dir = str(source_dir / ".oplist_archive")
        cfg = Config(
            source_dir=source_dir,
            dest_root=str(d["dest_root"]),
            webdav_base_url=str(d["webdav_base_url"]).rstrip("/"),
            auth_type=str(d.get("auth_type", "basic")).lower(),
            username=d.get("username"),
            password=d.get("password"),
            bearer_token=d.get("bearer_token"),
            verify_ssl=bool(d.get("verify_ssl", True)),
            state_file=Path(d.get("state_file") or (source_dir / ".oplist_state.json")).expanduser().resolve(),
            log_file=Path(d["log_file"]).expanduser().resolve() if d.get("log_file") else None,
            concurrency=int(d.get("concurrency", 4)),
            retries=int(d.get("retries", 3)),
            retry_backoff_seconds=float(d.get("retry_backoff_seconds", 1.0)),
            timeout_seconds=float(d.get("timeout_seconds", d.get("timeout", 30.0))),
            include_globs=list(d.get("include_globs", ["**/*"])),
            exclude_globs=list(d.get("exclude_globs", [])),
            delete_mode=str(d.get("delete_mode", "archive")).lower(),
            archive_dir=Path(archive_dir).expanduser().resolve() if archive_dir else None,
            retention_days=int(d.get("retention_days", 30)),
            clean_empty_dirs=bool(d.get("clean_empty_dirs", True)),
            fingerprint=str(d.get("fingerprint", "size_mtime")).lower(),
            history_keep=int(d.get("history_keep", 5)),
        )
        if cfg.delete_mode not in ("archive", "delete"):
            raise ValueError("delete_mode must be 'archive' or 'delete'")
        if cfg.fingerprint not in ("size_mtime", "sha256"):
            raise ValueError("fingerprint must be 'size_mtime' or 'sha256'")
        return cfg


class StateStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = threading.Lock()
        self.data: Dict[str, Dict] = {}
        self._loaded = False

    def load(self) -> None:
        if self._loaded:
            return
        if self.path.exists():
            try:
                with self.path.open("r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                logging.exception("Failed to load state file, starting with empty state: %s", self.path)
                self.data = {}
        else:
            self.data = {}
        self._loaded = True

    def save(self) -> None:
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        os.makedirs(self.path.parent, exist_ok=True)
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def get(self, rel_path: str) -> Optional[Dict]:
        return self.data.get(rel_path)

    def update_record(self, rel_path: str, new_fp: Fingerprint, uploaded_at: str, history_keep: int) -> None:
        with self._lock:
            rec = self.data.get(rel_path)
            history = list(rec.get("history", [])) if rec else []
            if rec:
                prev = {
                    "fingerprint": rec.get("fingerprint"),
                    "uploaded_at": rec.get("uploaded_at"),
                }
                if prev["fingerprint"] is not None and prev["uploaded_at"] is not None:
                    history.insert(0, prev)
            # trim
            if history_keep >= 0:
                history = history[:history_keep]
            self.data[rel_path] = FileRecord(fingerprint=new_fp, uploaded_at=uploaded_at, history=history).to_dict()


class WebDAVClient:
    def __init__(self, base_url: str, verify_ssl: bool, timeout_seconds: float, auth_type: str, username: Optional[str], password: Optional[str], bearer_token: Optional[str]):
        self.base_url = base_url.rstrip("/")
        self.verify_ssl = verify_ssl
        self.timeout_seconds = timeout_seconds
        self.auth_type = auth_type
        self.username = username
        self.password = password
        self.bearer_token = bearer_token

        self._session = requests.Session()
        if auth_type == "basic" and username:
            self._session.auth = HTTPBasicAuth(username, password or "")

    def _headers(self) -> Dict[str, str]:
        headers = {
            "User-Agent": "oplist-uploader/1.0",
        }
        if self.auth_type == "bearer" and self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        return headers

    @staticmethod
    def _quote_path_component(p: str) -> str:
        # quote each path segment but keep '/'
        if not p:
            return ""
        segs = p.split("/")
        return "/".join(quote(s, safe="") for s in segs if s != "")

    def _full_url(self, dest_root: str, rel_path: str) -> str:
        root = dest_root
        # ensure single slashes
        parts = [self.base_url]
        if not root.startswith("/"):
            root = "/" + root
        # encode root and rel path segments
        encoded_root = self._quote_path_component(root)
        encoded_rel = self._quote_path_component(rel_path)
        if encoded_root.startswith("/"):
            # base_url already without trailing slash
            parts.append(encoded_root)
        else:
            parts.append("/" + encoded_root)
        if encoded_rel:
            if not parts[-1].endswith("/"):
                parts.append("/")
            parts.append(encoded_rel)
        return "".join(parts)

    def ensure_dirs(self, dest_root: str, rel_path: str, retries: int, retry_backoff_seconds: float) -> bool:
        # create each directory level via MKCOL
        dir_path = os.path.dirname(rel_path).replace("\\", "/").strip("/")
        if not dir_path:
            return True
        segments = dir_path.split("/")
        path_so_far = ""
        for s in segments:
            path_so_far = f"{path_so_far}/{s}" if path_so_far else s
            url = self._full_url(dest_root, path_so_far)
            ok = self._mkcol_with_retries(url, retries, retry_backoff_seconds)
            if not ok:
                return False
        return True

    def _mkcol_with_retries(self, url: str, retries: int, backoff: float) -> bool:
        attempt = 0
        while True:
            try:
                resp = self._session.request("MKCOL", url, headers=self._headers(), verify=self.verify_ssl, timeout=self.timeout_seconds)
                if resp.status_code in (201, 405, 409):
                    return True
                if 200 <= resp.status_code < 300:
                    return True
                logging.warning("MKCOL failed (%s): %s", resp.status_code, url)
            except Exception:
                logging.exception("MKCOL exception for %s", url)
            attempt += 1
            if attempt > retries:
                return False
            sleep_s = backoff * (2 ** (attempt - 1))
            time.sleep(sleep_s)

    def put_file(self, dest_root: str, rel_path: str, local_path: Path, retries: int, retry_backoff_seconds: float) -> Tuple[bool, Optional[int]]:
        url = self._full_url(dest_root, rel_path)
        attempt = 0
        last_status = None
        while True:
            try:
                with local_path.open("rb") as f:
                    resp = self._session.put(url, data=f, headers=self._headers(), verify=self.verify_ssl, timeout=self.timeout_seconds)
                last_status = resp.status_code
                if 200 <= resp.status_code < 300:
                    return True, resp.status_code
                logging.warning("PUT failed (%s): %s", resp.status_code, url)
            except Exception:
                logging.exception("PUT exception for %s", url)
            attempt += 1
            if attempt > retries:
                return False, last_status
            sleep_s = retry_backoff_seconds * (2 ** (attempt - 1))
            time.sleep(sleep_s)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime(ISO8601)


def setup_logging(log_file: Optional[Path]) -> None:
    handlers: List[logging.Handler] = []
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    handlers.append(console)

    if log_file:
        os.makedirs(log_file.parent, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    logging.basicConfig(level=logging.INFO, handlers=handlers)


def load_config(config_path: Path) -> Config:
    with config_path.open("r", encoding="utf-8") as f:
        txt = f.read()
    data: Dict
    # try YAML first if available or if extension suggests yaml
    if yaml is not None:
        try:
            data = yaml.safe_load(txt)
            if not isinstance(data, dict):
                raise ValueError("Config file must define a mapping at the root")
        except Exception as e:
            # fallback to JSON
            try:
                data = json.loads(txt)
            except Exception:
                raise e
    else:
        data = json.loads(txt)
    return Config.from_dict(data)


def match_globs(rel_path: str, includes: List[str], excludes: List[str]) -> bool:
    # Normalize to POSIX style
    rp = rel_path.replace("\\", "/")
    included = False
    for pat in includes:
        if fnmatch.fnmatch(rp, pat):
            included = True
            break
    if not included:
        return False
    for pat in excludes:
        if fnmatch.fnmatch(rp, pat):
            return False
    return True


def iter_source_files(cfg: Config) -> Iterable[Tuple[str, Path]]:
    src = cfg.source_dir
    archive_dir = Path(cfg.archive_dir) if cfg.archive_dir else None

    for root, dirs, files in os.walk(src):
        root_path = Path(root)
        # skip archive_dir
        if archive_dir and archive_dir in (root_path, *[root_path / d for d in []]):
            pass
        # remove archive_dir from traversal if nested
        if archive_dir and archive_dir.is_dir():
            try:
                rel_arch = str(archive_dir.relative_to(root_path))
                # if the archive directory is directly under current root, skip descending into it
                if rel_arch in dirs:
                    dirs.remove(rel_arch)
            except Exception:
                # not relative
                pass
        for name in files:
            full = root_path / name
            try:
                rel = str(full.relative_to(src))
            except ValueError:
                continue
            # ignore state file and log file and files inside archive_dir
            if cfg.state_file and full == cfg.state_file:
                continue
            if cfg.log_file and full == cfg.log_file:
                continue
            if archive_dir and (archive_dir in full.parents or full == archive_dir):
                continue
            rel_posix = rel.replace("\\", "/")
            if match_globs(rel_posix, cfg.include_globs, cfg.exclude_globs):
                yield rel_posix, full


def ensure_remote_dirs(client: WebDAVClient, cfg: Config, rel_path: str) -> bool:
    return client.ensure_dirs(cfg.dest_root, rel_path, retries=cfg.retries, retry_backoff_seconds=cfg.retry_backoff_seconds)


def prune_empty_dirs(start_dir: Path, root_dir: Path) -> None:
    try:
        cur = start_dir
        while cur != root_dir and root_dir in cur.parents:
            if not any(cur.iterdir()):
                try:
                    cur.rmdir()
                except Exception:
                    break
            cur = cur.parent
    except Exception:
        logging.debug("Prune skipped for %s", start_dir)


@dataclasses.dataclass
class UploadTask:
    rel_path: str
    local_path: Path
    fingerprint: Fingerprint
    prior_record: Optional[Dict]
    action: str  # 'upload' or 'skip' or 'cleanup_only'


@dataclasses.dataclass
class Result:
    rel_path: str
    local_path: Path
    uploaded: bool
    status_code: Optional[int]
    fingerprint: Fingerprint
    error: Optional[str] = None


def plan_tasks(cfg: Config, state: StateStore) -> Tuple[List[UploadTask], List[Tuple[str, Path, Fingerprint]]]:
    tasks: List[UploadTask] = []
    residue_to_cleanup: List[Tuple[str, Path, Fingerprint]] = []

    for rel_path, full in iter_source_files(cfg):
        try:
            fp = Fingerprint.from_file(full, cfg.fingerprint)
        except Exception as e:
            logging.warning("Failed to fingerprint %s: %s", full, e)
            continue
        rec = state.get(rel_path)
        if rec is None:
            tasks.append(UploadTask(rel_path=rel_path, local_path=full, fingerprint=fp, prior_record=None, action="upload"))
        else:
            last_fp = rec.get("fingerprint", {})
            same = False
            if cfg.fingerprint == "sha256":
                same = (last_fp.get("sha256") == fp.sha256 and last_fp.get("size") == fp.size)
            else:
                # accept equality by size+mtime
                same = (last_fp.get("size") == fp.size and abs(float(last_fp.get("mtime", 0)) - fp.mtime) < 1e-6)
            if same:
                # Do not upload; but consider if this is a historical residue that remained
                tasks.append(UploadTask(rel_path=rel_path, local_path=full, fingerprint=fp, prior_record=rec, action="skip"))
                # We'll handle cleanup pass later
            else:
                tasks.append(UploadTask(rel_path=rel_path, local_path=full, fingerprint=fp, prior_record=rec, action="upload"))

    # Identify historical residue files to cleanup: files in source which match state and not being uploaded now
    # We treat all 'skip' tasks as residue candidates
    for t in tasks:
        if t.action == "skip" and t.prior_record is not None:
            residue_to_cleanup.append((t.rel_path, t.local_path, t.fingerprint))

    return tasks, residue_to_cleanup


def execute_upload_task(task: UploadTask, cfg: Config, client: WebDAVClient) -> Result:
    if task.action == "skip":
        return Result(rel_path=task.rel_path, local_path=task.local_path, uploaded=False, status_code=None, fingerprint=task.fingerprint)

    # Ensure remote dirs
    ok_dirs = ensure_remote_dirs(client, cfg, task.rel_path)
    if not ok_dirs:
        return Result(rel_path=task.rel_path, local_path=task.local_path, uploaded=False, status_code=None, fingerprint=task.fingerprint, error="MKCOL failed")

    ok_put, status = client.put_file(cfg.dest_root, task.rel_path, task.local_path, retries=cfg.retries, retry_backoff_seconds=cfg.retry_backoff_seconds)
    if not ok_put:
        return Result(rel_path=task.rel_path, local_path=task.local_path, uploaded=False, status_code=status, fingerprint=task.fingerprint, error=f"PUT failed: {status}")

    return Result(rel_path=task.rel_path, local_path=task.local_path, uploaded=True, status_code=status, fingerprint=task.fingerprint)


def archive_or_delete(path: Path, cfg: Config, source_root: Path) -> None:
    try:
        if cfg.delete_mode == "delete":
            orig_parent = path.parent
            try:
                path.unlink()
                logging.info("Deleted %s", path)
            except Exception as e:
                logging.warning("Failed to delete %s: %s", path, e)
            if cfg.clean_empty_dirs:
                prune_empty_dirs(orig_parent, source_root)
        else:
            # archive
            assert cfg.archive_dir is not None
            archive_root = Path(cfg.archive_dir)
            rel = path.relative_to(source_root)
            dest = archive_root / rel
            os.makedirs(dest.parent, exist_ok=True)
            try:
                shutil.move(str(path), str(dest))
                logging.info("Archived %s -> %s", path, dest)
            except Exception as e:
                logging.warning("Failed to archive %s -> %s: %s", path, dest, e)
            if cfg.clean_empty_dirs:
                prune_empty_dirs(dest.parent, archive_root)  # in case move created empty dir in archive? not needed
                prune_empty_dirs(path.parent, source_root)
    except Exception:
        logging.exception("archive_or_delete unexpected error for %s", path)


def cleanup_archive_retention(cfg: Config) -> None:
    if cfg.delete_mode == "delete":
        return
    if cfg.retention_days <= 0:
        return
    if not cfg.archive_dir:
        return
    cutoff = datetime.now(timezone.utc) - timedelta(days=cfg.retention_days)
    arc = Path(cfg.archive_dir)
    if not arc.exists():
        return
    for root, dirs, files in os.walk(arc, topdown=False):
        root_path = Path(root)
        for name in files:
            p = root_path / name
            try:
                st = p.stat()
                mtime = datetime.fromtimestamp(st.st_mtime, tz=timezone.utc)
                if mtime < cutoff:
                    try:
                        p.unlink()
                        logging.info("Retention: deleted %s", p)
                    except Exception as e:
                        logging.warning("Retention: failed to delete %s: %s", p, e)
            except Exception:
                continue
        # prune empty dirs
        if cfg.clean_empty_dirs:
            try:
                if not any((root_path / x).exists() for x in os.listdir(root_path)):
                    try:
                        root_path.rmdir()
                    except Exception:
                        pass
            except Exception:
                pass


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="WebDAV incremental uploader with safe archive/delete")
    parser.add_argument("--config", required=True, help="Path to YAML/JSON config file")
    args = parser.parse_args(argv)

    cfg = load_config(Path(args.config))

    # Setup logging
    setup_logging(cfg.log_file)

    logging.info("Starting WebDAV incremental uploader")

    # Prepare dirs
    os.makedirs(cfg.source_dir, exist_ok=True)
    if cfg.delete_mode == "archive" and cfg.archive_dir:
        os.makedirs(cfg.archive_dir, exist_ok=True)

    # Load state
    state = StateStore(cfg.state_file)
    state.load()

    # Plan tasks
    tasks, residue_to_cleanup = plan_tasks(cfg, state)

    # Execute uploads concurrently
    client = WebDAVClient(
        base_url=cfg.webdav_base_url,
        verify_ssl=cfg.verify_ssl,
        timeout_seconds=cfg.timeout_seconds,
        auth_type=cfg.auth_type,
        username=cfg.username,
        password=cfg.password,
        bearer_token=cfg.bearer_token,
    )

    upload_tasks = [t for t in tasks if t.action == "upload"]
    results: List[Result] = []
    if upload_tasks:
        with concurrent.futures.ThreadPoolExecutor(max_workers=cfg.concurrency) as executor:
            fut_to_task = {executor.submit(execute_upload_task, t, cfg, client): t for t in upload_tasks}
            for fut in concurrent.futures.as_completed(fut_to_task):
                res = fut.result()
                results.append(res)
                if res.uploaded:
                    # Update state
                    state.update_record(rel_path=res.rel_path, new_fp=res.fingerprint, uploaded_at=now_iso(), history_keep=cfg.history_keep)
                else:
                    if res.error:
                        logging.error("Upload failed for %s: %s", res.local_path, res.error)

    # Save state after successful uploads
    state.save()

    # Archive/Delete successfully uploaded files
    for res in results:
        if res.uploaded:
            archive_or_delete(res.local_path, cfg, cfg.source_dir)

    # Cleanup historical residue files left in place from prior runs (same fingerprint as recorded)
    for rel_path, full, fp in residue_to_cleanup:
        rec = state.get(rel_path)
        if not rec:
            continue
        last_fp = rec.get("fingerprint", {})
        if cfg.fingerprint == "sha256":
            same = (last_fp.get("sha256") == fp.sha256 and last_fp.get("size") == fp.size)
        else:
            same = (last_fp.get("size") == fp.size and abs(float(last_fp.get("mtime", 0)) - fp.mtime) < 1e-6)
        if same:
            # already uploaded before; safe to cleanup
            archive_or_delete(full, cfg, cfg.source_dir)

    # Archive retention cleanup
    try:
        cleanup_archive_retention(cfg)
    except Exception:
        logging.exception("Archive retention cleanup failed")

    logging.info("Done.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
