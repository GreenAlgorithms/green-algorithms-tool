# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go

import flask

import pandas as pd
import os
import copy

import pycountry_convert as pc

from html_layout import create_appLayout

#############
# LOAD DATA #
#############

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
pue_df = pd.read_csv(os.path.join(data_dir, "servers_PUE.csv"),
                     sep=',', skiprows=1)
pue_df.drop(['source'], axis=1, inplace=True)

### HARDWARE ###
hardware_df = pd.read_csv(os.path.join(data_dir, "providers_hardware.csv"),
                          sep=',', skiprows=1)
hardware_df.drop(['source'], axis=1, inplace=True)

### OFFSET ###
# offset_df = pd.read_csv(os.path.join(data_dir, "servers_offset.csv"),
#                         sep=',', skiprows=1)
# offset_df.drop(['source'], axis=1, inplace=True)

### CARBON INTENSITY BY LOCATION ###
CI_df =  pd.read_csv(os.path.join(data_dir, "CI_aggregated.csv"),
                     sep=',', skiprows=1)
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
cloudDatacenters_df = pd.read_csv(os.path.join(data_dir, "cloudProviders_datacenters.csv"),
                                  sep=',', skiprows=1)

### LOCAL DATACENTERS ###
localDatacenters_df = pd.read_csv(os.path.join(data_dir, "localProviders_datacenters.csv"),
                                  sep=',', skiprows=1)

datacenters_df = pd.concat([cloudDatacenters_df, localDatacenters_df], axis = 1)
datacenters_dict = dict()
for col in datacenters_df.columns:
    datacenters_dict[col] = list(datacenters_df[col].dropna().values)

### PROVIDERS CODES AND NAMES ###
providersNames_df = pd.read_csv(os.path.join(data_dir, "providersNamesCodes.csv"),
                                sep=',', skiprows=1)

### REFERENCE VALUES
refValues_df = pd.read_csv(os.path.join(data_dir, "referenceValues.csv"),
                           sep=',', skiprows=1)
refValues_df.drop(['source'], axis=1, inplace=True)
refValues_dict = pd.Series(refValues_df.value.values,index=refValues_df.variable).to_dict()

###########
# OPTIONS #
###########

platformType_options = [
    {'label': k,
     'value': v} for k,v in list(providersNames_df.loc[:,['platformName',
                                                          'platformType']].drop_duplicates().apply(tuple, axis=1)) +
                            [('Personal computer', 'personalComputer')] +
                            [('Local server', 'localServer')]
]

yesNo_options = [
    {'label': 'Yes', 'value': 'Yes'},
    {'label': 'No', 'value': 'No'}
]

## COLOURS
myColors = {
    'fontColor':'rgb(60, 60, 60)',
    'boxesColor': "#F9F9F9",
    'backgroundColor': '#f2f2f2',
    'pieChart': ['#E8A09A','#9BBFE0'],
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


##############
# CREATE APP #
##############

external_stylesheets = [
    dict(href="https://fonts.googleapis.com/css?family=Raleway:300,300i,400,400i,600|Ruda:400,500,700&display=swap",
         rel="stylesheet")
]

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
    yesNo_options=yesNo_options,
    PUE_default=pue_df.loc[pue_df.provider == 'Unknown', 'PUE'][0],
    usage_default=1,
    image_dir=image_dir,
    mapCI=mapCI,
)


##############
# CALLBACKS #
##############

### PLATFORM AND PROVIDER ###

# This callback shows or hides the choice of provider
@app.callback(
    Output('provider_dropdown', 'style'),
    [Input('platformType_dropdown', 'value')])
def display_provider(selected_platform):
    # if selected_platform in ['cloudComputing','localServer']:
    if selected_platform in ['cloudComputing']:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# This callback updates the choice of providers depending on the platform
@app.callback(
    Output('provider_dropdown', 'options'),
    [Input('platformType_dropdown', 'value')])
