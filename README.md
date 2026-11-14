# Glyph Doom

Play the original DOOM in a terminal with colored ASCII graphics. DoomGeneric
runs the game and renders its 320×200 framebuffer. GlyphForge draws the resulting
character grid, reads keyboard events, and exports still frames.

![DOOM title screen rendered as colored ASCII](docs/media/title-screen.png)

![Glyph Doom combat demo showing a pistol fight followed by a barrel explosion](docs/media/gameplay.gif)

Recorded with Glyph Doom in E1M1 with a former human and a barrel positioned
near the starting area for the demo.

## Quick start

Requires Python 3.10+, Git, a C compiler, Make, curl, and an ANSI terminal.

```sh
git clone --recurse-submodules git@github.com:amirhdolati/glyph-doom.git
cd glyph-doom
./setup.sh
python3 doom_glyph.py --warp 1 1
```

Setup builds [DoomGeneric](https://github.com/ozkl/doomgeneric) from a pinned
revision and downloads the [DOOM 1.8 shareware IWAD](https://www.gamers.org/pub/idgames/idstuff/doom/).
For your own game data, use `./setup.sh --no-shareware` and
`python3 doom_glyph.py --iwad /path/to/doom.wad`. Saves and settings live in
`.state/`. The game runs silently and uses keyboard controls.

| Key | Action |
| --- | --- |
| ↑ / ↓ or W / S | Move forward or backward |
| ← / → | Turn |
| A / D | Strafe |
| Space or F | Fire |
| E | Use or open |
| Shift | Run in terminals that report modifier-key events |
| 1–7 | Select weapon |
| Tab | Automap |
| Esc / Enter | Open menu / select |
| Q | Return to the shell |

Pass `--256` to force the xterm 256-color palette. Terminals that only report
keypresses use short key holds refreshed by keyboard repeat.

## Architecture

`setup.sh` downloads and verifies the pinned DoomGeneric source. The Makefile
links the DoomGeneric core with [`glyph_platform.c`](glyph_platform.c) to
produce `.build/doom-pixels`. The [Python frontend](doom_glyph.py) loads
GlyphForge from the pinned submodule and starts the executable with the chosen IWAD.

```mermaid
flowchart TB
    WAD["IWAD<br/>Maps, textures, sprites, and other game data"]
    TTY["ANSI terminal"]
    FILE["SVG, HTML, TXT, or ANSI file"]

    subgraph C["Native child process · .build/doom-pixels"]
        DOOM["DoomGeneric<br/>Game ticks and original software renderer"]
        DRAW["glyph_platform.c<br/>DG_DrawFrame"]
        KEY["glyph_platform.c<br/>DG_GetKey"]
        KEY -->|"Key code and press or release"| DOOM
        DOOM -->|"DG_ScreenBuffer"| DRAW
    end

    subgraph SOCK["Local socket pair · socket.socketpair()"]
        FRAMES["Native → Python<br/>Fixed-size frame stream"]
        KEYS["Python → Native<br/>Two-byte key records"]
    end

    subgraph PY["Python parent process · doom_glyph.py"]
        LAUNCH["doom_process<br/>Start child with the IWAD path and socket descriptor"]
        READ["read_frame<br/>Read one complete 320×200 frame"]
        CELLS["to_cells<br/>Sample four pixels per cell and choose a glyph and colors"]
        MAP["Controls.read<br/>Map events to Doom key codes"]
        EVENTS["GlyphForge · Terminal.events"]
        DISPLAY["GlyphForge · Terminal.draw"]
        SAVE["GlyphForge · save_frame"]
        READ --> CELLS
        CELLS -->|"Interactive play"| DISPLAY
        CELLS -->|"Screenshot mode"| SAVE
        EVENTS --> MAP
    end

    LAUNCH -.->|"Start with Popen"| DOOM
    WAD --> DOOM
    DRAW -->|"256,000 bytes per frame"| FRAMES
    FRAMES --> READ
    DISPLAY -->|"ANSI screen updates"| TTY
    TTY -->|"Keyboard bytes"| EVENTS
    MAP -->|"Key code, then 1 for press or 0 for release"| KEYS
    KEYS --> KEY
    SAVE --> FILE
```

1. **Start the game.** `doom_process()` creates the socket pair and gives
   DoomGeneric one endpoint through the inherited descriptor named by
   `DOOM_GLYPH_FD`. The C adapter calls `doomgeneric_Create()`, then repeatedly
   calls `doomgeneric_Tick()` to advance and render the game.
2. **Render to terminal cells.** `DG_DrawFrame()` sends the framebuffer as
   320×200 native 32-bit pixel values, with at least 28 ms between sends.
   Python assembles the full frame from the byte stream, averages four samples
   per cell, and uses luminance to select the ASCII glyph. GlyphForge writes
   ANSI updates for changed cells and redraws after a resize.
3. **Return keyboard input.** Each interactive iteration reads key events from
   GlyphForge before receiving the next frame. `Controls.read()` encodes each
   changed Doom key state as two bytes, which Python writes to the same socket. `DG_GetKey()`
   polls for those records without blocking the game tick.
4. **Export or exit.** Screenshot mode reads frames for roughly 1.5 seconds
   and exports one 120×45 cell frame without opening an interactive terminal.
   During play, `Q` exits the loop, GlyphForge restores the terminal, and
   Python closes the socket and reaps the child process.

## Export a screenshot

```sh
python3 doom_glyph.py --warp 1 1 --screenshot e1m1.svg
```

The exporter also supports `.html`, `.ans`, and `.txt`. For a DOOM II IWAD,
pass one map number to `--warp`.

## Support GlyphForge

You can support GlyphForge development with a donation on TRON. The QR code
below comes from the engine's repository.

[View the GlyphForge donation address on TRONSCAN](https://tronscan.org/#/address/TZ6HTiRLeyWoFJ5rGgx6qbMyjLAHNb6hfb)

[<img src="docs/media/donation-tron.png" width="220" alt="GlyphForge TRON donation QR code">](https://tronscan.org/#/address/TZ6HTiRLeyWoFJ5rGgx6qbMyjLAHNb6hfb)

## License

Glyph Doom is licensed under GPL-2.0-or-later. See [COPYING](COPYING).
[GlyphForge](https://github.com/amirhdolati/glyphforge-engine) is an independent
MIT-licensed dependency. DOOM game data is supplied separately.
