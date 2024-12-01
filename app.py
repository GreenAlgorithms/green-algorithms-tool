# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import os
import dash
import datetime
import copy

from dash import html, dcc, ctx
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from types import SimpleNamespace
from flask import send_file # Integrating Loader IO
from urllib import parse

import pandas as pd
import plotly.graph_objects as go

from utils.utils import put_value_first, YES_NO_OPTIONS, unlist, is_shown
from utils.graphics import create_cores_bar_chart_graphic, create_ci_bar_chart_graphic, create_cores_memory_pie_graphic, MY_COLORS
from utils.handle_inputs import load_data, current_version, data_dir
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region
from utils.handle_inputs import validateInput, prepURLqs, open_input_csv_and_comment, read_csv_input, default_values, read_input_csv

# current_version = 'v2.2'

#############
# LOAD DATA #
#############


# data_dir = os.path.join(os.path.abspath(''),'data')
image_dir = os.path.join('assets/images')
static_image_route = '/static/'
images_dir = os.path.join(os.path.abspath(''),'images')


##############
# CREATE APP #
##############

external_stylesheets = [
    dict(href="https://fonts.googleapis.com/css?family=Raleway:300,300i,400,400i,600|Ruda:400,500,700&display=swap",
         rel="stylesheet"),
    # dbc.themes.CERULEAN
]

# print(f'Dash version: {dcc.__version__}') # DEBUGONLY

app = dash.Dash(
    __name__,
    use_pages=True,
    external_stylesheets=external_stylesheets,
    # The following argument requires dash >= 2.14
    #---------------------------------------------
#     routing_callback_inputs={
#         # The mapCI will be passed as a `layout` keyword argument to page layout functions
#         "mapCI": mapCI,
#    },
    # these tags are to insure proper responsiveness on mobile devices
    meta_tags=[dict(
        name= 'viewport',
        content="width=device-width, initial-scale=1.0" #maximum-scale=1.0
    )]
)
app.title = "Green Algorithms"
server = app.server


# TODO: move towards a utils script
appVersions_options_list = [x for x in os.listdir(data_dir) if ((x[0]=='v')&(x!=current_version))]
appVersions_options_list.sort(reverse=True)
# Add the dev option for testing # TODO make it permanent, with a warning pop up if selected by mistake
# appVersions_options_list.append('dev') # DEBUGONLY

appVersions_options = [{'label': f'{current_version} (latest)', 'value': current_version}] + [{'label': k, 'value': k} for k in appVersions_options_list]

app.layout = html.Div(dash.page_container, id='fullfullPage')

# app.layout = create_appLayout(
#     yesNo_options=yesNo_options,
#     image_dir=image_dir,
#     mapCI=mapCI,
#     appVersions_options=appVersions_options,
# )


#############
# CALLBACKS #
#############


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
        Output('usageCPU_input','value'),
        Output('usageGPU_radio','value'),
        Output('usageGPU_input','value'),
        Output('pue_radio','value'),
        Output('PSF_radio', 'value'),
        Output('PSF_input', 'value'),
        Output('appVersions_dropdown','value'),
        # Output('fillIn_from_url', 'displayed'),
        # Output('fillIn_from_url', 'message'),
    ],
    [
        Input('url_content','search'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('aggregate_data', 'data'),
    ],
)
def filling_from_inputs(url_search, upload_content, filename, current_app_state):


    show_err_mess = False
    mess_content = 'Filling in values from the URL. To edit, click reset at the bottom of the form.'
    return_current_state = False

    defaults2 = copy.deepcopy(default_values)

    # pull default PUE eitherway

    if ctx.triggered_id is None:
        # NB This is needed because of this callback firing for no reason as documented by https://community.plotly.com/t/callback-fired-several-times-with-no-trigger-dcc-location/74525
        # print("-> no-trigger callback prevented") # DEBUGONLY
        raise PreventUpdate # TODO find a cleaner workaround
    
    # only for initial call
    elif 'upload-data.contents' not in ctx.triggered_prop_ids:
        return tuple(default_values.values())   # + (False, '', '')

    elif (url_search is not None)&(url_search != ''):

        # print("\n## picked from url") # DEBUGONLY

        show_err_mess = True

        url = parse.parse_qs(url_search[1:])

        # Load the right dataset to validate the URL inputs
        if 'appVersion' in url:
            new_version = unlist(url['appVersion'])
            # print(f"Validating URL with {new_version} data") # DEBUGONLY
        else:
            # print(f"App version not provided in URL, using default ({default_values['appVersion']})") # DEBUGONLY
            new_version = default_values['appVersion']
        assert new_version in (appVersions_options_list + [current_version])
        if new_version == current_version:
            newData = load_data(os.path.join(data_dir, 'latest'), version=current_version)
        else:
            newData = load_data(os.path.join(data_dir, new_version), version=new_version)

        # Validate URL
        url2, invalidInputs = validateInput(
            input_dict=url,
            data_dict=newData,
            keysOfInterest=list(url.keys())
        )

        defaults2.update((k, url2[k]) for k in defaults2.keys() & url2.keys())

        if len(invalidInputs) > 0:
            mess_content += f'\n\nThere seems to be some typos in this URL, ' \
                            f'using default values for '
            mess_content += f"{', '.join(list(invalidInputs.keys()))}."

        # print(tuple(defaults2.values()) + (show_popup,popup_message)) # DEBUGONLY
        return tuple(defaults2.values()) # + (show_err_mess, mess_content)
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
            defaults2, show_err_mess, mess_subtitle, mess_content = read_csv_input(input_data)
            return tuple(defaults2.values()) # + (show_err_mess, mess_content)  #(show_err_mess, mess_subtitle, mess_content)
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
                current_app_state['provider'],
                current_app_state['usageCPUradio'],
                current_app_state['usageCPU'],
                current_app_state['usageGPUradio'],
                current_app_state['usageGPU'],
                current_app_state['PUEradio'],
                current_app_state['PSFradio'],
                current_app_state['PSF'],
                current_app_state['appVersion'],
                # False,
                # ' '
                # show_err_mess,
                # mess_subtitle,
                # mess_content
            ]
        )

