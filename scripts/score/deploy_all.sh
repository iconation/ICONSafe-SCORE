#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_footer
    exit 1
}

function set_registrar {
    package=$1
    registrar=$(cat ./config/address_registrar/${network}/score_address.txt)
    cli_config=$(cat ./config/${package}/${network}/tbears_cli_config.json | jq '.deploy.scoreParams.registrar_address = "'${registrar}'"')
    echo -ne "$cli_config" > ./config/${package}/${network}/tbears_cli_config.json
}

function process {

    if [[ ("$network" == "") ]]; then
        print_usage
    fi

    ./build.py

    echo "Deploying address_registrar..."
    ./scripts/score/deploy_score.sh -n ${network} -p address_registrar

    echo "Configuring Registrar..."
    set_registrar iconsafe
    set_registrar balance_history_manager
    set_registrar event_manager
    set_registrar transaction_manager
    set_registrar wallet_owners_manager
    set_registrar wallet_settings_manager

    echo "Deploying iconsafe..."
    ./scripts/score/deploy_score.sh -n ${network} -p iconsafe
    echo "Deploying balance_history_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p balance_history_manager
    echo "Deploying event_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p event_manager
    echo "Deploying transaction_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p transaction_manager
    echo "Deploying wallet_owners_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p wallet_owners_manager
    echo "Deploying wallet_settings_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p wallet_settings_manager
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