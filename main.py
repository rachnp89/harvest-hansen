import argparse
import os

import pandas as pd
import numpy as np

import process_umd as umd
import common


def main(in_path, out_dir, output_type):
    if output_type == 'national':
        print 'Processing national-level data'
        fname = 'umd_nat.csv'
        header = common.HEADERSTART
        common.OUTPUTFIELDS.remove('region')
        output_header = common.OUTPUTFIELDS
    elif output_type == 'subnational':
        print 'Processing subnational-level data'
        header = common.HEADERSTART
        output_header = common.OUTPUTFIELDS
        fname = 'umd_subnat.csv'
    else:
        print 'Processing ecozone data'
        header = ['ecozone', 'realm'] + common.HEADERSTART[1:]
        output_header = ['ecozone', 'realm'] + common.OUTPUTFIELDS[2:]
        fname = 'umd_eco.csv'

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    out_df = pd.DataFrame()

    for thresh in common.THRESHOLDS[:-1]:  # ignore 100% threshold
        df = umd.load(in_path, header, common.THRESHOLDS, common.STARTYEAR,
                      common.ENDYEAR, common.YEARS)
        print 'Processing threshold %d' % thresh
        df = umd.main(df, thresh, output_type, output_header)
        out_df = out_df.append(df)

    out_df.reset_index()
    out_df = out_df.replace('', np.nan)
    out_df = out_df.replace('inf', np.nan)

    path = os.path.join(out_dir, fname)
    out_df.to_csv(path, index=False, na_rep='NULL')

    return out_df

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=str)
    parser.add_argument('output', type=str)
    parser.add_argument('type', choices=['eco', 'subnational', 'national'])

    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output
    output_type = args.type

    main(input_path, output_dir, output_type)
