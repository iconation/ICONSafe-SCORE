#!/bin/bash

./scripts/build/build.py

cd build
rm -f *.zip
find . -maxdepth 1 -type d ! -path . ! -name .git | while read i; do zip -r -9 ${i}.zip $i; done