def set_providers_options(selected_platform):
    availableOptions = providersNames_df.loc[providersNames_df.platformType == selected_platform]
    return [{'label': k, 'value': v} for k,v in list(zip(availableOptions.providerName, availableOptions.provider))+
            [("Other","other")]]

# ...and the default value
@app.callback(
    Output('provider_dropdown', 'value'),
    [Input('platformType_dropdown', 'value')])
def set_providers_value(selected_platform):
    if selected_platform in ['cloudComputing']:
        return 'aws'
    else:
        return 'other'

### COMPUTING CORES ###

# This callback updates the choice between CPU/GPU
@app.callback(
    Output('coreType_dropdown', 'options'),
    [Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_coreType_options(selected_provider, selected_platform):
    if (selected_provider == 'other')|(selected_platform in ['personalComputer','cloudComputing','localServer']):
        availableOptions = cores_dict.keys()
    else:
        availableOptions = list(set(hardware_df.loc[hardware_df.provider == selected_provider, 'type']))
    return [{'label': k, 'value': k} for k in sorted(availableOptions)]

# This callback adjusts the list of computing cores to choose from (models)
@app.callback(
    Output('coreModel_dropdown', 'options'),
    [Input('coreType_dropdown', 'value'),
     Input('provider_dropdown','value'),
     Input('platformType_dropdown', 'value')])
def set_coreModels_options(selected_coreType,selected_provider,selected_platform):
    if (selected_provider == 'other')|(selected_platform in ['personalComputer','cloudComputing','localServer']):
        availableOptions = sorted(list(cores_dict[selected_coreType].keys()))
    else:
        availableOptions = sorted(hardware_df.loc[(hardware_df.type == selected_coreType)&(
                hardware_df.provider == selected_provider), 'model'].tolist())
    return [{'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions))+[("Other","other")]]

@app.callback(
    Output('coreModel_dropdown', 'value'),
    [Input('coreType_dropdown', 'value'),
     Input('provider_dropdown','value'),
     Input('platformType_dropdown', 'value')])

def set_coreModels_value(selected_coreType,selected_provider,selected_platform):
    if (selected_provider == 'other') | (selected_platform in ['personalComputer', 'cloudComputing', 'localServer']):
        if selected_coreType == 'CPU':
            return 'Xeon E5-2683 v4'
        else:
            return 'Tesla V100'
    else:
        return sorted(hardware_df.loc[(hardware_df.type == selected_coreType)&(
                hardware_df.provider == selected_provider), 'model'].tolist())[0]

# This callback shows or hide the TDP input
@app.callback(
    Output('tdp_div', 'style'),
    [Input('coreModel_dropdown', 'value')])
def display_TDP(selected_coreModel):
    if selected_coreModel == "other":
        return {'display': 'flex'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('tdp_input','value'),
    [Input('coreType_dropdown', 'value')]
)
def tdp_default(selected_coreType):
    if selected_coreType == 'GPU':
        return 200
    else:
        return 12

### LOCATION ###

# This callback adjusts the list of continents to choose from depending on the provider
@app.callback(
    Output('location_continent_dropdown','options'),
    [Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_continents_options(selected_provider,selected_platform):
    if (selected_provider == 'other')|(selected_platform == 'personalComputer'):
        availableOptions = list(set(CI_df.continentName))
    else:
        availableOptions = list(set(CI_df.loc[CI_df.location.isin(datacenters_dict[selected_provider]),
                                              'continentName']))
    return [{'label': k, 'value': k} for k in sorted(availableOptions)]

# This callback adjusts the list of countries to choose from depending on the continent & the provider
@app.callback(
    Output('location_country_dropdown', 'options'),
    [Input('location_continent_dropdown', 'value'),
     Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_countries_options(selected_continent, selected_provider,selected_platform):
    if (selected_provider == 'other')|(selected_platform == 'personalComputer'):
        availableOptions = list(set(CI_df.loc[(CI_df.continentName == selected_continent), 'countryName']))
    else:
        availableOptions = list(set(CI_df.loc[(CI_df.location.isin(datacenters_dict[selected_provider])) & (
                CI_df.continentName == selected_continent), 'countryName']))
    return [{'label': k, 'value': k} for k in sorted(availableOptions)]

# and this one adjusts the list of region depending on the country & the provider
@app.callback(
    Output('location_region_dropdown', 'options'),
    [Input('location_continent_dropdown', 'value'),
     Input('location_country_dropdown', 'value'),
     Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_cities_options(selected_continent, selected_country,selected_provider,selected_platform):
    if (selected_provider == 'other')|(selected_platform == 'personalComputer'):
        availableOptions = CI_df.loc[(CI_df.continentName == selected_continent) & (
                CI_df.countryName == selected_country)]
    else:
        availableOptions = CI_df.loc[(CI_df.location.isin(datacenters_dict[selected_provider])) & (
                CI_df.continentName == selected_continent) & (
                                             CI_df.countryName == selected_country)]
    availableOptions = availableOptions.sort_values(by=['regionName'])
    return [{'label': k, 'value': v} for k,v in zip(availableOptions.regionName, availableOptions.location)]

# This callback shows or hide the country/region if WORLD is selected
@app.callback(
    [
        Output('location_country_dropdown', 'style'),
        Output('location_region_dropdown', 'style'),
        Output('location_country_dropdown', 'value'),
        Output('location_region_dropdown', 'value')
    ],
    [Input('location_continent_dropdown', 'value')])
def display_countryRegion(selected_continent):
    dictOut = {'display': 'block'}
    if selected_continent == 'Africa':
        return dictOut, dictOut, 'South Africa', 'ZA'
    elif selected_continent == 'Asia':
        return dictOut, dictOut, 'China', 'CN'
    elif selected_continent == 'Europe':
        return dictOut, dictOut, 'United Kingdom', 'GB'
    elif selected_continent == 'North America':
        return dictOut, dictOut, 'United States of America', 'US'
    elif selected_continent == 'Oceania':
        return dictOut, dictOut, 'Australia', 'AU'
    elif selected_continent == 'South America':
        return dictOut, dictOut, 'Brazil', 'BR'
    else: # selected_continent == 'World
        return {'display': 'none'}, {'display': 'none'}, 'Any', 'WORLD'

### Usage ###

# This asks for Usage input if necessary
@app.callback(
    Output('usage_input','style'),
    [Input('usage_radio', 'value')]
)
def display_usage_input(answer_usage):
    if answer_usage == 'No':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

### PUE ###

# This callback shows or hides the PUE question depending on the different answers
@app.callback(
    Output('PUEquestion_div','style'),
    [Input('location_region_dropdown','value'),
     Input('platformType_dropdown', 'value'),
     Input('provider_dropdown', 'value')]
)
def display_pue_question(selected_datacenter, selected_platform, selected_provider):
    providers_knownPUE = list(set(pue_df.provider))

    if selected_platform in ['cloudComputing','personalComputer']:
        return {'display': 'none'}

    elif selected_provider in providers_knownPUE:
        return {'display': 'none'}

    else:
        return {'display': 'flex'}

# And then asks for PUE input if necessary
@app.callback(
    Output('PUE_input','style'),
    [Input('pue_radio', 'value')]
)
def display_pue_input(answer_pue):
    if answer_pue == 'No':
        return {'display': 'none'}
    else:
        return {'display': 'block'}

### STORE ###
@app.callback(
    Output("aggregate_data", "data"),
    [
        Input("coreType_dropdown", "value"),
        Input("coreModel_dropdown", "value"),
        Input("numberCores_input", "value"),
        Input("tdp_input", "value"),
        Input("memory_input", "value"),
        Input("runTime_hour_input", "value"),
        Input("runTime_min_input", "value"),
        Input("location_region_dropdown", "value"),
        Input("usage_input", "value"),
        Input("PUE_input", "value"),
        Input('platformType_dropdown', 'value'),
        Input('provider_dropdown', 'value')
    ],
    [
        State("aggregate_data", "data")
    ]
)
def aggregate_input_values(coreType, coreModel, n_cores, tdp, memory, runTime_hours, runTime_min, location, usage, PUE, selected_platform, selected_provider, existing_state):
    output = dict()

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

    runTime = actual_runTime_hours + actual_runTime_min/60.

    if (coreType is None)|(coreModel is None)|(n_cores is None)|(tdp is None)|(memory is None)|(test_runTime == 2)|(location is None)|(usage is None)|(PUE is None)|(selected_platform is None)|(runTime_hours is None)|(runTime_min is None):
        print('Not enough information to display the results')

        output['coreType'] = None
        output['coreModel'] = None
        output['n_cores'] = None
        output['corePower'] = None
        output['memory'] = None
        output['runTime_hours'] = None
        output['runTime_min'] = None
        output['runTime'] = None
        output['location'] = None
        output['carbonIntensity'] = None
        output['usage'] = None
        output['PUE'] = None
        output['selected_platform'] = None
        output['carbonEmissions'] = 0
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

        return output

    else:
        carbonIntensity = CI_df.loc[CI_df.location == location, "carbonIntensity"].values[0]

        if selected_platform == 'personalComputer':
            PUE_used = 1
        elif selected_provider in pue_df.provider.values:
            PUE_used = pue_df.loc[pue_df.provider == selected_provider, "PUE"].values[0]
        else:
            PUE_used = PUE

        if coreModel == 'other':
            corePower = tdp
        else:
            corePower = cores_dict[coreType][coreModel]

        # Power needed, in Watt
        powerNeeded_core = PUE_used * (n_cores * corePower) * usage
        powerNeeded_memory = PUE_used * (memory * refValues_dict['memoryPower'])
        powerNeeded = powerNeeded_core + powerNeeded_memory

        # Energy needed, in kWh (so dividing by 1000 to convert to kW)
        energyNeeded_core = runTime * powerNeeded_core / 1000
        eneregyNeeded_memory = runTime * powerNeeded_memory / 1000
        energyNeeded = runTime * powerNeeded / 1000

        # Carbon emissions: carbonIntensity is in g per kWh, so results in gCO2
        CE_core = energyNeeded_core * carbonIntensity
        CE_memory  = eneregyNeeded_memory * carbonIntensity
        carbonEmissions = energyNeeded * carbonIntensity

        output['coreType'] = coreType
        output['coreModel'] = coreModel
        output['n_cores'] = n_cores
        output['corePower'] = corePower
        output['memory'] = memory
        output['runTime_hours'] = runTime_hours
        output['runTime_min'] = runTime_min
        output['runTime'] = runTime
        output['location'] = location
        output['carbonIntensity'] = carbonIntensity
        output['PUE'] = PUE_used
        output['selected_platform'] = selected_platform
        output['carbonEmissions'] = carbonEmissions
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
    carbonEmissions_value = data['carbonEmissions'] # in g CO2e
    carbonEmissions_unit = "g"
    if carbonEmissions_value >= 1e6:
        carbonEmissions_value /= 1e6
        carbonEmissions_unit = "T"
    elif carbonEmissions_value >= 1e3:
        carbonEmissions_value /= 1e3
        carbonEmissions_unit = "kg"
    text_CE = "{:,.2f} {} CO2e".format(carbonEmissions_value,
                                       carbonEmissions_unit)

    energyNeeded_value = data['energy_needed'] # in kWh
    energyNeeded_unit = "kWh"
    if energyNeeded_value >= 1e3:
        energyNeeded_value /= 1e3
        energyNeeded_unit = "MWh"
    text_energy = "{:,.2f} {}".format(energyNeeded_value, energyNeeded_unit)

    treeTime_value = data['n_treeMonths'] # in tree-months
    treeTime_unit = "tree-months"
    if treeTime_value >= 24:
        treeTime_value /= 24
        treeTime_unit = "tree-years"
    text_ty = "{:,.2f} {}".format(treeTime_value, treeTime_unit)

    text_car = "{:,.2f} km".format(data['nkm_drivingEU'])
    text_fly = "{:,.0f} %".format(data['flying_context']*100)

    return text_CE, text_energy, text_ty, text_car, text_fly

@app.callback(
    Output("flying_label", "children"),
    [Input("aggregate_data", "data")],
)
def update_text(data):
    return "of a flight {}".format(data['flying_text'])
    # return ["of a flight", html.Br(), "{}".format(data['flying_text'])]

### UPDATE PIE GRAPH ###
@app.callback(
    Output("pie_graph", "figure"),
    [Input("aggregate_data", "data")],
)
def create_pie_graph(aggData):
    layout_pie = copy.deepcopy(layout_plots)

    layout_pie['margin'] = dict(l=0, r=0, b=0, t=20)

    layout_pie['height'] = 300

    fig = go.Figure(
        data=[
            go.Pie(
                labels=['Computing <br> cores', 'Memory'],
                values=[aggData['CE_core'], aggData['CE_memory']],
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

    return fig


### UPDATE BAR CHART COMPARISON
@app.callback(
    Output("barPlotComparison", "figure"),
    [Input("aggregate_data", "data")],
)
def create_bar_chart(aggData):
    layout_bar = copy.deepcopy(layout_plots)

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

        if aggData['coreType'] == 'GPU':
            layout_bar['yaxis']['title'] = dict(text='Power draw (W)')

            list_cores = [
                'Jetson AGX Xavier',
                'Tesla T4',
                'GTX 1080',
                'TPU3',
                'RTX 2080 Ti',
                'GTX TITAN X',
                'Tesla P100 PCIe',
                'Tesla V100'
            ]

        else:
            layout_bar['yaxis']['title'] = dict(text='Power draw per core (W)')

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

        if aggData['coreModel'] not in list_cores:
            list_cores.append(aggData['coreModel'])

        power_list = []

        # calculate carbon emissions for each location
        if aggData['coreType'] == 'GPU':
            for gpu in list_cores:
                if gpu == 'other':
                    power_list.append(aggData['corePower'])
                else:
                    power_list.append(gpu_df.loc[gpu_df.model == gpu, 'TDP_per_core'].values[0])
        else:
            for cpu in list_cores:
                if cpu == 'other':
                    power_list.append(aggData['corePower'])
                else:
                    power_list.append(cpu_df.loc[cpu_df.model == cpu, 'TDP_per_core'].values[0])

        power_df = pd.DataFrame(dict(coreModel=list_cores, corePower=power_list))

        power_df.sort_values(by=['corePower'], inplace=True)

        power_df.set_index('coreModel', inplace=True)

        lines_thickness = [0] * len(power_df)
        lines_thickness[power_df.index.get_loc(aggData['coreModel'])] = 4

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

    if aggData['n_cores'] is None:
        return('')

    else:

        minutes = aggData['runTime_min']
        hours = aggData['runTime_hours']

        if (minutes > 0)&(hours>0):
            textRuntime = "{}h and {}min".format(hours, minutes)
        elif (hours > 0):
            textRuntime = "{}h".format(hours)
        else:
            textRuntime = "{}min".format(minutes)


        if aggData['n_cores'] > 1:
            suffixProcessor = 's'

        else:
            suffixProcessor = ''

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

        myText = '''
        > This algorithm runs in {} on {} {}{} {},
        > which draws {:,.2f} kWh. 
        > Based in {}{}{}, this produces {:,.0f} g of CO2e, which is equivalent to {:.2f} tree-months
        (calculated using www.green-algorithms.org \[1\]).
        '''.format(
            textRuntime,
            aggData['n_cores'], aggData['coreType'], suffixProcessor, aggData['coreModel'],
            aggData['energy_needed'],
            prefixCountry, country, textRegion,
            aggData['carbonEmissions'], aggData['n_treeMonths']
        )

        return myText

if __name__ == '__main__':
    # allows app to update when code is changed!
    app.run_server(debug=True)