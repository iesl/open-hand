#!/usr/bin/env bash

PROJECT_ROOT=$(pwd)
S2AND_ROOT="packages/s2and"
OPEN_HAND_ROOT="packages/open-hand"
OPENREVIEW_PY_ROOT="packages/openreview-py"

active_python=$(which python)

echo "Using Python $active_python"

if [ ! -d "$S2AND_ROOT" ]; then
    echo "No S2AND project found in $S2AND_ROOT"
    exit
fi

cd "$S2AND_ROOT" || exit

echo "In dir $(pwd)"
# pip3 --require-virtualenv install -r requirements.in
pip3 --require-virtualenv install -e .

cd "$PROJECT_ROOT" || exit
cd "$OPEN_HAND_ROOT" || exit

echo "In dir $(pwd)"
pip3 --require-virtualenv install -r requirements.in

cd "$PROJECT_ROOT" || exit
cd "$OPENREVIEW_PY_ROOT" || exit

echo "In dir $(pwd)"
pip3 --require-virtualenv install -e .
