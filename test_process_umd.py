import unittest

import process_umd as umd
import common


class Test(unittest.TestCase):
    path = 'data/country_admin_export_clean.xlsx - Admin_2013.csv'
    thresh = 50
    ts = umd.main(path, thresh, national=False)
    raw = common.load(path)

    ts_nat = umd.main(path, thresh, national=True)
    raw_nat = common.load(path)

    def test_loss(self):
        """Check that loss is calculated properly for a given threshold."""
        acre = self.ts.query("region == 'Acre'")

        df = self.raw[self.raw['name'] == 'Brazil_Acre']

        result = list(acre.query('year == 2003')['loss'])
        expected = list(df['loss_75_2003'] + df['loss_100_2003'])

        self.assertEqual(result, expected)

    def test_gain(self):
        """Check that gain field is properly generated."""
        acre = self.ts.query("region == 'Acre'")
        df = self.raw[self.raw['name'] == 'Brazil_Acre']

        result = list(acre[acre.year == 2003]['gain'])
        expected = list(df.gain0012 / 12.)

        self.assertEqual(result, expected)
