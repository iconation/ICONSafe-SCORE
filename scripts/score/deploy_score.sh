#!/bin/bash

. ./scripts/utils/utils.sh

function print_usage {
    usage_header ${0}
    usage_option " -n <network> : Network to use (localhost, yeouido, euljiro or mainnet)"
    usage_option " -p <package> : package to deploy"
    usage_footer
    exit 1
}

function process {
    if [[ ("$network" == "") || ("$package" == "") ]]; then
        print_usage
    fi

    cli_config=$(cat ./config/${package}/${network}/tbears_cli_config.json | jq '.keyStore = "./config/keystores/'${network}'/operator.icx"')
    echo $cli_config >"${cli_config_file:=$(mktemp)}"

    command="tbears deploy build/${package} -c ${cli_config_file}"

    txresult=$(./scripts/icon/txresult.sh -n "${network}" -c "${command}" -p ${package})
    exitcode=$?
    echo -e "${txresult}"

    if [ ${exitcode} -eq 0 ] ; then
        # Write the new score address to the configuration
        score_address=$(get_score_address "${txresult}")
        exitcode=$?
        if [ ${exitcode} -eq 0 ] ; then
            echo -e "New SCORE address detected : ${score_address}"
            echo -ne "${score_address}" > "./config/${package}/${network}/score_address.txt"
            info "SCORE ${package} successfully deployed !"
        else 
            error "An error occured. Exit code : ${exitcode}"
        fi
    else
        error "An error occured. Exit code : ${exitcode}"
    fi
}

# Parameters
while getopts "n:p:" option; do
    case "${option}" in
        n)
            network=${OPTARG}
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