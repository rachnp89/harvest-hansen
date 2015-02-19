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
    print path
    fp = UnicodeDictReader(open(path, 'r'))

    for row in fp:
        k = gen_key(row)
        d[k] = row

    return d


def update_row(row, merge_dict):
    try:
        new_row = copy.deepcopy(row)
        k = int(new_row['id'])
        gadm_data = merge_dict[k]
        new_row['region'] = gadm_data['region']
        new_row['id1'] = gadm_data['id']
        return new_row
    except KeyError:
        new_row['id1'] = ''
        return new_row



def process_csv(fp, fp_out, gadm_dict):
    n = 0
    for row in fp:
        new_row = update_row(row, gadm_dict)
        fp_out.writerow(new_row)
        n += 1
        if n % 1000 == 0:
            print "Processed %d rows" % n

    print "Processed %d rows total" % n
    return fp_out


def get_fieldnames(path):
    c = csv.DictReader(open(path, 'r'))
    print path
    fields = c.fieldnames
    fields.append('id1')
    return fields


def merge_dicts(gadm_path, hansen_path):
    """Generate lookup dictionary from Hansen's ids to GADM2 names."""
    d = dict()
    gadm = gen_dict(gadm_path)
    hansen = gen_dict(hansen_path)
    print len(hansen)
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

    subnat = csv.DictReader(open(inpath, 'r'))

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