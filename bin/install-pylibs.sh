#!/usr/bin/env bash

SCRIPT=$(readlink -f "$0")
BIN=$(dirname "$SCRIPT")

# shellcheck source=./paths.sh
. "$BIN/paths.sh"

active_python=$(which python)
env_python="$S2AND_ENV/bin/python"

if [ "$active_python" != "$env_python" ]; then
    echo "Active python is *not* $env_python"
    exit
fi

echo "Using Python $active_python"

if [ ! -d "$S2AND" ]; then
    echo "No S2AND project found in $S2AND"
    exit
fi

cd "$S2AND" || exit

pip3 install -r requirements.in
pip3 install -e .
