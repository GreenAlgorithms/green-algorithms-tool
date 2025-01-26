from dash import html, dcc
import dash_mantine_components as dmc
from utils.utils import YES_NO_OPTIONS
from utils.handle_inputs import get_available_versions

appVersions_options = get_available_versions()

def get_green_algo_form_layout(
    title: str,
    subtitle: html.P,
    continuous_inf_scheme_properties: dict,
    PSF_properties: dict,
    additional_bottom_fields: html.Div,
):
    return html.Form(
        [
            html.H3(title),
            html.Center(subtitle),

            ## BACKEND DATA
            dcc.Store(id='from_input_data'),
            dcc.Store(id='form_aggregate_data'),
            dcc.Store(id='form_output_metrics'),

            ## CONTINUOUS INFERENCE SCHEME

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
                                        "Please see the Help tab for more information about continuous inference. If chosen, then only report the computations falling within your ‘input data time span’. Scaling to the reporting time scope is done automatically.",
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
                                        "The input data time span is the time length over which you are able to estimate your computation requirements in terms of continuous inference.",
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

            ## RUN TIME
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

            ## TYPE OF CORES
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

            ## CPUs
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
                                        "A single CPU contains several cores.",
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
                                        "To fill-in a custom core power usage (TDP), please select 'other'.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                            
                        ],
                        className='form-row short-input'
                    ),

                    # CPU TDP
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

            ## GPUs
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
                                        "Here, we ask for the number of GPUs (not the cores).",
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
                                        "To fill-in a custom TDP, please select 'other'.",
                                        className='tooltip-text'
                                    ),
                                ],
                                className='tooltip',
                            ),
                        ],
                        className='form-row short-input'
                    ),

                    # GPU TDP
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

            ## MEMORY
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
                                "We refer to the ‘allocated memory’, not the memory actually used by the program.",
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

            ## SELECT COMPUTING PLATFORM
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
                                "This field enables us to retrieve the PUE and energy mix associated with your computations.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),    

                    ## SELECT PROVIDER, FOR CLOUD COMPUTING ONLY
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


            ## SERVER (for cloud computing)
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

            ## LOCATION
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
                                "In particular, the location is used to retrieve the energy mix.",
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

            ## CORE USAGE (CPU and GPU)
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
                                "Between 0 and 1. Should correspond to a temporal factor usage, accessible from log files for instance.",
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
                                "Between 0 and 1. In most cases, should be 1.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),                            
                ],
                className='form-row radio-row',
                id='usageGPU_div',
            ),

            ## PUE
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
                                "The PUE accounts for the extra energy consumption of the data centre, including cooling (1.67 by default).",
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

            ## PSF
            html.Div(
                [
                    html.Label("Do you want to use a Pragmatic Scaling Factor (PSF)?"),
                    html.Div(
                        [
                            dcc.RadioItems(
                                id='PSF_radio',
                                options=YES_NO_OPTIONS,
                                className="radio-input",
                            ),

                            dcc.Input(
                                min=1,
                                type='number',
                                id='PSF_input',
                                style=dict(display='none'),
                            ),
                        ],
                        className='radio-and-field',
                    ),

                    html.Div(
                        [
                            html.Div('i', className='tooltip-icon'),
                            html.P(
                                "The PSF refers to the number of repetions of the computation.",
                                className='tooltip-text'
                            ),
                        ],
                        className='tooltip',
                    ),

                ],
                className='form-row radio-row',
                style=PSF_properties,
                id='PSF_div'
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
                "R&D TRAININGS",
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
                                "If your R&D trainings represent twice the computations requirements of your main training, you should fill in '2'. " \
                                "If they represent only 50% of your main training compute time, then fill in '0.5'. "
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
                "RETRAININGS",
                id='title_RandD_trainings',
            ),

            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Do you want to add retrainings compute time?"),

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
                                        "If you plan to apply retrainings, select 'Yes'. " \
                                        "Then, fill in the number of retrainings and their average relative requirements.",
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
                                    html.Label("Number of retrainings"),

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
                                                "Simply the number of retrainings you plan to apply over your reporting scope.",
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
                                    html.Label("What is the relative length of an average retraining compared to your main training?"),

                                    dcc.Input(
                                        min=0,
                                        type='number',
                                        id='retrainings_MF_input',
                                    ),

                                    html.Div(
                                        [
                                            html.Div('i', className='tooltip-icon'),
                                            html.P(
                                                "If an average retraining represents half the computations requirements of your main training, you should fill in '0.5'. ",
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
        