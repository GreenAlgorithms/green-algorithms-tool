# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
from dash import dcc,html, ctx

from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from types import SimpleNamespace

from flask import send_file # Integrating Loader IO

import pandas as pd
import os
import copy
import numpy as np
import json
import time

from collections import OrderedDict
from urllib import parse

import pycountry_convert as pc

from html_layout import create_appLayout

current_version = 'v2.2'

#############
# LOAD DATA #
#############

data_dir = os.path.join(os.path.abspath(''),'data')
image_dir = os.path.join('assets/images')
static_image_route = '/static/'

# We download each csv and store it in a pd.DataFrame
# We ignore the first row, as it contains metadata
# All these correspond to tabs of the spreadsheet on the Google Drive

# Helpers functions
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

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

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

########################
# OPTIONS FOR DROPDOWN #
########################

def put_value_first(L, value):
    n = len(L)
    if value in L:
        L.remove(value)
        return [value] + L
        assert len(L)+1 == n
    else:
        # print(f'{value} not in list') # DEBUGONLY
        return L

yesNo_options = [
    {'label': 'Yes', 'value': 'Yes'},
    {'label': 'No', 'value': 'No'}
]

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

####################
# GRAPHIC SETTINGS #
####################

myColors = {
    'fontColor':'rgb(60, 60, 60)',
    'boxesColor': "#F9F9F9",
    'backgroundColor': '#f2f2f2',
    'pieChart': ['#E8A09A','#9BBFE0','#cfabd3'],
    'plotGrid':'#e6e6e6',
    'map1':['#78E7A2','#86D987','#93CB70','#9EBC5C',
           '#A6AD4D','#AB9E43','#AF8F3E','#AF803C','#AC713D','#A76440','#9E5943']

}

def colours_hex2rgba(hex):
    h = hex.lstrip('#')
    return('rgba({},{},{})'.format(*tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))))

def convertList_hex2rgba(hex_list):
    out = []
    for hex in hex_list:
        out.append(colours_hex2rgba(hex))

    return out

font_graphs = "Raleway"

layout_plots = dict(
    autosize=True,
    # margin=dict(l=30, r=30, b=20, t=40),
    margin=dict(l=0, r=0, b=0, t=50),
    paper_bgcolor=myColors['boxesColor'],
    plot_bgcolor=myColors['boxesColor'],
    # height=400,
    font = dict(family=font_graphs, color=myColors['fontColor']),
    separators=".,",
    # modebar = dict(bgcolor='#ff0000')
)

## make map
# The map is not updated when changing versions, but it's probably not an isssue
CI_4map = pd.read_csv(os.path.join(data_dir, 'latest', "CI_aggregated.csv"), sep=',', skiprows=1)
CI_4map['ISO3'] = CI_4map.location.apply(iso2_to_iso3)

map_df = CI_4map.loc[CI_4map.ISO3 != '', ['ISO3', 'carbonIntensity', 'countryName']]
map_df['text'] = map_df.carbonIntensity.apply(round).astype('str') + " gCO2e/kWh"

layout_map = copy.deepcopy(layout_plots)
layout_map['height'] = 250
layout_map['margin']['t'] = 30
layout_map['geo'] = dict(
    projection=dict(
        type='natural earth',
    ),
    showcoastlines=False,
    showocean=True,
    oceancolor=myColors['boxesColor'],
    showcountries=True,
    countrycolor=myColors['boxesColor'],
    showframe=False,
    bgcolor=myColors['boxesColor'],
)

mapCI = go.Figure(
    data=go.Choropleth(
        geojson=os.path.join(data_dir, 'world.geo.json'),
        locations = map_df.ISO3,
        locationmode='geojson-id',
        z=map_df.carbonIntensity.astype(float),
        colorscale=myColors['map1'],
        colorbar=dict(
            title=dict(
                # text="Carbon <br> intensity <br> (gCO2e/kWh)",
                font=dict(
                    color=myColors['fontColor'],
                )
            ),
            tickfont=dict(
                color=myColors['fontColor'],
                size=12,
            ),
            thicknessmode='fraction',
            thickness=0.04,
            xpad=3,
        ),
        showscale=True,
        hovertemplate="%{text} <extra> %{z:.0f} gCO2e/kWh </extra>",
        text=map_df.countryName,
        marker=dict(
            line=dict(
                color=myColors['boxesColor'],
                width=0.5
            )
        ),
    ),
    layout=layout_map
)

images_dir = os.path.join(os.path.abspath(''),'images')

##################
# DEFAULT VALUES #
##################

default_values = dict(
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
    platformType='localServer',
    provider='gcp',
    usageCPUradio='No',
    usageCPU=1.0,
    usageGPUradio='No',
    usageGPU=1.0,
    PUEradio='No',
    PSFradio='No',
    PSF=1,
    appVersion=current_version,
)
# FIXME no default value for location (therefore "reset" doesn't reset location)

# rest_of_default_values = dict(
#     serverContinent='Europe',
# )


##############
# CREATE APP #
##############

external_stylesheets = [
    dict(href="https://fonts.googleapis.com/css?family=Raleway:300,300i,400,400i,600|Ruda:400,500,700&display=swap",
         rel="stylesheet")
]

# print(f'Dash version: {dcc.__version__}') # DEBUGONLY

app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    # these tags are to insure proper responsiveness on mobile devices
    meta_tags=[dict(
        name= 'viewport',
        content="width=device-width, initial-scale=1.0" #maximum-scale=1.0
    )]
)
app.title = "Green Algorithms"
server = app.server

appVersions_options_list = [x for x in os.listdir(data_dir) if ((x[0]=='v')&(x!=current_version))]
appVersions_options_list.sort(reverse=True)
# Add the dev option for testing # TODO make it permanent, with a warning pop up if selected by mistake
# appVersions_options_list.append('dev') # DEBUGONLY

appVersions_options = [{'label': f'{current_version} (latest)', 'value': current_version}] + [{'label': k, 'value': k} for k in appVersions_options_list]

app.layout = create_appLayout(
    yesNo_options=yesNo_options,
    image_dir=image_dir,
    mapCI=mapCI,
    appVersions_options=appVersions_options,
)

##################
# HELP FUNCTIONS #
##################

def unlist(x):
    if isinstance(x, list):
        assert len(x) == 1
        return x[0]
    else:
        return x


def validateInput(input_dict, data_dict, keysOfInterest):
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


#############
# CALLBACKS #
#############

