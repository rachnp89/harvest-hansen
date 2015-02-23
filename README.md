## Introduction

Aggregate tree cover loss data from Hansen et al. (2013) has been handed over
to the GFW project for inclusion in the API.

## Preprocessing

Upload the spreadsheet to Google Drive, open it as a Google Docs spreadsheet, then download the admin sheet as CSV.

The original Excel spreadsheet is a bit unwieldy and doesn't handle non-ASCII
characters very well. And we need to convert the
file to CSV to take advantage of the rich Pandas `read_csv` function. Excel doesn't handle these characters very well by saving to CSV. But Google does.

## Processing

```python
>>> import main
>>> main('input.csv', '/tmp/hansen', national=True)
>>> main('input.csv', '/tmp/hansen', national=False)  # calculate subnational stats
```

## Postprocessing

We now have to deal with inconsistent naming conventions and ID fields,
accents, etc. between the UMD and GADM data. `subnat_names.py` helps by
removing accents from the province names, allowing for more straightforward
joins. We'll use these province names - along with ISO codes - to get the
proper ids. These province ids are not global, so the key in the API becomes
ISO code and province ID.

Check out postprocess.sh for details.

After running that, we can use the ID field in the raw UMD spreadsheet to extract
the correct province name for each record. We'll do the joins in CartoDB.

## CartoDB postprocessing

Process UMD data:

###### subnational table
```sql
UPDATE umd_subnat_final SET gain_perc = Null WHERE gain_perc = 'NULL';
ALTER TABLE umd_subnat_final RENAME COLUMN gain_perc TO gain_perc_str;
ALTER TABLE umd_subnat_final ADD COLUMN gain_perc float;
UPDATE umd_subnat_final SET gain_perc = gain_perc_str::float;
ALTER TABLE umd_subnat_final DROP COLUMN gain_perc_str;

UPDATE umd_subnat_final SET loss_perc = Null WHERE loss_perc = 'NULL';
ALTER TABLE umd_subnat_final RENAME COLUMN loss_perc TO loss_perc_str;
ALTER TABLE umd_subnat_final ADD COLUMN loss_perc float;
UPDATE umd_subnat_final SET loss_perc = loss_perc_str::float;
ALTER TABLE umd_subnat_final DROP COLUMN loss_perc_str;

UPDATE umd_subnat_final SET extent_perc = Null WHERE extent_perc = 'NULL';
ALTER TABLE umd_subnat_final RENAME COLUMN extent_perc TO extent_perc_str;
ALTER TABLE umd_subnat_final ADD COLUMN extent_perc float;
UPDATE umd_subnat_final SET extent_perc = extent_perc_str::float;
ALTER TABLE umd_subnat_final DROP COLUMN extent_perc_str;
```

###### national table
```sql
UPDATE umd_nat_final SET gain_perc = Null WHERE gain_perc = 'NULL';
ALTER TABLE umd_nat_final RENAME COLUMN gain_perc TO gain_perc_str;
ALTER TABLE umd_nat_final ADD COLUMN gain_perc float;
UPDATE umd_nat_final SET gain_perc = gain_perc_str::float;
ALTER TABLE umd_nat_final DROP COLUMN gain_perc_str;

UPDATE umd_nat_final SET loss_perc = Null WHERE loss_perc = 'NULL';
ALTER TABLE umd_nat_final RENAME COLUMN loss_perc TO loss_perc_str;
ALTER TABLE umd_nat_final ADD COLUMN loss_perc float;
UPDATE umd_nat_final SET loss_perc = loss_perc_str::float;
ALTER TABLE umd_nat_final DROP COLUMN loss_perc_str;

UPDATE umd_nat_final SET extent_perc = Null WHERE extent_perc = 'NULL';
ALTER TABLE umd_nat_final RENAME COLUMN extent_perc TO extent_perc_str;
ALTER TABLE umd_nat_final ADD COLUMN extent_perc float;
UPDATE umd_nat_final SET extent_perc = extent_perc_str::float;
ALTER TABLE umd_nat_final DROP COLUMN extent_perc_str;
```

Rename tables by removing the `_final` suffix, then make the permissions public.
