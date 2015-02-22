import os
import sys

import pandas as pd

import common

# header details
OUTPUTFIELDS = ['region', 'country', 'id', 'year', 'thresh', 'extent_2000',
                'extent_perc', 'gain', 'loss', 'gain_perc', 'loss_perc']


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
    df['gain'] = df['gain0012'] / float(common.NUMYEARS - 1)
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


def cleanup_name(df):
    df.loc[0, ['name']] = 'Outside any_'
    df['country'] = df.name.str.split('_').apply(lambda x: x[0])
    df['region'] = df.name.str.split('_').apply(lambda x: x[-1])

    return df


def main(path, thresh, national):
    '''Generate long-form datasets with year, thresh, gain, loss,
    treecover (and associated percentages).'''
    df = common.load(path)
    df = cleanup_name(df)

    if national:
        print "Processing national-level data"
        df = df.groupby(['country']).sum().reset_index()
    else:
        print "Processing subnational-level data"
        pass

    df = running_sum(df, thresh, 'loss')
    df = running_extent_sum(df, thresh)

    df = wide_to_long(df, thresh)
    df = calc_annual_gain(df)

    # percents default to offset extent as denominator
    df = calc_perc(df, 'loss', thresh, 'extent_%d_2000' % thresh)
    df = calc_perc(df, 'gain', thresh, 'extent_%d_2000' % thresh)
    # tree cover as share of country's land area
    df = calc_perc(df, 'extent_%d_2000' % thresh, thresh, denominator='land')
    df = df.rename(columns={'extent_%d_2000_perc' % thresh: 'extent_perc'})
    df['thresh'] = thresh

    df = df.rename(columns={'extent_%d_2000' % thresh: 'extent_2000'})

    df['year'] = df['year'].astype(int)
    df['id'] = df['id'].astype(int)

    df = df.loc[:, OUTPUTFIELDS]

    return df

if __name__ == '__main__':
    # parse CL args
    in_path = sys.argv[1]
    thresh = sys.argv[2]
    out_dir = sys.argv[3]

    df = main(in_path, thresh)

    save_csv(df, thresh, out_dir)
