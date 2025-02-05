"""
The page itself is defined as a DashBlueprint that encompasses both layout and callbacks.

Contrary to the Home page, the Ai page requires more intermediate processing to obtain the metrics.
These are due to the continuous inference option and the possible retraining or R&D experiments to take into account.

These additional fields must be taken into account:
    - when exporting or loading data
    - when computing the results: we compute and show both the training and inference results, as well as their sum
"""


import os

from dash import html, Input, Output, State, dcc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from dash_extensions.enrich import DashBlueprint, html

from blueprints.form.form_blueprint import get_form_blueprint
from blueprints.import_export.import_export_blueprint import get_import_expot_blueprint
from blueprints.metrics.metrics_blueprint import get_metrics_blueprint
from blueprints.methodology.methodology_blueprint import get_methodology_blueprint

import blueprints.metrics.metrics_layout as metrics_layout
import blueprints.metrics.utils as metrics_utils
import blueprints.methodology.methodology_layout as methodo_layout
import blueprints.form.form_layout as form_layout

from utils.graphics import MY_COLORS
from utils.handle_inputs import get_available_versions, filter_wrong_inputs, clean_non_used_inputs_for_export,  open_input_csv_and_comment, read_base_form_inputs_from_csv, AI_PAGE_DEFAULT_VALUES, validate_ai_page_specific_inputs


###################################################
# PAGE CREATION

AI_PAGE = DashBlueprint()

AI_PAGE_ID_PREFIX = 'ai'


###################################################
# MODULES CREATION

TRAINING_ID_PREFIX = 'training'
training_form = get_form_blueprint(
    id_prefix=TRAINING_ID_PREFIX,
    title='',
    subtitle=html.P('Report your training-related computations. For more information about R&D experiments, '
                    'retraining or overall tips regarding your reporting, please refer to the Help tab.'),
    mult_factor_properties={'display': 'none'},
    additional_bottom_fields=form_layout.get_additional_training_fields_layout()
)

INFERENCE_ID_PREFIX = 'inference'
inference_form = get_form_blueprint(
    id_prefix=INFERENCE_ID_PREFIX,
    title='',
    subtitle=html.P('Report your inference-related computations. For more information about continuous inference'
                    ' or overall tips regarding your reporting, please refer to the Help tab.'),
    continuous_inf_scheme_properties={'display': 'block'}
)

### WARNING: the csv_flushing_delay below should not be lower than 
# 2000 milliseconds to avoid rendering bugs of the server fields
import_export = get_import_expot_blueprint(id_prefix=AI_PAGE_ID_PREFIX, csv_flushing_delay=2500) 

methodo_content = get_methodology_blueprint(
    id_prefix=AI_PAGE_ID_PREFIX,
    additional_formula_content=dcc.Markdown(
        '''
        The training and inference forms rely on the same base formula as the one used in the main
        page calculator. 
        When appropriate, retraining and R&D impacts are then added, and continuous inference impacts 
        are scaled to the reporting period.
        More information is provided by the tooltips and the help tabs.
        ''',
        style={'margin-bottom': '10px'}
    )
)

