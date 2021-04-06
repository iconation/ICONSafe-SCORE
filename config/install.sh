#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "Usage: install.sh [network (yeouido, mainnet, euljiro, ...)]"
    exit
fi

network=${1}

function getOperatorKeystorePath {
    network=${1}
    path="./keystores/${network}/"
    mkdir -p ${path}
    echo "${path}/operator.icx"
}

function generateOperatorKeystore {
    network=${1}
    echo -e "\n===[${network}]===================================="
    keystore=$(getOperatorKeystorePath ${network})
    # Check if file exists
    if [ -f "$keystore" ]; then
        echo "Operator wallet is already generated for ${network}."
    else
        echo "Generating operator keystore for ${network} ..."
        tbears keystore ${keystore}
        echo "New address generated : $(cat ${keystore} | jq '.address')"
    fi
    echo -e "===[/${network}]====================================\n"
}

generateOperatorKeystore ${network}

