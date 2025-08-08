""" Generic Python utils. """

import pandas as pd

from blueprints.translation.translation_dicts import TRANSLATIONS_DICT


def get_yes_or_no_options(language_id: str= 'en'):
    '''
    Returns the options for Yes/no radio buttons.

    Args:
        language_id (str): the language identifier for translation purpose
    '''
    return [
    {'label': TRANSLATIONS_DICT['Yes'][language_id], 'value': 'Yes'},
    {'label': TRANSLATIONS_DICT['No'][language_id], 'value': 'No'}
]


class dotdict(dict):
    """dot.notation access to dictionary attributes."""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def put_value_first(L: list, value):
    """Does not modify the input list if it does not contain the input value."""
    if value in L:
        L.remove(value)
        return [value] + L
    return L


def unlist(x):
    """ Extracts content of ONE ITEM lists."""
    if isinstance(x, list):
        assert len(x) == 1
        return x[0]
    else:
        return x


def is_shown(style: dict):
    return style['display'] != 'none'


def check_CIcountries_df(df: pd.DataFrame):
    """
    Simple sanity check on the table containing the Carbon Intensities (CI) per country.
    """
    regions_cols_as_str = df.groupby(['continentName', 'countryName'])['regionName'].apply(','.join)
    for regions_per_country_as_str in regions_cols_as_str:
        assert 'Any' in regions_per_country_as_str.split(','), f"{regions_per_country_as_str} does't have an 'Any' column"


def custom_prefix_escape(component_id: str):
    """
    Allows to escape some ids from the PrefixIdTransform applied to DashBlueprints.
    Inspired from the default_prefix_escape() implemented in dash_exceptions.
    
    Its purpose is to avoid renaming the id of versioned-data, which does not belong
    to the scope of a particular form.
    TODO: implement in a more robust manner. 
    """
    if isinstance(component_id, str):
        if component_id.startswith("a-"):  # intended usage is for anchors
            return True
        if component_id.startswith("anchor-"):  # intended usage is for anchors
            return True
        if component_id in ['versioned_data', 'url_content', 'language_dropdown']:
            return True
    return False


def write_error_message(missing_inputs: list, invalid_inputs: list, language_id:str, show_err_mess: bool=False):
    '''
    Format the error message to display when csv containing errors are loaded.
    Currently distinguishes between:
    
    Args
        missing_inputs (list): inputs expected in the csv but not found
        invalid_inputs (list): unknown inputs and expected inputs with wrong value
        language_id (list): the language identifier for translation purpose
        show_err_mess (bool): whether an error previously existed or not

    Returns
        show_err_mess (bool): whether an error exists or not
        mess_content (str): the error message itself
    '''
    mess_content = ''
    # The first part of the error message contains missing inputs, ie expected inputs that were not found in the csv
    if len(missing_inputs) > 0:
        show_err_mess = True
        mess_content += TRANSLATIONS_DICT['fields_should_be_in_csv'][language_id]
        mess_content += f"*{', '.join(missing_inputs)}.*"
    # The second part of the error message gathers all other inputs from the csv raising an error
    if len(invalid_inputs) > 0:
        show_err_mess = True
        mess_content += TRANSLATIONS_DICT['wrong_fields'][language_id]
        mess_content += f"*{', '.join(invalid_inputs)}.*"
    return show_err_mess, mess_content