import os
import dash

from dash import html, ctx, callback, Input, Output, State
from types import SimpleNamespace

from all_in_one_components.form.green_algo_form_AIO import GreenAlgoFormAIO, TRAINING_FORM_ID, INFERENCE_FORM_ID
from all_in_one_components.form.green_algo_form_AIO_ids import GreenAlgoFormIDS

from utils.graphics import loading_wrapper
from utils.handle_inputs import get_available_versions, DEFAULT_VALUES
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region

dash.register_page(__name__, path='/ai')


###################################################
# SOME GLOBAL VARIABLES

image_dir = os.path.join('assets/images')
data_dir = os.path.join(os.path.abspath(''),'data')

appVersions_options = get_available_versions()
form_ids = GreenAlgoFormIDS()


###################################################
# DEFINE APP LAYOUT


def layout():
    page_layout = html.Div(
        [

            #### TRAINING FORM ####

            GreenAlgoFormAIO(
                    TRAINING_FORM_ID,
                    'TRAINING',
                    html.P('How to fill in training form')
                ),

            #### INFERENCE FORM ####

            GreenAlgoFormAIO(
                    INFERENCE_FORM_ID,
                    'INFERENCE',
                    html.P('How to fill in inference form')
                ),

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


def is_training_callback_fired(triggered_prop_ids):
    for prop_id in triggered_prop_ids.keys():
        if TRAINING_FORM_ID in prop_id:
            return True
    return False

def is_inference_callback_fired(triggered_prop_ids):
    for prop_id in triggered_prop_ids.keys():
        if INFERENCE_FORM_ID in prop_id:
            return True
    return False



###################################################
# DEFINE CALLBACKS


################## LOAD PAGE AND INPUTS

@callback(
    [
        ##################################################################
        ## WARNING: do not modify the order, unless modifying the order
        ## of the DEFAULT_VALUES accordingly
        Output(form_ids.runTime_hour_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.runTime_min_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.coreType_dropdown(TRAINING_FORM_ID),'value'),
        Output(form_ids.numberCPUs_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.CPUmodel_dropdown(TRAINING_FORM_ID), 'value'),
        Output(form_ids.tdpCPU_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.numberGPUs_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.GPUmodel_dropdown(TRAINING_FORM_ID), 'value'),
        Output(form_ids.tdpGPU_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.memory_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.platformType_dropdown(TRAINING_FORM_ID),'value'),
        Output(form_ids.usageCPU_radio(TRAINING_FORM_ID),'value'),
        Output(form_ids.usageCPU_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.usageGPU_radio(TRAINING_FORM_ID),'value'),
        Output(form_ids.usageGPU_input(TRAINING_FORM_ID),'value'),
        Output(form_ids.pue_radio(TRAINING_FORM_ID),'value'),
        Output(form_ids.PSF_radio(TRAINING_FORM_ID), 'value'),
        Output(form_ids.PSF_input(TRAINING_FORM_ID), 'value'),
        Output(form_ids.runTime_hour_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.runTime_min_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.coreType_dropdown(INFERENCE_FORM_ID),'value'),
        Output(form_ids.numberCPUs_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.CPUmodel_dropdown(INFERENCE_FORM_ID), 'value'),
        Output(form_ids.tdpCPU_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.numberGPUs_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.GPUmodel_dropdown(INFERENCE_FORM_ID), 'value'),
        Output(form_ids.tdpGPU_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.memory_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.platformType_dropdown(INFERENCE_FORM_ID),'value'),
        Output(form_ids.usageCPU_radio(INFERENCE_FORM_ID),'value'),
        Output(form_ids.usageCPU_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.usageGPU_radio(INFERENCE_FORM_ID),'value'),
        Output(form_ids.usageGPU_input(INFERENCE_FORM_ID),'value'),
        Output(form_ids.pue_radio(INFERENCE_FORM_ID),'value'),
        Output(form_ids.PSF_radio(INFERENCE_FORM_ID), 'value'),
        Output(form_ids.PSF_input(INFERENCE_FORM_ID), 'value'),
    ],
    [
        Input('url_content','pathname'),
        Input('url_content','search'),
    ],
    # suppress_callback_exceptions=True,
)
def filling_from_inputs(_, __):
    '''
    Fills the form either from the content of a csv of with default values.
    When errors are found in the csv, an alert container is displayed with 
    additional information for the user. Wrong values are replaced by default ones.
    The url is given as input so default values are filled when opening the app first.

    Once the appVersions_dropdown value is set, versionned data is loaded and
    the form starts to work accordingly.
    '''
    twice_default_values = list(DEFAULT_VALUES.values())[:-1] * 2
    return tuple(twice_default_values) 



@callback(
    Output(form_ids.provider_dropdown(TRAINING_FORM_ID),'value'),
    Output(form_ids.provider_dropdown(INFERENCE_FORM_ID),'value'),
    [
        Input(form_ids.platformType_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.platformType_dropdown(INFERENCE_FORM_ID), 'value'),
        Input('versioned_data','data'),
    ],
)
def set_provider(_, __, versioned_data):
    '''
    Sets the provider value, either from the csv content of as a default value.
    TODO: improve the choice of the default value.
    '''           
    return 'gcp', 'gcp'
    

@callback(
    Output(form_ids.server_continent_dropdown(TRAINING_FORM_ID),'value'),
    Output(form_ids.server_continent_dropdown(INFERENCE_FORM_ID),'value'),
    [
        Input(form_ids.provider_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.provider_dropdown(INFERENCE_FORM_ID), 'value'),
        Input('versioned_data','data'),
    ],
    [
        State(form_ids.server_continent_dropdown(TRAINING_FORM_ID), 'value'),
        State(form_ids.server_continent_dropdown(INFERENCE_FORM_ID), 'value'),
    ]
)
def set_server_continent_value(
        train_selected_provider,
        inference_selected_provider,
        versioned_data, 
        train_prev_server_continent,
        inference_prev_server_continent
    ):
    '''
    Sets the value for server's continent, depending on the provider.
    We want to display a value selected previously by 
    the user or to choose a relevant default value.
    '''

    triggered_prop_ids = ctx.triggered_prop_ids
    triggered_id = ctx.triggered_id

    new_train_server_continent = dash.no_update
    new_inference_server_continent = dash.no_update

    if is_training_callback_fired(triggered_prop_ids):
        new_train_server_continent = update_server_continent_value(versioned_data, train_selected_provider, train_prev_server_continent)
    if is_inference_callback_fired(triggered_prop_ids):
        new_inference_server_continent = update_server_continent_value(versioned_data, inference_selected_provider, inference_prev_server_continent)
    return new_train_server_continent, new_inference_server_continent
  

def update_server_continent_value(versioned_data, selected_provider, previous_value):
    available_options = availableLocations_continent(selected_provider, versioned_data)
    if previous_value in available_options:
        defaultValue = previous_value
    else:
        try: 
            defaultValue = available_options[0]
        except:
            defaultValue = None
    return defaultValue



@callback(
    Output(form_ids.server_dropdown(TRAINING_FORM_ID),'value'),
    Output(form_ids.server_dropdown(INFERENCE_FORM_ID),'value'),
    [
        Input(form_ids.provider_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.provider_dropdown(INFERENCE_FORM_ID), 'value'),
        Input(form_ids.server_continent_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.server_continent_dropdown(INFERENCE_FORM_ID), 'value'),
        Input('versioned_data','data'),
    ],
    [
        State(form_ids.server_dropdown(TRAINING_FORM_ID),'value'),
        State(form_ids.server_dropdown(INFERENCE_FORM_ID),'value'),
    ]
)
def set_server_value(
        train_selected_provider,
        inference_selected_provider,
        train_selected_continent,
        inference_selected_continent,
        versioned_data,
        train_prev_server_value,
        inference_prev_server_value
    ):
    '''
    Sets the value for servers, based on provider and continent.
    Here again we want to display a default value, to 
    fecth the value from a csv or to show a value previously selected by the user.
    '''
    triggered_prop_ids = ctx.triggered_prop_ids
    new_train_server = dash.no_update
    new_inference_server = dash.no_update

    if is_training_callback_fired(triggered_prop_ids):
        new_train_server = update_server_value(train_selected_continent, train_selected_provider, train_prev_server_value,  versioned_data)
    if is_inference_callback_fired(triggered_prop_ids):
        new_inference_server = update_server_value(inference_selected_continent, inference_selected_provider, inference_prev_server_value, versioned_data)
    return new_train_server, new_inference_server

def update_server_value(selected_continent, selected_provider, previous_value, versioned_data):
    # Handles special case
    if selected_continent == 'other':
        return 'other'
    # Otherwise we return a suitable default value
    availableOptions = availableOptions_servers(selected_provider, selected_continent, data=versioned_data)
    try:
        if previous_value in [server['name_unique'] for server in availableOptions]:
            # when the server continent value had previously been set by the user
            defaultValue = previous_value
        else :
            defaultValue = availableOptions[0]['name_unique']
    except:
        defaultValue = None
    return defaultValue


@callback(
    Output(form_ids.location_continent_dropdown(TRAINING_FORM_ID), 'value'),
    Output(form_ids.location_continent_dropdown(INFERENCE_FORM_ID), 'value'),
    [
        Input(form_ids.server_continent_dropdown(TRAINING_FORM_ID),'value'),
        Input(form_ids.server_continent_dropdown(INFERENCE_FORM_ID),'value'),
        Input(form_ids.server_div(TRAINING_FORM_ID), 'style'),
        Input(form_ids.server_div(INFERENCE_FORM_ID), 'style'),
    ],
    [
        State(form_ids.location_continent_dropdown(TRAINING_FORM_ID), 'value'),
        State(form_ids.location_continent_dropdown(INFERENCE_FORM_ID), 'value'),
    ]
)
def set_location_continent_value(
        train_selected_serverContinent,
        inference_selected_serverContinent,
        train_display_server,
        inference_display_server,
        train_prev_locationContinent,
        inference_prev_locationContinent,
    ):
    '''
    Sets the value for location continent.
    Same as for server and server continent regarding the different inputs.
    '''
    triggered_prop_ids = ctx.triggered_prop_ids
    new_train_continent = dash.no_update
    new_inference_continent = dash.no_update

    if is_training_callback_fired(triggered_prop_ids):
        new_train_continent = update_continent_value(train_prev_locationContinent, train_selected_serverContinent, train_display_server)
    if is_inference_callback_fired(triggered_prop_ids):
        new_inference_continent = update_continent_value(inference_prev_locationContinent, inference_selected_serverContinent, inference_display_server)
    return new_train_continent, new_inference_continent

def update_continent_value(prev_location_continent, selected_server_continent, display_server):
    # handles the case when the continent value had previously been set by the user
    if prev_location_continent is not None :
        return prev_location_continent
    # the server div is shown, so we pull the continent from there
    if (display_server['display'] != 'none') & (selected_server_continent != 'other'):
        return selected_server_continent
    return 'Europe'


@callback(
    [
        Output(form_ids.location_country_dropdown(TRAINING_FORM_ID), 'options'),
        Output(form_ids.location_country_dropdown(INFERENCE_FORM_ID), 'options'),
        Output(form_ids.location_country_dropdown(TRAINING_FORM_ID), 'value'),
        Output(form_ids.location_country_dropdown(INFERENCE_FORM_ID), 'value'),
        Output(form_ids.location_country_dropdown_div(TRAINING_FORM_ID), 'style'),
        Output(form_ids.location_country_dropdown_div(INFERENCE_FORM_ID), 'style'),
    ],
    [
        Input(form_ids.location_continent_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.location_continent_dropdown(INFERENCE_FORM_ID), 'value'),
        Input('versioned_data','data'),
    ],
    [
        State(form_ids.location_country_dropdown(TRAINING_FORM_ID), 'value'),
        State(form_ids.location_country_dropdown(INFERENCE_FORM_ID), 'value')
    ]
)
def set_countries_options(
        train_selected_continent,
        inference_selected_continent,
        versioned_data,
        train_prev_country,
        inference_prev_country,
    ):
    '''
    List of options and value for countries.
    Hides country dropdown if continent=World is selected.
    Must fetch the value from a csv as well.
    '''
    triggered_prop_ids = ctx.triggered_prop_ids
    new_train_options, new_train_value, new_train_div_style = dash.no_update, dash.no_update, dash.no_update
    new_inference_options, new_inference_value, new_inference_div_style = dash.no_update, dash.no_update, dash.no_update

    if is_training_callback_fired(triggered_prop_ids):
        new_train_options, new_train_value, new_train_div_style = update_countries_options_and_value(train_selected_continent, train_prev_country, versioned_data)
    if is_inference_callback_fired(triggered_prop_ids):
        new_inference_options, new_inference_value, new_inference_div_style = update_countries_options_and_value(inference_selected_continent, inference_prev_country, versioned_data)

    return new_train_options, new_inference_options, new_train_value, new_inference_value, new_train_div_style, new_inference_div_style

def update_countries_options_and_value(selected_continent, previous_country, versioned_data):
    availableOptions = availableOptions_country(selected_continent, data=versioned_data)
    listOptions = [{'label': k, 'value': k} for k in availableOptions]
    defaultValue = None
    # Handles the case  when the country value had previously been set by the user
    if previous_country in availableOptions :
        defaultValue = previous_country
    else:
        try:
            defaultValue = availableOptions[0]
        except:
            defaultValue = None
    # Handles special case for display 
    if selected_continent == 'World':
        country_style = {'display': 'none'}
    else:
        country_style = {'display': 'block'}

    return listOptions, defaultValue, country_style

@callback(
    [
        Output(form_ids.location_region_dropdown(TRAINING_FORM_ID), 'options'),
        Output(form_ids.location_region_dropdown(INFERENCE_FORM_ID), 'options'),
        Output(form_ids.location_region_dropdown(TRAINING_FORM_ID), 'value'),
        Output(form_ids.location_region_dropdown(INFERENCE_FORM_ID), 'value'),
        Output(form_ids.location_region_dropdown_div(TRAINING_FORM_ID), 'style'),
        Output(form_ids.location_region_dropdown_div(INFERENCE_FORM_ID), 'style'),
    ],
    [
        Input(form_ids.location_continent_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.location_continent_dropdown(INFERENCE_FORM_ID), 'value'),
        Input(form_ids.location_country_dropdown(TRAINING_FORM_ID), 'value'),
        Input(form_ids.location_country_dropdown(INFERENCE_FORM_ID), 'value'),
        Input('versioned_data','data'),
    ],
    [
        State(form_ids.location_region_dropdown(TRAINING_FORM_ID), 'value'),
        State(form_ids.location_region_dropdown(INFERENCE_FORM_ID), 'value'),
    ]

)
def set_regions_options(
        train_selected_continent,
        inference_selected_continent,
        train_selected_country,
        inference_selected_country,
        versioned_data,
        train_prev_region,
        inference_prev_region,
    ):
    '''
    List of options and value for regions.
    Hides region dropdown if only one possible region (or continent=World)
    '''
    triggered_prop_ids = ctx.triggered_prop_ids
    new_train_options, new_train_value, new_train_div_style = dash.no_update, dash.no_update, dash.no_update
    new_inference_options, new_inference_value, new_inference_div_style = dash.no_update, dash.no_update, dash.no_update

    if is_training_callback_fired(triggered_prop_ids):
        new_train_options, new_train_value, new_train_div_style = update_regions_options_and_value(train_selected_continent, train_selected_country, train_prev_region, versioned_data)
    if is_inference_callback_fired(triggered_prop_ids):
        new_inference_options, new_inference_value, new_inference_div_style = update_regions_options_and_value(inference_selected_continent, inference_selected_country, inference_prev_region, versioned_data)

    return new_train_options, new_inference_options, new_train_value, new_inference_value, new_train_div_style, new_inference_div_style


def update_regions_options_and_value(selected_continent, selected_country, previous_region, versioned_data):
    locs = availableOptions_region(selected_continent, selected_country, data=versioned_data)
    if versioned_data is not None:
        listOptions = [{'label': versioned_data['CI_dict_byLoc'][loc]['regionName'], 'value': loc} for loc in locs]
    else:
        listOptions = []
    defaultValue = None
    # Handles the case when the region value had previously been set by the user
    if previous_region in locs:
        defaultValue = previous_region
    else:
        try:
                defaultValue = locs[0]
        except:
            defaultValue = None
    # Handles the special case for display 
    if (selected_continent == 'World')|(len(listOptions) == 1):
        region_style = {'display': 'none'}
    else:
        region_style = {'display': 'block'}

    return listOptions, defaultValue, region_style


@callback(
    Output(form_ids.PUE_input(TRAINING_FORM_ID),'value'),
    Output(form_ids.PUE_input(INFERENCE_FORM_ID),'value'),
    [
        Input(form_ids.pue_radio(TRAINING_FORM_ID), 'value'),
        Input(form_ids.pue_radio(INFERENCE_FORM_ID), 'value'),
        Input('versioned_data','data'),
    ],
)
def set_PUE(_, __, versioned_data):
    '''
    Sets the PUE value, either from csv input or as a default value.
    '''
    triggered_prop_ids = ctx.triggered_prop_ids
    new_train_pue = dash.no_update
    new_inference_pue = dash.no_update

    if is_training_callback_fired(triggered_prop_ids):
        new_train_pue = update_pue_value(versioned_data)
    if is_inference_callback_fired(triggered_prop_ids):
        new_inference_pue = update_pue_value(versioned_data)
    return new_train_pue, new_inference_pue

def update_pue_value(versioned_data):
    if versioned_data is not None:
        data_dict = SimpleNamespace(**versioned_data)
        defaultPUE = data_dict.pueDefault_dict['Unknown']
    else:
        defaultPUE = 0
    return defaultPUE