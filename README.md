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

```mermaid
flowchart LR
    WAD["DOOM IWAD"] --> DOOM["DoomGeneric"]
    DOOM -->|"Game frames"| APP["Glyph Doom"]
    APP -->|"Colored ASCII cells"| GLYPH["GlyphForge"]
    GLYPH -->|"Screen updates"| TTY["Terminal"]
    TTY -.->|"Keyboard input"| GLYPH
    GLYPH -.->|"Key events"| APP
    APP -.->|"Doom key states"| DOOM
```

DoomGeneric runs and renders the game. Glyph Doom converts each frame into
colored ASCII cells, and GlyphForge displays them in the terminal.

[Runtime details and data flow](docs/architecture.md)

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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, Conventional Commits, and
English-only documentation rules.

## License

Glyph Doom is licensed under GPL-2.0-or-later. See [COPYING](COPYING).
[GlyphForge](https://github.com/amirhdolati/glyphforge-engine) is an independent
MIT-licensed dependency. DOOM game data is supplied separately.
