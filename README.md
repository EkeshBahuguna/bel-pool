# Rise pool distribution software
This software is created by oodles technologies for reward dis

## Configuration
edit constants/constants.py and modify the first lines with your settings:

- PUBKEY: your delegate pubkey
- PERCENTAGE: percentage to distribute
- SECRET: your secret
- SECONDSECRET: your second secret or none if disabled
- NODE: node where you get forging info
- NODEPAY: node used for payments
- MINPAYOUT: the minimum amount for a payout
- SENDERCOUNTRYCODE: country code of your delegate


## Running it

First install requests:

`pip3 install requests`

Then start it:

`python3 belpool.py`

It produces a file "payments.sh" with all payments shell commands. Run this file with:

`bash payments.sh`

The payments will be broadcasted (every 10 seconds). At the end you can move your generated
poollogs.json to docs/poollogs.json 

## Batch mode

The script is also runnable by cron using the -y argument:

`python3 belpool.py -y`

There is also a 'batch.sh' file which run belpool, then payments.sh and copy the poollogs.json
in the docs folder.