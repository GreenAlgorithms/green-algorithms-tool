'''
-*- coding: utf-8 -*-

The current Green Algorithms is a modularized two-pages application fully implemented in Dash. 
The modularization relies on the DashBlueprint class from the dash_extensions.enrich module. 
(https://www.dash-extensions.com/sections/enrich)
Each module <module> is implemented in a function defined in blueprints/<module>/<module>_blueprint.py.
These modules are inserted in the app at the page level (see pages/home.py and pages/ai.py).
They communicate with each other through intermediate variables stored in dcc.Store instances.
The callbacks between these intermediate variables are implemented at the page level too.

To ensure the uniqueness of each component's id, DashBlueprints rely on id prefix.
These prefix are automatically added to the blueprint components' id and 
to the Inputs, Outputs and States of its callbacks. Though, for outer callbacks,
the prefix needs to be manually added to the Inputs, Outputs and State ids.

The only app level variable is the backend data "versioned_data" used to run the calculator.
The "versioned_data" is loaded when the app is launched and then triggers all the callbacks 
that require backend data (cores, server, location, carbon intensity and "equivalent" callbacks).
As the name suggests, this data is versioned to ensure the results replicability accross the
different versions of the app data.

Because of our usage of DashBlueprint, we also implemented the pages as blueprints.
The pages are registered in the app and wrapped within a layout made of the
HTML/Dash components that are common to both pages.

This script generates and runs the app.
'''

import os
import dash
from flask import send_file # Integrating Loader IO

from dash import html, dcc, ctx, _dash_renderer
from dash.dependencies import Input, Output, State
import dash_mantine_components as dmc
_dash_renderer._set_react_version("18.2.0")

from utils.handle_inputs import load_data, CURRENT_VERSION, DATA_DIR, get_available_versions, APP_VERSION_OPTIONS_LIST
from pages.home import HOME_PAGE, HOME_PAGE_ID_PREFIX
from pages.ai import AI_PAGE, AI_PAGE_ID_PREFIX


###################################################
## CREATE APP AND PAGES

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
    # Below tags are to ensure proper responsiveness on mobile devices
    meta_tags=[
        dict(
            name= 'viewport',
            content="width=device-width, initial-scale=1.0" 
        )
    ],
    ############
    # DEBUGONLY: suppress_callback_exceptions = False
    suppress_callback_exceptions=True
    # Callbacks exceptions are removed because otherwise warning messages are raised
    # due to callbacks based on HTML components that are said to be nonexistent
    # whereas they are just implemented on the other app page.
    # In case a callback does not work, allowing callback_exception back
    # may help to find the right fix.
)

app.title = "Green Algorithms"
server = app.server

HOME_PAGE.register(app, module='home', path='/', title='Green Algorithms - Classic view')
AI_PAGE.register(app, module='ai', path='/ai', title='Green Algorithms - AI view')



###################################################
## CREATE NAVBAR

icons_per_page = {'Home': 'fluent-color:home-16', 'Ai': 'streamline:artificial-intelligence-spark'}
name_per_page = {'Home': 'Classic view', 'Ai': 'AI view'}
pages = list(dash.page_registry.values())

appVersions_options = get_available_versions()

pages_navbar = html.Div(
    [
        dmc.NavLink(
            label=html.Div(
                name_per_page[pages[0]['name']],
                className='navlink-label',
                id=f'{pages[0]["name"]}-navlink-label',
            ),
            # Built-in navigation from Dash (see the documentation)
            href=pages[0]["path"],
            id=f'{pages[0]["name"]}-navlink',
            className='page-navlink',
        ),

        # dmc.Divider(orientation="vertical", style={'height': '20', '--divider-color': 'rgb(60, 60, 60)'}),

        dmc.NavLink(
            label=html.Div(
                name_per_page[pages[1]['name']],
                className='navlink-label',
                id=f'{pages[1]["name"]}-navlink-label',
            ),
            # Built-in navigation from Dash (see the documentation)
            href=pages[1]["path"],
            id=f'{pages[1]["name"]}-navlink',
            className='page-navlink',
        ),
    ],
    className = 'pages-menu',
)

