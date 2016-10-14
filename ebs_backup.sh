#!/bin/bash
RADIO_ADDR="rtmp://ebsandroid.ebs.co.kr/fmradiofamilypc/familypc1m"
RADIO_NAME="ebs_radio"

PROGRAM_NAME=$1
RECORD_MINS=$(($2 * 60))
DEST_DIR=$3

#REC_DATE=`date +%Y%m%d-%H%M`
REC_DATE=`TZ=Asia/Seoul date +%Y%m%d-%H%M`
TEMP_FLV=/ebs/`date +%Y%m%d-%H%M`

M4A_FILE_NAME=$PROGRAM_NAME"_"$REC_DATE.m4a

rtmpdump -r $RADIO_ADDR -B $RECORD_MINS -o $TEMP_FLV
ffmpeg -i $TEMP_FLV -vn -acodec copy $M4A_FILE_NAME > /dev/null 2>&1

rm $TEMP_FLV

mkdir -p $DEST_DIR
mv $M4A_FILE_NAME $DEST_DIR
