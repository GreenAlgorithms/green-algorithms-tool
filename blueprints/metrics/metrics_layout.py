'''
This script contains:
    - the layout of the metrics and "equivalents" (tree absorption, km driving and plane trip) section
    - the layout of the textual content that gives training and inference results

It is important to note that the electricity consumption and carbon emissions sections
have a different structure than the three "equivalents" sections.
This is because the first also contain the training and inference results.
The latter only display the total value.
'''

import os

from dash import html, dcc
from utils.graphics import loading_wrapper

image_dir = os.path.join('assets/images')

###################################################
# METRICS MODULE LAYOUT

def get_green_algo_metrics_layout(
        carbon_footprint_details: html.Div,
        energy_needed_details: html.Div,
):
    return html.Div(
        [
            #### BACKEND DATA ####

            dcc.Store(id='base_results'),

            #### CARBON EMISSIONS ####
            
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
                            ),
                        ],
                        className='mini-box-main-content'

                    ),

                    carbon_footprint_details,
                ],
                className="container mini-box"
            ),

            #### ELECTRICITY CONSUMPTION ####

            html.Div(
                [
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
                            ),
                        ],
                        className='mini-box-main-content'
                    ),
                    
                    energy_needed_details,
                ],
                className="container mini-box"
            ),

            #### TREE ABSOPRTION EQUIVALENT ####

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

            #### CAR KILOMETERS EQUIVALENT ####

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

            #### PLANE TRIPS EQUIVALENT ####

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


###################################################
# METRICS PER FORM LAYOUT

def get_metric_per_form_layout(training_id, inference_id):
    return html.P(
        [
            html.B('Training:'),
            html.B(id=training_id, className='metric-per-form-value training-metric'),
            html.B('Inference:', style={'padding-left': '10px'}),
            html.B(id=inference_id, className='metric-per-form-value'),
        ],
        className='detailed-metric-container'
    )