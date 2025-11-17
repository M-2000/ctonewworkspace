use std::ffi::CString;
use std::os::raw::c_char;

const CRATE_NAME: &str = env!("CARGO_PKG_NAME");
const CRATE_VERSION: &str = env!("CARGO_PKG_VERSION");

#[no_mangle]
pub extern "C" fn core_version() -> *mut c_char {
    let metadata = format!(
        r#"{{"crate_name":"{}","crate_version":"{}"}}"#,
        CRATE_NAME,
        CRATE_VERSION
    );

    match CString::new(metadata) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    if s.is_null() {
        return;
    }

    unsafe {
        let _ = CString::from_raw(s);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::CStr;

    #[test]
    fn core_version_returns_metadata() {
        let ptr = core_version();
        assert!(!ptr.is_null());

        let metadata = unsafe { CStr::from_ptr(ptr) }
            .to_str()
            .unwrap()
            .to_string();
        free_string(ptr);

        let expected = format!(
            r#"{{"crate_name":"{}","crate_version":"{}"}}"#,
            CRATE_NAME,
            CRATE_VERSION
        );

        assert_eq!(metadata, expected);
    }
}
