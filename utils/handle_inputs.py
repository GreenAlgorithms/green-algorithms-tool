"""
This script implements miscellaneous functions and global variables
used at page loading or when a csv is uploaded.
"""

import os
import copy
import base64
import io

import pandas as pd

from types import SimpleNamespace
from utils.utils import check_CIcountries_df, unlist, put_value_first


###################################################
## GLOABAL VARIABLES

CURRENT_VERSION = 'v3.0'
DATA_DIR = os.path.join(os.path.abspath(''), 'data')

# TODO Add the dev option for testing, make it permanent, with a warning pop up if selected by mistake
APP_VERSION_OPTIONS_LIST = [x for x in os.listdir(DATA_DIR) if ((x[0] == 'v') & (x != CURRENT_VERSION))]
APP_VERSION_OPTIONS_LIST.sort(reverse=True)


def get_available_versions():
    appVersions_options = [{'label': f'{CURRENT_VERSION} (latest)', 'value': CURRENT_VERSION}] + [{'label': k, 'value': k} for k in APP_VERSION_OPTIONS_LIST]
    return appVersions_options

# The default values used to fill in the form when no other input is provided
#-----------------------------------------------------------------------------
# WARNING n°1: do not modify the order unless modifying the order of the outputs of 
# the filling_from_inputs callback accordingly
# WARNING n°2: the keys must absolutely match the columns name of the exported csv, 
# otherwise the value attribution after csv import fails
# TODO: make it more robust by using a dictionary or dataclass for storing ids
#-----------------------------------------------------------------------------
DEFAULT_VALUES_FOR_PAGE_LOAD = dict(
    runTime_hour=12,
    runTime_min=0,
    coreType='Both',
    numberCPUs=12,
    CPU_model_n_cores=26, #average value from the CPU csv
    tdpCPU=200, #average value from the CPU csv
    CPU_die_area=12, #average value from the CPU csv
    numberGPUs=1,
    tdpGPU=223,
    GPU_die_area = 6, #average value from the GPU csv
    GPU_memory = 25,  #average value from the GPU csv
    memory=64,
    platformType= 'localServer',
    carbonIntensity= 475, # in gCO2e/kWh, the world average value
    usageCPUradio='No',
    usageCPU=1.0,
    usageGPUradio='No',
    usageGPU=1.0,
    PUEradio='No',
    mult_factor_radio='No',
    mult_factor=1,
)

# We must distinguish between DEFAULT_VALUES_FOR_PAGE_LOAD  
# and DEFAULT_VALUES because the first one is returned as such in 
# the main loading callback of the form blueprints.
DEFAULT_VALUES = DEFAULT_VALUES_FOR_PAGE_LOAD.copy()
DEFAULT_VALUES.update(
    {
        'locationContinent': 'North America',
        'locationCountry': 'Canada', 
        'locationRegion': 'CA-ON', 
        'provider': 'gcp', 
        'serverContinent': 'Europe',
        'server': 'gcp--europe-west1',
        'PUE': 1.67,
    }
)

AI_PAGE_DEFAULT_VALUES = {
        'reporting_time_scope_unit': 'year',
        'reporting_time_scope_value': 1,
        'R&D_radio': 'No',
        'R&D_MF_value': 0,
        'retrainings_radio': 'No',
        'retrainings_number_input': 0,
        'retrainings_MF_value': 0,
        'continuous_inference_switcher': False,
        'input_data_time_scope_unit': 'month',
        'input_data_time_scope_val': 1,
    }

# The following list should contain tke keys of uploaded CSV that should not
# raise an message error because they are not intended to be processed as inputs
# Not all of them are relevant. 
# TODO: clean it and make it more robust when improving the error message system.
INPUT_KEYS_TO_IGNORE = [
    'runTime',
    'location',
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
    'energy_needed_before_scaling',
    'carbonEmissions_before_scaling',
    'main_training_share',
    'R&D_share',
    'retrainings_share',
    'manufacturing_carbonEmissions_before_scaling',
    'manufacturing_carbonEmissions',
    'manufacturing_abiotic_resources',
    'manufacturing_CE_CPU',
    'manufacturing_CE_GPU',
    'manufacturing_CE_memory',
    'manufacturing_CE_other',
    'manufacturing_ADP_CPU',
    'manufacturing_ADP_GPU',
    'manufacturing_ADP_memory',
    'manufacturing_ADP_other',
]


