#!/bin/bash

# m4_ignore(
echo "This is just a script template, not the script (yet) - pass it to 'argbash' to fix this." >&2
exit 11  #)Created by argbash-init v2.10.0
# DEFINE_SCRIPT_DIR()
# ARG_OPTIONAL_BOOLEAN([rebuild-script])
# ARG_OPTIONAL_BOOLEAN([info])
# ARG_OPTIONAL_BOOLEAN([make])
# ARG_OPTIONAL_BOOLEAN([download])
# ARG_OPTIONAL_BOOLEAN([install])
# ARG_OPTIONAL_BOOLEAN([install-env])
# ARG_OPTIONAL_BOOLEAN([dry-run])
# ARG_HELP([<The general help message of my script>])
# ARGBASH_GO

# [ <-- needed because of Argbash

# shellcheck disable=2154
source "$script_dir/paths.sh"

# shellcheck disable=2154
info=$_arg_info

# shellcheck disable=2154
rebuild_script=$_arg_rebuild_script

# shellcheck disable=2154
dryrun=$_arg_dry_run

# shellcheck disable=2154
download=$_arg_download

# shellcheck disable=2154
arg_make=$_arg_make

# shellcheck disable=2154
install=$_arg_install

# shellcheck disable=2154
install_env=$_arg_install_env


doit() {
    local cmds=("$@")
    if [ "$dryrun" = on ]; then
        echo "dry> ${cmds[*]}"
    else
        echo "run> ${cmds[*]}"
        "${cmds[@]}"
    fi

    echo ""
}

with_dirs() {
    local dirnames=("$@")
    for d in "${dirnames[@]}"; do
        if [ ! -d "$d" ]; then
            echo "could not cd to '$d' in ${dirnames[*]}"
            exit 1
        fi
        cd "$d" || exit 1
    done
    echo "In dir: $(pwd)"
}

do_rebuild_script() {
    echo "Rebuilding script.."
    with_dirs "$script_dir"
    argbash py-install.m4 -o py-install
    exit 0
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
}

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

test "$info" = on && show_paths && exit 0
test "$rebuild_script" = on && do_rebuild_script && exit 0

if [ "$download" = on ]; then
    echo "Downloading Python"
    download_python
    unpack_python
fi

if [ "$arg_make" = on ]; then
    echo "Making Python"
    make_python
fi

if [ "$install" = on ]; then
    echo "Installing Python"
    install_python
fi

if [ "$install_env" = on ]; then
    echo "(Re)installing Env"
    install_env
fi


# ] <-- needed because of Argbash
