# Installation

## Description

Service in python to mint NFTs on tesnet using the standard [CIP-0025](https://github.com/cardano-foundation/CIPs/blob/master/CIP-0025/CIP-0025.md)
- Creates every time a new policyId based on the current slot.
- Receives two parameters:
    - name: name of the nft
    - address: address to which the nft is sent
- Additional to the nft, it also pays 2 ADA as minUtxo to the received address

## Configuration

1. Run a cardano-node
2. Create a `payment` folder and store your key files:
    - `payment.addr`
    - `payment.svkey`
3. Create a `policy` folder and store your policy files:
    - `policy.skey`

## Run

In my case, I'm using a virtual environment with python: 3.6.9

1. `source <path-to-virtual-env>/bin/activate`
2. `gunicorn --bind 0.0.0.0:5000 --timeout=300 -k gevent mint-nft:api --reload`