import os
import dash

from dash import html, ctx, callback, Input, Output, State, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from types import SimpleNamespace

from dash_extensions.enrich import DashBlueprint, html
from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint
from blueprints.metrics.metrics_blueprint import get_metrics_blueprint

import blueprints.metrics.metrics_layout as metrics_layout
import blueprints.metrics.utils as metrics_utils
import blueprints.methodology.methodology_layout as methodo_layout
import blueprints.form.form_layout as form_layout

from utils.graphics import loading_wrapper, MY_COLORS
from utils.handle_inputs import get_available_versions, filter_wrong_inputs, clean_non_used_inputs_for_export, validateInput, open_input_csv_and_comment, read_csv_input, AI_PAGE_DEFAULT_VALUES, CURRENT_VERSION
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region


AI_PAGE = DashBlueprint()

AI_PAGE_ID_PREFIX = 'ai'

TRAINING_ID_PREFIX = 'training'
training_form = get_form_blueprint(
    id_prefix=TRAINING_ID_PREFIX,
    title='',
    subtitle=html.P('Report your training-related computations. For more information about R&D experiments, retrainings or overall tips regarding your reporting, please refer to the Help tab.'),
    PSF_properties={'display': 'none'},
    additional_bottom_fields=form_layout.get_additional_training_fields_layout()
)

