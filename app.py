# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from flask import send_file # Integrating Loader IO

import pandas as pd
import os
import copy
import numpy as np

from collections import OrderedDict
from urllib import parse

import pycountry_convert as pc

from html_layout import create_appLayout

#############
# LOAD DATA #
#############

# TODO try to speed up code

data_dir = os.path.join(os.path.abspath(''),'data')
image_dir = os.path.join('assets/images')
static_image_route = '/static/'

# We download each csv and store it in a pd.DataFrame
# We ignore the first row, as it contains metadata
# All these correspond to tabs of the spreadsheet on the Google Drive

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
cores_dict = dict()
cores_dict['CPU'] = pd.Series(cpu_df.TDP_per_core.values,index=cpu_df.model).to_dict()
cores_dict['GPU'] = pd.Series(gpu_df.TDP_per_core.values,index=gpu_df.model).to_dict()

### PUE ###
pue_df = pd.read_csv(os.path.join(data_dir, "defaults_PUE.csv"),
                     sep=',', skiprows=1)
pue_df.drop(['source'], axis=1, inplace=True)

### HARDWARE ###
hardware_df = pd.read_csv(os.path.join(data_dir, "providers_hardware.csv"),
                          sep=',', skiprows=1)
hardware_df.drop(['source'], axis=1, inplace=True)

### OFFSET ###
# TODO include offset of cloud providers
# offset_df = pd.read_csv(os.path.join(data_dir, "servers_offset.csv"),
#                         sep=',', skiprows=1)
# offset_df.drop(['source'], axis=1, inplace=True)

### CARBON INTENSITY BY LOCATION ###
def check_CIcountries(df):
    foo = df.groupby(['continentName', 'countryName'])['regionName'].apply(','.join)
    for x in foo:
        assert 'Any' in x.split(','), f"{x} does't have an 'Any' column"

# TODO Use live electricitymap API for evaluation
CI_df =  pd.read_csv(os.path.join(data_dir, "CI_aggregated.csv"),
                     sep=',', skiprows=1)
check_CIcountries(CI_df)
CI_df.drop(['source','Type'], axis=1, inplace=True)
CI_dict = pd.Series(CI_df.carbonIntensity.values,index=CI_df.location).to_dict()

def iso2_to_iso3(x):
    try:
        output = pc.country_name_to_country_alpha3(pc.country_alpha2_to_country_name(x, cn_name_format="default"),
                                                   cn_name_format="default")
    except:
        output = ''
    return output
CI_df['ISO3'] = CI_df.location.apply(iso2_to_iso3)

### CLOUD DATACENTERS ###
# TODO update all cloud datacenters
cloudDatacenters_df = pd.read_csv(os.path.join(data_dir, "cloudProviders_datacenters.csv"),
                                  sep=',', skiprows=1)

### LOCAL DATACENTERS ###
# TODO: include local datacentres
# localDatacenters_df = pd.read_csv(os.path.join(data_dir, "localProviders_datacenters.csv"),
#                                   sep=',', skiprows=1)
# datacenters_df = pd.concat([cloudDatacenters_df, localDatacenters_df], axis = 1)

# Create final datacentre DF
datacenters_df = cloudDatacenters_df
# Remove datacentres with unknown CI
datacenters_df.dropna(subset=['location'], inplace=True)
# TODO: add data centres from AWS
providers_withoutDC = ['aws']
# datacenters_dict = dict()
# for col in datacenters_df.columns:
#     datacenters_dict[col] = list(datacenters_df[col].dropna().values)

### PROVIDERS CODES AND NAMES ###
providersNames_df = pd.read_csv(os.path.join(data_dir, "providersNamesCodes.csv"),
                                sep=',', skiprows=1)

### REFERENCE VALUES
refValues_df = pd.read_csv(os.path.join(data_dir, "referenceValues.csv"),
                           sep=',', skiprows=1)
refValues_df.drop(['source'], axis=1, inplace=True)
refValues_dict = pd.Series(refValues_df.value.values,index=refValues_df.variable).to_dict()

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
        print(f'{value} not in list')
        return L

platformType_options = [
    {'label': k,
     'value': v} for k,v in list(providersNames_df.loc[:,['platformName',
                                                          'platformType']].drop_duplicates().apply(tuple, axis=1)) +
                            [('Personal computer', 'personalComputer')] +
                            [('Local server', 'localServer')]
]

