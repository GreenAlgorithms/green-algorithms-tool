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

# The styles are automatically loaded from the the /assets folder

app = dash.Dash(
    __name__,
    # these tags are to insure proper responsiveness on mobile devices
    meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)
server = app.server

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

layout_plots = dict(
    autosize=True,
    margin=dict(l=30, r=30, b=20, t=40),
    paper_bgcolor=myColors['boxesColor'],
    plot_bgcolor=myColors['boxesColor'],
    height=400,
)

## make map

map_df = CI_df.loc[CI_df.ISO3 != '', ['ISO3', 'carbonIntensity', 'countryName']]
map_df['text'] = map_df.carbonIntensity.apply(round).astype('str') + " gCO2e/kWh"

layout_map = copy.deepcopy(layout_plots)

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
                text="Carbon <br> intensity <br> (gCO2e/kWh)",
                font=dict(
                    color=myColors['fontColor'],
                )
            ),
            tickfont=dict(
                color=myColors['fontColor'],
            )
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
                # title
                html.Div(
                    [
                        html.H1(
                            "Green Algorithms",
                            id='title',
                        ),
                        html.H4(
                            "How sustainable is your research?",
                            id='subtitle'
                        ),
                    ],
                    # className="one-half column flex-display",
                    className="pretty_container",
                    id="title_container",
                ),
            ],
            id="header",
            className="row flex-display",
        ),

        ## FIRST ROW
        html.Div(
            [
                ## LEFT COLUMN: CALCULATOR INPUT
                html.Div(
                    [
                        html.Div(
                            [
                                html.H3(
                                    "Details about your algorithm"
                                ),

                                dcc.Markdown('''
                                _To understand how each parameter impacts your Carboon Emissions, check out the formula below._
                                '''),
                            ],
                            className='centered-text',
                        ),

                        ## RUN TIME
                        html.Div(
                            [
                                html.H6(
                                    "Runtime (hours and minutes):",
                                    className="control_label flex-half",
                                ),

                                html.Div(
                                    [
                                        dcc.Input(
                                            type='number',
                                            id="runTime_hour_input",
                                            className="dcc_control_row",
                                            value=5,
                                        ),
                                    ],
                                    className='flex-quarter'
                                ),

                                html.Div(
                                    [
                                        dcc.Input(
                                            type='number',
                                            id="runTime_min_input",
                                            value=5,
                                            className="dcc_control_row",
                                        )
                                    ],
                                    className='flex-quarter',

                                ),
                            ],
                            className="control-container-row",
                        ),


                        ## NUMBER OF CORES
                        html.Div(
                            [

                                html.H6(
                                    "Number of cores:",
                                    className="control_label flex-half",
                                ),

                                dcc.Input(
                                    type='number',
                                    id="numberCores_input",
                                    value=1,
                                    className="dcc_control_column flex-half",
                                    # style={"width" : "100%"},
                                ),
                            ],
                            className="control-container-row",
                        ),

                        ## MEMORY
                        html.Div(
                            [
                                html.H6(
                                    "Memory requested (in GB):",
                                    className="control_label flex-half",
                                ),

                                dcc.Input(
                                    type='number',
                                    id="memory_input",
                                    value=64,
                                    className="dcc_control_column flex-half",
                                ),
                            ],
                            className="control-container-row",
                        ),



                        ## SELECT COMPUTING PLATFORM
                        html.Div(
                            [
                                html.H6(
                                    "Select the platform used for the computations:",
                                    className="control_label",
                                ),

                                dcc.Dropdown(
                                    id="platformType_dropdown",
                                    options=platformType_options,
                                    value='localServer',
                                    className="dcc_control_column",
                                ),

                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="provider_dropdown",
                                            className="dcc_control_column",
                                        )
                                    ],
                                    style = {'display': 'none'},
                                    id = 'provider_div'
                                ),
                            ],
                            className="control-container-column",
                        ),

                        ## COMPUTING CORES
                        html.Div(
                            [
                                html.H6(
                                    "What type of core are you using:",
                                    className="control_label",
                                ),

                                dcc.Dropdown(
                                    id="coreType_dropdown",
                                    value = 'CPU',
                                    className="dcc_control_column",
                                ),

                                dcc.Dropdown(
                                    id = "coreModel_dropdown",
                                    className="dcc_control_column",
                                ),

                            ],
                            className="control-container-column",
                        ),

                        html.Div(
                            [
                                html.H6(
                                    'What is the Thermal Design Power (TDP) value per core of your processor? '
                                    'This can easily be found online (usually 10-15W for a CPU, 200W for a GPU)',
                                    className="control_label",
                                ),
                                dcc.Input(
                                    type='number',
                                    id="tdp_input",
                                    className="dcc_control_column",
                                )
                            ],
                            id = "tdp_div",
                            className="control-container-column",
                            style = {'display': 'none'},
                        ),

                        ## LOCATION
                        html.Div(
                            [
                                html.H6(
                                    "Select location:",
                                    className="control_label",
                                ),
                                dcc.Dropdown(
                                    id="location_continent_dropdown",
                                    value='North America',
                                    className="dcc_control_column",
                                ),

                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="location_country_dropdown",
                                            value="United States of America",
                                            className="dcc_control_column",
                                        ),
                                    ],
                                    id='container-country'
                                ),

                                html.Div(
                                    [
                                        dcc.Dropdown(
                                            id="location_region_dropdown",
                                            value = "US",
                                            className="dcc_control_column",
                                        ),
                                    ],
                                    id='container-region'
                                ),

                            ],
                            className="control-container-column",
                        ),


                        ## PUE
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H6(
                                            "Do you know the Power Usage Efficiency (PUE) of your local datacenter?",
                                            className="control_label",
                                        ),

                                        dcc.RadioItems(
                                            id = 'pue_radio',
                                            options=yesNo_options,
                                            value='No',
                                            labelStyle={"display": "inline-block"},
                                            className="dcc_control_column",
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
                                            value=pue_df.loc[pue_df.provider == 'Unknown','PUE'][0],
                                            className="dcc_control_column",
                                        ),
                                    ],
                                    id = 'PUEinput_div',
                                    style = {'display': 'none'},
                                ),
                            ],
                            className="control-container-column",
                        ),
                    ],
                    className="pretty_container four columns",
                    id="input_calculator"
                ),

                ## RIGHT COLUMN
                html.Div(
                    [
                        ## FIRST ROW: DISPLAY RESULTS
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Img(
                                            src=static_image_route + 'logo_co2.png',
                                            id="logo_co2",
                                            className="style-icon"
                                        ),

                                        html.Div(
                                            [
                                                html.H5(
                                                    id="carbonEmissions_text",
                                                ),

                                                html.H6(
                                                    "Carbon emissions",
                                                )
                                            ],
                                            className='container-labels-icon'
                                        ),

                                    ],
                                    id="carbonEmissions",
                                    className="mini_container",
                                ),

                                html.Div(
                                    [
                                        html.Img(
                                            src=static_image_route + 'logo_tree_1.png',
                                            id="logo_tree",
                                            className="style-icon"
                                        ),

                                        html.Div(
                                            [
                                                html.H5(
                                                    id="treeMonths_text",
                                                ),

                                                html.H6(
                                                    "Carbon sequestration",
                                                )
                                            ],
                                            className='container-labels-icon'
                                        ),

                                    ],
                                    id="treeMonths",
                                    className="mini_container",
                                ),

                                html.Div(
                                    [
                                        html.Img(
                                            src=static_image_route + 'logo_car.png',
                                            id="logo_car",
                                            className="style-icon"
                                        ),

                                        html.Div(
                                            [
                                                html.H5(
                                                    id="driving_text",
                                                ),

                                                html.H6(
                                                    "in a passenger car",
                                                )
                                            ],
                                            className='container-labels-icon'
                                        ),

                                    ],
                                    id="car",
                                    className="mini_container",
                                ),

                                html.Div(
                                    [
                                        html.Img(
                                            src=static_image_route + 'logo_plane.png',
                                            id="logo_plane",
                                            className="style-icon"
                                        ),

                                        html.Div(
                                            [
                                                html.H5(
                                                    id="flying_text",
                                                ),

                                                html.H6(
                                                    "of a flight NY -> SF",
                                                )
                                            ],
                                            className='container-labels-icon'
                                        ),

                                    ],
                                    id="plane",
                                    className="mini_container",
                                ),
                            ],
                            id="info_container",
                            className="row flex-display",
                        ),

                        ## SECOND ROW: GRAPH
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4(
                                            "Breakdown of the emissions"
                                        ),

                                        dcc.Graph(
                                            id="pie_graph",
                                        )
                                    ],
                                    className='flex-display by-column one-half column',
                                ),

                                html.Div(
                                    [
                                        html.H4(
                                            "How the location impacts your footprint"
                                        ),

                                        dcc.Graph(
                                            id = "barPlotComparison"
                                        )
                                    ],
                                    className='flex-display by-column one-half column flex-auto',

                                ),

                            ],
                            id="pieGraphContainer",
                            className="pretty_container row",
                        ),

                    ],
                    id="firstRow_rightColumn",
                    className="eight columns flex-display by-column bare_container flex-auto",
                ),

            ],
            # id='row_inputOutput',
            className="row flex-display",
        ),

        ## SECOND ROW
        html.Div(
            [
                html.Div(
                    [
                        html.H4("Carbon Intensity across the world"),
                        dcc.Graph(
                            id = "map",
                            figure = mapCI
                        )
                    ],
                    className="pretty_container seven columns by-column",
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "About CO2e"
                                ),

                                dcc.Markdown('''
                                It's a metric used to measure the Global Warming Potential of a mixture of greenhouse gases.
                                It represents the quantity of CO2 that would have the same impact of the environment.
                                ''')
                            ],
                            className="pretty_container by-column flex-auto"
                        ),

                        html.Div(
                            [
                                html.H4(
                                    "What is a tree-month?"
                                ),

                                dcc.Markdown('''
                                It's the amount of CO2 sequestred by a tree in a month.
                                It's a unit measuring how long it would take for a mature tree
                                to absorb the CO2e emitted by your algorithm.
                                
                                As an estimate here, we use 11.4 kg CO2e/year, which is roughly __1kg CO2e/month__.
                                '''),
                            ],
                            className="pretty_container by-column flex-auto"
                        ),
                    ],
                    className="flex-display five columns by-column",
                )
            ],
            # id='secondRow',
            className="row flex-display",
        ),

        ## THIRD ROW
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.H4(
                                    "What can you do about it?"
                                ),

                                dcc.Markdown('''
                                The main factor impacting your Carbon Emissions is the location of your servers:
                                the same algorithm will emit __64 times more__ CO2e
                                if ran in Australia compared to Switzerland.

                                Only requesting the necessary memory can also improve greatly your carbon footprint.

                                Generally, writing sensible code that runs faster with fewer resources saves both money
                                and the planet.
                                ''')
                            ],
                            className="pretty_container by-column"
                        ),

                        html.Div(
                            [
                                html.H4(
                                    "How to report it?"
                                ),

                                dcc.Markdown(id='report_markdown')
                            ],
                            className="pretty_container by-column"
                        ),
                    ],
                    className='flex-display six columns by-column'

                ),

                html.Div(
                    [
                        html.H4(
                            "The formula"
                        ),

                        dcc.Markdown('''
                        The carbon emission is calculated by estimating the energy draw of the algorithm
                        and the carbon intensity of producing such energy at a given location:

                        `carbon emissions = energy needed * carbon intensity`

                        The energy needed is:

                        `energy needed = time * (power draw for computing cores + power draw for memory) * PUE`

                        * the power draw for the computing cores depends on the CPU model and number of cores
                        * the memory power draw depends on the size of memory requested.
                        * the PUE (Power Usage Effectiveness) measures how much extra energy is needed for the data centre's cooling and lighting etc.

                        The Carbon Intensity depends on the location and the technologies used to produce electricity.
                        ''')
                    ],
                    className="pretty_container six columns by-column"
                )
            ],
            className="row flex-display",
        ),

        ## FOURTH ROW
        html.Div(
            [

                html.Div(
                    [
                        html.H4(
                            "Who are we?"
                        ),

                        dcc.Markdown('''
                        The Green algorithms initiative was created by 
                        \[1\] Loic Lannelongue, \[2\] Jason Grealey, and \[3\] Michael Inouye
                        
                        \[1\] University of Cambridge
                        
                        \[2\] Baker Heart and Diabetes Institute and La Trobe University
                        Baker Institute, University of Cambridge, Alan Turing Institute, Health Data Research UK
                        
                        Information about our lab is available [here]('https://sysgenresearch.org')
                         ''')
                    ],
                    className="pretty_container four columns by-column"
                ),

                html.Div(
                    [
                        html.H4(
                            "The data"
                        ),

                        dcc.Markdown('''
                        The data used to run this calculator can be found on github: 
                         ''')
                    ],
                    className="pretty_container four columns by-column"
                ),

                html.Div(
                    [
                        html.H4(
                            "#ShowYourStripes"
                        ),

                        dcc.Markdown('''
                        These coloured stripes in the background represent the change in world temperatures
                        from 1850 to 2018.
                        This striking design has been made by Ed Hawkins from the University of Reading.

                        More on [ShowYourStipes.info]('https://showyourstripes.info')
                        ''')
                    ],
                    className="pretty_container four columns by-column"
                ),
            ],
            className="row flex-display",
        ),
    ],
    id="mainContainer",
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
        return {'display': 'block'}
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
        Output('container-country', 'style'),
        Output('container-region', 'style'),
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
        Input("runTime_hour_input", "value"),
        Input("runTime_min_input", "value"),
        Input("location_region_dropdown", "value"),
        Input("PUE_input", "value"),
        Input('platformType_dropdown', 'value'),
        Input('provider_dropdown', 'value')
    ],
    [
        State("aggregate_data", "data")
    ]
)
def aggregate_input_values(coreType, coreModel, n_cores, tdp, memory, runTime_hours, runTime_min, location, PUE, selected_platform, selected_provider, existing_state):
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

    if (coreType is None)|(coreModel is None)|(n_cores is None)|(tdp is None)|(memory is None)|(test_runTime == 2)|(location is None)|(PUE is None)|(selected_platform is None):
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
        output['power_needed'] = 0

        return output

    else:
        # print(location)
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

        # dividing by 1000 converts to kW
        powerNeeded = runTime * PUE_used * (
                n_cores * corePower + memory * refValues_dict['memoryPower']) / 1000
        # carbonIntensity is in g per kWh, so results in gCO2
        carbonEmissions = powerNeeded * carbonIntensity

        CE_core = runTime * PUE_used * (n_cores * corePower) * carbonIntensity / 1000
        CE_memory = runTime * PUE_used * (memory * refValues_dict['memoryPower']) * carbonIntensity / 1000

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
        output['power_needed'] = powerNeeded

        ### CONTEXT

        output['n_treeMonths'] = carbonEmissions / refValues_dict['treeYear'] * 12

        # output['nkm_flying'] = carbonEmissions / refValues_dict['flight_economy_perkm']
        output['flying_context'] =  carbonEmissions / refValues_dict['flight_NY-SF']
        output['nkm_drivingUS'] = carbonEmissions / refValues_dict['passengerCar_US_perkm']
        output['nkm_drivingEU'] = carbonEmissions / refValues_dict['passengerCar_EU_perkm']
        output['nkm_train'] = carbonEmissions / refValues_dict['train_perkm']

        return output

