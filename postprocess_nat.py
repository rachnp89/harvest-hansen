import sys
import copy
import csv

from unicodedict import UnicodeDictReader, UnicodeDictWriter

import postprocess


def gen_iso_dict(isopath):
    d = dict()
    fp = UnicodeDictReader(open(isopath, 'r'))

    for row in fp:
        d[row['country']] = row['iso']
    return d


def get_fieldnames(path):
    c = csv.DictReader(open(path, 'r'))
    fields = c.fieldnames
    fields.append('iso')
    return fields


def main(natpath, isopath, outpath):
    nat = UnicodeDictReader(open(natpath, 'r'))
    iso_dict = gen_iso_dict(isopath)
    fields = get_fieldnames(natpath)

    nat_final = UnicodeDictWriter(open(outpath, 'w'), fieldnames=fields)
    nat_final.writeheader()

    for row in nat:
        new_row = copy.copy(row)
        new_row = postprocess.cleanup_names(new_row)
        try:
            new_row['iso'] = iso_dict[new_row['country']]
        except KeyError:
            new_row['iso'] = 'Null'
            print new_row['country']

        nat_final.writerow(new_row)

    print 'Done'


if __name__ == '__main__':

    natpath = sys.argv[1]
    isopath = sys.argv[2]
    outpath = sys.argv[3]

    main(natpath, isopath, outpath)
