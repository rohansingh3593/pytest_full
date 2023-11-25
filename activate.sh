#!/bin/bash

set -e
set -o errexit
SCRIPTDIR=$(dirname $(realpath -s $0))
echo SCRIPTDIR path $SCRIPTDIR
WORKDIR=$(pwd)

echo Script directory $SCRIPTDIR

function build_venv()
{
   cd $SCRIPTDIR/pytest-VGS-venv
   bash -c ./mkvenv
   # git rev-parse HEAD > pytest-python3.8/gitrev
   cd $SCRIPTDIR
}

######################################################################
# setup venv

cd $SCRIPTDIR

# if [ ! -f  pytest-VGS-venv/activate ]; then
#    git submodule init
# fi
# git submodule update

if [ ! -f pytest-regress-venv/pytest-python3.8 ]; then
   build_venv
fi
# cd $SCRIPTDIR
pwd
# VENV_HASH=$(cat pytest-regress-venv/pytest-python3.8/gitrev)
# CUR_HASH=$(cd pytest-regress-venv;git rev-parse HEAD)
# if [ "$VENV_HASH" != "$CUR_HASH" ]; then
#   rm -rf pytest-regress-venv/pytest-python3.8
#   build_venv
# else
#   echo VENV is current,  entering pytest shell ${VENV_HASH}
# fi

# cd $SCRIPTDIR

# ./fixmtu
cd $WORKDIR 
export DI_TEST_DIR=$SCRIPTDIR
bash --init-file $SCRIPTDIR/.initfile.sh