def build_coreModels_options():
    coreModels_options = dict()
    for coreType in ['CPU','GPU']:
        availableOptions = sorted(list(cores_dict[coreType].keys()))
        availableOptions = put_value_first(availableOptions, 'Any')
        coreModels_options[coreType] = [
            {'label': k, 'value': v} for k, v in list(zip(availableOptions,availableOptions)) +
                                                 [("Other","other")]
        ]
    return coreModels_options

coreModels_options = build_coreModels_options()

yesNo_options = [
    {'label': 'Yes', 'value': 'Yes'},
    {'label': 'No', 'value': 'No'}
]

continentsList = list(set(CI_df.continentName))
continentsDict = [{'label': k, 'value': k} for k in sorted(continentsList)]

def availableLocations_continent(selected_provider):
    availableLocations = datacenters_df.loc[datacenters_df.provider == selected_provider, 'location'].to_list()
    availableLocations = list(set(availableLocations))

    availableOptions = list(set(CI_df.loc[CI_df.location.isin(availableLocations), 'continentName']))

    return availableOptions

def availableOptions_servers(selected_provider,selected_continent):
    locationsINcontinent = CI_df.loc[CI_df.continentName == selected_continent, "location"].values

    availableOptions = datacenters_df.loc[
        (datacenters_df.provider == selected_provider) &
        (datacenters_df.location.isin(locationsINcontinent))
        ]

    availableOptions = availableOptions.sort_values(by=['Name'])

    return availableOptions

def availableOptions_country(selected_continent):
    availableOptions = list(set(CI_df.loc[(CI_df.continentName == selected_continent), 'countryName']))
    availableOptions = sorted(availableOptions)
    return availableOptions

def availableOptions_region(selected_continent,selected_country):
    availableOptions = CI_df.loc[(CI_df.continentName == selected_continent) &
                                 (CI_df.countryName == selected_country)]
    availableOptions = availableOptions.sort_values(by=['regionName'])
    # Move Any to the first row:
    availableOptions["new"] = range(1, len(availableOptions) + 1)
    availableOptions.loc[availableOptions.regionName == 'Any', 'new'] = 0
    availableOptions = availableOptions.sort_values("new").reset_index(drop='True').drop('new', axis=1)
    return availableOptions

####################
# GRAPHIC SETTINGS #
####################

