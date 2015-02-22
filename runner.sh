rootdir="/data"
rawdata='data/country_admin_export_clean_Admin_2013_google_drive.csv'

subnat="umd_subnat.csv"
subnatfinal="umd_subnat_final.csv"
nat="umd_nat.csv"
natfinal="umd_nat_final.csv"
gadm2final="gadm2_final.csv"
gadm3final="gadm3_final.csv"

echo "Generate subnational data"
python main.py $rawdata $rootdir False
echo "Assign proper ids"
python postprocess.py $rootdir/$subnat $rootdir/$subnatfinal $rootdir/$gadm2final $rootdir/$gadm3final

echo "Generate national data"
python main.py $rawdata $rootdir True
echo "Assign proper iso codes"
isos="$rootdir/isos.txt"
cut -f 1,13 -d, $rootdir/$subnatfinal | awk '!seen[$0]++' > $isos
python postprocess_nat.py $rootdir/$nat $isos $rootdir/$natfinal
echo
echo



echo "Upload to CartoDB:"
echo "$rootdir/umd_subnat_final.csv"
echo "$rootdir/umd_nat_final.csv"