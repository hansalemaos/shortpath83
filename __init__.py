import ctypes
import itertools
import os
import pathlib
import platform
import re
from functools import cache

iswindows = "win" in platform.platform().lower()
if iswindows:
    from ctypes import wintypes

    windll = ctypes.LibraryLoader(ctypes.WinDLL)
    user32 = windll.user32
    kernel32 = windll.kernel32

    GetWindowRect = user32.GetWindowRect
    GetClientRect = user32.GetClientRect
    _GetShortPathNameW = kernel32.GetShortPathNameW
    _GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
    _GetShortPathNameW.restype = wintypes.DWORD
forbiddennames = r"""(?:CON|PRN|AUX|NUL|COM0|COM1|COM2|COM3|COM4|COM5|COM6|COM7|COM8|COM9|LPT0|LPT1|LPT2|LPT3|LPT4|LPT5|LPT6|LPT7|LPT8|LPT9)"""
compregex = re.compile(rf"(^.*?\\?)?\b{forbiddennames}\b(\.?[^\\]*$)?", flags=re.I)
forbiddenchars = {"<", ">", ":", '"', "|", "?", "*"}
allcontrols_s = {
    "\x00",
    "\x01",
    "\x02",
    "\x03",
    "\x04",
    "\x05",
    "\x06",
    "\x07",
    "\x08",
    "\x09",
    "\x0a",
    "\x0b",
    "\x0c",
    "\x0d",
    "\x0e",
    "\x0f",
    "\x10",
    "\x11",
    "\x12",
    "\x13",
    "\x14",
    "\x15",
    "\x16",
    "\x17",
    "\x18",
    "\x19",
    "\x1a",
    "\x1b",
    "\x1c",
    "\x1d",
    "\x1e",
    "\x1f",
}


@cache
def inforbidden(x):
    return x in forbiddenchars or x in allcontrols_s


def check_if_space(text):
    def tw(x):
        return x == " "

    left = len(list(itertools.takewhile(tw, text)))
    right = len(list(itertools.takewhile(tw, list(reversed(text)))))
    return left, right


def convert_path_in_string(t, minlen=None, convert_to_abs_path=True):
    r"""
    Convert file and directory paths within a string to their short (8.3) path names on Windows.

    This function processes a string containing file and directory paths and replaces them with their short (8.3) path
    names if running on a Windows system.
    It can also convert paths to absolute paths if specified. Non-Windows platforms will leave the input string unchanged.

    Parameters:
    t (str): The input string containing file and directory paths.
    minlen (int): The minimum length for a valid path component. If not specified, it is automatically determined.
    convert_to_abs_path (bool): Whether to convert paths to absolute paths. Defaults to True.

    Returns:
    str: The input string with file and directory paths replaced by their short (8.3) path names on Windows, or the input
    string itself on other platforms.

    Examples:
        print(convert_path_in_string(r"C:\Users\hansc\Downloads\RobloxPlayerLauncher (2).exe --somearg --another arg --somefile C:\Users\hansc\Downloads\1633513733_526_Roblox-Royale-High-Halloween-이벤트에서-사탕을-얻는-방법 (4).jpg --some_not_existing_file=c:\idontexistsandwontbeconverted", minlen=None, convert_to_abs_path=True))
        C:\Users\hansc\DOWNLO~1\ROBLOX~3.EXE --somearg --another arg --somefile C:\Users\hansc\DOWNLO~1\164186~1.JPG --some_not_existing_file=c:\idontexistsandwontbeconverted
    """
    if not iswindows:
        return t
    wholestring = t
    if not minlen:
        minlen = (
            len(
                sorted(
                    [
                        x
                        for x in re.split(r"[\\/]+", t)
                        if not (g := set(x)).intersection(allcontrols_s)
                        and not g.intersection(forbiddenchars)
                        and not compregex.match(x)
                    ],
                    key=lambda q: len(q),
                )[0]
            )
            + 1
        )

    def _get_path_from_string(lis):
        allresults = []
        lastin = 0
        templist = lis.copy()
        abscounter = 0
        while True:
            somethinfound = False
            lastpath = ""
            for la in range(0, len(templist)):
                for q in range(1, len(templist) + 1):
                    if q - la < minlen:
                        continue
                    joix = templist[la:q]

                    if "\\" not in joix and "/" not in joix:
                        continue

                    joi = "".join(joix)
                    if os.path.exists(joi):
                        lastpath = joi
                        lastin = q
                        somethinfound = True
                    if lastpath:
                        if inforbidden(joi[-1]):
                            break

                if lastpath:
                    templist = templist[lastin:]
                    allresults.append(
                        (
                            lastin - len(lastpath) + abscounter,
                            lastin + abscounter,
                            lastpath,
                        )
                    )
                    abscounter = lastin + abscounter
                    lastin = 0
                    break
            if not somethinfound:
                break

        return allresults

    lis = list(t)
    laazx = _get_path_from_string(lis)
    allres = []
    wholestringnew = []
    ini = 0
    lastindi = 0
    for s, e, text in laazx:
        sta, end = check_if_space(text)
        endx = end * " "
        s += sta
        e -= end

        longname = wholestring[s:e]
        if convert_to_abs_path:
            if ":" not in longname:
                p = pathlib.Path(longname)
                longname = p.resolve()
                longname = os.path.normpath(longname)
        shortname = get_short_path_name(longname)
        shortname = os.path.normpath(shortname)
        wholestringnew.append(wholestring[lastindi:s])
        wholestringnew.append(shortname)
        wholestringnew.append(endx)

        lastindi = e + end
        if ini == len(laazx) - 1:
            wholestringnew.append(wholestring[lastindi:])
        ini += 1
        kind = ""
        if os.path.ismount(shortname):
            kind = "mount"
        elif os.path.isfile(shortname):
            kind = "file"
        elif os.path.isdir(shortname):
            kind = "dir"
        elif os.path.islink(shortname):
            kind = "link"
        allres.append([s, e, longname, shortname, kind])
    return "".join(wholestringnew)  # , wholestringnew, allres


def get_short_path_name(long_name):
    r"""
    Get the short (8.3) path name of a given long file or directory path on Windows.

    This function takes a long file or directory path as input and returns its short (8.3) path name if running on a Windows system.
    If the input path is already in short format or the function is run on a non-Windows system, the input path is returned unchanged.

    Parameters:
    long_name (str): The long file or directory path to be converted to a short path name.

    Returns:
    str: The short (8.3) path name of the input path on Windows, or the input path itself on other platforms.

    print(get_short_path_name(long_name=r"C:\Users\hansc\Downloads\RobloxPlayerLauncher (2).exe"))
    C:\Users\hansc\DOWNLO~1\ROBLOX~3.EXE

    """
    if not iswindows:
        return long_name
    output_buf_size = 4096
    output_buf = ctypes.create_unicode_buffer(output_buf_size)
    _ = _GetShortPathNameW(long_name, output_buf, output_buf_size)
    return output_buf.value
