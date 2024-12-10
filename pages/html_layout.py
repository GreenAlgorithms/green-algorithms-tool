import os
import dash

from dash import html, dcc
from utils.handle_inputs import get_available_versions
from utils.graphics import BLANK_FIGURE

from all_in_one_components.form.green_algo_form_AIO import GreenAlgoFormAIO, ID_MAIN_FORM

import dash_bootstrap_components as dbc

dash.register_page(__name__, path='/', title='Green Algorithms')

def loading_wrapper(component):
    return html.P(dcc.Loading(component, type='circle', color='#96BA6E'))

# SOME GLOBAL VARIABLES
#############################################

image_dir = os.path.join('assets/images')
data_dir = os.path.join(os.path.abspath(''),'data')

appVersions_options = get_available_versions()

# DEFINE APP LAYOUT
###################

def layout(**query_strings):
    appLayout = html.Div(
        [
            dcc.Store(id="versioned_data"),
            dcc.Store(id="aggregate_data"),
            dcc.Location(id='url_content', refresh='callback-nav'), # TODO issue https://github.com/plotly/dash/issues/1346 should be fixed in later releases

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
                        ],
                        className='buttons-row'
                    ),
                ],
                className='container footer'
            ),


            #### INPUT FORM ####

            GreenAlgoFormAIO(ID_MAIN_FORM),

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

    return appLayout