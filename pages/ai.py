import os
import dash

from dash import html, ctx, callback, Input, Output, State, dcc
from types import SimpleNamespace

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint
from blueprints.metrics.metrics_blueprint import get_metrics_blueprint

import blueprints.metrics.metrics_layout as metrics_layout
import blueprints.metrics.utils as metrics_utils

from utils.graphics import loading_wrapper
from utils.handle_inputs import get_available_versions, filter_wrong_inputs, clean_non_used_inputs_for_export, validateInput, open_input_csv_and_comment, read_csv_input, DEFAULT_VALUES_FOR_PAGE_LOAD, CURRENT_VERSION
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

metrics = get_metrics_blueprint(
    id_prefix=AI_PAGE_ID_PREFIX,
    energy_needed_details=metrics_layout.get_metric_per_form_layout(
        training_id=f'{TRAINING_ID_PREFIX}-energy_needed',
        inference_id= f'{INFERENCE_ID_PREFIX}-energy_needed',
    ),
    carbon_footprint_details=metrics_layout.get_metric_per_form_layout(
        training_id=f'{TRAINING_ID_PREFIX}-carbon_emissions',
        inference_id= f'{INFERENCE_ID_PREFIX}-carbon_emissions',
    )
)


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

            #### PAGE DATA ####

            dcc.Store(id=f'{AI_PAGE_ID_PREFIX}-aggregate_data'),

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

            html.Div(
                [
                    #### TRAINING FORM ####

                    training_form.embed(AI_PAGE),

                    #### INFERENCE FORM ####

                    inference_form.embed(AI_PAGE),
                ],
                className=f'ai-input-form'
            ),

            #### RESULTS ####

            metrics.embed(AI_PAGE),

        ],
        className='page_content'
    )

    return page_layout


AI_PAGE.layout = get_ai_page_layout()

###################################################
# DEFINE CALLBACKS


################## LOAD PAGE AND INPUTS

@AI_PAGE.callback(
    [
        Output(f'{TRAINING_ID_PREFIX}-from_input_data', 'data'),
        Output(f'{INFERENCE_ID_PREFIX}-from_input_data', 'data'),
        Output(f'{AI_PAGE_ID_PREFIX}-import-error-message', 'is_open'),
        Output(f'{AI_PAGE_ID_PREFIX}-log-error-subtitle', 'children'),
        Output(f'{AI_PAGE_ID_PREFIX}-log-error-content', 'children'),
        Output(f"{AI_PAGE_ID_PREFIX}-version_from_input",'data'),
    ],
    [
        Input(f'{AI_PAGE_ID_PREFIX}-import-content', 'data'),
    ],
    [
        State(f'{AI_PAGE_ID_PREFIX}-upload-data', 'filename'),
        State(f'{TRAINING_ID_PREFIX}-form_aggregate_data', 'data'),
        State(f'{INFERENCE_ID_PREFIX}-form_aggregate_data', 'data'),
        State('appVersions_dropdown','value'),
    ]
)
def forward_imported_content_to_form(import_data, filename, current_training_form_data, current_inference_form_data, current_app_version):
    '''
    Read input, split data between training and inference forms.
    Then process and check content.
    '''
    show_err_mess = False
    input_data, mess_subtitle, mess_content = open_input_csv_and_comment(import_data, filename)

    # The input file could not be opened correctly
    if not input_data:
        show_err_mess = True
        return current_training_form_data, current_inference_form_data, show_err_mess, mess_subtitle, mess_content, current_app_version
    
    # If input data could be read, we check its validity and consistency
    else:
        app_version = input_data['appVersion']
        mess_subtitle = ''
        # Processing training data
        training_input_data = {key.replace(f'{TRAINING_ID_PREFIX}-', ''): value for key, value in input_data.items() if TRAINING_ID_PREFIX in key}
        clean_training_input_data, invalid_training_inputs, _ = read_csv_input(training_input_data)
        invalid_training_inputs = filter_wrong_inputs(clean_training_input_data, invalid_training_inputs)
        # Processing inference data
        inference_input_data = {key.replace(f'{INFERENCE_ID_PREFIX}-', ''): value for key, value in input_data.items() if INFERENCE_ID_PREFIX in key}
        clean_inference_input_data, invalid_inference_inputs, _ = read_csv_input(inference_input_data)
        invalid_inference_inputs = filter_wrong_inputs(clean_inference_input_data, invalid_inference_inputs)
        # Building error message
        if len(invalid_training_inputs) or len(invalid_inference_inputs):
            show_err_mess = True
            mess_subtitle += f'\n\nThere seems to be some typos in the csv columns name or inconsistencies in its values. ' \
                            f'We use default values for the following fields. \n' 
            if len(invalid_training_inputs):
                mess_content += 'For the training form:'
                mess_content += f"{', '.join(list(invalid_training_inputs.keys()))}."
            if len(invalid_inference_inputs):
                mess_content += 'For the inference form:'
                mess_content += f"{', '.join(list(invalid_inference_inputs.keys()))}."
        return clean_training_input_data, clean_inference_input_data, show_err_mess, mess_subtitle, mess_content, app_version



