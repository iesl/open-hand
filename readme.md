# OpenHand
## OpenReview Author Name Disambiguation

### Installation

##### Install locally built python to project-root/.local/python/

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

##### Install python libraries contained in submodules
```
./bin/install-pylibs.sh
```


In directory ./root/packages/open-hand

Run
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
