#!/bin/sh
# SPDX-License-Identifier: GPL-2.0-or-later
set -eu

cd "$(dirname "$0")"
revision=e257a09527062bfb986b6e5e0780839b6cbd5b71
source_sha=26f8f60daa6c6e4d3c01e5eac9fb700d592dede803d13ac848154ff356b2a2e7
wad_sha=bb449c7480e9a02a62012d041406e8e43daa51caa0650646d1307d8650b8f837
wad_url=https://www.gamers.org/pub/idgames/idstuff/doom/doom-1.8.wad.gz

case "${1:-}" in
    '') shareware=1 ;;
    --no-shareware) shareware=0 ;;
    *) printf 'Usage: %s [--no-shareware]\n' "$0" >&2; exit 2 ;;
esac

verify() {
    python3 - "$1" "$2" <<'PY'
import hashlib
from pathlib import Path
import sys

path = Path(sys.argv[1])
if hashlib.sha256(path.read_bytes()).hexdigest() != sys.argv[2]:
    sys.exit(f"SHA-256 mismatch for {path}")
PY
}

mkdir -p .build
if [ ! -f .build/upstream/doomgeneric/Makefile ]; then
    archive=.build/doomgeneric-$revision.tar.gz
    curl -fL --retry 2 --max-time 180 -o "$archive" \
        "https://codeload.github.com/ozkl/doomgeneric/tar.gz/$revision"
    verify "$archive" "$source_sha"
    mkdir -p .build/upstream
    tar -xzf "$archive" --strip-components 1 -C .build/upstream
fi

make -j "${JOBS:-4}"

if [ "$shareware" = 1 ] && [ ! -f assets/doom1.wad ]; then
    mkdir -p assets
    curl -fL --retry 2 --max-time 180 -o .build/doom1.wad.gz "$wad_url"
    gzip -dc .build/doom1.wad.gz > .build/doom1.wad
    verify .build/doom1.wad "$wad_sha"
    mv .build/doom1.wad assets/doom1.wad
fi
