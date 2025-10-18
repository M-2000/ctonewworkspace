#include "run_loop.h"

#include <windows.h>

RunLoop::RunLoop() {}

RunLoop::~RunLoop() {}

void RunLoop::Run() {
  bool should_exit = false;
  while (!should_exit) {
    MSG message;
    BOOL got_message = ::GetMessage(&message, nullptr, 0, 0);
    if (got_message == -1) {
      should_exit = true;
    } else if (got_message == 0) {
      should_exit = true;
    } else {
      ::TranslateMessage(&message);
      ::DispatchMessage(&message);
    }
  }
}

void RunLoop::RegisterFlutterInstance(
    flutter::FlutterEngine* flutter_instance) {
}

void RunLoop::UnregisterFlutterInstance(
    flutter::FlutterEngine* flutter_instance) {
}
