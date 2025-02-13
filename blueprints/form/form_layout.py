''''
This script implements:
    - the layout of the Form module
    - the layout of the retraining and R&D training sections 

TODO: move the continuous inference scheme section to a specific function instead of being part of the base Form layout.
'''

from dash import html, dcc
import dash_mantine_components as dmc
from utils.utils import YES_NO_OPTIONS
from utils.handle_inputs import get_available_versions

appVersions_options = get_available_versions()

# FIXME the margins on the tooltips are a bit tight


def get_green_algo_form_layout(
    title: str,
    subtitle: html.P,
    continuous_inf_scheme_properties: dict,
    mult_factor_properties: dict,
    additional_bottom_fields: html.Div,
):
    return html.Form(
        [
            #### BACKEND DATA ####

            # Obtained through intermediate processing applied to the import-content of a page
            # Once it is updated, it is used to spread uploaded data to the corresponding form fields
            dcc.Store(id='form_data_imported_from_csv'),

            # The following two components are form outputs: form_aggregate_data is the collection
            # of all fields required to replicate the whole form, form_output_metrics is the collection
            # of raw metrics (electricity consumption, carbon emissions...) that will be forwarded
            # to the results section
            dcc.Store(id='form_aggregate_data'),
            dcc.Store(id='form_output_metrics'),

            #### FORM HEADER ####

            html.H3(title),
            html.Center(subtitle),

            #### CONTINUOUS INFERENCE SCHEME ####

            html.Div(
                [
                    html.Div(
                        [
                            dmc.Switch(
                                size="lg",
                                radius="xl",
                                label="Apply continuous inference scheme",
                                checked=False,
                                id='continuous_inference_scheme_switcher',
                                className = 'continuous-switcher'
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "See the Help tab for more information about continuous inference. "
                                        "If chosen, then only report the computations falling "
                                        "within your ‘input data time span’. "
                                        "Scaling to the reporting period is done automatically.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='switcher-section'
                    ),

                    html.Div(
                        [
                            html.Label("Input data time span"),

                            dcc.Input(
                                type='number',
                                id='input_data_time_scope_input',
                                min=0.5,
                                value=1,
                                step=0.5,
                            ),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id='input_data_time_scope_dropdown',
                                        options=[
                                                {'label': 'Day(s)', 'value': 'day'},
                                                {'label': 'Week(s)', 'value': 'week'},
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

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "The `input data time span` is the length of time over which you are able "
                                        "to estimate your resource usage for continuous inference.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className="input_data_time-section form-row short-input",
                        id='input_data_time_scope_section'
                    ),

                    html.Div(
                        [
                            html.Hr(),
                        ],
                        className='Hr_div'
                    ),
                
                ],
                style=continuous_inf_scheme_properties,
            ),

            #### RUN TIME ####

            html.Div(
                [
                    html.Label("Runtime (HH:MM)"),

                    html.Div(
                        [
                            dcc.Input(
                                type='number',
                                id='runTime_hour_input',
                                min=0,
                            ),

                            dcc.Input(
                                type='number',
                                id='runTime_min_input',
                                min=0,
                                max=59,
                            )
                        ],
                        className="box-runtime box-fields"
                    ),
                ],
                className='form-row short-input'
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div'
            ),

            #### TYPE OF CORES ####

            html.Div(
                [
                    html.Label("Type of cores"),

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='coreType_dropdown',
                                clearable=False,
                            ),
                        ],
                        className="box-fields"
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "Select the type of hardware used.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),
                ],
                className='form-row short-input'
            ),

            #### CPUs ####

            html.Div(
                [
                    html.H3(
                        "CPUs",
                        id='title_CPU',
                    ),

                    html.Div(
                        [
                            html.Label("Number of cores"),

                            dcc.Input(
                                type='number',
                                id='numberCPUs_input',
                                min=0,
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Refers to the number of cores used (a single CPU contains several cores).",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    html.Div(
                        [
                            html.Label("Model"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id='CPUmodel_dropdown',
                                        className='bottom-dropdown',
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields"
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Select 'other' to fill-in a custom core power usage (TDP).",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                            
                        ],
                        className='form-row short-input'
                    ),

                    #### CPU TDP

                    html.Div(
                        [
                            html.Label(
                                'What is the Thermal Design Power (TDP) value per core of your CPU? '
                                'This can easily be found online (usually 10-15W per core)'),

                            dcc.Input(
                                type='number',
                                id='tdpCPU_input',
                                min=0,
                            )
                        ],
                        className='form-row TDP',
                        id='tdpCPU_div',
                        style=dict(display='none')
                    ),
                ],
                className="group-of-rows",
                id='CPU_div',
            ),

            #### GPUs ####

            html.Div(
                [
                    html.H3(
                        "GPUs",
                        id='title_GPU',
                    ),

                    html.Div(
                        [
                            html.Label("Number of GPUs"),

                            dcc.Input(
                                type='number',
                                id='numberGPUs_input',
                                min=0,
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Refers to the number of GPUs used (no cores here).",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    html.Div(
                        [
                            html.Label("Model"),

                            html.Div(
                                [
                                    dcc.Dropdown(
                                        id='GPUmodel_dropdown',
                                        className='bottom-dropdown',
                                        clearable=False,
                                    ),
                                ],
                                className="box-fields"
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Select 'other' to fill-in a custom TDP.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    #### GPU TDP

                    html.Div(
                        [
                            html.Label(
                                'What is the Thermal Design Power (TDP) value per core of your GPU? '
                                'This can easily be found online (usually around 200W)'),

                            dcc.Input(
                                type='number',
                                id='tdpGPU_input',
                                min=0,
                            )
                        ],
                        className='form-row TDP',
                        id='tdpGPU_div',
                        style=dict(display='none')
                    ),
                ],
                className="group-of-rows",
                id='GPU_div',
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div'
            ),

            #### MEMORY ####

            html.Div(
                [
                    html.Label("Memory available (in GB)"),

                    dcc.Input(
                        type='number',
                        id='memory_input',
                        min=0,
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "Refers to the total memory allocated to the task, "
                                "not the memory actually used.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),
                ],
                className='form-row short-input',
                id='div_memory',
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div'
            ),

            #### SELECT COMPUTING PLATFORM ####

            html.Div(
                [
                    html.Label("Select the platform used for the computations"),

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='platformType_dropdown',
                                clearable=False,
                            ),
                        ],
                        className='box-fields',
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "This field is used to retrieve specific data centre efficiency metrics "
                                "and location energy mixes.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),    

                    #### SELECT PROVIDER, FOR CLOUD COMPUTING ONLY

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='provider_dropdown',
                                clearable=False,
                                className='bottom-dropdown',
                            ),
                        ],
                        className="box-fields",
                        id='provider_dropdown_div',
                    ),
                ],
                className='form-row long-input'
            ),


            #### SERVER (for cloud computing) ####

            html.Div(
                [
                    html.Label("Select server"),

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='server_continent_dropdown',
                                clearable=False,
                            ),

                            dcc.Dropdown(
                                id='server_dropdown',
                                clearable=False,
                                className='bottom-dropdown',
                            ),
                        ],
                        className="box-fields"
                    )
                ],
                id='server_div',
                className='form-row long-input',
                style={'display': 'none'}
            ),

            #### LOCATION ####

            # TODO add a display of the carbon intensity value used
            # TODO Give the option to input a custom carbon intensity value

            html.Div(
                [
                    html.Label("Select location"),

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='location_continent_dropdown',
                                clearable=False,
                            ),
                        ],
                        className="box-fields",
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "This is used to retrieve the energy mix in a location.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),   

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='location_country_dropdown',
                                className='bottom-dropdown',
                                clearable=False,
                            ),
                        ],
                        className="box-fields",
                        id='location_country_dropdown_div',
                    ),

                    html.Div(
                        [
                            dcc.Dropdown(
                                id='location_region_dropdown',
                                className='bottom-dropdown',
                                clearable=False,
                            ),
                        ],
                        className="box-fields",
                        id='location_region_dropdown_div',
                    ),
                ],
                id='location_div',
                className='form-row long-input',
                style={'display': 'flex'}
            ),

            #### CORE USAGE (CPU and GPU) ####

            html.Div(
                [
                    html.Label("Do you know the real usage factor of your CPU?"),
                    
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='usageCPU_radio',
                                options=YES_NO_OPTIONS,
                                className="radio-input",
                            ),
                            dcc.Input(
                                min=0,
                                max=1,
                                type='number',
                                id='usageCPU_input',
                                style=dict(display='none'),
                            )
                        ],
                        className='radio-and-field'
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "Between 0 and 1 (default: 1). This is the usage % of the cores, "
                                "e.g. % of the time the cores were active. "
                                "This can be obtained from log files for instance.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),
                ],
                className='form-row radio-row',
                id='usageCPU_div',
            ),

            html.Div(
                [
                    html.Label("Do you know the real usage factor of your GPU?"),
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='usageGPU_radio',
                                options=YES_NO_OPTIONS,
                                className="radio-input",
                            ),

                            dcc.Input(
                                min=0,
                                max=1,
                                type='number',
                                id='usageGPU_input',
                                style=dict(display='none'),
                            ),
                        ],
                        className='radio-and-field'
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "Between 0 and 1 (default: 1). This is the usage % of the GPUs, "
                                "e.g. % of the time the GPUs were active. "
                                "This can be obtained from log files for instance.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),                            
                ],
                className='form-row radio-row',
                id='usageGPU_div',
            ),

            #### PUE ####

            html.Div(
                [
                    html.Label("Do you know the Power Usage Efficiency (PUE) of your local data centre?"),
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='pue_radio',
                                options=YES_NO_OPTIONS,
                                className='radio-input',
                            ),

                            dcc.Input(
                                min=1,
                                type='number',
                                id='PUE_input',
                                style=dict(display='none'),
                            ),
                        ],
                        className='radio-and-field'
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "PUE is a standardised efficiency metrics measuring the"
                                "energy consumption of data centre overheads (e.g. cooling).",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),

                ],
                className='form-row radio-row',
                id='PUEquestion_div',
                style=dict(display='none'),
            ),

            #### MULTIPLICATIVE FACTOR ####

            html.Div(
                [
                    html.Label("Do you want to use a multiplicative factor?"),
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='mult_factor_radio',
                                options=YES_NO_OPTIONS,
                                className="radio-input",
                            ),

                            dcc.Input(
                                min=1,
                                type='number',
                                id='mult_factor_input',
                                style=dict(display='none'),
                            ),
                        ],
                        className='radio-and-field',
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "Used to multiply the final results, for example when a same task is repeated "
                                "multiple times.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),

                ],
                className='form-row radio-row',
                style=mult_factor_properties,
                id='mult_factor_div'
            ),

            dcc.ConfirmDialog(
                id='confirm_reset',
                message='This will reset all the values you have entered so far!\n' \
                'Are you sure you want to continue?',
            ),

            additional_bottom_fields,

            html.P(
                id="placeholder",
                style={"display": "none"}
            ),

        ],
        className='container input-form'
    )


