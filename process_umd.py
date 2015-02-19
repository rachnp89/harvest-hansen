import os
import sys

import pandas as pd

import common

# header details
OUTPUTFIELDS = ['region', 'country', 'iso', 'id', 'year', 'thresh', 'extent',
                'extent_offset', 'extent_perc', 'gain', 'loss', 'gain_perc',
                'loss_perc']


def calc_extents(df, thresh):
    """Calculate extent by year."""

    extent = 'extent_%d_%d'  # e.g. 'extent_25_2005'
    loss = 'loss_%d_%d'  # e.g. 'loss_25_2005'

    for year in common.YEARS:
        new_ext = df[extent % (thresh, year - 1)] - df[loss % (thresh, year)]
        df[extent % (thresh, year)] = new_ext

    return df


def calc_offset_extents(df, thresh):
    """Calculate extent by year, offsetting extent one year in the past for
    purposes of percentage calculations. This way, 2001 loss percent can be
    calculated with 2000 extent in the denominator."""

    extent = 'extent_%d_%d'
    extent_offset = 'extent_offset_%d_%d'

    # set year 2000 offset
    df[extent_offset % (thresh, 2000)] = df[extent % (thresh, 2000)]

    for year in common.YEARS:
        new_ext = df[extent % (thresh, year - 1)]
        df[extent_offset % (thresh, year)] = new_ext

    return df


def wide_to_long(df, thresh):
    """Reshape dataframe from wide to long format."""

    fields = ['extent', 'extent_offset', 'loss']
    stubs = ['%s_%d_' % (prefix, thresh) for prefix in fields]
    new_names = dict(zip(stubs, fields))

    df = pd.wide_to_long(df, stubs, i='id', j='year').reset_index()

    df = df.rename(columns=new_names)

    return df


def calc_annual_gain(df):
    """Calculate annual gain field."""
    df['gain'] = df['gain'] / float(common.NUMYEARS)
    df = set_2000_0(df, 'gain')

    return df


def set_2000_0(df, field):
    """Set year 2000 to zero for given field. Use with loss/gain percentage
    since year 2000 has no meaning."""

    idx = df['year'] == 2000
    subdf = df[idx]
    subdf[field] = 0
    df.update(subdf)

    return df


def calc_perc(df, field, thresh, denominator='extent_offset'):
    '''Calculate given field as share of tree cover extent or
    another denominator for a given threshold.

    The dataframe should already be in long form, so this is
    effectively a percentage for a particular year.'''

    new_field = '%s_perc' % field
    df[new_field] = (df[field] / df[denominator]) * 100

    return df


def save_csv(df, thresh, out_dir):
    """Output to CSV with threshold in filename."""

    # generate output path
    fname = 'umd_%d.csv' % thresh
    out_path = os.path.join(out_dir, fname)

    # output to threshold-specific CSV
    df.to_csv(out_path, index=False, na_rep='NULL')

    return df


def main(path, thresh, national):
    '''Generate long-form datasets with year, thresh, gain, loss,
    treecover (and associated percentages).'''
    df = common.load(path)

    if national:
        print "Processing national-level data"
        df.drop('region', axis=1)
        df = df.groupby(['country', 'iso']).sum().reset_index()
    else:
        print "Processing subnational-level data"
        pass

    df = calc_extents(df, thresh)
    df = calc_offset_extents(df, thresh)
    df = wide_to_long(df, thresh)
    df = calc_annual_gain(df)
    df = set_2000_0(df, 'loss')

    # percents default to offset extent as denominator
    df = calc_perc(df, 'loss', thresh)
    df = calc_perc(df, 'gain', thresh)
    # tree cover as share of country's land area
    df = calc_perc(df, 'extent', thresh, denominator='land')
    df['thresh'] = thresh
    df = df.loc[:, OUTPUTFIELDS]

    df['year'] = df['year'].astype(int)
    df['id'] = df['id'].astype(int)

    return df

if __name__ == '__main__':

     # parse CL args
    in_path = sys.argv[1]
    thresh = sys.argv[2]
    out_dir = sys.argv[3]

    df = main(in_path, thresh)

    save_csv(df, thresh, out_dir)
