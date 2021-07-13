#!/bin/bash

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     sharepath=$PWD;;
    CYGWIN*)    sharepath=$(cygpath -wa $PWD);;
    MINGW*)     sharepath=$(cygpath -wa $PWD);;
    *)          machine="UNKNOWN:${unameOut}"
esac

docker rm -v ${PWD##*/}
docker run -v ${sharepath}:/score --name ${PWD##*/} -it -p 9000:9000 tbears_v2