def get_additional_training_fields_layout():
    return html.Div(
        [
            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div'
            ),

            #### R&D TRAININGS ####

            html.H3(
                "R&D TRAINING",
                id='title_RandD_trainings',
            ),
            
            html.Div(
                [
                    html.Label("Do you want to add R&D compute time?"),
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='RandD_radio',
                                options=YES_NO_OPTIONS,
                                className="radio-input",
                            ),

                            dcc.Input(
                                min=0,
                                type='number',
                                id='RandD_MF_input',
                                style=dict(display='none'),
                            ),
                        ],
                        className='radio-and-field',
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "Used to add R&D compute to the final training impact. "
                                "If in total you estimate your R&D training computes to represent "
                                "twice the compute of your final training run, input '2'. "
                                "If total R&D is about half of the final run, input '0.5'. "
                                "The resulting value will be added to your main training footprint.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),

                ],
                className='form-row radio-row',
            ),

            #### RETRAININGS ####

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div',
            ),

            html.H3(
                "RETRAINING",
                id='title_RandD_trainings',
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Do you want to add retraining compute time?"),

                            html.Div(
                                [
                                    dcc.RadioItems(
                                        id='retrainings_radio',
                                        options=YES_NO_OPTIONS,
                                        className="radio-input",
                                    ),
                                ],
                                className='radio-and-field',
                            ),

                            html.Div(
                                [
                                    html.Div('i', className='tooltip-icon'),
                                    html.P(
                                        "Used if you want to account for model retraining. ",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row radio-row',
                    ),

                    html.Div(
                        [
                            html.Div(
                                [
                                    html.Label("Number of runs"),

                                    dcc.Input(
                                        min=0,
                                        step=1,
                                        type='number',
                                        id='retrainings_number_input',
                                    ),

                                    
                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "Number of times you plan to retrain the model "
                                                "over the reporting period.",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                ],
                                className='form-row short-input'
                            ),

                            html.Div(
                                [
                                    html.Label("What is the relative runtime of an average retraining run "
                                               "compared to the main training?"),

                                    dcc.Input(
                                        min=0,
                                        type='number',
                                        id='retrainings_MF_input',
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "If retraining takes on average 10% of the "
                                                "runtime of the main training, input '0.1'.",
                                                className='tooltip-text'
                                            ),
                                        ],
                                        className='tooltip',
                                    ),
                                ],
                                className='form-row short-input'
                            ),
                        ],
                        id='retraining-additional-inputs',
                        style=dict(display='none'),
                    )
                ],
            ),
        ]
    )
        