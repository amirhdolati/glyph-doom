# Glyph Doom

Play the original DOOM in an ANSI terminal. DoomGeneric renders the game into a
320×200 pixel framebuffer. The Python frontend samples it into colored ASCII
cells, and GlyphForge handles terminal drawing, input, and frame export.

## Run

Use macOS, Linux, or WSL with Python 3.10+, a C compiler, Make, and curl. The project
loads [GlyphForge](https://github.com/amirhdolati/glyphforge-engine) from an adjacent
`glyphforge-engine/src` checkout when present. A standalone clone can install it
in a virtual environment:

```sh
git clone https://github.com/amirhdolati/glyph-doom.git
cd glyph-doom
python3 -m venv .venv
. .venv/bin/activate
python -m pip install "git+https://github.com/amirhdolati/glyphforge-engine.git"
./setup.sh
python doom_glyph.py --warp 1 1
```

Setup builds the pinned [DoomGeneric source](https://github.com/ozkl/doomgeneric/tree/e257a09527062bfb986b6e5e0780839b6cbd5b71)
and downloads the original [DOOM 1.8 shareware episode](https://www.gamers.org/pub/idgames/idstuff/doom/).
Use `./setup.sh --no-shareware` and `python3 doom_glyph.py --iwad /path/to/doom.wad`
to use your own IWAD. Each IWAD gets its own local save/config directory in `.state/`.

| Keys | Action |
| --- | --- |
| Up / Down or W / S | Move forward / backward |
| Left / Right | Turn |
| A / D | Strafe |
| Space or F | Fire |
| E | Use / open |
| Shift | Run in terminals that report modifier-key events |
| 1–7 | Select weapon |
| Tab | Automap |
| Esc / Enter | Menu / select |
| Q | Exit to the shell |

For held keys, the frontend uses press and release events when the terminal provides
them and short pulses refreshed by keyboard repeat otherwise. This port uses keyboard
controls and runs silently. Color is detected by GlyphForge. Pass `--256` to force
the xterm palette.

## Start a level or export a frame

```sh
python3 doom_glyph.py --warp 1 1
python3 doom_glyph.py --warp 1 1 --screenshot e1m1.svg
```

The screenshot command also accepts `.html`, `.ans`, and `.txt`. Use one map
number with `--warp` for DOOM II.

Glyph Doom is licensed under GPL-2.0-or-later. See [COPYING](COPYING) for the
GPL text. Game data is downloaded separately, and GlyphForge is an independent
MIT-licensed dependency.