###################################################
## DATA LOADING 

def load_data(data_dir: str, version: str):
    """
    Download each CSV and store it in a SimpleNamespace.
    We often ignore the first row, as it contains metadata.
    All these CSV correspond to tabs of the spreadsheet on the Google Drive.

    Args:
        data_dir (str): the local directory containing the versioned data to load
        version (str): the version value, for later usage

    Returns:
        data_dict (SimpleNamespace): works as a NameSpace (dot commands work) but is structured
        as a dictionnary. Its different 'attributes' are `cores_dict` (CPUs and GPUs data), 
        `pueDefault_dict` (PUE per provider), `CI_dict_byLoc` (carbon intensities per location, where location
        is a shortname like CA-ON for "Canada - Ontario"), `CI_dict_byName` (a nested dictionnary for carbon intensities per
        continent / country / region), `datacenters_dict_byProvider`, `datacenters_dict_byName`, `refValues_dict` (miscellaneous 
        reference values, most of them for metrics computation) and `hardware_impacts_dict` (all required values for manufacturing
        impacts computation).
    """
    
    # We want to include the version itself in the versioned_data
    data_dict = SimpleNamespace(**{'version': version})

    ### CPU ###
    cpu_df = pd.read_csv(os.path.join(data_dir, "CPUs.csv"), sep=',', skiprows=1)
    cpu_df.set_index('model', inplace=True)
    cpu_df.drop(['source'], axis=1, inplace=True)
    # In previous versions, there was no column for the die area of the cpus
    # so we artificially add it with null values. This tweak avoids modifying the
    # form calculator itself. Otherwise we would have to implement different
    # form behaviours for the different versions depending on the data content
    if 'die_area' not in cpu_df.columns:
        cpu_df['die_area'] = 0

    ### GPU ###
    gpu_df = pd.read_csv(os.path.join(data_dir, "GPUs.csv"), sep=',', skiprows=1)
    gpu_df.set_index('model', inplace=True)
    gpu_df.drop(['source'], axis=1, inplace=True)
    # In previous versions, there was no column for the die area and memory of the gpus
    # so we artificially add it with null values. This tweak avoids modifying the
    # form calculator itself. Otherwise we would have to implement different
    # form behaviours for the different versions depending on the data content
    if 'die_area' not in gpu_df.columns:
        gpu_df['die_area'] = 0
    if 'memory' not in gpu_df.columns:
        gpu_df['memory'] = 0
    

    ### AGGREGATED CORES ###
    # Dict of dict with all the possible models
    # e.g. {'CPU': {'Core i9-10920XE': {'TDP_per_core': 13.8, 'die_area_per_core': None, 'embodied_gwp_per_core': 761.7, 'embodied_adp_per_core': 1.7e-3 ...
    data_dict.cores_dict = {
        'CPU': cpu_df[
            [
                'TDP',
                'die_area',
                'n_cores'
            ]
        ].to_dict(orient='index'),
        'GPU': gpu_df[
            [
                'TDP',
                'die_area',
                'memory',
            ]
        ].to_dict(orient='index')
    }

    ### PUE ###
    pue_df = pd.read_csv(os.path.join(data_dir, "defaults_PUE.csv"), sep=',', skiprows=1)
    pue_df.drop(['source'], axis=1, inplace=True)

    data_dict.pueDefault_dict = pd.Series(pue_df.PUE.values, index=pue_df.provider).to_dict()

    ### CARBON INTENSITY BY LOCATION ###
    CI_df = pd.read_csv(os.path.join(data_dir, "CI_aggregated.csv"), sep=',', skiprows=1)
    check_CIcountries_df(CI_df)
    assert len(set(CI_df.location)) == len(CI_df.location)

    data_dict.CI_dict_byLoc = {}
    for location in CI_df.location:
        foo = {}
        for col in ['continentName', 'countryName', 'regionName', 'carbonIntensity']:
            foo[col] = CI_df.loc[CI_df.location == location, col].values[0]
        data_dict.CI_dict_byLoc[location] = foo

    data_dict.CI_dict_byName = {}
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
    cloudDatacenters_df = pd.read_csv(os.path.join(data_dir, "cloudProviders_datacenters.csv"), sep=',', skiprows=1)
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

    data_dict.platformName_byType = {}
    for platformType in set(providersNames_df.platformType):
        foo = providersNames_df.loc[providersNames_df.platformType == platformType]
        data_dict.platformName_byType[platformType] = pd.Series(providersNames_df.providerName.values, index=providersNames_df.provider).to_dict()

    ### REFERENCE VALUES
    # When implementing the manufacturing impacts backend, we added dozens of 
    # 'reference values' that are stored in a new csv: 'hardware_impacts'. When data from a previous
    # version is used, we artificially create this data so we do not have to adapt
    # the form calculator itself based on the data version. We do the same for some reference values
    # added to the new file 'context.csv'
    if 'context.csv' not in os.listdir(data_dir):
        refValues_df = pd.read_csv(os.path.join(data_dir, "referenceValues.csv"), sep=',', skiprows=1)
        refValues_df.drop(['source'], axis=1, inplace=True)
        memory_power = refValues_df[refValues_df.variable == 'memoryPower']['value'].values[0]
    else: 
        refValues_df = pd.read_csv(os.path.join(data_dir, "context.csv"), sep=',')
    data_dict.refValues_dict = pd.Series(refValues_df.value.values, index=refValues_df.variable).to_dict()

    if 'PB_GWP_per_capita' not in data_dict.refValues_dict.keys():
        data_dict.refValues_dict['PB_GWP_per_capita'] = 1
    if 'PB_ADP_per_capita' not in data_dict.refValues_dict.keys():
        data_dict.refValues_dict['PB_ADP_per_capita'] = 1

    ### HARDWARE IMPACTS
    # WARNING: when changing indexes og this CSV, one also has to change the keys below
    if 'hardware_impacts.csv' not in os.listdir(data_dir):
        data_dict.hardware_impacts_dict = {
            'cpu_die_impact_gwp': 0,
            'cpu_base_impact_gwp': 0,
            'cpu_die_impact_adp': 0,
            'cpu_base_impact_adp': 0,
            'ram_die_impact_gwp': 0,
            'ram_base_impact_gwp': 0,
            'ram_die_impact_adp': 0,
            'ram_base_impact_adp': 0,
            'ram_density': 1.8762,
            'ram_default_strip_size': 32,
            'gpu_die_impact_gwp': 0,
            'gpu_base_impact_gwp': 0,
            'gpu_die_impact_adp': 0,
            'gpu_base_impact_adp': 0,
            'PSU_impact_gwp': 0,
            'PSU_impact_adp': 0,
            'motherboard_impact_gwp': 0,
            'motherboard_impact_adp': 0,
            'rack_casing_impact_gwp': 0,
            'rack_casing_impact_adp': 0,
            'assembly_impact_gwp': 0,
            'assembly_impact_adp': 0,
            'laptop_base_impact_gwp': 0,
            'laptop_base_impact_adp': 0,
            'workstation_base_impact_gwp': 0,
            'workstation_base_impact_adp': 0,
            'active_lifespan_local_server': 1,
            'active_lifespan_cloud_server': 1,
            'active_lifespan_laptop': 1,
            'active_lifespan_workstation': 1,
            'nb_CPU_per_server': 2,
            'nb_GPU_local_per_server': 2,
            'nb_GPU_cloud_per_server': 4,
        }
        data_dict.hardware_impacts_dict['memoryPower'] = memory_power
    else: 
        hardware_impacts_df = pd.read_csv(os.path.join(data_dir, "hardware_impacts.csv"), sep=',')
        hardware_impacts_df.drop(['source'], axis=1, inplace=True)
        data_dict.hardware_impacts_dict = pd.Series(hardware_impacts_df.value.values, index=hardware_impacts_df.variable).to_dict()
    
    return data_dict # This is a SimpleNamespace


