# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import pandas as pd
import sys
import numpy as np
import os

#########
# STYLE #
#########

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


#############
# LOAD DATA #
#############

data_dir = os.path.join(os.path.abspath(''),'data')

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

### IMPACT BY LOCATION ###
impact_df = pd.read_csv(os.path.join(data_dir, "impact_by_location.csv"),
                        sep=',', skiprows=1)
impact_df.drop(['source'], axis=1, inplace=True)
impact_dict = pd.Series(impact_df.impact.values,index=impact_df.location).to_dict()

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


############
# DASH APP #
############

colors = {
    'background': '#f2efe4',
    'text': '#4c3327'
}

allPlatforms_names = dict({
    'Cloud computing':'cloudComputing',
    'Local server':'localServer',
    'Local desktop':'localDesktop'
})

app.layout = html.Div(
    style = {'backgroundColor':colors['background'],'padding': 100},
    children = [

        ### TITLE ###

        html.H1('CO2 calculator for (bio)informatic tools',
                style = {
                    'textAlign':'center',
                    'color': colors['text'],
                    'padding': 10
                }),

        ### SELECT COMPUTING PLATFORM ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children=[
                html.Label('On what platform are you running your tool:'),

                dcc.Dropdown(
                    options=[{'label': k, 'value': v} for k,v in list(providersNames_df.loc[:,['platformName',
                                                                                               'platformType']].drop_duplicates().apply(tuple, axis=1)) +
                             [('Personal computer', 'personalComputer')]],
                    id="platformType_dropdown", value='cloudComputing'),

                html.Div(children = dcc.Dropdown(id="provider_dropdown", value='gcp'),
                         style = {'display': 'none'},
                         id = 'provider_div')
            ]
        ),

        ### COMPUTING CORES ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('What type of computing core are you using?'),

                dcc.Dropdown(id="coreType_dropdown", value = 'CPU'),

                dcc.Dropdown(id = "coreModel_dropdown")]),

        ### NUMBER OF CORES ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('Number of Cores'),
                dcc.Input(type='number',
                          id="numberCores_input",
                          value=1)]),

        ### RUN TIME ###

        html.Div(
            style={'columnCount': 1, 'padding': 10},
            children=[
                html.Label('Runtime (hours)'),
                dcc.Input(type='number',
                          id="runTime_input",
                          value=5),
            ]),

        ### LOCATION ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('Select Location'),
                dcc.Dropdown(id="location_continent_dropdown",value='North America'),

                dcc.Dropdown(id="location_country_dropdown", value="USA"),

                dcc.Dropdown(id="location_city_dropdown")]),

        ### PUE ###

        html.Div(
            style = {'columnCount': 1,'padding': 10,'display': 'none'},
            children = [
                html.Label('Do you know the Power Usage Efficiency (PUE) of your local datacenter?'),
                dcc.RadioItems(
                    options=[
                        {'label': 'Yes', 'value': 'Yes'},
                        {'label': 'No', 'value': 'No'}
                    ],
                    id = 'pue_radio',
                    value='No')
            ],
            id = 'PUEquestion_div'
        ),

        html.Div(
            style = {'columnCount': 1,'padding': 10,'display': 'none'},
            children = [
                dcc.Input(min=1,
                          type='number',
                          id="PUE_input",
                          value=pue_df.loc[pue_df.provider == 'Unknown','PUE'][0])
            ],
            id = 'PUEinput_div'
        ),

        ### BUTTON ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [html.Button('Compute', id='button')]
        ),


        ### OUTPUT ###

        # html.Div(id='output')
        dcc.Markdown(id='output',style={'padding': 10})
    ])


##############
# APP OUTPUT #
##############

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

@app.callback(
    Output('provider_dropdown', 'options'),
    [Input('platformType_dropdown', 'value')])
def set_providers_options(selected_platform):
    availableOptions = providersNames_df.loc[providersNames_df.platformType == selected_platform]
    return [{'label': k, 'value': v} for k,v in list(zip(availableOptions.providerName, availableOptions.provider))+[("Other","other")]]

### COMPUTING CORES ###

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
    return [{'label': k, 'value': k} for k in availableOptions]

### LOCATION ###

