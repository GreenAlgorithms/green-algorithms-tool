import os
import copy
import base64
import io

import pandas as pd

from urllib import parse
from dash import html
from types import SimpleNamespace
from utils.utils import check_CIcountries_df, unlist, put_value_first

current_version = 'v2.2'
data_dir = os.path.join(os.path.abspath(''),'data')


###################################################
## DATA LOADING 

def load_data(data_dir, **kwargs):
    '''
    We download each csv and store it in a pd.DataFrame
    We ignore the first row, as it contains metadata
    All these correspond to tabs of the spreadsheet on the Google Drive
    '''

    data_dict0 = dict()

    for k,v in kwargs.items():
        data_dict0[k] = v

    data_dict = SimpleNamespace(**data_dict0)

    ### CPU ###
    cpu_df = pd.read_csv(os.path.join(data_dir, "TDP_cpu.csv"),
                         sep=',', skiprows=1)
    cpu_df.drop(['source'], axis=1, inplace=True)

    ### GPU ###
    gpu_df = pd.read_csv(os.path.join(data_dir, "TDP_gpu.csv"),
                         sep=',', skiprows=1)
    gpu_df.drop(['source'], axis=1, inplace=True)

    # Dict of dict with all the possible models
    # e.g. {'CPU': {'Intel(R) Xeon(R) Gold 6142': 150, 'Core i7-10700K': 125, ...
    data_dict.cores_dict = dict()
    data_dict.cores_dict['CPU'] = pd.Series(cpu_df.TDP_per_core.values,index=cpu_df.model).to_dict()
    data_dict.cores_dict['GPU'] = pd.Series(gpu_df.TDP_per_core.values,index=gpu_df.model).to_dict()

    ### PUE ###
    pue_df = pd.read_csv(os.path.join(data_dir, "defaults_PUE.csv"),
                         sep=',', skiprows=1)
    pue_df.drop(['source'], axis=1, inplace=True)

    data_dict.pueDefault_dict = pd.Series(pue_df.PUE.values, index=pue_df.provider).to_dict()

    ### HARDWARE ###
    # hardware_df = pd.read_csv(os.path.join(data_dir, "providers_hardware.csv"),
    #                           sep=',', skiprows=1)
    # hardware_df.drop(['source'], axis=1, inplace=True)

    ### OFFSET ###
    # offset_df = pd.read_csv(os.path.join(data_dir, "servers_offset.csv"),
    #                         sep=',', skiprows=1)
    # offset_df.drop(['source'], axis=1, inplace=True)

    ### CARBON INTENSITY BY LOCATION ###
    CI_df =  pd.read_csv(os.path.join(data_dir, "CI_aggregated.csv"),
                         sep=',', skiprows=1)
    check_CIcountries_df(CI_df)
    assert len(set(CI_df.location)) == len(CI_df.location)

    data_dict.CI_dict_byLoc = dict()
    for location in CI_df.location:
        foo = dict()
        for col in ['continentName','countryName','regionName','carbonIntensity']:
            foo[col] = CI_df.loc[CI_df.location == location,col].values[0]
        data_dict.CI_dict_byLoc[location] = foo

    data_dict.CI_dict_byName = dict()
    for continent in set(CI_df.continentName):
        foo = CI_df.loc[CI_df.continentName == continent]
        data_dict.CI_dict_byName[continent] = dict()
        for country in set(foo.countryName):
            bar = foo.loc[foo.countryName == country]
            data_dict.CI_dict_byName[continent][country] = dict()
            for region in set(bar.regionName):
                baar = bar.loc[bar.regionName == region]
                data_dict.CI_dict_byName[continent][country][region] = dict()
                data_dict.CI_dict_byName[continent][country][region]['location'] = baar.location.values[0]
                data_dict.CI_dict_byName[continent][country][region]['carbonIntensity'] = baar.carbonIntensity.values[0]

    ### CLOUD DATACENTERS ###
    cloudDatacenters_df = pd.read_csv(os.path.join(data_dir, "cloudProviders_datacenters.csv"),
                                      sep=',', skiprows=1)
    data_dict.providers_withoutDC = ['aws']

    ### LOCAL DATACENTERS ###
    # localDatacenters_df = pd.read_csv(os.path.join(data_dir, "localProviders_datacenters.csv"),
    #                                   sep=',', skiprows=1)
    # datacenters_df = pd.concat([data_dict.cloudDatacenters_df, localDatacenters_df], axis = 1)

    datacenters_df = cloudDatacenters_df

    # Remove datacentres with unknown CI
    datacenters_df.dropna(subset=['location'], inplace=True)

    # Create unique names (in case some names are shared between providers)
    for x in set(datacenters_df.provider):
        foo = datacenters_df.loc[datacenters_df.provider == x]
        assert len(foo.Name) == len(set(foo.Name))

    datacenters_df['name_unique'] = datacenters_df.provider + '--' + datacenters_df.Name

    assert len(datacenters_df.name_unique) == len(set(datacenters_df.name_unique))

    data_dict.datacenters_dict_byProvider = datacenters_df.groupby('provider')[['Name','name_unique','location','PUE']].apply(lambda x:x.set_index('Name', drop=False).to_dict(orient='index')).to_dict()
    data_dict.datacenters_dict_byName = datacenters_df[['provider','Name','name_unique','location','PUE']].set_index('name_unique', drop=False).to_dict(orient='index')

    ### PROVIDERS CODES AND NAMES ###
    providersNames_df = pd.read_csv(os.path.join(data_dir, "providersNamesCodes.csv"),
                                    sep=',', skiprows=1)

    data_dict.providersTypes = pd.Series(providersNames_df.platformName.values, index=providersNames_df.platformType).to_dict()

    data_dict.platformName_byType = dict()
    for platformType in set(providersNames_df.platformType):
        foo = providersNames_df.loc[providersNames_df.platformType == platformType]
        data_dict.platformName_byType[platformType] = pd.Series(providersNames_df.providerName.values, index=providersNames_df.provider).to_dict()

    ### REFERENCE VALUES
    refValues_df = pd.read_csv(os.path.join(data_dir, "referenceValues.csv"),
                               sep=',', skiprows=1)
    refValues_df.drop(['source'], axis=1, inplace=True)
    data_dict.refValues_dict = pd.Series(refValues_df.value.values,index=refValues_df.variable).to_dict()

    return data_dict # This is a SimpleNamespace

