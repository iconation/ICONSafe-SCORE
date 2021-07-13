#!/bin/bash

. ./scripts/utils/utils.sh
. ./scripts/utils/iconsafe_utils.sh

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

    # Check operator balance
    warning "/\!\\ BEFORE DEPLOYING, PLEASE MAKE SURE YOUR OPERATOR ADDRESS HAVE AT LEAST 200 ICX AS ICONSAFE WILL DEPLOY 8 CONTRACTS !"
    balances=$(tbears balance $(cat ./config/keystores/${network}/operator.icx | jq -r .address) -c ./config/iconsafe/${network}/tbears_cli_config.json | head -2 | tail -1)
    python3 -c "print('Operator balance: %f ICX' % ($(echo $balances | cut -d ":" -f2).0 / 10**18))"

    # Build && deploy everything
    ./build.sh

    echo "Deploying address_registrar..."
    ./scripts/score/deploy_score.sh -n ${network} -p address_registrar

    echo "Configuring Registrar..."
    set_registrar iconsafe
    set_registrar address_book
    set_registrar balance_history_manager
    set_registrar event_manager
    set_registrar transaction_manager
    set_registrar wallet_owners_manager
    set_registrar wallet_settings_manager

    echo "Deploying iconsafe..."
    ./scripts/score/deploy_score.sh -n ${network} -p iconsafe
    echo "Deploying address_book..."
    ./scripts/score/deploy_score.sh -n ${network} -p address_book
    echo "Deploying balance_history_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p balance_history_manager
    echo "Deploying event_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p event_manager
    echo "Deploying transaction_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p transaction_manager
    echo "Deploying wallet_settings_manager..."
    ./scripts/score/deploy_score.sh -n ${network} -p wallet_settings_manager

    echo "Deploying wallet_owners_manager..."
    operator=$(cat ./config/keystores/${network}/operator.icx | jq .address)
    wallet_owners_manager_config=$(cat ./config/wallet_owners_manager/${network}/tbears_cli_config.json | jq '.deploy.scoreParams.owners[0].address = '${operator}'' | jq '.deploy.scoreParams.owners[0].name = "Operator"' | jq '.deploy.scoreParams.owners_required = "0x1"')
    echo -ne "$wallet_owners_manager_config" > ./config/wallet_owners_manager/${network}/tbears_cli_config.json
    ./scripts/score/deploy_score.sh -n ${network} -p wallet_owners_manager
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