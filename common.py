THRESHOLDS = [10, 15, 20, 25, 30, 50, 75, 100]
STARTYEAR = 2001
ENDYEAR = 2013
NUMYEARS = ENDYEAR - STARTYEAR + 1
YEARS = xrange(STARTYEAR, ENDYEAR + 1)

# standard fields at beginning of input header. modified within main() to
# account for the dataset being processed
HEADERSTART = ['name', 'code', 'area', 'nodata',  'land', 'water', 'loss0013',
               'gain0012']

# output header. modified within main() to account for the dataset being
# processed
OUTPUTFIELDS = ['region', 'country', 'id', 'year', 'thresh', 'extent_2000',
                'extent_perc', 'gain', 'loss', 'gain_perc', 'loss_perc']
