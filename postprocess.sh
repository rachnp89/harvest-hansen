HEADER="country,region,iso,id,region_ascii"
rootdir="/data"

# clean up province names
python subnat_names.py $rootdir/gadm_regions_v3.shp  # UMD's modified GADM file
python subnat_names.py $rootdir/gadm2.shp  # raw GADM data

# sort and deduplicate the results 
sort $rootdir/gadm2_clean.csv | awk '!seen[$0]++' > $rootdir/gadm2_clean_deduped.csv
sort $rootdir/gadm_regions_v3_clean.csv | awk '!seen[$0]++' > $rootdir/gadm3_clean_deduped.csv

# add back header
echo $HEADER > $rootdir/gadm2_final.csv
cat $rootdir/gadm2_clean_deduped.csv >> $rootdir/gadm2_final.csv

echo $HEADER > $rootdir/gadm3_final.csv
cat $rootdir/gadm3_clean_deduped.csv >> $rootdir/gadm3_final.csv

echo "Upload files to cartodb:"
echo $(ls /data/gadm*_final.csv)
echo "Then run postprocess.py."