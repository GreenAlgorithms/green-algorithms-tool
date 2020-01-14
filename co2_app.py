# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
#Carbon Intensity (gCO2eq/kWh) so divide by 1000 to get into KG from eletricity map for state vic
vic_co2_kg=0.611
#reading in CPUs and their TDPs taken from https://www.techpowerup.com/cpudb/
cpus=pd.read_csv('cpu_tdp.txt', header=None,sep=" ").set_index(0).squeeze().to_dict()
#print(cpus)
#must parse into dictionary form for dcc.dropdown

#app begins here
app.layout = html.Div([
#creating clickable dropdown for CPUs, returns wattage of given CPU
html.Label('Select CPU'),
dcc.Dropdown(
        options=[{'label': k, 'value': v} for k, v in cpus.items()],
        value=120,clearable=False,id="cpuwattage"
    ),

    #input box for number of CPUs
    html.Label('Number of CPUs'),
    dcc.Input(value=1, type='number',id="numcpu"),

    #box for PUE input
    html.Label('Power Usage Efficiency'),
    dcc.Input(value=1.5,min=1, type='number',id="PUE"),

    #input for time in hours
    html.Label('Time (hours)'),
     dcc.Input(value=1, type='number',id="hours"),
    #haven't done memory yet...

    #html.Label('Memory'),
     #dcc.Input(value='1.5', type='text'),

     #will in future draw these %s from the location from electricity mapper
    html.Label('Carbon Offsetting or Renewable (%)'),
      dcc.Input(value=0,min=0,max=100, type='number',id="offset"),
    html.Label('Carbon Intensity (KgCO2eq/KWh)'),
       dcc.Input(value=float(vic_co2_kg),min=0, type='number',id="intense"),
    html.Div(id='output')

#app ends here
    ])#,style={'columnCount': 2,'backgroundColor' :'black'})


@app.callback(
    #currently one output
    Output('output', 'children'),
    #all inputs from above
    [Input("numcpu","value"),Input("PUE","value"),Input("hours","value"),Input("offset","value"),Input("cpuwattage","value"),Input("intense","value")])
    #this function calculates CO2 equivalent and estimated energy consumed
def update_output(numcpus,PUEy,time,offsets,wattage,carbon):
    #energy here
    energy=float(time)*float(PUEy)*float(numcpus)*float(wattage)
    energy=energy/1000.0
    print(time)
    print(numcpus)
    print(wattage)
    print(PUEy)
    #changing by offsets, if 100% offset then should be zero
    co2eq=energy*(100-offsets)*0.01*carbon
    #final return statement of both outputs
    return 'Energy Consumed is {:10.2f} KWh, \nCO2 equivalent is {:10.2f} KgCO2eq '.format(energy,co2eq)


if __name__ == '__main__':
    #allows app to update when code is changed!
    app.run_server(debug=True)