myColors = {
    'fontColor':'rgb(60, 60, 60)',
    'boxesColor': "#F9F9F9",
    'backgroundColor': '#f2f2f2',
    'pieChart': ['#E8A09A','#9BBFE0','#cfabd3'],
    'plotGrid':'#e6e6e6',
    'map':['#78E7A2','#86D987','#93CB70','#9EBC5C',
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

map_df = CI_df.loc[CI_df.ISO3 != '', ['ISO3', 'carbonIntensity', 'countryName']]
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
        colorscale=myColors['map'],
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
    usageGPUradio='No',
    PUEradio='No',
    PSFradio='No',
)

defaultPUE = pue_df.loc[pue_df.provider == 'Unknown', 'PUE'][0]


##############
# CREATE APP #
##############

# TODO better favicon?

external_stylesheets = [
    dict(href="https://fonts.googleapis.com/css?family=Raleway:300,300i,400,400i,600|Ruda:400,500,700&display=swap",
         rel="stylesheet")
]

print(f'Dash version: {dcc.__version__}')

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

app.layout = create_appLayout(
    platformType_options=platformType_options,
    coreModels_options=coreModels_options,
    yesNo_options=yesNo_options,
    image_dir=image_dir,
    mapCI=mapCI,
    location_continentsList=continentsDict,
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

def validateInput(input_dict):
    '''
    Validate the input, either from a url or others
    :param input_dict:
    :return:
    '''
    new_dict = dict()
    for key, value in input_dict.items():
        new_value = unlist(value)

        try:
            if key in ['runTime_hour','runTime_min','numberCPUs','numberGPUs']:
                new_value = int(new_value)
                assert new_value >= 0
            elif key in ['PSF']:
                new_value = int(new_value)
                assert new_value >= 1
            elif key in ['tdpCPU','tdpGPU','memory']:
                new_value = float(new_value)
                assert new_value >= 0
            elif key in ['usageCPU','usageGPU']:
                new_value = float(new_value)
                assert (new_value >= 0)&(new_value <= 1)
            elif key in ['usageCPUradio','usageGPUradio','PUEradio','PSFradio']:
                assert new_value in ['Yes','No']
            elif key == 'coreType':
                assert new_value in ['CPU','GPU','Both']
            elif key in ['CPUmodel','GPUmodel']:
                assert new_value in [x['value'] for x in coreModels_options[key[:3]]]
            elif key == 'platformType':
                assert new_value in [x['value'] for x in platformType_options]
            elif key == 'provider':
                if unlist(input_dict['platformType']) == 'cloudComputing':
                    assert new_value in providersNames_df.loc[providersNames_df.platformType == unlist(input_dict['platformType'])].provider.tolist() + ['other']
            elif key == 'serverContinent':
                assert new_value in availableLocations_continent(unlist(input_dict['provider'])) + ['other']
            elif key == 'server':
                assert new_value in availableOptions_servers(unlist(input_dict['provider']), unlist(input_dict['serverContinent'])).Name.tolist() + ["other"]
            elif key == 'locationContinent':
                assert new_value in continentsList
            elif key == 'locationCountry':
                assert new_value in availableOptions_country(unlist(input_dict['locationContinent']))
            elif key == 'locationRegion':
                assert new_value in availableOptions_region(unlist(input_dict['locationContinent']),unlist(input_dict['locationCountry'])).location.tolist()
            elif key == 'PUE':
                new_value = float(new_value)
                assert new_value >= 1
            else:
                assert False, 'Unknown key'

        except:
            print(f'Wrong input for {key}: {new_value}')
            new_value = None

        new_dict[key] = new_value

    return new_dict

def prepURLqs(url_search):
    if (url_search is not None) & (url_search != ''):
        url = validateInput(parse.parse_qs(url_search[1:]))
    else:
        url = dict()
    return url


#############
# CALLBACKS #
#############

### URL-BASED QUERY ###
# If parameters are passed on the URL, these are inputs in the app
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
        Output('usageGPU_radio','value'),
        Output('pue_radio','value'),
        Output('PSF_radio', 'value'),
    ],
    [
        Input('url','search'),
        Input('confirm_reset','submit_n_clicks'),
    ]
)
def fillInFromURL(url_search, reset_click):
    '''
    Only called once, when the page is loaded.
    :param url_search: Format is "?key=value&key=value&..."
    '''
    # validateInput(default_values) # TODO comment this out when not debugging

    defaults2 = copy.deepcopy(default_values)

    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'confirm_reset' in changed_id:
        return tuple(default_values.values())

    if (url_search is not None)&(url_search != ''):
        url = parse.parse_qs(url_search[1:])
        defaults2.update((k, url[k]) for k in defaults2.keys() & url.keys())
        defaults2 = validateInput(defaults2)
    return tuple(defaults2.values())

######
## PLATFORM AND PROVIDER
################

@app.callback(
    Output('provider_dropdown_div', 'style'),
    [Input('platformType_dropdown', 'value')]
)
def set_providers(selected_platform):
    '''
    Shows or hide the "providers" box, based on the platform selected
    '''
    if selected_platform in ['cloudComputing']:
        # Only Cloud Computing need the providers box
        outputStyle = {'display': 'block'}
    else:
        outputStyle = {'display': 'none'}

    return outputStyle

@app.callback(
    Output('provider_dropdown', 'options'),
    [Input('platformType_dropdown', 'value')],
)
def set_providers(selected_platform):
    '''
    List options for the "provider" box
    '''
    availableOptions = providersNames_df.loc[providersNames_df.platformType == selected_platform]

    listOptions = [
        {'label': k, 'value': v} for k,v in list(zip(availableOptions.providerName, availableOptions.provider)) +
                                            [("Other","other")]
    ]

    return listOptions

######
## COMPUTING CORES
################

