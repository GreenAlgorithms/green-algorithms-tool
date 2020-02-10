# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate
import plotly.express as px
import plotly.graph_objects as go

import flask

import pandas as pd
import sys
import numpy as np
import os
import copy

import pycountry_convert as pc

# The styles are automatically loaded from the the /assets folder

app = dash.Dash(
    __name__,
    # these tags are to insure proper responsiveness on mobile devices
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

#############
# LOAD DATA #
#############

data_dir = os.path.join(os.path.abspath(''),'data')
image_dir = os.path.join(os.path.abspath(''),'images')
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
cores_dict['CPU'] = pd.Series(cpu_df.TDP.values,index=cpu_df.model).to_dict()
cores_dict['GPU'] = pd.Series(gpu_df.TDP.values,index=gpu_df.model).to_dict()

### PUE ###
pue_df = pd.read_csv(os.path.join(data_dir, "servers_PUE.csv"),
                     sep=',', skiprows=1)
pue_df.drop(['source'], axis=1, inplace=True)

### HARDWARE ###
hardware_df = pd.read_csv(os.path.join(data_dir, "providers_hardware.csv"),
                          sep=',', skiprows=1)
hardware_df.drop(['source'], axis=1, inplace=True)

### OFFSET ###
offset_df = pd.read_csv(os.path.join(data_dir, "servers_offset.csv"),
                        sep=',', skiprows=1)
offset_df.drop(['source'], axis=1, inplace=True)

### CARBON INTENSITY BY LOCATION ###
CI_df =  pd.read_csv(os.path.join(data_dir, "CI_aggregated.csv"),
                        sep=',', skiprows=1)
CI_df.drop(['source'], axis=1, inplace=True)
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
                            [('Personal computer', 'personalComputer')]
]

yesNo_options = [
    {'label': 'Yes', 'value': 'Yes'},
    {'label': 'No', 'value': 'No'}
]

## GLOBAL CHART TEMPLATE
layout = dict(
    autosize=True,
    automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
    # ),
)

## make map

map_df = CI_df.loc[CI_df.ISO3 != '', ['ISO3', 'carbonIntensity', 'countryName']]
map_df['text'] = map_df.carbonIntensity.apply(round).astype('str') + " gCO2e/kWh"

mapColorScale = [
    # greens
    'rgb(116,196,118)',
    'rgb(161,217,155)',
    'rgb(199,233,192)',
    'rgb(229,245,224)',
    'rgb(255,255,229)',
    'rgb(255,247,188)',
    'rgb(254,227,145)',
    'rgb(254,196,79)',
    'rgb(254,153,41)',
    'rgb(236,112,20)',
    'rgb(204,76,2)',
    'rgb(153,52,4)',
    'rgb(102,37,6)'
]

myColors = {
    'boxesColor': "#F9F9F9"
}

mapCI = go.Figure(
    data=go.Choropleth(
        geojson=os.path.join(data_dir, 'world.geo.json'),
        locations = map_df.ISO3,
        locationmode='geojson-id',
        z=map_df.carbonIntensity.astype(float).apply(round),
        colorscale = mapColorScale,
        colorbar_title = "gCO2e/kWh",
        hoverinfo='location+z+text', # Any combination of ['location', 'z', 'text', 'name'] joined with '+' characters
        text=map_df.countryName,
        # name=map_df.countryName,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        showscale=False,
    )
)
mapCI.update_layout(
    title_text = 'Carbon Intensity by country',
    autosize=True,
    # automargin=True,
    margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    # legend=dict(font=dict(size=10), orientation="h"),
    plot_bgcolor=myColors['boxesColor'],
    paper_bgcolor= myColors['boxesColor'],
    geo=dict(
        showframe=False,
        showcoastlines=False,
        projection_type='natural earth',#'equirectangular',
        showocean=True, oceancolor=myColors['boxesColor'], #"#EBF5FB",
        bgcolor=myColors['boxesColor'],
    ),
)



##########
# LAYOUT #
##########

images_dir = os.path.join(os.path.abspath(''),'images')

