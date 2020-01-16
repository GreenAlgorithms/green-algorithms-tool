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
cpu_dict = pd.Series(cpu_df.TDP.values,index=cpu_df.model).to_dict()

### GPU ###
gpu_df = pd.read_csv(os.path.join(data_dir, "TDP_gpu.csv"),
                     sep=',', skiprows=1)
gpu_df.drop(['source'], axis=1, inplace=True)
gpu_dict = pd.Series(gpu_df.TDP.values,index=gpu_df.model).to_dict()

### PUE ###
pue_df = pd.read_csv(os.path.join(data_dir, "servers_PUE.csv"),
                     sep=',', skiprows=1)
pue_df.drop(['source'], axis=1, inplace=True)

### HARDWARE ###
hardware_df = pd.read_csv(os.path.join(data_dir, "servers_hardware.csv"),
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
                                  sep=',')


############
# DASH APP #
############

colors = {
    'background': '#f2efe4',
    'text': '#4c3327'
}

# Dict of dict of dict ... with all the possible locations.
# e.g. {'Europe': {'Belgium': {'St. Ghislain': 'BEL-StGhislain'} ...
allLocations = dict()
for continent in set(impact_df.continentName):
    allLocations[continent] = dict()

    list_countries = list(set(impact_df.loc[impact_df.continentName == continent, 'countryName']))
    for country in list_countries:
        subDf = impact_df.loc[(impact_df.continentName == continent)&(impact_df.countryName == country)]
        allLocations[continent][country] = pd.Series(subDf.location.values,index=subDf.cityName).to_dict()
        # allLocations[continent][country] = list(set(impact_df.loc[(impact_df.continentName == continent)&(impact_df.countryName == country), 'cityName']))

# Dict of dict with all the possible models
# e.g. {'CPU': {'Intel(R) Xeon(R) Gold 6142': 150, 'Core i7-10700K': 125, ...
allCores = dict()
allCores['CPU'] = pd.Series(cpu_df.TDP.values,index=cpu_df.model).to_dict()
allCores['GPU'] = pd.Series(gpu_df.TDP.values,index=gpu_df.model).to_dict()

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

        ### RUN TIME ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('Runtime (hours)'),
                dcc.Input(type='number',
                          id="runTime_input",
                          value=5),
            ]),

        ### COMPUTING CORES ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('What type of computing core are you using?'),
                dcc.Dropdown(
                    options=[{'label': k, 'value': k} for k in allCores.keys()],
                    id="coreType_dropdown", value='CPU'),
                dcc.Dropdown(id = "coreModel_dropdown")]),

        ### NUMBER OF CORES ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('Number of Cores'),
                dcc.Input(type='number',
                          id="numberCores_input",
                          value=1)]),

        ### LOCATION ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('Select Location'),
                dcc.Dropdown(
                    options=[{'label': k, 'value': k} for k in allLocations.keys()],
                    id="location_continent_dropdown",value='North America'),

                dcc.Dropdown(id="location_country_dropdown", value="USA"),

                dcc.Dropdown(id="location_city_dropdown")]),

        ### PUE ###

        html.Div(
            style = {'columnCount': 1,'padding': 10},
            children = [
                html.Label('Power Usage Efficiency'),
                dcc.Input(min=1,
                          type='number',
                          id="PUE_input",
                          value=1.58)]),

        ### BUTTON ###

        html.Button('Compute', id='button'),

        ### OUTPUT ###

        # html.Div(id='output')
        dcc.Markdown(id='output',style={'padding': 10})
    ])


##############
# APP OUTPUT #
##############

# This callback adjusts the list of computing cores to choose from (CPU or GPU)
@app.callback(
    Output('coreModel_dropdown', 'options'),
    [Input('coreType_dropdown', 'value')])
def set_coreModels_options(selected_coreType):
    return [{'label': k, 'value': k} for k in allCores[selected_coreType].keys()]

# This callback adjusts the list of countries to choose from depending on the continent
@app.callback(
    Output('location_country_dropdown', 'options'),
    [Input('location_continent_dropdown', 'value')])
def set_countries_options(selected_continent):
    return [{'label': i, 'value': i} for i in allLocations[selected_continent].keys()]

# and this ones adjusts the list of cities depending on the country
@app.callback(
    Output('location_city_dropdown', 'options'),
    [Input('location_continent_dropdown', 'value'),
    Input('location_country_dropdown', 'value')])
def set_cities_options(selected_continent, selected_country):
    return [{'label': k, 'value': v} for k,v in allLocations[selected_continent][selected_country].items()]

# This callback updates the output
@app.callback(
    Output(component_id='output', component_property='children'),
    [Input(component_id='button', component_property='n_clicks')],
    [State(component_id="coreType_dropdown", component_property="value"),
     State(component_id="coreModel_dropdown", component_property="value"),
     State(component_id="numberCores_input", component_property="value"),
     State(component_id="runTime_input", component_property="value"),
     State(component_id="location_city_dropdown", component_property="value"),
     State(component_id="PUE_input", component_property="value")
     ])
def update_output(n_clicks, coreType, coreModel, n_cores, runTime, location, PUE):
    if n_clicks is None:
        # We only display the output when the button is clicked
        raise PreventUpdate

    else:
        corePower = allCores[coreType][coreModel]
        impactValue = impact_df.loc[impact_df.location == location, "impact"].values[0]

        output = "{}: {} \n".format(coreModel, corePower)
        output += "n_cores: {} \n".format(n_cores)
        output += "runTime: {} \n".format(runTime)
        output += "{}: {} \n".format(location, impactValue)
        output += "PUE: {} \n".format(PUE)
        #dividing by 1000 converts to kW.. so this is in g
        energy_consumption = runTime * PUE * n_cores * corePower * impactValue / 1000
        #convert to kg then to pounds
        energy_consumption_lbs=energy_consumption*0.453592/1000

        ### CONTEXT ###

        #convert to % of flight
        co2_flight_ny_sf=1984# in lbsCO2eq (from stubell)
        car_co2=404# grams of CO2 per mile from EPA US https://www.epa.gov/greenvehicles/greenhouse-gas-emissions-typical-passenger-vehicle
        #if job is too small to compare with flight then look at car mileage (can change this)
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
        output += "/// Energy Consumption: {:.2f}g CO2e".format(energy_consumption)

        output2 = f'''
        Summary of the parameters:
        - {n_cores} {coreModel}: {corePower} W
        - run time: {runTime} hours
        - {location}: {impactValue} g CO2e / kWh
        - PUE: {PUE}

        **Your carbon footprint is {energy_consumption} g CO2e**

        **{context_str}**
        '''
        return output2

if __name__ == '__main__':
    # allows app to update when code is changed!
    app.run_server(debug=True)
