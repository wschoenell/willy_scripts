#!/usr/bin/env bash
python search_t80_images.py $1 > tmp
grep http tmp | cut -f4 -d/ | sort | uniq > nights
filters=`grep Filter tmp  | cut -f2 -d= | cut -f1 -d, | sort | uniq | sed ':a;N;$!ba;s/\n/ /g;s/[ ]\+/,/g;s/^,//g'`
for night in `cat nights`
do
    date=`echo $night | cut -c1-4`-`echo $night | cut -c5-6`-`echo $night | cut -c7-8`
    python search_t80_images.py bias-date $date >> tmp
    python search_t80_images.py skyflat-date $filters $date >> tmp
done
cat tmp
rm nights tmp