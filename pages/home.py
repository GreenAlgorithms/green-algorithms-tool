import os
import dash

import plotly.graph_objects as go

from dash import ctx, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from types import SimpleNamespace

from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region
from utils.handle_inputs import get_available_versions, validateInput, open_input_csv_and_comment, read_csv_input, DEFAULT_VALUES, CURRENT_VERSION

from utils.graphics import BLANK_FIGURE, loading_wrapper
from utils.graphics import create_cores_bar_chart_graphic, create_ci_bar_chart_graphic, create_cores_memory_pie_graphic

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.methodology.methodology_blueprint import get_methodology_blueprint
from blueprints.results.results_blueprint import get_results_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint


# dash.register_page(__name__, path='/', title='Green Algorithms')

HOME_PAGE = DashBlueprint()

HOME_PAGE_ID_PREFIX = 'main'

form = get_form_blueprint(
    id_prefix = HOME_PAGE_ID_PREFIX,
    title = "Details about your algorithm",
    subtitle = html.P(
        [
            "To understand how each parameter impacts your carbon footprint, "
            "check out the formula below and the ",
            html.A(
                "methods article",
                href='https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707',
                target='_blank'
            )
        ]
    )
)

methodology_content = get_methodology_blueprint(id_prefix=HOME_PAGE_ID_PREFIX)

results = get_results_blueprint(id_prefix=HOME_PAGE_ID_PREFIX)

import_export = get_import_expot_blueprint(id_prefix=HOME_PAGE_ID_PREFIX) 


###################################################
# SOME GLOBAL VARIABLES

image_dir = os.path.join('assets/images')
data_dir = os.path.join(os.path.abspath(''),'data')

appVersions_options = get_available_versions()
# form_ids = GreenAlgoFormIDS()


###################################################
# DEFINE APP LAYOUT

def get_home_page_layout():
    page_layout = html.Div(
        [

            #### INPUT FORM ####

            form.embed(HOME_PAGE),

            #### FIRST OUTPUTS ####

            html.Div(
                [
                    import_export.embed(HOME_PAGE),

                    results.embed(HOME_PAGE),

            #### DYNAMIC GRAPHS ####
        
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        "Computing cores VS Memory"
                                    ),
                                    loading_wrapper(
                                        dcc.Graph(
                                            id="pie_graph",
                                            className='graph-container pie-graph',
                                            config={'displaylogo': False},
                                            figure=BLANK_FIGURE,
                                        )
                                    ),

                                ],
                                className='one-of-two-graphs'
                            ),

                            html.Div(
                                [
                                    html.H2(
                                        "How the location impacts your footprint"
                                    ),

                                    loading_wrapper(
                                        dcc.Graph(
                                            id="barPlotComparison",
                                            className='graph-container',
                                            config={'displaylogo': False},
                                            figure=BLANK_FIGURE,
                                            style={
                                                'margin-top': '20px'
                                            }
                                        ),
                                    ),

                                ],
                                className='one-of-two-graphs'
                            )
                        ],
                        className="container two-graphs-box"
                    ),
                ],
                className='super-section first-output'
            ),
            
            #### METHODOLOGY CONTENT ####

            methodology_content.embed(HOME_PAGE),

            #### HOW TO REPORT ####

            html.Div(
                [
                    html.H2("How to report it?"),

                    dcc.Markdown('''
            It's important to track the impact 
            of computational research on climate change in order to stimulate greener algorithms.
            For that, __we believe that the carbon footprint of a project should be reported on publications
            alongside other performance metrics__. 

            Here is a text you can include in your paper:
            '''),

                    dcc.Markdown(id='report_markdown'),

                    dcc.Markdown(
                        # '\[1\] see citation below',
                        '\[1\] Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. Adv. Sci. 2021, 2100707.',
                        className='footnote citation-report'
                    ),

                    dcc.Markdown(
                        '_Including the version of the tool is useful to keep track of the version of the data used._',
                        className='footnote-authorship'
                    )

                ],
                className='container report'
            ),

            #### CORES COMPARISON ####

            html.Div(
                [
                    html.H2("Power draw of different processors"),

                    html.Div(
                        [
                            loading_wrapper(
                                dcc.Graph(
                                    id="barPlotComparison_cores",
                                    config={'displaylogo': False},
                                    figure=BLANK_FIGURE,
                                ),
                            ),
                        ],
                        className='graph-container'
                    )
                ],
                className='container core-comparison'
            ),

        ],
        className='fullPage'
        


    )

    return page_layout

HOME_PAGE.layout = get_home_page_layout()

###################################################
# DEFINE CALLBACKS


################## LOAD PAGE AND INPUTS

