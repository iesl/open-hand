# OpenHand
## OpenReview Author Name Disambiguation

### Installation
#### Install locally built python to project-root/.local/python/
#### Linux build prereqs
Run script to install python build deps:
```
> py-insitu/bin/dist-setup
```
Which is equivalent to:
n.b., this works for certain versions of Linux (last used on Ubuntu 21.10), but might need to be tweaked for other platforms
```
sudo apt install libbz2-dev docutils-common
sudo apt install build-essential python-dev python-setuptools python-pip python-smbus
sudo apt install libncursesw5-dev libgdbm-dev libc6-dev
sudo apt install zlib1g-dev libsqlite3-dev tk-dev
sudo apt install libssl-dev openssl
sudo apt install libffi-dev
```

#### Download/Unpack/Build/Install Python and Virtual Env
```
> py-insitu/bin/py-install --all
```

or run steps individually

```
> py-insitu/bin/py-install --download
> py-insitu/bin/py-install --make
> py-insitu/bin/py-install --install-python
> py-insitu/bin/py-install --install-env
```

#### Install python libraries contained in submodules
```
./bin/install-pylibs.sh
```

#### Run apps from open-hand package

In directory ./root/packages/open-hand

```
# reset mongo DB
./bin/run shadow reset
# Populate shadow db with 100 notes (research papers)
./bin/run shadow notes --slice 0 100
# run prediction over all authors
./bin/run predict --all
# show all canopies in system
./run show canopies
# display the author prediction for a given canopy
./run show canopy 'a mccallum'
```
