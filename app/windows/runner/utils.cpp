#include "utils.h"

#include <windows.h>
#include <shellapi.h>

std::vector<std::string> GetCommandLineArguments() {
  int argc;
  wchar_t** argv = ::CommandLineToArgvW(::GetCommandLineW(), &argc);
  if (argv == nullptr) {
    return std::vector<std::string>();
  }

  std::vector<std::string> command_line_arguments;
  for (int i = 1; i < argc; i++) {
    std::wstring wide_arg(argv[i]);
    int size = ::WideCharToMultiByte(CP_UTF8, 0, wide_arg.c_str(),
                                      wide_arg.size(), nullptr, 0, nullptr,
                                      nullptr);
    std::string utf8_arg(size, '\0');
    ::WideCharToMultiByte(CP_UTF8, 0, wide_arg.c_str(), wide_arg.size(),
                          &utf8_arg[0], size, nullptr, nullptr);
    command_line_arguments.push_back(utf8_arg);
  }

  ::LocalFree(argv);

  return command_line_arguments;
}

std::wstring Utf8ToWideString(const std::string& utf8_string) {
  if (utf8_string.empty()) {
    return std::wstring();
  }
  int size = ::MultiByteToWideChar(CP_UTF8, 0, utf8_string.c_str(),
                                    utf8_string.size(), nullptr, 0);
  std::wstring wide_string(size, L'\0');
  ::MultiByteToWideChar(CP_UTF8, 0, utf8_string.c_str(), utf8_string.size(),
                        &wide_string[0], size);
  return wide_string;
}
