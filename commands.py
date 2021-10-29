import re

MIN_UTXO = 2000000


def CARDANO_CLI_GET_TIP():
    return "cardano-cli query tip --testnet-magic 1097911063".split()


def CARDANO_CLI_HASH_POLICY():
    return "cardano-cli transaction policyid --script-file policy.json".split()


def CARDANO_CLI_PROTOCOL_PARAM():
    return "cardano-cli query protocol-parameters --testnet-magic 1097911063 --out-file protocol-params.json".split()


def CARDANO_CLI_GET_UTXO():
    return re.split("\s\s+",
                    """cardano-cli  query  utxo
            --address  addr_test1qzr8dxy9wy4lyjsrmhufkrcfhdxy27k329z66xs6xqjartzrym79ewvl0rem9r0wk8dtry43hj4nt0ghw09n60v40k3srv5uq3
            --testnet-magic  1097911063"""
                    )


def CARDANO_CLI_BUILD_TRANSACTION(fee, tx_hash, tx_ix, address, change, tokens, policy_id, slot, name):
    return re.split("\s\s+",
                    """cardano-cli  transaction  build-raw
            --fee  """ + str(fee) + """
            --tx-in  """ + tx_hash + """#""" + str(tx_ix) + """
            --tx-out  addr_test1qzr8dxy9wy4lyjsrmhufkrcfhdxy27k329z66xs6xqjartzrym79ewvl0rem9r0wk8dtry43hj4nt0ghw09n60v40k3srv5uq3+""" + str(change) + tokens + """
            --tx-out  """ + address + """+""" + str(MIN_UTXO) + """+1 """ + policy_id + """.""" + name + """
            --mint=1 """ + policy_id + """.""" + name + """
            --minting-script-file  policy.json
            --metadata-json-file  metadata.json
            --invalid-hereafter=""" + str(slot) + """
            --out-file  transaction.raw"""
                    )


def CARDANO_CLI_CALCULATE_FEE():
    return re.split("\s\s+",
                    """cardano-cli  transaction  calculate-min-fee
            --tx-body-file  transaction.raw
            --tx-in-count  1
            --tx-out-count  2
            --witness-count  2
            --testnet-magic  1097911063
            --protocol-params-file  protocol-params.json"""
                    )


def CARDANO_CLI_SIGN():
    return re.split("\s\s+",
                    """cardano-cli  transaction  sign
            --signing-key-file  payment/payment.skey
            --signing-key-file  policy/policy.skey
            --testnet-magic  1097911063
            --tx-body-file  transaction.raw
            --out-file  transaction.signed"""
                    )


def CARDANO_CLI_SUBMIT():
    return re.split("\s\s+",
                    """cardano-cli  transaction  submit
            --tx-file  transaction.signed
            --testnet-magic  1097911063"""
                    )