### URL-BASED QUERY ###
# If parameters are passed on the URL, these are inputs in the app
# In this function, it's all the values that don't have their own callbacks further down
# FIXME still not working in prod
@app.callback(
    [
        Output('runTime_hour_input','value'),
        Output('runTime_min_input','value'),
        Output('coreType_dropdown','value'),
        Output('numberCPUs_input','value'),
        Output('CPUmodel_dropdown', 'value'),
        Output('tdpCPU_input','value'),
        Output('numberGPUs_input','value'),
        Output('GPUmodel_dropdown', 'value'),
        Output('tdpGPU_input','value'),
        Output('memory_input','value'),
        Output('platformType_dropdown','value'),
        Output('provider_dropdown','value'),
        Output('usageCPU_radio','value'),
        Output('usageCPU_input','value'),
        Output('usageGPU_radio','value'),
        Output('usageGPU_input','value'),
        Output('pue_radio','value'),
        Output('PSF_radio', 'value'),
        Output('PSF_input', 'value'),
        Output('appVersions_dropdown','value'),
        Output('fillIn_from_url', 'displayed'),
        Output('fillIn_from_url', 'message'),
    ],
    [
        Input('url_content','search'),
    ],
)
def fillInFromURL(url_search):
    '''
    :param url_search: Format is "?key=value&key=value&..."
    '''
    # validateInput(default_values) # DEBUGONLY
    # print("\n## Running fillInFromURL / triggered by: ", ctx.triggered_prop_ids) # DEBUGONLY

    # print("\n## URL callback 1 / triggered by: ", ctx.triggered_prop_ids)  # DEBUGONLY
    # ctx_msg = json.dumps({
    #     'states': ctx.states,
    #     'triggered': ctx.triggered,
    #     'inputs': ctx.inputs,
    #     'args': ctx.args_grouping
    # }, indent=2) # DEBUGONLY
    # print(ctx_msg) # DEBUGONLY

    show_popup = False
    popup_message = 'Filling in values from the URL. To edit, click reset at the bottom of the form.'

    defaults2 = copy.deepcopy(default_values)

    # pull default PUE eitherway

    if ctx.triggered_id is None:
        # NB This is needed because of this callback firing for no reason as documented by https://community.plotly.com/t/callback-fired-several-times-with-no-trigger-dcc-location/74525
        # print("-> no-trigger callback prevented") # DEBUGONLY
        raise PreventUpdate # TODO find a cleaner workaround

    elif (url_search is not None)&(url_search != ''):

        # print("\n## picked from url") # DEBUGONLY

        show_popup = True

        url = parse.parse_qs(url_search[1:])

        # Load the right dataset to validate the URL inputs
        if 'appVersion' in url:
            new_version = unlist(url['appVersion'])
            # print(f"Validating URL with {new_version} data") # DEBUGONLY
        else:
            # print(f"App version not provided in URL, using default ({default_values['appVersion']})") # DEBUGONLY
            new_version = default_values['appVersion']
        assert new_version in (appVersions_options_list + [current_version])
        if new_version == current_version:
            newData = load_data(os.path.join(data_dir, 'latest'), version=current_version)
        else:
            newData = load_data(os.path.join(data_dir, new_version), version=new_version)

        # Validate URL
        url2, invalidInputs = validateInput(
            input_dict=url,
            data_dict=newData,
            keysOfInterest=list(url.keys())
        )

        defaults2.update((k, url2[k]) for k in defaults2.keys() & url2.keys())

        if len(invalidInputs) > 0:
            popup_message += f'\n\nThere seems to be some typos in this URL, ' \
                            f'using default values for '
            popup_message += f"{', '.join(list(invalidInputs.keys()))}."

    # print(tuple(defaults2.values()) + (show_popup,popup_message)) # DEBUGONLY
    return tuple(defaults2.values()) + (show_popup,popup_message)

@app.callback(
    [
        Output('runTime_hour_input','disabled'),
        Output('runTime_min_input','disabled'),
        Output('coreType_dropdown','disabled'),
        Output('numberCPUs_input','disabled'),
        Output('CPUmodel_dropdown', 'disabled'),
        Output('tdpCPU_input','disabled'),
        Output('numberGPUs_input','disabled'),
        Output('GPUmodel_dropdown', 'disabled'),
        Output('tdpGPU_input','disabled'),
        Output('memory_input','disabled'),
        Output('platformType_dropdown','disabled'),
        Output('provider_dropdown','disabled'),
        Output('appVersions_dropdown','disabled'),
        Output('location_continent_dropdown', 'disabled'),
        Output('location_country_dropdown', 'disabled'),
        Output('location_region_dropdown', 'disabled'),
        Output('usageCPU_input','disabled'),
        Output('usageGPU_input','disabled'),
        Output('PUE_input','disabled'),
        Output('PSF_input','disabled'),
        Output('runTime_hour_input','style'),
        Output('runTime_min_input','style'),
        Output('numberCPUs_input','style'),
        Output('tdpCPU_input','style'),
        Output('numberGPUs_input','style'),
        Output('tdpGPU_input','style'),
        Output('memory_input','style'),
        Output('usageCPU_radio','options'),
        Output('usageGPU_radio','options'),
        Output('pue_radio','options'),
        Output('PSF_radio', 'options'),
    ],
    [
        Input('url_content','search'),
    ],
)
def disable_inputFromURL(url_search):
    '''
    Disable all the input fields when filling in from URL to avoid weird inter-dependancies
    :param url_search:
    :return:
    '''
    n_output_disable = 20
    n_output_style = 7
    n_radio = 4

    if (url_search is not None) & (url_search != ''):
        yesNo_options_disabled = [
            {'label': 'Yes', 'value': 'Yes', 'disabled':True},
            {'label': 'No', 'value': 'No', 'disabled':True}
        ]

        return (True,)*n_output_disable + ({'background-color': myColors['boxesColor']},)*n_output_style + (yesNo_options_disabled,)*n_radio
    else:
        return (False,)*n_output_disable + (dict(),)*n_output_style + (yesNo_options,)*n_radio

@app.callback(
    Output('url_content', 'search'),
    [
        Input('confirm_reset','submit_n_clicks'),
    ]
)
def reset_url(submit_n_clicks):
    '''
    When clicking reset, it reloads a new pages and removes the URL
    :param submit_n_clicks:
    :return:
    '''
    # Other way to do it:
    # changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # if ('confirm_reset' in changed_id):
    if submit_n_clicks:
        return ""

######
## PLATFORM AND PROVIDER
################

@app.callback(
    Output('platformType_dropdown', 'options'),
    [Input('versioned_data','data')]
)
def set_platform(data):
    if data is not None:
        data_dict = SimpleNamespace(**data)

        platformType_options = [
            {'label': k,
             'value': v} for v, k in list(data_dict.providersTypes.items()) +
                                     [('personalComputer', 'Personal computer')] +
                                     [('localServer', 'Local server')]
        ]
        return platformType_options
    else:
        return []

@app.callback(
    Output('provider_dropdown_div', 'style'),
    [Input('platformType_dropdown', 'value')]
)
def set_providers(selected_platform):
    '''
    Shows or hide the "providers" box, based on the platform selected
    '''
    # print('\n## platformDropdown changed to: ', selected_platform) # DEBUGONLY

    if selected_platform in ['cloudComputing']:
        # Only Cloud Computing need the providers box
        outputStyle = {'display': 'block'}
    else:
        outputStyle = {'display': 'none'}

    return outputStyle

