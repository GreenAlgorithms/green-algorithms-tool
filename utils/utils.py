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
    
def is_shown(style):
    return style['display'] != 'none'

def check_CIcountries_df(df):
    '''
    Simple sanity check on the table containing the Carbon Intensities (CI) per country.
    '''
    regions_cols_as_str = df.groupby(['continentName', 'countryName'])['regionName'].apply(','.join)
    for regions_per_country_as_str in regions_cols_as_str:
        assert 'Any' in regions_per_country_as_str.split(','), f"{regions_per_country_as_str} does't have an 'Any' column"

def custom_prefix_escape(component_id: str):
    '''
    Allows to escape some ids from the PrefixIdTransform applied to DashBlueprints.
    Inspired from the default_prefix_escape() implemented in dash_exceptions.
    
    Its purpose is to avoid renaming the id of versioned-data, which does not belong
    to the scope of a particular form.
    TODO: implement in a more robust manner. 
    '''
    if isinstance(component_id, str):
        if component_id.startswith("a-"):  # intended usage is for anchors
            return True
        if component_id.startswith("anchor-"):  # intended usage is for anchors
            return True
        if component_id == 'versioned_data':
            return True
    return False