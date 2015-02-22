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

```sql
UPDATE umd_subnat SET gain_perc = Null WHERE gain_perc = 'NULL';
UPDATE umd_subnat SET loss_perc = Null WHERE loss_perc = 'NULL';
UPDATE umd_subnat SET extent_perc = Null WHERE extent_perc = 'NULL';
UPDATE umd_subnat SET gain = Null WHERE gain = 'NULL';
UPDATE umd_subnat SET loss = Null WHERE loss = 'NULL';
UPDATE umd_subnat SET extent = Null WHERE extent = 'NULL';
```

Process GADM data:

```sql
WITH ids AS (
SELECT DISTINCT gadm3.iso iso, reg, gadm3.attribute id, gadm2.id_1 gadmid FROM gadm_regions_v3_clean gadm3
LEFT JOIN 
    (SELECT DISTINCT iso, country, id1 FROM gadm2_clean) gadm2 ON (gadm2.name_1 = gadm3.first_na_1 AND gadm2.iso = gadm3.first_iso)
ORDER BY gadm3.first_iso, gadm2.id_1
)
```

 
SELECT umd.*, ids.gadmid, ids.reg FROM umd_subnat umd
LEFT JOIN (SELECT DISTINCT gadm3.iso iso, gadm3.name1 name1, gadm3.name1_ascii name1_ascii,
           gadm3.id umd_id, gadm2.id1 gadmid
           FROM gadm_regions_v3_clean gadm3
           LEFT JOIN gadm2_clean ON (gadm2.name1_ascii = gadm3.name1_ascii AND gadm2.iso = gadm3.iso)
           ORDER BY gadm3.iso, gadm2.id1) ids
           ON (umd.id = ids.umd_id)