def get_available_versions():
    # TODO: move towards a utils script
    appVersions_options_list = [x for x in os.listdir(data_dir) if ((x[0]=='v')&(x!=current_version))]
    appVersions_options_list.sort(reverse=True)
    # Add the dev option for testing # TODO make it permanent, with a warning pop up if selected by mistake
    # appVersions_options_list.append('dev') # DEBUGONLY

    appVersions_options = [{'label': f'{current_version} (latest)', 'value': current_version}] + [{'label': k, 'value': k} for k in appVersions_options_list]
    return appVersions_options


###################################################
## DROPDOWN OPTIONS
'''
No particular dependency. Could be stored in a separate file.
'''

def availableLocations_continent(selected_provider, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        foo = data_dict.datacenters_dict_byProvider.get(selected_provider)
    else:
        foo = None

    if foo is not None:
        availableLocations = [x['location'] for x in foo.values()]
        availableLocations = list(set(availableLocations))

        availableOptions = list(set([data_dict.CI_dict_byLoc[x]['continentName'] for x in availableLocations if x in data_dict.CI_dict_byLoc]))

        return availableOptions
    else:
        return []

def availableOptions_servers(selected_provider, selected_continent, data):
    '''
    Provides 
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)
        ci_by_country_in_continent = data_dict.CI_dict_byName.get(selected_continent)
        dict_per_server_id_in_provider = data_dict.datacenters_dict_byProvider.get(selected_provider)
    else:
        ci_by_country_in_continent, dict_per_server_id_in_provider = None, None

    if ci_by_country_in_continent is not None:
        locationsINcontinent = [region['location'] for country in ci_by_country_in_continent.values() for region in country.values()]
    else:
        locationsINcontinent = []

    if dict_per_server_id_in_provider is not None:
        availableOptions_Names = [server['Name'] for server in dict_per_server_id_in_provider.values() if server['location'] in locationsINcontinent]
        availableOptions_Names.sort()

        availableOptions = [dict_per_server_id_in_provider[name] for name in availableOptions_Names]

        return availableOptions
    else:
        return []

def availableOptions_country(selected_continent, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        foo = data_dict.CI_dict_byName.get(selected_continent)
    else:
        foo = None

    if foo is not None:
        availableOptions = [country for country in foo]
        availableOptions = sorted(availableOptions)
        return availableOptions
    else:
        return []

def availableOptions_region(selected_continent,selected_country,data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        foo = data_dict.CI_dict_byName.get(selected_continent)
        if foo is not None:
            availableOptions_data = foo.get(selected_country)
        else:
            availableOptions_data = None
    else:
        availableOptions_data = None

    if availableOptions_data is not None:
        availableOptions_names = list(availableOptions_data.keys())
        availableOptions_names.sort()
        # Move Any to the first row:
        availableOptions_names.remove('Any')
        availableOptions_names = ['Any'] + availableOptions_names

        availableOptions_loc = [availableOptions_data[x]['location'] for x in availableOptions_names]

    else:
        availableOptions_loc = []

    return availableOptions_loc


###################################################
## PROPERLY HANDLE INPUTS
'''
Should be the core of the module 'handle_inputs'.
'''

def validateInput(input_dict, data_dict, keysOfInterest):
    '''
    Validate the input, either from a url or others
    '''
    appVersions_options_list = get_available_versions()

    def validateKey(key, value):
        new_val = copy.copy(value)
        # print('#b ', key, new_val, type(new_value))  # DEBUGONLY

        if key in ['runTime_hour', 'numberCPUs', 'numberGPUs']:
            new_val = int(float(new_val))
        elif key in ['runTime_min']:
            new_val = float(new_val)
            assert new_val >= 0
        elif key in ['PSF']:
            new_val = int(new_val)
            assert new_val >= 1
        elif key in ['tdpCPU', 'tdpGPU', 'memory']:
            new_val = float(new_val)
            assert new_val >= 0
        elif key in ['usageCPU', 'usageGPU']:
            new_val = float(new_val)
            assert (new_val >= 0) & (new_val <= 1)
        elif key in ['usageCPUradio', 'usageGPUradio', 'PUEradio', 'PSFradio']:
            assert new_val in ['Yes', 'No']
        elif key == 'coreType':
            assert new_val in ['CPU', 'GPU', 'Both']
        elif key in ['CPUmodel', 'GPUmodel']:
            assert new_val in [x['value'] for x in coreModels_options[key[:3]]]
        elif key == 'platformType':
            assert new_val in [x['value'] for x in platformType_options]
        elif key == 'provider':
            if unlist(input_dict['platformType']) == 'cloudComputing':  # TODO: I don't think this if is necessary?
                assert (new_val in data_dict.platformName_byType['cloudComputing']) | (new_val == 'other')
        elif key == 'serverContinent':
            assert new_val in availableLocations_continent(unlist(input_dict['provider']), data=vars(data_dict)) + ['other']
        elif key == 'server':
            list_servers = availableOptions_servers(unlist(input_dict['provider']),
                                                    unlist(input_dict['serverContinent']),
                                                    data=vars(data_dict))
            assert new_val in [x['name_unique'] for x in list_servers] + ["other"]
        elif key == 'locationContinent':
            assert new_val in list(data_dict.CI_dict_byName.keys())
        elif key == 'locationCountry':
            assert new_val in availableOptions_country(unlist(input_dict['locationContinent']), data=vars(data_dict))
        elif key == 'locationRegion':
            list_loc = availableOptions_region(unlist(input_dict['locationContinent']),
                                               unlist(input_dict['locationCountry']), data=vars(data_dict))
            assert new_val in list_loc
        elif key == 'PUE':
            new_val = float(new_val)
            assert new_val >= 1
        elif key == 'appVersion':
            assert new_val in (appVersions_options_list + [current_version])
        else:
            assert False, 'Unknown URL key'

        return new_val

    ## CREATE DICT OF OPTIONS to be used in validateKey
    if set(['CPUmodel','GPUmodel']) & set(input_dict.keys()):
        coreModels_options = dict()
        for coreType in ['CPU', 'GPU']:
            availableOptions = sorted(list(data_dict.cores_dict[coreType].keys()))
            availableOptions = put_value_first(availableOptions, 'Any')
            coreModels_options[coreType] = [
                {'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions)) +
                                                     [("Other", "other")]
            ]
    else:
        coreModels_options = None


    if 'platformType' in input_dict:
        platformType_options = [
            {'label': k,
             'value': v} for v, k in list(data_dict.providersTypes.items()) +
                                     [('personalComputer', 'Personal computer')] +
                                     [('localServer', 'Local server')]
        ]
    else:
        platformType_options = None

    new_dict = dict()
    wrong_imputs = dict()
    for key in keysOfInterest:
        new_value = unlist(input_dict[key])
        # validateKey(key, new_value) # DEBUGONLY

        try:
            new_dict[key] = validateKey(key, new_value)

        except Exception as e:
            # print(f'Exception {e} raised for key = {key}')
            # print(f'Wrong input for {key}: {new_value}') # DEBUGONLY
            wrong_imputs[key] = new_value
            # new_value = None

        # new_dict[key] = new_value # I'm moving that in the try so that failed values are not added

    return new_dict, wrong_imputs

def prepURLqs(url_search, data, keysOfInterest):
    if (url_search is not None) & (url_search != '') & (data is not None):
        url0 = parse.parse_qs(url_search[1:])

        # check whether the keysOfInterest are in the url
        commonKeys = set(keysOfInterest)&set(url0.keys())

        if len(commonKeys) > 0:
            data_dict = SimpleNamespace(**data)
            url, _ = validateInput(input_dict=url0, data_dict=data_dict, keysOfInterest=keysOfInterest)
        else:
            url = dict()
    else:
        url = dict()
    return url

def parse_query_strings(query_strings, default_values):
    values = copy.deepcopy(default_values)
    appVersions_options_list = get_available_versions()
    popup_message = 'Filling in values from the URL. \n' \
    'All fields will be frozen. To edit, please click reset.'
    show_popup = False
        
    # Load the right dataset to validate the URL inputs
    new_version = default_values['appVersion']
    if 'appVersion' in query_strings:
        new_version = unlist(query_strings['appVersion'])
    assert new_version in (appVersions_options_list + [current_version])
    if new_version == current_version:
        newData = load_data(os.path.join(data_dir, 'latest'), version=current_version)
    else:
        newData = load_data(os.path.join(data_dir, new_version), version=new_version)

    # Validate URL
    processed_query_strings, invalidInputs = validateInput(
        input_dict=query_strings,
        data_dict=newData,
        keysOfInterest=list(query_strings.keys())
    )
    # Check if the url contained relevant query strings used to fill the form in
    if len(query_strings) > 0:
        show_popup = True
        # Check if there are mispelled inputs
        if len(invalidInputs) > 0:
            popup_message += f'\n\nThere seems to be some typos in this URL, ' \
                            f'using default values for '
            popup_message += f"{', '.join(list(invalidInputs.keys()))}."        

    values.update((k, processed_query_strings[k]) for k in values.keys() & processed_query_strings.keys())
    values['popup_message'] = popup_message
    values['show_popup'] = show_popup
    return values

def read_input_csv(input_csv_content, filename):
    _, content_string = input_csv_content.split(',')
    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        else:
            return {}
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return  df.to_dict() 


