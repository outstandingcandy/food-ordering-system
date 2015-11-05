export DISPLAY=:10
date=`date "+%Y%m%d"`
cd /root/mmh/shopping-guide/scrapy/bbzdm
BIN_NAME=scrapy
ps -ef | sed -e 's/[\/]\+/\//g' | grep "${BIN_NAME}" | awk '{if ($8 != "grep") print $2}' | while read pid; do [ -z $pid ] || kill -9  $pid; done
nohup sh crawler.sh > /tmp/crawler.${date}.log 2>&1 &
