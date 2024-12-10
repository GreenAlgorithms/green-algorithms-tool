# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import os
import dash
import datetime

from dash import html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from types import SimpleNamespace
from flask import send_file # Integrating Loader IO

import pandas as pd
import plotly.graph_objects as go

from utils.utils import put_value_first, is_shown
from utils.graphics import create_cores_bar_chart_graphic, create_ci_bar_chart_graphic, create_cores_memory_pie_graphic, MY_COLORS
from utils.handle_inputs import load_data, CURRENT_VERSION, DATA_DIR
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region
from utils.handle_inputs import validateInput, open_input_csv_and_comment, read_csv_input, DEFAULT_VALUES, APP_VERSION_OPTIONS_LIST

from all_in_one_components.form.green_algo_form_AIO import ID_MAIN_FORM
from all_in_one_components.form.green_algo_form_AIO_ids import GreenAlgoFormIDS

form_ids = GreenAlgoFormIDS()

###################################################
## LOAD DATA

image_dir = os.path.join('assets/images')
static_image_route = '/static/'
images_dir = os.path.join(os.path.abspath(''),'images')


###################################################
## CREATE APP

external_stylesheets = [
    dict(
        href="https://fonts.googleapis.com/css?family=Raleway:300,300i,400,400i,600|Ruda:400,500,700&display=swap",
        rel="stylesheet"
    ),
]

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=external_stylesheets,
    # these tags are to insure proper responsiveness on mobile devices
    meta_tags=[
        dict(
            name= 'viewport',
            content="width=device-width, initial-scale=1.0" #maximum-scale=1.0
        )
    ]
)
app.title = "Green Algorithms"
server = app.server

appVersions_options = [{'label': f'{CURRENT_VERSION} (latest)', 'value': CURRENT_VERSION}] + [{'label': k, 'value': k} for k in APP_VERSION_OPTIONS_LIST]
app.layout = html.Div(dash.page_container, id='fullfullPage')




###################################################
# CALLBACKS #


### LOAD APP AND INPUTS
#######################

@app.callback(
    [
        ##################################################################
        ## WARNING: do not modify the order, unless modifying the order
        ## of the DEFAULT_VALUES accordingly
        Output(form_ids.runTime_hour_input(ID_MAIN_FORM),'value'),
        Output(form_ids.runTime_min_input(ID_MAIN_FORM),'value'),
        Output(form_ids.coreType_dropdown(ID_MAIN_FORM),'value'),
        Output(form_ids.numberCPUs_input(ID_MAIN_FORM),'value'),
        Output(form_ids.CPUmodel_dropdown(ID_MAIN_FORM), 'value'),
        Output(form_ids.tdpCPU_input(ID_MAIN_FORM),'value'),
        Output(form_ids.numberGPUs_input(ID_MAIN_FORM),'value'),
        Output(form_ids.GPUmodel_dropdown(ID_MAIN_FORM), 'value'),
        Output(form_ids.tdpGPU_input(ID_MAIN_FORM),'value'),
        Output(form_ids.memory_input(ID_MAIN_FORM),'value'),
        Output(form_ids.platformType_dropdown(ID_MAIN_FORM),'value'),
        Output(form_ids.usageCPU_radio(ID_MAIN_FORM),'value'),
        Output(form_ids.usageCPU_input(ID_MAIN_FORM),'value'),
        Output(form_ids.usageGPU_radio(ID_MAIN_FORM),'value'),
        Output(form_ids.usageGPU_input(ID_MAIN_FORM),'value'),
        Output(form_ids.pue_radio(ID_MAIN_FORM),'value'),
        Output(form_ids.PSF_radio(ID_MAIN_FORM), 'value'),
        Output(form_ids.PSF_input(ID_MAIN_FORM), 'value'),
        Output('appVersions_dropdown','value'),
        Output('import-error-message', 'is_open'),
        Output('log-error-subtitle', 'children'),
        Output('log-error-content', 'children'),
    ],
    [
        Input('url_content','search'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.aggregate_data(ID_MAIN_FORM), 'data'),
    ],
    # below line is required because the 'alert' container import-error-message is not in the layout initially
    suppress_callback_exceptions=True,
)
def filling_from_inputs(_, upload_content, filename, current_app_state):
    '''
    Fills the form either from the content of a csv of with default values.
    When errors are found in the csv, an alert container is displayed with 
    additional information for the user. Wrong values are replaced by default ones.
    The url is given as input so default values are filled when opening the app first.

    Once the appVersions_dropdown value is set, versionned data is loaded and
    the form starts to work accordingly.
    '''
    return_current_state = False

    if ctx.triggered_id is None:
        # NOTE this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
        # this is also the case for most of the callbacks takin the csv upload content as input, and was already the case when using 
        # the url instead of csv files for sharing the results
        # TODO understand this behaviour
        raise PreventUpdate 
    
    # only for initial call, when trigerred by the url
    elif 'upload-data.contents' not in ctx.triggered_prop_ids:
        return tuple(DEFAULT_VALUES.values()) + (False, '', '')

    # First we deal with the case the input_csv has just been flushed
    # Then we want to fill in the form with its current state
    elif upload_content is None:
        return_current_state = True
        show_err_mess = dash.no_update
        mess_subtitle = dash.no_update
        mess_content = dash.no_update

    elif upload_content:
        input_data, mess_subtitle, mess_content = open_input_csv_and_comment(upload_content, filename)
        # The input file could not be opened correctly
        if not input_data:
            return_current_state = True
            show_err_mess = True
        # If everything is fine so far, we parse the csv content
        else:
            processed_values, show_err_mess, mess_subtitle, mess_content = read_csv_input(input_data)
            return tuple(processed_values.values()) + (show_err_mess, mess_subtitle, mess_content)

    # The keys used to retrieve the content from aggregate data must 
    # match those of the callback generating it
    if return_current_state:
        return tuple(
            [
                current_app_state['runTime_hour'],
                current_app_state['runTime_min'],
                current_app_state['coreType'],
                current_app_state['numberCPUs'],
                current_app_state['CPUmodel'],
                current_app_state['tdpCPU'],
                current_app_state['numberGPUs'],
                current_app_state['GPUmodel'],
                current_app_state['tdpGPU'],
                current_app_state['memory'],
                current_app_state['platformType'],
                current_app_state['usageCPUradio'],
                current_app_state['usageCPU'],
                current_app_state['usageGPUradio'],
                current_app_state['usageGPU'],
                current_app_state['PUEradio'],
                current_app_state['PSFradio'],
                current_app_state['PSF'],
                current_app_state['appVersion'],
                show_err_mess,
                mess_subtitle,
                mess_content
            ]
        )