@app.callback(
    Output('provider_dropdown', 'options'),
    [
        Input('platformType_dropdown', 'value'),
        Input('versioned_data','data')
    ],
)
def set_providers(selected_platform, data):
    '''
    List options for the "provider" box
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)

        foo = data_dict.platformName_byType.get(selected_platform)
        if foo is not None:
            availableOptions = list(foo.items())
        else:
            availableOptions = []

        listOptions = [
            {'label': v, 'value': k} for k, v in availableOptions + [("other","Other")]
        ]

        return listOptions
    else:
        return []

######
## COMPUTING CORES
################

@app.callback(
    Output('coreType_dropdown', 'options'),
    [
        Input('provider_dropdown', 'value'),
        Input('platformType_dropdown', 'value'),
        Input('versioned_data','data')
    ])
def set_coreType_options(selected_provider, selected_platform, data):
    '''
    List of options for coreType (CPU or GPU), based on the platform/provider selected
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)

        availableOptions = data_dict.cores_dict.keys()
        listOptions = [{'label': k, 'value': k} for k in list(sorted(availableOptions))+['Both']]
        return listOptions
    else:
        return []


@app.callback(
    [
        Output('CPUmodel_dropdown', 'options'),
        Output('GPUmodel_dropdown', 'options')
    ],
    [Input('versioned_data','data')]
)
def set_coreOptions(data):
    '''
    List of options for core models
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)

        coreModels_options = dict()
        for coreType in ['CPU', 'GPU']:
            availableOptions = sorted(list(data_dict.cores_dict[coreType].keys()))
            availableOptions = put_value_first(availableOptions, 'Any')
            coreModels_options[coreType] = [
                {'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions)) +
                                                     [("Other", "other")]
            ]

        return coreModels_options['CPU'], coreModels_options['GPU']

    else:
        return [],[]


@app.callback(
    [
        Output('CPU_div', 'style'),
        Output('title_CPU', 'style'),
        Output('usageCPU_div', 'style'),
        Output('GPU_div', 'style'),
        Output('title_GPU', 'style'),
        Output('usageGPU_div', 'style'),
    ],
    [
        Input('coreType_dropdown', 'value')
    ]
)
def show_CPUGPUdiv(selected_coreType):
    '''
    Show or hide the CPU/GPU input blocks (and the titles) based on the selected core type
    '''
    show = {'display': 'block'}
    showFlex = {'display': 'flex'}
    hide = {'display': 'none'}
    if selected_coreType == 'CPU':
        return show, hide, showFlex, hide, hide, hide
    elif selected_coreType == 'GPU':
        return hide, hide, hide, show, hide, showFlex
    else:
        return show, show, showFlex, show, show, showFlex

@app.callback(
    Output('tdpCPU_div', 'style'),
    [
        Input('CPUmodel_dropdown', 'value'),
    ]
)
def display_TDP4CPU(selected_coreModel):
    '''
    Shows or hide the CPU TDP input box
    '''
    if selected_coreModel == "other":
        return {'display': 'flex'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('tdpGPU_div', 'style'),
    [
        Input('GPUmodel_dropdown', 'value'),
    ]
)
def display_TDP4GPU(selected_coreModel):
    '''
    Shows or hide the GPU TDP input box
    '''
    if selected_coreModel == "other":
        return {'display': 'flex'}
    else:
        return {'display': 'none'}

######
## LOCATION AND SERVER
################

@app.callback(
    [
        Output('location_div', 'style'),
        Output('server_div', 'style'),
    ],
    [
        Input('platformType_dropdown', 'value'),
        Input('provider_dropdown', 'value'),
        Input('server_dropdown','value'),
        Input('versioned_data','data')
    ]
)
def display_location(selected_platform, selected_provider, selected_server, data):
    '''
    Shows either LOCATION or SERVER depending on the platform
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)
        providers_withoutDC = data_dict.providers_withoutDC
    else:
        providers_withoutDC = []

    show = {'display': 'flex'}
    hide = {'display': 'none'}
    if selected_platform == 'cloudComputing':
        if selected_provider in ['other'] + providers_withoutDC:
            return show, hide
        elif selected_server == 'other':
            return show, show
        else:
            return hide, show
    else:
        return show, hide


## SERVER (only for Cloud computing for now)

@app.callback(
    Output('server_continent_dropdown','value'),
    [
        Input('provider_dropdown', 'value'),
        Input('url_content','search'),
        Input('versioned_data','data')
    ]
)
def set_serverContinents_value(selected_provider, url_search, data):
    '''
    Default value for server's continent, depending on the provider
    '''
    availableOptions = availableLocations_continent(selected_provider, data=data)
    url = prepURLqs(url_search, data=data, keysOfInterest=['serverContinent'])

    if len(url)>0: # that means that serverContinent is indeed in the url
        defaultValue = url['serverContinent']
    else:
        if 'Europe' in availableOptions:
            defaultValue = 'Europe'
        else:
            try:
                defaultValue = availableOptions[0]
            except:
                defaultValue = None

    return defaultValue


@app.callback(
    Output('server_continent_dropdown','options'),
    [
        Input('provider_dropdown', 'value'),
        Input('versioned_data','data')
    ]
)
def set_serverContinents_options(selected_provider, data):
    '''
    List of options and default value for server's continent, based on the provider
    '''
    availableOptions = availableLocations_continent(selected_provider, data=data)
    listOptions = [{'label': k, 'value': k} for k in sorted(availableOptions)] + [{'label': 'Other', 'value': 'other'}]
    return listOptions


@app.callback(
    Output('server_dropdown','style'),
    [
        Input('server_continent_dropdown', 'value')
    ]
)
def set_server_style(selected_continent):
    '''
    Show or not the choice of servers, don't if continent is on "Other"
    '''
    if selected_continent == 'other':
        return {'display': 'none'}

    else:
        return {'display': 'block'}

@app.callback(
    Output('server_dropdown','value'),
    [
        Input('provider_dropdown', 'value'),
        Input('server_continent_dropdown', 'value'),
        Input('url_content','search'),
        Input('versioned_data','data')
    ]
)
def set_server_value(selected_provider,selected_continent, url_search, data):
    '''
    Default value for servers, based on provider and continent
    '''

    url = prepURLqs(url_search, data=data, keysOfInterest=['server'])

    if len(url)>0:
        return url['server']
    else:
        if selected_continent == 'other':
            return 'other'

        else:
            availableOptions = availableOptions_servers(selected_provider,selected_continent, data=data)

            try:
                defaultValue = availableOptions[0]['name_unique']
            except:
                defaultValue = None

            return defaultValue

@app.callback(
    Output('server_dropdown','options'),
    [
        Input('provider_dropdown', 'value'),
        Input('server_continent_dropdown', 'value'),
        Input('versioned_data','data')
    ]
)
def set_server_options(selected_provider,selected_continent, data):
    '''
    List of options for servers, based on provider and continent
    '''
    availableOptions = availableOptions_servers(selected_provider,selected_continent,data=data)
    listOptions = [{'label': k['Name'], 'value': k['name_unique']} for k in availableOptions + [{'Name':"other", 'name_unique':'other'}]]

    return listOptions

@app.callback(
    [
        Output('server_continent_dropdown','disabled'),
        Output('server_dropdown','disabled'),
    ],
    [
        Input('server_continent_dropdown','value'),
        Input('server_dropdown','value'),
        Input('url_content','search'),
    ]
)
def disable_server_inputs(continent, server, url_search):
    if (url_search is not None) & (url_search != ''):
        return True,True
    else:
        if (continent=='other')|(server=='other'):
            return True,True
        else:
            return False,False

