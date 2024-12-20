import os
import dash

from dash import html, ctx, callback, Input, Output, State
from types import SimpleNamespace

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint

from utils.graphics import loading_wrapper
from utils.handle_inputs import get_available_versions, DEFAULT_VALUES
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region


AI_PAGE = DashBlueprint()

AI_PAGE_ID_PREFIX = 'ai'

TRAINING_ID_PREFIX = 'training'
training_form = get_form_blueprint(
    id_prefix=TRAINING_ID_PREFIX,
    title='TRAINING',
    subtitle=html.P('How to fill in training form'),
)

INFERENCE_ID_PREFIX = 'inference'
inference_form = get_form_blueprint(
    id_prefix=INFERENCE_ID_PREFIX,
    title='INFERENCE',
    subtitle=html.P('How to fill in inference form'),
)

import_export = get_import_expot_blueprint(id_prefix=AI_PAGE_ID_PREFIX) 


###################################################
# SOME GLOBAL VARIABLES

image_dir = os.path.join('assets/images')
data_dir = os.path.join(os.path.abspath(''),'data')

appVersions_options = get_available_versions()


###################################################
# DEFINE APP LAYOUT


def get_ai_page_layout():
    page_layout = html.Div(
        [

            #### PAGE VARIABLES ####

            

            #### OVERALL EXPLAINATION ####

            html.Div(
                [
                    html.H2('Artificial intelligence dedicated page'),
                    html.P('Some explainations')
                ],
                className='container'
            ),

            #### IMPORT AND EXPORT ####

            import_export.embed(AI_PAGE),

            #### TRAINING FORM ####

            training_form.embed(AI_PAGE),

            #### INFERENCE FORM ####

            inference_form.embed(AI_PAGE),

            #### RESULTS ####

            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H2('RESULTS')
                                ],
                                id='result-title'
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
                        className='super-section'
                    ),
                ],
                className='result-section container'
            )

        ],
        className='fullPage'
    )

    return page_layout


AI_PAGE.layout = get_ai_page_layout()

###################################################
# DEFINE CALLBACKS


################## LOAD PAGE AND INPUTS

# @AI_PAGE.callback(
#     [
#         ##################################################################
#         ## WARNING: do not modify the order, unless modifying the order
#         ## of the DEFAULT_VALUES accordingly
#         Output(f'{TRAINING_ID_PREFIX}-runTime_hour_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-runTime_min_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-coreType_dropdown','value'),
#         Output(f'{TRAINING_ID_PREFIX}-numberCPUs_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-CPUmodel_dropdown', 'value'),
#         Output(f'{TRAINING_ID_PREFIX}-tdpCPU_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-numberGPUs_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-GPUmodel_dropdown', 'value'),
#         Output(f'{TRAINING_ID_PREFIX}-tdpGPU_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-memory_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-platformType_dropdown','value'),
#         Output(f'{TRAINING_ID_PREFIX}-usageCPU_radio','value'),
#         Output(f'{TRAINING_ID_PREFIX}-usageCPU_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-usageGPU_radio','value'),
#         Output(f'{TRAINING_ID_PREFIX}-usageGPU_input','value'),
#         Output(f'{TRAINING_ID_PREFIX}-pue_radio','value'),
#         Output(f'{TRAINING_ID_PREFIX}-PSF_radio', 'value'),
#         Output(f'{TRAINING_ID_PREFIX}-PSF_input', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-runTime_hour_input','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-runTime_min_input','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-coreType_dropdown','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-numberCPUs_input','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-CPUmodel_dropdown', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-tdpCPU_input','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-numberGPUs_input','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-GPUmodel_dropdown', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-tdpGPU_input', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-memory_input', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-platformType_dropdown','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-usageCPU_radio', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-usageCPU_input', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-usageGPU_radio', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-usageGPU_input', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-pue_radio','value'),
#         Output(f'{INFERENCE_ID_PREFIX}-PSF_radio', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-PSF_input', 'value'),
#     ],
#     [
#         Input('url_content','pathname'),
#         Input('url_content','search'),
#     ],
#     # suppress_callback_exceptions=True,
# )
# def filling_from_inputs(_, __):
#     '''
#     Fills the form either from the content of a csv of with default values.
#     When errors are found in the csv, an alert container is displayed with 
#     additional information for the user. Wrong values are replaced by default ones.
#     The url is given as input so default values are filled when opening the app first.

#     Once the appVersions_dropdown value is set, versionned data is loaded and
#     the form starts to work accordingly.
#     '''
#     twice_default_values = list(DEFAULT_VALUES.values())[:-1] * 2
#     return tuple(twice_default_values) 



