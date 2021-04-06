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
    
    # Already registered at deploy
    # info "Registering address_registrar ..."
    # ./scripts/score/register.sh -n ${network} -r ADDRESS_REGISTRAR_PROXY -a $(cat ./config/address_registrar/${network}/score_address.txt)
    info "Registering iconsafe ..."
    ./scripts/score/register.sh -n ${network} -r ICONSAFE_PROXY -a $(cat ./config/iconsafe/${network}/score_address.txt)
    info "Registering address_book ..."
    ./scripts/score/register.sh -n ${network} -r ADDRESS_BOOK_PROXY -a $(cat ./config/address_book/${network}/score_address.txt)
    info "Registering balance_history_manager ..."
    ./scripts/score/register.sh -n ${network} -r BALANCE_HISTORY_MANAGER_PROXY -a $(cat ./config/balance_history_manager/${network}/score_address.txt)
    info "Registering event_manager ..."
    ./scripts/score/register.sh -n ${network} -r EVENT_MANAGER_PROXY -a $(cat ./config/event_manager/${network}/score_address.txt)
    info "Registering transaction_manager ..."
    ./scripts/score/register.sh -n ${network} -r TRANSACTION_MANAGER_PROXY -a $(cat ./config/transaction_manager/${network}/score_address.txt)
    info "Registering wallet_owners_manager ..."
    ./scripts/score/register.sh -n ${network} -r WALLET_OWNERS_MANAGER_PROXY -a $(cat ./config/wallet_owners_manager/${network}/score_address.txt)
    info "Registering wallet_settings_manager ..."
    ./scripts/score/register.sh -n ${network} -r WALLET_SETTINGS_MANAGER_PROXY -a $(cat ./config/wallet_settings_manager/${network}/score_address.txt)
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