#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_footer
    exit 1
}

function process {

    if [[ ("$network" == "") ]]; then
        print_usage
    fi

    echo "Resolving ADDRESS_REGISTRAR_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r ADDRESS_REGISTRAR_PROXY
    echo "Resolving ICONSAFE_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r ICONSAFE_PROXY
    echo "Resolving ADDRESS_BOOK_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r ADDRESS_BOOK_PROXY
    echo "Resolving BALANCE_HISTORY_MANAGER_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r BALANCE_HISTORY_MANAGER_PROXY
    echo "Resolving EVENT_MANAGER_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r EVENT_MANAGER_PROXY
    echo "Resolving TRANSACTION_MANAGER_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r TRANSACTION_MANAGER_PROXY
    echo "Resolving WALLET_OWNERS_MANAGER_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r WALLET_OWNERS_MANAGER_PROXY
    echo "Resolving WALLET_SETTINGS_MANAGER_PROXY ..."
    ./scripts/score/resolve.sh -n ${network} -r WALLET_SETTINGS_MANAGER_PROXY
}

# Parameters
while getopts "n:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
            ;;
        *)
            print_usage 
            ;;
    esac 
done
shift $((OPTIND-1))

process