## LOCATION (only for local server, personal device or "other" cloud server)

@app.callback(
    Output('location_continent_dropdown', 'options'),
    [Input('versioned_data','data')]
)
def set_continentOptions(data):
    if data is not None:
        data_dict = SimpleNamespace(**data)

        continentsList = list(data_dict.CI_dict_byName.keys())
        continentsDict = [{'label': k, 'value': k} for k in sorted(continentsList)]

        return continentsDict
    else:
        return []

@app.callback(
    Output('location_continent_dropdown', 'value'),
    [
        Input('server_continent_dropdown','value'),
        Input('server_div', 'style'),
        Input('url_content','search'),
        Input('versioned_data','data')
    ],
    [
        State('location_continent_dropdown', 'value')
    ]
)
def set_continent_value(selected_serverContinent, display_server, url_search, data, prev_selectedContinent):

    url = prepURLqs(url_search, data=data, keysOfInterest=['locationContinent'])

    # print(dash.callback_context.triggered)

    # changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if len(url)>0:
        return url['locationContinent']
    else:
        if (display_server['display'] != 'none')&(selected_serverContinent != 'other'):
            # the server div is shown, so we pull the continent from there
            return selected_serverContinent
        elif (prev_selectedContinent is not None):
            return prev_selectedContinent
        else:
            return 'Europe'



@app.callback(
    [
        Output('location_country_dropdown', 'options'),
        Output('location_country_dropdown', 'value'),
        Output('location_country_dropdown_div', 'style'),
    ],
    [
        Input('location_continent_dropdown', 'value'),
        Input('url_content','search'),
        Input('versioned_data','data')
    ],
    [
        State('location_country_dropdown', 'value')
    ]
)
def set_countries_options(selected_continent, url_search, data, prev_selectedCountry):
    '''
    List of options and default value for countries.
    Hides country dropdown if continent=World is selected
    '''
    url = prepURLqs(url_search, data=data, keysOfInterest=['locationCountry'])

    availableOptions = availableOptions_country(selected_continent, data=data)
    listOptions = [{'label': k, 'value': k} for k in availableOptions]

    if len(url)>0:
        defaultValue =  url['locationCountry']
    else:
        try:
            defaultValue = availableOptions[0]

        except:
            defaultValue = None
    if (prev_selectedCountry is not None) and (prev_selectedCountry in availableOptions):
        defaultValue = prev_selectedCountry

    if selected_continent == 'World':
        country_style = {'display': 'none'}
    else:
        country_style = {'display': 'block'}

    return listOptions,defaultValue,country_style

@app.callback(
    [
        Output('location_region_dropdown', 'options'),
        Output('location_region_dropdown', 'value'),
        Output('location_region_dropdown_div', 'style'),
    ],
    [
        Input('location_continent_dropdown', 'value'),
        Input('location_country_dropdown', 'value'),
        Input('url_content','search'),
        Input('versioned_data','data')
    ],
    [
        State('location_region_dropdown', 'value'),
    ]

)
def set_regions_options(selected_continent, selected_country, url_search, data, prev_selectedRegion):
    '''
    List of options and default value for regions.
    Hides region dropdown if only one possible region (or continent=World)
    '''
    url = prepURLqs(url_search, data=data, keysOfInterest=['locationRegion'])

    locs = availableOptions_region(selected_continent, selected_country, data=data)
    if data is not None:
        listOptions = [{'label': data['CI_dict_byLoc'][loc]['regionName'], 'value': loc} for loc in locs]
    else:
        listOptions = []

    if len(url)>0:
        defaultValue =  url['locationRegion']
    else:
        try:
            if (prev_selectedRegion is not None) and (prev_selectedRegion in locs):
                defaultValue = prev_selectedRegion
            else:
                defaultValue = locs[0]
        except:
            defaultValue = None

    if (selected_continent == 'World')|(len(listOptions) == 1):
        region_style = {'display': 'none'}
    else:
        region_style = {'display': 'block'}

    return listOptions,defaultValue,region_style


### Usage factor ###

@app.callback(
    Output('usageCPU_input','style'),
    [
        Input('usageCPU_radio', 'value'),
        Input('usageCPU_input', 'disabled')
    ]
)
def display_usage_input(answer_usage, disabled):
    '''
    Show or hide the usage factor input box, based on Yes/No input
    '''

    if answer_usage == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = myColors['boxesColor']

    return out



@app.callback(
    Output('usageGPU_input','style'),
    [
        Input('usageGPU_radio', 'value'),
        Input('usageGPU_input', 'disabled')
    ]
)
def display_usage_input(answer_usage, disabled):
    '''
    Show or hide the usage factor input box, based on Yes/No input
    '''
    if answer_usage == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = myColors['boxesColor']

    return out


### PUE ###

@app.callback(
    Output('PUEquestion_div','style'),
    [
        Input('location_region_dropdown','value'),
        Input('platformType_dropdown', 'value'),
        Input('provider_dropdown', 'value'),
        Input('server_dropdown', 'value')
    ]
)
def display_pue_question(selected_datacenter, selected_platform, selected_provider, selected_server):
    '''
    Shows or hides the PUE question depending on the platform
    '''

    if selected_platform == 'localServer':
        return {'display': 'flex'}
    elif (selected_platform == 'cloudComputing')&((selected_provider == 'other')|(selected_server == 'other')):
        return {'display': 'flex'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('PUE_input','style'),
    [
        Input('pue_radio', 'value'),
        Input('PUE_input','disabled')
    ]
)
def display_pue_input(answer_pue, disabled):
    '''
    Shows or hides the PUE input box
    '''
    if answer_pue == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = myColors['boxesColor']

    return out

@app.callback(
    Output('PUE_input','value'),
    [
        Input('pue_radio', 'value'),
        Input('url_content','search'),
        Input('versioned_data','data')
    ]
)
def set_PUE(radio, url_search, data):
    url = prepURLqs(url_search, data=data, keysOfInterest=['PUE'])

    if data is not None:
        data_dict = SimpleNamespace(**data)
        defaultPUE = data_dict.pueDefault_dict['Unknown']
    else:
        defaultPUE = 0

    if radio == 'No':
        return defaultPUE
    else:
        if len(url)>0:
            return url['PUE']
        else:
            return defaultPUE

### PSF ###

@app.callback(
    Output('PSF_input','style'),
    [
        Input('PSF_radio', 'value'),
        Input('PSF_input', 'disabled')
    ]
)
def display_PSF_input(answer_PSF, disabled):
    '''
    Shows or hides the PSF input box
    '''
    if answer_PSF == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = myColors['boxesColor']

    return out


## RESET ###

@app.callback(
    Output('confirm_reset','displayed'),
    [
        Input('reset_link','n_clicks')
    ]
)
def display_confirm(clicks):
    if clicks is not None:
        return True
    return False

## CHANGE APP VERSION ##

