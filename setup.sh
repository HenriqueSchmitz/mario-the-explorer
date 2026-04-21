#!/bin/bash

parent_path=$(cd "$(dirname "$0")" && pwd)

cd "$parent_path" || exit 1

pip install -q .
python -m retro.import ./roms