###################################################
## DROPDOWN OPTIONS

# The following functions return the options for the target dropdown
# of the form. They are called within the Form blueprints.

def availableLocations_continent(selected_provider: str, versioned_data: dict):
    """
    Provides the available continents for a given provider.
    """
    if versioned_data is not None:
        data_dict = SimpleNamespace(**versioned_data)
        dict_per_server_id_in_provider = data_dict.datacenters_dict_byProvider.get(selected_provider)
    else:
        dict_per_server_id_in_provider = None

    if dict_per_server_id_in_provider is not None:
        availableLocations = [x['location'] for x in dict_per_server_id_in_provider.values()]
        availableLocations = list(set(availableLocations))
        availableOptions = list(set(
            [data_dict.CI_dict_byLoc[x]['continentName'] for x in availableLocations if x in data_dict.CI_dict_byLoc]
        ))
        return availableOptions
    else:
        return []


def availableOptions_servers(selected_provider: str, selected_continent: str, versioned_data: dict):
    """
    Provides the available servers for the given provider and continent.
    """
    if versioned_data is not None:
        data_dict = SimpleNamespace(**versioned_data)
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


def availableOptions_country(selected_continent: str, versioned_data: dict):
    """
    Provides the available country for the selected continent.
    """
    if versioned_data is not None:
        data_dict = SimpleNamespace(**versioned_data)
        ci_per_country_dit = data_dict.CI_dict_byName.get(selected_continent)
    else:
        ci_per_country_dit = None

    if ci_per_country_dit is not None:
        availableOptions = [country for country in ci_per_country_dit]
        availableOptions = sorted(availableOptions)
        return availableOptions
    else:
        return []

