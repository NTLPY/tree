"""! @brief Utils for file processing."""

##
# @file utils.py
#
# @brief Defines the utils for file processing.
#
# @section description_utils Description
# Defines the utils for file processing.
# - get_file_type
#
# @section libraries_utils Libraries/Modules
# - None.
#
# @section notes_utils Notes
# - Comments are Doxygen compatible.
#
# @section todo_utils TODO
# - None.
#
# @section author_sensors Author(s)
# - Created by NTLPY on 02/03/2023.
#
#    Copyright 2023 NTLPY, https://github.com/NTLPY.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

# Imports.
from os import stat, readlink;
from os.path import normpath, join, dirname, abspath, basename, commonpath;
from stat import S_IMODE, S_IFMT, S_ISDIR, S_ISCHR, S_ISBLK, S_ISREG, S_ISFIFO, S_ISLNK, S_ISSOCK, S_ISDOOR, S_ISPORT, S_ISWHT;

def is_path_include(path1:str, path2:str) -> bool:
    """! Determine whether `path2` included in `path1`.

    @param  path1   A path-like.
    @param  path2   A path-like.

    @TODO Only for abspath, better solution?

    @return A `bool`.
    """
    return commonpath([path1, path2]) == path1;


def get_file_identifier(path:str, follow_symlinks=True) -> tuple:
    """! Get inode number and device number by stat.
    
    @param  path    A path-like, path of file to determined.
    @param  follow_symlinks A `bool`, pass to `os.stat`.

    @note   Exception see `os.stat`.
    
    @return A `tuple` of inode number and device number.
    """

    st = stat(path, follow_symlinks=follow_symlinks);
    return (st.st_ino, st.st_dev);

def track_link(path:str):
    """! Recursive version of `os.readlink`.
    
    @param  path    A path-like, path of file to determined.

    @note   Exception see `tree.utils.get_file_identifier`.
    
    @return A `dict`, item `'abspaths'` is a `list` of all absolute paths, item `'relpaths'` is a `list` of all relative paths, item `'path'` is path to target and item `'status'` indicate whether exists a loop (`'loop'`) or a corrupted link (`'broken'`). 
    """
    
    abspaths, relpaths = [], [];
    status = "success";

    visited = set();
    path = normpath(path);  relpaths.append(path);
    absp = abspath(path);   abspaths.append(absp);
    visited.add(get_file_identifier(absp, follow_symlinks=False));

    while True:
        try:
            tar = readlink(absp);
        except:
            # search over
            break;
        path = join(dirname(path), tar);
        absp = join(dirname(absp), tar);

        abspaths.append(absp);
        relpaths.append(path);

        ## detect loop
        try:
            id = get_file_identifier(absp, follow_symlinks=False);
        except:
            # broken link
            status = "broken";
            break;
        if (id in visited):
            # visited, a loop found
            status = "loop";
            break;
        visited.add(id);

    return {
        "abspaths"  : abspaths,
        "relpaths"  : relpaths,
        "status"    : status
    };

def is_link_from_track_link(link_info:dict):
    """! Determine a file is link from result of `track_link`.

    @param  link_info   A `dict`, result from call of `track_link`.

    @return A `bool`.
    """

    return not ((link_info["status"] == "success") and (len(link_info["abspaths"]) == 1));

def get_file(path:str, need=set()):
    """! Get the info of file.
    
    @param  path    A path-like, path of file to determined.
    @param  need    A `set`, can contain `'size'`, `'mod'`, `'fs'`, `'own'`, `'time'`, `'lnk'` determine the output info, default is empty.
    
    @return A `dict` contain stat info.
    """
    
    st = stat(path, follow_symlinks=False);

    info = {
        "name"  : basename(normpath(path)),
        "fmt"   : S_IFMT(st.st_mode),
        "fmt_set" : set()
    }

    if ("size" in need):
        info["size"] = st.st_size;
    if ("mod" in need):
        info["mod"] = S_IMODE(st.st_mode);
    if ("fs" in need):
        info["ino"], info["dev"], info["nlink"] = st.st_ino, st.st_dev, st.st_nlink;
    if ("own" in need):
        info["uid"], info["gid"] = st.st_uid, st.st_gid;
    if ("time" in need):
        info["atime"], info["mtime"], info["ctime"] = st.st_atime, st.st_mtime, st.st_ctime;
        info["atime_ns"], info["mtime_ns"], info["ctime_ns"] = st.st_atime_ns, st.st_mtime_ns, st.st_ctime_ns;



    if (S_ISDIR(st.st_mode)):
        # ? directory
        info["fmt_set"].add("dir");
    if (S_ISCHR(st.st_mode)):
        # ? character special device file
        info["fmt_set"].add("chr");
    if (S_ISBLK(st.st_mode)):
        # ? block special device file
        info["fmt_set"].add("blk");
    if (S_ISREG(st.st_mode)):
        # ? regular
        info["fmt_set"].add("reg");
    if (S_ISFIFO(st.st_mode)):
        # ? fifo (named pipe)
        info["fmt_set"].add("fifo");
    if (S_ISSOCK(st.st_mode)):
        # ? socket
        info["fmt_set"].add("sock");
    
    if (S_ISDOOR(st.st_mode)):
        # ? door
        info["fmt_set"].add("door");
    if (S_ISPORT(st.st_mode)):
        # ? event port
        info["fmt_set"].add("port");
    if (S_ISWHT(st.st_mode)):
        # ? whiteout
        info["fmt_set"].add("wht");
    
    # check if a hardlink in WinNT
    if ("lnk" in need):
        lnk_info = track_link(path);
        if (is_link_from_track_link(lnk_info)):
            info["lnk_info"] = lnk_info;
            # link
            info["fmt_set"].add("lnk");
            # sym link or a hard link
            info["fmt_set"].add("slnk" if S_ISLNK(st.st_mode) else "hlnk");
    else:
        link = True;
        try:
            readlink(path);
        except:
            link = False;
        if (link):
            info["fmt_set"].add("lnk");
            info["fmt_set"].add("slnk" if S_ISLNK(st.st_mode) else "hlnk");

    return info;

if __name__ == "__main__":
    print(track_link("sltar"));

    print(get_file("hltar"));