# @AI_PAGE.callback(
#     Output(f'{TRAINING_ID_PREFIX}-provider_dropdown','value'),
#     [
#         Input(f'{TRAINING_ID_PREFIX}-platformType_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
# )
# def set_provider(_, versioned_data):
#     '''
#     Sets the provider value, either from the csv content of as a default value.
#     TODO: improve the choice of the default value.
#     '''           
#     return 'gcp'

# @AI_PAGE.callback(
#     Output(f'{INFERENCE_ID_PREFIX}-provider_dropdown','value'),
#     [
#         Input(f'{INFERENCE_ID_PREFIX}-platformType_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
# )
# def set_provider(_, versioned_data):
#     '''
#     Sets the provider value, either from the csv content of as a default value.
#     TODO: improve the choice of the default value.
#     '''           
#     return 'gcp'
    

# def update_server_continent_value(versioned_data, selected_provider, previous_value):
#     available_options = availableLocations_continent(selected_provider, versioned_data)
#     if previous_value in available_options:
#         defaultValue = previous_value
#     else:
#         try: 
#             defaultValue = available_options[0]
#         except:
#             defaultValue = None
#     return defaultValue

# @AI_PAGE.callback(
#     Output(f'{TRAINING_ID_PREFIX}-server_continent_dropdown','value'),
#     [
#         Input(f'{TRAINING_ID_PREFIX}-provider_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{TRAINING_ID_PREFIX}-server_continent_dropdown', 'value'),
#     ]
# )
# def set_server_continent_value(
#         train_selected_provider,
#         versioned_data, 
#         train_prev_server_continent,
#     ):
#     '''
#     Sets the value for server's continent, depending on the provider.
#     We want to display a value selected previously by 
#     the user or to choose a relevant default value.
#     '''
#     return  update_server_continent_value(versioned_data, train_selected_provider, train_prev_server_continent)

# @AI_PAGE.callback(
#     Output(f'{INFERENCE_ID_PREFIX}-server_continent_dropdown','value'),
#     [
#         Input(f'{INFERENCE_ID_PREFIX}-provider_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{INFERENCE_ID_PREFIX}-server_continent_dropdown', 'value'),
#     ]
# )
# def set_server_continent_value(
#         inference_selected_provider,
#         versioned_data, 
#         inference_prev_server_continent,
#     ):
#     '''
#     Sets the value for server's continent, depending on the provider.
#     We want to display a value selected previously by 
#     the user or to choose a relevant default value.
#     '''
#     return  update_server_continent_value(versioned_data, inference_selected_provider, inference_prev_server_continent)


# def update_server_value(selected_continent, selected_provider, previous_value, versioned_data):
#     # Handles special case
#     if selected_continent == 'other':
#         return 'other'
#     # Otherwise we return a suitable default value
#     availableOptions = availableOptions_servers(selected_provider, selected_continent, data=versioned_data)
#     try:
#         if previous_value in [server['name_unique'] for server in availableOptions]:
#             # when the server continent value had previously been set by the user
#             defaultValue = previous_value
#         else :
#             defaultValue = availableOptions[0]['name_unique']
#     except:
#         defaultValue = None
#     return defaultValue

# @AI_PAGE.callback(
#     Output(f'{TRAINING_ID_PREFIX}server_dropdown','value'),
#     [
#         Input(f'{TRAINING_ID_PREFIX}provider_dropdown', 'value'),
#         Input(f'{TRAINING_ID_PREFIX}server_continent_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{TRAINING_ID_PREFIX}server_dropdown','value'),
#     ]
# )
# def set_server_value(
#         train_selected_provider,
#         train_selected_continent,
#         versioned_data,
#         train_prev_server_value,
#     ):
#     '''
#     Sets the value for servers, based on provider and continent.
#     Here again we want to display a default value, to 
#     fecth the value from a csv or to show a value previously selected by the user.
#     '''
#     return update_server_value(train_selected_continent, train_selected_provider, train_prev_server_value,  versioned_data)

# @AI_PAGE.callback(
#     Output(f'{INFERENCE_ID_PREFIX}server_dropdown','value'),
#     [
#         Input(f'{INFERENCE_ID_PREFIX}provider_dropdown', 'value'),
#         Input(f'{INFERENCE_ID_PREFIX}server_continent_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{INFERENCE_ID_PREFIX}server_dropdown','value'),
#     ]
# )
# def set_server_value(
#         inference_selected_provider,
#         inference_selected_continent,
#         versioned_data,
#         inference_prev_server_value,
#     ):
#     '''
#     Sets the value for servers, based on provider and continent.
#     Here again we want to display a default value, to 
#     fecth the value from a csv or to show a value previously selected by the user.
#     '''
#     return update_server_value(inference_selected_continent, inference_selected_provider, inference_prev_server_value,  versioned_data)


