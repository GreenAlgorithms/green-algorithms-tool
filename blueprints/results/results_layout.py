import os

from dash import html, dcc
from utils.graphics import loading_wrapper

import dash_bootstrap_components as dbc

image_dir = os.path.join('assets/images')

def get_green_algo_results_layout():
    return html.Div(
        [
            dcc.Store(id='res_aggregate_data'),
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
    )