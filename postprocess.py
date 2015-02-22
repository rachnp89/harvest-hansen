# encoding: UTF-8

import sys
import copy
import csv
from unicodedict import UnicodeDictReader, UnicodeDictWriter


def gen_key(row):
    try:
        return '%s %s' % (row['iso'], row['region_ascii'])
    except KeyError:
        region = row['region']
        return '%s %s' % (row['iso'], region)


def gen_dict(path):
    d = dict()
    fp = UnicodeDictReader(open(path, 'r'))

    for row in fp:
        k = gen_key(row)
        d[k] = row

    return d


def cleanup_names(new_row):
    '''Cleanup names - easier postprocessing without commas.'''
    if new_row['country'] == 'Virgin Islands, U.S.':
        new_row['country'] = 'U.S. Virgin Islands'

    if new_row['country'] == 'Bonaire, Saint Eustatius and Saba':
        new_row['country'] = 'Bonaire Saint Eustatius and Saba'

    if new_row['country'] == 'Spratly Islands' or new_row['country'] == 'Clipperton Islands':
        new_row['iso'] = 'Null'

    if new_row['country'] == u'Curaчao':
        new_row['country'] = u'Curaçao'

    if new_row['country'] == u'Saint-Barthщlemy':
        new_row['country'] = u'Saint-Barthélemy'

    if new_row['country'] == u"CЇte d'Ivoire":
        new_row['country'] = u"Côte d'Ivoire"

    try:
        if new_row['region'] == 'Southern Nations, Nationalities and Peoples':
            new_row['region'] = 'Southern Nations Nationalities and Peoples'
    except KeyError:
        # processing national data - no region
        pass

    return new_row


def update_row(row, merge_dict):
    try:
        new_row = copy.deepcopy(row)
        k = int(new_row['id'])
        gadm_data = merge_dict[k]
        new_row['country'] = gadm_data['country']
        new_row['region'] = gadm_data['region']
        new_row['id1'] = gadm_data['id']
        new_row['iso'] = gadm_data['iso']

        new_row = cleanup_names(new_row)

        return new_row
    except KeyError:
        # for "Outside any", "Eland, Finland", and "Mayaguez, Puerto Rico"
        if new_row['country'] == 'Puerto Rico':
            new_row['id1'] = 'Null'
            new_row['iso'] = 'PRI'
        elif new_row['country'] == 'Finland':
            new_row['id1'] = 'Null'
            new_row['iso'] = 'FIN'
        else:
            new_row['id1'] = 'Null'
            new_row['iso'] = 'Null'
        return new_row


def process_csv(fp, fp_out, gadm_dict):
    n = 0
    skip = 0
    for row in fp:
        new_row = update_row(row, gadm_dict)
        fp_out.writerow(new_row)
        n += 1
        if n % 1000 == 0:
            print "Processed %d rows" % n

    print "Processed %d rows total" % n
    print "Skipped %d rows" % skip
    return fp_out


def get_fieldnames(path):
    c = csv.DictReader(open(path, 'r'))
    fields = c.fieldnames
    fields.append('id1')
    fields.append('iso')
    return fields


def merge_dicts(gadm_path, hansen_path):
    """Generate lookup dictionary from Hansen's ids to GADM2 names."""
    d = dict()
    gadm = gen_dict(gadm_path)
    hansen = gen_dict(hansen_path)
    for k in hansen:
        try:
            new_k = int(hansen[k]['id'])
            d[new_k] = gadm[k]
        except KeyError:
            print "Skipping %s" % k
        except ValueError:
            print "Skipping %s" % str(hansen[k])
    return d


def main(inpath, outpath, gadmpath, hansen_path):
    d = merge_dicts(gadmpath, hansenpath)

    subnat = UnicodeDictReader(open(inpath, 'r'))

    fields = get_fieldnames(inpath)

    outcsv = UnicodeDictWriter(open(outpath, 'w'), fieldnames=fields)
    outcsv.writeheader()
    process_csv(subnat, outcsv, d)

    print 'Done'

    return


if __name__ == '__main__':

    inpath = sys.argv[1]
    outpath = sys.argv[2]
    gadmpath = sys.argv[3]
    hansenpath = sys.argv[4]

    main(inpath, outpath, gadmpath, hansenpath)

"""
import postprocess
import unidecode

def func():
    thecsv = 'gadm2_clean_deduped.csv'
    outcsv = '/home/robin/Dropbox/tmp/clean.csv'
    k = 'SLV Cuscatlan'
    d = postprocess.gen_dict(thecsv)
    outcsv = UnicodeDictWriter(open(outcsv, 'w'), fieldnames=d[k].keys())
    outcsv.writeheader()
    outcsv.writerow(d[k])
    return

def func1():
    thecsv = '/tmp/hansen/umd_subnat.csv'
    c = csv.DictReader(open(thecsv, 'r'))
    for row in c:




import postprocess

gadm = '/data/gadm2_final.csv'
hansen = '/data/gadm3_final.csv'
a = postprocess.merge_dicts(gadm, hansen)

"""