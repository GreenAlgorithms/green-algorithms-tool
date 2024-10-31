import os
import copy

import pycountry_convert as pc
import pandas as pd

from urllib import parse
from types import SimpleNamespace


###################################################
## UTILS 
'''
Utils to mannage the input values.
Should be written in a separate utils file, either in the module
or at the root of the app if used more globally.
'''

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

def put_value_first(L, value):
    n = len(L)
    if value in L:
        L.remove(value)
        return [value] + L
        assert len(L)+1 == n
    else:
        # print(f'{value} not in list') # DEBUGONLY
        return L

def unlist(x):
    if isinstance(x, list):
        assert len(x) == 1
        return x[0]
    else:
        return x

def check_CIcountries(df):
    foo = df.groupby(['continentName', 'countryName'])['regionName'].apply(','.join)
    for x in foo:
        assert 'Any' in x.split(','), f"{x} does't have an 'Any' column"

def iso2_to_iso3(x):
    try:
        output = pc.country_name_to_country_alpha3(pc.country_alpha2_to_country_name(x, cn_name_format="default"),
                                                   cn_name_format="default")
    except:
        output = ''
    return output


###################################################
## DATA LOADING 
'''
Only for data loading. No particular dependency except towards some utils.
'''

def load_data(data_dir, **kwargs):

    data_dict0 = dict() # dotdict()

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
    check_CIcountries(CI_df)
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

    datacenters_df['name_unique'] = datacenters_df.provider + ' / ' + datacenters_df.Name

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

def availableOptions_servers(selected_provider,selected_continent, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        foo = data_dict.CI_dict_byName.get(selected_continent)
        bar = data_dict.datacenters_dict_byProvider.get(selected_provider)
    else:
        foo, bar = None, None

    if foo is not None:
        locationsINcontinent = [region['location'] for country in foo.values() for region in country.values()]
    else:
        locationsINcontinent = []

    if bar is not None:
        availableOptions_Names = [server['Name'] for server in bar.values() if server['location'] in locationsINcontinent]
        availableOptions_Names.sort()

        availableOptions = [bar[name] for name in availableOptions_Names]

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

def validateInput(input_dict, data_dict, keysOfInterest, appVersions_options_list, current_version):
    '''
    Validate the input, either from a url or others
    '''

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

    ## CREATE DICT OF OPTIONS
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

        except:
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