@app.callback(
    Output('url_content', 'search'),
    [
        Input(form_ids.confirm_reset(ID_MAIN_FORM),'submit_n_clicks'),
    ]
)
def reset_url(submit_n_clicks):
    '''
    When clicking reset, it reloads a new pages and removes the URL
    '''
    if submit_n_clicks:
        return ""
    
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
    '''
    Loads all the backend data required to propose consistent options to the user.
    '''
    if newVersion is None:
        newVersion = CURRENT_VERSION
    assert newVersion in APP_VERSION_OPTIONS_LIST + [CURRENT_VERSION]

    if newVersion == CURRENT_VERSION:
        newData = load_data(os.path.join(DATA_DIR, 'latest'), version = CURRENT_VERSION)
        # print('Loading latest data') # DEBUGONLY
    else:
        newData = load_data(os.path.join(DATA_DIR, newVersion), version=newVersion)
        # print(f'Loading {newVersion} data') # DEBUGONLY
    # print(f"CI FR: {newData.CI_dict_byLoc['FR']['carbonIntensity']}") # DEBUGONLY
    # print(f"TPUv3 TDP: {newData.cores_dict['GPU']['TPU v3']}")  # DEBUGONLY
    return vars(newData)


## PLATFORM AND PROVIDER
########################

# @app.callback(
#     Output('platformType_dropdown', 'options'),
#     [Input('versioned_data','data')]
# )
# def set_platform(data):
#     '''
#     Loads platform options based on backend data.
#     '''
#     if data is not None:
#         data_dict = SimpleNamespace(**data)
#         platformType_options = [
#             {'label': k,
#              'value': v} for v, k in list(data_dict.providersTypes.items()) +
#                                      [('personalComputer', 'Personal computer')] +
#                                      [('localServer', 'Local server')]
#         ]
#         return platformType_options
#     else:
#         return []

# @app.callback(
#     Output('provider_dropdown_div', 'style'),
#     [Input('platformType_dropdown', 'value')]
# )
# def set_providers(selected_platform):
#     '''
#     Shows or hide the "providers" box, based on the platform selected.
#     '''
#     if selected_platform in ['cloudComputing']:
#         # Only Cloud Computing need the providers box
#         outputStyle = {'display': 'block'}
#     else:
#         outputStyle = {'display': 'none'}

#     return outputStyle

@app.callback(
    Output(form_ids.provider_dropdown(ID_MAIN_FORM),'value'),
    [
        Input(form_ids.platformType_dropdown(ID_MAIN_FORM), 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.provider_dropdown(ID_MAIN_FORM), 'value'),
    ]
)
def set_provider(_, versioned_data, upload_content, filename, prev_provider):
    '''
    Sets the provider value, either from the csv content of as a default value.
    TODO: improve the choice of the default value.
    '''
    # Handles the case when the upload csv has just been flushed
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        return prev_provider
    
    # We check wheter the target value is found in the input csv
    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['provider'])
            if target_input:
                return target_input['provider']   
                
    return 'gcp'     

# @app.callback(
#     Output('provider_dropdown', 'options'),
#     [
#         Input('platformType_dropdown', 'value'),
#         Input('versioned_data','data')
#     ],
# )
# def set_providers(selected_platform, data):
#     '''
#     List options for the "provider" box.
#     '''
#     if data is not None:
#         data_dict = SimpleNamespace(**data)

#         providers_dict = data_dict.platformName_byType.get(selected_platform)
#         if providers_dict is not None:
#             availableOptions = list(providers_dict.items())
#         else:
#             availableOptions = []

#         listOptions = [
#             {'label': v, 'value': k} for k, v in availableOptions + [("other","Other")]
#         ]
#         return listOptions
#     else:
#         return []


## COMPUTING CORES
##################

# @app.callback(
#     Output('coreType_dropdown', 'options'),
#     [
#         Input('provider_dropdown', 'value'),
#         Input('platformType_dropdown', 'value'),
#         Input('versioned_data','data')
#     ])
# def set_coreType_options(_, __, data):
#     '''
#     List of options for coreType (CPU or GPU), based on the platform/provider selected.
#     Not really useful so far because we have no specific core types for a given provider.
#     '''
#     if data is not None:
#         data_dict = SimpleNamespace(**data)

#         availableOptions = data_dict.cores_dict.keys()
#         listOptions = [{'label': k, 'value': k} for k in list(sorted(availableOptions))+['Both']]
#         return listOptions
#     else:
#         return []

# @app.callback(
#     [
#         Output('CPUmodel_dropdown', 'options'),
#         Output('GPUmodel_dropdown', 'options')
#     ],
#     [Input('versioned_data','data')]
# )
# def set_coreOptions(data):
#     '''
#     List of options for core models.
#     '''
#     if data is not None:
#         data_dict = SimpleNamespace(**data)

#         coreModels_options = dict()
#         for coreType in ['CPU', 'GPU']:
#             availableOptions = sorted(list(data_dict.cores_dict[coreType].keys()))
#             availableOptions = put_value_first(availableOptions, 'Any')
#             coreModels_options[coreType] = [
#                 {'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions)) +
#                 [("Other", "other")]
#             ]

#         return coreModels_options['CPU'], coreModels_options['GPU']