@app.callback(
    Output('oldVersions_div','style'),
    [
        Input('oldVersion_link','n_clicks'),
        Input('appVersions_dropdown','value')
    ],
    [
        State('oldVersions_div', 'style')
    ]
)
def display_oldVersion(clicks, version, oldStyle):
    if (clicks is not None)|((version is not None)&(version != current_version)):
        return {'display':'flex'}
    else:
        return oldStyle

@app.callback(
    Output("versioned_data", "data"),
    [
        Input('appVersions_dropdown','value')
    ],
)
def loadDataFromVersion(
        newVersion,
        # oldData
):
    # print('-- version:', newVersion) # DEBUGONLY

    if newVersion is None:
        newVersion = current_version

    assert newVersion in appVersions_options_list + [current_version]

    if newVersion == current_version:
        newData = load_data(os.path.join(data_dir, 'latest'), version = current_version)
        # print('Loading latest data') # DEBUGONLY
    else:
        newData = load_data(os.path.join(data_dir, newVersion), version=newVersion)
        # print(f'Loading {newVersion} data') # DEBUGONLY
    # print(f"CI FR: {newData.CI_dict_byLoc['FR']['carbonIntensity']}") # DEBUGONLY
    # print(f"TPUv3 TDP: {newData.cores_dict['GPU']['TPU v3']}")  # DEBUGONLY

    return vars(newData) # to turn the SimpleNamespace into a dict that can be json serialized

# app.clientside_callback(
#     clientside_function = ClientsideFunction(
#         namespace='clientside',
#         function_name='reset_function'
#     ),
#     output = Output('placeholder', 'children'),
#     inputs = [Input('confirm_reset', 'submit_n_clicks')]
# )

#################
# PROCESS INPUT #
#################

def showing(style):
    return style['display'] != 'none'