metrics = get_metrics_blueprint(
    id_prefix=AI_PAGE_ID_PREFIX,
    energy_needed_details=metrics_layout.get_metric_per_form_layout(
        training_id=f'{TRAINING_ID_PREFIX}-energy_needed',
        inference_id=f'{INFERENCE_ID_PREFIX}-energy_needed',
    ),
    carbon_footprint_details=metrics_layout.get_metric_per_form_layout(
        training_id=f'{TRAINING_ID_PREFIX}-carbon_emissions',
        inference_id=f'{INFERENCE_ID_PREFIX}-carbon_emissions',
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
                    html.H2('The Green Algorithms calculator, adapted for artificial intelligence'),
                    html.P([
                            "This new page is especially dedicated to AI-related computations, ",
                            "where compute is usually divided between training and inference phases. ",
                            "The method is the same as in the original tool, ",
                            "it simply facilitates the reporting of AI systems' environmental impacts ",
                            "over a fixed period of time, e.g. one year."
                        ])
                ],
                className='container'
            ),

            #### IMPORT AND EXPORT ####

            import_export.embed(AI_PAGE),

            # The following intermediate variable contains the fields imported by csv upload that cannot
            # be handled at the form level because they are specific to the AI page:
            # the reporting scope, the continuous inference related fields, retrainings and R&D training fields
            dcc.Store(id='specific_ai_page_inputs'),

            #### FORMS ####

            html.Div(
                [
                    #### REPORTING SCOPE ####

                    html.Div(
                        [
                            html.H3("Reporting period"),

                            html.P(
                                [
                                    'The reporting period is the period of time over which you want to estimate '
                                    'the environmental impacts of your AI system (training and inference). '
                                    'This is particularly relevant in the case of ongoing deployment of the system. '
                                    'Typical values might be one year or the whole estimated lifespan of your system. ',
                                ],
                                className='reporting-scope-text'
                            ),

                            html.P(
                                [
                                    'The value is only used by the calculator when you select "continuous inference" '
                                    'to report the total energy and carbon footprint over the reporting period. '
                                    'It is nonetheless good practice to enter it to clarify the scope of your '
                                    'estimations.',
                                ],
                                className='reporting-scope-text text-italic'
                            ),
                                  
                            html.Div(
                                [
                                    dcc.Input(
                                        type='number',
                                        id='reporting_time_scope_input',
                                        min=0.5,
                                        value=1,
                                    ),

                                    html.Div(
                                        [
                                            dcc.Dropdown(
                                                id='reporting_time_scope_dropdown',
                                                options=[
                                                        {'label': 'Month(s)', 'value': 'month'},
                                                        {'label': 'Year(s)', 'value': 'year'},
                                                    ],
                                                value='year',
                                                className='dropdown',
                                                clearable=False,
                                            ),
                                        ],
                                        className='box-fields'
                                    ),

                                    # I don't think a tooltip is needed there
                                    # html.Div(
                                    #     [
                                    #         html.Div('i', className='tooltip-icon'),
                                    #         html.P(
                                    #             "Fill in your reporting period.",
                                    #             className='tooltip-text'
                                    #         ),
                                    #     ],
                                    #     className='tooltip',
                                    # ),
                                ],
                                className="reporting-row short-input"
                            ),
                        ],
                        className='container',
                    ),

                    #### TRAINING FORM ####

                    # Variable containing the "final" training related results.
                    # It is computed from the training form's 'form_output_metrics'
                    #  and the retrainings/R&D training fields
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

                    # Variable containing the "final" inference related results.
                    # It is computed from the inference form's 'form_output_metrics' and 
                    # the reporting scope / continuous inference fields
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
                        
            #### METHODOLOGY CONTENT ####

            methodo_content.embed(AI_PAGE),

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
        Output(f'{TRAINING_ID_PREFIX}-form_data_imported_from_csv', 'data'),
        Output(f'{INFERENCE_ID_PREFIX}-form_data_imported_from_csv', 'data'),
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
        State('specific_ai_page_inputs', 'data'),
        State('app_versions_dropdown','value'),
    ]
)
def forward_imported_content_to_form(
    import_data: str,
    filename: str,
    current_training_form_data: dict,
    current_inference_form_data: dict,
    current_specific_ai_inputs: dict,
    current_app_version: str
):
    """
    Read input from uploaded CSV, split data between training and inference forms.
    Process specific inputs such as retraining, R&D training and continuous inference related fields.
    Then process and check content, filtering wrong inputs and displaying error message if required.
    """
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
            current_specific_ai_inputs
        )
    
    # If input data could be read, we check its validity and consistency
    else:
        mess_subtitle = ''
        # Processing inputs specific to the AI page
        # TODO: improve the error message based on the different error categories
        ai_page_specific_inputs_keys = [
            'reporting_time_scope_unit', 'reporting_time_scope_value', 'R&D_radio', 'R&D_MF_value',
            'retrainings_radio', 'retrainings_number_input', 'retrainings_MF_value', 'continuous_inference_switcher',
            'input_data_time_scope_unit', 'input_data_time_scope_val'
        ]
        clean_AI_inputs, invalid_AI_inputs = validate_ai_page_specific_inputs(input_dict=input_data, keys_of_interest=ai_page_specific_inputs_keys)
        for key in ai_page_specific_inputs_keys:
            if key not in clean_AI_inputs:
                clean_AI_inputs[key] = AI_PAGE_DEFAULT_VALUES[key]
        # Processing training data
        training_input_data = {key.replace(f'{TRAINING_ID_PREFIX}-', ''): value for key, value in input_data.items() if TRAINING_ID_PREFIX in key}
        if 'appVersion' in input_data:
            training_input_data['appVersion'] = input_data['appVersion']
        clean_training_input_data, invalid_training_inputs, app_version = read_base_form_inputs_from_csv(training_input_data)
        invalid_training_inputs = filter_wrong_inputs(clean_training_input_data, invalid_training_inputs)
        # Processing inference data
        inference_input_data = {key.replace(f'{INFERENCE_ID_PREFIX}-', ''): value for key, value in input_data.items() if INFERENCE_ID_PREFIX in key}
        if 'appVersion' in input_data:
            inference_input_data['appVersion'] = input_data['appVersion']
        clean_inference_input_data, invalid_inference_inputs, _ = read_base_form_inputs_from_csv(inference_input_data)
        invalid_inference_inputs = filter_wrong_inputs(clean_inference_input_data, invalid_inference_inputs)
        # Building error message
        if len(invalid_training_inputs) or len(invalid_inference_inputs) or len(invalid_AI_inputs):
            show_err_mess = True
            mess_subtitle += f'\n\nThere seems to be some typos in the csv columns name or ' \
                             f'inconsistencies in its values. We use default values for the following fields. \n'
            if len(invalid_AI_inputs):
                mess_content += 'Regarding the AI page specific inputs: '
                mess_content += f"{', '.join(list(invalid_AI_inputs.keys()))}. \n"
            if len(invalid_training_inputs):
                mess_content += 'For the training form: '
                mess_content += f"{', '.join(list(invalid_training_inputs.keys()))}. \n"
            if len(invalid_inference_inputs):
                mess_content += 'For the inference form: '
                mess_content += f"{', '.join(list(invalid_inference_inputs.keys()))}."
        return (
            clean_training_input_data, 
            clean_inference_input_data, 
            show_err_mess, 
            mess_subtitle, 
            mess_content, 
            app_version,
            clean_AI_inputs,
        )  