#     else:
#         return [],[]

# @app.callback(
#     [
#         Output('CPU_div', 'style'),
#         Output('title_CPU', 'style'),
#         Output('usageCPU_div', 'style'),
#         Output('GPU_div', 'style'),
#         Output('title_GPU', 'style'),
#         Output('usageGPU_div', 'style'),
#     ],
#     [
#         Input('coreType_dropdown', 'value')
#     ]
# )
# def show_CPUGPUdiv(selected_coreType):
#     '''
#     Shows or hides the CPU/GPU input blocks (and the titles) based on the selected core type.
#     '''
#     show = {'display': 'block'}
#     showFlex = {'display': 'flex'}
#     hide = {'display': 'none'}
#     if selected_coreType == 'CPU':
#         return show, hide, showFlex, hide, hide, hide
#     elif selected_coreType == 'GPU':
#         return hide, hide, hide, show, hide, showFlex
#     else:
#         return show, show, showFlex, show, show, showFlex

# @app.callback(
#     Output('tdpCPU_div', 'style'),
#     [
#         Input('CPUmodel_dropdown', 'value'),
#     ]
# )
# def display_TDP4CPU(selected_coreModel):
#     '''
#     Shows or hides the CPU TDP input box.
#     '''
#     if selected_coreModel == "other":
#         return {'display': 'flex'}
#     else:
#         return {'display': 'none'}

# @app.callback(
#     Output('tdpGPU_div', 'style'),
#     [
#         Input('GPUmodel_dropdown', 'value'),
#     ]
# )
# def display_TDP4GPU(selected_coreModel):
#     '''
#     Shows or hides the GPU TDP input box.
#     '''
#     if selected_coreModel == "other":
#         return {'display': 'flex'}
#     else:
#         return {'display': 'none'}


## LOCATION AND SERVER
######################

# @app.callback(
#     [
#         Output('location_div', 'style'),
#         Output('server_div', 'style'),
#     ],
#     [
#         Input('platformType_dropdown', 'value'),
#         Input('provider_dropdown', 'value'),
#         Input('server_dropdown','value'),
#         Input('versioned_data','data')
#     ]
# )
# def display_location(selected_platform, selected_provider, selected_server, data):
#     '''
#     Shows either LOCATION or SERVER depending on the platform.
#     '''
#     if data is not None:
#         data_dict = SimpleNamespace(**data)
#         providers_withoutDC = data_dict.providers_withoutDC
#     else:
#         providers_withoutDC = []

#     show = {'display': 'flex'}
#     hide = {'display': 'none'}
#     if selected_platform == 'cloudComputing':
#         if selected_provider in ['other'] + providers_withoutDC:
#             return show, hide
#         elif selected_server == 'other':
#             return show, show
#         else:
#             return hide, show
#     else:
#         return show, hide
    

# ### SERVER (only for Cloud computing for now)

@app.callback(
    Output(form_ids.server_continent_dropdown(ID_MAIN_FORM),'value'),
    [
        Input(form_ids.provider_dropdown(ID_MAIN_FORM), 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.server_continent_dropdown(ID_MAIN_FORM), 'value'),
    ]
)
def set_serverContinents_value(selected_provider, versioned_data, upload_content, filename, prev_server_continent):
    '''
    Sets the value for server's continent, depending on the provider.
    We want to fetch the value based on csv input but also to display 
    a value selcted previously by the user.
    '''
    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to understand which cases
    # may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        return prev_server_continent

    # We first check wheter the target value is found in the input csv
    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['serverContinent'])
            if target_input:
                return target_input['serverContinent']

    # Otherwise we return a suitable default value
    availableOptions = availableLocations_continent(selected_provider, data=versioned_data)

    # NOTE The following handles two cases: 
    # when the server continent value had previously been set by the user
    # when this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
    # print('avai loc in set conti server, ', availableOptions)
    if prev_server_continent in availableOptions:
        defaultValue = prev_server_continent
    else:
        try: 
            defaultValue = availableOptions[0]
        except:
            defaultValue = None
    return defaultValue

# @app.callback(
#     Output('server_continent_dropdown','options'),
#     [
#         Input('provider_dropdown', 'value'),
#         Input('versioned_data','data')
#     ]
# )
# def set_serverContinents_options(selected_provider, data):
#     '''
#     List of options and default value for server's continent, based on the provider
#     '''
#     availableOptions = availableLocations_continent(selected_provider, data=data)
#     listOptions = [{'label': k, 'value': k} for k in sorted(availableOptions)] + [{'label': 'Other', 'value': 'other'}]
#     return listOptions

# @app.callback(
#     Output('server_dropdown','style'),
#     [
#         Input('server_continent_dropdown', 'value')
#     ]
# )
# def set_server_style(selected_continent):
#     '''
#     Show or not the choice of servers, don't if continent is on "Other"
#     '''
#     if selected_continent == 'other':
#         return {'display': 'none'}

#     else:
#         return {'display': 'block'}

@app.callback(
    Output(form_ids.server_dropdown(ID_MAIN_FORM),'value'),
    [
        Input(form_ids.provider_dropdown(ID_MAIN_FORM), 'value'),
        Input(form_ids.server_continent_dropdown(ID_MAIN_FORM), 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.server_dropdown(ID_MAIN_FORM),'value'),
    ]
)
def set_server_value(selected_provider, selected_continent, versioned_data, upload_content, filename, prev_server_value):
    '''
    Sets the value for servers, based on provider and continent.
    Here again we want to display a default value, to 
    fecth the value from a csv or to show a value previously selected by the user.
    '''

    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to 
    # understand which cases may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        return prev_server_value

    # We first check wheter the target value is found in the input csv 
    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['server'])
            if target_input :
                return target_input['server']
    
    # Handles special case
    if selected_continent == 'other':
        return 'other'

    # Otherwise we return a suitable default value
    availableOptions = availableOptions_servers(selected_provider, selected_continent, data=versioned_data)
    try:
        if prev_server_value in [server['name_unique'] for server in availableOptions]:
            # print('set server val, get previous value ', prev_server_value)
            # NOTE The following handles two cases: 
            # when the server continent value had previously been set by the user
            # when this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
            defaultValue = prev_server_value
        else :
            defaultValue = availableOptions[0]['name_unique']
    except:
        defaultValue = None
    return defaultValue

