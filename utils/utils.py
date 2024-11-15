YES_NO_OPTIONS = [
    {'label': 'Yes', 'value': 'Yes'},
    {'label': 'No', 'value': 'No'}
]

class dotdict(dict):
    """dot.notation access to dictionary attributes."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def put_value_first(L, value):
    '''Does not modify the input list if it does not contain the input value.'''
    if value in L:
        L.remove(value)
        return [value] + L
    return L

def unlist(x):
    ''' Extracts content of ONE ITEM lists.'''
    if isinstance(x, list):
        assert len(x) == 1
        return x[0]
    else:
        return x

def check_CIcountries_df(df):
    '''
    Simple sanity check on the table containing the Carbon Intensities (CI) per country.
    '''
    regions_cols_as_str = df.groupby(['continentName', 'countryName'])['regionName'].apply(','.join)
    for regions_per_country_as_str in regions_cols_as_str:
        assert 'Any' in regions_per_country_as_str.split(','), f"{regions_per_country_as_str} does't have an 'Any' column"

