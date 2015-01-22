import pandas as pd

THRESHOLDS = [10, 15, 20, 25, 30, 50, 75]
STARTYEAR = 2001
ENDYEAR = 2012
NUMYEARS = ENDYEAR - STARTYEAR + 1

YEARS = xrange(STARTYEAR, ENDYEAR + 1)

HEADERSTART = ['region', 'country', 'iso', 'id', 'total_area', 'nodata',
               'land', 'water', 'gain']

FORESTCOVERSTART = len(HEADERSTART)  # first field after main fields - i.e. 9
LOSSFIELDSSTART = FORESTCOVERSTART + len(THRESHOLDS)  # i.e. 16


def gen_extent_2000_fields():
    return ['extent_%d_2000' % thresh for thresh in THRESHOLDS]


def gen_thresh_year_fields(prefix):
    field_str = '%s_%d_%d'  # e.g. extent_25_2005

    return [field_str % (prefix, t, y) for t in THRESHOLDS for y in YEARS]


def gen_header():
    extent_2000_fields = gen_extent_2000_fields()
    loss_fields = gen_thresh_year_fields('loss')

    return HEADERSTART + extent_2000_fields + loss_fields


def load(path):
    header = gen_header()
    return pd.read_csv(path, skiprows=1, header=0, names=header)

