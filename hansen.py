import sys

import pandas as pd # requires 0.13
import numpy as np

START_YEAR = 2001
END_YEAR = 2012

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

def process_loss_perc(df, thresh, start_year, end_year):
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

def process_loss(df, start_year, end_year):
    '''Combine long-form dataframes for 75 and 100% loss columns (i.e. >
    50% tree cover).'''

    # create dataframes for each threshold, organized into long form
    loss_75 = process_loss_perc(df, 75, start_year, end_year + 1)
    loss_100 = process_loss_perc(df, 100, start_year, end_year + 1)

    # merge the threshold dataframes
    loss = pd.merge(loss_75, loss_100, on=['iso', 'year'])

    #  sum loss across thresholds
    loss['loss'] = pd.DataFrame(loss[['loss_75', 'loss_100']].sum(axis=1))

    # drop now-extraneous columns
    loss = loss.drop('loss_75', 1)
    loss = loss.drop('loss_100', 1)

    # generate loss as share of land area
    loss = pd.merge(loss, df[['iso', 'land']], on='iso')
    loss['loss_perc'] = 100 * (loss['loss'] / loss['land'])
    loss = loss.drop('land', 1)

    return loss

def process_gain(df):
    '''Process gain data. No threshold is specified in the input spreadsheet.'''

    # select out the appropriate columns
    gain = df[['iso', 'gaintotal']]

    # rename columns
    gain.columns = ['iso', 'gain']

    # generate gain as share of land area
    gain['gain_perc'] = 100 * (df['gain'] / df['land'])

    return gain

###############################
# tree cover > 50% as of 2000 #
###############################

def process_treecover(df):
    '''Select treecover data where > 50%.'''
    # add up total tree cover > 50%
    cover = pd.DataFrame(df[['cover75','cover100']].sum(axis=1))
    cover.columns = ['treecover_2000']

    # add iso column back in
    cover = pd.concat([df[['iso']], cover], axis=1)

    # generate treecover as share of land area
    cover = pd.merge(cover, df[['iso', 'land']], on='iso')
    cover['treecover_2000_perc'] = 100 * (cover['treecover_2000'] / cover['land'])
    cover = cover.drop('land', 1)

    return cover

def load_data(in_path):
    '''Load data and do initial massaging.'''

    # load data
    df = pd.DataFrame.from_csv(in_path).rename(columns={'Country_ISO': 'iso'}).reset_index()

    # return dataframe aggregated by iso code
    return df.groupby('iso').sum().reset_index()

def main(in_path):

    df = load_data(in_path)

    # process columns
    loss = process_loss(df, START_YEAR, END_YEAR)
    gain = process_gain(df)
    cover = process_treecover(df)
    
    # merge dataframes
    tmp = pd.merge(cover, gain, on='iso')
    final = pd.merge(loss, tmp, on='iso')

    return final

if __name__ == '__main__':
    in_path = sys.argv[1]
    out_path = sys.argv[2]

    final = main(in_path)

    # output to CSV
    final.to_csv(out_path, index=False)
