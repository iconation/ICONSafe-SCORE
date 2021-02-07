#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_option " -c <token contract>"
    usage_footer
    exit 1
}

function process {

    if [[ ("$network" == "") || ("$contract" == "") ]]; then
        print_usage
    fi

    package=iconsafe

    cli_config=$(cat ./config/${package}/${network}/tbears_cli_config.json | jq '.keyStore = "./config/'${package}'/localhost/keystores/operator.icx"')
    echo $cli_config >"${cli_config_file:=$(mktemp)}"

    command=$(cat <<-COMMAND
    tbears sendtx <(
        python ./scripts/score/dynamic_call/add_balance_tracker.py
            ${network@Q}
            ${contract@Q}
        )
        -c ${cli_config_file}
COMMAND
)

    txresult=$(./scripts/icon/txresult.sh -n "${network}" -c "${command}" -p ${package})
    echo -e "${txresult}"
}

# Parameters
while getopts "n:c:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
            ;;
        c)
            contract=${OPTARG}
            ;;
        *)
            print_usage 
            ;;
    esac 
done
shift $((OPTIND-1))

process