@app.callback(
    Output('coreType_dropdown', 'options'),
    [Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_coreType_options(selected_provider, selected_platform):
    '''
    List of options for coreType (CPU or GPU), based on the platform/provider selected
    '''
    # TODO: Add custom hardware for cloud providers
    availableOptions = cores_dict.keys()

    # else:
    #     availableOptions = list(set(hardware_df.loc[hardware_df.provider == selected_provider, 'type']))

    listOptions = [{'label': k, 'value': k} for k in list(sorted(availableOptions))+['Both']]

    return listOptions

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
        Input('server_dropdown','value')
    ]
)
def display_location(selected_platform, selected_provider, selected_server):
    '''
    Shows either LOCATION or SERVER depending on the platform
    '''
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
        Input('url','search')
    ]
)
def set_serverContinents_options(selected_provider, url_search):
    '''
    Default value for server's continent, depending on the provider
    '''
    availableOptions = availableLocations_continent(selected_provider)
    url = prepURLqs(url_search)

    if 'serverContinent' in url.keys():
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
    [Input('provider_dropdown', 'value')]
)
def set_serverContinents_options(selected_provider):
    '''
    List of options and default value for server's continent, based on the provider
    '''
    availableOptions = availableLocations_continent(selected_provider)

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
        Input('url','search')
    ]
)
def set_server_value(selected_provider,selected_continent, url_search):
    '''
    Default value for servers, based on provider and continent
    '''
    url = prepURLqs(url_search)

    if 'server' in url.keys():
        return url['server']
    else:
        if selected_continent == 'other':
            return 'other'

        else:
            availableOptions = availableOptions_servers(selected_provider,selected_continent)

            try:
                defaultValue = availableOptions.Name.values[0]
            except:
                defaultValue = None

            return defaultValue

@app.callback(
    Output('server_dropdown','options'),
    [
        Input('provider_dropdown', 'value'),
        Input('server_continent_dropdown', 'value'),
    ]
)
def set_server_options(selected_provider,selected_continent):
    '''
    List of options for servers, based on provider and continent
    '''

    availableOptions = availableOptions_servers(selected_provider,selected_continent)
    # listOptions = [{'label': k, 'value': v} for k, v in zip(availableOptions.Name, availableOptions.location)]
    listOptions = [{'label': k, 'value': k} for k in list(availableOptions.Name)+[("other")]]

    return listOptions

@app.callback(
    [
        Output('server_continent_dropdown','disabled'),
        Output('server_dropdown','disabled'),
    ],
    [
        Input('server_continent_dropdown','value'),
        Input('server_dropdown','value')
    ]
)
def disable_server_inputs(continent, server):
    if (continent=='other')|(server=='other'):
        return True,True
    else:
        return False,False

## LOCATION (only for local server, personal device or "other" cloud server)

@app.callback(
    Output('location_continent_dropdown', 'value'),
    [
        Input('server_continent_dropdown','value'),
        Input('server_div', 'style'),
        Input('url','search'),
        Input('confirm_reset', 'submit_n_clicks')
    ],
    [
        State('location_continent_dropdown', 'value')
    ]
)
def set_continent_value(selected_serverContinent, display_server, url_search,reset, prev_selectedContinent):
    url = prepURLqs(url_search)
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'locationContinent' in url.keys():
        return url['locationContinent']
    else:
        if ('confirm_reset' in changed_id):
            return 'Europe'
        if (prev_selectedContinent is not None):
            return prev_selectedContinent
        if (display_server['display'] != 'none')&(selected_serverContinent != 'other'):
            # the server div is shown, so we pull the continent from there
            return selected_serverContinent
        else:
            return 'Europe'


@app.callback(
    [
        Output('location_country_dropdown', 'options'),
        Output('location_country_dropdown', 'value'),
        Output('location_country_dropdown_div', 'style')
    ],
    [
        Input('location_continent_dropdown', 'value'),
        Input('url','search'),
    ],
    [
        State('location_country_dropdown', 'value')
    ]
)
def set_countries_options(selected_continent, url_search, prev_selectedCountry):
    '''
    List of options and default value for countries.
    Hides country dropdown if continent=World is selected
    '''
    url = prepURLqs(url_search)
    # TODO add "other" country which prompts for carbon intensity
    # TODO add custom carbon intensity

    availableOptions = availableOptions_country(selected_continent)
    listOptions = [{'label': k, 'value': k} for k in availableOptions]

    if 'locationCountry' in url.keys():
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
        Input('url','search')
    ],
    [
        State('location_region_dropdown', 'value'),
    ]

)
def set_regions_options(selected_continent, selected_country, url_search, prev_selectedRegion):
    '''
    List of options and default value for regions.
    Hides region dropdown if only one possible region (or continent=World)
    '''
    availableOptions = availableOptions_region(selected_continent, selected_country)
    listOptions = [{'label': k, 'value': v} for k,v in zip(availableOptions.regionName, availableOptions.location)]

    url = prepURLqs(url_search)

    if 'locationRegion' in url.keys():
        defaultValue =  url['locationRegion']
    else:
        try:
            if (prev_selectedRegion is not None) and (prev_selectedRegion in availableOptions['location'].values):
                defaultValue = prev_selectedRegion
            else:
                defaultValue = availableOptions.loc[availableOptions.regionName == 'Any', 'location'].values[0]
        except:
            defaultValue = None

    if (selected_continent == 'World')|(len(availableOptions) == 1):
        region_style = {'display': 'none'}
    else:
        region_style = {'display': 'block'}

    return listOptions,defaultValue,region_style


