import os

import pandas as pd
import numpy as np

import process_umd as umd
import common


def main(in_path, out_dir, national=False):
    if national:
        fname = 'umd_nat.csv'
        umd.OUTPUTFIELDS.remove('region')

    else:
        fname = 'umd_subnat.csv'
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    out_df = pd.DataFrame()

    for thresh in common.THRESHOLDS:
        print 'Processing threshold %d' % thresh
        df = umd.main(in_path, thresh, national)
        out_df = out_df.append(df)

        # subnat.save_csv(df, thresh, out_dir)

    out_df.reset_index()
    out_df = out_df.replace('', np.nan)
    out_df = out_df.replace('inf', np.nan)

    path = os.path.join(out_dir, fname)
    out_df.to_csv(path, index=False, na_rep='NULL')

    return out_df
