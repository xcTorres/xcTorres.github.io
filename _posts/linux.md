# lsof

# netstat

ps aux | sed 1d | awk '{print "fd_count=$(lsof -p " $2 " | wc -l) && echo " $2 " $fd_count"}' | xargs -I {} bash -c {}


netstat -anp  | grep 10.34.44.12 | wc -l



locust -f ./tests/locust/locust_test.py  --csv=load_test \
                                             --headless \
                                             --reset-stats \
                                             --host=http://localhost:8020 \
                                             -u 10  \
                                             -r 1
