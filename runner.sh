rootdir="/data"
rawdata='data/Admin_2014.csv'
ecodata='data/Ecozone_2014.csv'

subnat="umd_subnat.csv"
subnatfinal="umd_subnat_final.csv"
nat="umd_nat.csv"
natfinal="umd_nat_final.csv"
eco="umd_eco.csv"
gadm2final="gadm2_final.csv"
gadm3final="gadm3_final.csv"

echo "Generate subnational data"
python main.py $rawdata $rootdir subnational
echo "Assign proper ids"
python postprocess.py $rootdir/$subnat $rootdir/$subnatfinal $rootdir/$gadm2final $rootdir/$gadm3final

echo "Generate national data"
python main.py $rawdata $rootdir national
echo "Assign proper iso codes"
isos="$rootdir/isos.txt"
cut -f 1,13 -d, $rootdir/$subnatfinal | awk '!seen[$0]++' > $isos
python postprocess_nat.py $rootdir/$nat $isos $rootdir/$natfinal

echo "Generate ecozone data"
python main.py $ecodata $rootdir eco

echo
echo



echo "Upload to CartoDB:"
echo "$rootdir/$subnatfinal"
echo "$rootdir/$natfinal"
echo "$rootdir/$eco"