app.layout = html.Div(
    [
        dcc.Store(id="aggregate_data"),
        # empty Div to trigger javascript file for graph resizing
        html.Div(id="output-clientside"),

        ## HEADER
        html.Div(
            [
                # first image
                html.Div(
                    [
                        html.Img(
                            src=static_image_route+'cbsgi_logo_100dpi.png',
                            id="logo1",
                            style={
                                "height": "60px",
                                "width": "auto",
                                "margin-bottom": "25px",
                            },
                        )
                    ],
                    className="one-third column",
                ),

                # title
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "CO2 impact calculator",
                                    style={"margin-bottom": "0px"},
                                ),
                                html.H5(
                                    "Is your algorithm bad for the planet?",
                                    style={"margin-top": "0px"}
                                ),
                            ]
                        )
                    ],
                    className="one-half column",
                    id="title"
                ),

                html.Div(
                    [
                        html.A(
                            html.Button("Doesn't do anything", id="header-button"),
                            # href="https://plot.ly/dash/pricing/",
                        )
                    ],
                    className="one-third column",
                    id="button-title",
                ),
            ],
            id="header",
            className="row flex-display",
            style={"margin-bottom": "25px"},
        ),

        ## FIRST ROW
        html.Div(
            [
                ## LEFT COLUMN: CALCULATOR INPUT
                html.Div(
                    [
                        ## NUMBER OF CORES
                        html.P(
                            "How many cores:",
                            className="control_label",
                        ),

                        dcc.Input(
                            type='number',
                            id="numberCores_input",
                            value=1,
                            className="dcc_control",
                        ),

                        ## MEMORY
                        html.P(
                            "Memory requested (in GB):",
                            className="control_label",
                        ),

                        dcc.Input(
                            type='number',
                            id="memory_input",
                            value=64,
                            className="dcc_control",
                        ),

                        ## RUN TIME
                        html.P(
                            "Runtime (h):",
                            className="control_label",
                        ),

                        dcc.Input(
                            type='number',
                            id="runTime_input",
                            value=5,
                            className="dcc_control",
                        ),

                        ## SELECT COMPUTING PLATFORM
                        html.P(
                            "Select the platform used for the computations:",
                            className="control_label",
                        ),
                        dcc.RadioItems(
                            id="platformType_dropdown",
                            options=platformType_options,
                            value='cloudComputing',
                            labelStyle={"display": "inline-block"},
                            className="dcc_control",
                        ),
                        # dcc.Dropdown(
                        #     id="platformType_dropdown",
                        #     options=platformType_options,
                        #     value='cloudComputing',
                        #     className="dcc_control",
                        # ),
                        html.Div(
                            [
                                dcc.Dropdown(
                                    id="provider_dropdown",
                                    value='gcp',
                                    className="dcc_control",
                                )
                            ],
                            style = {'display': 'none'},
                            id = 'provider_div'
                        ),

                        ## COMPUTING CORES
                        html.P(
                            "What type of core are you using:",
                            className="control_label",
                        ),

                        dcc.Dropdown(
                            id="coreType_dropdown",
                            value = 'CPU',
                            className="dcc_control",
                        ),

                        dcc.Dropdown(
                            id = "coreModel_dropdown",
                            value = "Xeon E5-2683 v4",
                            className="dcc_control",
                        ),

                        html.Div(
                            [
                                html.P(
                                    'What is the TDP of your computing core (in W)? (easily accessible online)',
                                    className="control_label",
                                ),
                                dcc.Input(
                                    type='number',
                                    id="tdp_input",
                                    value=95,
                                    className="dcc_control",
                                )
                            ],
                            id = "tdp_div",
                            style = {'display': 'none'},
                         ),

                        ## LOCATION
                        html.P(
                            "Select location:",
                            className="control_label",
                        ),
                        dcc.Dropdown(
                            id="location_continent_dropdown",
                            value='North America',
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="location_country_dropdown",
                            value="United States of America",
                            className="dcc_control",
                        ),
                        dcc.Dropdown(
                            id="location_region_dropdown",
                            value = "US-CA",
                            className="dcc_control",
                        ),

                        ## PUE
                        html.Div(
                            [
                                html.P(
                                    "Do you know the Power Usage Efficiency (PUE) of your local datacenter?",
                                    className="control_label",
                                ),

                                dcc.RadioItems(
                                    id = 'pue_radio',
                                    options=yesNo_options,
                                    value='No',
                                    labelStyle={"display": "inline-block"},
                                    className="dcc_control",
                                ),
                            ],
                            id = 'PUEquestion_div',
                            style = {'display': 'none'},
                        ),

                        html.Div(
                            [
                                dcc.Input(
                                    min=1,
                                    type='number',
                                    id="PUE_input",
                                    value=pue_df.loc[pue_df.provider == 'Unknown','PUE'][0]
                                ),
                            ],
                            id = 'PUEinput_div',
                            style = {'display': 'none'},
                            className="dcc_control",
                        ),

                        # html.Button(
                        #     'Compute',
                        #     id='button'
                        # ),

                    ],
                    className="pretty_container four columns",
                    id="input-calculator",
                ),

                ## RIGHT COLUMN
                html.Div(
                    [
                        ## FIRST ROW: DISPLAY RESULTS
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(id="carbonEmissions_text"),
                                        html.P("Carbon emissions")
                                    ],
                                    id="carbonEmissions",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [
                                        html.H6(id="treeYears_text"),
                                        html.P("No. of trees")
                                    ],
                                    id="treeYears",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [
                                        html.H6(id="driving_text"),
                                        html.P("Driving a passenger car")
                                    ],
                                    id="car",
                                    className="mini_container",
                                ),
                                html.Div(
                                    [
                                        html.H6(id="flying_text"),
                                        html.P("Flying in economy")
                                    ],
                                    id="plane",
                                    className="mini_container",
                                ),
                            ],
                            id="info-container",
                            className="row container-display",
                        ),

                        ## SECOND ROW: GRAPH
                        html.Div(
                            [
                                dcc.Graph(id="pie_graph")
                            ],
                            id="pieGraphContainer",
                            className="pretty_container",
                        ),

                    ],
                    id="right-column",
                    className="eight columns",
                ),

            ],
            className="row flex-display",
        ),

        ## SECOND ROW
        html.Div(
            [
                html.Div(
                    [dcc.Graph(id = "map", figure = mapCI)],
                    className="pretty_container seven columns",
                ),
                html.Div(
                    [dcc.Graph(id="individual_graph")],
                    className="pretty_container five columns",
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
    style={
        "display": "flex",
        "flex-direction": "column",
        # 'background-image':'url(http://blogs.reading.ac.uk/climate-lab-book/files/2018/05/globalcore.png)',
    },
)


##############
# CALLBACKS #
##############

app.clientside_callback(
    ClientsideFunction(namespace="clientside", function_name="resize"),
    Output("output-clientside", "children"),
    [Input("pie_graph", "figure")],
)


### PLATFORM AND PROVIDER ###

# This callback shows or hides the choice of provider
@app.callback(
    Output('provider_div', 'style'),
    [Input('platformType_dropdown', 'value')])
def display_provider(selected_platform):
    # if selected_platform == 'personalComputer':
    if selected_platform in ['cloudComputing','localServer']:
        return {'display': 'block'}
    else:
        return {'display': 'none'}

# This callback updates the choice of providers depending on the platform
@app.callback(
    Output('provider_dropdown', 'options'),
    [Input('platformType_dropdown', 'value')])
def set_providers_options(selected_platform):
    availableOptions = providersNames_df.loc[providersNames_df.platformType == selected_platform]
    return [{'label': k, 'value': v} for k,v in list(zip(availableOptions.providerName, availableOptions.provider))+[("Other","other")]]

### COMPUTING CORES ###

# This callback updates the choice of CPUs/GPUs available
@app.callback(
    Output('coreType_dropdown', 'options'),
    [Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_coreType_options(selected_provider, selected_platform):
    if (selected_provider == 'other')|(selected_platform in ['personalComputer','cloudComputing']):
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
    if (selected_provider == 'other')|(selected_platform in ['personalComputer','cloudComputing']):
        availableOptions = sorted(list(cores_dict[selected_coreType].keys()))
    else:
        availableOptions = sorted(hardware_df.loc[(hardware_df.type == selected_coreType)&(
                hardware_df.provider == selected_provider), 'model'].tolist())
    return [{'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions))+[("Other","other")]]

# This callback shows or hide the TDP input
@app.callback(
    Output('tdp_div', 'style'),
    [Input('coreModel_dropdown', 'value')])
def display_provider(selected_coreModel):
    if selected_coreModel == "other":
        return {'display': 'block'}
    else:
        return {'display': 'none'}

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
        return {'columnCount': 1,'padding': 10,'display': 'none'}

    elif selected_provider in providers_knownPUE:
        return {'columnCount': 1,'padding': 10,'display': 'none'}

    else:
        return {'columnCount': 1,'padding': 10,'display': 'block'}

# And then asks for PUE input if necessary
@app.callback(
    Output('PUEinput_div','style'),
    [Input('pue_radio', 'value')]
)
def display_pue_input(answer_pue):
    if answer_pue == 'No':
        return {'columnCount': 1,'padding': 10,'display': 'none'}
    else:
        return {'columnCount': 1,'padding': 10,'display': 'block'}

### STORE ###
@app.callback(
    Output("aggregate_data", "data"),
    [
        Input("coreType_dropdown", "value"),
        Input("coreModel_dropdown", "value"),
        Input("numberCores_input", "value"),
        Input("tdp_input", "value"),
        Input("memory_input", "value"),
        Input("runTime_input", "value"),
        Input("location_region_dropdown", "value"),
        Input("PUE_input", "value"),
        Input('platformType_dropdown', 'value')
    ],
    [
        State("aggregate_data", "data")
    ]
)
def aggregate_input_values(coreType, coreModel, n_cores, tdp, memory, runTime, location, PUE, selected_platform, existing_state):
    output = dict()

    if (coreType is None)|(coreModel is None)|(n_cores is None)|(tdp is None)|(memory is None)|(runTime is None)|(location is None)|(PUE is None)|(selected_platform is None):
        print('Not enough information to display the results')

        output['coreType'] = None
        output['coreModel'] = None
        output['n_cores'] = None
        output['corePower'] = None
        output['memory'] = None
        output['runTime'] = None
        output['location'] = None
        output['carbonIntensity'] = None
        output['PUE'] = None
        output['selected_platform'] = None
        output['carbonEmissions'] = 0
        output['CE_core'] = 0
        output['CE_memory'] = 0
        output['n_treeYears'] = 0
        output['nkm_flying'] = 0
        output['nkm_drivingUS'] = 0
        output['nkm_drivingEU'] = 0
        output['nkm_train'] = 0

        return output

    else:
        print(location)
        carbonIntensity = CI_df.loc[CI_df.location == location, "carbonIntensity"].values[0]

        if selected_platform == 'personalComputer':
            PUE_used = 1
        else:
            PUE_used = PUE

        if coreModel == 'other':
            corePower = tdp
        else:
            corePower = cores_dict[coreType][coreModel]

        # dividing by 1000 converts to kW.. so this is in g
        carbonEmissions = runTime * PUE_used * (
                n_cores * corePower + memory * refValues_dict['memoryPower']) * carbonIntensity / 1000

        CE_core = runTime * PUE_used * (n_cores * corePower) * carbonIntensity / 1000
        CE_memory = runTime * PUE_used * (memory * refValues_dict['memoryPower']) * carbonIntensity / 1000

        output['coreType'] = coreType
        output['coreModel'] = coreModel
        output['n_cores'] = n_cores
        output['corePower'] = corePower
        output['memory'] = memory
        output['runTime'] = runTime
        output['location'] = location
        output['carbonIntensity'] = carbonIntensity
        output['PUE'] = PUE_used
        output['selected_platform'] = selected_platform
        output['carbonEmissions'] = carbonEmissions
        output['CE_core'] = CE_core
        output['CE_memory'] = CE_memory

        ### CONTEXT

        output['n_treeYears'] = carbonEmissions / refValues_dict['treeYear']

        output['nkm_flying'] = carbonEmissions / refValues_dict['flight_economy_perkm']
        output['nkm_drivingUS'] = carbonEmissions / refValues_dict['passengerCar_US_perkm']
        output['nkm_drivingEU'] = carbonEmissions / refValues_dict['passengerCar_EU_perkm']
        output['nkm_train'] = carbonEmissions / refValues_dict['train_perkm']

        return output

### UPDATE TOP TEXT ###

@app.callback(
    [
        Output("carbonEmissions_text", "children"),
        Output("treeYears_text", "children"),
        Output("driving_text", "children"),
        Output("flying_text", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    text_CE = "{} g CO2".format(round(data['carbonEmissions'], 2))
    text_ty = "{} tree-years".format(round(data['n_treeYears'],2))
    text_car = "{} km".format(round(data['nkm_drivingEU'], 2))
    text_fly = "{} km".format(round(data['nkm_flying'], 2))

    return text_CE, text_ty, text_car, text_fly

### UPDATE PIE GRAPH ###
@app.callback(
    Output("pie_graph", "figure"),
    [Input("aggregate_data", "data")],
)
def create_pie_graph(aggData):
    layout_pie = copy.deepcopy(layout)

    data = [
        dict(
            type='pie',
            labels=['Computing cores','Memory'],
            values=[aggData['CE_core'], aggData['CE_memory']],
            name='Carbon impact breakdown',
            text=[
                'CE due to CPU usage (g CO2)',
                'CE due to memory usage (g CO2)'
            ],
            hoverinfo="text+value+percent",
            textinfo="label+percent+name",
            hole=0.5,
            marker=dict(colors=["#fac1b7", "#a9bb95", "#92d8d8"]),
        )
    ]

    layout_pie["title"] = "Impact breakdown"
    layout_pie["font"] = dict(color="#777777")
    layout_pie["legend"] = dict(
        font=dict(color="#CCCCCC", size="10"), orientation="h", bgcolor="rgba(0,0,0,0)"
    )

    figure = dict(data=data, layout=layout_pie)

    return figure

### UPDATE IMAGES ###

# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory(image_dir, image_name)

if __name__ == '__main__':
    # allows app to update when code is changed!
    app.run_server(debug=True)