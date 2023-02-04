"""! @brief Walk all files recursively under a directory."""

##
# @file walk.py
#
# @brief Defines the function walk all files recursively under a directory.
#
# @section description_walk Description
# Defines the function walk all files recursively under a directory.
# - walk
#
# @section libraries_walk Libraries/Modules
# - None.
#
# @section notes_walk Notes
# - Comments are Doxygen compatible.
#
# @section todo_walk TODO
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

from os import listdir;
from os.path import isdir, join, normpath, abspath;

from re import match;

from tree.utils import get_file, is_path_include;

def walk(root, ignore="^$", follow_link:set=set(), need:set=set()):
    """! Walk all files recursively under a directory.
    
    @param  root    A `str`, indicate the path to the directory to walk.
    @param  ignore  A `str`, regular expression indicate which full path should be ignore.
    @param  follow_link A `set`, can contain `'sym'` or `'hard'`, default is empty.
    @param  need    A `set`, see `tree.utils.get_file` for details, default is empty.

    @note   

    @retun  A `list` contain files recursively, children of each directory is in its `'child`` item.
    """

    def push_work(work:list, pchild:list, ppath:str, name:str):
        path = join(ppath, name);
        if (match(ignore, normpath(path))):
            return;
        info = get_file(path, need.union({"lnk"}));

        if (((("slnk" in info["fmt_set"]) and ("sym" in follow_link)) or (("hlnk" in info["fmt_set"]) and ("hard" in follow_link))) and \
            (info["lnk_info"]["status"] == "success") and \
                (("dir" in info["fmt_set"]) or isdir(info["lnk_info"]["abspaths"][-1]))):
            # link and follow link && \
            # not broken or loop && \
            # is directory or link to directory(for hard link in WinNT) && \
            if (not is_path_include(abspath(ppath), info["lnk_info"]["abspaths"][-1])):
                # not recursive
                info["child"] = [];
                work.append((info["child"], path));
            else:
                info["flags"] = info.get("flags", set()).union("recur");
        elif (("lnk" not in info["fmt_set"]) and ("dir" in info["fmt_set"])):
            # regular directory
            info["child"] = [];
            work.append((info["child"], path));
        else:
            # other link or non-directory
            pass;
        # add files
        if ("lnk" not in need):
            info.pop("lnk_info", None);
        pchild.append(info);
        return;

    # process first file
    all = [];
    works = [];

    push_work(works, all, "", normpath(root));

    while (len(works)):
        pchild, ppath = works.pop();
        files = listdir(ppath);
        for file in files:
            push_work(works, pchild, ppath, file);
    return all;