@HOME_PAGE.callback(
    [
        ##################################################################
        ## WARNING: do not modify the order, unless modifying the order
        ## of the DEFAULT_VALUES accordingly
        Output(f'{HOME_PAGE_ID_PREFIX}-runTime_hour_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-runTime_min_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-coreType_dropdown','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-numberCPUs_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-CPUmodel_dropdown', 'value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-tdpCPU_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-numberGPUs_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-GPUmodel_dropdown', 'value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-tdpGPU_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-memory_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-platformType_dropdown','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-usageCPU_radio','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-usageCPU_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-usageGPU_radio','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-usageGPU_input','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-pue_radio','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-PSF_radio', 'value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-PSF_input', 'value'),
        Output('appVersions_dropdown','value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-import-error-message', 'is_open'),
        Output(f'{HOME_PAGE_ID_PREFIX}-log-error-subtitle', 'children'),
        Output(f'{HOME_PAGE_ID_PREFIX}-log-error-content', 'children'),
    ],
    [
        Input('url_content','search'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', 'data'),
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
    if 'main-upload-data.contents' not in ctx.triggered_prop_ids:
        return tuple(DEFAULT_VALUES.values()) + (False, '', '')

    # First we deal with the case the input_csv has just been flushed
    # Then we want to fill in the form with its current state
    if upload_content is None:
        if current_app_state is None:
            return tuple(DEFAULT_VALUES.values()) + (False, '', '')
        else:
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
    

@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-provider_dropdown','value'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-platformType_dropdown', 'value'),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-provider_dropdown', 'value'),
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

@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-server_continent_dropdown','value'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-provider_dropdown', 'value'),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-server_continent_dropdown', 'value'),
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


@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-server_dropdown','value'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-provider_dropdown', 'value'),
        Input(f'{HOME_PAGE_ID_PREFIX}-server_continent_dropdown', 'value'),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-server_dropdown','value'),
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


@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-location_continent_dropdown', 'value'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-server_continent_dropdown','value'),
        Input(f'{HOME_PAGE_ID_PREFIX}-server_div', 'style'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-location_continent_dropdown', 'value'),
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

@HOME_PAGE.callback(
    [
        Output(f'{HOME_PAGE_ID_PREFIX}-location_country_dropdown', 'options'),
        Output(f'{HOME_PAGE_ID_PREFIX}-location_country_dropdown', 'value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-location_country_dropdown_div', 'style'),
    ],
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-location_continent_dropdown', 'value'),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-location_country_dropdown', 'value')
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

@HOME_PAGE.callback(
    [
        Output(f'{HOME_PAGE_ID_PREFIX}-location_region_dropdown', 'options'),
        Output(f'{HOME_PAGE_ID_PREFIX}-location_region_dropdown', 'value'),
        Output(f'{HOME_PAGE_ID_PREFIX}-location_region_dropdown_div', 'style'),
    ],
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-location_continent_dropdown', 'value'),
        Input(f'{HOME_PAGE_ID_PREFIX}-location_country_dropdown', 'value'),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-location_region_dropdown', 'value'),
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


@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-PUE_input','value'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-pue_radio', 'value'),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'contents'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-PUE_input','value'),
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


    ##################### RESET ###

@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-confirm_reset','displayed'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-reset_link','n_clicks')
    ]
)
def display_confirm(clicks):
    '''
    Display a popup asking for reset confirmation.
    '''
    if clicks is not None:
        return True
    return False


## OUTPUT GRAPHICS
#################

@HOME_PAGE.callback(
    Output("pie_graph", "figure"),
    Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
)
def create_pie_graph(aggData):
    return create_cores_memory_pie_graphic(aggData)

### UPDATE BAR CHART COMPARISON
# FIXME: looks weird with 0 emissions
@HOME_PAGE.callback(
    Output("barPlotComparison", "figure"),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart(aggData, data):
    if data is not None:
        data_dict = SimpleNamespace(**data)
        return create_ci_bar_chart_graphic(aggData, data_dict)
    return None

### UPDATE BAR CHARTCPU
@HOME_PAGE.callback(
    Output("barPlotComparison_cores", "figure"),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
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

@HOME_PAGE.callback(
    Output('report_markdown', 'children'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
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

# @HOME_PAGE.callback(
#     Output(f'{HOME_PAGE_ID_PREFIX}-res_aggregate_data', 'data'),
#     Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
# )
# def update_text(data):
#     return {
#             'text_CE': data.get('text_CE'),
#             'text_energyNeeded': data.get('text_energyNeeded'),
#             'text_treeYear': data.get('text_treeYear'),
#             'nkm_drivingEU': data.get('nkm_drivingEU'),
#             'flying_context': data.get('flying_context'),
#             'flying_text': data.get('flying_text'),
#     }
