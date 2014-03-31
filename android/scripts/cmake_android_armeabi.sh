#!/bin/sh

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

OUTPUT=$DIR/..
cd $OUTPUT

mkdir -p $OUTPUT/dist

mkdir -p build_armeabi
cd build_armeabi

cmake -DANDROID_ABI=armeabi -DCMAKE_TOOLCHAIN_FILE=../android.toolchain.cmake -DWITHOUT_TESTAPPS=1 -DWITH_SSL=0 -DWITHOUT_SERVER=1 -DCMAKE_INSTALL_PREFIX:PATH=$OUTPUT/dist/armv5 $@ ../..
make -j8
make install


cd ../
mkdir -p build_armeabi-v7a
cd build_armeabi-v7a

cmake -DANDROID_ABI=armeabi-v7a -DCMAKE_TOOLCHAIN_FILE=../android.toolchain.cmake -DWITHOUT_TESTAPPS=1 -DWITH_SSL=0 -DWITHOUT_SERVER=1 -DCMAKE_INSTALL_PREFIX:PATH=$OUTPUT/dist/armv7a $@ ../..
make -j8
make install

cd ../
mkdir -p build_x86
cd build_x86

cmake -DANDROID_ABI=x86 -DCMAKE_TOOLCHAIN_FILE=../android.toolchain.cmake -DWITHOUT_TESTAPPS=1 -DWITH_SSL=0 -DWITHOUT_SERVER=1 -DCMAKE_INSTALL_PREFIX:PATH=$OUTPUT/dist/x86 $@ ../..
make -j8
make install

# cmake -DANDROID_ABI=armeabi -DCMAKE_TOOLCHAIN_FILE=../scripts/toolchain-android-ndk-r8e.cmake $@ ../..