INFERENCE_ID_PREFIX = 'inference'
inference_form = get_form_blueprint(
    id_prefix=INFERENCE_ID_PREFIX,
    title='',
    subtitle=html.P('Report your inference-related computations. For more information about continuous inference scheme or overall tips regarding your reporting, please refer to the Help tab.'),
    continuous_inf_scheme_properties={'display': 'block'}
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
            #### OVERALL EXPLAINATION ####

            html.Div(
                [
                    html.H2('Artificial intelligence dedicated page'),
                    html.P(
                            'This new page is especially dedicated to AI-related computations, namely training and inference phases. ' \
                            "It is intended to ease the reporting of AI systems' environmental impacts over a fixed time lenght, typically one year. " \
                            'The formula applied to your inputs is exactly the same as the one used in the main page calculator.'
                        )
                ],
                className='container'
            ),

            #### IMPORT AND EXPORT ####

            import_export.embed(AI_PAGE),
            dcc.Store(id='specific_ai_page_inputs'),

            #### FORMS ####

            html.Div(
                [
                    #### REPORTING SCOPE ####

                    html.Div(
                        [
                            html.H3("Reporting time scope"),

                            html.P(
                                [
                                    'Your reporting (time) scope corresponds to the time length over which you want to estimate the environmental impacts of your AI system. ' ,
                                    'Typical values might be one year or the whole estimated lifespan of your system. ' ,
                                    html.B('To consistently report the impacts of your project, you are invited to take into account all the computations happening during / falling within the scope. ' ),
                                    'This period must correspond to a period of stabilized inference (constant inference or known growth).',
                                ],
                                className='reporting-scope-text'
                            ),
                                  
                            html.Div(
                                [
                                    dcc.Input(
                                        type='number',
                                        id='reporting_time_scope_input',
                                        min=0.5,
                                        step = 0.5,
                                        value=1,
                                    ),

                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id='reporting_time_scope_dropdown',
                                                options=[
                                                        {'label': 'Month', 'value': 'month'},
                                                        {'label': 'Year', 'value': 'year'},
                                                    ],
                                                value='year',
                                                className='dropdown',
                                                clearable=False,
                                            ),
                                        ],
                                        className='box-fields'
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "Please, fill in your reporting time scope",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                ],
                                className="reporting-row form-row short-input"
                            ),

                            html.P(
                                [
                                    'The above field is mostly declarative. It should help you to correctly quantify your computations and then easily communicate about your reporting. It has no impact on the calculator outputs ',
                                    html.B('except when choosing the continuous inference scheme. Please refer to the inference Help tab for more information.'),
                                ],
                                className='reporting-scope-text',
                                style={'margin-top': '10px'},
                            )

                        ],
                        className='container',
                    ),

                    #### TRAINING FORM ####

                    dcc.Store(id='training_processed_output_metrics'),

                    dmc.Tabs(
                        [
                            html.H3('TRAINING'),

                            dmc.TabsList(
                                [
                                    dmc.TabsTab(
                                        "Form",
                                        leftSection=DashIconify(icon="simple-line-icons:calculator"),
                                        value='form',
                                        className = 'tab-label',
                                    ),
                                    dmc.TabsTab(
                                        "Help",
                                        leftSection=DashIconify(icon="streamline:help-question-1"),
                                        value='help',
                                        className = 'tab-label',
                                    ),
                                ]
                            ),
                            dmc.TabsPanel(children=training_form.embed(AI_PAGE), value='form'),
                            dmc.TabsPanel(children=methodo_layout.get_training_help_content(''), value='help'),
                        ],
                        value="form",
                        className='tab-container',
                    ),

                    #### INFERENCE FORM ####

                    dcc.Store(id='inference_processed_output_metrics'),

                    dmc.Tabs(
                        [
                            html.H3('INFERENCE'),

                            dmc.TabsList(
                                [
                                    dmc.TabsTab(
                                        "Form",
                                        leftSection=DashIconify(icon="simple-line-icons:calculator"),
                                        value='form',
                                        className = 'tab-label',
                                    ),
                                    dmc.TabsTab(
                                        "Help",
                                        leftSection=DashIconify(icon="streamline:help-question-1"),
                                        value='help',
                                        className = 'tab-label',
                                    ),
                                ]
                            ),
                            dmc.TabsPanel(children=inference_form.embed(AI_PAGE), value='form'),
                            dmc.TabsPanel(children=methodo_layout.get_inference_help_content(''), value='help'),
                        ],
                        value="form",
                        className='tab-container',
                    ),
                ],
                className=f'ai-input-forms'
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
        Output('specific_ai_page_inputs', 'data'),
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
    Process specific inputs such as etrainings, R&D training and continuous inference related fields
    Then process and check content, filtering wrong inputs and displayling error message if required.
    '''
    show_err_mess = False
    input_data, mess_subtitle, mess_content = open_input_csv_and_comment(import_data, filename)

    # The input file could not be opened correctly
    if not input_data:
        show_err_mess = True
        return (
            current_training_form_data,
            current_inference_form_data,
            show_err_mess,
            mess_subtitle,
            mess_content,
            current_app_version,
            {}
        )
    
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
                mess_content += f"{', '.join(list(invalid_training_inputs.keys()))}. \n"
            if len(invalid_inference_inputs):
                mess_content += 'For the inference form:'
                mess_content += f"{', '.join(list(invalid_inference_inputs.keys()))}."
        return (
            clean_training_input_data, 
            clean_inference_input_data, 
            show_err_mess, 
            mess_subtitle, 
            mess_content, 
            app_version,
            input_data
        )  

@AI_PAGE.callback(
        [
            Output(f'{TRAINING_ID_PREFIX}-RandD_PSF_radio','value'),
            Output(f'{TRAINING_ID_PREFIX}-RandD_PSF_input','value'),
            Output(f'{TRAINING_ID_PREFIX}-retrainings_PSF_radio','value'),
            Output(f'{TRAINING_ID_PREFIX}-retrainings_PSF_input','value'),
        ],
        [
            # to allow initial triggering
            Input('url_content','search'),
            Input('specific_ai_page_inputs', 'data'),
        ]
)
def load_RandD_and_retrainings_inputs(_, specific_ai_inputs: dict):
    '''
    Forward inputs from the csv to retrainings and R&D fields.
    If not, fill in with default values, for instance when loading the page.
    '''
    if specific_ai_inputs:
        return (
            specific_ai_inputs['R&D_PSF_radio'],
            specific_ai_inputs['R&D_PSF_value'],
            specific_ai_inputs['retrainings_PSF_radio'],
            specific_ai_inputs['retrainings_PSF_value'],
        )
    else:
        # otherwise we return default values
        return (
            AI_PAGE_DEFAULT_VALUES['R&D_PSF_radio'],
            AI_PAGE_DEFAULT_VALUES['R&D_PSF_value'],
            AI_PAGE_DEFAULT_VALUES['retrainings_PSF_radio'],
            AI_PAGE_DEFAULT_VALUES['retrainings_PSF_value'], 
        )

@AI_PAGE.callback(
        [
            Output(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
            Output(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_dropdown', 'value'),
            Output(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_input', 'value'),
        ],
        [
            # to allow initial triggering
            Input('url_content','search'),
            Input('specific_ai_page_inputs', 'data'),
        ]
)
def load_inference_specific_inputs(_, specific_ai_inputs: dict):
    '''
    Forward inputs from the csv to input data time scope and continuous inference field.
    If not, fill in with default values, for instance when loading the page.
    '''
    if specific_ai_inputs:
        return (
            specific_ai_inputs['continuous_inference_switcher'],
            specific_ai_inputs['input_data_time_scope_unit'],
            specific_ai_inputs['input_data_time_scope_val'],
        )
    else:
        # otherwise we return default values
        return (
            AI_PAGE_DEFAULT_VALUES['continuous_inference_switcher'],
            AI_PAGE_DEFAULT_VALUES['input_data_time_scope_unit'],
            AI_PAGE_DEFAULT_VALUES['input_data_time_scope_val'],
        )



################## CONTINUOUS INFERENCE

@AI_PAGE.callback(
    Output(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_section', 'style'),
    Input(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
)
def display_or_hide_input_data_time_scope_section(is_inference_continuous):
    if is_inference_continuous:
        return {'diplay': 'block'}
    return {'display': 'none'}


################## ADDITIONAL TRAININGS FIELDS

@AI_PAGE.callback(
    Output(f'{TRAINING_ID_PREFIX}-RandD_PSF_input','style'),
    [
        Input(f'{TRAINING_ID_PREFIX}-RandD_PSF_radio', 'value'),
        Input(f'{TRAINING_ID_PREFIX}-RandD_PSF_input','disabled')
    ]
)
def display_RandD_trainings_input(RandD_trainings_radio, disabled):
    '''
    Shows or hides the  R&D trainings input box
    '''
    if RandD_trainings_radio == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out


@AI_PAGE.callback(
    Output(f'{TRAINING_ID_PREFIX}-retrainings_PSF_input','style'),
    [
        Input(f'{TRAINING_ID_PREFIX}-retrainings_PSF_radio', 'value'),
        Input(f'{TRAINING_ID_PREFIX}-retrainings_PSF_input','disabled')
    ]
)
def display_RandD_trainings_input(retrainings_radio, disabled):
    '''
    Shows or hides the  R&D trainings input box
    '''
    if retrainings_radio == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out


################## EXPORT DATA

@AI_PAGE.callback(
        Output(f'{AI_PAGE_ID_PREFIX}-export-content', 'data'),
        Input(f"{AI_PAGE_ID_PREFIX}-btn-download_csv", "n_clicks"),
        [
            State(f'reporting_time_scope_input', 'value'),
            State(f'reporting_time_scope_dropdown', 'value'),
            State(f'{TRAINING_ID_PREFIX}-form_aggregate_data', 'data'),
            State(f'{INFERENCE_ID_PREFIX}-form_aggregate_data', 'data'),
            State(f'{TRAINING_ID_PREFIX}-retrainings_PSF_radio', 'value'),
            State(f'{TRAINING_ID_PREFIX}-retrainings_PSF_input', 'value'),
            State(f'{TRAINING_ID_PREFIX}-RandD_PSF_radio', 'value'),
            State(f'{TRAINING_ID_PREFIX}-RandD_PSF_input', 'value'),
            State(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_input', 'value'),
            State(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_dropdown', 'value'),
            State(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
        ],
        prevent_initial_call=True,
)
def forward_form_input_to_export_module(
    _,
    reporting_time_val: int,
    reporting_time_unit: str,
    training_form_agg_data:dict,
    inference_form_agg_data:dict,
    retraining_PSF_radio: str,
    retraining_PSF_val: float,
    RandD_PSF_radio: str,
    RandD_PSF_val: float,
    input_data_time_scope_val: int,
    input_data_time_scope_unit: str,
    inference_continuous_activated: bool,
):
    '''
    Intermediate processing specific to the AI page before exporting data.
    Cleans content to export by standardizing non-used inputs.
    We concatenate the content of the training form and inference form into a single dictionnary to be exported.
    '''
    forms_aggregate_data = dict()
    # Forward global inputs
    forms_aggregate_data['appVersion'] = training_form_agg_data['appVersion']
    forms_aggregate_data['reporting_time_scope_unit'] = reporting_time_unit
    forms_aggregate_data['reporting_time_scope_value'] = reporting_time_val
    # Clean non-used inputs
    training_data = clean_non_used_inputs_for_export(training_form_agg_data)
    inference_data = clean_non_used_inputs_for_export(inference_form_agg_data)
    # Add prefix to differentiate between training and inference
    training_data = {f'training-{key}': value for key, value in training_data.items() if key != 'appVersion'}
    inference_data = {f'inference-{key}': value for key, value in inference_data.items() if key != 'appVersion'}
    # Add training additional fields - retrainings and R&D trainings
    if retraining_PSF_radio == 'No':
        retraining_PSF_val = 0
    ### WARNING: should not put the word 'training' in the key of the retraining items
    training_data['retrainings_PSF_radio'] = retraining_PSF_radio
    training_data['retrainings_PSF_value'] = retraining_PSF_val
    if RandD_PSF_radio == 'No':
        RandD_PSF_val = 0
    training_data['R&D_PSF_radio'] = RandD_PSF_radio
    training_data['R&D_PSF_value'] = RandD_PSF_val
    # Add inference additional fields - continuous inference scheme
    inference_data['continuous_inference_switcher'] = inference_continuous_activated
    inference_data['input_data_time_scope_unit'] = input_data_time_scope_unit
    inference_data['input_data_time_scope_val'] = input_data_time_scope_val
    # Concatenate training and inference data
    forms_aggregate_data.update(training_data)
    forms_aggregate_data.update(inference_data)
    return forms_aggregate_data


################## RESULTS AND METRICS 

@AI_PAGE.callback(
        Output('inference_processed_output_metrics', 'data'),
        [
            Input(f'{INFERENCE_ID_PREFIX}-form_output_metrics', 'data'),
            Input(f'reporting_time_scope_input', 'value'),
            Input(f'reporting_time_scope_dropdown', 'value'),
            Input(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_input', 'value'),
            Input(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_dropdown', 'value'),
            Input(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
        ],
)
def process_inference_form_outputs_based_on_reporting_scope(
    inference_form_metrics: dict,
    reporting_time_val: int,
    reporting_time_unit: str,
    input_data_time_scope_val: int,
    input_data_time_scope_unit: str,
    inference_continuous_activated: bool,
):
    '''
    The purpose of this callback is to take into account the reporting scope
    in case continuous inference scheme is selected by the user.
    It automatically scales the end electricity consumption based on reporting scope and
    and the input data time scope.
    '''
    # We need to process the form outputs only if continuous inference is activated
    if inference_continuous_activated:
        # We scale input_data_time scope to month
        input_scope_mutiplicative_factor = 1.
        if input_data_time_scope_unit == 'day':
            input_scope_mutiplicative_factor *= (30/input_data_time_scope_val)
        elif input_data_time_scope_unit == 'week':
            input_scope_mutiplicative_factor *= (4/input_data_time_scope_val)
        elif input_data_time_scope_unit == 'month':
            input_scope_mutiplicative_factor /= (1*input_data_time_scope_val)
        elif input_data_time_scope_unit == 'year':
            input_scope_mutiplicative_factor /= (12*input_data_time_scope_val)
        # We scale reporting scope from month
        reporting_multiplicative_factor = 1
        if reporting_time_unit == 'month':
             reporting_multiplicative_factor *= (1*reporting_time_val)
        if reporting_time_unit == 'year':
             reporting_multiplicative_factor *= (12*reporting_time_val)
        # We apply multiplicative coefficients to the form outputs
        mult_coef = input_scope_mutiplicative_factor * reporting_multiplicative_factor
        inference_form_metrics['energy_needed'] = mult_coef * inference_form_metrics['energy_needed']
        inference_form_metrics['carbonEmissions'] = mult_coef * inference_form_metrics['carbonEmissions']
    return inference_form_metrics
    

@AI_PAGE.callback(
        Output('training_processed_output_metrics', 'data'),
        [
            Input(f'{TRAINING_ID_PREFIX}-form_output_metrics', 'data'),
            Input(f'{TRAINING_ID_PREFIX}-retrainings_PSF_radio', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-retrainings_PSF_input', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-RandD_PSF_radio', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-RandD_PSF_input', 'value'),
        ]
)
def add_retrainings_and_RandD_to_training_outputs(
    training_form_metrics: dict,
    retraining_PSF_radio: str,
    retraining_PSF_val: float,
    RandD_PSF_radio: str,
    RandD_PSF_val: float,
):
    ''' 
    The purpose of this callback is to take into account retrainings and R&D inputs.
    The main training form outputs (energy consumption and crbon emissions) are 
    multiplied by the corresponding PSF for both retrainings and R&D 
    before they are added to the total.
    '''
    # Checking is values should be added from retrainings or RandD
    if retraining_PSF_radio == 'No':
        retraining_PSF_val = 0
    if RandD_PSF_radio == 'No':
        RandD_PSF_val = 0
    # Add values to main training metrics
    training_form_metrics['energy_needed'] = training_form_metrics['energy_needed'] * (1 + RandD_PSF_val + retraining_PSF_val)
    training_form_metrics['carbonEmissions'] = training_form_metrics['carbonEmissions'] * (1 + RandD_PSF_val + retraining_PSF_val)
    return training_form_metrics



@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-base_results', 'data'),
    [ 
        Input(f'training_processed_output_metrics', 'data'),
        Input(f'inference_processed_output_metrics', 'data'),
    ],
)
def forward_aggregate_results_from_forms_to_metrics(training_form_metrics, inference_form_metrics,):
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
    Input(f'training_processed_output_metrics', 'data'),
)
def get_training_needed_energy(training_form_metrics):
    return metrics_utils.format_energy_text(training_form_metrics['energy_needed'])

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{INFERENCE_ID_PREFIX}-energy_needed', 'children'),
    Input(f'inference_processed_output_metrics', 'data'),
)
def get_training_needed_energy(inference_form_metrics):
    return metrics_utils.format_energy_text(inference_form_metrics['energy_needed'])

# Carbon emissions
@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{TRAINING_ID_PREFIX}-carbon_emissions', 'children'),
    Input(f'training_processed_output_metrics', 'data'),
)
def get_training_needed_energy(training_form_metrics):
    return metrics_utils.format_CE_text(training_form_metrics['carbonEmissions'])

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{INFERENCE_ID_PREFIX}-carbon_emissions', 'children'),
    Input(f'inference_processed_output_metrics', 'data'),
)
def get_training_needed_energy(inference_form_metrics):
    return metrics_utils.format_CE_text(inference_form_metrics['carbonEmissions'])
