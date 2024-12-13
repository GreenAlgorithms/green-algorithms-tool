import os
import dash
import datetime

import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go

from dash import ctx, html, dcc, callback, Input, Output, State
from dash.exceptions import PreventUpdate
from types import SimpleNamespace

from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region
from utils.handle_inputs import get_available_versions, validateInput, open_input_csv_and_comment, read_csv_input, DEFAULT_VALUES, CURRENT_VERSION

from utils.graphics import BLANK_FIGURE, loading_wrapper
from utils.graphics import create_cores_bar_chart_graphic, create_ci_bar_chart_graphic, create_cores_memory_pie_graphic

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint


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
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            html.Div(
                                                [
                                                    html.Div(
                                                        [
                                                            html.B("Share your results "),
                                                            html.A(html.B('as a csv file!'), id='btn-download_csv'),
                                                            dcc.Download(id="aggregate-data-csv"),
                                                        ],
                                                    )
                                                ],
                                                className='container footer import-export',
                                                id='export-result',
                                            ),

                                            html.Div(
                                                dcc.Upload(
                                                    html.Div(
                                                        [
                                                            html.B("Import resuts"),
                                                            html.Div(
                                                                [
                                                                    html.A("Drag and drop or click to select your .csv file.")
                                                                ],
                                                                style={'font-size': '12px', 'margin-top': '3px', 'text-decoration': 'underline'}
                                                            )
                                                        ]
                                                    ),
                                                    id='upload-data',
                                                ),
                                                className='container footer import-export',
                                                id='import-result',
                                            ),
                                        ],
                                        id='import-export-buttons'
                                    ),

                                    dbc.Alert(
                                        [
                                            html.B('Filling values from csv: error'),
                                            html.Div(id='log-error-subtitle'),
                                            html.Div(id='log-error-content'),
                                        ],
                                        className = 'container footer import-export',
                                        id='import-error-message',
                                        is_open=False,
                                        duration=60000,
                                    ),

                                ],
                                id='import-export'
                            ),

                            html.Div(
                                [
                                    html.Img(
                                        src=os.path.join(image_dir, 'logo_co2.svg'),
                                        id="logo_co2",
                                        className="style-icon",
                                        style={
                                            'margin-top': '-7px',
                                            'margin-bottom': '7px'
                                        },
                                    ),

                                    html.Div(
                                        [
                                            loading_wrapper(html.Div(
                                                id="carbonEmissions_text",
                                            )),

                                            html.P(
                                                "Carbon footprint",
                                            )
                                        ],
                                        className='caption-icons'
                                    )
                                ],
                                className="container mini-box"
                            ),

                            html.Div(
                                [
                                    html.Img(
                                        src=os.path.join(image_dir, 'logo_power_1.svg'),
                                        id="logo_power",
                                        className="style-icon",
                                        style={
                                            'margin': '0px',
                                            'padding': '15px'
                                        },
                                    ),

                                    html.Div(
                                        [
                                            loading_wrapper(html.Div(
                                                id="energy_text",
                                            )),

                                            html.P(
                                                "Energy needed",
                                            )
                                        ],
                                        className='caption-icons'
                                    )
                                ],
                                className="container mini-box"
                            ),

                            html.Div(
                                [
                                    html.Img(
                                        src=os.path.join(image_dir, 'logo_tree_1.svg'),
                                        id="logo_tree",
                                        className="style-icon",
                                        style={
                                            'padding': '15px'
                                        },
                                    ),

                                    html.Div(
                                        [
                                            loading_wrapper(html.Div(
                                                id="treeMonths_text",
                                            )),

                                            html.P(
                                                "Carbon sequestration"
                                            )
                                        ],
                                        className='caption-icons'
                                    )

                                ],
                                className="container mini-box"
                            ),

                            html.Div(
                                [
                                    html.Img(
                                        src=os.path.join(image_dir, 'logo_car_3.svg'),
                                        id="logo_car",
                                        className="style-icon",
                                        style={
                                            'padding': '13px'
                                        },
                                    ),

                                    html.Div(
                                        [
                                            loading_wrapper(html.Div(
                                                id="driving_text",
                                            )),

                                            html.P(
                                                "in a passenger car",
                                            )
                                        ],
                                        className='caption-icons'
                                    )
                                ],
                                className="container mini-box"
                            ),

                            html.Div(
                                [
                                    html.Img(
                                        src=os.path.join(image_dir, 'logo_plane_1.svg'),
                                        id="logo_plane",
                                        className="style-icon",
                                        style={
                                            'padding': '4px'
                                        },
                                    ),

                                    html.Div(
                                        [
                                            loading_wrapper(html.Div(
                                                id="flying_text",
                                            )),

                                            html.P(
                                                id="flying_label",
                                            ),
                                        ],
                                        className='caption-icons'
                                    )
                                ],
                                className="container mini-box"
                            ),
                        ],
                        className='super-section mini-boxes'
                    ),

                    dcc.Interval(
                        id='csv-input-timer',
                        interval=10000, 
                        # in milliseconds, should not be lower than 1000
                        # otherwise the update of the upload csv content is done too soon
                        # and there is not consistency between the state of the form and 
                        # the content  of the csv
                        disabled=True
                        ),

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

            #### PUBLICATION ####

            html.Div(
                [
                    html.Center(
                        html.P(["More details about the methodology in the ",
                                html.A("methods paper",
                                       href='https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707',
                                       target='_blank'),
                                "."
                                ]),
                    ),
                ],
                className='container footer preprint'
            ),

            #### FORMULA ####

            html.Div(
                [
                    html.H2("The formula"),

                    dcc.Markdown('''
                        The carbon footprint is calculated by estimating the energy draw of the algorithm
                        and the carbon intensity of producing this energy at a given location:

                        `carbon footprint = energy needed * carbon intensity`

                        Where the energy needed is: 

                        `runtime * (cores power draw cores * usage + memory power draw) * PUE * PSF`

                        The power draw of the computing cores depends on the model and number of cores, 
                        while the memory power draw only depends on the size of memory __available__. 
                        The usage factor corrects for the real core usage (default is 1, i.e. full usage).
                        The PUE (Power Usage Effectiveness) measures how much extra energy is needed 
                        to operate the data centre (cooling, lighting etc.). 
                        The PSF (Pragmatic Scaling Factor) is used to take into account multiple identical runs 
                        (e.g. for testing or optimisation).

                        The Carbon Intensity depends on the location and the technologies used to produce electricity.
                        If you want to check out the carbon intensity in real time, and see discrepancies between countries,
                        check out the [ElectricityMap website](https://app.electricitymaps.com/map).
                        Also, note that __the "energy needed" indicated at the top of this page is independent of the location.__
                        ''')
                ],
                className='container formula'
            ),

            #### DEFINITIONS ####

            html.Div(
                [
                    html.Div(
                        [
                            html.H2("About CO2e"),

                            dcc.Markdown('''
                            "Carbon dioxide equivalent" (CO2e) measures 
                            the global warming potential of a mixture of greenhouse gases.
                            __It represents the quantity of CO2 that would have 
                            the same impact on global warming__ as the mix of interest
                            and is used as a standardised unit to assess 
                            the environmental impact of human activities.
                            ''')
                        ],
                        className='container'
                    ),

                    html.Div(
                        [
                            html.H2("What is a tree-month?"),

                            dcc.Markdown('''
                            It's the amount of CO2 sequestered by a tree in a month.
                            __We use it to measure how long it would take to a mature tree
                            to absorb the CO2 emitted by an algorithm.__
                            We use the value of 11 kg CO2/year, which is roughly 1kg CO2/month.
                            '''),
                        ],
                        className='container'
                    ),
                ],
                className='super-section definitions'
            ),

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

            #### WHAT TO DO ####

            # TODO rewrite the "what can you do" section

            # html.Div(
            #     [
            #         html.H2("What can you do about it?"),
            #
            #         dcc.Markdown('''
            #         The main factor impacting your footprint is the location of your servers:
            #         the same algorithm will emit __74 times more__ CO2e
            #         if ran in Australia compared to Switzerland.
            #         Although it's not always the case,
            #         many cloud providers offer the option to select a data centre.
            #
            #         Memory power draw is a huge source of waste,
            #         because __the energy consumption depends on the memory available,
            #         not the actual usage__, only requesting the needed memory
            #         is a painless way to reduce greenhouse gas emissions.
            #
            #         Generally, taking the time to write optimised code that runs faster with fewer
            #         resources saves both money and the planet.
            #
            #         And above all, __only run jobs that you need!__
            #         ''')
            #     ],
            #     className='container to-do'
            # ),

            #### DATA AND Q ####

            # TODO reorganise the footer, it doesn't look great

            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Data and code"),

                            html.Center(
                                html.P(["All the data and code used to run this calculator can be found on ",
                                        html.A("GitHub",
                                               href='https://github.com/GreenAlgorithms/green-algorithms-tool',
                                               target='_blank')
                                        ]),
                            ),
                        ],
                        className='container footer'
                    ),

                    html.Div(
                        [
                            html.H2('Questions / Suggestions?'),

                            html.Center(
                                html.P(["If you have questions or suggestions about the tool, you can ",
                                        html.A("open an issue",
                                               href='https://github.com/GreenAlgorithms/green-algorithms-tool/issues',
                                               target='_blank'),
                                        " on the GitHub or ",
                                        html.A("email us",
                                               href='mailto:green.algorithms@gmail.com', ),
                                        ]),
                            ),
                        ],
                        className='container footer'
                    )
                ],
                className='super-section data-questions'
            ),

            #### HOW TO CITE ####

            html.Div(
                [
                    html.H2("How to cite this work"),

                    html.Center(
                        html.P([
                            "Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. "
                            "Adv. Sci. 2021, 2100707. ",
                            html.A("https://doi.org/10.1002/advs.202100707",
                                   href='https://doi.org/10.1002/advs.202100707',
                                   target='_blank')
                        ]),
                    ),
                ],
                className='container citation footer'
            ),

            #### ABOUT US ####

            html.Div(
                [
                    html.H2("About us"),

                    dcc.Markdown('''
                    The Green Algorithms project is led by

                    [Loïc Lannelongue](www.lannelongue.eu)¹ and [Michael Inouye](https://www.inouyelab.org/home/people)².
                    ''',
                                 className='authors'
                                 ),

                    dcc.Markdown('''
                    (1) University of Cambridge

                    (2) Baker Heart and Diabetes Institute
                    
                    ''',
                                 className='affiliations'
                                 ),
                ],
                className='container about-us footer'
            ),

            #### FUNDERS ####

            # TODO add funders logos

            #### SHOW YOUR STRIPES ####

            html.Div(
                [
                    html.H2("#ShowYourStripes"),

                    html.Center(
                        html.P([html.P(
                            "These coloured stripes in the background represent the change in world temperatures "
                            "from 1850 to 2018. "
                            "This striking design was made by Ed Hawkins from the University of Reading. "),
                            html.P(["More on ",
                                    html.A("ShowYourStipes.info",
                                           href='https://showyourstripes.info',
                                           target='_blank')]),
                            html.P(["Additional credits for the app can be found on the ",
                                    html.A("GitHub",
                                           href='https://github.com/GreenAlgorithms/green-algorithms-tool',
                                           target='_blank'), ])
                        ]),
                    ),
                ],
                className='container show-stripes footer'
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
    if 'upload-data.contents' not in ctx.triggered_prop_ids:
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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
        Input('upload-data', 'contents'),
    ],
    [
        State('upload-data', 'filename'),
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


@HOME_PAGE.callback(
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

@HOME_PAGE.callback(
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

@HOME_PAGE.callback(
    Output("aggregate-data-csv", "data"),
    Input("btn-download_csv", "n_clicks"),
    State(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
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

@HOME_PAGE.callback(
    [
        Output("carbonEmissions_text", "children"),
        Output("energy_text", "children"),
        Output("treeMonths_text", "children"),
        Output("driving_text", "children"),
        Output("flying_text", "children"),
    ],
    [Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data")],
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

@HOME_PAGE.callback(
    Output("flying_label", "children"),
    Input(f'{HOME_PAGE_ID_PREFIX}-aggregate_data', "data"),
)
def update_text(data):
    if (data['flying_context'] >= 1)|(data['flying_context'] == 0):
        foo = f"flights {data['flying_text']}"
    else:
        foo = f"of a flight {data['flying_text']}"
    return foo