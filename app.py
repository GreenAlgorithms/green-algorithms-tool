# -*- coding: utf-8 -*-
#currently running on Python 3.7.4

import os
import dash

from dash import html, dcc
from dash.dependencies import Input, Output, State

from flask import send_file # Integrating Loader IO

import dash_bootstrap_components as dbc

from utils.handle_inputs import load_data, CURRENT_VERSION, DATA_DIR
from utils.handle_inputs import APP_VERSION_OPTIONS_LIST


###################################################
## CREATE APP

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
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
            content="width=device-width, initial-scale=1.0" #maximum-scale=1.0
        )
    ]
)
app.title = "Green Algorithms"
server = app.server
appVersions_options = [{'label': f'{CURRENT_VERSION} (latest)', 'value': CURRENT_VERSION}] + [{'label': k, 'value': k} for k in APP_VERSION_OPTIONS_LIST]


###################################################
## CREATE LAYOUT

pages_dropdown = dbc.DropdownMenu(
    [
        dbc.DropdownMenuItem(
            children=html.Div(
                [
                    html.Img(
                        src=app.get_asset_url(page["image"]),
                        height="20px",
                        width="20px",
                        style={'padding-right': '5px'}
                    ),
                    page["name"],
                ]
            ),
            href=page["path"],
            style={'align-item': 'center'}
        )
        for page in dash.page_registry.values()
    ],
    nav=True,
    label="More Pages",
)


navbar = dbc.Navbar(
    dbc.Container(
        [
            html.A(
                # Use row and col to control vertical alignment of logo / brand
                dbc.Row(
                    [
                        dbc.Col(
                            html.Img(src=app.get_asset_url("favicon.ico"), height="50px")
                        ),
                        dbc.Col(dbc.NavbarBrand("Navbar", className="ms-2")),
                    ],
                    align="center",
                    className="g-0",
                ),
            ),

            html.Div(
                [
                    html.P("Change app version", id='oldVersion_link'),
                ],
                className='reset-button'
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

            pages_dropdown,
        ],
        fluid=True,
    ),
)



app.layout = html.Div(
    [
        
        #### BACKEND PURPOSE ####
        
        dcc.Store(id="versioned_data"),
        dcc.Location(id='url_content', refresh='callback-nav'), 
        
        #### NAVBAR ####

        html.Div(navbar, id='navbar-container'),

        #### HEADER ####
        html.Div(
            [
                html.Div(
                    [
                        html.H1("Green Algorithms calculator"),
                        html.P("What's the carbon footprint of your computations?"),

                    ],
                    className='container header'
                ),
            ],
            style={'justify-content': 'center', 'display': 'flex', 'flex-direction': 'row'}
        ),

        html.Div(
            [

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
            ],
            style={'justify-content': 'center', 'display': 'flex', 'flex-direction': 'row'}
        ),

        #### PAGE CONTENT #####

        dash.page_container
    ],
    # style={'justify-content': 'space-between', 'display': 'flex', 'flex-direction': 'column'},
    id='fullfullPage'
)



###################################################
# CALLBACKS #

    
@app.callback(
    Output("versioned_data", "data"),
    [
        Input('appVersions_dropdown','value')
    ],
)
def loadDataFromVersion(newVersion):
    '''
    Loads all the backend data required to propose consistent options to the user.
    '''
    if newVersion is None:
        newVersion = CURRENT_VERSION
    assert newVersion in APP_VERSION_OPTIONS_LIST + [CURRENT_VERSION]

    if newVersion == CURRENT_VERSION:
        newData = load_data(os.path.join(DATA_DIR, 'latest'), version = CURRENT_VERSION)
        # print('Loading latest data') # DEBUGONLY
    else:
        newData = load_data(os.path.join(DATA_DIR, newVersion), version=newVersion)
        # print(f'Loading {newVersion} data') # DEBUGONLY
    # print(f"CI FR: {newData.CI_dict_byLoc['FR']['carbonIntensity']}") # DEBUGONLY
    # print(f"TPUv3 TDP: {newData.cores_dict['GPU']['TPU v3']}")  # DEBUGONLY
    return vars(newData)


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
    '''
    Show the different available versions.
    '''
    if (clicks is not None)|((version is not None)&(version != CURRENT_VERSION)):
        return {'display':'flex'}
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
    # allows app to update when code is changed!
    app.run_server(debug=True)