# @app.callback(
#     Output('server_dropdown','options'),
#     [
#         Input('provider_dropdown', 'value'),
#         Input('server_continent_dropdown', 'value'),
#         Input('versioned_data','data')
#     ]
# )
# def set_server_options(selected_provider,selected_continent, data):
#     '''
#     List of options for servers, based on provider and continent
#     '''
#     availableOptions = availableOptions_servers(selected_provider,selected_continent,data=data)
#     listOptions = [{'label': k['Name'], 'value': k['name_unique']} for k in availableOptions + [{'Name':"other", 'name_unique':'other'}]]

#     return listOptions


# ## LOCATION (only for local server, personal device or "other" cloud server)

# @app.callback(
#     Output('location_continent_dropdown', 'options'),
#     [Input('versioned_data','data')]
# )
# def set_continentOptions(data):
#     if data is not None:
#         data_dict = SimpleNamespace(**data)

#         continentsList = list(data_dict.CI_dict_byName.keys())
#         continentsDict = [{'label': k, 'value': k} for k in sorted(continentsList)]

#         return continentsDict
#     else:
#         return []

@app.callback(
    Output(form_ids.location_continent_dropdown(ID_MAIN_FORM), 'value'),
    [
        Input(form_ids.server_continent_dropdown(ID_MAIN_FORM),'value'),
        Input(form_ids.server_div(ID_MAIN_FORM), 'style'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.location_continent_dropdown(ID_MAIN_FORM), 'value'),
        State('versioned_data','data'),
    ]
)
def set_continent_value(selected_serverContinent, display_server, upload_content, filename, prev_locationContinent, versioned_data):
    '''
    Sets the value for location continent.
    Same as for server and server continent regarding the different inputs.
    '''
    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to 
    # understand which cases may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        return prev_locationContinent
    
    # We first check wheter the target value is found in the input csv
    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['locationContinent'])
            if target_input :
                return target_input['locationContinent']
    
    # NOTE The following handles two cases: 
    # when the continent value had previously been set by the user
    # when this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
    if prev_locationContinent is not None :
        return prev_locationContinent
    # the server div is shown, so we pull the continent from there
    if (display_server['display'] != 'none') & (selected_serverContinent != 'other'):
        return selected_serverContinent
    return 'Europe'

@app.callback(
    [
        Output(form_ids.location_country_dropdown(ID_MAIN_FORM), 'options'),
        Output(form_ids.location_country_dropdown(ID_MAIN_FORM), 'value'),
        Output(form_ids.location_country_dropdown_div(ID_MAIN_FORM), 'style'),
    ],
    [
        Input(form_ids.location_continent_dropdown(ID_MAIN_FORM), 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.location_country_dropdown(ID_MAIN_FORM), 'value')
    ]
)
def set_countries_options(selected_continent, versioned_data, upload_content, filename, prev_selectedCountry):
    '''
    List of options and value for countries.
    Hides country dropdown if continent=World is selected.
    Must fetch the value from a csv as well.
    '''
    availableOptions = availableOptions_country(selected_continent, data=versioned_data)
    listOptions = [{'label': k, 'value': k} for k in availableOptions]
    
    defaultValue = None

    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server country value for the default Value, but it allows to 
    # understand which cases may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        defaultValue = prev_selectedCountry

    # We first check wheter the target value is found in the input csv
    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['locationCountry'])
            if target_input :
                defaultValue = target_input['locationCountry']

    # otherwise we get a suitable default value    
    if defaultValue is None:
        # NOTE The following handles two cases: 
        # when the country value had previously been set by the user
        # when this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
        if prev_selectedCountry in availableOptions :
            defaultValue = prev_selectedCountry
        else:
            try:
                defaultValue = availableOptions[0]
            except:
                defaultValue = None

    if selected_continent == 'World':
        country_style = {'display': 'none'}
    else:
        country_style = {'display': 'block'}

    return listOptions, defaultValue, country_style

@app.callback(
    [
        Output(form_ids.location_region_dropdown(ID_MAIN_FORM), 'options'),
        Output(form_ids.location_region_dropdown(ID_MAIN_FORM), 'value'),
        Output(form_ids.location_region_dropdown_div(ID_MAIN_FORM), 'style'),
    ],
    [
        Input(form_ids.location_continent_dropdown(ID_MAIN_FORM), 'value'),
        Input(form_ids.location_country_dropdown(ID_MAIN_FORM), 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.location_region_dropdown(ID_MAIN_FORM), 'value'),
    ]

)
def set_regions_options(selected_continent, selected_country, versioned_data, upload_content, filename, prev_selectedRegion):
    '''
    List of options and value for regions.
    Hides region dropdown if only one possible region (or continent=World)
    '''
    locs = availableOptions_region(selected_continent, selected_country, data=versioned_data)
    if versioned_data is not None:
        listOptions = [{'label': versioned_data['CI_dict_byLoc'][loc]['regionName'], 'value': loc} for loc in locs]
    else:
        listOptions = []

    defaultValue = None

    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server region value for the default Value, but it allows to 
    # understand which cases may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        defaultValue = prev_selectedRegion


    # We first check wheter the target value is found in the input csv
    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['locationRegion'])
            if target_input :
                defaultValue = target_input['locationRegion']

    # otherwise we get a suitable default value  
    if defaultValue is None:
        # NOTE The following handles two cases: 
        # when the region value had previously been set by the user
        # when this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
        if prev_selectedRegion in locs:
            defaultValue = prev_selectedRegion
        else:
            try:
                    defaultValue = locs[0]
            except:
                defaultValue = None

    if (selected_continent == 'World')|(len(listOptions) == 1):
        region_style = {'display': 'none'}
    else:
        region_style = {'display': 'block'}

    return listOptions, defaultValue, region_style


