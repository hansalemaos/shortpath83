# simplifies Windows path handling, providing short path name conversion and string path manipulation.

## Tested against Windows 10 / Python 3.10 / Anaconda

## pip install shortpath83

## About

The provided Python library is focused on working with file and directory paths on Windows systems. 
It primarily offers two functions, get_short_path_name and convert_path_in_string, 
which help manage and manipulate file paths. 
While the library focuses on Windows path management, it also considers compatibility with non-Windows systems. 
It doesn't modify paths on non-Windows platforms, making it versatile for cross-platform development.


Here's a description of what the library is doing and the potential advantages it offers:

## get_short_path_name Function:

Purpose: This function takes a long file or directory path as input and returns its short (8.3) path name on Windows systems.

#### Advantages:

- Compatibility: It ensures compatibility with older Windows systems that use short path names for compatibility with legacy software.
- Uniformity: Provides a standardized way to obtain short path names, which can be useful when working with mixed path formats.
- Path Validation: The function checks if the input path is already in short format and only converts long paths if necessary.


## convert_path_in_string Function:

Purpose: This function processes a string containing file and directory paths and replaces them with their short (8.3) path names on Windows systems.

#### Advantages:

- String Manipulation: Allows you to efficiently manipulate strings containing paths by converting them to short names while preserving the original string's structure.
- Flexibility: You can specify whether to convert paths to absolute paths, providing flexibility in how paths are represented in the output.
- Automatic Path Detection: Automatically identifies valid paths within the input string, ensuring that only paths are converted.


```python

from shortpath83 import get_short_path_name, convert_path_in_string
print(get_short_path_name(long_name=r"C:\Users\hansc\Downloads\RobloxPlayerLauncher (2).exe"))
print(convert_path_in_string(r"C:\Users\hansc\Downloads\RobloxPlayerLauncher (2).exe --somearg --another arg --somefile C:\Users\hansc\Downloads\1633513733_526_Roblox-Royale-High-Halloween-이벤트에서-사탕을-얻는-방법 (4).jpg --some_not_existing_file=c:\idontexistsandwontbeconverted", minlen=None, convert_to_abs_path=True))
C:\Users\hansc\DOWNLO~1\ROBLOX~3.EXE
C:\Users\hansc\DOWNLO~1\ROBLOX~3.EXE --somearg --another arg --somefile C:\Users\hansc\DOWNLO~1\164186~1.JPG --some_not_existing_file=c:\idontexistsandwontbeconverted

```