# def update_continent_value(prev_location_continent, selected_server_continent, display_server):
#     # handles the case when the continent value had previously been set by the user
#     if prev_location_continent is not None :
#         return prev_location_continent
#     # the server div is shown, so we pull the continent from there
#     if (display_server['display'] != 'none') & (selected_server_continent != 'other'):
#         return selected_server_continent
#     return 'Europe'

# @AI_PAGE.callback(
#     Output(f'{TRAINING_ID_PREFIX}-location_continent_dropdown', 'value'),
#     [
#         Input(f'{TRAINING_ID_PREFIX}-server_continent_dropdown','value'),
#         Input(f'{TRAINING_ID_PREFIX}-server_div', 'style'),
#     ],
#     [
#         State(f'{TRAINING_ID_PREFIX}-location_continent_dropdown', 'value'),
#     ]
# )
# def set_location_continent_value(
#         train_selected_serverContinent,
#         train_display_server,
#         train_prev_locationContinent,
#     ):
#     '''
#     Sets the value for location continent.
#     Same as for server and server continent regarding the different inputs.
#     '''
#     return update_continent_value(train_prev_locationContinent, train_selected_serverContinent, train_display_server)

# @AI_PAGE.callback(
#     Output(f'{INFERENCE_ID_PREFIX}-location_continent_dropdown', 'value'),
#     [
#         Input(f'{INFERENCE_ID_PREFIX}-server_continent_dropdown','value'),
#         Input(f'{INFERENCE_ID_PREFIX}-server_div', 'style'),
#     ],
#     [
#         State(f'{INFERENCE_ID_PREFIX}-location_continent_dropdown', 'value'),
#     ]
# )
# def set_location_continent_value(
#         inference_selected_serverContinent,
#         inference_display_server,
#         inference_prev_locationContinent,
#     ):
#     '''
#     Sets the value for location continent.
#     Same as for server and server continent regarding the different inputs.
#     '''
#     return update_continent_value(inference_prev_locationContinent, inference_selected_serverContinent, inference_display_server)



# def update_countries_options_and_value(selected_continent, previous_country, versioned_data):
#     availableOptions = availableOptions_country(selected_continent, data=versioned_data)
#     listOptions = [{'label': k, 'value': k} for k in availableOptions]
#     defaultValue = None
#     # Handles the case  when the country value had previously been set by the user
#     if previous_country in availableOptions :
#         defaultValue = previous_country
#     else:
#         try:
#             defaultValue = availableOptions[0]
#         except:
#             defaultValue = None
#     # Handles special case for display 
#     if selected_continent == 'World':
#         country_style = {'display': 'none'}
#     else:
#         country_style = {'display': 'block'}

#     return listOptions, defaultValue, country_style

# @AI_PAGE.callback(
#     [
#         Output(f'{TRAINING_ID_PREFIX}-location_country_dropdown', 'options'),
#         Output(f'{TRAINING_ID_PREFIX}-location_country_dropdown', 'value'),
#         Output(f'{TRAINING_ID_PREFIX}-location_country_dropdown_div', 'style'),
#     ],
#     [
#         Input(f'{TRAINING_ID_PREFIX}-location_continent_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{TRAINING_ID_PREFIX}-location_country_dropdown', 'value'),
#     ]
# )
# def set_countries_options(
#         train_selected_continent,
#         versioned_data,
#         train_prev_country,
#     ):
#     '''
#     List of options and value for countries.
#     Hides country dropdown if continent=World is selected.
#     Must fetch the value from a csv as well.
#     '''
#     return update_countries_options_and_value(train_selected_continent, train_prev_country, versioned_data)

# @AI_PAGE.callback(
#     [
#         Output(f'{INFERENCE_ID_PREFIX}-location_country_dropdown', 'options'),
#         Output(f'{INFERENCE_ID_PREFIX}-location_country_dropdown', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-location_country_dropdown_div', 'style'),
#     ],
#     [
#         Input(f'{INFERENCE_ID_PREFIX}-location_continent_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{INFERENCE_ID_PREFIX}-location_country_dropdown', 'value'),
#     ]
# )
# def set_countries_options(
#         inference_selected_continent,
#         versioned_data,
#         inference_prev_country,
#     ):
#     '''
#     List of options and value for countries.
#     Hides country dropdown if continent=World is selected.
#     Must fetch the value from a csv as well.
#     '''
#     return update_countries_options_and_value(inference_selected_continent, inference_prev_country, versioned_data)


