import json
import sys

if __name__ == '__main__':
    network = sys.argv[1]
    sub_transactions = sys.argv[2]

    score_address_txt = "./config/iconsafe/" + network + "/score_address.txt"

    call = json.loads(open("./calls/submit_transaction.json", "rb").read())
    call["params"]["to"] = open(score_address_txt, "r").read()

    call["params"]["data"]["params"]["sub_transactions"] = open(sub_transactions).read()

    print(json.dumps(call))
