import hansen_subnat as subnat

import common


def main(input, out_dir):
    for thresh in common.THRESHOLDS:
        df = subnat.main(input, thresh)
        subnat.save_csv(df, thresh, out_dir)
