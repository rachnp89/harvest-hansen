import os
import sys

import pandas as pd

import common


def gen_extent_2000_fields(thresholds):
    return ['extent_%d_2000' % thresh for thresh in thresholds]


def gen_annual_loss_fields(start, end):
    return ['annual_loss_%d' % year for year in xrange(start, end + 1)]


def gen_loss_thresh_year_fields(prefix, thresholds, years):
    field_str = '%s_%d_%d'  # e.g. extent_25_2005
    return [field_str % (prefix, t, y) for t in thresholds for y in years]


def gen_header(starting_header, thresholds, start, end, years):
    extent_2000_fields = gen_extent_2000_fields(thresholds)
    annual_loss_fields = gen_annual_loss_fields(start, end)
    loss_thresh_year_fields = gen_loss_thresh_year_fields('loss',
                                                          thresholds,
                                                          years)

    h = starting_header + annual_loss_fields + extent_2000_fields
    h += loss_thresh_year_fields

    return h


def load(path, starting_header, thresholds, start, end, years):
    header = gen_header(starting_header, thresholds, start, end, years)
    df = pd.read_csv(path, skiprows=2, header=0, names=header)
    df = df.rename(columns=dict(code='id'))

    return df


def wide_to_long(df, thresh):
    """Reshape dataframe from wide to long format."""

    fields = ['loss']
    stubs = ['%s_%d_' % (prefix, thresh) for prefix in fields]
    new_names = dict(zip(stubs, fields))

    df = pd.wide_to_long(df, stubs, i='id', j='year')
    df = df.reset_index()
    df = df.rename(columns=new_names)

    return df


def calc_annual_gain(df):
    """Calculate annual gain field."""
    df['gain'] = df['gain0012'] / float(common.NUMYEARS - 2)
    df[df['year'] == 2013]['gain'] = None
    # df = set_2000_0(df, 'gain')

    return df


def set_2000_0(df, field):
    """Set year 2000 to zero for given field. Use with loss/gain percentage
    since year 2000 has no meaning."""

    idx = df['year'] == 2000
    subdf = df[idx]
    subdf[field] = 0
    df.update(subdf)

    return df


def calc_perc(df, field, thresh, denominator):
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


def gen_sum_fields(year, thresh, prefix='loss'):
    '''Generate field names for thresholds of interest. See docs for
    `running_sum` for an explanation of why this is x > thresh, not x >=
    thresh'''
    thresholds = filter(lambda x: x > thresh, common.THRESHOLDS)
    return ['%s_%d_%d' % (prefix, thresh, year) for thresh in thresholds]


def running_sum(df, thresh, prefix):
    '''Generate the sum of loss at all thresholds > the given threshold, for
    each year. The data dump from UMD in 2015-02 was for forest extent ranges
    as strata like 11-15% (S2). So for a 15% threshold, that corresponds to
    strata S3 (16-20%) through S8 (76-100%).'''
    fields = []
    for year in common.YEARS:
        fields = gen_sum_fields(year, thresh, prefix)
        df['%s_%d_%d' % (prefix, thresh, year)] = df.loc[:, fields].sum(axis=1)
    return df


def running_extent_sum(df, thresh):
    prefix = 'extent'
    year = 2000
    fields = gen_sum_fields(year, thresh, prefix)
    df['%s_%d_%d' % (prefix, thresh, year)] = df.loc[:, fields].sum(axis=1)
    return df


def cleanup_name(df, data_type):
    if data_type == 'eco':
        df['ecozone'] = df.ecozone.str.split(' ').apply(lambda x: x[0])
    else:
        df.loc[0, ['name']] = 'Outside any_'
        df['country'] = df.name.str.split('_').apply(lambda x: x[0])
        df['region'] = df.name.str.split('_').apply(lambda x: x[-1])
    return df


def main(df, thresh, output_type, output_fields):
    '''Generate long-form datasets with year, thresh, gain, loss,
    treecover (and associated percentages).'''

    df = cleanup_name(df, output_type)

    if output_type == 'national':
        df = df.groupby(['country']).sum().reset_index()
    if output_type == 'eco':
        df = df.groupby(['ecozone']).sum().reset_index()
        # remove non-forest zones
        df = df[df.ecozone != 'Water']
        df = df[df.ecozone != 'Polar']
        df = df[df.ecozone != 'No']
        df = df.reset_index()
    df = running_sum(df, thresh, 'loss')
    df = running_extent_sum(df, thresh)
    df = wide_to_long(df, thresh)
    df = calc_annual_gain(df)

    df = calc_perc(df, 'loss', thresh, 'extent_%d_2000' % thresh)
    df = calc_perc(df, 'gain', thresh, 'extent_%d_2000' % thresh)

    # tree cover as share of land area
    df = calc_perc(df, 'extent_%d_2000' % thresh, thresh, denominator='land')
    df = df.rename(columns={'extent_%d_2000_perc' % thresh: 'extent_perc'})
    df['thresh'] = thresh

    df = df.rename(columns={'extent_%d_2000' % thresh: 'extent_2000'})

    df['year'] = df['year'].astype(int)
    df['id'] = df['id'].astype(int)

    df = df.loc[:, output_fields]

    return df

if __name__ == '__main__':
    # parse CL args
    in_path = sys.argv[1]
    thresh = sys.argv[2]
    out_dir = sys.argv[3]

    df = main(in_path, thresh)

    # save_csv(df, thresh, out_dir)
