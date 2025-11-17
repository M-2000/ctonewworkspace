library bridge;

import 'dart:ffi' as ffi;
import 'dart:io' show Platform;
import 'package:ffi/ffi.dart';

typedef CoreVersionNative = ffi.Pointer<ffi.Char> Function();
typedef CoreVersionDart = ffi.Pointer<ffi.Char> Function();

typedef FreeStringNative = ffi.Void Function(ffi.Pointer<ffi.Char>);
typedef FreeStringDart = void Function(ffi.Pointer<ffi.Char>);

class CoreLib {
  static final ffi.DynamicLibrary _dylib = _loadLibrary();

  static ffi.DynamicLibrary _loadLibrary() {
    if (Platform.isAndroid) {
      return ffi.DynamicLibrary.open('libcore.so');
    } else if (Platform.isWindows) {
      return ffi.DynamicLibrary.open('core.dll');
    } else if (Platform.isLinux) {
      return ffi.DynamicLibrary.open('libcore.so');
    } else if (Platform.isMacOS) {
      return ffi.DynamicLibrary.open('libcore.dylib');
    } else {
      throw UnsupportedError('Unsupported platform');
    }
  }

  static final CoreVersionDart _coreVersion = _dylib
      .lookup<ffi.NativeFunction<CoreVersionNative>>('core_version')
      .asFunction<CoreVersionDart>();

  static final FreeStringDart _freeString = _dylib
      .lookup<ffi.NativeFunction<FreeStringNative>>('free_string')
      .asFunction<FreeStringDart>();

  static String coreVersion() {
    final resultPtr = _coreVersion();

    if (resultPtr == ffi.nullptr) {
      throw Exception('Failed to call core_version');
    }

    final result = resultPtr.cast<ffi.Utf8>().toDartString();

    _freeString(resultPtr);

    return result;
  }
}

String coreVersion() => CoreLib.coreVersion();
