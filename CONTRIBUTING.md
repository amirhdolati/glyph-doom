# Contributing to Glyph Doom

Open an issue for a bug or feature proposal. Include your OS, terminal, Python version, and the exact `doom_glyph.py` flags you used. Do not attach private WADs or personal save files.

## Setup

Requires Python 3.10+, Git, a C compiler, Make, curl, and an ANSI terminal.

```sh
git clone --recurse-submodules git@github.com:amirhdolati/glyph-doom.git
cd glyph-doom
./setup.sh
python3 doom_glyph.py --warp 1 1
```

Keep the GlyphForge submodule on the pinned revision unless the change explicitly updates it.

## Commit messages and documentation

Use [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

| Type | Use for |
| --- | --- |
| `feat` | New user-facing capability |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `build` | Build system, dependencies, packaging |
| `refactor` | Code change that is neither feat nor fix |
| `test` | Tests only |
| `chore` | Maintenance that does not change product behavior |

Format: `<type>(optional-scope): <imperative summary>`

Examples:

- `feat(input): map Shift as a run key when the terminal reports it`
- `fix(render): preserve aspect ratio on tall terminals`
- `docs: separate architecture overview from runtime details`
- `build: pin GlyphForge as a Git submodule`

Keep the subject under ~72 characters, use the imperative mood, and write in English.

All project documentation (`README`, `docs/`, `CONTRIBUTING`, and contributor-facing comments) must be in English. Do not add localized documentation files.

## License

Glyph Doom is licensed under GPL-2.0-or-later. Preserve third-party notices and keep DoomGeneric / IWAD handling clearly separated from GlyphForge.
