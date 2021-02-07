#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_option " -s <sub_transactions.json> : Path to sub transactions json file"
    usage_footer
    exit 1
}

function process {

    if [[ ("$network" == "") || ("$subtx" == "") ]]; then
        print_usage
    fi

    command=$(cat <<-COMMAND
    tbears sendtx <(
        python ./scripts/score/dynamic_call/submit_transaction.py
            ${network@Q}
            ${subtx@Q}
        )
        -c ./config/iconsafe/${network}/tbears_cli_config.json
COMMAND
)

    txresult=$(./scripts/icon/txresult.sh -n "${network}" -c "${command}")
    echo -e "${txresult}"
}

# Parameters
while getopts "n:s:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
            ;;
        s)
            subtx=${OPTARG}
            ;;
        *)
            print_usage 
            ;;
    esac 
done
shift $((OPTIND-1))

process