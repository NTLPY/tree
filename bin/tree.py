#! /usr/bin/env python3

# Tree to markdown

from os import getcwd, listdir, readlink;
from os.path import abspath, isdir, isfile, islink, ismount, join, normpath;

from re import match;

from copy import deepcopy;

def walk_recusively(root, ignore="^$", sort_args=None):
    assert (isdir(root)), f"Not a directory: {args.dir}";
    assert (isinstance(sort_args, dict) or sort_args is None), \
        "Invalid parameter `sort_args, a dict expected.`";

    all = {
        "type"  : "dir",
        "name"  : ".",
        "child" : []
    };
    works = [(all, ".")];

    while (len(works)):
        work, relap = works.pop();
        absp = normpath(join(root, relap));

        raw = listdir(absp);
        if (sort_args is not None):
            raw.sort(key=sort_args.get("key", None),
                reverse=sort_args.get("reverse", False));

        for file in raw:
            if (match(args.ignore, file)):
                continue;
            fn = join(absp, file);
            if (isfile(fn)):
                work["child"].append({
                    "type"  : "file",
                    "name"  : file,
                });
            elif (islink(fn)):
                work["child"].append({
                    "type"  : "link",
                    "name"  : file,
                    "target": readlink(fn)
                });
            elif (ismount(fn)):
                work["child"].append({
                    "type"  : "mount",
                    "name"  : file,
                    "target": readlink(fn)
                });
            elif (isdir(fn)):
                nw = {
                    "type"  : "dir",
                    "name"  : file,
                    "child" : []
                }
                work["child"].append(nw);
                works.append((nw, normpath(join(relap, file))));
            else:
                work["child"].append({
                    "type"  : "unknown",
                    "name"  : file,
                });
    return all;

def print_markdown(all):
    all = deepcopy(all);

    works = [all];
    while (len(works)):
        target = works[-1];
        pre = (len(works) - 1) * "  ";

        broke = False;
        while (len(target["child"])):
            item = target["child"].pop(0);
            if (item["type"] == "file"):
                print(f"{pre}- 📄 {item['name']}");
            elif (item["type"] == "link"):
                print(f"{pre}- 📄 {item['name']} -> {item['target']}");
            elif (item["type"] == "mount"):
                print(f"{pre}- 📁 {item['name']} -> {item['target']}");
            elif (item["type"] == "dir"):
                print(f"{pre}- 📁 {item['name']}");
                works.append(item);
                broke = True;
                break;
        if (broke):
            continue;
        works.pop();
    return;

if __name__ == "__main__":
    from argparse import ArgumentParser;

    arg_parser = ArgumentParser(description="List all files in a markdown text.");
    arg_parser.add_argument("-d", "--dir", help="Directory to listed.", type=str, default=getcwd());
    arg_parser.add_argument("--ignore", help="Reg expr to ignore.", type=str, default="^$");
    arg_parser.add_argument("--sort", help="Sort mode.", type=str, choices=["a-z", "z-a", "none"], default="a-z");
    args = arg_parser.parse_args();

    root = normpath(args.dir);
    assert(isdir(root)), f"Not a directory: {args.dir}";

    if (args.sort == "a-z"):
        all = walk_recusively(root, args.ignore, {});
    elif (args.sort == "z-a"):
        all = walk_recusively(root, args.ignore, {"reverse" : True});
    else:
        all = walk_recusively(root, args.ignore);

    print(f"*{root}*");
    print("");
    print_markdown(all);
    