def availableOptions_region(selected_continent: str,selected_country: str, data: dict):
    """
    Provides the available region for the selected continent and contry.
    """
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

def validate_main_form_inputs(input_dict: dict, data_dict: dict, keys_of_interest: list):
    """
    Validates the inputs: ensures the consistency between the keys and corresponding 
    value but also between some values.
    Args:
        - input_dict: inputs to process
        - data_dict: backend data used to check consistency between provided values.
        - keyOfInterest [list]: a list of keys to process.
    Returns: 
        - clean_inputs [dict]: a curated subset of input_dict with clean inputs. Its keys
        are contained in keysofInterest.
        - wrong_imputs [dict]: a subset of the input_dict containing inputs
        either raising erorrs either not corresponding to keysOfInterest.
        - TO IMPLEMENT: unkonwn_inputs [dict]: a subset of the input_dict containing 
        inputs with an unknown key.
    """
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
            availableOptions = put_value_first(availableOptions, 'Average')
            coreModels_options[coreType] = [
                {'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions)) +
                                                    [("I can't find my CPU", "other")]
            ]
    else:
        coreModels_options = None

    ### PLATFORM TYPE options
    if 'platformType' in input_dict:
        platformType_options = [
            {'label': k,
            'value': v} for v, k in list(data_dict.providersTypes.items()) +
                                    [('personal_workstation', 'Personal workstation')] +
                                    [('localServer', 'Local server')]
        ]
    else:
        platformType_options = None

    def validateKey(key, value):
        """
        Ensures the consistency between the key and the provided value and
        checks the dependencies between different values.

        WARNING: the keys used to check should be the same as those used
        in the DEFAULT_VALUES and aggregate_data.
        """
        new_val = copy.copy(value)
        if key in ['runTime_hour', 'numberCPUs', 'numberGPUs', 'CPU_model_n_cores']:
            new_val = int(float(new_val))
            assert new_val >= 0
        elif key in ['runTime_min']:
            new_val = float(new_val)
            assert new_val >= 0
        elif key in ['mult_factor']:
            new_val = int(new_val)
            assert new_val >= 1
        elif key in ['tdpCPU', 'CPU_die_area', 'tdpGPU', 'GPU_memory', 'GPU_die_area', 'memory', 'carbonIntensity']:
            if key == 'carbonIntensity':
                # The custom carbon intensity field should not be pre-filled with the regular
                # carbonIntensity column of the exported csv, except if the field is being used (i.e if locationContinent='custom')
                if unlist(input_dict['locationContinent']) != 'custom':
                    new_val = DEFAULT_VALUES['carbonIntensity']
            new_val = float(new_val)
            assert new_val >= 0
        elif key in ['usageCPU', 'usageGPU']:
            new_val = float(new_val)
            assert (new_val >= 0) & (new_val <= 1)
        elif key in ['usageCPUradio', 'usageGPUradio', 'PUEradio', 'mult_factor_radio']:
            assert new_val in ['Yes', 'No']
        elif key == 'coreType':
            assert new_val in ['CPU', 'GPU', 'Both']
        elif key in ['CPUmodel', 'GPUmodel']:
            assert new_val in [x['value'] for x in coreModels_options[key[:3]]]
        elif key == 'platformType':
            # The following line is intended to correct the 'personalComputer' platform that was used in previous version
            # TODO: maybe delete it because serves only very few use cases
            if new_val == 'personalComputer' and  'personalComputer' not in platformType_options:
                new_val = 'personal_workstation'
            assert new_val in [x['value'] for x in platformType_options]
        elif key == 'provider':
            if unlist(input_dict['platformType']) == 'cloudComputing':  # TODO: I don't think this if is necessary?
                assert (new_val in data_dict.platformName_byType['cloudComputing']) | (new_val == 'other')
        elif key == 'serverContinent':
            assert new_val in availableLocations_continent(unlist(input_dict['provider']), versioned_data=vars(data_dict)) + ['other']
        elif key == 'server':
            list_servers = availableOptions_servers(unlist(input_dict['provider']),
                                                    unlist(input_dict['serverContinent']),
                                                    versioned_data=vars(data_dict))
            assert new_val in [x['name_unique'] for x in list_servers] + ["other"]
        elif key == 'locationContinent':
            assert new_val in list(data_dict.CI_dict_byName.keys()) + ['custom']
        elif key == 'locationCountry':
            assert new_val in availableOptions_country(unlist(input_dict['locationContinent']), versioned_data=vars(data_dict))
        elif key == 'locationRegion':
            list_loc = availableOptions_region(
                unlist(input_dict['locationContinent']),
                unlist(input_dict['locationCountry']), 
                data=vars(data_dict)
            )
            assert new_val in list_loc
        elif key == 'PUE':
            new_val = float(new_val)
            assert new_val >= 1
        elif key == 'appVersion':
            assert new_val in [option['value'] for option in appVersions_options_list] + [CURRENT_VERSION]
        else:
            assert False, 'Unknown key'
        return new_val

    ############################
    # Now we validate each of the target key from the input dict

    clean_inputs = {}
    wrong_imputs = {}
    for key in keys_of_interest:
        if key not in INPUT_KEYS_TO_IGNORE:
            new_value = unlist(input_dict[key])
            try:
                clean_inputs[key] = validateKey(key, new_value)
            except Exception as e:
                ### TODO: distinguish between wrong_inputs and unknown_inputs
                wrong_imputs[key] = new_value

    return clean_inputs, wrong_imputs


def validate_ai_page_specific_inputs(input_dict: dict, keys_of_interest: list):
    """
    Validates the inputs related to the ai page: ensures the consistency between 
    the keys and correspondind values. 

    Args:
        input_dict[dict]: inputs to process
        keyOfInterest [list]: a list of keys to process.

    Returns: 
        clean_inputs [dict]: a curated subset of input_dict with clean inputs. Its keys
        are contained in keysofInterest.
        wrong_imputs [dict]: a subset of the input_dict containing inputs raising an error
        (TO IMPLEMENT : with an expected key and a value raising an error).
        TO IMPLEMENT: unkonwn_inputs [dict]: a subset of the input_dict containing inputs with
        an unknown key.
    """

    def validateKey(key, value):
        """
        Ensure the consistency between the key and the provided value and
        checks the dependencies between different values.

        WARNING: the keys used to check should be the same as those used
        in the AI_PAGE_DEFAULT_VALUES and aggregate_data.
        """
        new_val = copy.copy(value)
        if key in ['R&D_radio', 'retrainings_radio']:
            assert new_val in ['Yes', 'No']
        elif key in ['R&D_MF_value', 'retrainings_MF_value']:
            new_val = float(new_val)
            assert new_val >= 0
        elif key  == 'retrainings_number_input':
            new_val = int(new_val)
            assert new_val >= 0
        elif key == 'continuous_inference_switcher':
            assert new_val in [True, False]
        elif key == 'input_data_time_scope_unit':
            assert new_val in ['day', 'week', 'month', 'year']
        elif key == 'input_data_time_scope_val':
            new_val = float(new_val)
            assert new_val >= 0
        elif key == 'reporting_time_scope_unit':
            assert new_val in ['month', 'year']
        elif key == 'reporting_time_scope_value':
            new_val = float(new_val)
            assert new_val >= 0
        else:
            assert False, 'Unknown key'
        return new_val
    
    clean_inputs = {}
    wrong_imputs = {}
    unknown_inputs = {}

    for key in keys_of_interest:
        new_value = unlist(input_dict[key])
        try:
            clean_inputs[key] = validateKey(key, new_value)
        except Exception as e:
            ### TODO: distinguish between wrong_inputs and unknown_inputs
            wrong_imputs[key] = new_value

    return clean_inputs, wrong_imputs


def open_input_csv_and_comment(upload_csv_content: str, filename: str):
    """
    Args:
        upload_csv_content [str]: a binary string corresponding to the uploaded file.
        filename [str]: the uploaded file name.

    Opens the input file content and stores it in a pandas DataFrame.
    NOTE: so far, only the first line of an input csv is read.
    """
    _, upload_string = upload_csv_content.split(',')
    decoded = base64.b64decode(upload_string)
    try:
        # TODO: extract content from .xlsx files as well.
        if '.csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), sep=';')
        else:
            return {}, 'The CSV file can’t be read, so doing nothing…', 'The file extension is not "csv".'
    except Exception as e:
        subtitle = 'The CSV file can’t be read, so doing nothing…'
        message = f'We got the following error type: {type(e)}, and message: {str(e)}.'
        return {}, subtitle, message
    # TODO : raise a warning if there are several rows in the input csv
    return {key: val[0] for key, val in df.to_dict().items()}, 'Input can be opened correctly', ''


def read_base_form_inputs_from_csv(upload_csv:dict):
    """
    Reads the input dataframe to extract all the keys supposed to be verified.
    When an input raises an error, it is replaced by its corresponding default value.

    Args:
        upload_csv (dict): the input csv content

    Returns:
        clean_values (dict): curated inputs.
        invalid_inputs (dict): inputs that could not be read properly.
        missing_inputs (list): expected inputs that were not provided.
        new_version (str): app version to use, maybe coming from input data.
    """
    appVersions_options_list = get_available_versions()
    # Retrieve the target data version if correctly provided
    new_version = CURRENT_VERSION
    if 'appVersion' in upload_csv:
        new_version = unlist(upload_csv['appVersion'])
        if not new_version in [option['value'] for option in appVersions_options_list] + [CURRENT_VERSION]:
            new_version = CURRENT_VERSION
    # Loads the right dataset to validate the inputs
    if new_version == CURRENT_VERSION:
        newData = load_data(os.path.join(DATA_DIR, 'latest'), version=CURRENT_VERSION)
    else:
        newData = load_data(os.path.join(DATA_DIR, new_version), version=new_version)

    # Missing inputs: we need to manually add CPUmodel and GPUmodel because they do not have static default value
    expected_inputs = list(DEFAULT_VALUES.keys()) + ['CPUmodel', 'GPUmodel']
    missing_inputs = list(set(expected_inputs).difference(set((upload_csv.keys()))))

    # Validates the inputs against the data
    processed_inputs, invalid_inputs = validate_main_form_inputs(
        input_dict=upload_csv,
        data_dict=newData,
        keys_of_interest=list(upload_csv.keys())
    )
    # Returns the verified inputs, where wrong keys are replaced
    # by default values, hence the importance of the order of the keys
    clean_values = copy.deepcopy(DEFAULT_VALUES)
    # adding required values that were not found as expected in the processed inputs
    processed_inputs.update((k, DEFAULT_VALUES[k]) for k in set(DEFAULT_VALUES.keys()).difference(set(processed_inputs.keys())))
    # enforcing processed input values for entries that are correct
    clean_values.update((k, processed_inputs[k]) for k in processed_inputs.keys())
    # Small fix for special case: when the provider is not Google Cloud we should not
    # replace the serverContinent and server values by default ones, because it has
    # an influence on how the PUE is computed in the aggregate_input_values callback.
    if clean_values['provider'] != 'gcp':
        clean_values['serverContinent'] = None
        clean_values['server'] = None
    return clean_values, invalid_inputs, missing_inputs, new_version


def clean_non_used_inputs_for_export(form_aggregate_data: dict):
    """
    Sets non-used fields of the form to standardized values (typically 0)
    so the csv downloaded from the web page is less confusing for the user.

    Args:
        form_aggregate_data (dict): the form aggregate data, containing all its fields
    """
    ### Cores processing
    if form_aggregate_data['coreType'] == 'CPU':
        form_aggregate_data['GPUmodel'] = None
        form_aggregate_data['numberGPUs'] = 0
        form_aggregate_data['usageGPU'] = 1
        form_aggregate_data['usageGPUradio'] = 'No'
        form_aggregate_data['tdpGPU'] = 0
    elif form_aggregate_data['coreType'] == 'GPU':
        form_aggregate_data['CPUmodel'] = None
        form_aggregate_data['numberCPUs'] = 0
        form_aggregate_data['usageCPU'] = 1
        form_aggregate_data['usageCPUradio'] = 'No'
        form_aggregate_data['tdpCPU'] = 0
    ### Platform related processing
    if form_aggregate_data['platformType'] != 'cloudComputing':
        form_aggregate_data['provider'] = None
        form_aggregate_data['serverContinent'] = None
        form_aggregate_data['server'] = None
    else:
        if form_aggregate_data['provider'] == 'gcp':
            form_aggregate_data['locationContinent'] = None
            form_aggregate_data['locationCountry'] = None
            form_aggregate_data['locationRegion'] = None
        else:
            form_aggregate_data['serverContinent'] = None
            form_aggregate_data['server'] = None
    return form_aggregate_data


def filter_wrong_inputs(clean_inputs_from_csv: dict, wrong_inputs_from_csv: dict):
    # the pop method is used with None arg to avoid KeyError
    """
    Removes some items from the wrong inputs list.
    For instance, we do not want to raise alerts to the user about
    the 'GPUmodel' field if the 'coreType' field equals 'CPU'.

    Args:
        clean_inputs_from_csv (dict): the processed inputs from the csv.
        wrong_inputs_from_csv (dict): the raw wrong inputs as returned by the checking function.

    Returns:
        wrong_inputs_from_csv (dict): filtered wrong inputs.
    """
    ### Cores processing
    if clean_inputs_from_csv['coreType'] == 'CPU':
        wrong_inputs_from_csv.pop('GPUmodel', None)
        wrong_inputs_from_csv.pop('numberGPUs', None)
        wrong_inputs_from_csv.pop('usageGPU', None)
        wrong_inputs_from_csv.pop('usageGPUradio', None)
        wrong_inputs_from_csv.pop('tdpGPU', None)
    elif clean_inputs_from_csv['coreType'] == 'GPU':
        wrong_inputs_from_csv.pop('CPUmodel', None)
        wrong_inputs_from_csv.pop('numberCPUs', None)
        wrong_inputs_from_csv.pop('usageCPU', None)
        wrong_inputs_from_csv.pop('usageCPUradio', None)
        wrong_inputs_from_csv.pop('tdpCPU', None)
    ### Platform related processing
    if clean_inputs_from_csv['platformType'] != 'cloudComputing':
        wrong_inputs_from_csv.pop('provider', None)
        wrong_inputs_from_csv.pop('serverContinent', None)
        wrong_inputs_from_csv.pop('server', None)
    else:
        if clean_inputs_from_csv['provider'] == 'gcp':
            wrong_inputs_from_csv.pop('locationContinent', None)
            wrong_inputs_from_csv.pop('locationCountry', None)
            wrong_inputs_from_csv.pop('locationRegion', None)
        else:
            wrong_inputs_from_csv.pop('serverContinent', None)
            wrong_inputs_from_csv.pop('server', None)
    ### Location related
    if clean_inputs_from_csv['locationContinent'] == 'custom':
        wrong_inputs_from_csv.pop('locationCountry', None)
        wrong_inputs_from_csv.pop('locationRegion', None)
    ### For consistency with AI page utilities
    wrong_inputs_from_csv.pop('R&D_radio', None)
    wrong_inputs_from_csv.pop('R&D_MF_value', None)
    wrong_inputs_from_csv.pop('retrainings_radio', None)
    wrong_inputs_from_csv.pop('retrainings_number_input', None)
    wrong_inputs_from_csv.pop('retrainings_MF_value', None)
    wrong_inputs_from_csv.pop('continuous_inference_switcher', None)
    wrong_inputs_from_csv.pop('input_data_time_scope_unit', None)
    wrong_inputs_from_csv.pop('input_data_time_scope_val', None)
    wrong_inputs_from_csv.pop('tot_energy_needed', None)
    wrong_inputs_from_csv.pop('tot_carbonEmissions', None)
    return wrong_inputs_from_csv




