import pandas as pd

THRESHOLDS = [10, 15, 20, 25, 30, 50, 75, 100]
STARTYEAR = 2001
ENDYEAR = 2013
NUMYEARS = ENDYEAR - STARTYEAR + 1

YEARS = xrange(STARTYEAR, ENDYEAR + 1)

HEADERSTART = ['name', 'code', 'area', 'nodata',  'land', 'water', 'loss0013',
               'gain0012']

FORESTCOVERSTART = len(HEADERSTART)  # first field after main fields - i.e. 9
LOSSFIELDSSTART = FORESTCOVERSTART + len(THRESHOLDS)  # i.e. 16


def gen_extent_2000_fields():
    return ['extent_%d_2000' % thresh for thresh in THRESHOLDS]


def gen_annual_loss_fields():
    return ['annual_loss_%d' % year for year in xrange(STARTYEAR, ENDYEAR + 1)]


def gen_loss_thresh_year_fields(prefix):
    field_str = '%s_%d_%d'  # e.g. extent_25_2005

    return [field_str % (prefix, t, y) for t in THRESHOLDS for y in YEARS]


def gen_header():
    annual_loss_fields = gen_annual_loss_fields()
    extent_2000_fields = gen_extent_2000_fields()
    loss_thresh_year_fields = gen_loss_thresh_year_fields('loss')

    h = HEADERSTART + annual_loss_fields + extent_2000_fields
    h += loss_thresh_year_fields

    return h


def load(path):
    header = gen_header()
    df = pd.read_csv(path, skiprows=1, header=0, names=header)
    df = df.rename(columns=dict(code='id'))
    print len(list(df.columns))
    print list(df.columns)
    return df
