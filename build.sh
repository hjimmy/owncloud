#!/bin/bash
NAME="owncloud"
VERSION="6.0.9"
cp -rvf  *.spec ~/rpmbuild/SPECS/
if [ -d "$NAME" ]; then
   rm -rf "$NAME"
fi
cp -rf source $NAME
tar -cjf $NAME-$VERSION.tar.bz2 $NAME
cp -rvf  *.tar.bz2  ~/rpmbuild/SOURCES/
#cp -rvf patches/origin/*  ~/rpmbuild/SOURCES/
#cp -rvf patches/cs2c/*  ~/rpmbuild/SOURCES/
rpmbuild -bs --nodeps owncloud.spec
rpmbuild -ba owncloud.spec
rm -rf $NAME
rm -rf $NAME-$VERSION.tar.bz2

