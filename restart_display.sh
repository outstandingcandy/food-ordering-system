date=`date "+%Y%m%d"`
cd /root/mmh/bbzdm_web/
BIN_NAME=item_display
ps -ef | sed -e 's/[\/]\+/\//g' | grep ${BIN_NAME} | awk '{if ($8 != "grep") print $2}' | while read pid; do kill -9 $pid; done
nohup python item_display.py > /tmp/item_display.${date}.log 2>&1 &
