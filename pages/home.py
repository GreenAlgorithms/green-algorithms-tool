'''
The page itself is defined as a DashBlueprint that encompasses both layout and callbacks.

The layout is a combination Dash components directly implemented in this script and 
modules' layout inserted as blueprints (the form, import-export section or results section).
Such modules also contain their own callbacks that will first be registered as page callbacks 
and then, when the page is registered in the app, as app callbacks.
'''

import os

import plotly.graph_objects as go

from dash import html, dcc, Input, Output, State
from types import SimpleNamespace

from utils.handle_inputs import get_available_versions, filter_wrong_inputs, clean_non_used_inputs_for_export, open_input_csv_and_comment, read_base_form_inputs_from_csv
from utils.graphics import BLANK_FIGURE, loading_wrapper
from utils.graphics import create_cores_bar_chart_graphic, create_ci_bar_chart_graphic, create_cores_memory_pie_graphic

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.methodology.methodology_blueprint import get_methodology_blueprint
from blueprints.metrics.metrics_blueprint import get_metrics_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint


###################################################
# PAGE CREATION

HOME_PAGE = DashBlueprint()

HOME_PAGE_ID_PREFIX = 'main'


###################################################
# MODULES CREATION

# TODO add a "help" tab on the home form as well (similar to the AI one)
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

metrics = get_metrics_blueprint(id_prefix=HOME_PAGE_ID_PREFIX)

import_export = get_import_expot_blueprint(id_prefix=HOME_PAGE_ID_PREFIX) 


###################################################
# SOME GLOBAL VARIABLES

image_dir = os.path.join('assets/images')
data_dir = os.path.join(os.path.abspath(''),'data')

appVersions_options = get_available_versions()


###################################################
# DEFINE PAGE LAYOUT

