#!/bin/bash

# m4_ignore(
echo "This is just a script template, not the script (yet) - pass it to 'argbash' to fix this." >&2
exit 11  #)Created by argbash-init v2.10.0
# DEFINE_SCRIPT_DIR([_script_dir])
#
# ARG_OPTIONAL_BOOLEAN([dry-run], [], [Display Commands])
#
# ARG_OPTIONAL_ACTION([info],[],[Show python install info],[show_paths])
# ARG_OPTIONAL_ACTION([make],[],[Configure/Make python],[make_pytho])
# ARG_OPTIONAL_ACTION([download],[],[Download/Unpack Python *.tgz],[download_python])
# ARG_OPTIONAL_ACTION([install-python],[],[Install python to .local/python/],[install_python])
# ARG_OPTIONAL_ACTION([install-env],[],[Install env to .local/envs/],[install_env])
# ARG_OPTIONAL_ACTION([all],[],[Download/Make/Install/Setup Everything],[run_all])
#
# ARG_HELP([<Python/virtual env download/make/install>])
#
# ARGBASH_PREPARE()

# [ <-- needed because of Argbash

# shellcheck disable=2154
readonly script_dir="$_script_dir"

source "$script_dir/_utils.sh"

# shellcheck disable=2154
source "$script_dir/paths.sh"

unpack_python() {
    echo "Unpacking Python $PYVER"
    with_dirs "$INSTALL_TMPD"
    if [ ! -d "$PYSRC" ]; then
        echo "Unpacking $PYTGZ => $PYSRC"
        doit tar -zxf "$PYTGZ"
    else
        echo "$PYSRC exists"
    fi

    if [ ! -d "$PYSRC" ]; then
        echo "Error unpacking $PYSRC"
        exit
    else
        echo "Unpacked Python $PYSRC"
    fi
}

download_python() {
    echo "Download Python $PYVER"
    with_dirs "$INSTALL_TMPD"
    if [ ! -f "$PYTGZ" ]; then
        echo "No $PYTGZ found, downloading"
        doit wget "$PYSRC_URL"
    fi
    if [ ! -f "$PYTGZ" ]; then
        echo "Could not download Python from $PYSRC_URL"
        exit 1
    fi
    if [ -f "$PYTGZ" ]; then
        echo "$PYTGZ downloaded"
    fi
    unpack_python
}

make_python() {
    echo "Making Python $PYVER"
    with_dirs "$INSTALL_TMPD" "$PYSRC"
    doit ./configure --prefix="$PYTHOND" --enable-optimizations --with-lto --enable-loadable-sqlite-extensions

    doit make clean
    doit make build_all
}

install_python() {
    with_dirs "$INSTALL_TMPD" "$PYSRC"
    echo "Making Python $PYVER"
    cd "$INSTALL_TMPD" || exit
    cd "$PYSRC" || exit

    doit rm -rf "$PYTHOND"
    doit mkdir -p "$PYTHOND"
    doit make install
    doit "$PYTHOND/bin/pip3" install --ignore-installed virtualenv
}

install_env() {
    with_dirs "$PROJECT_ROOT"
    echo "Deleting python envs $PYENVS/*"
    doit rm -rf "$PYENVS"
    doit mkdir -p "$PYENVS"
    doit "$PYTHOND/bin/virtualenv" "$ENV_ROOT"
}

run_all() {
    echo "Running Everything"
    download_python
    make_python
    install_python
    install_env
}

#########################
## Run Main
#########################
parse_commandline "$@"

## Print help if no other action has been taken
_PRINT_HELP=yes die "" 1

# ] <-- needed because of Argbash
