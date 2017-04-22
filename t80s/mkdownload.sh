#!/usr/bin/env bash
python search_t80s_images.py "$1" | gsed 's/Z:\\images\\20151203\\//g' > tmp
grep http tmp | cut -f4 -d/ | sort | uniq > nights
filters=`grep Filter tmp  | cut -f2 -d= | cut -f1 -d, | sort | uniq | gsed ':a;N;$!ba;s/\n/ /g;s/[ ]\+/,/g;s/^,//g'`
echo '# '$filters

echo "# Allsky videos list:"
cat nights | gsed 's/^/# wget -c --no-check-certificate https:\/\/t80s_images:t80s_images_keywords_pass@splus.astro.ufsc.br\/allsky_gifs\/allsky_animation_/g;s/$/.gif/g'

for night in `cat nights`
do
    date=`echo $night | cut -c1-4`-`echo $night | cut -c5-6`-`echo $night | cut -c7-8`
    python search_t80s_images.py bias-date $date >> tmp
    python search_t80s_images.py skyflat-date $filters $date >> tmp
done
cat tmp
#rm nights tmp
