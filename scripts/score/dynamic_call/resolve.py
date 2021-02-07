import json
import sys

if __name__ == '__main__':
    network = sys.argv[1]
    name = sys.argv[2]
    score_address_txt = "./config/address_registrar/" + network + "/score_address.txt"

    call = json.loads(open("./calls/resolve.json", "rb").read())
    call["params"]["to"] = open(score_address_txt, "r").read()

    call["params"]["data"]["params"]["name"] = name

    print(json.dumps(call))