@AI_PAGE.callback(
        [
            Output('reporting_time_scope_dropdown', 'value'),
            Output('reporting_time_scope_input', 'value'),
        ],
        [
            # To force initial triggering
            Input('url_content','search'),
            Input('specific_ai_page_inputs', 'data'),
        ]
)
def forward_reporting_scope_inputs(_, specific_ai_inputs: dict):
    """
    Args:
        specific_ai_inputs (dict): the dictionnary of inputs that cannot
        be handled at the form level because they are specific to the AI page.
    """
    if specific_ai_inputs:
        return (
            specific_ai_inputs['reporting_time_scope_unit'],
            specific_ai_inputs['reporting_time_scope_value'],
        )
    else:
        # otherwise we return default values
        return (
            AI_PAGE_DEFAULT_VALUES['reporting_time_scope_unit'],
            AI_PAGE_DEFAULT_VALUES['reporting_time_scope_value'], 
        )


@AI_PAGE.callback(
        [
            Output(f'{TRAINING_ID_PREFIX}-RandD_radio','value'),
            Output(f'{TRAINING_ID_PREFIX}-RandD_MF_input','value'),
            Output(f'{TRAINING_ID_PREFIX}-retrainings_radio','value'),
            Output(f'{TRAINING_ID_PREFIX}-retrainings_number_input', 'value'),
            Output(f'{TRAINING_ID_PREFIX}-retrainings_MF_input','value'),
        ],
        [
            # To force initial triggering
            Input('url_content','search'),
            Input('specific_ai_page_inputs', 'data'),
        ]
)
def load_RandD_and_retrainings_inputs(_, specific_ai_inputs: dict):
    """
    Forward inputs from the csv to retrainings and R&D fields.
    If not, fill in with default values, for instance when loading the page.
    """
    if specific_ai_inputs:
        return (
            specific_ai_inputs['R&D_radio'],
            specific_ai_inputs['R&D_MF_value'],
            specific_ai_inputs['retrainings_radio'],
            specific_ai_inputs['retrainings_number_input'],
            specific_ai_inputs['retrainings_MF_value'],
        )
    else:
        # otherwise we return default values
        return (
            AI_PAGE_DEFAULT_VALUES['R&D_radio'],
            AI_PAGE_DEFAULT_VALUES['R&D_MF_value'],
            AI_PAGE_DEFAULT_VALUES['retrainings_radio'],
            AI_PAGE_DEFAULT_VALUES['retrainings_number_input'], 
            AI_PAGE_DEFAULT_VALUES['retrainings_MF_value'], 
        )


