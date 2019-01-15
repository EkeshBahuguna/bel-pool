import requests
import json
import sys
import time

from constant import constants

# node to get the address of super delegate
NODE = constants.NODE
# node to perform payment
NODEPAY =constants.NODEPAY 
# public key of super representative
PUBKEY = constants.PUBKEY
# store the voting information
LOGFILE = constants.LOGFILE
# percentage to distribute
PERCENTAGE = constants.PERCENTAGE
# perform the payment after
MINPAYOUT =constants.MINPAYOUTINBEL 
#secret of super representative
SECRET = constants.SECRET
#second secret if any
SECONDSECRET = constants.SECONDSECRET
#country code of super representative
SENDERCOUNTRYCODE= constants.SENDERCOUNTRYCODE




def loadLog ():
	#load poollogs.json in read mode
	try:
		data = json.load (open (LOGFILE, 'r'))
	except:
		data = {
			"lastpayout": 0, 
			"accounts": {},
			"skip": []
		}
	return data
	
#to write into poollogs.json	
def saveLog (log):
	json.dump (log, open (LOGFILE, 'w'), indent=4, separators=(',', ': '))
	


def estimatePayouts (log):
	uri = NODE + '/api/delegates/forging/getForgedByAccount?generatorPublicKey=' + PUBKEY + '&start=' + str (log['lastpayout']) + '&end=' + str (int (time.time ()))
	#gets the forging details of super representative
	d = requests.get (uri)
	rew = d.json ()['rewards']
	forged = (int (rew) / 10000000000) * PERCENTAGE / 100
	print ('To distribute: %f BEL' % forged)
	
	if forged < 0.1:
		return []
	#get all the voters of this public key
	d = requests.get (NODE + '/api/delegates/voters?publicKey=' + PUBKEY).json ()
	
	weight = 0.0
	payouts = []
	
	for x in d['accounts']:
		if x['balance'] == '0' or x['address'] in log['skip']:
			continue
			
		weight += float (x['balance']) / 10000000000

	print ('Total weight is: %f' % weight)
	
	for x in d['accounts']:
		if int (x['balance']) == 0 or x['address'] in log['skip']:
			continue
			
		payouts.append ({ "address": x['address'], "balance": (float (x['balance']) / 10000000000 * forged) / weight})
		
	return payouts
	
	
def pool ():
	#loads polling.json in read mode
	log = loadLog ()
	
	
	topay = estimatePayouts(log)
	#check if there is nothing to pay
	if len (topay) == 0:
		print ('Nothing to distribute, exiting...')
		return
	#otherwise open payments.sh in write mode	
	f = open ('payments.sh', 'w')
	for x in topay:
		if not (x['address'] in log['accounts']) and x['balance'] != 0.0:
			log['accounts'][x['address']] = { 'pending': 0.0, 'received': 0.0 }

		#check if balance is lesser then minpayout and greater then 0, add it to pending amount 	
		if x['balance'] < MINPAYOUT and x['balance'] > 0.0:
			log['accounts'][x['address']]['pending'] += x['balance']
			continue
		#otherwise add the received amount to log file	
		log['accounts'][x['address']]['received'] += x['balance']	
		#write into payments.sh
		f.write ('echo Sending ' + str (x['balance']) + ' to ' + x['address'] + '\n')
		addr=x['address']
		data = { "secret": SECRET, "amount": int (x['balance'] * 10000000000), "recipientId": x['address'],"publicKey":PUBKEY,"recepientCountryCode": addr[-2:],"senderCountryCode":SENDERCOUNTRYCODE}
		if SECONDSECRET != None:
			data['secondSecret'] = SECONDSECRET
		#write josn data with curl command
		f.write ('curl -k -H  "Content-Type: application/json" -X PUT -d \'' + json.dumps (data) + '\' ' + NODEPAY + "/api/transactions\n\n")
		f.write ('sleep 3\n')
		
		#check the poollogs.json if it has pending amount which is greater then minpayout	
	for y in log['accounts']:
		if log['accounts'][y]['pending'] > MINPAYOUT:
			f.write ('echo Sending pending ' + str (log['accounts'][y]['pending']) + ' to ' + y + '\n')
			data = { "secret": SECRET, "amount": int (log['accounts'][y]['pending'] * 10000000000), "recipientId": y }
			if SECONDSECRET != None:
				data['secondSecret'] = SECONDSECRET
			f.write ('curl -k -H  "Content-Type: application/json" -X PUT -d \'' + json.dumps (data) + '\' ' + NODEPAY + "/api/transactions\n\n")
			#add another curl command to payment.sh
			log['accounts'][y]['received'] += log['accounts'][y]['pending']
			log['accounts'][y]['pending'] = 0.0
			f.write ('sleep 3\n')
			
	# Donations
	if 'donations' in log:
		for y in log['donations']:
			f.write ('echo Sending donation ' + str (log['donations'][y]) + ' to ' + y + '\n')
				
			data = { "secret": SECRET, "amount": int (log['donations'][y] * 10000000000), "recipientId": y }
			if SECONDSECRET != None:
				data['secondSecret'] = SECONDSECRET
			#if there are any donations in the
		f.write ('curl -k -H  "Content-Type: application/json" -X PUT -d \'' + json.dumps (data) + '\' ' + NODEPAY + "/api/transactions\n\n")
		f.write ('sleep 3\n')


	f.close ()
	#add last payout time to poollogs.json
	log['lastpayout'] = int (time.time ())
	
	print (json.dumps (log, indent=4, separators=(',', ': ')))
	
	if len (sys.argv) > 1 and sys.argv[1] == '-y':
		print ('Saving...')
		saveLog (log)
	else:
		yes = input ('save? y/n: ')
		if yes == 'y':
			saveLog (log)
			
			

if __name__ == "__main__":
	pool ()