# ## USAGE FACTORS
# ################

# @app.callback(
#     Output('usageCPU_input','style'),
#     [
#         Input('usageCPU_radio', 'value'),
#         Input('usageCPU_input', 'disabled')
#     ]
# )
# def display_usage_input(answer_usage, disabled):
#     '''
#     Show or hide the usage factor input box, based on Yes/No input
#     '''
#     if answer_usage == 'No':
#         out = {'display': 'none'}
#     else:
#         out = {'display': 'block'}

#     if disabled:
#         out['background-color'] = MY_COLORS['boxesColor']

#     return out

# @app.callback(
#     Output('usageGPU_input','style'),
#     [
#         Input('usageGPU_radio', 'value'),
#         Input('usageGPU_input', 'disabled')
#     ]
# )
# def display_usage_input(answer_usage, disabled):
#     '''
#     Show or hide the usage factor input box, based on Yes/No input
#     '''
#     if answer_usage == 'No':
#         out = {'display': 'none'}
#     else:
#         out = {'display': 'block'}

#     if disabled:
#         out['background-color'] = MY_COLORS['boxesColor']

#     return out


# ## PUE INPUTS
# ################

# @app.callback(
#     Output('PUEquestion_div','style'),
#     [
#         Input('location_region_dropdown','value'),
#         Input('platformType_dropdown', 'value'),
#         Input('provider_dropdown', 'value'),
#         Input('server_dropdown', 'value')
#     ]
# )
# def display_pue_question(_, selected_platform, selected_provider, selected_server):
#     '''
#     Shows or hides the PUE question depending on the platform
#     '''
#     if selected_platform == 'localServer':
#         return {'display': 'flex'}
#     elif (selected_platform == 'cloudComputing')&((selected_provider == 'other')|(selected_server == 'other')):
#         return {'display': 'flex'}
#     else:
#         return {'display': 'none'}

# @app.callback(
#     Output('PUE_input','style'),
#     [
#         Input('pue_radio', 'value'),
#         Input('PUE_input','disabled')
#     ]
# )
# def display_pue_input(answer_pue, disabled):
#     '''
#     Shows or hides the PUE input box
#     '''
#     if answer_pue == 'No':
#         out = {'display': 'none'}
#     else:
#         out = {'display': 'block'}

#     if disabled:
#         out['background-color'] = MY_COLORS['boxesColor']

#     return out

@app.callback(
    Output(form_ids.PUE_input(ID_MAIN_FORM),'value'),
    [
        Input(form_ids.pue_radio(ID_MAIN_FORM), 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State(form_ids.PUE_input(ID_MAIN_FORM),'value'),
    ]
)
def set_PUE(radio, versioned_data, upload_content, filename, prev_pue):
    '''
    Sets the PUE value, either from csv input or as a default value.
    '''
    if versioned_data is not None:
        data_dict = SimpleNamespace(**versioned_data)
        defaultPUE = data_dict.pueDefault_dict['Unknown']
    else:
        defaultPUE = 0

    if radio == 'No':
        return defaultPUE
    
    # Handles the case when the upload csv has just been flushed
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        defaultPUE = prev_pue

    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['PUE'])
            if target_input :
                defaultPUE = target_input['PUE']

    return defaultPUE


# ## PSF INPUTS
# ##############

# @app.callback(
#     Output('PSF_input','style'),
#     [
#         Input('PSF_radio', 'value'),
#         Input('PSF_input', 'disabled')
#     ]
# )
# def display_PSF_input(answer_PSF, disabled):
#     '''
#     Shows or hides the PSF input box
#     '''
#     if answer_PSF == 'No':
#         out = {'display': 'none'}
#     else:
#         out = {'display': 'block'}

#     if disabled:
#         out['background-color'] = MY_COLORS['boxesColor']

#     return out


# ## RESET AND APP VERSIONS
# #########################

@app.callback(
    Output(form_ids.confirm_reset(ID_MAIN_FORM),'displayed'),
    [
        Input(form_ids.reset_link(ID_MAIN_FORM),'n_clicks')
    ]
)
def display_confirm(clicks):
    '''
    Display a popup asking for reset confirmation.
    '''
    if clicks is not None:
        return True
    return False

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
    '''
    Show the different available versions.
    '''
    if (clicks is not None)|((version is not None)&(version != CURRENT_VERSION)):
        return {'display':'flex'}
    else:
        return oldStyle


# ## PROCESS INPUTS
# #################

# @app.callback(
#     Output("aggregate_data", "data"),
#     [
#         Input('versioned_data','data'),
#         Input("coreType_dropdown", "value"),
#         Input("numberCPUs_input", "value"),
#         Input("CPUmodel_dropdown", "value"),
#         Input("tdpCPU_div", "style"),
#         Input("tdpCPU_input", "value"),
#         Input("numberGPUs_input", "value"),
#         Input("GPUmodel_dropdown", "value"),
#         Input("tdpGPU_div", "style"),
#         Input("tdpGPU_input", "value"),
#         Input("memory_input", "value"),
#         Input("runTime_hour_input", "value"),
#         Input("runTime_min_input", "value"),
#         Input("location_continent_dropdown", "value"),
#         Input("location_country_dropdown", "value"),
#         Input("location_region_dropdown", "value"),
#         Input("server_continent_dropdown", "value"),
#         Input("server_dropdown", "value"),
#         Input('location_div', 'style'),
#         Input('server_div','style'),
#         Input("usageCPU_radio", "value"),
#         Input("usageCPU_input", "value"),
#         Input("usageGPU_radio", "value"),
#         Input("usageGPU_input", "value"),
#         Input('PUEquestion_div','style'),
#         Input("pue_radio", "value"),
#         Input("PUE_input", "value"),
#         Input("PSF_radio", "value"),
#         Input("PSF_input", "value"),
#         Input('platformType_dropdown', 'value'),
#         Input('provider_dropdown', 'value'),
#         Input('provider_dropdown_div', 'style'),
#     ],
# )
# def aggregate_input_values(data, coreType, n_CPUcores, CPUmodel, tdpCPUstyle, tdpCPU, n_GPUs, GPUmodel, tdpGPUstyle, tdpGPU,
#                            memory, runTime_hours, runTime_min, locationContinent, locationCountry, locationRegion,
#                            serverContinent, server, locationStyle, serverStyle, usageCPUradio, usageCPU, usageGPUradio, usageGPU,
#                            PUEdivStyle, PUEradio, PUE, PSFradio, PSF, selected_platform, selected_provider, providerStyle):
#     '''
#     Computes all the metrics and gathers the information provided by the inputs of the form.
#     '''
#     output = dict()

