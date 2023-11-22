#!/usr/bin/env bash
# first argument of the script is Xapian version (e.g. 1.4.19)
# stolen from  https://github.com/notanumber/xapian-haystack/blob/master/install_xapian.sh

source venv/bin/activate

VERSION=${1:-1.4.23}

if [ -z "$VERSION" ]; then
    echo "usage: $0 version_number" 1>&2
    exit 1
fi

# prepare
mkdir -p $VIRTUAL_ENV/packages && cd $VIRTUAL_ENV/packages

CORE=xapian-core-$VERSION
BINDINGS=xapian-bindings-$VERSION

# download
echo "Downloading source..."
curl -O https://oligarchy.co.uk/xapian/$VERSION/${CORE}.tar.xz
curl -O https://oligarchy.co.uk/xapian/$VERSION/${BINDINGS}.tar.xz

# extract
echo "Extracting source..."
tar xf ${CORE}.tar.xz
tar xf ${BINDINGS}.tar.xz

# install
echo "Installing Xapian-core..."
cd $VIRTUAL_ENV/packages/${CORE}
./configure --prefix=$VIRTUAL_ENV && make && make install

PYTHON_FLAG=--with-python3

# The bindings for Python require python-sphinx
echo "Installing Python-Sphinx..."
SPHINX2_FIXED_VERSION=1.4.12
if [ $(printf "${VERSION}\n${SPHINX2_FIXED_VERSION}" | sort -V | head -n1) = "${SPHINX2_FIXED_VERSION}" ]; then
    pip install sphinx
else
    pip install "sphinx<2"
fi

echo "Installing Xapian-bindings..."
cd $VIRTUAL_ENV/packages/${BINDINGS}
./configure --prefix=$VIRTUAL_ENV $PYTHON_FLAG && make && make install

# clean
cd $VIRTUAL_ENV
rm -rf $VIRTUAL_ENV/packages

# test
echo "Testing Xapian..."
python -c "import xapian"
