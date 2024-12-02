import os
import dash

from dash import html, dcc
from utils.utils import YES_NO_OPTIONS
from utils.graphics import BLANK_FIGURE

import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go

dash.register_page(__name__, path='/', title='Green Algorithms')

def loading_wrapper(component):
    return html.P(dcc.Loading(component, type='circle', color='#96BA6E'))

# SOME GLOBAL VARIABLES
#############################################

image_dir = os.path.join('assets/images')
data_dir = os.path.join(os.path.abspath(''),'data')

current_version = 'v2.2'

appVersions_options_list = [x for x in os.listdir(data_dir) if ((x[0]=='v')&(x!=current_version))]
appVersions_options_list.sort(reverse=True)
appVersions_options = [{'label': f'{current_version} (latest)', 'value': current_version}] + [{'label': k, 'value': k} for k in appVersions_options_list]


def layout(
        mapCI=go.Figure(),
        **query_strings
):
    # clean_inputs = parse_query_strings(query_strings, default_values) 
    appLayout = html.Div(
        [
            dcc.Store(id="versioned_data"),
            dcc.Store(id="aggregate_data"),
            dcc.Location(id='url_content', refresh='callback-nav'), # TODO issue https://github.com/plotly/dash/issues/1346 should be fixed in later releases

            #### POP UP FOR URL + INVALID INPUTS ####

            dcc.ConfirmDialog(
                id='filling_from_csv',
                message='Filling in values from the input csv file.',
                # message=clean_inputs['popup_message'],
                # displayed=clean_inputs['show_popup'],
            ),

            #### HEADER ####

            html.Div(
                [
                    html.H1("Green Algorithms calculator"),
                    html.P("What's the carbon footprint of your computations?"),

                ],
                className='container header'
            ),

            html.Div(
                [
                    html.H2("Some news..."), # TODO align this left?
                    html.P([
                        html.A(
                            "The GREENER principles",
                            href="https://rdcu.be/dfpLM",
                            target="_blank"
                        ),
                        " for environmentally sustainable computational science."
                    ]),
                    html.P([
                        html.A(
                            "A short primer",
                            href="https://www.green-algorithms.org/assets/publications/2023_Comment_NRPM.pdf",
                            target="_blank"
                        ),
                        " discussing different options for carbon footprint estimation."
                    ]),

                    # TODO add something else there? GA4HPC?

                    html.Div(
                        [
                            html.A(
                                html.Button(
                                    'More on the project website!',
                                    id='website-link-button'
                                ),
                                href='https://www.green-algorithms.org',
                                target="_blank",
                                className='button-container'
                            ),

                            # html.A(
                            #     html.Button(
                            #         'Website 2'
                            #     ),
                            #     href='https://www.green-algorithms.org',
                            #     target="_blank",
                            #     className='button-container'
                            # ),
                        ],
                        className='buttons-row'
                    ),
                ],
                className='container footer'
            ),


            #### INPUT FORM ####

            html.Form(
                [
                    html.H2(
                        "Details about your algorithm"
                    ),
                    html.Center(
                        html.P(["To understand how each parameter impacts your carbon footprint, "
                                "check out the formula below and the ",
                                html.A("methods article",
                                       href='https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707',
                                       target='_blank')
                                ]),
                    ),

                    ## RUN TIME
                    html.Div(
                        [
                            html.Label("Runtime (HH:MM)"),

                            html.Div(
                                [
                                    dcc.Input(
                                        type='number',
                                        id="runTime_hour_input",
                                        min=0,
                                    ),

                                    dcc.Input(
                                        type='number',
                                        id="runTime_min_input",
                                        min=0,
                                        max=59,
                                    )
                                ],
                                className="box-runtime box-fields"
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    html.Div(
                        [
                            html.Hr(),
                        ],
                        className='Hr_div'
                    ),

                    ## TYPE OF CORES
                    html.Div(
                        [
                            html.Label("Type of cores"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="coreType_dropdown",
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields"
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Select the type of hardware used.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    ## CPUs
                    html.Div(
                        [
                            html.H3(
                                "CPUs",
                                id='title_CPU'
                            ),

                            html.Div(
                                [
                                    html.Label("Number of cores"),

                                    dcc.Input(
                                        type='number',
                                        id="numberCPUs_input",
                                        min=0,
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "A single CPU contains several cores.",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                ],
                                className='form-row short-input'
                            ),

                            html.Div(
                                [
                                    html.Label("Model"),

                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id="CPUmodel_dropdown",
                                                className='bottom-dropdown',
                                                clearable=False,
                                            ),
                                        ],
                                        className="box-fields"
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "To fill-in a custom core power usage (TDP), please select 'other'.",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                    
                                ],
                                className='form-row short-input'
                            ),

                            # CPU TDP
                            html.Div(
                                [
                                    html.Label(
                                        'What is the Thermal Design Power (TDP) value per core of your CPU? '
                                        'This can easily be found online (usually 10-15W per core)'),

                                    dcc.Input(
                                        type='number',
                                        id="tdpCPU_input",
                                        min=0,
                                    )
                                ],
                                className='form-row',
                                id='tdpCPU_div',
                                style=dict(display='none')
                            ),
                        ],
                        className="group-of-rows",
                        id="CPU_div"
                    ),

                    ## GPUs
                    html.Div(
                        [
                            html.H3(
                                "GPUs",
                                id='title_GPU'
                            ),

                            html.Div(
                                [
                                    html.Label("Number of GPUs"),

                                    dcc.Input(
                                        type='number',
                                        id="numberGPUs_input",
                                        min=0,
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "Here, we ask for the number of GPUs (not the cores).",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                ],
                                className='form-row short-input'
                            ),

                            html.Div(
                                [
                                    html.Label("Model"),

                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id="GPUmodel_dropdown",
                                                className='bottom-dropdown',
                                                clearable=False,
                                            ),
                                        ],
                                        className="box-fields"
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "To fill-in a custom TDP, please select 'other'.",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                ],
                                className='form-row short-input'
                            ),

                            # GPU TDP
                            html.Div(
                                [
                                    html.Label(
                                        'What is the Thermal Design Power (TDP) value per core of your GPU? '
                                        'This can easily be found online (usually around 200W)'),

                                    dcc.Input(
                                        type='number',
                                        id="tdpGPU_input",
                                        min=0,
                                    )
                                ],
                                className='form-row',
                                id='tdpGPU_div',
                                style=dict(display='none')
                            ),
                        ],
                        className="group-of-rows",
                        id="GPU_div"
                    ),

                    html.Div(
                        [
                            html.Hr(),
                        ],
                        className='Hr_div'
                    ),

                    ## MEMORY
                    html.Div(
                        [
                            html.Label("Memory available (in GB)"),

                            dcc.Input(
                                type='number',
                                id="memory_input",
                                min=0,
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "We refer to the ‘allocated memory’, not the memory actually used by the program.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row short-input',
                        id='div_memory'
                    ),

                    html.Div(
                        [
                            html.Hr(),
                        ],
                        className='Hr_div'
                    ),

                    ## SELECT COMPUTING PLATFORM
                    html.Div(
                        [
                            html.Label("Select the platform used for the computations"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="platformType_dropdown",
                                        clearable=False,
                                    ),
                                ],
                                className='box-fields',
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "This field enables us to retrieve the PUE and energy mix associated with your computations.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),    

                            ## SELECT PROVIDER, FOR CLOUD COMPUTING ONLY
                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="provider_dropdown",
                                        clearable=False,
                                        className='bottom-dropdown'
                                    ),
                                ],
                                className="box-fields",
                                id="provider_dropdown_div"
                            ),
                        ],
                        className='form-row'
                    ),


                    ## SERVER (for cloud computing)
                    html.Div(
                        [
                            html.Label("Select server"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="server_continent_dropdown",
                                        clearable=False,
                                    ),

                                    dcc.Dropdown(
                                        id="server_dropdown",
                                        clearable=False,
                                        className='bottom-dropdown',
                                    ),
                                ],
                                className="box-fields"
                            )
                        ],
                        id='server_div',
                        className='form-row',
                        style={'display': 'none'}
                    ),

                    ## LOCATION
                    html.Div(
                        [
                            html.Label("Select location"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="location_continent_dropdown",
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields",
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "In particular, the location is used to retrieve the energy mix.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),   

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="location_country_dropdown",
                                        className='bottom-dropdown',
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields",
                                id="location_country_dropdown_div"
                            ),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="location_region_dropdown",
                                        className='bottom-dropdown',
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields",
                                id="location_region_dropdown_div"
                            ),
                        ],
                        id='location_div',
                        className='form-row',
                        style={'display': 'flex'}
                    ),

                    ## CORE USAGE (CPU and GPU)
                    html.Div(
                        [
                            html.Label("Do you know the real usage factor of your CPU?"),
                            
                            html.Div(
                                [
                                    dcc.RadioItems(
                                        id='usageCPU_radio',
                                        options=YES_NO_OPTIONS,
                                        className="radio-input",
                                    ),
                                    dcc.Input(
                                        min=0,
                                        max=1,
                                        # step=0.1,
                                        type='number',
                                        id="usageCPU_input",
                                        style=dict(display='none'),
                                    )
                                ],
                                className='radio-and-field'
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Between 0 and 1. Should correspond to a temporal factor usage, accessible from log files for instance.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row radio-row',
                        id='usageCPU_div'
                    ),

                    html.Div(
                        [
                            html.Label("Do you know the real usage factor of your GPU?"),
                            html.Div(
                                [
                                    dcc.RadioItems(
                                        id='usageGPU_radio',
                                        options=YES_NO_OPTIONS,
                                        className="radio-input",
                                    ),

                                    dcc.Input(
                                        min=0,
                                        max=1,
                                        # step=0.1,
                                        type='number',
                                        id="usageGPU_input",
                                        style=dict(display='none'),
                                    ),
                                ],
                                className='radio-and-field'
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Between 0 and 1. In most cases, should be 1.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),                            
                        ],
                        className='form-row radio-row',
                        id='usageGPU_div'
                    ),

                    ## PUE
                    html.Div(
                        [
                            html.Label("Do you know the Power Usage Efficiency (PUE) of your local data centre?"),
                            html.Div(
                                [
                                    dcc.RadioItems(
                                        id='pue_radio',
                                        options=YES_NO_OPTIONS,
                                    ),

                                    dcc.Input(
                                        min=1,
                                        type='number',
                                        id="PUE_input",
                                        style=dict(display='none'),
                                    ),
                                ],
                                className='radio-and-field'
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "The PUE accounts for the extra energy consumption of the data centre, including cooling (1.67 by default).",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),

                        ],
                        className='form-row radio-row',
                        id='PUEquestion_div',
                        style=dict(display='none'),
                    ),

                    ## PSF
                    html.Div(
                        [
                            html.Label("Do you want to use a Pragmatic Scaling Factor (PSF)?"),
                            html.Div(
                                [
                                    dcc.RadioItems(
                                        id='PSF_radio',
                                        options=YES_NO_OPTIONS,
                                        className="radio-input",
                                    ),

                                    dcc.Input(
                                        min=1,
                                        type='number',
                                        id="PSF_input",
                                        style=dict(display='none'),
                                    ),
                                ],
                                className='radio-and-field',
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "The PSF refers to the number of repetions of the computation.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),

                        ],
                        className='form-row radio-row',
                    ),

                    dcc.ConfirmDialog(
                        id='confirm_reset',
                        message='This will reset all the values you have entered so far!\n' \
                        'Are you sure you want to continue?',
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.P("Reset", id='reset_link'),
                                ],
                                className='reset-button'
                            ),
                            html.Div(
                                [
                                    html.P("Change app version", id='oldVersion_link'),
                                ],
                                className='reset-button'
                            ),
                        ],
                        className='two-buttons'
                    ),

                    html.Div(
                        [
                            html.Label("App version"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="appVersions_dropdown",
                                        options=appVersions_options,
                                        className='bottom-dropdown',
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields"
                            )
                        ],
                        className='form-row short-input',
                        id='oldVersions_div',
                        style=dict(display='none'),
                    ),

                    html.P(
                        id="placeholder",
                        style={"display": "none"}
                    )

                ],
                className='container input-form'
            ),

            #### FIRST OUTPUTS ####

            html.Div(
                [
                    html.Div(
                        [
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
                            
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            # html.P([
                                            #     html.B("Share your results "),
                                            #     "with ",
                                            #     html.A("this link", target='_blank', id='share_permalink'),
                                            #     ","
                                            # ]),

                                            html.Div([
                                                html.B("Share your results as a "),
                                                html.Button("csv file", id="btn-download_csv"),
                                                dcc.Download(id="aggregate-data-csv"),
                                                html.B(' !')
                                            ])
                                        ],
                                        className='container footer',
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
                                        className='container footer',
                                        style={
                                            'borderWidth': '2px',
                                            'borderStyle': 'dashed',
                                            'borderRadius': '5px',
                                        },
                                        id='import-result',
                                    ),
                                ],
                                className='import-export'
                            ),

                            dbc.Alert(
                                [
                                    html.B('Logs from import (automatic erase after 1min)'),
                                    html.Div(id='log-error-subtitle'),
                                    html.Div(id='log-error-content'),
                                ],
                                id='import-error-message',
                                is_open=False,
                                duration=60000,
                            ),

                        ],
                        className='super-section mini-boxes'
                    ),

                    dcc.Interval(
                        id='csv-input-timer',
                        interval=3000, 
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

                    # html.Center(
                    #     html.P(["This work is being supported by ",
                    #             html.A("here",
                    #                    href='http://www.inouyelab.org/',
                    #                    target='_blank')
                    #             ]),
                    # ),
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

    return appLayout