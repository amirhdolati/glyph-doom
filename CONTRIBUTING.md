# Contributing to Glyph Doom

Open an issue for a bug or feature proposal. Include your OS, terminal, Python version, and the exact `doom_glyph.py` flags you used. Do not attach private WADs or personal save files.

## Setup

Requires Python 3.10+, Git, a C compiler, Make, curl, and an ANSI terminal.

```sh
git clone --recurse-submodules https://github.com/amirhdolati/glyph-doom.git
cd glyph-doom
./setup.sh
python3 doom_glyph.py --warp 1 1
```

Keep the GlyphForge submodule on the pinned revision unless the change explicitly updates it.

## Commit messages and documentation

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).
Write each subject in English, start the summary with a verb, and aim for
72 characters or fewer. Use `type: summary` or `type(scope): summary`.

| Type | Use for |
| --- | --- |
| `feat` | New functionality |
| `fix` | Bug fixes |
| `docs` | Documentation |
| `build` | Build tools, dependencies, and packaging |
| `ci` | CI configuration and workflows |
| `refactor` | Code changes that preserve behavior |
| `perf` | Performance improvements |
| `test` | Tests |
| `chore` | Other project maintenance |

For example, use `docs: clarify the quick start` or
`fix(terminal): restore the cursor on exit`. Mark breaking changes with
`!` before the colon or a `BREAKING CHANGE:` footer.

Write project documentation in English. Use the README for the project
overview, prerequisites, and quick start. Link to the relevant guides from
the README and put longer guides in `docs/`. Use descriptive headings,
relative links for repository files, and alt text for screenshots.

## License

Glyph Doom is licensed under GPL-2.0-or-later. Preserve third-party notices and keep DoomGeneric / IWAD handling clearly separated from GlyphForge.