versions_choice = html.Div(
    [
        
        html.Div(
            [
                html.Div('i', className='tooltip-icon'),

                html.P(
                    "The calculator data (carbon intensities, hardware...) is regularly updated. If you want to replicate results computed in the past, please select the corresponding data version.",
                    className='tooltip-text'
                ),
            ],
            className='tooltip',
            id='data_version_tooltip'
        ),
        
        html.Div(
            [
                html.P("Change data version", id='old_version_link'),
            ],
            className='change_version_text'
        ),

        html.Div(
            dcc.Dropdown(
                id="app_versions_dropdown",
                options=appVersions_options,
                className='bottom-dropdown',
                clearable=False,
                value=CURRENT_VERSION
            ),
            id='app_versions_dropdown_div',
            style={'display': 'none'},
        )
    ],
    className='form-row short-input',
    id='versions_div',
)



###################################################
## CREATE LAYOUT

app.layout = dmc.MantineProvider(
    html.Div(
        [
            
            #### BACKEND PURPOSE ####

            # Used to forward the version coming from a CSV uploaded to the Home page 
            dcc.Store(id=f"{HOME_PAGE_ID_PREFIX}-version_from_input"),
            # Used to forward the version coming from a CSV uploaded to the Ai page 
            dcc.Store(id=f"{AI_PAGE_ID_PREFIX}-version_from_input"),
            # A dictionnary containing all the backend data used everywhere in the app
            dcc.Store(id="versioned_data"),
            # The component storing the url state, only used to trigger callback when the app is loaded
            dcc.Location(id='url_content', refresh='callback-nav'), 

            #### HEADER ####
            html.Div(
                [
                    html.H1("Green Algorithms calculator"),
                    html.P("What's the carbon footprint of your computations?"),

                    html.Div(
                        [
                            html.Hr(style={'background-color': 'rgb(60, 60, 60)'}),
                        ],
                        className='Hr_div_header',
                    ),

                    pages_navbar,

                    html.Div(
                        [
                            versions_choice,
                        ],
                        className='version_and_language_div'
                    )

                ],
                className='container header'
            ),
            
            # TODO include outstanding issues and PRs

            html.Div(
                [
                    html.H2("Some news..."), # TODO align this left?
                    
                    html.P([
                        "🌱 ",
                        html.B('Interested in green computing?'),
                        " We're recruiting for 2 research roles at the University of Cambridge! ",
                        html.A("More info here", href="https://www.lannelongue-group.org/join/", target="_blank")
                    ]),

                    html.P([
                        "🌱 ",
                        html.B('The new major update of the calculator is here!'),
                        " Possibility to share your results as csv, more guidelines on how to use the tool, "
                        "and the addition of a brand-new AI-specific calculator! ",
                        html.A("Check out the release notes", href="", target="_blank"),
                        " for the full list of new features."
                    ]),

                    html.P([
                        "🐞 It's always possible that some bugs have slipped through the net of this new release... "
                        "If you spot one, just let us know ",
                        html.A("here", href="https://github.com/GreenAlgorithms/green-algorithms-tool/issues", target="_blank"),
                        "."
                    ]),

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

            #### PAGE CONTENT #####
            
            # Pages are registered manually above and their layout is inserted in the app
            # as suggested in the official documentation (https://dash.plotly.com/urls)
            dash.page_container,

            #### FOOTERS #####

            # TODO revisit the footer
        
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
                                        # TODO set up a better green algorithms email redirecting to someone
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
                    [Loïc Lannelongue](www.lannelongue-group.org) and 
                    [Michael Inouye](https://www.inouyelab.org/home/people) at the University of Cambridge,
                    but made possible by the contribution and support of many: 
                    [full list here](https://www.green-algorithms.org/about/)
                    ''',
                    className='authors'
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
)



###################################################
# CALLBACKS #

# These are the few callbacks implemented at the app level, namely
# those related to the version choice and backend data loading, 
# and page navigation.

################## NAVIGATION BAR

@app.callback(
        [
            Output('Home-navlink', 'style'),
            Output('Home-navlink-label', 'style'),
            Output('Ai-navlink', 'style'),
            Output('Ai-navlink-label', 'style'),
        ],
        Input('url_content', 'pathname')
)
def style_navlink(url_pathname: str):
    """ 
    Once the page is changed (built-in page navigation), this
    callback adapts the css of the navigation labels.
    """
    # Define the different styles possibilities
    to_be_clicked_style = {'cursor': 'pointer'}
    to_be_clicked_label_style = {'text-decoration': 'underline', 'font-weight': '200'}
    current_page_navlink_style = {'cursor': 'default'}
    current_page_label_style = {'text-decoration': 'none', 'font-weight': '600'}
    # Allocate the style dictionnaries to the right ouputs
    if 'ai' in url_pathname:
        return to_be_clicked_style, to_be_clicked_label_style, current_page_navlink_style, current_page_label_style
    else:
        return current_page_navlink_style, current_page_label_style, to_be_clicked_style, to_be_clicked_label_style


################## APP VERSIONING

@app.callback(
    Output('app_versions_dropdown','value'),
    [
        Input(f"{HOME_PAGE_ID_PREFIX}-version_from_input",'data'),
        Input(f"{AI_PAGE_ID_PREFIX}-version_from_input",'data'),
    ]
)
def set_version_from_csv_inputs(version_from_home_input: str, version_from_ai_input: str):
    """
    Set the app version based on csv inputs 
    dropped either from the home page or the ai page.
    """
    # We use the ctx.triggered_id to get know which input triggered the callback.
    new_version = None
    if HOME_PAGE_ID_PREFIX in ctx.triggered_id:
        new_version = version_from_home_input
    elif AI_PAGE_ID_PREFIX in ctx.triggered_id:
        new_version = version_from_ai_input
    return new_version

@app.callback(
    Output('app_versions_dropdown_div', 'style'),
    [
        Input('old_version_link','n_clicks'),
        Input('app_versions_dropdown','value')
    ],
    [
        State('app_versions_dropdown_div', 'style')
    ]
)
def display_oldVersion(clicks: int, version: str, oldStyle: dict):
    """
    Show the different available versions.
    """
    if (clicks is not None)|((version is not None)&(version != CURRENT_VERSION)):
        return {'display':'flex', 'flex-direction': 'row', 'width': 'fit-content'}
    else:
        return oldStyle
    
@app.callback(
    Output("versioned_data", "data"),
    [
        # To force initial triggering
        Input('url_content','search'),
        Input('app_versions_dropdown','value'),
    ],
)
def load_data_from_version(_, new_version:str):
    """
    Loads all the backend data required to propose consistent options to the user.
    """
    # Collect input version and check validity
    if new_version is None:
        new_version = CURRENT_VERSION
    assert new_version in APP_VERSION_OPTIONS_LIST + [CURRENT_VERSION]

    # Load corresponding backend data
    if new_version == CURRENT_VERSION:
        new_data = load_data(os.path.join(DATA_DIR, 'latest'), version = CURRENT_VERSION)
    else:
        new_data = load_data(os.path.join(DATA_DIR, new_version), version=new_version)

    return vars(new_data)


# Loader IO
@app.server.route('/loaderio-1360e50f4009cc7a15a00c7087429524/')
def download_loader():
    return send_file('assets/loaderio-1360e50f4009cc7a15a00c7087429524.txt',
                     mimetype='text/plain',
                     attachment_filename='loaderio-1360e50f4009cc7a15a00c7087429524.txt',
                     as_attachment=True)

if __name__ == '__main__':
    app.run_server(debug=True)