#     #############################################
#     ### PREPROCESS: check if computations can be performed

#     notReady = False

#     ### Runtime
#     test_runTime = 0
#     if runTime_hours is None:
#         actual_runTime_hours = 0
#         test_runTime += 1
#     else:
#         actual_runTime_hours = runTime_hours

#     if runTime_min is None:
#         actual_runTime_min = 0
#         test_runTime += 1
#     else:
#         actual_runTime_min = runTime_min
#     runTime = actual_runTime_hours + actual_runTime_min/60.

#     ### Core type
#     if coreType is None:
#         notReady = True
#     elif (coreType in ['CPU','Both'])&((n_CPUcores is None)|(CPUmodel is None)):
#         notReady = True
#     elif (coreType in ['GPU','Both'])&((n_GPUs is None)|(GPUmodel is None)):
#         notReady = True

#     ### Versioned data
#     if data is not None:
#         data_dict = SimpleNamespace(**data)
#         version = data_dict.version
#     else:
#         notReady = True

#     ### Location
#     if is_shown(locationStyle):
#         # this means the "location" input is shown, so we use location instead of server
#         locationVar = locationRegion
#     elif (server is None) | (server == 'other') | (data is None):
#         locationVar = None
#     else:
#         locationVar = data_dict.datacenters_dict_byName[server]['location']

#     ### Platform
#     if selected_platform is None:
#         notReady = True
#     elif (selected_platform == 'cloudComputing')&(selected_provider is None):
#         notReady = True

#     ### Other required inputs
#     if (memory is None)|(tdpCPU is None)|(tdpGPU is None)|(locationVar is None)| \
#             (usageCPU is None)|(usageGPU is None)|(PUE is None)|(PSF is None):
#         notReady = True

#     ### If any of the required inputs is note ready: do not compute
#     if notReady:
#         output['coreType'] = None
#         output['CPUmodel'] = None
#         output['numberCPUs'] = None
#         output['usageCPU'] = None
#         output['usageCPUradio'] = None
#         output['tdpCPU'] = None
#         output['GPUmodel'] = None
#         output['numberGPUs'] = None
#         output['tdpGPU'] = None
#         output['usageGPU'] = None
#         output['usageGPUradio'] = None
#         output['GPUpower'] = None
#         output['memory'] = None
#         output['runTime_hour'] = None
#         output['runTime_min'] = None
#         output['runTime'] = None
#         output['platformType'] = None
#         output['location'] = None
#         output['carbonIntensity'] = None
#         output['PUE'] = None
#         output['PUEradio'] = None
#         output['PSF'] = None
#         output['PSFradio'] = None
#         output['carbonEmissions'] = 0
#         output['CE_CPU'] = 0
#         output['CE_GPU'] = 0
#         output['CE_core'] = 0
#         output['CE_memory'] = 0
#         output['n_treeMonths'] = 0
#         output['flying_context'] = 0
#         output['nkm_drivingUS'] = 0
#         output['nkm_drivingEU'] = 0
#         output['nkm_train'] = 0
#         output['energy_needed'] = 0
#         output['power_needed'] = 0
#         output['flying_text'] = None
#         output['text_CE'] = '... g CO2e'
#         output['appVersion'] = version

#     #############################################
#     ### PRE-COMPUTATIONS: update variables used in the calcul based on inputs

#     else:
#         ### PUE
#         defaultPUE = data_dict.pueDefault_dict['Unknown']
#         # the input PUE is used only if the PUE box is shown AND the radio button is "Yes"
#         if (is_shown(PUEdivStyle)) & (PUEradio == 'Yes'):
#             PUE_used = PUE
        
#         ### PLATFORM ALONG WITH PUE
#         else:
#             if selected_platform == 'personalComputer':
#                 PUE_used = 1
#             elif selected_platform == 'localServer':
#                 PUE_used = defaultPUE
#             else:
#                 # Cloud
#                 if selected_provider == 'other':
#                     PUE_used = defaultPUE
#                 else:
#                     # if we don't know the PUE of this specific data centre, or if we 
#                     # don't know the data centre, we use the provider's default
#                     server_data = data_dict.datacenters_dict_byName.get(server)
#                     if server_data is not None:
#                         if pd.isnull(server_data['PUE']):
#                             PUE_used = data_dict.pueDefault_dict[selected_provider]
#                         else:
#                             PUE_used = server_data['PUE']
#                     else:
#                         PUE_used = data_dict.pueDefault_dict[selected_provider]

#         ### CPUs
#         if coreType in ['CPU', 'Both']:
#             if is_shown(tdpCPUstyle):
#                 # we asked the question about TDP
#                 CPUpower = tdpCPU
#             else:
#                 if CPUmodel == 'other':
#                     CPUpower = tdpCPU
#                 else:
#                     CPUpower = data_dict.cores_dict['CPU'][CPUmodel]
#             if usageCPUradio == 'Yes':
#                 usageCPU_used = usageCPU
#             else:
#                 usageCPU_used = 1.
#             powerNeeded_CPU = PUE_used * n_CPUcores * CPUpower * usageCPU_used
#         else:
#             powerNeeded_CPU = 0
#             CPUpower = 0
#             usageCPU_used = 0

