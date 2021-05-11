#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_option " -c <command> : The T-Bears command to launch"
    usage_option " -p <package> : package name"
    usage_footer
    exit 1
}

function process {
    if [[ ("$network" == "") || ("$command" == "") || ("$package" == "") ]]; then
        print_usage
    fi

    # Execute T-Bears
    result=`eval ${command}`
    txhash=$(get_tx_hash "${result}")

    # Display commands
    info "> Command:"
    debug "$ ${command}"

    # Display result
    info "> Result:"
    if [[ "$txhash" != "0x" ]]; then
        debug " \`-> ${result}"
        debug " \`-> Getting result for TxHash: ${txhash} ..."
        # sleep 1

        # Wait for the txresult
        while true; do
            txresult=$(tbears txresult ${txhash} -c ./config/${package}/${network}/tbears_cli_config.json)
            if [[ "$(echo ${txresult} | grep 'Pending')" == "" && "$(echo ${txresult} | grep 'Executing')" == "" ]]; then
                if [[ "$(echo ${txresult} | grep 'Invalid params txHash')" == "" ]]; then
                    if [[ "$(echo ${txresult} | grep '"status": "0x0"')" == "" ]]; then
                        highlight " \`-> ${txresult}"
                        break
                    else
                        error " \`-> ${txresult}"
                        exit 1
                    fi
                fi
            fi
        done
    else
        error " \`-> ${result} "
        exit 1
    fi
}

# Parameters
while getopts "n:c:p:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
            ;;
        c)
            command=${OPTARG}
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