# def update_regions_options_and_value(selected_continent, selected_country, previous_region, versioned_data):
#     locs = availableOptions_region(selected_continent, selected_country, data=versioned_data)
#     if versioned_data is not None:
#         listOptions = [{'label': versioned_data['CI_dict_byLoc'][loc]['regionName'], 'value': loc} for loc in locs]
#     else:
#         listOptions = []
#     defaultValue = None
#     # Handles the case when the region value had previously been set by the user
#     if previous_region in locs:
#         defaultValue = previous_region
#     else:
#         try:
#                 defaultValue = locs[0]
#         except:
#             defaultValue = None
#     # Handles the special case for display 
#     if (selected_continent == 'World')|(len(listOptions) == 1):
#         region_style = {'display': 'none'}
#     else:
#         region_style = {'display': 'block'}

#     return listOptions, defaultValue, region_style

# @AI_PAGE.callback(
#     [
#         Output(f'{TRAINING_ID_PREFIX}-location_region_dropdown', 'options'),
#         Output(f'{TRAINING_ID_PREFIX}-location_region_dropdown', 'value'),
#         Output(f'{TRAINING_ID_PREFIX}-location_region_dropdown_div', 'style'),
#     ],
#     [
#         Input(f'{TRAINING_ID_PREFIX}-location_continent_dropdown', 'value'),
#         Input(f'{TRAINING_ID_PREFIX}-location_country_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{TRAINING_ID_PREFIX}-location_region_dropdown', 'value'),
#     ]

# )
# def set_regions_options(
#         train_selected_continent,
#         train_selected_country,
#         versioned_data,
#         train_prev_region,
#     ):
#     '''
#     List of options and value for regions.
#     Hides region dropdown if only one possible region (or continent=World)
#     '''
#     return update_regions_options_and_value(train_selected_continent, train_selected_country, train_prev_region, versioned_data)

# @AI_PAGE.callback(
#     [
#         Output(f'{INFERENCE_ID_PREFIX}-location_region_dropdown', 'options'),
#         Output(f'{INFERENCE_ID_PREFIX}-location_region_dropdown', 'value'),
#         Output(f'{INFERENCE_ID_PREFIX}-location_region_dropdown_div', 'style'),
#     ],
#     [
#         Input(f'{INFERENCE_ID_PREFIX}-location_continent_dropdown', 'value'),
#         Input(f'{INFERENCE_ID_PREFIX}-location_country_dropdown', 'value'),
#         Input('versioned_data','data'),
#     ],
#     [
#         State(f'{INFERENCE_ID_PREFIX}-location_region_dropdown', 'value'),
#     ]

# )
# def set_regions_options(
#         inference_selected_continent,
#         inference_selected_country,
#         versioned_data,
#         inference_prev_region,
#     ):
#     '''
#     List of options and value for regions.
#     Hides region dropdown if only one possible region (or continent=World)
#     '''
#     return update_regions_options_and_value(inference_selected_continent, inference_selected_country, inference_prev_region, versioned_data)


# def update_pue_value(versioned_data):
#     if versioned_data is not None:
#         data_dict = SimpleNamespace(**versioned_data)
#         defaultPUE = data_dict.pueDefault_dict['Unknown']
#     else:
#         defaultPUE = 0
#     return defaultPUE

# @AI_PAGE.callback(
#     Output(f'{TRAINING_ID_PREFIX}-PUE_input','value'),
#     [
#         Input(f'{TRAINING_ID_PREFIX}-pue_radio', 'value'),
#         Input('versioned_data','data'),
#     ],
# )
# def set_PUE(_, versioned_data):
#     '''
#     Sets the PUE value, either from csv input or as a default value.
#     '''
#     return update_pue_value(versioned_data)

# @AI_PAGE.callback(
#     Output(f'{INFERENCE_ID_PREFIX}-PUE_input','value'),
#     [
#         Input(f'{INFERENCE_ID_PREFIX}-pue_radio', 'value'),
#         Input('versioned_data','data'),
#     ],
# )
# def set_PUE(_, versioned_data):
#     '''
#     Sets the PUE value, either from csv input or as a default value.
#     '''
#     return update_pue_value(versioned_data)

