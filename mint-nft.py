# mint-nft.py

import falcon
import json
import logging
import subprocess
from subprocess import CalledProcessError
import pandas as pd
import numpy as np
import copy
import os
from falcon_cors import CORS
from commands import *
from templates import *

logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)


class GetTip(object):
    """GetTip class to return the status of cardano-cli"""

    def on_get(self, req, resp):
        try:
            tip_resp = run_command(CARDANO_CLI_GET_TIP())
            resp.status = falcon.HTTP_200
            resp.body = tip_resp
        except:
            resp.status = 500


class MintNFT(object):
    """Mint class to mint NFT based on parameters"""

    def on_post(self, req, resp):
        try:
            # Body validations
            body = {}
            if req.content_length:
                body = json.load(req.stream)
            else:
                raise Exception("No body found")
            if "name" in body:
                name = body["name"]
            else:
                raise Exception("Attribute name not found")
            if "address" in body:
                address = body["address"]
            else:
                raise Exception("Attribute address not found")
            logging.info("Minting process started")
            logging.info("Name:\t" + name)
            logging.info("Address:\t" + address)
            delete_files(["metadata.json", "policy.json", "utxo.txt",
                          "transaction.raw", "transaction.signed"])
            # Getting tip
            tip_resp = run_command(CARDANO_CLI_GET_TIP())
            tip = json.loads(tip_resp)
            slot = tip["slot"] + 120
            # Defining policy
            policy = copy.deepcopy(policy_template)
            policy["scripts"][1]["slot"] = slot
            write_file("policy.json", policy)
            # Hash of policy
            policy_hash = run_command(
                CARDANO_CLI_HASH_POLICY(), text=True).strip()
            logging.info("PolicyId:\t" + policy_hash)
            # Defining metadata
            metadata = copy.deepcopy(metadata_template)
            metadata["721"][policy_hash] = metadata["721"]["<policy_id>"]
            del metadata["721"]["<policy_id>"]
            write_file("metadata.json", metadata)
            # Getting UTxOs
            utxos_resp = run_command(CARDANO_CLI_GET_UTXO(), text=True)
            write_file("utxo.txt", utxos_resp, False)
            utxos = pd.read_table("utxo.txt", sep="\s\s+", engine="python", names=[
                                  "TxHash", "TxIx", "Amount"], skiprows=lambda x: x in [0, 1])
            utxos[["Lovelace", "Additional"]] = utxos["Amount"].str.split(
                pat=" lovelace ", expand=True)
            utxos = json.loads(utxos.to_json(orient="records"))
            for i in range(len(utxos)):
                # Finding UTxO
                tx_hash = utxos[i]["TxHash"]
                tx_ix = utxos[i]["TxIx"]
                logging.info("TxIn:\t" + tx_hash + "#" + str(tx_ix))
                lovelace = int(utxos[i]["Lovelace"])
                tokens = str(utxos[i]["Additional"])
                if tokens != "+ TxOutDatumHashNone":
                    tokens = tokens.replace("+ TxOutDatumHashNone", "")
                else:
                    tokens = ""
                logging.info("Lovelace:\t" + str(lovelace))
                # Calculating fees
                fee = 0
                change = 1
                run_command(CARDANO_CLI_BUILD_TRANSACTION(
                    fee, tx_hash, tx_ix, address, change, tokens, policy_hash, slot, name))
                fee_resp = run_command(
                    CARDANO_CLI_CALCULATE_FEE(), text=True, capture=True)
                fee = int(fee_resp.split()[0])
                logging.info("Fee:\t" + str(fee))
                if lovelace > fee + MIN_UTXO:
                    # Building, signing and submitting final transaction
                    change = lovelace - fee - MIN_UTXO
                    logging.info("Change:\t" + str(change))
                    run_command(CARDANO_CLI_BUILD_TRANSACTION(
                        fee, tx_hash, tx_ix, address, change, tokens, policy_hash, slot, name))
                    run_command(CARDANO_CLI_SIGN())
                    result = run_command(
                        CARDANO_CLI_SUBMIT(), text=True, capture=True)
                    logging.info("Minting process completed: " + result)
                    resp.body = '{ "status": "' + name + \
                        ' NFT minted successfully" }'
                    break
        except Exception as err:
            logging.error("Error on minting: " + str(err))
            resp.body = '{ "error": "' + str(err) + '" }'
            resp.status = falcon.HTTP_500


def run_command(command, text=False, capture=True):
    try:
        process = subprocess.run(
            command, check=True, text=text, capture_output=capture)
        if process.stdout != None:
            return process.stdout
        else:
            raise Exception(process.stderr)
    except Exception as err:
        logging.error("Error on command: " + str(err))
        raise err


def write_file(file, data, is_json=True):
    f = open(file, "w")
    if is_json:
        f.write(json.dumps(data))
    else:
        f.write(data)
    f.close()


def delete_file(file):
    if os.path.isfile(file):
        os.remove(file)
    else:
        logging.warning("File not found: " + file)


def delete_files(files):
    for file in files:
        delete_file(file)


cors = CORS(
    allow_origins_list=["*"],
    allow_methods_list=["GET", "POST"],
)
api = falcon.API(middleware=[cors.middleware])
api.add_route("/get-tip", GetTip())
api.add_route("/mint-nft", MintNFT())