@AI_PAGE.callback(
        [
            Output(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
            Output(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_dropdown', 'value'),
            Output(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_input', 'value'),
        ],
        [
            # To force initial triggering
            Input('url_content','search'),
            Input('specific_ai_page_inputs', 'data'),
        ]
)
def load_inference_specific_inputs(_, specific_ai_inputs: dict):
    """
    Forward inputs from the csv to input data time scope and continuous inference field.
    If not, fill in with default values, for instance when loading the page.
    """
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

################## CONTINUOUS INFERENCE SECTION

@AI_PAGE.callback(
    [
        Output(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_section', 'style'),
        Output(f'{INFERENCE_ID_PREFIX}-mult_factor_div', 'style'),
        Output(f'{INFERENCE_ID_PREFIX}-mult_factor_radio', 'value', allow_duplicate=True),
        Output(f'{INFERENCE_ID_PREFIX}-mult_factor_input', 'value', allow_duplicate=True),
    ],
    Input(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
    prevent_initial_call = True
)
def adapt_the_form_depending_on_inference_mode(is_inference_continuous):
    if is_inference_continuous:
        return {'diplay': 'block'}, {'display': 'none'}, 'No', 1
    return {'display': 'none'}, {'display': 'flex'}, 'No', 1


################## ADDITIONAL TRAININGS FIELDS SECTIONS

@AI_PAGE.callback(
    Output(f'{TRAINING_ID_PREFIX}-RandD_MF_input','style'),
    [
        Input(f'{TRAINING_ID_PREFIX}-RandD_radio', 'value'),
        Input(f'{TRAINING_ID_PREFIX}-RandD_MF_input','disabled')
    ]
)
def display_RandD_trainings_input(RandD_trainings_radio, disabled):
    """
    Shows or hides the  R&D trainings input box
    """
    if RandD_trainings_radio == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'block'}

    if disabled:
        out['background-color'] = MY_COLORS['boxesColor']

    return out


@AI_PAGE.callback(
    Output(f'{TRAINING_ID_PREFIX}-retraining-additional-inputs', 'style'),
    [
        Input(f'{TRAINING_ID_PREFIX}-retrainings_radio', 'value'),
    ]
)
def display_retrainings_div(retrainings_radio):
    """
    Shows or hides the retrainings input fields
    """
    if retrainings_radio == 'No':
        out = {'display': 'none'}
    else:
        out = {'display': 'flex', 'flex-direction': 'column'}

    return out


################## EXPORT DATA

@AI_PAGE.callback(
        Output(f'{AI_PAGE_ID_PREFIX}-export-content', 'data'),
        Input(f"{AI_PAGE_ID_PREFIX}-btn-download_csv", "n_clicks"),
        [
            State(f'reporting_time_scope_input', 'value'),
            State(f'reporting_time_scope_dropdown', 'value'),
            State(f'{TRAINING_ID_PREFIX}-form_aggregate_data', 'data'),
            State(f'training_processed_output_metrics', 'data'),
            State(f'{INFERENCE_ID_PREFIX}-form_aggregate_data', 'data'),
            State(f'inference_processed_output_metrics', 'data'),
            State(f'{TRAINING_ID_PREFIX}-retrainings_radio', 'value'),
            State(f'{TRAINING_ID_PREFIX}-retrainings_number_input', 'value'),
            State(f'{TRAINING_ID_PREFIX}-retrainings_MF_input', 'value'),
            State(f'{TRAINING_ID_PREFIX}-RandD_radio', 'value'),
            State(f'{TRAINING_ID_PREFIX}-RandD_MF_input', 'value'),
            State(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_input', 'value'),
            State(f'{INFERENCE_ID_PREFIX}-input_data_time_scope_dropdown', 'value'),
            State(f'{INFERENCE_ID_PREFIX}-continuous_inference_scheme_switcher', 'checked'),
            State(f'{AI_PAGE_ID_PREFIX}-base_results', 'data'),
        ],
        prevent_initial_call=True,
)
def forward_form_input_to_export_module(
    _,
    reporting_time_val: int,
    reporting_time_unit: str,
    training_form_agg_data: dict,
    training_form_outputs: dict,
    inference_form_agg_data: dict,
    inference_form_outputs: dict,
    retraining_radio: str,
    retraining_number_val: float,
    retraining_MF_val: float,
    RandD_radio: str,
    RandD_MF_val: float,
    input_data_time_scope_val: int,
    input_data_time_scope_unit: str,
    inference_continuous_activated: bool,
    ai_aggregated_results: dict,
):
    """
    Intermediate processing specific to the AI page before exporting data.
    Cleans content to export by standardizing non-used inputs.
    We concatenate the content of the training form and inference form into a single dictionnary to be exported.

    Even if no retrainings, R&D experiments or even if the continuous inference scheme, we
    add the intermediate results to the CSV so the CSV are homogeneous.
    """
    forms_aggregate_data = {}
    # Forward global inputs
    forms_aggregate_data['appVersion'] = training_form_agg_data['appVersion']
    forms_aggregate_data['reporting_time_scope_unit'] = reporting_time_unit
    forms_aggregate_data['reporting_time_scope_value'] = reporting_time_val
    # Clean non-used inputs
    training_data = clean_non_used_inputs_for_export(training_form_agg_data)
    inference_data = clean_non_used_inputs_for_export(inference_form_agg_data)
    # Add prefix to differentiate between training and inference
    training_data = {f'training-{key}': value for key, value in training_data.items() if key != 'appVersion'}
    training_outputs = {f'training-{key}': value for key, value in training_form_outputs.items()}
    inference_data = {f'inference-{key}': value for key, value in inference_data.items() if key != 'appVersion'}
    inference_outputs = {f'inference-{key}': value for key, value in inference_form_outputs.items()}
    # Add training additional fields - retrainings and R&D trainings
    if retraining_radio == 'No':
        retraining_MF_val = 0
    ### WARNING: should not put the word 'training' in the key of the retraining items
    training_data['retrainings_radio'] = retraining_radio
    training_data['retrainings_MF_value'] = retraining_MF_val
    training_data['retrainings_number_input'] = retraining_number_val
    if RandD_radio == 'No':
        RandD_MF_val = 0
    training_data['R&D_radio'] = RandD_radio
    training_data['R&D_MF_value'] = RandD_MF_val
    # Add inference additional fields - continuous inference scheme
    inference_data['continuous_inference_switcher'] = inference_continuous_activated
    inference_data['input_data_time_scope_unit'] = input_data_time_scope_unit
    inference_data['input_data_time_scope_val'] = input_data_time_scope_val
    # Concatenate training and inference data
    forms_aggregate_data.update(training_data)
    forms_aggregate_data.update(training_outputs)
    forms_aggregate_data.update(inference_data)
    forms_aggregate_data.update(inference_outputs)
    forms_aggregate_data['tot_energy_needed'] = ai_aggregated_results['energy_needed']
    forms_aggregate_data['tot_carbonEmissions'] = ai_aggregated_results['carbonEmissions']
    return forms_aggregate_data


################## RESULTS AND METRICS 

## Once we process training and inference fields to 
## get their final energy consumption and carbon emissions,
## we store them in intermediate variables that are used to show the final results


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
    """
    The purpose of this callback is to take into account the reporting scope
    in case continuous inference scheme is selected by the user.
    It automatically scales the end electricity consumption based on reporting scope and
    and the input data time scope.
    """
    processed_inference_metrics = {}
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
    else:
        mult_coef = 1
    processed_inference_metrics['energy_needed_before_scaling'] =  inference_form_metrics['energy_needed']
    processed_inference_metrics['energy_needed'] = mult_coef * inference_form_metrics['energy_needed']
    processed_inference_metrics['carbonEmissions_before_scaling'] =  inference_form_metrics['carbonEmissions']
    processed_inference_metrics['carbonEmissions'] = mult_coef * inference_form_metrics['carbonEmissions']
    return processed_inference_metrics
    

@AI_PAGE.callback(
        Output('training_processed_output_metrics', 'data'),
        [
            Input(f'{TRAINING_ID_PREFIX}-form_output_metrics', 'data'),
            Input(f'{TRAINING_ID_PREFIX}-retrainings_radio', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-retrainings_number_input', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-retrainings_MF_input', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-RandD_radio', 'value'),
            Input(f'{TRAINING_ID_PREFIX}-RandD_MF_input', 'value'),
        ]
)
def add_retrainings_and_RandD_to_training_outputs(
    training_form_metrics: dict,
    retraining_radio: str,
    retraining_number_val: float,
    retraining_MF_val: float,
    RandD_radio: str,
    RandD_MF_val: float,
):
    """
    The purpose of this callback is to take into account retrainings and R&D inputs.
    The main training form outputs (energy consumption and carbon emissions) are
    multiplied by the corresponding multiplicative factor for both retrainings and R&D
    before they are added to the total.
    """
    # Handling wrong inputs from the user
    if retraining_MF_val is None:
        retraining_MF_val = 0
    if retraining_number_val is None:
        retraining_number_val = 0
    if RandD_MF_val is None:
        RandD_MF_val = 0
    # Checking if values should be added from retrainings or RandD
    if retraining_radio == 'No':
        retraining_MF_val = 0
        retraining_number_val = 0
    if RandD_radio == 'No':
        RandD_MF_val = 0
    # Add values to main training metrics
    detailed_training_metrics = {}
    detailed_training_metrics['main_energy_needed'] = training_form_metrics['energy_needed']
    detailed_training_metrics['R&D_energy_needed'] = training_form_metrics['energy_needed'] * RandD_MF_val 
    detailed_training_metrics['retrainings_energy_needed'] = training_form_metrics['energy_needed'] * retraining_MF_val * retraining_number_val
    detailed_training_metrics['energy_needed'] = training_form_metrics['energy_needed'] * (1 + RandD_MF_val + retraining_MF_val * retraining_number_val)
    detailed_training_metrics['main_carbonEmissions'] = training_form_metrics['carbonEmissions']
    detailed_training_metrics['R&D_carbonEmissions'] = training_form_metrics['carbonEmissions'] *  RandD_MF_val 
    detailed_training_metrics['retrainings_carbonEmissions'] = training_form_metrics['carbonEmissions'] *  retraining_MF_val * retraining_number_val
    detailed_training_metrics['carbonEmissions'] = training_form_metrics['carbonEmissions'] * (1 + RandD_MF_val + retraining_MF_val * retraining_number_val)
    return detailed_training_metrics


@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-base_results', 'data'),
    [ 
        Input('training_processed_output_metrics', 'data'),
        Input('inference_processed_output_metrics', 'data'),
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
    Input('training_processed_output_metrics', 'data'),
)
def get_training_needed_energy(training_form_metrics):
    return metrics_utils.format_energy_text(training_form_metrics['energy_needed'])

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{INFERENCE_ID_PREFIX}-energy_needed', 'children'),
    Input('inference_processed_output_metrics', 'data'),
)
def get_training_needed_energy(inference_form_metrics):
    return metrics_utils.format_energy_text(inference_form_metrics['energy_needed'])

# Carbon emissions
@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{TRAINING_ID_PREFIX}-carbon_emissions', 'children'),
    Input('training_processed_output_metrics', 'data'),
)
def get_training_needed_energy(training_form_metrics):
    return metrics_utils.format_CE_text(training_form_metrics['carbonEmissions'])

@AI_PAGE.callback(
    Output(f'{AI_PAGE_ID_PREFIX}-{INFERENCE_ID_PREFIX}-carbon_emissions', 'children'),
    Input('inference_processed_output_metrics', 'data'),
)
def get_training_needed_energy(inference_form_metrics):
    return metrics_utils.format_CE_text(inference_form_metrics['carbonEmissions'])
