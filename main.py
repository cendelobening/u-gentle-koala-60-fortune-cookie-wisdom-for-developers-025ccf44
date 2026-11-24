"""Fortune Cookie Wisdom for Developers entry.

Writes exactly one original fortune-cookie line for a software
developer to <output dir>/entry.txt and verifies the file afterwards.
Pure standard library, no network.
"""

import os
import stat
import tempfile

# The entry: one original fortune-cookie line, 102 characters.
LINE = "You will meet the author of your worst bug tonight: a younger you, who meant well and left no comment."

MAX_CHARS = 120


def check_line(line):
    """Make sure the line is a single clean line within the limit."""
    if not isinstance(line, str):
        raise ValueError("line must be a string")
    if not line:
        raise ValueError("line must not be empty")
    if not line.strip():
        raise ValueError("line must not be only whitespace")
    if line != line.strip():
        raise ValueError("line must have no leading or trailing whitespace")
    if "\n" in line or "\r" in line:
        raise ValueError("line must be a single line with no newline")
    if any(ord(ch) < 0x20 for ch in line):
        raise ValueError("line must not contain control characters")
    if not line.isascii():
        raise ValueError("line must be plain ASCII so bytes equal characters")
    if not line.startswith("You will"):
        raise ValueError("line must read like a fortune cookie ('You will ...')")
    if not 1 <= len(line) <= MAX_CHARS:
        raise ValueError(
            "line must be 1-%d characters, got %d" % (MAX_CHARS, len(line))
        )


def describe():
    """One-line summary of what this program does."""
    return "Writes one fortune-cookie line for developers (%d characters) to entry.txt." % len(LINE)


def output_dir():
    return os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"


def main():
    check_line(LINE)
    out_dir = output_dir()
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.txt")

    # Write to a temp file in the same directory, then move it into
    # place so the entry is never seen half-written.
    fd, tmp_path = tempfile.mkstemp(dir=out_dir, prefix=".entry-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(LINE)
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, target)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
    os.chmod(target, 0o644)

    # Read it back and confirm it is exactly what we meant to write,
    # byte for byte, with no stray newline or encoding surprise.
    with open(target, "rb") as handle:
        raw = handle.read()
    if raw != LINE.encode("utf-8"):
        raise ValueError("verification failed: entry.txt does not match the line")
    if raw.decode("utf-8") != LINE:
        raise ValueError("verification failed: entry.txt is not valid UTF-8 text")
    if raw.endswith(b"\n"):
        raise ValueError("verification failed: entry.txt has a trailing newline")
    mode = stat.S_IMODE(os.stat(target).st_mode)
    if mode != 0o644:
        raise ValueError("verification failed: entry.txt mode is %o" % mode)
    print(describe())
    print(
        "wrote %r (%d characters, %d bytes, mode %o) to %s"
        % (LINE, len(LINE), len(raw), mode, target)
    )


if __name__ == "__main__":
    main()
