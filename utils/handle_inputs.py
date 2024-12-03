import os
import copy
import base64
import io

import pandas as pd

from types import SimpleNamespace
from utils.utils import check_CIcountries_df, unlist, put_value_first


###################################################
## GLOABAL VARIABLES

CURRENT_VERSION = 'v2.2'
DATA_DIR = os.path.join(os.path.abspath(''),'data')

# TODO Add the dev option for testing, make it permanent, with a warning pop up if selected by mistake
APP_VERSION_OPTIONS_LIST = [x for x in os.listdir(DATA_DIR) if ((x[0]=='v')&(x!=CURRENT_VERSION))]
APP_VERSION_OPTIONS_LIST.sort(reverse=True)

# The default values used to fill in the form when no other input is provided
# WARNING: do not modify the order unless modifying the order of the outputs of 
# the fillin_from_inputs callback accordingly
# TODO: make it more robust
DEFAULT_VALUES = dict(
    runTime_hour=12,
    runTime_min=0,
    coreType='CPU',
    numberCPUs=12,
    CPUmodel='Xeon E5-2683 v4',
    tdpCPU=12,
    numberGPUs=1,
    GPUmodel='NVIDIA Tesla V100',
    tdpGPU=200,
    memory=64,
    platformType= 'localServer',
    provider='gcp',
    usageCPUradio='No',
    usageCPU=1.0,
    usageGPUradio='No',
    usageGPU=1.0,
    PUEradio='No',
    PSFradio='No',
    PSF=1,
    appVersion=CURRENT_VERSION,
)

# The following list should contain tke keys of aggregate_data that should not
# raise an message error because they are not intended to be processed as inputs
INPUT_KEYS_TO_IGNORE = [
    'runTime',
    'location',
    'carbonIntensity',
    'carbonEmissions',
    'CE_CPU',
    'CE_GPU',
    'CE_core',
    'CE_memory',
    'text_CE',
    'power_needed',
    'energy_needed',
    'text_energyNeeded',
    'n_treeMonths',
    'text_treeYear',
    'nkm_drivingUS',
    'nkm_drivingEU',
    'nkm_train',
    'flying_context',
    'flying_text',
]


###################################################
## DATA LOADING 

def load_data(data_dir, **kwargs):
    '''
    We download each csv and store it in a pd.DataFrame.
    We ignore the first row, as it contains metadata.
    All these correspond to tabs of the spreadsheet on the Google Drive.
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
    appVersions_options = [{'label': f'{CURRENT_VERSION} (latest)', 'value': CURRENT_VERSION}] + [{'label': k, 'value': k} for k in APP_VERSION_OPTIONS_LIST]
    return appVersions_options


###################################################
## DROPDOWN OPTIONS

def availableLocations_continent(selected_provider, data):
    '''
    Provides the available continents for a given provider.
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)
        dict_per_server_id_in_provider = data_dict.datacenters_dict_byProvider.get(selected_provider)
    else:
        dict_per_server_id_in_provider = None

    if dict_per_server_id_in_provider is not None:
        availableLocations = [x['location'] for x in dict_per_server_id_in_provider.values()]
        availableLocations = list(set(availableLocations))
        availableOptions = list(set([data_dict.CI_dict_byLoc[x]['continentName'] for x in availableLocations if x in data_dict.CI_dict_byLoc]))
        return availableOptions
    else:
        return []

def availableOptions_servers(selected_provider, selected_continent, data):
    '''
    Provides the available servers for the given provider and continent.
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
    '''
    Provides the available country for the selected continent.
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)
        ci_per_country_dit = data_dict.CI_dict_byName.get(selected_continent)
    else:
        ci_per_country_dit = None

    if ci_per_country_dit is not None:
        availableOptions = [country for country in ci_per_country_dit]
        availableOptions = sorted(availableOptions)
        return availableOptions
    else:
        return []