### Usage factor ###

@app.callback(
    Output('usageCPU_input','style'),
    [Input('usageCPU_radio', 'value')]
)
def display_usage_input(answer_usage):
    '''
    Show or hide the usage factor input box, based on Yes/No input
    '''
    if answer_usage == 'No':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output('usageCPU_input','value'),
    [
        Input('usageCPU_radio', 'value'),
        Input('url','search')
    ]
)
def reset_usage_input(radio, url_search):
    if radio == 'No':
        return 1
    else:
        url = prepURLqs(url_search)
        if 'usageCPU' in url.keys():
            return url['usageCPU']
        else:
            return 1

@app.callback(
    Output('usageGPU_input','style'),
    [Input('usageGPU_radio', 'value')]
)
def display_usage_input(answer_usage):
    '''
    Show or hide the usage factor input box, based on Yes/No input
    '''
    if answer_usage == 'No':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output('usageGPU_input','value'),
    [
        Input('usageGPU_radio', 'value'),
        Input('url','search')
    ]
)
def reset_usage_input(radio, url_search):
    if radio == 'No':
        return 1
    else:
        url = prepURLqs(url_search)
        if 'usageGPU' in url.keys():
            return url['usageGPU']
        else:
            return 1

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
    providers_knownPUE = list(set(pue_df.provider))

    if selected_platform == 'localServer':
        return {'display': 'flex'}
    elif (selected_platform == 'cloudComputing')&((selected_provider == 'other')|(selected_server == 'other')):
        return {'display': 'flex'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('PUE_input','style'),
    [Input('pue_radio', 'value')]
)
def display_pue_input(answer_pue):
    '''
    Shows or hides the PUE input box
    '''
    if answer_pue == 'No':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output('PUE_input','value'),
    [
        Input('pue_radio', 'value'),
        Input('url','search')
    ]
)
def reset_PUE_input(radio, url_search):
    if radio == 'No':
        return defaultPUE
    else:
        url = prepURLqs(url_search)
        if 'PUE' in url.keys():
            return url['PUE']
        else:
            return defaultPUE

### PSF ###

@app.callback(
    Output('PSF_input','style'),
    [Input('PSF_radio', 'value')]
)
def display_PSF_input(answer_PSF):
    '''
    Shows or hides the PSF input box
    '''
    if answer_PSF == 'No':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

