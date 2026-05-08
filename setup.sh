#!/bin/bash

parent_path=$(cd "$(dirname "$0")" && pwd)

cd "$parent_path" || exit 1

pip install --no-cache-dir -q .
python -m retro.import ./roms
cp ./states/* "/usr/local/lib/python3.12/dist-packages/stable_retro/data/stable/SuperMarioWorld-Snes-v0/"