@app.callback(
    Output("aggregate_data", "data"),
    [
        Input('versioned_data','data'),
        Input("coreType_dropdown", "value"),
        Input("numberCPUs_input", "value"),
        Input("CPUmodel_dropdown", "value"),
        Input("tdpCPU_div", "style"),
        Input("tdpCPU_input", "value"),
        Input("numberGPUs_input", "value"),
        Input("GPUmodel_dropdown", "value"),
        Input("tdpGPU_div", "style"),
        Input("tdpGPU_input", "value"),
        Input("memory_input", "value"),
        Input("runTime_hour_input", "value"),
        Input("runTime_min_input", "value"),
        Input("location_continent_dropdown", "value"),
        Input("location_country_dropdown", "value"),
        Input("location_region_dropdown", "value"),
        Input("server_continent_dropdown", "value"),
        Input("server_dropdown", "value"),
        Input('location_div', 'style'),
        Input('server_div','style'),
        Input("usageCPU_radio", "value"),
        Input("usageCPU_input", "value"),
        Input("usageGPU_radio", "value"),
        Input("usageGPU_input", "value"),
        Input('PUEquestion_div','style'),
        Input("pue_radio", "value"),
        Input("PUE_input", "value"),
        Input("PSF_radio", "value"),
        Input("PSF_input", "value"),
        Input('platformType_dropdown', 'value'),
        Input('provider_dropdown', 'value'),
        Input('provider_dropdown_div', 'style')
    ],
    [
        State("aggregate_data", "data")
    ]
)
def aggregate_input_values(data, coreType, n_CPUcores, CPUmodel, tdpCPUstyle, tdpCPU, n_GPUs, GPUmodel, tdpGPUstyle, tdpGPU,
                           memory, runTime_hours, runTime_min, locationContinent, locationCountry, location,
                           serverContinent, server, locationStyle, serverStyle, usageCPUradio, usageCPU, usageGPUradio, usageGPU,
                           PUEdivStyle, PUEradio, PUE, PSFradio, PSF, selected_platform, selected_provider, providerStyle,
                           existing_state):

    output = dict()

    # print('\n## data callback: runTime_hours=', runTime_hours) # DEBUGONLY
    # print("triggered by: ", ctx.triggered_prop_ids) # DEBUGONLY

    permalink = f'http://calculator.green-algorithms.org//'
    # permalink = 'http://127.0.0.1:8050/' # DEBUGONLY
    permalink_temp = ''

    ### Preprocess
    #######

    notReady = False

    ## Runtime
    test_runTime = 0
    if runTime_hours is None:
        actual_runTime_hours = 0
        test_runTime += 1
    else:
        actual_runTime_hours = runTime_hours

    if runTime_min is None:
        actual_runTime_min = 0
        test_runTime += 1
    else:
        actual_runTime_min = runTime_min
    permalink_temp += f'?runTime_hour={actual_runTime_hours}&runTime_min={actual_runTime_min}'
    runTime = actual_runTime_hours + actual_runTime_min/60.

    ## Core type
    if coreType is None:
        notReady = True
    elif (coreType in ['CPU','Both'])&((n_CPUcores is None)|(CPUmodel is None)):
        notReady = True
    elif (coreType in ['GPU','Both'])&((n_GPUs is None)|(GPUmodel is None)):
        notReady = True

    ## Data
    if data is not None:
        data_dict = SimpleNamespace(**data)
        permalink_temp += f'&appVersion={data_dict.version}'
    else:
        notReady = True

    ## Location
    if showing(locationStyle):
        # this means the "location" input is shown, so we use location instead of server
        locationVar = location
        permalink_temp += f'&locationContinent={locationContinent}&locationCountry={locationCountry}&locationRegion={location}'
    elif (server is None)|(server == 'other')|(data is None):
        locationVar = None
    else:
        locationVar = data_dict.datacenters_dict_byName[server]['location']
    if showing(serverStyle):
        permalink_temp += f'&serverContinent={serverContinent}&server={server}'

    ## Platform
    if selected_platform is None:
        notReady = True
    elif (selected_platform == 'cloudComputing')&(selected_provider is None):
        notReady = True

    ## The rest
    if (memory is None)|(tdpCPU is None)|(tdpGPU is None)|(locationVar is None)| \
            (usageCPU is None)|(usageGPU is None)|(PUE is None)|(PSF is None):
        notReady = True

    if notReady:
        output['coreType'] = None
        output['CPUmodel'] = None
        output['n_CPUcores'] = None
        output['GPUmodel'] = None
        output['n_GPUs'] = None
        output['CPUpower'] = None
        output['GPUpower'] = None
        output['memory'] = None
        output['runTime_hours'] = None
        output['runTime_min'] = None
        output['runTime'] = None
        output['location'] = None
        output['carbonIntensity'] = None
        output['usageCPU'] = None
        output['usageGPU'] = None
        output['PUE'] = None
        output['PSF'] = None
        output['selected_platform'] = None
        output['carbonEmissions'] = 0
        output['CE_CPU'] = 0
        output['CE_GPU'] = 0
        output['CE_core'] = 0
        output['CE_memory'] = 0
        output['n_treeMonths'] = 0
        # output['nkm_flying'] = 0
        output['flying_context'] = 0
        output['nkm_drivingUS'] = 0
        output['nkm_drivingEU'] = 0
        output['nkm_train'] = 0
        output['energy_needed'] = 0
        output['power_needed'] = 0
        output['flying_text'] = None
        output['text_CE'] = '... g CO2e'

    else:
        permalink += permalink_temp
        ### PUE
        defaultPUE = data_dict.pueDefault_dict['Unknown']

        if (showing(PUEdivStyle))&(PUEradio == 'Yes'):
            # I only use the inputted PUE if the PUE box is shown AND the radio button is "Yes"
            PUE_used = PUE
            permalink += f'&PUEradio={PUEradio}&PUE={PUE}'
        else:
            # PUE question not asked or is answered by "No"
            if selected_platform == 'personalComputer':
                PUE_used = 1
            elif selected_platform == 'localServer':
                PUE_used = defaultPUE
            else:
                # Cloud
                if selected_provider == 'other':
                    PUE_used = defaultPUE
                else:
                    foo = data_dict.datacenters_dict_byName.get(server)

                    if foo is not None:
                        if pd.isnull(foo['PUE']):
                            # if we don't know the PUE of this specific data centre, or if we don't know the data centre,
                            # we use the provider's default
                            PUE_used = data_dict.pueDefault_dict[selected_provider]
                        else:
                            PUE_used = foo['PUE']
                    else:
                        PUE_used = data_dict.pueDefault_dict[selected_provider]

        ### CORES

        permalink += f'&coreType={coreType}'
        if coreType in ['CPU', 'Both']:
            permalink += f'&numberCPUs={n_CPUcores}&CPUmodel={CPUmodel}'
            if showing(tdpCPUstyle):
                # we asked the question about TDP
                permalink += f'&tdpCPU={tdpCPU}'
                CPUpower = tdpCPU
            else:
                if CPUmodel == 'other':
                    CPUpower = tdpCPU
                else:
                    CPUpower = data_dict.cores_dict['CPU'][CPUmodel]

            if usageCPUradio == 'Yes':
                permalink += f'&usageCPUradio=Yes&usageCPU={usageCPU}'
                usageCPU_used = usageCPU
            else:
                usageCPU_used = 1.

            powerNeeded_CPU = PUE_used * n_CPUcores * CPUpower * usageCPU_used
        else:
            powerNeeded_CPU = 0
            CPUpower = 0

        if coreType in ['GPU', 'Both']:
            permalink += f'&numberGPUs={n_GPUs}&GPUmodel={GPUmodel}'
            if showing(tdpGPUstyle):
                permalink += f'&tdpGPU={tdpGPU}'
                GPUpower = tdpGPU
            else:
                if GPUmodel == 'other':
                    GPUpower = tdpGPU
                else:
                    GPUpower = data_dict.cores_dict['GPU'][GPUmodel]

            if usageGPUradio == 'Yes':
                permalink += f'&usageGPUradio=Yes&usageGPU={usageGPU}'
                usageGPU_used = usageGPU
            else:
                usageGPU_used = 1.

            powerNeeded_GPU = PUE_used * n_GPUs * GPUpower * usageGPU_used
        else:
            powerNeeded_GPU = 0
            GPUpower = 0

        ### MEMORY
        permalink += f'&memory={memory}'

        ### PLATFORM
        permalink += f'&platformType={selected_platform}'
        if showing(providerStyle):
            permalink += f'&provider={selected_provider}'

        # SERVER/LOCATION
        carbonIntensity = data_dict.CI_dict_byLoc[locationVar]['carbonIntensity']

        # PSF
        if PSFradio == 'Yes':
            permalink += f'&PSFradio=Yes&PSF={PSF}'
            PSF_used = PSF
        else:
            PSF_used = 1


        # Power needed, in Watt
        powerNeeded_core = powerNeeded_CPU + powerNeeded_GPU
        powerNeeded_memory = PUE_used * (memory * data_dict.refValues_dict['memoryPower'])
        powerNeeded = powerNeeded_core + powerNeeded_memory

        # Energy needed, in kWh (so dividing by 1000 to convert to kW)
        energyNeeded_CPU = runTime * powerNeeded_CPU * PSF_used / 1000
        energyNeeded_GPU = runTime * powerNeeded_GPU * PSF_used / 1000
        energyNeeded_core = runTime * powerNeeded_core * PSF_used / 1000
        eneregyNeeded_memory = runTime * powerNeeded_memory * PSF_used / 1000
        energyNeeded = runTime * powerNeeded * PSF_used / 1000

        # Carbon emissions: carbonIntensity is in g per kWh, so results in gCO2
        CE_CPU = energyNeeded_CPU * carbonIntensity
        CE_GPU = energyNeeded_GPU * carbonIntensity
        CE_core = energyNeeded_core * carbonIntensity
        CE_memory  = eneregyNeeded_memory * carbonIntensity
        carbonEmissions = energyNeeded * carbonIntensity

        output['coreType'] = coreType
        output['CPUmodel'] = CPUmodel
        output['n_CPUcores'] = n_CPUcores
        output['CPUpower'] = CPUpower
        output['GPUmodel'] = GPUmodel
        output['n_GPUs'] = n_GPUs
        output['GPUpower'] = GPUpower
        output['memory'] = memory
        output['runTime_hours'] = actual_runTime_hours
        output['runTime_min'] = actual_runTime_min
        output['runTime'] = runTime
        output['location'] = locationVar
        output['carbonIntensity'] = carbonIntensity
        output['PUE'] = PUE_used
        output['PSF'] = PSF_used
        output['selected_platform'] = selected_platform
        output['carbonEmissions'] = carbonEmissions
        output['CE_CPU'] = CE_CPU
        output['CE_GPU'] = CE_GPU
        output['CE_core'] = CE_core
        output['CE_memory'] = CE_memory
        output['energy_needed'] = energyNeeded
        output['power_needed'] = powerNeeded

        ### CONTEXT

        output['n_treeMonths'] = carbonEmissions / data_dict.refValues_dict['treeYear'] * 12

        output['nkm_drivingUS'] = carbonEmissions / data_dict.refValues_dict['passengerCar_US_perkm']
        output['nkm_drivingEU'] = carbonEmissions / data_dict.refValues_dict['passengerCar_EU_perkm']
        output['nkm_train'] = carbonEmissions / data_dict.refValues_dict['train_perkm']

        if carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NY-SF']:
            output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_PAR-LON']
            output['flying_text'] = "Paris-London"
        elif carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NYC-MEL']:
            output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NY-SF']
            output['flying_text'] = "NYC-San Francisco"
        else:
            output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NYC-MEL']
            output['flying_text'] = "NYC-Melbourne"

        ### text carbon emissions
        carbonEmissions_value = carbonEmissions  # in g CO2e
        carbonEmissions_unit = "g"
        if carbonEmissions_value >= 1e6:
            carbonEmissions_value /= 1e6
            carbonEmissions_unit = "T"
        elif carbonEmissions_value >= 1e3:
            carbonEmissions_value /= 1e3
            carbonEmissions_unit = "kg"
        elif carbonEmissions_value < 1:
            carbonEmissions_value *= 1e3
            carbonEmissions_unit = "mg"

        if (carbonEmissions_value != 0)&((carbonEmissions_value >= 1e3)|(carbonEmissions_value < 1)):
            output['text_CE'] = f"{carbonEmissions_value:,.2e} {carbonEmissions_unit} CO2e"
        else:
            output['text_CE'] = f"{carbonEmissions_value:,.2f} {carbonEmissions_unit} CO2e"

        ### text energy
        energyNeeded_value = energyNeeded  # in kWh
        energyNeeded_unit = "kWh"
        if energyNeeded_value >= 1e3:
            energyNeeded_value /= 1e3
            energyNeeded_unit = "MWh"
        elif energyNeeded_value < 1:
            energyNeeded_value *= 1e3
            energyNeeded_unit = "Wh"

        if (energyNeeded_value != 0) & ((energyNeeded_value >= 1e3) | (energyNeeded_value < 1)):
            output['text_energyNeeded'] = f"{energyNeeded_value:,.2e} {energyNeeded_unit}"
        else:
            output['text_energyNeeded'] = f"{energyNeeded_value:,.2f} {energyNeeded_unit}"

        ### Text tree-months
        treeTime_value = output['n_treeMonths']  # in tree-months
        treeTime_unit = "tree-months"
        if treeTime_value >= 24:
            treeTime_value /= 12
            treeTime_unit = "tree-years"

        if (treeTime_value != 0) & ((treeTime_value >= 1e3) | (treeTime_value < 0.1)):
            output['text_treeYear'] = f"{treeTime_value:,.2e} {treeTime_unit}"
        else:
            output['text_treeYear'] = f"{treeTime_value:,.2f} {treeTime_unit}"

    output['permalink'] = permalink.replace(' ','%20')

    return output