# @app.callback(
#     [
#         Output('runTime_hour_input','disabled'),
#         Output('runTime_min_input','disabled'),
#         Output('coreType_dropdown','disabled'),
#         Output('numberCPUs_input','disabled'),
#         Output('CPUmodel_dropdown', 'disabled'),
#         Output('tdpCPU_input','disabled'),
#         Output('numberGPUs_input','disabled'),
#         Output('GPUmodel_dropdown', 'disabled'),
#         Output('tdpGPU_input','disabled'),
#         Output('memory_input','disabled'),
#         Output('platformType_dropdown','disabled'),
#         Output('provider_dropdown','disabled'),
#         Output('appVersions_dropdown','disabled'),
#         Output('location_continent_dropdown', 'disabled'),
#         Output('location_country_dropdown', 'disabled'),
#         Output('location_region_dropdown', 'disabled'),
#         Output('usageCPU_input','disabled'),
#         Output('usageGPU_input','disabled'),
#         Output('PUE_input','disabled'),
#         Output('PSF_input','disabled'),
#         Output('runTime_hour_input','style'),
#         Output('runTime_min_input','style'),
#         Output('numberCPUs_input','style'),
#         Output('tdpCPU_input','style'),
#         Output('numberGPUs_input','style'),
#         Output('tdpGPU_input','style'),
#         Output('memory_input','style'),
#         Output('usageCPU_radio','options'),
#         Output('usageGPU_radio','options'),
#         Output('pue_radio','options'),
#         Output('PSF_radio', 'options'),
#     ],
#     [
#         Input('url_content','search'),
#     ],
# )
# def disable_inputFromURL(url_search):
#     '''
#     Disable all the input fields when filling in from URL to avoid weird inter-dependancies
#     :param url_search:
#     :return:
#     '''
#     n_output_disable = 20
#     n_output_style = 7
#     n_radio = 4

#     if (url_search is not None) & (url_search != ''):
#         yesNo_options_disabled = [
#             {'label': 'Yes', 'value': 'Yes', 'disabled':True},
#             {'label': 'No', 'value': 'No', 'disabled':True}
#         ]

#         return (True,)*n_output_disable + ({'background-color': MY_COLORS['boxesColor']},)*n_output_style + (yesNo_options_disabled,)*n_radio
#     else:
#         return (False,)*n_output_disable + (dict(),)*n_output_style + (YES_NO_OPTIONS,)*n_radio

@app.callback(
    Output('url_content', 'search'),
    [
        Input('confirm_reset','submit_n_clicks'),
    ]
)
def reset_url(submit_n_clicks):
    '''
    When clicking reset, it reloads a new pages and removes the URL
    :param submit_n_clicks:
    :return:
    '''
    # Other way to do it:
    # changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    # if ('confirm_reset' in changed_id):
    if submit_n_clicks:
        return ""

######
## PLATFORM AND PROVIDER
################

