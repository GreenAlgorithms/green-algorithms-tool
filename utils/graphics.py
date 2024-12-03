import os 
import copy

import pandas as pd
import pycountry_convert as pc
import plotly.graph_objects as go

from utils.handle_inputs import DATA_DIR


###################################################
## GLOBAL SETTINGS 

MY_COLORS = {
    'fontColor':'rgb(60, 60, 60)',
    'boxesColor': "#F9F9F9",
    'backgroundColor': '#f2f2f2',
    'pieChart': ['#E8A09A','#9BBFE0','#cfabd3'],
    'plotGrid':'#e6e6e6',
    'map1':['#78E7A2','#86D987','#93CB70','#9EBC5C',
           '#A6AD4D','#AB9E43','#AF8F3E','#AF803C','#AC713D','#A76440','#9E5943']
}

FONT_GRAPHS = "Raleway"

PLOTS_LAYOUT = dict(
    autosize=True,
    margin=dict(l=0, r=0, b=0, t=50),
    paper_bgcolor=MY_COLORS['boxesColor'],
    plot_bgcolor=MY_COLORS['boxesColor'],
    font = dict(family=FONT_GRAPHS, color=MY_COLORS['fontColor']),
    separators=".,",
)

BLANK_FIGURE = {
    "layout": {
        "xaxis": {
            "visible": False
        },
        "yaxis": {
            "visible": False
        },
        "plot_bgcolor": "#f9f9f9",
        "paper_bgcolor": "#f9f9f9",
        "annotations": [
            {
                "text": "",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {
                    "size": 28
                }
            }
        ]
    }
}

###################################################
## UTILS

def iso2_to_iso3(x):
    try:
        output = pc.country_name_to_country_alpha3(pc.country_alpha2_to_country_name(x, cn_name_format="default"),
                                                   cn_name_format="default")
    except:
        output = ''
    return output

def colours_hex2rgba(hex):
    h = hex.lstrip('#')
    return('rgba({},{},{})'.format(*tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))))

def convertList_hex2rgba(hex_list):
    out = []
    for hex in hex_list:
        out.append(colours_hex2rgba(hex))
    return out


###################################################
## CARBON INTENSITIES MAP

def get_map_layout():
    layout_map = copy.deepcopy(PLOTS_LAYOUT)
    layout_map['height'] = 250
    layout_map['margin']['t'] = 30
    layout_map['geo'] = dict(
        projection=dict(
            type='natural earth',
        ),
        showcoastlines=False,
        showocean=True,
        oceancolor=MY_COLORS['boxesColor'],
        showcountries=True,
        countrycolor=MY_COLORS['boxesColor'],
        showframe=False,
        bgcolor=MY_COLORS['boxesColor'],
    )
    return layout_map

def create_CI_map_graphic():
    '''
    Generates a map showing carbon intensities over the world.
    The map is not updated when changing versions, but it's probably not an isssue
    '''
    # Loading carbon intensity data
    CI_4map = pd.read_csv(os.path.join(DATA_DIR, 'latest', "CI_aggregated.csv"), sep=',', skiprows=1)
    CI_4map['ISO3'] = CI_4map.location.apply(iso2_to_iso3)

    map_df = CI_4map.loc[CI_4map.ISO3 != '', ['ISO3', 'carbonIntensity', 'countryName']]
    map_df['text'] = map_df.carbonIntensity.apply(round).astype('str') + " gCO2e/kWh"

    # Building the map
    mapCI = go.Figure(
        data=go.Choropleth(
            geojson=os.path.join(DATA_DIR, 'world.geo.json'),
            locations = map_df.ISO3,
            locationmode='geojson-id',
            z=map_df.carbonIntensity.astype(float),
            colorscale=MY_COLORS['map1'],
            colorbar=dict(
                title=dict(
                    # text="Carbon <br> intensity <br> (gCO2e/kWh)",
                    font=dict(
                        color=MY_COLORS['fontColor'],
                    )
                ),
                tickfont=dict(
                    color=MY_COLORS['fontColor'],
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
                    color=MY_COLORS['boxesColor'],
                    width=0.5
                )
            ),
        ),
        layout=get_map_layout()
    )
    return mapCI


###################################################
## CORES BAR CHART 

def get_cores_bar_layout():
    layout_bar = copy.deepcopy(PLOTS_LAYOUT)
    layout_bar['margin']['t'] = 60
    layout_bar['xaxis'] = dict(
        color=MY_COLORS['fontColor'],
    )
    layout_bar['yaxis'] = dict(
        color=MY_COLORS['fontColor'],
        showspikes=False,
        showgrid=True,
        gridcolor=MY_COLORS['plotGrid'],
    )
    return layout_bar

