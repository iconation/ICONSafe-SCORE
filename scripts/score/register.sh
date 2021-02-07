#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_option " -r : Name of the address"
    usage_option " -a : Address value"
    usage_footer
    exit 1
}

function process {

    if [[ ("$network" == "") || ("$name" == "")  || ("$address" == "") ]]; then
        print_usage
    fi

    package="address_registrar"
    cli_config=$(cat ./config/${package}/${network}/tbears_cli_config.json)
    cli_config=${cli_config//PACKAGE_NAME/${package}}
    echo $cli_config >"${cli_config_file:=$(mktemp)}"

    command=$(cat <<-COMMAND
    tbears sendtx <(
        python ./scripts/score/dynamic_call/register.py
            ${network@Q}
            ${name@Q}
            ${address@Q}
        )
        -c ${cli_config_file}
COMMAND
)

    txresult=$(./scripts/icon/txresult.sh -n "${network}" -c "${command}" -p address_registrar)
    echo -e "${txresult}"
}

# Parameters
while getopts "n:r:a:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
            ;;
        r)
            name=${OPTARG}
            ;;
        a)
            address=${OPTARG}
            ;;
        *)
            print_usage 
            ;;
    esac 
done
shift $((OPTIND-1))

process