#         if coreType in ['GPU', 'Both']:
#             if is_shown(tdpGPUstyle):
#                 GPUpower = tdpGPU
#             else:
#                 if GPUmodel == 'other':
#                     GPUpower = tdpGPU
#                 else:
#                     GPUpower = data_dict.cores_dict['GPU'][GPUmodel]
#             if usageGPUradio == 'Yes':
#                 usageGPU_used = usageGPU
#             else:
#                 usageGPU_used = 1.
#             powerNeeded_GPU = PUE_used * n_GPUs * GPUpower * usageGPU_used
#         else:
#             powerNeeded_GPU = 0
#             GPUpower = 0
#             usageGPU_used = 0

#         ### SERVER/LOCATION
#         carbonIntensity = data_dict.CI_dict_byLoc[locationVar]['carbonIntensity']

#         ### PSF
#         if PSFradio == 'Yes':
#             PSF_used = PSF
#         else:
#             PSF_used = 1

#         #############################################
#         ### COMPUTATIONS: final outputs are computed

#         # Power needed, in Watt
#         powerNeeded_core = powerNeeded_CPU + powerNeeded_GPU
#         powerNeeded_memory = PUE_used * (memory * data_dict.refValues_dict['memoryPower'])
#         powerNeeded = powerNeeded_core + powerNeeded_memory

#         # Energy needed, in kWh (so dividing by 1000 to convert to kW)
#         energyNeeded_CPU = runTime * powerNeeded_CPU * PSF_used / 1000
#         energyNeeded_GPU = runTime * powerNeeded_GPU * PSF_used / 1000
#         energyNeeded_core = runTime * powerNeeded_core * PSF_used / 1000
#         eneregyNeeded_memory = runTime * powerNeeded_memory * PSF_used / 1000
#         energyNeeded = runTime * powerNeeded * PSF_used / 1000

#         # Carbon emissions: carbonIntensity is in g per kWh, so results in gCO2
#         CE_CPU = energyNeeded_CPU * carbonIntensity
#         CE_GPU = energyNeeded_GPU * carbonIntensity
#         CE_core = energyNeeded_core * carbonIntensity
#         CE_memory  = eneregyNeeded_memory * carbonIntensity
#         carbonEmissions = energyNeeded * carbonIntensity

#         # Storing all outputs to catch the app state and adapt textual content
#         output['coreType'] = coreType
#         output['CPUmodel'] = CPUmodel
#         output['numberCPUs'] = n_CPUcores
#         output['tdpCPU'] = CPUpower
#         output['usageCPUradio'] = usageCPUradio
#         output['usageCPU'] = usageCPU_used
#         output['GPUmodel'] = GPUmodel
#         output['numberGPUs'] = n_GPUs
#         output['tdpGPU'] = GPUpower
#         output['usageGPUradio'] = usageGPUradio
#         output['usageGPU'] = usageGPU_used
#         output['memory'] = memory
#         output['runTime_hour'] = actual_runTime_hours
#         output['runTime_min'] = actual_runTime_min
#         output['runTime'] = runTime
#         output['platformType'] = selected_platform
#         output['locationContinent'] = locationContinent
#         output['locationCountry'] = locationCountry
#         output['locationRegion'] = locationRegion
#         output['provider'] = selected_provider
#         output['serverContinent'] = serverContinent
#         output['server'] = server
#         output['location'] = locationVar
#         output['carbonIntensity'] = carbonIntensity
#         output['PUE'] = PUE_used
#         output['PUEradio'] = PUEradio
#         output['PSF'] = PSF_used
#         output['PSFradio'] = PSFradio
#         output['carbonEmissions'] = carbonEmissions
#         output['CE_CPU'] = CE_CPU
#         output['CE_GPU'] = CE_GPU
#         output['CE_core'] = CE_core
#         output['CE_memory'] = CE_memory
#         output['energy_needed'] = energyNeeded
#         output['power_needed'] = powerNeeded
#         output['appVersion'] = version

#         ### Context
#         output['n_treeMonths'] = carbonEmissions / data_dict.refValues_dict['treeYear'] * 12
#         output['nkm_drivingUS'] = carbonEmissions / data_dict.refValues_dict['passengerCar_US_perkm']
#         output['nkm_drivingEU'] = carbonEmissions / data_dict.refValues_dict['passengerCar_EU_perkm']
#         output['nkm_train'] = carbonEmissions / data_dict.refValues_dict['train_perkm']

#         ### Text plane trips
#         if carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NY-SF']:
#             output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_PAR-LON']
#             output['flying_text'] = "Paris-London"
#         elif carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NYC-MEL']:
#             output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NY-SF']
#             output['flying_text'] = "NYC-San Francisco"
#         else:
#             output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NYC-MEL']
#             output['flying_text'] = "NYC-Melbourne"

#         ### Text carbon emissions
#         carbonEmissions_value = carbonEmissions  # in g CO2e
#         carbonEmissions_unit = "g"
#         if carbonEmissions_value >= 1e6:
#             carbonEmissions_value /= 1e6
#             carbonEmissions_unit = "T"
#         elif carbonEmissions_value >= 1e3:
#             carbonEmissions_value /= 1e3
#             carbonEmissions_unit = "kg"
#         elif carbonEmissions_value < 1:
#             carbonEmissions_value *= 1e3
#             carbonEmissions_unit = "mg"
#         if (carbonEmissions_value != 0)&((carbonEmissions_value >= 1e3)|(carbonEmissions_value < 1)):
#             output['text_CE'] = f"{carbonEmissions_value:,.2e} {carbonEmissions_unit} CO2e"
#         else:
#             output['text_CE'] = f"{carbonEmissions_value:,.2f} {carbonEmissions_unit} CO2e"

