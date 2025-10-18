library bridge;

import 'dart:ffi' as ffi;
import 'dart:io' show Platform;
import 'package:ffi/ffi.dart';

typedef GreetNative = ffi.Pointer<ffi.Char> Function(ffi.Pointer<ffi.Char>);
typedef GreetDart = ffi.Pointer<ffi.Char> Function(ffi.Pointer<ffi.Char>);

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

  static final GreetDart _greet = _dylib
      .lookup<ffi.NativeFunction<GreetNative>>('greet')
      .asFunction<GreetDart>();

  static final FreeStringDart _freeString = _dylib
      .lookup<ffi.NativeFunction<FreeStringNative>>('free_string')
      .asFunction<FreeStringDart>();

  static String greet(String name) {
    final namePtr = name.toNativeUtf8().cast<ffi.Char>();
    final resultPtr = _greet(namePtr);
    
    if (resultPtr == ffi.nullptr) {
      malloc.free(namePtr);
      throw Exception('Failed to call greet');
    }

    final result = resultPtr.cast<Utf8>().toDartString();
    
    _freeString(resultPtr);
    malloc.free(namePtr);
    
    return result;
  }
}

String greet(String name) {
  return CoreLib.greet(name);
}
