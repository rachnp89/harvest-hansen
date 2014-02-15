import sys

import pandas as pd # requires 0.13
import numpy as np

START_YEAR = 2001
END_YEAR = 2012
NUM_YEARS = END_YEAR - START_YEAR + 1

CONVERSION_FACTOR = 0.01 # hectares to square km.
gt_thresh = 25 # greater-than threshold
quartiles = [50, 75, 100]


###########################    
# loss annual - long form #
###########################    

def loss_fields(thresh, start_year, end_year):
    '''For a given threshold, generate fieldnames for loss by year.

    Usage:
        >>> loss_fields(75, 2001, 2012)
        ['loss_75_2001', 'loss_75_2002', 'loss_75_2003', 'loss_75_2004',
        'loss_75_2005', 'loss_75_2006', 'loss_75_2007', 'loss_75_2008',
        'loss_75_2009', 'loss_75_2010', 'loss_75_2011']'''
    return ['loss_%d_%d' % (thresh, year) for year in range(start_year, end_year)]

def loss_wide_to_long(df, thresh, start_year, end_year):
    '''Convert annual loss columns from wide to long form.'''
    # get fieldnames
    fields = loss_fields(thresh, start_year, end_year)

    # add iso code
    data = pd.concat([df[['iso'] + fields]], axis=1)

    # convert from wide to long based on year
    data = pd.wide_to_long(data, ['loss_%d_' % thresh], i='iso', j='year').reset_index()

    # rename columns
    data.columns = ['iso', 'year', 'loss_%d' % thresh]

    return data

def sum_loss(loss, thresh):
    ranges = [25, 50, 75, 100]
    fields = ['loss_%d' % t for t in ranges if t > thresh]
    loss['loss_gt_%d' % thresh] = pd.DataFrame(loss[fields].sum(axis=1))

    return loss

def process_loss(df, start_year, end_year):
    '''Combine long-form dataframes for different loss thresholds.'''

    # create dataframes for each threshold, organized into long form
    loss_25 = loss_wide_to_long(df, 25, start_year, end_year + 1)
    loss_50 = loss_wide_to_long(df, 50, start_year, end_year + 1)
    loss_75 = loss_wide_to_long(df, 75, start_year, end_year + 1)
    loss_100 = loss_wide_to_long(df, 100, start_year, end_year + 1)

    # merge the threshold dataframes
    loss = pd.merge(loss_25, loss_50, on=['iso', 'year'])
    loss = pd.merge(loss, loss_75, on=['iso', 'year'])
    loss = pd.merge(loss, loss_100, on=['iso', 'year'])

    #  sum loss across thresholds
    loss_thresholds = [0, 25, 50]

    for thresh in loss_thresholds:
        loss = sum_loss(loss, thresh)

    # drop now-extraneous columns
    loss = loss.drop('loss_25', 1)
    loss = loss.drop('loss_50', 1)
    loss = loss.drop('loss_75', 1)
    loss = loss.drop('loss_100', 1)
    
    return loss

def extent_fields(year, gt_thresh, quartiles):

    fields = dict(extent_fields = ['cover%d' % thresh for thresh in quartiles],
                  extent_gt_str = 'extent_gt_%d_%d', # e.g. extent_gt_25_2000
                  loss_str = 'loss_%d_%d', # e.g. loss_25_2000
                  loss_gt_str = 'loss_gt_%d_%d', # e.g. loss_gt_25_2000
                  loss_gt_perc_str = 'loss_perc_gt_%d_%d') # e.g. loss_perc_gt_25_2000

    out_fields = dict(extent_fields=fields['extent_fields'])

    # e.g. 'extent_gt_25_2001'
    out_fields['extent_field'] = fields['extent_gt_str'] % (gt_thresh, year)

    # e.g. 'extent_gt_25_2000'
    out_fields['extent_field_prev'] = fields['extent_gt_str'] % (gt_thresh, year - 1)

    # e.g. ['loss_50_2000', 'loss_75_2000', 'loss_100_2000']
    out_fields['loss_fields'] = [fields['loss_str'] % (thresh, year) 
                                 for thresh in quartiles]

    # e.g. 'loss_gt_25_2000'
    out_fields['loss_gt_field'] = fields['loss_gt_str'] % (gt_thresh, year)
    
    # e.g. 'loss_perc_25_2001'
    out_fields['loss_perc_gt_field'] = fields['loss_gt_perc_str'] % (gt_thresh, year)

    return out_fields

