import os
import dash

import plotly.graph_objects as go

from dash import ctx, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from types import SimpleNamespace

from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region
from utils.handle_inputs import get_available_versions, filter_wrong_inputs, clean_non_used_inputs_for_export, validateInput, open_input_csv_and_comment, read_csv_input, DEFAULT_VALUES_FOR_PAGE_LOAD, CURRENT_VERSION

from utils.graphics import BLANK_FIGURE, loading_wrapper
from utils.graphics import create_cores_bar_chart_graphic, create_ci_bar_chart_graphic, create_cores_memory_pie_graphic

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.methodology.methodology_blueprint import get_methodology_blueprint
from blueprints.results.results_blueprint import get_results_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint


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
            
            #### PAGE DATA ####

            dcc.Store(id=f'{HOME_PAGE_ID_PREFIX}-aggregate_data'),

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
        Output(f'{HOME_PAGE_ID_PREFIX}-from_input_data', 'data'),
        Output(f'{HOME_PAGE_ID_PREFIX}-import-error-message', 'is_open'),
        Output(f'{HOME_PAGE_ID_PREFIX}-log-error-subtitle', 'children'),
        Output(f'{HOME_PAGE_ID_PREFIX}-log-error-content', 'children'),
        Output(f"{HOME_PAGE_ID_PREFIX}-version_from_input",'data'),
    ],
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-import-content', 'data'),
    ],
    [
        State(f'{HOME_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{HOME_PAGE_ID_PREFIX}-form_aggregate_data', 'data'),
        State('appVersions_dropdown','value'),
    ]
)
def forward_imported_content_to_form(import_data, filename, current_form_data, current_app_version):
    '''
    Processes the raw input dictionnary and checks content before 
    forwarding it to the main page form. 
    '''
    show_err_mess = False
    input_data, mess_subtitle, mess_content = open_input_csv_and_comment(import_data, filename)

    # The input file could not be opened correctly
    if not input_data:
        input_data = current_form_data
        show_err_mess = True
        
        return input_data, show_err_mess, mess_subtitle, mess_content, current_app_version
    
    # If input data could be read, we check its validity and consistency
    else:
        clean_inputs, invalid_inputs, app_version = read_csv_input(input_data)
        invalid_inputs = filter_wrong_inputs(invalid_inputs)
        mess_subtitle = 'Filling in values from the input csv file.'
        mess_content = ''
        if len(invalid_inputs) > 0:
            show_error_mess = True
            mess_content += f'\n\nThere seems to be some typos in the csv columns name or inconsistencies in its values, ' \
                            f'so we use default values for the following fields: \n'
            mess_content += f"{', '.join(list(invalid_inputs.keys()))}." 
        return clean_inputs, show_error_mess, mess_subtitle, mess_content, app_version
    

################## EXPORT RESULTS

@HOME_PAGE.callback(
        Output(f'{HOME_PAGE_ID_PREFIX}-export-content', 'data'),
        Input(f"{HOME_PAGE_ID_PREFIX}-btn-download_csv", "n_clicks"),
        State(f'{HOME_PAGE_ID_PREFIX}-form_aggregate_data', 'data'),
        prevent_initial_call=True,
)
def forward_form_input_to_export_module(_, form_aggregate_data):
    '''
    Intermediate processing specific to the HOME page before exporting data.
    So far, we just forward the inputs of the form to the export file. 
    '''
    form_aggregate_data = clean_non_used_inputs_for_export(form_aggregate_data)
    return form_aggregate_data


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