def get_home_page_layout():
    page_layout = html.Div(
        [

            #### INPUT FORM ####

            form.embed(HOME_PAGE),

            #### IMPORT-EXPORT AND FIRST OUTPUTS ####

            html.Div(
                [
                    import_export.embed(HOME_PAGE),

                    metrics.embed(HOME_PAGE),

            #### DYNAMIC GRAPHS ####
        
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2("Computing cores VS Memory"),

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

                    dcc.Markdown(
                        '''
                        It's important to track the impact 
                        of computational research on climate change in order to stimulate greener algorithms.
                        For that, __we believe that the carbon footprint of a project should be reported on publications
                        alongside other performance metrics__. 

                        Here is a text you can include in your paper:
                        '''
                    ),

                    dcc.Markdown(id='report_markdown'),

                    dcc.Markdown(
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
        className='page_content'

    )

    return page_layout

HOME_PAGE.layout = get_home_page_layout()


###################################################
# DEFINE CALLBACKS

################## LOAD PAGE AND INPUTS

@HOME_PAGE.callback(
    [
        Output(f'{HOME_PAGE_ID_PREFIX}-form_data_imported_from_csv', 'data'),
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
        State('app_versions_dropdown','value'),
    ]
)
def forward_imported_content_to_form(import_data, filename, current_form_data, current_app_version):
    '''
    Processes the raw input dictionnary and checks content before 
    forwarding it to the main page form. 
    Produces error messages depending on the csv content.
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
        clean_inputs, invalid_inputs, app_version = read_base_form_inputs_from_csv(input_data)
        invalid_inputs = filter_wrong_inputs(clean_inputs, invalid_inputs)
        mess_subtitle = 'Filling in values from the input csv file.'
        mess_content = ''
        if len(invalid_inputs) > 0:
            show_err_mess = True
            mess_content += f'\n\nThere seems to be some typos in the csv columns name or inconsistencies in its values, ' \
                            f'so we use default values for the following fields: \n'
            mess_content += f"{', '.join(list(invalid_inputs.keys()))}." 
        return clean_inputs, show_err_mess, mess_subtitle, mess_content, app_version
    

################## EXPORT DATA

@HOME_PAGE.callback(
        Output(f'{HOME_PAGE_ID_PREFIX}-export-content', 'data'),
        Input(f"{HOME_PAGE_ID_PREFIX}-btn-download_csv", "n_clicks"),
        State(f'{HOME_PAGE_ID_PREFIX}-form_aggregate_data', 'data'),
        State(f'{HOME_PAGE_ID_PREFIX}-form_output_metrics', "data"),
        prevent_initial_call=True,
)
def forward_form_input_to_export_module(_, form_aggregate_data, form_output_metrics):
    '''
    Intermediate processing specific to the HOME page before exporting data.
    We forward the inputs of the form to the export file along with the main outputs. 
    '''
    to_export = {}
    # Raw inputs of the form
    form_aggregate_data = clean_non_used_inputs_for_export(form_aggregate_data)
    to_export.update(form_aggregate_data)
    # Outputs of the form
    to_export.update(form_output_metrics)
    return to_export


################## RESULTS AND METRICS 

@HOME_PAGE.callback(
    Output(f'{HOME_PAGE_ID_PREFIX}-base_results', 'data'),
    Input(f'{HOME_PAGE_ID_PREFIX}-form_output_metrics', 'data')
)
def forward_results_from_form_to_metrics(form_metrics):
    return {
        'energy_needed': form_metrics['energy_needed'],
        'carbonEmissions': form_metrics['carbonEmissions'],
    }

## OUTPUT GRAPHICS

@HOME_PAGE.callback(
    Output("pie_graph", "figure"),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-form_aggregate_data', "data"),
        Input(f'{HOME_PAGE_ID_PREFIX}-form_output_metrics', "data"),
    ]
)
def create_pie_graph(form_agg_data, form_metrics):
    return create_cores_memory_pie_graphic(form_agg_data, form_metrics)

# FIXME: looks weird with 0 emissions
@HOME_PAGE.callback(
    Output("barPlotComparison", "figure"),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-form_output_metrics', "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart(form_metrics, versioned_data):
    if versioned_data is not None:
        versioned_data = SimpleNamespace(**versioned_data)
        return create_ci_bar_chart_graphic(form_metrics, versioned_data)
    return None

@HOME_PAGE.callback(
    Output("barPlotComparison_cores", "figure"),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-form_aggregate_data', "data"),
        Input('versioned_data','data')
    ],
)
def create_bar_chart_cores(form_agg_data, versioned_data):
    if versioned_data is not None:
        versioned_data = SimpleNamespace(**versioned_data)
        if form_agg_data['coreType'] is None:
            return go.Figure()
        return create_cores_bar_chart_graphic(form_agg_data, versioned_data)
    return None

## OUTPUT SUMMARY

@HOME_PAGE.callback(
    Output('report_markdown', 'children'),
    [
        Input(f'{HOME_PAGE_ID_PREFIX}-form_aggregate_data', "data"),
        Input('versioned_data','data'),
        Input(f'{HOME_PAGE_ID_PREFIX}-energy_text', 'children'),
        Input(f'{HOME_PAGE_ID_PREFIX}-carbonEmissions_text', 'children'),
        Input(f'{HOME_PAGE_ID_PREFIX}-treeMonths_text', 'children'),
    ],
)
def fillin_report_text(form_agg_data, versioned_data, text_CE, text_energy, text_ty):
    '''
    Writes a summary text of the current computation that is shown as an example
    for the user on how to report its impact.
    '''
    if (form_agg_data['numberCPUs'] is None)&(form_agg_data['numberGPUs'] is None):
        return('')
    elif versioned_data is None:
        return ('')
    else:
        versioned_data = SimpleNamespace(**versioned_data)

        # Text runtime
        minutes = form_agg_data['runTime_min']
        hours = form_agg_data['runTime_hour']
        if (minutes > 0)&(hours>0):
            textRuntime = "{}h and {}min".format(hours, minutes)
        elif (hours > 0):
            textRuntime = "{}h".format(hours)
        else:
            textRuntime = "{}min".format(minutes)

        # text cores
        textCores = ""
        if form_agg_data['coreType'] in ['GPU','Both']:
            if form_agg_data['numberGPUs'] > 1:
                suffixProcessor = 's'
            else:
                suffixProcessor = ''
            textCores += f"{form_agg_data['numberGPUs']} GPU{suffixProcessor} {form_agg_data['GPUmodel']}"
        if form_agg_data['coreType'] == 'Both':
            textCores += " and "
        if form_agg_data['coreType'] in ['CPU','Both']:
            if form_agg_data['numberCPUs'] > 1:
                suffixProcessor = 's'
            else:
                suffixProcessor = ''
            textCores += f"{form_agg_data['numberCPUs']} CPU{suffixProcessor} {form_agg_data['CPUmodel']}"

        country = versioned_data.CI_dict_byLoc[form_agg_data['location']]['countryName']
        region = versioned_data.CI_dict_byLoc[form_agg_data['location']]['regionName']

        if region == 'Any':
            textRegion = ''
        else:
            textRegion = ' ({})'.format(region)

        if country in ['United States of America', 'United Kingdom']:
            prefixCountry = 'the '
        else:
            prefixCountry = ''

        if form_agg_data['mult_factor'] > 1:
            text_mult_factor = ' and ran {} times in total,'.format(form_agg_data['mult_factor'])
        else:
            text_mult_factor = ''

        myText = f'''
        > This algorithm runs in {textRuntime} on {textCores},
        > and draws {text_energy}. 
        > Based in {prefixCountry}{country}{textRegion},{text_mult_factor} this has a carbon footprint of {text_CE}, which is equivalent to {text_ty}
        (calculated using green-algorithms.org {form_agg_data['appVersion']} \[1\]).
        '''

        return myText