def create_cores_bar_chart_graphic(aggregated_data, data_dict):
    
    layout_bar = get_cores_bar_layout()

    if aggregated_data['coreType'] in ['GPU','Both']:
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

        coreModel = aggregated_data['GPUmodel']

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

        coreModel = aggregated_data['CPUmodel']

    if coreModel not in list_cores:
        list_cores.append(coreModel)

    power_list = []

    # calculate carbon emissions for each core
    if aggregated_data['coreType'] in ['GPU','Both']:
        for gpu in list_cores:
            if gpu == 'other':
                power_list.append(aggregated_data['tdpGPU'])
            else:
                power_list.append(data_dict.cores_dict['GPU'][gpu])
    else:
        for cpu in list_cores:
            if cpu == 'other':
                power_list.append(aggregated_data['tdpCPU'])
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
                        color=MY_COLORS['fontColor'],
                    )
                ),
                hovertemplate='%{y:.1f} W<extra></extra>',
                hoverlabel=dict(
                    font=dict(
                        color=MY_COLORS['fontColor'],
                    )
                ),

            )
        ],
        layout = layout_bar
    )

    return fig


###################################################
## CARBON INTENSITIES BAR CHART

def get_ci_bar_chart_layout():
    layout_bar = copy.deepcopy(PLOTS_LAYOUT)
    layout_bar['xaxis'] = dict(
        color=MY_COLORS['fontColor'],
    )
    layout_bar['yaxis'] = dict(
        color=MY_COLORS['fontColor'],
        title=dict(
            text='Emissions (gCO2e)',
            standoff=100,
        ),
        showspikes=False,
        showgrid=True,
        gridcolor=MY_COLORS['plotGrid'],
    )
    return layout_bar

def create_ci_bar_chart_graphic(aggregated_data, data_dict):

    # list of countries displayed
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
        loc_ref[countryCode]['carbonEmissions'] = aggregated_data['energy_needed'] * data_dict.CI_dict_byLoc[countryCode]['carbonIntensity']
        loc_ref[countryCode]['opacity'] = 0.2

    # adapt the final dataframe
    loc_ref['You'] = dict(
        name='Your algorithm',
        carbonEmissions=aggregated_data['carbonEmissions'],
        opacity=1
    )
    loc_df = pd.DataFrame.from_dict(loc_ref, orient='index')
    loc_df.sort_values(by=['carbonEmissions'], inplace=True)
    lines_thickness = [0] * len(loc_df)
    lines_thickness[loc_df.index.get_loc('You')] = 4

    # create the end figure
    fig = go.Figure(
        data = [
            go.Bar(
                x=loc_df.name.values,
                y=loc_df.carbonEmissions.values,
                marker = dict(
                    color=loc_df.carbonEmissions.values,
                    colorscale=MY_COLORS['map1'],
                    line=dict(
                        width=lines_thickness,
                        color=MY_COLORS['fontColor'],
                    )
                ),
                hovertemplate='%{y:.0f} gCO2e<extra></extra>',
                hoverlabel=dict(
                    font=dict(
                        color=MY_COLORS['fontColor'],
                    )
                ),
            )
        ],
        layout = get_ci_bar_chart_layout()
    )

    return fig



###################################################
## CORES AND MEMORY CONSUMPTION PIE GRAH

def get_cores_memory_pie_chart_layout(aggregated_data):
    layout_pie = copy.deepcopy(PLOTS_LAYOUT)
    layout_pie['margin'] = dict(l=0, r=0, b=0, t=60)
    if aggregated_data['coreType'] == 'Both':
        layout_pie['height'] = 400
    else:
        layout_pie['height'] = 350
        layout_pie['margin']['t'] = 40
    return layout_pie


def create_cores_memory_pie_graphic(aggregated_data):
    labels = ['Memory']
    values = [aggregated_data['CE_memory']]

    if aggregated_data['coreType'] in ['CPU', 'Both']:
        labels.append('CPU')
        values.append(aggregated_data['CE_CPU'])

    if aggregated_data['coreType'] in ['GPU', 'Both']:
        labels.append('GPU')
        values.append(aggregated_data['CE_GPU'])
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
                    colors=MY_COLORS['pieChart']
                ),
                texttemplate="<b>%{label}</b><br>%{percent}",
                textfont=dict(
                    family=FONT_GRAPHS,
                    color=MY_COLORS['fontColor'],
                ),
                hovertemplate='%{value:.0f} gCO2e<extra></extra>',
                hoverlabel=dict(
                    font=dict(
                        family=FONT_GRAPHS,
                        color=MY_COLORS['fontColor'],
                    )
                )
            )
        ],
        layout=get_cores_memory_pie_chart_layout(aggregated_data)
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