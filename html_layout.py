import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State, ClientsideFunction
import plotly.graph_objects as go

import os

def create_appLayout(platformType_options,
                     yesNo_options,
                     PUE_default,
                     image_dir,
                     mapCI):

    appLayout = html.Div(
        [
            dcc.Store(id="aggregate_data"),

            #### HEADER ####

            html.Div(
                [
                    html.H1("Green Algorithms"),
                    html.P("How green are your computations?"),
                ],
                className='container header'
            ),

            #### INPUT FORM ####

            html.Form(
                [
                    html.H2(
                        "Details about your algorithm"
                    ),

                    html.P("To understand how each parameter impacts your carbon emissions, "
                           "check out the formula below."),

                    ## RUN TIME
                    html.Div(
                        [
                            html.Label("Runtime (hours and minutes)"),

                            html.Div(
                                [
                                    dcc.Input(
                                        type='number',
                                        id="runTime_hour_input",
                                        value=12,
                                    ),

                                    dcc.Input(
                                        type='number',
                                        id="runTime_min_input",
                                        value=0,
                                    )
                                ],
                                className="box-runtime box-fields"
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    ## NUMBER OF CORES
                    html.Div(
                        [
                            html.Label("Number of cores"),

                            dcc.Input(
                                type='number',
                                id="numberCores_input",
                                value=12,
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    ## MEMORY
                    html.Div(
                        [
                            html.Label("Memory requested (in GB)"),

                            dcc.Input(
                                type='number',
                                id="memory_input",
                                value=64,
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    ## SELECT COMPUTING PLATFORM
                    html.Div(
                        [
                            html.Label("Select the platform used for the computations"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="platformType_dropdown",
                                        options=platformType_options,
                                        value='localServer',
                                    ),

                                    dcc.Dropdown(
                                        id="provider_dropdown",
                                        style=dict(display='none'),
                                        className='bottom-dropdown'
                                    )
                                ],
                                className="box-fields"
                            )
                        ],
                        className='form-row'
                    ),

                    ## COMPUTING CORES
                    html.Div(
                        [
                            html.Label("What type of core are you using"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="coreType_dropdown",
                                        value='CPU',
                                    ),

                                    dcc.Dropdown(
                                        id="coreModel_dropdown",
                                        className='bottom-dropdown'
                                    ),
                                ],
                                className="box-fields"
                            )
                        ],
                        className='form-row'
                    ),

                    ## TDP
                    html.Div(
                        [
                            html.Label('What is the Thermal Design Power (TDP) value per core of your processor? '
                                       'This can easily be found online (usually 10-15W for a CPU, 200W for a GPU)'),

                            dcc.Input(
                                type='number',
                                id="tdp_input",
                            )
                        ],
                        className='form-row',
                        id='tdp_div',
                        style=dict(display='none')
                    ),

                    ## LOCATION
                    html.Div(
                        [
                            html.Label("Select location"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id="location_continent_dropdown",
                                        value='North America',
                                    ),

                                    dcc.Dropdown(
                                        id="location_country_dropdown",
                                        value="United States of America",
                                        className='bottom-dropdown'
                                    ),

                                    dcc.Dropdown(
                                        id="location_region_dropdown",
                                        value="US",
                                        className='bottom-dropdown'
                                    ),
                                ],
                                className="box-fields"
                            )
                        ],
                        className='form-row'
                    ),

                    ## PUE
                    html.Div(
                        [
                            html.Label("Do you know the Power Usage Efficiency (PUE) of your local datacentre?"),

                            dcc.RadioItems(
                                id='pue_radio',
                                options=yesNo_options,
                                value='No',
                                className="radio-input"
                                # labelStyle={"display": "inline-block"},
                            ),

                            dcc.Input(
                                min=1,
                                type='number',
                                id="PUE_input",
                                value=PUE_default,
                                style=dict(display='none'),
                            ),
                        ],
                        className='form-row',
                        id='PUEquestion_div',
                        style=dict(display='none'),
                    ),
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
                                            html.P(
                                                id="carbonEmissions_text",
                                            ),

                                            html.P(
                                                "Carbon emissions",
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
                                            html.P(
                                                id="treeMonths_text",
                                            ),

                                            html.P(
                                                "Carbon sequestration",
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
                                            html.P(
                                                id="driving_text",
                                            ),

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
                                            html.P(
                                                id="flying_text",
                                            ),

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

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2(
                                        "Computing cores VS Memory"
                                    ),

                                    dcc.Graph(
                                        id="pie_graph",
                                        className='graph-container pie-graph',
                                    )
                                ],
                                className='one-of-two-graphs'
                            ),

                            html.Div(
                                [
                                    html.H2(
                                        "How the location impacts your footprint"
                                    ),

                                    dcc.Graph(
                                        id="barPlotComparison",
                                        className='graph-container',
                                        style={
                                            'margin-top':'20px'
                                        }
                                    )
                                ],
                                className='one-of-two-graphs'
                            )
                        ],
                        className="container two-graphs-box"
                    ),
                ],
                className='super-section first-output'
            ),

            #### MAP ####

            html.Div(
                [
                    html.H2("Carbon Intensity across the world"),
                    html.Div(
                        [
                            dcc.Graph(
                                figure=mapCI,
                                className='graph',
                            )
                        ],
                        className='graph-container'
                    )

                ],
                className="container map",
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
                            the same impact on the environment__ as the mix of interest
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
                            We use the value of 11.4 kg CO2/year, which is roughly 1kg CO2/month.
                            '''),
                        ],
                        className='container'
                    ),
                ],
                className='super-section definitions'
            ),

            #### CORES COMPARISON ####

            html.Div(
                [
                    html.H2("Power draw of different processors"),

                    html.Div(
                        [
                            dcc.Graph(
                                id="barPlotComparison_cores"
                            ),
                        ],
                        className='graph-container'
                    )
                ],
                className='container core-comparison'
            ),

            #### WHAT TO DO ####

            html.Div(
                [
                    html.H2("What can you do about it?"),

                    dcc.Markdown('''
                    The main factor impacting your footprint is the location of your servers:
                    the same algorithm will emit __64 times more__ CO2e
                    if ran in Australia compared to Switzerland. 
                    Although it's not always the case, 
                    many cloud providers offer the option to select a datacentre.
                    
                    Memory power draw is a huge source of waste: 
                    because __the energy consumption depends on the memory requested, 
                    not the actual usage__, only requesting the needed memory 
                    is a painless way to reduce emissions.  
                    
                    Generally, taking the time to write optimised code that runs faster with fewer 
                    resources saves both money and the planet.
                    
                    And above all, __only run jobs that you need!__
                    ''')
                ],
                className='container to-do'
            ),

            #### FORMULA ####

            html.Div(
                [
                    html.H2("The formula"),

                    dcc.Markdown('''
                    The carbon emissions are calculated by estimating the energy draw of the algorithm
                    and the carbon intensity of producing this energy at a given location:

                    `carbon emissions = energy needed * carbon intensity`

                    Where the energy needed is: 
                    
                    `time * (power draw for computing cores + power draw for memory) * PUE`

                    The power draw for the computing cores depends on the CPU model and number of cores, 
                    while the memory power draw only depends on the size of memory requested.
                    The PUE (Power Usage Effectiveness) measures how much extra energy is needed 
                    to operate the datacentre (cooling, lighting etc.).

                    The Carbon Intensity depends on the location and the technologies used to produce electricity.
                    ''')
                ],
                className='container formula'
            ),

            #### HOW TO REPORT ####

            html.Div(
                [
                    html.H2( "How to report it?"),

                    dcc.Markdown('''
                    It's important to track the impact 
                    of computational research on climate change in order to stimulate greener algorithms.
                    For that, __we believe that the carbon footprint of a project should be reported on articles
                    alongside other performance metrics__. 
                    
                    Here is an example you can include in your paper:
                    '''),

                    dcc.Markdown(id='report_markdown')
                ],
                className='container report'
            ),

            #### DATA AND Q ####

            html.Div(
                [
                    html.Div(
                        [
                            html.H2("The data"),

                            dcc.Markdown('''
                            All the data used to run this calculator can be found 
                            on [github](https://github.com/green-algorithms/project).
                             '''),
                        ],
                        className='container footer'
                    ),

                    html.Div(
                        [
                            html.H2('Questions / Suggestions?'),

                            dcc.Markdown('''
                            The app is still under development and new data and features are coming soon.
    
                            You can reach out to us here: [green.algorithms@gmail.com](mailto:green.algorithms@gmail.com) 
                            ''')
                        ],
                        className='container footer'
                    )
                ],
                className='super-section data-questions'
            ),

            #### ABOUT US ####

            html.Div(
                [
                    html.H2("About us"),

                    dcc.Markdown('''
                    The Green Algorithms project was jointly developed by

                    Loïc Lannelongue¹, Jason Grealey², and Michael Inouye³
                    ''',
                     className='authors'
                     ),

                    dcc.Markdown('''
                    (1) University of Cambridge

                    (2) Baker Heart and Diabetes Institute and La Trobe University

                    (3) Baker Institute, University of Cambridge, Alan Turing Institute, Health Data Research UK
                    ''',
                    className='affiliations'
                    ),

                    dcc.Markdown('''
                    More information [here](http://www.inouyelab.org/)
                     ''')
                ],
                className='container about-us footer'
            ),

            #### SHOW YOUR STRIPES ####

            html.Div(
                [
                    html.H2("#ShowYourStripes"),

                    dcc.Markdown('''
                    These coloured stripes in the background represent the change in world temperatures
                    from 1850 to 2018.
                    This striking design has been made by Ed Hawkins from the University of Reading.

                    More on [ShowYourStipes.info](https://showyourstripes.info)
                    
                    Additional credits can be found on the [github](https://github.com/green-algorithms/project).
                    ''')
                ],
                className='container show-stripes footer'
            ),

        ],
        className='fullPage'
    )

    return appLayout