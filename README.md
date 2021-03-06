## Introduction

Aggregate tree cover loss data from Hansen et al. (2013) has been handed over
to the GFW project for inclusion in the API.

## Preprocessing

For ecozones or subnational spreadsheets, upload the spreadsheet to Google Drive, open it as a Google Docs spreadsheet, then download the admin sheet as CSV. The national data are generated based on subnational data.

The original Excel spreadsheets are a bit unwieldy and doesn't handle non-ASCII characters very well. And we need to convert the file to CSV to take advantage of the rich Pandas `read_csv` function. Excel doesn't handle these characters very well by saving to CSV. But Google does.

## Processing

It's simple! Make sure the /data directory exists on your machine, and you're all set. The datasets to process are in this repo. You can process them with `runner.sh`:

```shell
sh runner.sh
```

This script does all transformations from wide to long format, cleans up names, etc. It also deals with inconsistent naming conventions and ID fields,
accents, etc. between the UMD and GADM data. `subnat_names.py` helps by
removing accents from the province names, allowing for more straightforward
joins. We'll use these province names - along with ISO codes - to get the
proper ids. These province ids are not global, so the key in the API becomes
ISO code and province ID.

But all this is taken care of if you just run `sh runner.sh`.

## CartoDB postprocessing

Some field data types aren't parsed properly due to the nodata values mixed in with numbers and strings. We need to run a few SQL queries in CartoDB to clean things up and recast the offending columns as numbers.

###### Subnational table
```sql
UPDATE umd_subnat_final SET region = Null WHERE region = 'NULL';
UPDATE umd_subnat_final SET iso = Null WHERE iso = 'Null';
UPDATE umd_subnat_final SET id1 = Null WHERE id1 = 'Null';
ALTER TABLE umd_subnat_final ALTER COLUMN id1 SET DATA TYPE float USING to_number(id1, '999')
UPDATE umd_subnat_final SET loss_perc = Null WHERE loss_perc = 'NULL';
UPDATE umd_subnat_final SET gain_perc = Null WHERE gain_perc = 'NULL';
UPDATE umd_subnat_final SET extent_perc = Null WHERE extent_perc = 'NULL';
ALTER TABLE umd_subnat_final ALTER COLUMN loss_perc SET DATA TYPE float USING to_number(loss_perc, '99999999999999.99999999999');
ALTER TABLE umd_subnat_final ALTER COLUMN gain_perc SET DATA TYPE float USING to_number(gain_perc, '99999999999999.99999999999');
ALTER TABLE umd_subnat_final ALTER COLUMN extent_perc SET DATA TYPE float USING to_number(extent_perc, '99999999999999.99999999999');
```

###### National table
```sql
UPDATE umd_nat_final SET loss_perc = Null WHERE loss_perc = 'NULL'
ALTER TABLE umd_nat_final ALTER COLUMN loss_perc SET DATA TYPE float USING to_number(loss_perc, '99999999999999.99999999999')
UPDATE umd_nat_final SET gain_perc = Null WHERE gain_perc = 'NULL'
ALTER TABLE umd_nat_final ALTER COLUMN gain_perc SET DATA TYPE float USING to_number(gain_perc, '99999999999999.99999999999')
UPDATE umd_nat_final SET extent_perc = Null WHERE extent_perc = 'NULL'
ALTER TABLE umd_nat_final ALTER COLUMN extent_perc SET DATA TYPE float USING to_number(extent_perc, '99999999999999.99999999999')
```

## Final Step

Rename the tables by removing the `_final` suffix, then make the permissions public.
