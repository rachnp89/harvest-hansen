import os
import sys
import csv


import fiona
from unidecode import unidecode

# fields in customized GADM shapefile provided by Potapov
GADM3FIELDMAP = dict(iso='FIRST_ISO', country='FIRST_NAME', id1='ATTRIBUTE',
                     name1='FIRST_NA_1')

# fields in original GADM v2 shapefile
GADM2FIELDMAP = dict(iso='ISO', country='NAME_0', id1='ID_1',
                     name1='NAME_1')

FIELDMAP = dict(gadm3=GADM3FIELDMAP, gadm2=GADM2FIELDMAP)


def extract_fields(rec, field_map):
    iso = rec['properties'][field_map['iso']]
    country = rec['properties'][field_map['country']]
    id1 = int(rec['properties'][field_map['id1']])
    name1 = rec['properties'][field_map['name1']]

    # handle missing name1 value
    if not name1:
        name1 = u''
    name1_ascii = unidecode(name1)

    # print conversion results, if any
    if name1 != name1_ascii:
        print "%s ====> %s" % (name1, name1_ascii)

    # encode potentially funky fields properly
    country = country.encode('utf-8')
    name1 = name1.encode('utf-8')

    return dict(iso=iso, country=country, id1=id1,
                name1=name1, name1_ascii=name1_ascii)


def shp_to_csv(path, field_map):
    stub, ext = os.path.splitext(path)
    outpath = '%s_clean.csv' % (stub)
    fp = open(outpath, 'w')

    with fiona.drivers():
        with fiona.open(path) as shp:
            output_fields = field_map.keys()
            output_fields.append('name1_ascii')
            csv_out = csv.DictWriter(fp, fieldnames=output_fields)
            # csv_out.writeheader()

            for rec in shp:
                row_dict = extract_fields(rec, field_map)
                csv_out.writerow(row_dict)
    return


if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]
        if 'gadm2' in path:
            field_map = FIELDMAP['gadm2']
        elif 'gadm' in path and 'v3' in path:
            field_map = FIELDMAP['gadm3']
        else:
            raise Exception('%s "%s" %s' %
                            ('Path requires gadm2.shp or gadm_regions_v3.shp.',
                             path, 'is invalid.'))
        shp_to_csv(path, field_map)
    else:
        raise Exception('Please provide an input path.')