@app.callback(
    Output('PSF_input','value'),
    [
        Input('PSF_radio', 'value'),
        Input('url','search')
    ]
)
def reset_PSF_input(radio, url_search):
    if radio == 'No':
        return 1
    else:
        url = prepURLqs(url_search)
        if 'PSF' in url.keys():
            return url['PSF']
        else:
            return 1

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
def aggregate_input_values(coreType, n_CPUcores, CPUmodel, tdpCPUstyle, tdpCPU, n_GPUs, GPUmodel, tdpGPUstyle, tdpGPU,
                           memory, runTime_hours, runTime_min, locationContinent, locationCountry, location,
                           serverContinent, server, locationStyle, serverStyle, usageCPUradio, usageCPU, usageGPUradio, usageGPU,
                           PUEradio, PUE, PSFradio, PSF, selected_platform, selected_provider, providerStyle,
                           existing_state):
    output = dict()

    permalink = f'https://green-algorithms.org//'
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

    ## Location
    if showing(locationStyle):
        # this means the "location" input is shown, so we use location instead of server
        locationVar = location
        permalink_temp += f'&locationContinent={locationContinent}&locationCountry={locationCountry}&locationRegion={location}'
    elif (server is None)|(server == 'other'):
        locationVar = None
    else:
        locationVar = cloudDatacenters_df.loc[cloudDatacenters_df.Name == server, 'location'].values[0]
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
        print('Not enough information to display the results')

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
        print('Updating results')
        permalink += permalink_temp
        ### PUE
        if PUEradio == 'Yes':
            PUE_used = PUE
            permalink += f'&PUEradio={PUEradio}&PUE={PUE}'
        else:
            # PUE question not asked
            if selected_platform == 'personalComputer':
                PUE_used = 1
            elif selected_platform == 'localServer':
                PUE_used = defaultPUE
            else:
                # Cloud
                if selected_provider == 'other':
                    PUE_used = defaultPUE
                else:
                    foo = cloudDatacenters_df.loc[cloudDatacenters_df.Name == server, 'PUE'].values

                    if len(foo) == 0:
                        take_default = True
                    elif pd.isnull(foo[0]):
                        take_default = True
                    else:
                        take_default = False
                    if take_default:
                        # if we don't know the PUE of this specific data centre, or if we don't know the data centre,
                        # we use the provider's default
                        PUE_used = pue_df.loc[pue_df.provider == selected_provider, "PUE"].values[0]
                    else:
                        PUE_used = foo[0]

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
                    CPUpower = cores_dict['CPU'][CPUmodel]

            if usageCPUradio == 'Yes':
                permalink += f'&usageCPUradio=Yes&usageCPU={usageCPU}'

            powerNeeded_CPU = PUE_used * n_CPUcores * CPUpower * usageCPU
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
                    GPUpower = cores_dict['GPU'][GPUmodel]

            if usageGPUradio == 'Yes':
                permalink += f'&usageGPUradio=Yes&usageGPU={usageGPU}'

            powerNeeded_GPU = PUE_used * n_GPUs * GPUpower * usageGPU
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
        carbonIntensity = CI_df.loc[CI_df.location == locationVar, "carbonIntensity"].values[0]

        # PSF

        if PSFradio == 'Yes':
            permalink += f'&PSFradio=Yes&PSF={PSF}'

        # Power needed, in Watt
        powerNeeded_core = powerNeeded_CPU + powerNeeded_GPU
        powerNeeded_memory = PUE_used * (memory * refValues_dict['memoryPower'])
        powerNeeded = powerNeeded_core + powerNeeded_memory

        # Energy needed, in kWh (so dividing by 1000 to convert to kW)
        energyNeeded_CPU = runTime * powerNeeded_CPU * PSF / 1000
        energyNeeded_GPU = runTime * powerNeeded_GPU * PSF / 1000
        energyNeeded_core = runTime * powerNeeded_core * PSF / 1000
        eneregyNeeded_memory = runTime * powerNeeded_memory * PSF / 1000
        energyNeeded = runTime * powerNeeded * PSF / 1000

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
        output['PSF'] = PSF
        output['selected_platform'] = selected_platform
        output['carbonEmissions'] = carbonEmissions
        output['CE_CPU'] = CE_CPU
        output['CE_GPU'] = CE_GPU
        output['CE_core'] = CE_core
        output['CE_memory'] = CE_memory
        output['energy_needed'] = energyNeeded
        output['power_needed'] = powerNeeded

        ### CONTEXT

        output['n_treeMonths'] = carbonEmissions / refValues_dict['treeYear'] * 12

        output['nkm_drivingUS'] = carbonEmissions / refValues_dict['passengerCar_US_perkm']
        output['nkm_drivingEU'] = carbonEmissions / refValues_dict['passengerCar_EU_perkm']
        output['nkm_train'] = carbonEmissions / refValues_dict['train_perkm']

        if carbonEmissions < 0.5 * refValues_dict['flight_NY-SF']:
            output['flying_context'] = carbonEmissions / refValues_dict['flight_PAR-LON']
            output['flying_text'] = "Paris-London"
        elif carbonEmissions < 0.5 * refValues_dict['flight_NYC-MEL']:
            output['flying_context'] = carbonEmissions / refValues_dict['flight_NY-SF']
            output['flying_text'] = "NYC-San Francisco"
        else:
            output['flying_context'] = carbonEmissions / refValues_dict['flight_NYC-MEL']
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

        if carbonEmissions_value >= 1e9:
            output['text_CE'] = f"{carbonEmissions_value:,.2e} {carbonEmissions_unit} CO2e"
        else:
            output['text_CE'] = f"{carbonEmissions_value:,.2f} {carbonEmissions_unit} CO2e"

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
    text_CE = data['text_CE']

    energyNeeded_value = data['energy_needed'] # in kWh
    energyNeeded_unit = "kWh"
    if energyNeeded_value >= 1e3:
        energyNeeded_value /= 1e3
        energyNeeded_unit = "MWh"
    if energyNeeded_value >= 1e6:
        text_energy = "{:,.2e} {}".format(energyNeeded_value, energyNeeded_unit)
    else:
        text_energy = "{:,.2f} {}".format(energyNeeded_value, energyNeeded_unit)

    treeTime_value = data['n_treeMonths'] # in tree-months
    treeTime_unit = "tree-months"
    if treeTime_value >= 24:
        treeTime_value /= 12
        treeTime_unit = "tree-years"

    if treeTime_value >=1e6:
        text_ty = "{:,.2e} {}".format(treeTime_value, treeTime_unit)
    else:
        text_ty = "{:,.2f} {}".format(treeTime_value, treeTime_unit)

    if data['nkm_drivingEU'] >=1e6:
        text_car = "{:,.2e} km".format(data['nkm_drivingEU'])
    else:
        text_car = "{:,.2f} km".format(data['nkm_drivingEU'])

    if (data['flying_context']*100) >=1e6:
        text_fly = "{:,.0e} %".format(data['flying_context']*100)
    else:
        text_fly = "{:,.0f} %".format(data['flying_context']*100)

    return text_CE, text_energy, text_ty, text_car, text_fly

