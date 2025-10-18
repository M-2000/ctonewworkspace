#ifndef RUNNER_RUN_LOOP_H_
#define RUNNER_RUN_LOOP_H_

#include <windows.h>

class RunLoop {
 public:
  RunLoop();
  ~RunLoop();

  void Run();

  void RegisterFlutterInstance(flutter::FlutterEngine* flutter_instance);

  void UnregisterFlutterInstance(flutter::FlutterEngine* flutter_instance);

 private:
};

#endif  // RUNNER_RUN_LOOP_H_