### UPDATE TOP TEXT ###

@app.callback(
    [
        Output("carbonEmissions_text", "children"),
        Output("treeMonths_text", "children"),
        Output("driving_text", "children"),
        Output("flying_text", "children"),
    ],
    [Input("aggregate_data", "data")],
)
def update_text(data):
    text_CE = "{} g CO2e".format(round(data['carbonEmissions'], 2))
    text_ty = "{} tree-months".format(round(data['n_treeMonths'],2))
    text_car = "{} km".format(round(data['nkm_drivingEU'], 2))
    text_fly = "{} %".format(round(data['flying_context']*100, 0))

    return text_CE, text_ty, text_car, text_fly

### UPDATE PIE GRAPH ###
@app.callback(
    Output("pie_graph", "figure"),
    [Input("aggregate_data", "data")],
)
def create_pie_graph(aggData):
    layout_pie = copy.deepcopy(layout_plots)

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
                    color=myColors['fontColor'],
                ),
                hovertemplate='%{value:.0f} gCO2e<extra></extra>',
                hoverlabel=dict(
                    font=dict(
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
            text='Emissions (gCO2e)'
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
        loc_ref[countryCode]['carbonEmissions'] = aggData['power_needed'] * CI_df.loc[CI_df.location == countryCode, "carbonIntensity"].values[0]
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


### UPDATE THE REPORT TEXT ###

@app.callback(
    Output('report_markdown', 'children'),
    [Input("aggregate_data", "data")],
)
def fillin_report_text(aggData):

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
    Why not reporting the environmental footprint of your computations alongside other performance metrics?

    Here is an example:

    > This algorithm runs in {}h and {}min on {} {}{} {}.
    > Based in {}{}{}, this produces {:.0f}g of CO2e, which is equivalent to {:.2f} tree-months.
    '''.format(
        aggData['runTime_hours'], aggData['runTime_min'],
        aggData['n_cores'], aggData['coreType'], suffixProcessor, aggData['coreModel'],
        prefixCountry, country, textRegion,
        aggData['carbonEmissions'], aggData['n_treeMonths']
    )

    return myText



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
