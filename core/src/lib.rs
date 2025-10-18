use std::ffi::{CStr, CString};
use std::os::raw::c_char;

#[no_mangle]
pub extern "C" fn greet(name: *const c_char) -> *mut c_char {
    let name = unsafe {
        if name.is_null() {
            return std::ptr::null_mut();
        }
        CStr::from_ptr(name)
    };

    let name_str = match name.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(),
    };

    let greeting = format!("Hello, {} from Rust!", name_str);
    
    match CString::new(greeting) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => std::ptr::null_mut(),
    }
}

#[no_mangle]
pub extern "C" fn free_string(s: *mut c_char) {
    if !s.is_null() {
        unsafe {
            let _ = CString::from_raw(s);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::ffi::CString;

    #[test]
    fn test_greet() {
        let name = CString::new("World").unwrap();
        let result_ptr = greet(name.as_ptr());
        
        assert!(!result_ptr.is_null());
        
        let result = unsafe { CStr::from_ptr(result_ptr) };
        assert_eq!(result.to_str().unwrap(), "Hello, World from Rust!");
        
        free_string(result_ptr);
    }
}