@app.callback(
    Output('platformType_dropdown', 'options'),
    [Input('versioned_data','data')]
)
def set_platform(data):
    if data is not None:
        data_dict = SimpleNamespace(**data)

        platformType_options = [
            {'label': k,
             'value': v} for v, k in list(data_dict.providersTypes.items()) +
                                     [('personalComputer', 'Personal computer')] +
                                     [('localServer', 'Local server')]
        ]
        return platformType_options
    else:
        return []

@app.callback(
    Output('provider_dropdown_div', 'style'),
    [Input('platformType_dropdown', 'value')]
)
def set_providers(selected_platform):
    '''
    Shows or hide the "providers" box, based on the platform selected
    '''
    # print('\n## platformDropdown changed to: ', selected_platform) # DEBUGONLY

    if selected_platform in ['cloudComputing']:
        # Only Cloud Computing need the providers box
        outputStyle = {'display': 'block'}
    else:
        outputStyle = {'display': 'none'}

    return outputStyle

@app.callback(
    Output('provider_dropdown', 'options'),
    [
        Input('platformType_dropdown', 'value'),
        Input('versioned_data','data')
    ],
)
def set_providers(selected_platform, data):
    '''
    List options for the "provider" box
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)

        foo = data_dict.platformName_byType.get(selected_platform)
        if foo is not None:
            availableOptions = list(foo.items())
        else:
            availableOptions = []

        listOptions = [
            {'label': v, 'value': k} for k, v in availableOptions + [("other","Other")]
        ]

        return listOptions
    else:
        return []

######
## COMPUTING CORES
################

@app.callback(
    Output('coreType_dropdown', 'options'),
    [
        Input('provider_dropdown', 'value'),
        Input('platformType_dropdown', 'value'),
        Input('versioned_data','data')
    ])
def set_coreType_options(selected_provider, selected_platform, data):
    '''
    List of options for coreType (CPU or GPU), based on the platform/provider selected
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)

        availableOptions = data_dict.cores_dict.keys()
        listOptions = [{'label': k, 'value': k} for k in list(sorted(availableOptions))+['Both']]
        return listOptions
    else:
        return []


@app.callback(
    [
        Output('CPUmodel_dropdown', 'options'),
        Output('GPUmodel_dropdown', 'options')
    ],
    [Input('versioned_data','data')]
)
def set_coreOptions(data):
    '''
    List of options for core models
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)

        coreModels_options = dict()
        for coreType in ['CPU', 'GPU']:
            availableOptions = sorted(list(data_dict.cores_dict[coreType].keys()))
            availableOptions = put_value_first(availableOptions, 'Any')
            coreModels_options[coreType] = [
                {'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions)) +
                [("Other", "other")]
            ]

        return coreModels_options['CPU'], coreModels_options['GPU']

    else:
        return [],[]


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
        Input('server_dropdown','value'),
        Input('versioned_data','data')
    ]
)
def display_location(selected_platform, selected_provider, selected_server, data):
    '''
    Shows either LOCATION or SERVER depending on the platform
    '''
    if data is not None:
        data_dict = SimpleNamespace(**data)
        providers_withoutDC = data_dict.providers_withoutDC
    else:
        providers_withoutDC = []

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
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('server_continent_dropdown', 'value'),
    ]
)
def set_serverContinents_value(selected_provider, versioned_data, upload_content, filename, prev_server_continent):
    '''
    Default value for server's continent, depending on the provider
    '''

    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to understand which cases
    # may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        # print('in set server continent, when csb flushed')
        # print(prev_server_continent)
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
        # print('prev continent ', prev_server_continent)
        defaultValue = prev_server_continent
        # print('previous continent gives defaultValue being ', defaultValue)
    else:
        try: 
            defaultValue = availableOptions[0]
        except:
            defaultValue = None
    return defaultValue


@app.callback(
    Output('server_continent_dropdown','options'),
    [
        Input('provider_dropdown', 'value'),
        Input('versioned_data','data')
    ]
)
def set_serverContinents_options(selected_provider, data):
    '''
    List of options and default value for server's continent, based on the provider
    '''
    availableOptions = availableLocations_continent(selected_provider, data=data)
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
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('server_dropdown','value'),
    ]
)
def set_server_value(selected_provider, selected_continent, versioned_data, upload_content, filename, prev_server_value):
    '''
    Default value for servers, based on provider and continent
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
        # print('looking for def val in set server', prev_server_value)
        # print([server['name_unique'] for server in availableOptions])
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

@app.callback(
    Output('server_dropdown','options'),
    [
        Input('provider_dropdown', 'value'),
        Input('server_continent_dropdown', 'value'),
        Input('versioned_data','data')
    ]
)
def set_server_options(selected_provider,selected_continent, data):
    '''
    List of options for servers, based on provider and continent
    '''
    availableOptions = availableOptions_servers(selected_provider,selected_continent,data=data)
    listOptions = [{'label': k['Name'], 'value': k['name_unique']} for k in availableOptions + [{'Name':"other", 'name_unique':'other'}]]

    return listOptions

