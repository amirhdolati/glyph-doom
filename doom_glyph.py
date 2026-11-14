#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Play DoomGeneric in a GlyphForge terminal."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from array import array
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryFile

ROOT = Path(__file__).resolve().parent
GLYPHFORGE = ROOT / "vendor" / "glyphforge-engine" / "src"
if not (GLYPHFORGE / "glyphforge").is_dir():
    sys.exit("GlyphForge is missing. Run git submodule update --init --recursive.")
sys.path.insert(0, str(GLYPHFORGE))

from glyphforge import Terminal, save_frame  # noqa: E402

WIDTH, HEIGHT = 320, 200
FRAME_SIZE = WIDTH * HEIGHT * 4
DISPLAY_ASPECT = 4 / 3
RAMP = " .:-=+*#%@"
ASCII_RAMP = " .,:;-~=+*oO#%@"
ASCII_GLYPHS = tuple(
    ASCII_RAMP[round((level / 255) ** 0.65 * (len(ASCII_RAMP) - 1))]
    for level in range(256)
)
ASCII_FOREGROUND = (255, 255, 255)
ASCII_BACKGROUND = (0, 0, 0)
DISPLAY_CHANNEL = tuple(round(255 * (channel / 255) ** 0.8) for channel in range(256))
KEYS = {
    "up": 0xAD,
    "w": 0xAD,
    "down": 0xAF,
    "s": 0xAF,
    "left": 0xAC,
    "right": 0xAE,
    "a": 0xA0,
    "d": 0xA1,
    "e": 0xA2,
    "space": 0xA3,
    "f": 0xA3,
    "exit": 27,
    "enter": 13,
    "tab": 9,
    "backspace": 127,
    "shift-left": 0xB6,
    "shift-right": 0xB6,
    **{key: ord(key) for key in "1234567+-yn"},
}


