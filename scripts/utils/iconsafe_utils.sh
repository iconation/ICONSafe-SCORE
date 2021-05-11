
function set_registrar {
    package=$1
    registrar=$(cat ./config/address_registrar/${network}/score_address.txt)
    cli_config=$(cat ./config/${package}/${network}/tbears_cli_config.json | jq '.keyStore = "./config/keystores/'${network}'/operator.icx"' | jq '.deploy.scoreParams.registrar_address = "'${registrar}'"')
    echo -ne "$cli_config" > ./config/${package}/${network}/tbears_cli_config.json
}
