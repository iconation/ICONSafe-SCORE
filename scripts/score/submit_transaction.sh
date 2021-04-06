#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_option " -s <sub_transactions.json> : Path to sub transactions json file"
    usage_option " -p <package> : package name"
    usage_footer
    exit 1
}

function process {

    if [[ ("$network" == "") || ("$subtx" == "") || ("$package" == "") ]]; then
        print_usage
    fi

    cli_config=$(cat ./config/${package}/${network}/tbears_cli_config.json | jq '.keyStore = "./config/keystores/'${network}'/operator.icx"')
    echo $cli_config >"${cli_config_file:=$(mktemp)}"

    command=$(cat <<-COMMAND
    tbears sendtx <(
        python ./scripts/score/dynamic_call/submit_transaction.py
            ${network@Q}
            ${subtx@Q}
        )
        -c ${cli_config_file}
COMMAND
)

    txresult=$(./scripts/icon/txresult.sh -n "${network}" -p "${package}" -c "${command}")
    echo -e "${txresult}"
}

# Parameters
while getopts "n:s:p:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
            ;;
        s)
            subtx=${OPTARG}
            ;;
        p)
            package=${OPTARG}
            ;;
        *)
            print_usage 
            ;;
    esac 
done
shift $((OPTIND-1))

process