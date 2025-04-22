touch api.log
nohup docker compose --profile dev up > output.log 2>&1 &
echo $! > pid.txt