# This callback adjusts the list of continents to choose from depending on the provider
@app.callback(
    Output('location_continent_dropdown','options'),
    [Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_continents_options(selected_provider,selected_platform):
    if (selected_provider == 'other')|(selected_platform == 'personalComputer'):
        availableOptions = list(set(impact_df.loc[:,
                                                  'continentName']))
    else:
        availableOptions = list(set(impact_df.loc[impact_df.location.isin(datacenters_dict[selected_provider]),
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
        availableOptions = list(set(impact_df.loc[(impact_df.continentName == selected_continent), 'countryName']))
    else:
        availableOptions = list(set(impact_df.loc[(impact_df.location.isin(datacenters_dict[selected_provider])) & (
            impact_df.continentName == selected_continent), 'countryName']))
    return [{'label': k, 'value': k} for k in sorted(availableOptions)]

# and this one adjusts the list of cities depending on the country & the provider
@app.callback(
    Output('location_city_dropdown', 'options'),
    [Input('location_continent_dropdown', 'value'),
     Input('location_country_dropdown', 'value'),
     Input('provider_dropdown', 'value'),
     Input('platformType_dropdown', 'value')])
def set_cities_options(selected_continent, selected_country,selected_provider,selected_platform):
    if (selected_provider == 'other')|(selected_platform == 'personalComputer'):
        availableOptions = impact_df.loc[(impact_df.continentName == selected_continent) & (
                impact_df.countryName == selected_country)]
    else:
        availableOptions = impact_df.loc[(impact_df.location.isin(datacenters_dict[selected_provider])) & (
                impact_df.continentName == selected_continent) & (
                impact_df.countryName == selected_country)]
    availableOptions = availableOptions.sort_values(by=['cityName'])
    return [{'label': k, 'value': v} for k,v in zip(availableOptions.cityName, availableOptions.location)]

### PUE ###

# This callback shows or hides the PUE question depending on the different answers
@app.callback(
    Output('PUEquestion_div','style'),
    [Input('location_city_dropdown','value'),
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


### OUTPUT ###

# This callback updates the output
@app.callback(
    Output(component_id='output', component_property='children'),
    [Input(component_id='button', component_property='n_clicks')],
    [State(component_id="coreType_dropdown", component_property="value"),
     State(component_id="coreModel_dropdown", component_property="value"),
     State(component_id="numberCores_input", component_property="value"),
     State(component_id="runTime_input", component_property="value"),
     State(component_id="location_city_dropdown", component_property="value"),
     State(component_id="PUE_input", component_property="value"),
     State('platformType_dropdown', 'value')
     ])
def update_output(n_clicks, coreType, coreModel, n_cores, runTime, location, PUE, selected_platform):
    if n_clicks is None:
        # We only display the output when the button is clicked
        raise PreventUpdate

    else:
        corePower = cores_dict[coreType][coreModel]
        impactValue = impact_df.loc[impact_df.location == location, "impact"].values[0]

        if selected_platform == 'personalComputer':
            PUE_used = 1
        else:
            PUE_used = PUE

        # dividing by 1000 converts to kW.. so this is in g
        energy_consumption = runTime * PUE_used * n_cores * corePower * impactValue / 1000
        # convert to kg then to pounds
        energy_consumption_lbs=energy_consumption*0.453592/1000

        ### CONTEXT ###

        # convert to % of flight
        co2_flight_ny_sf=1984# in lbsCO2eq (from stubell)
        car_co2=404# grams of CO2 per mile from EPA US https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
        # if job is too small to compare with flight then look at car mileage (can change this)
        if energy_consumption_lbs > co2_flight_ny_sf*0.10:
            #percentage of flight
            context=round(float(energy_consumption_lbs)/co2_flight_ny_sf,2)
            if context<1:
                #use percentage
                context=context*100
                context_str="This is {}% of a one passenger flight from New York to San Franciso".format(context)
            else:
                #use multiples
                context_str="This is {} times larger than a one passenger flight from New York to San Franciso".format(context)
        #look at smaller co2 context such as car mileage
        else:
            # g of job co2 / g average car co2 -> driving average car for this many km (note 1.60934 km per mile)
            context=round(energy_consumption*1.60934/(car_co2),2)
            context_str="This is the same as driving an average car for {} km".format(context)

        #formatting
        energy_consumption=round(energy_consumption,2)

        #outputting
        output = f'''
        Summary of the parameters:
        - {n_cores} {coreModel}: {corePower} W
        - run time: {runTime} hours
        - {location}: {impactValue} g CO2e / kWh
        - PUE: {PUE_used}

        **Your carbon footprint is {energy_consumption} g CO2e**

        **{context_str}**
        '''
        return output

if __name__ == '__main__':
    # allows app to update when code is changed!
    app.run_server(debug=True)