def sample_axis(source, cells):
    # Two sample centers in each cell, at 25% and 75% of its span.
    return [
        ((4 * i + 1) * source // (4 * cells), (4 * i + 3) * source // (4 * cells))
        for i in range(cells)
    ]


def to_cells(pixels, width, height, *, ascii_mode=False):
    xs = sample_axis(WIDTH, width)
    ys = sample_axis(HEIGHT, height)
    frame = []
    for upper, lower in ys:
        top, bottom = upper * WIDTH, lower * WIDTH
        row = []
        for left, right in xs:
            samples = (
                pixels[top + left],
                pixels[top + right],
                pixels[bottom + left],
                pixels[bottom + right],
            )
            r = sum((pixel >> 16) & 255 for pixel in samples) // 4
            g = sum((pixel >> 8) & 255 for pixel in samples) // 4
            b = sum(pixel & 255 for pixel in samples) // 4
            if ascii_mode:
                luminance = (54 * r + 183 * g + 19 * b) >> 8
                row.append((ASCII_GLYPHS[luminance], ASCII_FOREGROUND, ASCII_BACKGROUND))
                continue
            r, g, b = DISPLAY_CHANNEL[r], DISPLAY_CHANNEL[g], DISPLAY_CHANNEL[b]
            luminance = (54 * r + 183 * g + 19 * b) >> 8
            glyph = RAMP[(luminance * (len(RAMP) - 1) + 127) // 255]
            fg = tuple(min(255, c * 3 // 2 + 24) for c in (r, g, b))
            bg = (r * 3 // 4, g * 3 // 4, b * 3 // 4)
            row.append((glyph, fg, bg))
        frame.append(row)
    return frame


def encode_ascii(frame, x=1, y=1):
    """Position plain glyph rows using the terminal's default colors."""
    return "".join(
        f"\x1b[{y + offset};{x}H" + "".join(cell[0] for cell in row)
        for offset, row in enumerate(frame)
    )


@contextmanager
def doom_process(args, log):
    binary = ROOT / ".build" / "doom-pixels"
    if not binary.is_file():
        raise RuntimeError("Build DoomGeneric first with ./setup.sh.")
    state = ROOT / ".state" / args.iwad.stem.lower()
    if args.screenshot:
        state /= "capture"
    state.mkdir(parents=True, exist_ok=True)
    command = [str(binary), "-iwad", str(args.iwad), "-nosound", "-nomouse"]
    if args.warp:
        command.extend(["-warp", *args.warp])

    client, backend = socket.socketpair()
    with client, backend:
        process = subprocess.Popen(
            command,
            cwd=state,
            stdin=subprocess.DEVNULL,
            stdout=log,
            stderr=log,
            env={**os.environ, "DOOM_GLYPH_FD": str(backend.fileno())},
            pass_fds=(backend.fileno(),),
        )
        backend.close()
        client.settimeout(5)
        try:
            yield client, process
        finally:
            # EOF lets the native backend finish even if stopped mid-frame.
            client.close()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


class Controls:
    def __init__(self):
        self.held = {}

    def read(self, events, now):
        previous = {KEYS[key] for key in self.held}
        for event in events:
            if event.key == "q" and not event.release:
                return None
            if event.key == "focus-out":
                self.held.clear()
                continue
            if event.key not in KEYS:
                continue
            if event.release:
                self.held.pop(event.key, None)
            else:
                # Older terminals report presses and repeats only.
                self.held[event.key] = float("inf") if event.enhanced else now + 0.16
        self.held = {key: until for key, until in self.held.items() if until > now}
        current = {KEYS[key] for key in self.held}
        return bytes(
            [value for key in sorted(previous - current) for value in (key, 0)]
            + [value for key in sorted(current - previous) for value in (key, 1)]
        )


def layout(terminal, aspect):
    columns, lines = terminal.size()
    width = min(max(1, columns), 160)
    height = min(max(1, lines), 80)
    width = max(1, min(width, round(height * DISPLAY_ASPECT / aspect)))
    height = max(1, min(height, round(width * aspect / DISPLAY_ASPECT)))
    return (
        width,
        height,
        max(1, (columns - width) // 2 + 1),
        max(1, (lines - height) // 2 + 1),
    )


def read_frame(connection, pixels):
    remaining = memoryview(pixels).cast("B")
    while remaining:
        received = connection.recv_into(remaining)
        if not received:
            if len(remaining) != FRAME_SIZE:
                raise RuntimeError("DoomGeneric closed its connection mid-frame.")
            return False
        remaining = remaining[received:]
    return True


def play(connection, terminal, pixels, *, ascii_mode=False):
    previous_layout = None
    controls = Controls()
    displayed = False
    while True:
        changes = controls.read(terminal.events(), time.monotonic())
        if changes is None:
            return False
        if changes:
            try:
                connection.sendall(changes)
            except BrokenPipeError:
                if displayed:
                    return True
                raise
        aspect = terminal.aspect()
        size = layout(terminal, aspect)
        width, height, x, y = size
        if not read_frame(connection, pixels):
            if not displayed:
                raise RuntimeError("DoomGeneric stopped before displaying a frame.")
            return True
        if size != previous_layout:
            terminal.clear()
            previous_layout = size
        frame = to_cells(pixels, width, height, ascii_mode=ascii_mode)
        if ascii_mode:
            sys.stdout.write("\x1b[?2026h" + encode_ascii(frame, x, y) + "\x1b[?2026l")
            sys.stdout.flush()
        else:
            terminal.draw(frame, x=x, y=y, delta=True)
        displayed = True


def capture(connection, pixels, path, *, ascii_mode=False):
    until = time.monotonic() + 1.5
    while read_frame(connection, pixels):
        if time.monotonic() >= until:
            frame = to_cells(pixels, 120, 45, ascii_mode=ascii_mode)
            if ascii_mode and path.suffix.lower() == ".ans":
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(encode_ascii(frame), encoding="ascii")
                return path
            return save_frame(frame, path)
    raise RuntimeError("DoomGeneric stopped before the screenshot was ready.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iwad", type=Path, default=ROOT / "assets" / "doom1.wad")
    parser.add_argument(
        "--warp", nargs="+", metavar="N", help="episode and map, or a DOOM II map"
    )
    parser.add_argument(
        "--screenshot",
        type=Path,
        metavar="FILE",
        help="export one .svg, .html, .ans or .txt frame",
    )
    display = parser.add_mutually_exclusive_group()
    display.add_argument(
        "--256", dest="palette256", action="store_true", help="force xterm-256 colors"
    )
    display.add_argument(
        "--ascii",
        dest="ascii_mode",
        action="store_true",
        help="render the full frame with ASCII characters and no color changes",
    )
    args = parser.parse_args()
    if args.warp and (len(args.warp) > 2 or not all(n.isdecimal() for n in args.warp)):
        parser.error("--warp takes one or two map numbers")
    args.iwad = args.iwad.expanduser().resolve()
    try:
        with args.iwad.open("rb") as wad:
            if wad.read(4) != b"IWAD":
                parser.error(f"Expected an IWAD file at {args.iwad}.")
    except OSError as error:
        parser.error(f"{error}. Run ./setup.sh for the shareware IWAD or pass --iwad.")

    pixels = array("I", [0]) * (WIDTH * HEIGHT)
    with TemporaryFile() as log:
        try:
            with doom_process(args, log) as (connection, process):
                if args.screenshot:
                    print(
                        capture(
                            connection, pixels, args.screenshot, ascii_mode=args.ascii_mode
                        )
                    )
                else:
                    with Terminal(
                        truecolor=False if args.palette256 else None
                    ) as terminal:
                        backend_closed = play(
                            connection, terminal, pixels, ascii_mode=args.ascii_mode
                        )
                    if backend_closed and process.wait(timeout=1):
                        raise RuntimeError(
                            f"DoomGeneric exited with status {process.returncode}."
                        )
        except KeyboardInterrupt:
            return 0
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as error:
            log.seek(0)
            details = log.read().decode(errors="replace").strip()
            if details:
                print(details, file=sys.stderr)
            parser.exit(1, f"{error}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