@app.callback(
    Output("flying_label", "children"),
    [Input("aggregate_data", "data")],
)
def update_text(data):
    return "of a flight {}".format(data['flying_text'])
    # return ["of a flight", html.Br(), "{}".format(data['flying_text'])]

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
    percentages = [x/sum(values) for x in values]
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
@app.callback(
    Output("barPlotComparison", "figure"),
    [Input("aggregate_data", "data")],
)
def create_bar_chart(aggData):
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
        loc_ref[countryCode]['carbonEmissions'] = aggData['energy_needed'] * CI_df.loc[CI_df.location == countryCode, "carbonIntensity"].values[0]
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
                    colorscale=myColors['map'],
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

### UPDATE BAR CHARTCPU
@app.callback(
    Output("barPlotComparison_cores", "figure"),
    [Input("aggregate_data", "data")],
)
def create_bar_chart_cores(aggData):
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

            list_cores = [
                'NVIDIA Jetson AGX Xavier',
                'NVIDIA Tesla T4',
                'NVIDIA GTX 1080',
                'TPU v3',
                'NVIDIA RTX 2080 Ti',
                'NVIDIA GTX TITAN X',
                'NVIDIA Tesla P100 PCIe',
                'NVIDIA Tesla V100'
            ]

            coreModel = aggData['GPUmodel']

        else:
            layout_bar['yaxis']['title'] = dict(text='Power draw per core (W)')

            # TODO clean CPU core names
            list_cores = [
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
                    power_list.append(gpu_df.loc[gpu_df.model == gpu, 'TDP_per_core'].values[0])
        else:
            for cpu in list_cores:
                if cpu == 'other':
                    power_list.append(aggData['CPUpower'])
                else:
                    power_list.append(cpu_df.loc[cpu_df.model == cpu, 'TDP_per_core'].values[0])

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


### UPDATE THE REPORT TEXT ###

@app.callback(
    Output('report_markdown', 'children'),
    [Input("aggregate_data", "data")],
)
def fillin_report_text(aggData):

    if (aggData['n_CPUcores'] is None)&(aggData['n_GPUs'] is None):
        return('')

    else:

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

        country = CI_df.loc[CI_df.location == aggData['location'], 'countryName'].values[0]
        region = CI_df.loc[CI_df.location == aggData['location'], 'regionName'].values[0]

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
        > and draws {aggData['energy_needed']:,.2f} kWh. 
        > Based in {prefixCountry}{country}{textRegion},{textPSF} this has a carbon footprint of {aggData['text_CE']}, which is equivalent to {aggData['n_treeMonths']:.2f} tree-months
        (calculated using green-algorithms.org v2.1 \[1\]).
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