def availableOptions_region(selected_continent,selected_country,data):
    '''
    Provides the available region for the selected continent and contry.
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)
        ci_per_country_dict = data_dict.CI_dict_byName.get(selected_continent)
        if ci_per_country_dict is not None:
            availableOptions_data = ci_per_country_dict.get(selected_country)
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

def validateInput(input_dict, data_dict, keysOfInterest):
    '''
    Validates the inputs: ensures the consistency between the keys and corresponding 
    value but also between some values.
    args:
        - input_dict: inputs to process
        - data_dict: backend data used to check consistency between provided values.
        - keyOfInterest [list]: a list of keys to process.
    returns: 
        - new_dict: a curated subset of input_dict with clean inputs. Its keys
        are contained in keysofInterest.
        - wrong_imputs: a subset of the input_dict containing inputs
        either raising erorrs either not corresponding to keysOfInterest.
    '''
    if type(data_dict) == dict:
        data_dict = SimpleNamespace(**data_dict)
    appVersions_options_list = get_available_versions()

    ############################
    # We first build some data frameworks to be used later on during our checkings
    
    ### CPU AND GPU options
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

    ### PLATFORM TYPE options
    if 'platformType' in input_dict:
        platformType_options = [
            {'label': k,
            'value': v} for v, k in list(data_dict.providersTypes.items()) +
                                    [('personalComputer', 'Personal computer')] +
                                    [('localServer', 'Local server')]
        ]
    else:
        platformType_options = None

    def validateKey(key, value):
        '''
        WARNING: the keys used to check should be the same as those used
        in the DEFAULT_VALUES and aggregate_data.

        Ensures the consistency between the key and the provided value and
        checks the dependencies between different values.
        '''
        new_val = copy.copy(value)
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
            assert new_val in (appVersions_options_list + [CURRENT_VERSION])
        else:
            assert False, 'Unknown key'
        return new_val

    ############################
    # Now we validate each of the target key from the input dict

    new_dict = dict()
    wrong_imputs = dict()
    for key in keysOfInterest:
        if key not in INPUT_KEYS_TO_IGNORE:
            new_value = unlist(input_dict[key])
            # validateKey(key, new_value) # DEBUGONLY 
            try:
                new_dict[key] = validateKey(key, new_value)
            except Exception as e:
                # print(f'Wrong input for {key}: {new_value}') # DEBUGONLY
                wrong_imputs[key] = new_value

    return new_dict, wrong_imputs

def open_input_csv_and_comment(upload_csv_content, filename):
    '''
    Opens the input file content and stores it in a pandas DataFrame.
    NOTE: so far, only the first line of an input csv is read.
    '''
    _, upload_string = upload_csv_content.split(',')
    decoded = base64.b64decode(upload_string)
    try:
        # TODO: extarct content from .xlsx files as well.
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=';')
        else:
            return {}, 'CSV file can’t be read, doing nothing…', 'The file extension is not "csv".'
    except Exception as e:
        subtitle = 'CSV file can’t be read, doing nothing…'
        message = f'We got the following error type: {type(e)}, and message: {str(e)}.'
        return {}, subtitle, message
    # TODO : raise a warning if there are several rows in the input csv
    return  {key: val[0] for key, val in df.to_dict().items()}, 'Input can be opened correctly', ''

def read_csv_input(upload_csv:pd.DataFrame):
    '''
    Reads the input dataframe to extract all the keys supposed to be verified.
    When an input raises an error, it is replaced by its corresponding default value.
    Returns:
    - values: curated inputs
    - show_error_mess [bool]: whether to display an error message 
    - mess_subtitle [str]: erorr message subtitle
    - mess_content [str]: error message content
    '''
    show_error_mess = False
    mess_subtitle = 'Filling in values from the input csv file.'
    mess_content = ''
    
    # Loads the right dataset to validate the inputs
    appVersions_options_list = get_available_versions()
    new_version = DEFAULT_VALUES['appVersion']
    if 'appVersion' in upload_csv:
        new_version = unlist(upload_csv['appVersion'])
    assert new_version in (appVersions_options_list + [CURRENT_VERSION])
    if new_version == CURRENT_VERSION:
        newData = load_data(os.path.join(DATA_DIR, 'latest'), version=CURRENT_VERSION)
    else:
        newData = load_data(os.path.join(DATA_DIR, new_version), version=new_version)

    # Validates the inputs against the data
    processed_inputs, invalid_inputs = validateInput(
        input_dict=upload_csv,
        data_dict=newData,
        keysOfInterest=list(upload_csv.keys())
    )
    if len(invalid_inputs) > 0:
        show_error_mess = True
        mess_content += f'\n\nThere seems to be some typos in the csv columns name or inconsistencies in its values, ' \
                        f'so we use default values for the following fields: \n'
        mess_content += f"{', '.join(list(invalid_inputs.keys()))}." 

    # Returns the verified inputs, where wrong keys are replaced by default values,
    # hence the importance of the order of the keys
    values = copy.deepcopy(DEFAULT_VALUES)
    values.update((k, processed_inputs[k]) for k in values.keys() & processed_inputs.keys())
    return values, show_error_mess, mess_subtitle, mess_content




