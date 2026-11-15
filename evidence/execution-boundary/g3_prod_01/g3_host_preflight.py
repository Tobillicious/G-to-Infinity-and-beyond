"""Preflight for the bounded G3 writer host, NOT a production certificate.

Run as the dedicated writer identity against already-provisioned local paths.
This denies unsafe file ownership, hard-link aliases, symlinks, and accessible
writable data roots before treating the host as an acceptable research fixture.
It cannot enumerate capabilities held by OTHER processes, detect mount/root
attacks, or guarantee paths remain unchanged after this check.
"""
import os
from pathlib import Path
import stat



def inspect_trusted_ancestors(path):
    """Check each directory component in an existing absolute pathname.

    This catches preexisting symlink and writable-parent hazards. It is
    intentionally conservative and NOT atomic against simultaneous rename
    or mount changes. A root-owned sticky /tmp-style ancestor is allowed
    for disposable fixtures, relying on sticky-directory protections.
    """
    p = Path(path)
    if not p.is_absolute():
        return {'ok': False, 'code': 'relative_path'}
    current = Path('/')
    for part in p.parts[1:-1]:
        current = current / part
        try:
            s = os.lstat(current)
        except OSError:
            return {'ok': False, 'code': 'ancestor_unavailable'}
        if not stat.S_ISDIR(s.st_mode):
            return {'ok': False, 'code': 'ancestor_not_directory'}
        if s.st_uid not in (0, os.geteuid()):
            return {'ok': False, 'code': 'ancestor_untrusted_owner'}
        if s.st_mode & 0o022:
            if not (s.st_uid == 0 and s.st_mode & stat.S_ISVTX):
                return {'ok': False, 'code': 'ancestor_writable'}
    return {'ok': True, 'code': 'ancestors_checked'}


def inspect_private_root(path):
    """Inspect a private directory with O_NOFOLLOW, using its actual inode."""
    p = Path(path)
    if not p.is_absolute():
        return {'ok': False, 'code': 'relative_directory'}
    try:
        fd = os.open(p, os.O_RDONLY | os.O_DIRECTORY |
                     os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError:
        return {'ok': False, 'code': 'directory_unavailable'}
    try:
        s = os.fstat(fd)
        if (not stat.S_ISDIR(s.st_mode) or s.st_uid != os.geteuid()
                or s.st_mode & 0o077):
            return {'ok': False, 'code': 'directory_not_private'}
        return {'ok': True, 'code': 'directory_private'}
    finally:
        os.close(fd)


def inspect_private_file(path):
    """Inspect existing regular files; prohibit link aliases and group access."""
    p = Path(path)
    if not p.is_absolute():
        return {'ok': False, 'code': 'relative_file'}
    try:
        fd = os.open(p, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC |
                     os.O_NONBLOCK)
    except OSError:
        return {'ok': False, 'code': 'file_unavailable'}
    try:
        s = os.fstat(fd)
        if (not stat.S_ISREG(s.st_mode) or s.st_uid != os.geteuid()
                or s.st_mode & 0o077 or s.st_nlink != 1):
            return {'ok': False, 'code': 'file_not_private'}
        return {'ok': True, 'code': 'file_private'}
    finally:
        os.close(fd)


def inspect_writer_host(*, output_dir, writer_db, fence_file, gate_db, mesh_db):
    """Deny on first unsafe directory or persistent authority resource.

    All paths must be independently configured, already exist, and be owned by
    the current unprivileged writer. The output directory must be separate
    from authority DB and fence parents; no pathname supplied by a guest is
    accepted here. The caller must also enforce the secure IPC constructor,
    distinguish guest UID, prevent FD transfer, and pin mount/configuration.
    """
    if os.geteuid() == 0:
        return {'ok': False, 'code': 'root_writer_forbidden'}
    paths = [output_dir, writer_db, fence_file, gate_db, mesh_db]
    if any(type(p) is not str or not os.path.isabs(p) for p in paths):
        return {'ok': False, 'code': 'invalid_path'}
    # Reject symlink and untrusted write-capable ancestors before examining
    # the final inode. O_NOFOLLOW alone covers only the final component.
    for p in paths:
        ancestor = inspect_trusted_ancestors(p)
        if not ancestor['ok']:
            return {'ok': False, 'code': 'unsafe_ancestor', 'path': p,
                    'reason': ancestor['code']}
    real = [os.path.abspath(p) for p in paths]
    if len(set(real)) != len(real):
        return {'ok': False, 'code': 'resource_path_collision'}
    for p in [output_dir] + [os.path.dirname(x) for x in paths[1:]]:
        check = inspect_private_root(p)
        if not check['ok']:
            return {'ok': False, 'code': 'unsafe_directory', 'path': p,
                    'reason': check['code']}
    # No authority DB, control lock or guest-selected path within effects.
    if any(os.path.commonpath([output_dir, name]) == output_dir
           for name in paths[1:]):
        return {'ok': False, 'code': 'authority_inside_effect_output'}
    for p in paths[1:]:
        check = inspect_private_file(p)
        if not check['ok']:
            return {'ok': False, 'code': 'unsafe_resource', 'path': p,
                    'reason': check['code']}
    return {'ok': True, 'code': 'bounded_local_preflight_only',
            'certified': False, 'all_capabilities_mediated': False}