# @app.callback(
#     [
#         Output('server_continent_dropdown','disabled'),
#         Output('server_dropdown','disabled'),
#     ],
#     [
#         Input('server_continent_dropdown','value'),
#         Input('server_dropdown','value'),
#         Input('url_content','search'),
#     ]
# )
# def disable_server_inputs(continent, server, url_search):
#     if (url_search is not None) & (url_search != ''):
#         return True,True
#     else:
#         if (continent=='other')|(server=='other'):
#             return True,True
#         else:
#             return False,False

## LOCATION (only for local server, personal device or "other" cloud server)

@app.callback(
    Output('location_continent_dropdown', 'options'),
    [Input('versioned_data','data')]
)
def set_continentOptions(data):
    if data is not None:
        data_dict = SimpleNamespace(**data)

        continentsList = list(data_dict.CI_dict_byName.keys())
        continentsDict = [{'label': k, 'value': k} for k in sorted(continentsList)]

        return continentsDict
    else:
        return []

@app.callback(
    Output('location_continent_dropdown', 'value'),
    [
        Input('server_continent_dropdown','value'),
        Input('server_div', 'style'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('location_continent_dropdown', 'value'),
        State('versioned_data','data'),
    ]
)
def set_continent_value(selected_serverContinent, display_server, upload_content, filename, prev_locationContinent, versioned_data):

    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to 
    # understand which cases may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        return prev_locationContinent
    
    # We first check wheter the target value is found in the input csv
    if upload_content is not None:
        print('in set continent : the upload-csv')
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
        Output('location_country_dropdown', 'options'),
        Output('location_country_dropdown', 'value'),
        Output('location_country_dropdown_div', 'style'),
    ],
    [
        Input('location_continent_dropdown', 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('location_country_dropdown', 'value')
    ]
)
def set_countries_options(selected_continent, versioned_data, upload_content, filename, prev_selectedCountry):
    '''
    List of options and default value for countries.
    Hides country dropdown if continent=World is selected
    '''
    availableOptions = availableOptions_country(selected_continent, data=versioned_data)
    listOptions = [{'label': k, 'value': k} for k in availableOptions]
    
    defaultValue = None

    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to 
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
        Output('location_region_dropdown', 'options'),
        Output('location_region_dropdown', 'value'),
        Output('location_region_dropdown_div', 'style'),
    ],
    [
        Input('location_continent_dropdown', 'value'),
        Input('location_country_dropdown', 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('location_region_dropdown', 'value'),
    ]

)
def set_regions_options(selected_continent, selected_country, versioned_data, upload_content, filename, prev_selectedRegion):
    '''
    List of options and default value for regions.
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
    # server continent value for the default Value, but it allows to 
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
        # when the country value had previously been set by the user
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


### Usage factor ###

@app.callback(
    Output('usageCPU_input','style'),
    [
        Input('usageCPU_radio', 'value'),
        Input('usageCPU_input', 'disabled')
    ]
)
def display_usage_input(answer_usage, disabled):
    '''
    Show or hide the usage factor input box, based on Yes/No input
    '''

    if answer_usage == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out



@app.callback(
    Output('usageGPU_input','style'),
    [
        Input('usageGPU_radio', 'value'),
        Input('usageGPU_input', 'disabled')
    ]
)
def display_usage_input(answer_usage, disabled):
    '''
    Show or hide the usage factor input box, based on Yes/No input
    '''
    if answer_usage == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out


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

    if selected_platform == 'localServer':
        return {'display': 'flex'}
    elif (selected_platform == 'cloudComputing')&((selected_provider == 'other')|(selected_server == 'other')):
        return {'display': 'flex'}
    else:
        return {'display': 'none'}

@app.callback(
    Output('PUE_input','style'),
    [
        Input('pue_radio', 'value'),
        Input('PUE_input','disabled')
    ]
)
def display_pue_input(answer_pue, disabled):
    '''
    Shows or hides the PUE input box
    '''
    if answer_pue == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out

@app.callback(
    Output('PUE_input','value'),
    [
        Input('pue_radio', 'value'),
        Input('versioned_data','data'),
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
        State('PUE_input','value'),
    ]
)
def set_PUE(radio, versioned_data, upload_content, filename, prev_pue):

    if versioned_data is not None:
        data_dict = SimpleNamespace(**versioned_data)
        defaultPUE = data_dict.pueDefault_dict['Unknown']
    else:
        defaultPUE = 0

    if radio == 'No':
        return defaultPUE
    
    # Handles the case when the upload csv has just been flushed
    # NOTE: this could be handled below when looking for the previous
    # server continent value for the default Value, but it allows to 
    # understand which cases may trigger this callback
    if 'upload-data.contents' in ctx.triggered_prop_ids and upload_content is None:
        defaultPUE = prev_pue

    if upload_content is not None:
        input_data, _, _ = open_input_csv_and_comment(upload_content, filename)
        if input_data:
            target_input, _ = validateInput(input_data, versioned_data, keysOfInterest=['PUE'])
            if target_input :
                defaultPUE = target_input['PUE']

            
    return defaultPUE

### PSF ###

@app.callback(
    Output('PSF_input','style'),
    [
        Input('PSF_radio', 'value'),
        Input('PSF_input', 'disabled')
    ]
)
def display_PSF_input(answer_PSF, disabled):
    '''
    Shows or hides the PSF input box
    '''
    if answer_PSF == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out


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

## CHANGE APP VERSION ##

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
    if (clicks is not None)|((version is not None)&(version != current_version)):
        return {'display':'flex'}
    else:
        return oldStyle

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
    # print('-- version:', newVersion) # DEBUGONLY

    if newVersion is None:
        newVersion = current_version

    assert newVersion in appVersions_options_list + [current_version]

    if newVersion == current_version:
        newData = load_data(os.path.join(data_dir, 'latest'), version = current_version)
        # print('Loading latest data') # DEBUGONLY
    else:
        newData = load_data(os.path.join(data_dir, newVersion), version=newVersion)
        # print(f'Loading {newVersion} data') # DEBUGONLY
    # print(f"CI FR: {newData.CI_dict_byLoc['FR']['carbonIntensity']}") # DEBUGONLY
    # print(f"TPUv3 TDP: {newData.cores_dict['GPU']['TPU v3']}")  # DEBUGONLY

    return vars(newData) # to turn the SimpleNamespace into a dict that can be json serialized

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
        Input('versioned_data','data'),
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
        Input('PUEquestion_div','style'),
        Input("pue_radio", "value"),
        Input("PUE_input", "value"),
        Input("PSF_radio", "value"),
        Input("PSF_input", "value"),
        Input('platformType_dropdown', 'value'),
        Input('provider_dropdown', 'value'),
        Input('provider_dropdown_div', 'style'),
    ],
    # [
    #     State("aggregate_data", "data")
    # ]
)
def aggregate_input_values(data, coreType, n_CPUcores, CPUmodel, tdpCPUstyle, tdpCPU, n_GPUs, GPUmodel, tdpGPUstyle, tdpGPU,
                           memory, runTime_hours, runTime_min, locationContinent, locationCountry, locationRegion,
                           serverContinent, server, locationStyle, serverStyle, usageCPUradio, usageCPU, usageGPUradio, usageGPU,
                           PUEdivStyle, PUEradio, PUE, PSFradio, PSF, selected_platform, selected_provider, providerStyle): #, existing_agg_data):

    # first check if input is provided
    # if 'upload-data.contents' in ctx.triggered_prop_ids:
    #     if input_content is not None:
    #         input_data = read_input_csv(input_content, input_filename)
    #         clean_input_data = {key: value[0] for key, value in input_data.items() if key!='Unnamed: 0'}
    #         return clean_input_data
    #     else:
    #         return existing_agg_data

    # print('in aggregate callback ctx.triggered_prop_ids: ', ctx.triggered_prop_ids)
    output = dict()

    # print('\n## data callback: runTime_hours=', runTime_hours) # DEBUGONLY
    # print("triggered by: ", ctx.triggered_prop_ids) # DEBUGONLY

    permalink = f'http://calculator.green-algorithms.org//'
    # permalink = 'http://127.0.0.1:8050/' # DEBUGONLY
    permalink_temp = ''

    #############################################
    ### PREPROCESS: check if computations can be performed

    notReady = False

    ### Runtime
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

    ### Core type
    if coreType is None:
        notReady = True
    elif (coreType in ['CPU','Both'])&((n_CPUcores is None)|(CPUmodel is None)):
        notReady = True
    elif (coreType in ['GPU','Both'])&((n_GPUs is None)|(GPUmodel is None)):
        notReady = True

    ### Versioned data
    if data is not None:
        data_dict = SimpleNamespace(**data)
        version = data_dict.version
        permalink_temp += f'&appVersion={data_dict.version}'
    else:
        notReady = True

    ### Location
    if is_shown(locationStyle):
        # this means the "location" input is shown, so we use location instead of server
        locationVar = locationRegion
        permalink_temp += f'&locationContinent={locationContinent}&locationCountry={locationCountry}&locationRegion={locationRegion}'
    elif (server is None)|(server == 'other')|(data is None):
        locationVar = None
    else:
        locationVar = data_dict.datacenters_dict_byName[server]['location']
    if is_shown(serverStyle):
        permalink_temp += f'&serverContinent={serverContinent}&server={server}'

    ### Platform
    if selected_platform is None:
        notReady = True
    elif (selected_platform == 'cloudComputing')&(selected_provider is None):
        notReady = True

    ### The rest
    if (memory is None)|(tdpCPU is None)|(tdpGPU is None)|(locationVar is None)| \
            (usageCPU is None)|(usageGPU is None)|(PUE is None)|(PSF is None):
        notReady = True

    if notReady:
        output['coreType'] = None
        output['CPUmodel'] = None
        output['numberCPUs'] = None
        output['usageCPU'] = None
        output['tdpCPU'] = None
        output['GPUmodel'] = None
        output['numberGPUs'] = None
        output['tdpGPU'] = None
        output['usageGPU'] = None
        output['CPUpower'] = None
        output['GPUpower'] = None
        output['memory'] = None
        output['runTime_hour'] = None
        output['runTime_min'] = None
        output['runTime'] = None
        output['platformType'] = None
        output['location'] = None
        output['carbonIntensity'] = None
        output['PUE'] = None
        output['PSF'] = None
        output['carbonEmissions'] = 0
        output['CE_CPU'] = 0
        output['CE_GPU'] = 0
        output['CE_core'] = 0
        output['CE_memory'] = 0
        output['n_treeMonths'] = 0
        output['flying_context'] = 0
        output['nkm_drivingUS'] = 0
        output['nkm_drivingEU'] = 0
        output['nkm_train'] = 0
        output['energy_needed'] = 0
        output['power_needed'] = 0
        output['flying_text'] = None
        output['text_CE'] = '... g CO2e'
        output['appVersion'] = version

    #############################################
    ### PRE-COMPUTATIONS: update variables used in the calcul based on inputs

    else:
        permalink += permalink_temp
        ### PUE
        defaultPUE = data_dict.pueDefault_dict['Unknown']
        # the input PUE is used only if the PUE box is shown AND the radio button is "Yes"
        if (is_shown(PUEdivStyle)) & (PUEradio == 'Yes'):
            PUE_used = PUE
            permalink += f'&PUEradio={PUEradio}&PUE={PUE}'
        
        ### PLATFORM ALONG WITH PUE
        else:
            if selected_platform == 'personalComputer':
                PUE_used = 1
            elif selected_platform == 'localServer':
                PUE_used = defaultPUE
            else:
                # Cloud
                if selected_provider == 'other':
                    PUE_used = defaultPUE
                else:
                    # if we don't know the PUE of this specific data centre, or if we 
                    # don't know the data centre, we use the provider's default
                    server_data = data_dict.datacenters_dict_byName.get(server)
                    if server_data is not None:
                        if pd.isnull(server_data['PUE']):
                            PUE_used = data_dict.pueDefault_dict[selected_provider]
                        else:
                            PUE_used = server_data['PUE']
                    else:
                        PUE_used = data_dict.pueDefault_dict[selected_provider]

        ### CPUs
        permalink += f'&coreType={coreType}'
        if coreType in ['CPU', 'Both']:
            permalink += f'&numberCPUs={n_CPUcores}&CPUmodel={CPUmodel}'
            if is_shown(tdpCPUstyle):
                # we asked the question about TDP
                permalink += f'&tdpCPU={tdpCPU}'
                CPUpower = tdpCPU
            else:
                if CPUmodel == 'other':
                    CPUpower = tdpCPU
                else:
                    CPUpower = data_dict.cores_dict['CPU'][CPUmodel]
            if usageCPUradio == 'Yes':
                permalink += f'&usageCPUradio=Yes&usageCPU={usageCPU}'
                usageCPU_used = usageCPU
            else:
                usageCPU_used = 1.
            powerNeeded_CPU = PUE_used * n_CPUcores * CPUpower * usageCPU_used
        else:
            powerNeeded_CPU = 0
            CPUpower = 0
            usageCPU_used = 0

        if coreType in ['GPU', 'Both']:
            permalink += f'&numberGPUs={n_GPUs}&GPUmodel={GPUmodel}'
            if is_shown(tdpGPUstyle):
                permalink += f'&tdpGPU={tdpGPU}'
                GPUpower = tdpGPU
            else:
                if GPUmodel == 'other':
                    GPUpower = tdpGPU
                else:
                    GPUpower = data_dict.cores_dict['GPU'][GPUmodel]
            if usageGPUradio == 'Yes':
                permalink += f'&usageGPUradio=Yes&usageGPU={usageGPU}'
                usageGPU_used = usageGPU
            else:
                usageGPU_used = 1.
            powerNeeded_GPU = PUE_used * n_GPUs * GPUpower * usageGPU_used
        else:
            powerNeeded_GPU = 0
            GPUpower = 0
            usageGPU_used = 0

        ### MEMORY
        permalink += f'&memory={memory}'

        ### PLATFORM
        permalink += f'&platformType={selected_platform}'
        if is_shown(providerStyle):
            permalink += f'&provider={selected_provider}'

        ### SERVER/LOCATION
        carbonIntensity = data_dict.CI_dict_byLoc[locationVar]['carbonIntensity']

        ### PSF
        if PSFradio == 'Yes':
            permalink += f'&PSFradio=Yes&PSF={PSF}'
            PSF_used = PSF
        else:
            PSF_used = 1

        #############################################
        ### COMPUTATIONS: final outputs are computed

        # Power needed, in Watt
        powerNeeded_core = powerNeeded_CPU + powerNeeded_GPU
        powerNeeded_memory = PUE_used * (memory * data_dict.refValues_dict['memoryPower'])
        powerNeeded = powerNeeded_core + powerNeeded_memory

        # Energy needed, in kWh (so dividing by 1000 to convert to kW)
        energyNeeded_CPU = runTime * powerNeeded_CPU * PSF_used / 1000
        energyNeeded_GPU = runTime * powerNeeded_GPU * PSF_used / 1000
        energyNeeded_core = runTime * powerNeeded_core * PSF_used / 1000
        eneregyNeeded_memory = runTime * powerNeeded_memory * PSF_used / 1000
        energyNeeded = runTime * powerNeeded * PSF_used / 1000

        # Carbon emissions: carbonIntensity is in g per kWh, so results in gCO2
        CE_CPU = energyNeeded_CPU * carbonIntensity
        CE_GPU = energyNeeded_GPU * carbonIntensity
        CE_core = energyNeeded_core * carbonIntensity
        CE_memory  = eneregyNeeded_memory * carbonIntensity
        carbonEmissions = energyNeeded * carbonIntensity

        # Storing all outputs to catch the app state and adapt textual content
        output['coreType'] = coreType
        output['CPUmodel'] = CPUmodel
        output['numberCPUs'] = n_CPUcores
        output['tdpCPU'] = CPUpower
        output['usageCPUradio'] = usageCPUradio
        output['usageCPU'] = usageCPU_used
        output['GPUmodel'] = GPUmodel
        output['numberGPUs'] = n_GPUs
        output['tdpGPU'] = GPUpower
        output['usageGPUradio'] = usageGPUradio
        output['usageGPU'] = usageGPU_used
        output['memory'] = memory
        output['runTime_hour'] = actual_runTime_hours
        output['runTime_min'] = actual_runTime_min
        output['runTime'] = runTime
        output['platformType'] = selected_platform
        output['locationContinent'] = locationContinent
        output['locationCountry'] = locationCountry
        output['locationRegion'] = locationRegion
        output['provider'] = selected_provider
        output['serverContinent'] = serverContinent
        output['server'] = server
        output['location'] = locationVar
        output['carbonIntensity'] = carbonIntensity
        output['PUE'] = PUE_used
        output['PUEradio'] = PUEradio
        output['PSF'] = PSF_used
        output['PSFradio'] = PSFradio
        output['carbonEmissions'] = carbonEmissions
        output['CE_CPU'] = CE_CPU
        output['CE_GPU'] = CE_GPU
        output['CE_core'] = CE_core
        output['CE_memory'] = CE_memory
        output['energy_needed'] = energyNeeded
        output['power_needed'] = powerNeeded
        output['appVersion'] = version

        ### Context
        output['n_treeMonths'] = carbonEmissions / data_dict.refValues_dict['treeYear'] * 12
        output['nkm_drivingUS'] = carbonEmissions / data_dict.refValues_dict['passengerCar_US_perkm']
        output['nkm_drivingEU'] = carbonEmissions / data_dict.refValues_dict['passengerCar_EU_perkm']
        output['nkm_train'] = carbonEmissions / data_dict.refValues_dict['train_perkm']

        ### Text plane trips
        if carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NY-SF']:
            output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_PAR-LON']
            output['flying_text'] = "Paris-London"
        elif carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NYC-MEL']:
            output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NY-SF']
            output['flying_text'] = "NYC-San Francisco"
        else:
            output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NYC-MEL']
            output['flying_text'] = "NYC-Melbourne"

        ### Text carbon emissions
        carbonEmissions_value = carbonEmissions  # in g CO2e
        carbonEmissions_unit = "g"
        if carbonEmissions_value >= 1e6:
            carbonEmissions_value /= 1e6
            carbonEmissions_unit = "T"
        elif carbonEmissions_value >= 1e3:
            carbonEmissions_value /= 1e3
            carbonEmissions_unit = "kg"
        elif carbonEmissions_value < 1:
            carbonEmissions_value *= 1e3
            carbonEmissions_unit = "mg"
        if (carbonEmissions_value != 0)&((carbonEmissions_value >= 1e3)|(carbonEmissions_value < 1)):
            output['text_CE'] = f"{carbonEmissions_value:,.2e} {carbonEmissions_unit} CO2e"
        else:
            output['text_CE'] = f"{carbonEmissions_value:,.2f} {carbonEmissions_unit} CO2e"

        ### Text energy
        energyNeeded_value = energyNeeded  # in kWh
        energyNeeded_unit = "kWh"
        if energyNeeded_value >= 1e3:
            energyNeeded_value /= 1e3
            energyNeeded_unit = "MWh"
        elif energyNeeded_value < 1:
            energyNeeded_value *= 1e3
            energyNeeded_unit = "Wh"
        if (energyNeeded_value != 0) & ((energyNeeded_value >= 1e3) | (energyNeeded_value < 1)):
            output['text_energyNeeded'] = f"{energyNeeded_value:,.2e} {energyNeeded_unit}"
        else:
            output['text_energyNeeded'] = f"{energyNeeded_value:,.2f} {energyNeeded_unit}"

        ### Text tree-months
        treeTime_value = output['n_treeMonths']  # in tree-months
        treeTime_unit = "tree-months"
        if treeTime_value >= 24:
            treeTime_value /= 12
            treeTime_unit = "tree-years"
        if (treeTime_value != 0) & ((treeTime_value >= 1e3) | (treeTime_value < 0.1)):
            output['text_treeYear'] = f"{treeTime_value:,.2e} {treeTime_unit}"
        else:
            output['text_treeYear'] = f"{treeTime_value:,.2f} {treeTime_unit}"

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
    [Input("aggregate_data", "data")],
)
def update_text(data):
    if (data['flying_context'] >= 1)|(data['flying_context'] == 0):
        foo = f"flights {data['flying_text']}"
    else:
        foo = f"of a flight {data['flying_text']}"
    return foo

### INPORT AND EXPORT RESULTS ###

# @app.callback(
#     Output('share_permalink', 'href'),
#     [Input("aggregate_data", "data")],
# )
# def share_permalink(aggData):
#     return f"{aggData['permalink']}"

@app.callback(
    Output('csv-input-timer', 'disabled'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True,
)
def trigger_timer_to_flush_input_csv(input_csv):
    if input_csv is None:
        return True
    return False

@app.callback(
        Output('upload-data', 'contents'),
        Input('csv-input-timer', 'n_intervals'),
        prevent_initial_call=True,
)
def flush_input_csv_content(n):
    return None

@app.callback(
    Output("aggregate-data-csv", "data"),
    Input("btn-download_csv", "n_clicks"),
    State("aggregate_data", "data"),
    prevent_initial_call=True,
)
def export_as_csv(_, aggregate_data):
    to_export_dict = {key: [str(val)] for key, val in aggregate_data.items()}
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    to_export = pd.DataFrame.from_dict(to_export_dict, orient='columns')
    return dcc.send_data_frame(to_export.to_csv, f"GreenAlgorithms_results_{now}.csv", index=False, sep=';')

### UPDATE PIE GRAPH ###
@app.callback(
    Output("pie_graph", "figure"),
    [Input("aggregate_data", "data")],
)
def create_pie_graph(aggData):
    return create_cores_memory_pie_graphic(aggData)

### UPDATE BAR CHART COMPARISON
# FIXME: looks weird with 0 emissions
@app.callback(
    Output("barPlotComparison", "figure"),
    [
        Input("aggregate_data", "data"),
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
        Input("aggregate_data", "data"),
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


### UPDATE THE REPORT TEXT ###

@app.callback(
    Output('report_markdown', 'children'),
    [
        Input("aggregate_data", "data"),
        Input('versioned_data','data')
    ],
)
def fillin_report_text(aggData, data):

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
        (calculated using green-algorithms.org {current_version} \[1\]).
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