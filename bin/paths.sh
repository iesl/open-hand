#!/bin/bash

# SCRIPT=$(readlink -f "$0")
# BIN=$(dirname "$SCRIPT")

export PYVER="3.7.13"

CWD=$(pwd)
ROOTD=$(pwd)
TMPD="$ROOTD/install.tmp.d"

PYSRC="Python-$PYVER"
PYTGZ="$PYSRC.tgz"
PYSRC_URL="http://www.python.org/ftp/python/$PYVER/$PYTGZ"

PYTHOND="$ROOTD/.local/python"
PYENVS="$ROOTD/.local/envs"

S2AND_ENV="$PYENVS/s2and-env"

export CWD
export TMPD
export ROOTD

export PYSRC
export PYTGZ
export PYSRC_URL

export PYTHOND
export PYENVS

export S2AND_ENV

echo "Directory Structure"
echo "  ROOTD         $ROOTD"
echo "  TMPD          $TMPD"
echo
echo "  PYSRC         $PYSRC"
echo "  PYTGZ         $PYTGZ"
echo "  PYSRC_URL     $PYSRC_URL"
echo
echo "  PYTHOND       $PYTHOND"
echo "  PYENVS        $PYENVS"
echo
echo "  S2AND_ENV     $S2AND_ENV"
