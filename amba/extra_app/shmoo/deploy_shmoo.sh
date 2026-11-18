#!/bin/sh
# script 
cp start_shmood.sh shmood cec_shmoo_loading.sh  cec_auto_shmoo.sh test_logger shmoo_valid_log.sh  cec_run_shmoo_test.sh /usr/local/bin
# binary 
cp shmood receiver test_logger  /usr/local/bin
# config
cp shmoo.json /etc	 


# external
cp jq 7zz /usr/local/bin



cp offset_shmoo.sh  dynamic_shmoo.sh /usr/local/bin


cp -af shmoo/bst_fw  shmoo/Progress.txt /root
cp shmood.service receiver.service /usr/lib/systemd/system/
systemctl enable shmood
systemctl enable receiver