python3 belpool.py -y
bash payments.sh
cp poollogs.json docs/poollogs.json
echo -e "\ncurrent log file copied to docs directory"
current_time=$(date "+%Y.%m.%d-%H.%M.%S")
cp poollogs.json history/$current_time.json
echo -e "\npoollogs stored into history"


#run this script as a cron job