#!/bin/bash

set -e
mkdir -p "$HOME/.icu_cache"
mkdir -p "$HOME/lib"
cd "$HOME/.icu_cache"
if [ ! -d "icu4c-57_1-src" ]; then
    echo "Downloading latest ICU – please wait."
    wget --quiet http://download.icu-project.org/files/icu4c/57.1/icu4c-57_1-src.tgz

    # checking md5sum!
    echo "976734806026a4ef8bdd17937c8898b9 *icu4c-57_1-src.tgz" | md5sum -c -

    tar xf icu4c-57_1-src.tgz
    mv icu icu4c-57_1-src
fi

[ "$TRAVIS" == "true" ] && PREFIX="$HOME/lib" || PREFIX="/usr"

echo "Compiling and installing ICU to $PREFIX"
cd icu4c-57_1-src/source
./configure --prefix=$PREFIX && make &&  make install
echo "ICU successfully installed."
