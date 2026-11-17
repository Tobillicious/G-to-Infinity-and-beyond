"""Read-only, separate-process observation of the bounded G3 fixed.marker fixture.

Not independently administered: process and authority are under one disposable
CI host administrator. No physical subject/consent assertions or effect grants.
"""
import argparse
import json
import os
from pathlib import Path
import stat


def observe(directory, *, expected_uid):
    if (not isinstance(directory, (str, Path))
            or not Path(directory).is_absolute()
            or type(expected_uid) is not int or expected_uid < 0):
        raise ValueError("absolute marker directory and pinned UID required")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open(directory, flags)
    try:
        directory_id = os.fstat(fd)
        names = os.listdir(fd)
        if names not in ([], ["fixed.marker"]):
            raise ValueError("unexpected marker-directory contents")
        if names == []:
            result = {"exists": False}
        else:
            # Anchor inspection to the opened directory descriptor. A symlink
            # or replacement between enumeration and open must not substitute
            # another inode; O_NONBLOCK prevents a hostile FIFO from hanging.
            before = os.stat("fixed.marker", dir_fd=fd, follow_symlinks=False)
            file_flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
            try:
                marker_fd = os.open("fixed.marker", file_flags, dir_fd=fd)
            except OSError as error:
                raise ValueError("marker identity or inode properties invalid") from error
            try:
                info = os.fstat(marker_fd)
            finally:
                os.close(marker_fd)
            if ((before.st_dev, before.st_ino) != (info.st_dev, info.st_ino)
                    or not stat.S_ISREG(info.st_mode) or info.st_uid != expected_uid
                    or info.st_size != 0 or info.st_nlink != 1):
                raise ValueError("marker identity or inode properties invalid")
            result = {"exists": True, "device": info.st_dev, "inode": info.st_ino,
                      "uid": info.st_uid, "size": info.st_size, "nlink": info.st_nlink}
        # Detect a replaceable name or directory changed during the read.
        if os.listdir(fd) != names:
            raise ValueError("marker directory changed during observation")
        if result["exists"]:
            # Same filename is not sufficient: reject an inode swapped between
            # the descriptor inspection and final directory enumeration.
            final_info = os.stat("fixed.marker", dir_fd=fd, follow_symlinks=False)
            if ((final_info.st_dev, final_info.st_ino, final_info.st_uid,
                 final_info.st_size, final_info.st_nlink) !=
                (info.st_dev, info.st_ino, info.st_uid, info.st_size, info.st_nlink)):
                raise ValueError("marker replaced during observation")
        after_dir = os.fstat(fd)
        named_dir = os.stat(directory, follow_symlinks=False)
        if ((directory_id.st_dev, directory_id.st_ino) !=
                (after_dir.st_dev, after_dir.st_ino)
                or (named_dir.st_dev, named_dir.st_ino) !=
                   (directory_id.st_dev, directory_id.st_ino)):
            raise ValueError("observed marker directory replaced")
        return result
    finally:
        os.close(fd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--marker-dir", required=True)
    parser.add_argument("--expected-uid", required=True, type=int)
    args = parser.parse_args()
    result = observe(args.marker_dir, expected_uid=args.expected_uid)
    print(json.dumps({"observer_pid": os.getpid(), "observation": result},
                     sort_keys=True))


if __name__ == "__main__":
    main()
