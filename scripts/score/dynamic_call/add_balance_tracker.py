import json
import sys

if __name__ == '__main__':
    network = sys.argv[1]
    token = sys.argv[2]

    score_address_txt = "./config/iconsafe/" + network + "/score_address.txt"

    call = json.loads(open("./calls/add_balance_tracker.json", "rb").read())
    call["params"]["to"] = open(score_address_txt, "r").read()

    call["params"]["data"]["params"]["token"] = token

    print(json.dumps(call))