### UPDATE TOP TEXT ###

@app.callback(
    [
        Output("carbonEmissions_text", "children"),
        Output("energy_text", "children"),
        Output("treeMonths_text", "children"),
        Output("driving_text", "children"),
        Output("flying_text", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    text_CE = data.get('text_CE')
    text_energy = data.get('text_energyNeeded')
    text_ty = data.get('text_treeYear')

    if (data['nkm_drivingEU'] != 0) & ((data['nkm_drivingEU'] >= 1e3) | (data['nkm_drivingEU'] < 0.1)):
        text_car = f"{data['nkm_drivingEU']:,.2e} km"
    else:
        text_car = f"{data['nkm_drivingEU']:,.2f} km"

    if data['flying_context'] == 0:
        text_fly = "0"
    elif data['flying_context'] > 1e6:
        text_fly = f"{data['flying_context']:,.0e}"
    elif data['flying_context'] >= 1:
        text_fly = f"{data['flying_context']:,.1f}"
    elif data['flying_context'] >= 0.01:
        text_fly = f"{data['flying_context']:,.0%}"
    elif data['flying_context'] >= 1e-4:
        text_fly = f"{data['flying_context']:,.2%}"
    else:
        text_fly = f"{data['flying_context']*100:,.0e} %"

    return text_CE, text_energy, text_ty, text_car, text_fly

@app.callback(
    Output("flying_label", "children"),
    [Input("aggregate_data", "data")],
)
def update_text(data):
    if (data['flying_context'] >= 1)|(data['flying_context'] == 0):
        foo = f"flights {data['flying_text']}"
    else:
        foo = f"of a flight {data['flying_text']}"
    return foo

### UPDATE PERMALINK ###

@app.callback(
    Output('share_permalink', 'href'),
    [Input("aggregate_data", "data")],
)
def share_permalink(aggData):
    return f"{aggData['permalink']}"

### UPDATE PIE GRAPH ###
@app.callback(
    Output("pie_graph", "figure"),
    [Input("aggregate_data", "data")],
)
def create_pie_graph(aggData):
    layout_pie = copy.deepcopy(layout_plots)
    layout_pie['margin'] = dict(l=0, r=0, b=0, t=60)
    if aggData['coreType'] == 'Both':
        layout_pie['height'] = 400
    else:
        layout_pie['height'] = 350
        layout_pie['margin']['t'] = 40

    labels = ['Memory']
    values = [aggData['CE_memory']]

    if aggData['coreType'] in ['CPU', 'Both']:
        labels.append('CPU')
        values.append(aggData['CE_CPU'])

    if aggData['coreType'] in ['GPU', 'Both']:
        labels.append('GPU')
        values.append(aggData['CE_GPU'])

    annotations = []
    percentages = [x/sum(values) if sum(values)!=0 else 0 for x in values]
    to_del = []
    for i,j in enumerate(percentages):
        if j < 1e-8:
            text = '{} makes up < 1e-6% ({:.0f} gCO2e)'.format(labels[i],values[i])
            annotations.append(text)
            to_del.append(i)
    for idx in sorted(to_del, reverse=True):
        del values[idx]
        del labels[idx]
    annotation = '<br>'.join(annotations)

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                insidetextorientation='horizontal',
                showlegend=False,
                pull=[0.05, 0.05],
                marker=dict(
                    colors=myColors['pieChart']
                ),
                texttemplate="<b>%{label}</b><br>%{percent}",
                textfont=dict(
                    family=font_graphs,
                    color=myColors['fontColor'],
                ),
                hovertemplate='%{value:.0f} gCO2e<extra></extra>',
                hoverlabel=dict(
                    font=dict(
                        family=font_graphs,
                        color=myColors['fontColor'],
                    )
                )
            )
        ],
        layout=layout_pie
    )
    fig.update_layout(
        # Add annotations of trace (<1e-6%) variables
        title = {
            'text':annotation,
            'font':{'size':12},
            'x': 1,
            'xanchor': 'right',
            'y': 0.97,
            'yanchor': 'top',
        }
    )

    return fig