def extent_year(year, gt_thresh, quartiles, data, df):
    '''Calculate extent for a given year after 2000. Extent in 2000 must
    already be in the `data` dataframe.'''

    f = extent_fields(year, gt_thresh, quartiles)

    # calculate loss > 25%
    data[f['loss_gt_field']] = pd.DataFrame(df[f['loss_fields']].sum(axis=1))
    
    # calculate current extent by subtracting current loss from
    # last year's extent
    data[f['extent_field']] = data[f['extent_field_prev']] - data[f['loss_gt_field']]

    # calculate loss percentage by dividing by previous year's extent
    data[f['loss_perc_gt_field']] = 100 * data[f['loss_gt_field']] \
                                    / data[f['extent_field_prev']]

    return data

def extent_2000(df, gt_thresh, quartiles):
    '''Calculate extent for the year 2000.'''
    f = extent_fields(2000, gt_thresh, quartiles)

    data = pd.DataFrame(df[f['extent_fields']].sum(axis=1))
    data.columns = [f['extent_field']]

    return data

def process_extent(df, end_year):
    '''Based on extent & loss > 25%, take extent in 2000 as the base
    extent. For each subsequent year, calculate extent by subtracting
    loss from the previous year's extent.'''

    # calculate extent in 2000
    data = extent_2000(df, gt_thresh, quartiles)

    # calculate extent for remaining years
    for year in range(2001, end_year + 1):
        data = extent_year(year, gt_thresh, quartiles, data, df)

    # add iso code
    data = pd.concat([df[['iso']], data], axis=1)

    # get fieldnames
    f = extent_fields(2000, gt_thresh, quartiles)

    # generate field stubs
    extent_stub = '_'.join(f['extent_field'].split('_')[:-1]) + '_' # extent_gt_25_
    loss_stub = extent_stub.replace('extent', 'loss') # loss_gt_25_
    loss_perc_stub = extent_stub.replace('extent', 'loss_perc') #l loss_perc_gt_25_

    # reshape wide to long
    data = pd.wide_to_long(data, [extent_stub, loss_stub, loss_perc_stub], i='iso',
                           j='year').reset_index()

    # rename columns
    extent_field = 'extent_gt_%d' % gt_thresh
    loss_field = 'loss_gt_%d' % gt_thresh
    loss_perc_field = 'loss_perc_gt_%d' % gt_thresh
    data.columns = ['iso', 'year', extent_field, loss_field, loss_perc_field]

    data = data.drop(loss_field, 1)

    return data

def process_gain(df, data):
    '''Process gain data. No threshold is specified in the input
    spreadsheet. `df` is in wide form.'''

    # select out the appropriate columns
    gain = df[['iso', 'gaintotal']]
    
    # add an annual field
    gain[['gain_annual']] = gain[['gaintotal']] / float(NUM_YEARS)

    # rename columns
    gain.columns = ['iso', 'gain', 'gain_annual']

    # merge with long-form dataframe
    gain = pd.merge(data[['iso', 'year', 'extent_gt_%d' % gt_thresh]], gain, on='iso')

    # generate gain as share of tree cover extent
    gain['gain_perc'] = 100 * (gain['gain_annual'] / gain['extent_gt_%d' % gt_thresh])

    # drop extent
    gain = gain.drop('extent_gt_%d' % gt_thresh, 1)

    return gain

def convert_ha_km2(df, fields):
    for f in fields:
        df[[f]] = df[[f]] * CONVERSION_FACTOR

    return df
    
def load_data(in_path):
    '''Load data and groupby iso code.'''

    # load data
    df = pd.DataFrame.from_csv(in_path).rename(columns={'Country_ISO': 'iso'}).reset_index()

    # return dataframe aggregated by iso code
    return df.groupby('iso').sum().reset_index()

def main(in_path):

    df = load_data(in_path)

    # process columns
    extent = process_extent(df, END_YEAR)
    loss = process_loss(df, START_YEAR, END_YEAR)
    gain = process_gain(df, extent)

    # merge dataframes
    tmp = pd.merge(extent, loss, on=['iso', 'year'], how='left')
    final = pd.merge(tmp, gain, on=['iso', 'year'], how='left')

    final = convert_ha_km2(final, ['gain', 'gain_annual', 'extent_gt_25',
                                   'loss_gt_0', 'loss_gt_25', 'loss_gt_50'])

    # remove inf (divide by zero) and NaN (loss in 2000)
    final = final.replace([np.inf, np.nan], 0)
    
    final = final.sort(['iso', 'year'])

    return final

if __name__ == '__main__':
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    final = main(in_path)

    # output to CSV
    final.to_csv(out_path, index=False)
