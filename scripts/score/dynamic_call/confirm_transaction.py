import json
import sys

if __name__ == '__main__':
    network = sys.argv[1]
    transaction_uid = sys.argv[2]

    score_address_txt = "./config/" + network + "/score_address.txt"

    call = json.loads(open("./calls/confirm_transaction.json", "rb").read())
    call["params"]["to"] = open(score_address_txt, "r").read()

    call["params"]["data"]["params"]["transaction_uid"] = transaction_uid

    print(json.dumps(call))
