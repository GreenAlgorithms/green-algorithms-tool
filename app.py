# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import os
import dash
from flask import send_file # Integrating Loader IO

from dash import html, dcc, ctx, _dash_renderer
from dash.dependencies import Input, Output, State
import dash_mantine_components as dmc
from dash_iconify import DashIconify
_dash_renderer._set_react_version("18.2.0")

from utils.handle_inputs import load_data, CURRENT_VERSION, DATA_DIR
from utils.handle_inputs import APP_VERSION_OPTIONS_LIST

from pages.home import HOME_PAGE, HOME_PAGE_ID_PREFIX
from pages.ai import AI_PAGE, AI_PAGE_ID_PREFIX


###################################################
## CREATE APP

external_stylesheets = [
    # dbc.themes.BOOTSTRAP,
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
            content="width=device-width, initial-scale=1.0" 
        )
    ],
    suppress_callback_exceptions=True
)
app.title = "Green Algorithms"
server = app.server

HOME_PAGE.register(app, module='home', path='/', title='Green Algorithms - Classic view')
AI_PAGE.register(app, module='ai', path='/ai', title='Green Algorithms - AI view')

appVersions_options = [{'label': f'{CURRENT_VERSION} (latest)', 'value': CURRENT_VERSION}] + [{'label': k, 'value': k} for k in APP_VERSION_OPTIONS_LIST]


###################################################
## CREATE NAVBAR

icons_per_page = {'Home': 'fluent-color:home-16', 'Ai': 'streamline:artificial-intelligence-spark'}

name_per_page = {'Home': 'Classic view', 'Ai': 'AI view'}

pages_navbar = html.Div(
    [
        dmc.NavLink(
            label=html.Div(
                name_per_page[page['name']],
                className='navlink-label',
                id=f'{page["name"]}-navlink-label',
            ),
            href=page["path"],
            id=f'{page["name"]}-navlink',
            leftSection=DashIconify(icon=icons_per_page[page['name']], className='navlink-icon', height=20),
            className='page-navlink',
        )
        for page in dash.page_registry.values()
    ],
    className = 'pages-menu',
)

versions_choice = html.Div(
    [
        html.Div(
            [
                html.P("Change app version", id='old_version_link'),
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
            
            dcc.Store(id=f"{HOME_PAGE_ID_PREFIX}-version_from_input"),
            dcc.Store(id=f"{AI_PAGE_ID_PREFIX}-version_from_input"),
            dcc.Store(id="versioned_data"),
            dcc.Location(id='url_content', refresh='callback-nav'), 

            #### HEADER ####
            html.Div(
                [
                    html.H1("Green Algorithms calculator"),
                    html.P("What's the carbon footprint of your computations?"),

                    html.Div(
                        [
                            html.Hr(),
                        ],
                        className='Hr_div_header'
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

            #### PAGE CONTENT #####

            dash.page_container,

        
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
)



###################################################
# CALLBACKS #

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
    to_be_clicked_style = {'cursor': 'pointer'}
    to_be_clicked_label_style = {'text-decoration': 'underline', 'font-weight': '200'}
    current_page_navlink_style = {'cursor': 'default'}
    current_page_label_style = {'text-decoration': 'none', 'font-style': 'italic'}
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
def set_version_from_csv_inputs(version_from_home_input, version_from_ai_input):
    '''
    Set the app version based on csv inputs 
    dropped either from the home page or the ai page.
    '''
    new_version = None
    if HOME_PAGE_ID_PREFIX in ctx.triggered_id:
        new_version = version_from_home_input
    elif AI_PAGE_ID_PREFIX in ctx.triggered_id:
        new_version = version_from_ai_input
    return new_version

    
@app.callback(
    Output("versioned_data", "data"),
    [
        Input('url_content','search'),
        Input('app_versions_dropdown','value'),
    ],
)
def load_data_from_version(_, new_version):
    '''
    Loads all the backend data required to propose consistent options to the user.
    '''
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
def display_oldVersion(clicks, version, oldStyle):
    '''
    Show the different available versions.
    '''
    if (clicks is not None)|((version is not None)&(version != CURRENT_VERSION)):
        return {'display':'flex', 'flex-direction': 'row', 'width': 'fit-content'}
    else:
        return oldStyle



# Loader IO
@app.server.route('/loaderio-1360e50f4009cc7a15a00c7087429524/')
def download_loader():
    return send_file('assets/loaderio-1360e50f4009cc7a15a00c7087429524.txt',
                     mimetype='text/plain',
                     attachment_filename='loaderio-1360e50f4009cc7a15a00c7087429524.txt',
                     as_attachment=True)

if __name__ == '__main__':
    app.run_server(debug=True)