## Introduction

Aggregate tree cover loss data from Hansen et al. (2013) has been
handed over to the GFW project for inclusion in the API. The original
Excel spreadsheet was a bit unwieldy, so that was cleaned up and
exported as a CSV file.

That's where this project comes in. This CSV file contains aggregated
data for each province in the [GADM 2.0](http://gadm.org/version2)
data set. We need to aggregate these to countries and do a bit more
massaging, then upload the clean CSV file to CartoDB.

The CartoDB table needs to return results by year ([sample](http://wip.gfw-apis.appspot.com/datasets/hansen?layer=loss&geom=%7B%22type%22:%22Polygon%22,%22coordinates%22:%5B%5B%5B102.65350,-0.73499%5D,%5B103.75488,-0.89153%5D,%5B104.14764,-1.57527%5D,%5B102.77161,-1.47368%5D%5D%5D%7D&bust=1)) and cumulatively ([sample](http://wip.gfw-apis.appspot.com/datasets/hansen?layer=sum&geom=%7B%22type%22:%22Polygon%22,%22coordinates%22:%5B%5B%5B102.65350,-0.73499%5D,%5B103.75488,-0.89153%5D,%5B104.14764,-1.57527%5D,%5B102.77161,-1.47368%5D%5D%5D%7D&bust=1)).

## Data spec

1) Use columns where pixels > 50% forest cover are aggregated (they
have `_75` and `_100` in the name).  
2) The annual query should return loss area by year, and percent loss
by year as a share of total land area.

```sql
SELECT iso, year, sum(loss) loss, sum(loss_perc) loss_perc 
FROM hansen
WHERE iso = 'BRA'
GROUP BY iso, year
ORDER BY iso ASC, year ASC
```
3) The cumulative query should return cumulative loss as well as
loss and treecover in 2000, both as area and percent of land area.

```sql
SELECT iso, avg(treecover_2000) treecover_2000,
       avg(treecover_2000_perc) treecover_2000_perc, avg(gain) gain,
       avg(gain_perc) gain_perc, sum(loss) loss, sum(loss_perc) loss_perc
FROM hansen
WHERE iso = 'BRA'
GROUP BY iso
```

## Usage

From the repo:

```shell
mkdir /data/hansen
python main.py ~/Downloads/hansen/GFW_admin_stat.csv /data/hansen False
python main.py ~/Downloads/hansen/GFW_admin_stat.csv /data/hansen True

# upload a zipped copy of umd_nat.csv to cartodb

# postprocess subnational data
sh postprocess.sh
python postprocess.py /data/hansen/umd_subnat.csv /data/hansen/umd_subnat_final.csv /data/gadm2_final.csv /data/gadm3_final.csv

# upload a zipped copy of umd_subnat_final.csv to cartodb

# change column data types, set permissions, and rename tables
# in that order
```

## Postprocessing

Upload the output file to CartoDB. It's not very big, so there's no
need to compress it. All fields will start out as string type, so we need to recast numeric fields appropriately:

```sql
ALTER TABLE hansen ADD COLUMN year_int int;
UPDATE hansen SET year_int = year::int;
ALTER TABLE hansen DROP COLUMN year;
ALTER TABLE hansen RENAME COLUMN year_int TO year;

ALTER TABLE hansen ADD COLUMN extent_gt_25_float float;
UPDATE hansen SET extent_gt_25_float = extent_gt_25::float;
ALTER TABLE hansen DROP COLUMN extent_gt_25;
ALTER TABLE hansen RENAME COLUMN extent_gt_25_float TO extent_gt_25;

ALTER TABLE hansen ADD COLUMN gain_float float;
UPDATE hansen SET gain_float = gain::float;
ALTER TABLE hansen DROP COLUMN gain;
ALTER TABLE hansen RENAME COLUMN gain_float TO gain;

ALTER TABLE hansen ADD COLUMN gain_annual_float float;
UPDATE hansen SET gain_annual_float = gain_annual::float;
ALTER TABLE hansen DROP COLUMN gain_annual;
ALTER TABLE hansen RENAME COLUMN gain_annual_float TO gain_annual;

ALTER TABLE hansen ADD COLUMN gain_perc_float float;
UPDATE hansen SET gain_perc_float = gain_perc::float;
ALTER TABLE hansen DROP COLUMN gain_perc;
ALTER TABLE hansen RENAME COLUMN gain_perc_float TO gain_perc;

ALTER TABLE hansen ADD COLUMN loss_gt_0_float float;
UPDATE hansen SET loss_gt_0_float = loss_gt_0::float;
ALTER TABLE hansen DROP COLUMN loss_gt_0;
ALTER TABLE hansen RENAME COLUMN loss_gt_0_float TO loss_gt_0;

ALTER TABLE hansen ADD COLUMN loss_gt_25_float float;
UPDATE hansen SET loss_gt_25_float = loss_gt_25::float;
ALTER TABLE hansen DROP COLUMN loss_gt_25;
ALTER TABLE hansen RENAME COLUMN loss_gt_25_float TO loss_gt_25;

ALTER TABLE hansen ADD COLUMN loss_gt_50_float float;
UPDATE hansen SET loss_gt_50_float = loss_gt_50::float;
ALTER TABLE hansen DROP COLUMN loss_gt_50;
ALTER TABLE hansen RENAME COLUMN loss_gt_50_float TO loss_gt_50;

ALTER TABLE hansen ADD COLUMN loss_perc_gt_25_float float;
UPDATE hansen SET loss_perc_gt_25_float = loss_perc_gt_25::float;
ALTER TABLE hansen DROP COLUMN loss_perc_gt_25;
ALTER TABLE hansen RENAME COLUMN loss_perc_gt_25_float TO loss_perc_gt_25;
```

Then you're all set. Go have a beer.