### UPDATE BAR CHART COMPARISON
# FIXME: looks weird with 0 emissions
@app.callback(
    Output("barPlotComparison", "figure"),
    [
        Input("aggregate_data", "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart(aggData, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)

        layout_bar = copy.deepcopy(layout_plots)
        # if aggData['coreType'] == 'Both':
        #     layout_bar['height'] = 400
        # else:
        #     layout_bar['height'] = 350

        layout_bar['xaxis'] = dict(
            color=myColors['fontColor'],
        )

        layout_bar['yaxis'] = dict(
            color=myColors['fontColor'],
            title=dict(
                text='Emissions (gCO2e)',
                standoff=100,
            ),
            showspikes=False,
            showgrid=True,
            gridcolor=myColors['plotGrid'],
        )

        loc_ref = {
            'CH':{'name':'Switzerland'},
            'SE':{'name':'Sweden'},
            'FR':{'name':'France'},
            'CA':{'name':'Canada'},
            'GB':{'name':'United Kingdom'},
            'US':{'name':'USA'},
            'CN':{'name':'China'},
            'IN':{'name':'India'},
            'AU':{'name':'Australia'}
        }

        # calculate carbon emissions for each location
        for countryCode in loc_ref.keys():
            loc_ref[countryCode]['carbonEmissions'] = aggData['energy_needed'] * data_dict.CI_dict_byLoc[countryCode]['carbonIntensity']
            loc_ref[countryCode]['opacity'] = 0.2

        loc_ref['You'] = dict(
            name='Your algorithm',
            carbonEmissions=aggData['carbonEmissions'],
            opacity=1
        )

        loc_df = pd.DataFrame.from_dict(loc_ref, orient='index')

        loc_df.sort_values(by=['carbonEmissions'], inplace=True)

        lines_thickness = [0] * len(loc_df)
        lines_thickness[loc_df.index.get_loc('You')] = 4

        fig = go.Figure(
            data = [
                go.Bar(
                    x=loc_df.name.values,
                    y=loc_df.carbonEmissions.values,
                    marker = dict(
                        color=loc_df.carbonEmissions.values,
                        colorscale=myColors['map1'],
                        line=dict(
                            width=lines_thickness,
                            color=myColors['fontColor'],
                        )
                    ),
                    hovertemplate='%{y:.0f} gCO2e<extra></extra>',
                    hoverlabel=dict(
                        font=dict(
                            color=myColors['fontColor'],
                        )
                    ),

                )
            ],
            layout = layout_bar
        )

        return fig
    else:
        return None

### UPDATE BAR CHARTCPU
@app.callback(
    Output("barPlotComparison_cores", "figure"),
    [
        Input("aggregate_data", "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart_cores(aggData, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)

        layout_bar = copy.deepcopy(layout_plots)

        layout_bar['margin']['t'] = 60

        layout_bar['xaxis'] = dict(
            color=myColors['fontColor'],
        )

        layout_bar['yaxis'] = dict(
            color=myColors['fontColor'],
            showspikes=False,
            showgrid=True,
            gridcolor=myColors['plotGrid'],
        )

        if aggData['coreType'] is None:
            return go.Figure()

        else:
            if aggData['coreType'] in ['GPU','Both']:
                layout_bar['yaxis']['title'] = dict(text='Power draw (W)')

                list_cores0 = [
                    'NVIDIA Jetson AGX Xavier',
                    'NVIDIA Tesla T4',
                    'NVIDIA GTX 1080',
                    'TPU v3',
                    'NVIDIA RTX 2080 Ti',
                    'NVIDIA GTX TITAN X',
                    'NVIDIA Tesla P100 PCIe',
                    'NVIDIA Tesla V100'
                ]
                list_cores = [x for x in list_cores0 if x in data_dict.cores_dict['GPU']]

                coreModel = aggData['GPUmodel']

            else:
                layout_bar['yaxis']['title'] = dict(text='Power draw per core (W)')

                list_cores0 = [
                    'Ryzen 5 3500U',
                    'Xeon Platinum 9282',
                    'Xeon E5-2683 v4',
                    'Core i7-10700',
                    'Xeon Gold 6142',
                    'Core i5-10600',
                    'Ryzen 5 3600',
                    'Core i9-10920XE',
                    'Core i5-10600K',
                    'Ryzen 5 3400G',
                    'Core i3-10320',
                    'Xeon X3430'
                ]
                list_cores = [x for x in list_cores0 if x in data_dict.cores_dict['CPU']]

                coreModel = aggData['CPUmodel']

            if coreModel not in list_cores:
                list_cores.append(coreModel)

            power_list = []

            # calculate carbon emissions for each core
            if aggData['coreType'] in ['GPU','Both']:
                for gpu in list_cores:
                    if gpu == 'other':
                        power_list.append(aggData['GPUpower'])
                    else:
                        power_list.append(data_dict.cores_dict['GPU'][gpu])
            else:
                for cpu in list_cores:
                    if cpu == 'other':
                        power_list.append(aggData['CPUpower'])
                    else:
                        power_list.append(data_dict.cores_dict['CPU'][cpu])

            power_df = pd.DataFrame(dict(coreModel=list_cores, corePower=power_list))
            power_df.sort_values(by=['corePower'], inplace=True)
            power_df.set_index('coreModel', inplace=True)

            lines_thickness = [0] * len(power_df)
            lines_thickness[power_df.index.get_loc(coreModel)] = 4

            fig = go.Figure(
                data = [
                    go.Bar(
                        x=list(power_df.index),
                        y=power_df.corePower.values,
                        marker = dict(
                            color=power_df.corePower.values,
                            colorscale='OrRd',
                            line=dict(
                                width=lines_thickness,
                                color=myColors['fontColor'],
                            )
                        ),
                        hovertemplate='%{y:.1f} W<extra></extra>',
                        hoverlabel=dict(
                            font=dict(
                                color=myColors['fontColor'],
                            )
                        ),

                    )
                ],
                layout = layout_bar
            )

            return fig
    else:
        return None


### UPDATE THE REPORT TEXT ###

@app.callback(
    Output('report_markdown', 'children'),
    [
        Input("aggregate_data", "data"),
        Input('versioned_data','data')
    ],
)
def fillin_report_text(aggData, data):

    if (aggData['n_CPUcores'] is None)&(aggData['n_GPUs'] is None):
        return('')
    elif data is None:
        return ('')
    else:
        data_dict = SimpleNamespace(**data)

        # Text runtime
        minutes = aggData['runTime_min']
        hours = aggData['runTime_hours']
        if (minutes > 0)&(hours>0):
            textRuntime = "{}h and {}min".format(hours, minutes)
        elif (hours > 0):
            textRuntime = "{}h".format(hours)
        else:
            textRuntime = "{}min".format(minutes)

        # text cores
        textCores = ""
        if aggData['coreType'] in ['GPU','Both']:
            if aggData['n_GPUs'] > 1:
                suffixProcessor = 's'
            else:
                suffixProcessor = ''
            textCores += f"{aggData['n_GPUs']} GPU{suffixProcessor} {aggData['GPUmodel']}"
        if aggData['coreType'] == 'Both':
            textCores += " and "
        if aggData['coreType'] in ['CPU','Both']:
            if aggData['n_CPUcores'] > 1:
                suffixProcessor = 's'
            else:
                suffixProcessor = ''
            textCores += f"{aggData['n_CPUcores']} CPU{suffixProcessor} {aggData['CPUmodel']}"

        country = data_dict.CI_dict_byLoc[aggData['location']]['countryName']
        region = data_dict.CI_dict_byLoc[aggData['location']]['regionName']

        if region == 'Any':
            textRegion = ''
        else:
            textRegion = ' ({})'.format(region)

        if country in ['United States of America', 'United Kingdom']:
            prefixCountry = 'the '
        else:
            prefixCountry = ''

        if aggData['PSF'] > 1:
            textPSF = ' and ran {} times in total,'.format(aggData['PSF'])
        else:
            textPSF = ''

        myText = f'''
        > This algorithm runs in {textRuntime} on {textCores},
        > and draws {aggData['text_energyNeeded']}. 
        > Based in {prefixCountry}{country}{textRegion},{textPSF} this has a carbon footprint of {aggData['text_CE']}, which is equivalent to {aggData['text_treeYear']}
        (calculated using green-algorithms.org {current_version} \[1\]).
        '''

        return myText

# Loader IO
@app.server.route('/loaderio-1360e50f4009cc7a15a00c7087429524/')
def download_loader():
    return send_file('assets/loaderio-1360e50f4009cc7a15a00c7087429524.txt',
                     mimetype='text/plain',
                     attachment_filename='loaderio-1360e50f4009cc7a15a00c7087429524.txt',
                     as_attachment=True)

if __name__ == '__main__':
    # allows app to update when code is changed!
    app.run_server(debug=True)