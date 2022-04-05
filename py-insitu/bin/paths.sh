#!/usr/bin/env bash

SCRIPT=$(readlink -f "$0")
SCRIPT_BIN=$(dirname "$SCRIPT")

# export PYVER="3.7.13" ## <- original version used by S2AND
# export PYVER="3.10.4" ## <- incompatible with numpy
export PYVER="3.9.11"

PY_INSITU_ROOT=$(dirname "$SCRIPT_BIN")
PROJECT_ROOT=$(pwd)

INSTALL_TMPD="$PY_INSITU_ROOT/install.tmp.d"

PYSRC="Python-$PYVER"
PYTGZ="$PYSRC.tgz"
PYSRC_URL="http://www.python.org/ftp/python/$PYVER/$PYTGZ"

PYTHOND="$PROJECT_ROOT/.local/python"
PYENVS="$PROJECT_ROOT/.local/envs"

ENV_NAME="open-hand-env"
ENV_ROOT="$PYENVS/$ENV_NAME"

show_paths() {
    echo "Directory Structure"
    echo "  PROJECT_ROOT   $PROJECT_ROOT"
    echo "  PY_INSITU      $PY_INSITU_ROOT"
    echo "  INSTALL_TMPD   $INSTALL_TMPD"
    echo
    echo "  PYSRC          $PYSRC"
    echo "  PYTGZ          $PYTGZ"
    echo "  PYSRC_URL      $PYSRC_URL"
    echo
    echo "  PYTHOND        $PYTHOND"
    echo "  PYENVS         $PYENVS"
    echo
    echo "  ENV_NAME       $ENV_NAME"
    echo "  ENV_ROOT       $ENV_ROOT"
}
