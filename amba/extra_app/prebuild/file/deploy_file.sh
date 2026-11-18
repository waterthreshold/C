#!/bin/sh

mkdir -p /usr/local/share/misc/
cp magic.mgc /usr/local/share/misc/
cp libmagic.so.1.0.0 /usr/lib
ln -sf /usr/lib/libmagic.so.1.0.0  /usr/lib/libmagic.so.1
ln -sf /usr/lib/libmagic.so.1 usr/lib/libmagic.so
cp file /usr/bin