#         ### Text energy
#         energyNeeded_value = energyNeeded  # in kWh
#         energyNeeded_unit = "kWh"
#         if energyNeeded_value >= 1e3:
#             energyNeeded_value /= 1e3
#             energyNeeded_unit = "MWh"
#         elif energyNeeded_value < 1:
#             energyNeeded_value *= 1e3
#             energyNeeded_unit = "Wh"
#         if (energyNeeded_value != 0) & ((energyNeeded_value >= 1e3) | (energyNeeded_value < 1)):
#             output['text_energyNeeded'] = f"{energyNeeded_value:,.2e} {energyNeeded_unit}"
#         else:
#             output['text_energyNeeded'] = f"{energyNeeded_value:,.2f} {energyNeeded_unit}"

#         ### Text tree-months
#         treeTime_value = output['n_treeMonths']  # in tree-months
#         treeTime_unit = "tree-months"
#         if treeTime_value >= 24:
#             treeTime_value /= 12
#             treeTime_unit = "tree-years"
#         if (treeTime_value != 0) & ((treeTime_value >= 1e3) | (treeTime_value < 0.1)):
#             output['text_treeYear'] = f"{treeTime_value:,.2e} {treeTime_unit}"
#         else:
#             output['text_treeYear'] = f"{treeTime_value:,.2f} {treeTime_unit}"

#     return output


# ## UPDATE TOP TEXT
# ##################

@app.callback(
    [
        Output("carbonEmissions_text", "children"),
        Output("energy_text", "children"),
        Output("treeMonths_text", "children"),
        Output("driving_text", "children"),
        Output("flying_text", "children"),
    ],
    [Input(form_ids.aggregate_data(ID_MAIN_FORM), "data")],
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
    Input(form_ids.aggregate_data(ID_MAIN_FORM), "data"),
)
def update_text(data):
    if (data['flying_context'] >= 1)|(data['flying_context'] == 0):
        foo = f"flights {data['flying_text']}"
    else:
        foo = f"of a flight {data['flying_text']}"
    return foo


## IMPORT AND EXPORT RESULTS
############################

@app.callback(
    Output('csv-input-timer', 'disabled'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True,
)
def trigger_timer_to_flush_input_csv(input_csv):
    '''
    When a csv is dropped, triggers a timer that allows to flush this csv.
    If the input is none, this means that we just flushed it so we do not
    trigger the timer again.
    '''
    if input_csv is None:
        return True
    return False

@app.callback(
        Output('upload-data', 'contents'),
        Input('csv-input-timer', 'n_intervals'),
        prevent_initial_call=True,
)
def flush_input_csv_content(n):
    '''
    Flushes the input csv.
    This is required if we want to enable the user to load again the same csv.
    Otherwise, if not flushed, the csv content does not change so it does not trigger
    the reading of its content.
    '''
    return None

@app.callback(
    Output("aggregate-data-csv", "data"),
    Input("btn-download_csv", "n_clicks"),
    State(form_ids.aggregate_data(ID_MAIN_FORM), "data"),
    prevent_initial_call=True,
)
def export_as_csv(_, aggregate_data):
    '''
    Exports the aggregate_data.
    '''
    to_export_dict = {key: [str(val)] for key, val in aggregate_data.items()}
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    to_export = pd.DataFrame.from_dict(to_export_dict, orient='columns')
    return dcc.send_data_frame(to_export.to_csv, f"GreenAlgorithms_results_{now}.csv", index=False, sep=';')


## OUTPUT GRAPHICS
#################

@app.callback(
    Output("pie_graph", "figure"),
    Input(form_ids.aggregate_data(ID_MAIN_FORM), "data"),
)
def create_pie_graph(aggData):
    return create_cores_memory_pie_graphic(aggData)

### UPDATE BAR CHART COMPARISON
# FIXME: looks weird with 0 emissions
@app.callback(
    Output("barPlotComparison", "figure"),
    [
        Input(form_ids.aggregate_data(ID_MAIN_FORM), "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart(aggData, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        return create_ci_bar_chart_graphic(aggData, data_dict)
    return None

### UPDATE BAR CHARTCPU
@app.callback(
    Output("barPlotComparison_cores", "figure"),
    [
        Input(form_ids.aggregate_data(ID_MAIN_FORM), "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart_cores(aggData, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        if aggData['coreType'] is None:
            return go.Figure()
        return create_cores_bar_chart_graphic(aggData, data_dict)
    return None


## OUTPUT SUMMARY
#################

@app.callback(
    Output('report_markdown', 'children'),
    [
        Input(form_ids.aggregate_data(ID_MAIN_FORM), "data"),
        Input('versioned_data','data')
    ],
)
def fillin_report_text(aggData, data):
    '''
    Writes a summary text of the current computation that is shown as an example
    for the user on how to report its impact.
    '''
    if (aggData['numberCPUs'] is None)&(aggData['numberGPUs'] is None):
        return('')
    elif data is None:
        return ('')
    else:
        data_dict = SimpleNamespace(**data)

        # Text runtime
        minutes = aggData['runTime_min']
        hours = aggData['runTime_hour']
        if (minutes > 0)&(hours>0):
            textRuntime = "{}h and {}min".format(hours, minutes)
        elif (hours > 0):
            textRuntime = "{}h".format(hours)
        else:
            textRuntime = "{}min".format(minutes)

        # text cores
        textCores = ""
        if aggData['coreType'] in ['GPU','Both']:
            if aggData['numberGPUs'] > 1:
                suffixProcessor = 's'
            else:
                suffixProcessor = ''
            textCores += f"{aggData['numberGPUs']} GPU{suffixProcessor} {aggData['GPUmodel']}"
        if aggData['coreType'] == 'Both':
            textCores += " and "
        if aggData['coreType'] in ['CPU','Both']:
            if aggData['numberCPUs'] > 1:
                suffixProcessor = 's'
            else:
                suffixProcessor = ''
            textCores += f"{aggData['numberCPUs']} CPU{suffixProcessor} {aggData['CPUmodel']}"

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
        (calculated using green-algorithms.org {CURRENT_VERSION} \[1\]).
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