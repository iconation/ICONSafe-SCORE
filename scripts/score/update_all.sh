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

    ./build.sh

    echo "Updating address_registrar..."
    ./scripts/score/update_score.sh -n ${network} -p address_registrar
    echo "Updating iconsafe..."
    ./scripts/score/update_score.sh -n ${network} -p iconsafe
    echo "Updating address_book..."
    ./scripts/score/update_score.sh -n ${network} -p address_book
    echo "Updating balance_history_manager..."
    ./scripts/score/update_score.sh -n ${network} -p balance_history_manager
    echo "Updating event_manager..."
    ./scripts/score/update_score.sh -n ${network} -p event_manager
    echo "Updating transaction_manager..."
    ./scripts/score/update_score.sh -n ${network} -p transaction_manager
    echo "Updating wallet_owners_manager..."
    ./scripts/score/update_score.sh -n ${network} -p wallet_owners_manager
    echo "Updating wallet_settings_manager..."
    ./scripts/score/update_score.sh -n ${network} -p wallet_settings_manager
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