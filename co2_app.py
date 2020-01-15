# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import sys
import numpy as np
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
# Carbon Intensity (gCO2eq/kWh) so divide by 1000 to get into KG from eletricity map for state vic
vic_co2_kg=0.611
# taken from electricitymap.org 13th Jan 2020

#############
# LOAD DATA #
#############

### CPU DATA ###

# reading in CPUs and their TDPs taken from https://www.techpowerup.com/cpudb/
# must parse into dictionary form for dcc.dropdown
print("loading CPU data")
cpus = pd.read_csv('cpu_tdp.txt', header=None,sep=" ").set_index(0).squeeze().to_dict()
# print(cpus)

### IMPACT DATA ###

# taken from MLCO2 Github https://github.com/mlco2/impact/blob/master/data/impact.csv 14th Jan
print("loading impact data")
impact = pd.read_csv("impact_mlco2_data.csv")
columns = ["location","impact"]
# padding for combined country and city string
pad1=[" ("]
pad2=[")"]
# adding padding
impact["country"]=impact["country"]+np.asarray(pad1)
# creating unique location ID for one dropdown box
impact["location"] = impact["country"].map(str) + impact["city"]
# adding padding
impact["location"]=impact["location"]+np.asarray(pad2)
# dropping other unnecessary columns
impact=impact[columns]
impact=impact.set_index("location")
impact= impact.squeeze().to_dict()
# print(impact)

# sys.exit(0)

############
# DASH APP #
############

# app begins here
app.layout = html.Div([
    # creating clickable dropdown for CPUs, returns TDP of given CPU (in watt)
    html.Label('Select CPU'),
    dcc.Dropdown(
        options=[{'label': k, 'value': v} for k, v in cpus.items()],
        value=120,clearable=False,id="cpuwattage"
    ),

    # creating clickable dropdown for location, returns impact at that location (in g CO2e / kWh)
    html.Label('Select Location'),
    dcc.Dropdown(
         options=[{'label': k, 'value': v} for k, v in     impact.items()],
         value=300,clearable=False,id="location"
     ),

    # input box for number of CPUs
    html.Label('Number of CPUs'),
    dcc.Input(value=1, type='number',id="numcpu"),

    # box for PUE input
    # default taken from 2018 global average for data centres - Rhonda Ascierto. 2018.
    # Uptime Institute Global Data Center Survey. Technical report, Uptime Institute.
    html.Label('Power Usage Efficiency'),
    dcc.Input(value=1.58,min=1, type='number',id="PUE"),

    # input for running time (in hours)
    html.Label('Runtime (hours)'),
    dcc.Input(value=1, type='number',id="hours"),

    # haven't done memory yet...
    # html.Label('Memory'),
    # dcc.Input(value='1.5', type='text'),

     # will in future draw these %s from the location from electricity mapper
    html.Label('Carbon Offsetting or Renewable (%)'),
      dcc.Input(value=0,min=0,max=100, type='number',id="offset"),
    # html.Label('Carbon Intensity (KgCO2eq/KWh)'),
    #   dcc.Input(value=float(vic_co2_kg),min=0, type='number',id="intense"),
    html.Div(id='output')

#app ends here
    ])#,style={'columnCount': 2,'backgroundColor' :'black'})


##############
# APP OUTPUT #
##############

@app.callback(
    # currently one output
    Output('output', 'children'),
    # all inputs from above
    [Input("numcpu","value"),Input("PUE","value"),Input("hours","value"),Input("offset","value"),Input("cpuwattage","value"),Input("location","value")])


def update_output(numcpus,PUEy,time,offsets,wattage,loc_carbon):
    '''
    this function calculates CO2 equivalent and estimated energy consumed
    :param numcpus: int
    :param PUEy:
    :param time: float, in hours
    :param offsets:
    :param wattage: in Watt
    :param loc_carbon:
    :return:
    '''
    # energy here
    energy=float(time)*float(PUEy)*float(numcpus)*float(wattage)
    energy=energy/1000.0
    print(time)
    print(numcpus)
    print(wattage)
    print(PUEy)
    # convert to kg/kwH
    loc_carbon=loc_carbon*0.001
    # changing by offsets, if 100% offset then should be zero
    co2eq=energy*(100-offsets)*0.01*loc_carbon
    # convert to pounds
    co2eqlbs=co2eq*0.453592
    # final return statement of both outputs
    # flight from NY to San Fran pounds of CO2
    co2_flight_ny_sf=1984#in lbs (from stubell)
    num_flights_equivalent=float(co2eqlbs)/co2_flight_ny_sf
    if num_flights_equivalent<=1:
        # convert to percentage
        num_flights_equivalent=num_flights_equivalent*100
        return 'Energy Consumed is {:10.2f} KWh, \nCO2    equivalent is {:10.2f} KgCO2eq, this is {:10.2f}% of one person flight from NY to SF'.format(energy,co2eq,     num_flights_equivalent)
    else:
        return 'Energy Consumed is {:10.2f} KWh, \nCO2 equivalent is {:10.2f} KgCO2eq, this is {:10.2f} times a one person flight from NY to SF'.format(energy,co2eq,num_flights_equivalent)


if __name__ == '__main__':
    # allows app to update when code is changed!
    app.run_server(debug=True)
