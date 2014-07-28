#!/bin/sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Adjust to your environment
OPENSSL_SSL_LIBRARY=/opt/local/lib/libssl.dylib
OPENSSL_CRYPTO_LIBRARY=/opt/local/lib/libcrypto.dylib
OPENSSL_INCLUDE_DIR=/opt/local/include 

OUTPUT=$DIR/..
cd $OUTPUT

mkdir -p $OUTPUT/dist

mkdir -p build_armeabi
cd build_armeabi

cmake -DANDROID_ABI=armeabi -DCMAKE_TOOLCHAIN_FILE=../android.toolchain.cmake     -DWITH_SSL=1 -DOPENSSL_SSL_LIBRARY=${OPENSSL_SSL_LIBRARY}  -DOPENSSL_CRYPTO_LIBRARY=${OPENSSL_CRYPTO_LIBRARY} -DOPENSSL_INCLUDE_DIR=${OPENSSL_INCLUDE_DIR}  -DWITHOUT_SERVER=1 -DCMAKE_INSTALL_PREFIX:PATH=$OUTPUT/dist/armv5 $@ ../..
make
make install


cd ../
mkdir -p build_armeabi-v7a
cd build_armeabi-v7a

cmake -DANDROID_ABI=armeabi-v7a -DCMAKE_TOOLCHAIN_FILE=../android.toolchain.cmake -DWITH_SSL=1 -DOPENSSL_SSL_LIBRARY=${OPENSSL_SSL_LIBRARY}  -DOPENSSL_CRYPTO_LIBRARY=${OPENSSL_CRYPTO_LIBRARY} -DOPENSSL_INCLUDE_DIR=${OPENSSL_INCLUDE_DIR} -DWITHOUT_SERVER=1 -DCMAKE_INSTALL_PREFIX:PATH=$OUTPUT/dist/armv7a $@ ../..
make
make install

cd ../
mkdir -p build_x86
cd build_x86

cmake -DANDROID_ABI=x86 -DCMAKE_TOOLCHAIN_FILE=../android.toolchain.cmake -DWITH_SSL=1 -DOPENSSL_SSL_LIBRARY=${OPENSSL_SSL_LIBRARY}  -DOPENSSL_CRYPTO_LIBRARY=${OPENSSL_CRYPTO_LIBRARY} -DOPENSSL_INCLUDE_DIR=${OPENSSL_INCLUDE_DIR} -DWITHOUT_SERVER=1 -DCMAKE_INSTALL_PREFIX:PATH=$OUTPUT/dist/x86 $@ ../..
make
make install

# cmake -DANDROID_ABI=armeabi -DCMAKE_TOOLCHAIN_FILE=../scripts/toolchain-android-ndk-r8e.cmake $@ ../..