################## EXPORT DATA

@AI_PAGE.callback(
        Output(f'{AI_PAGE_ID_PREFIX}-export-content', 'data'),
        Input(f"{AI_PAGE_ID_PREFIX}-btn-download_csv", "n_clicks"),
        State(f'{TRAINING_ID_PREFIX}-form_aggregate_data', 'data'),
        State(f'{INFERENCE_ID_PREFIX}-form_aggregate_data', 'data'),
        prevent_initial_call=True,
)
def forward_form_input_to_export_module(_, training_form_agg_data, inference_form_agg_data):
    '''
    Intermediate processing specific to the AI page before exporting data.
    Cleans content to export by standardizing non-used inputs.
    We concatenate the content of the training form and inference form into a single dictionnary to be exported.
    '''
    # Clean non-used inputs
    training_data = clean_non_used_inputs_for_export(training_form_agg_data)
    inference_data = clean_non_used_inputs_for_export(inference_form_agg_data)
    # Add prefix to differentiate between training and inference
    training_data = {f'training-{key}': value for key, value in training_data.items() if key != 'appVersion'}
    inference_data = {f'inference-{key}': value for key, value in inference_data.items() if key != 'appVersion'}
    # Concatenate data
    form_aggregate_data = dict()
    form_aggregate_data['appVersion'] = training_form_agg_data['appVersion']
    form_aggregate_data.update(training_data)
    form_aggregate_data.update(inference_data)
    return form_aggregate_data


################## RESULTS AND METRICS 

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-base_results', 'data'),
    [ 
        Input(f'{TRAINING_ID_PREFIX}-form_output_metrics', 'data'),
        Input(f'{INFERENCE_ID_PREFIX}-form_output_metrics', 'data'),
    ]
)
def forward_aggregate_results_from_forms_to_metrics(training_form_metrics, inference_form_metrics):
    tot_energy_needed = training_form_metrics['energy_needed'] + inference_form_metrics['energy_needed']
    tot_carbon_emissions = training_form_metrics['carbonEmissions'] + inference_form_metrics['carbonEmissions']
    return {
        'energy_needed': tot_energy_needed,
        'carbonEmissions': tot_carbon_emissions,
    }

### DETAILED METRICS PER FORM

# Energy
@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{TRAINING_ID_PREFIX}-energy_needed', 'children'),
    Input(f'{TRAINING_ID_PREFIX}-form_output_metrics', 'data'),
)
def get_training_needed_energy(training_form_metrics):
    return metrics_utils.format_energy_text(training_form_metrics['energy_needed'])

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{INFERENCE_ID_PREFIX}-energy_needed', 'children'),
    Input(f'{INFERENCE_ID_PREFIX}-form_output_metrics', 'data'),
)
def get_training_needed_energy(inference_form_metrics):
    return metrics_utils.format_energy_text(inference_form_metrics['energy_needed'])

# Carbon emissions
@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{TRAINING_ID_PREFIX}-carbon_emissions', 'children'),
    Input(f'{TRAINING_ID_PREFIX}-form_output_metrics', 'data'),
)
def get_training_needed_energy(training_form_metrics):
    return metrics_utils.format_CE_text(training_form_metrics['carbonEmissions'])

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{INFERENCE_ID_PREFIX}-carbon_emissions', 'children'),
    Input(f'{INFERENCE_ID_PREFIX}-form_output_metrics', 'data'),
)
def get_training_needed_energy(inference_form_metrics):
    return metrics_utils.format_CE_text(inference_form_metrics['carbonEmissions'])
