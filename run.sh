DATE=$(/bin/date '+%Y%m%d')

nohup /usr/bin/python bot.py &
echo $! > nohup.pid

# STOP
# kill -9 `cat nohup.pid`
# rm nohup.pid 