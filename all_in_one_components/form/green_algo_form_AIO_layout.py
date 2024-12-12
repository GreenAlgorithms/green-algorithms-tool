from dash import html, dcc
from utils.utils import YES_NO_OPTIONS
from utils.handle_inputs import get_available_versions

from all_in_one_components.form.green_algo_form_AIO_ids import GreenAlgoFormIDS

appVersions_options = get_available_versions()

def get_green_algo_form_layout(aio_id, title, subtitle):
    ids = GreenAlgoFormIDS()
    return [
                dcc.Store(id=ids.aggregate_data(aio_id)),
                html.H2(title),
                html.Center(subtitle),

                ## RUN TIME
                html.Div(
                    [
                        html.Label("Runtime (HH:MM)"),

                        html.Div(
                            [
                                dcc.Input(
                                    type='number',
                                    id=ids.runTime_hour_input(aio_id),
                                    min=0,
                                ),

                                dcc.Input(
                                    type='number',
                                    id=ids.runTime_min_input(aio_id),
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
                                    id=ids.coreType_dropdown(aio_id),
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
                            id=ids.title_CPU(aio_id),
                        ),

                        html.Div(
                            [
                                html.Label("Number of cores"),

                                dcc.Input(
                                    type='number',
                                    id=ids.numberCPUs_input(aio_id),
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
                                            id=ids.CPUmodel_dropdown(aio_id),
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
                                    id=ids.tdpCPU_input(aio_id),
                                    min=0,
                                )
                            ],
                            className='form-row',
                            id=ids.tdpCPU_div(aio_id),
                            style=dict(display='none')
                        ),
                    ],
                    className="group-of-rows",
                    id=ids.CPU_div(aio_id),
                ),

                ## GPUs
                html.Div(
                    [
                        html.H3(
                            "GPUs",
                            id=ids.title_GPU(aio_id),
                        ),

                        html.Div(
                            [
                                html.Label("Number of GPUs"),

                                dcc.Input(
                                    type='number',
                                    id=ids.numberGPUs_input(aio_id),
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
                                            id=ids.GPUmodel_dropdown(aio_id),
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
                                    id=ids.tdpGPU_input(aio_id),
                                    min=0,
                                )
                            ],
                            className='form-row',
                            id=ids.tdpGPU_div(aio_id),
                            style=dict(display='none')
                        ),
                    ],
                    className="group-of-rows",
                    id=ids.GPU_div(aio_id),
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
                            id=ids.memory_input(aio_id),
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
                    id=ids.div_memory(aio_id),
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
                                    id=ids.platformType_dropdown(aio_id),
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
                                    id=ids.provider_dropdown(aio_id),
                                    clearable=False,
                                    className='bottom-dropdown',
                                ),
                            ],
                            className="box-fields",
                            id=ids.provider_dropdown_div(aio_id),
                        ),
                    ],
                    className='form-row'
                ),


                ## SERVER (for cloud computing)
                html.Div(
                    [
                        html.Label("Select server"),

                        html.Div(
                            [
                                dcc.Dropdown(
                                    id=ids.server_continent_dropdown(aio_id),
                                    clearable=False,
                                ),

                                dcc.Dropdown(
                                    id=ids.server_dropdown(aio_id),
                                    clearable=False,
                                    className='bottom-dropdown',
                                ),
                            ],
                            className="box-fields"
                        )
                    ],
                    id=ids.server_div(aio_id),
                    className='form-row',
                    style={'display': 'none'}
                ),

                ## LOCATION
                html.Div(
                    [
                        html.Label("Select location"),

                        html.Div(
                            [
                                dcc.Dropdown(
                                    id=ids.location_continent_dropdown(aio_id),
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
                                    id=ids.location_country_dropdown(aio_id),
                                    className='bottom-dropdown',
                                    clearable=False,
                                ),
                            ],
                            className="box-fields",
                            id=ids.location_country_dropdown_div(aio_id),
                        ),

                        html.Div(
                            [
                                dcc.Dropdown(
                                    id=ids.location_region_dropdown(aio_id),
                                    className='bottom-dropdown',
                                    clearable=False,
                                ),
                            ],
                            className="box-fields",
                            id=ids.location_region_dropdown_div(aio_id),
                        ),
                    ],
                    id=ids.location_div(aio_id),
                    className='form-row',
                    style={'display': 'flex'}
                ),

                ## CORE USAGE (CPU and GPU)
                html.Div(
                    [
                        html.Label("Do you know the real usage factor of your CPU?"),
                        
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id=ids.usageCPU_radio(aio_id),
                                    options=YES_NO_OPTIONS,
                                    className="radio-input",
                                ),
                                dcc.Input(
                                    min=0,
                                    max=1,
                                    # step=0.1,
                                    type='number',
                                    id=ids.usageCPU_input(aio_id),
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
                    id=ids.usageCPU_div(aio_id),
                ),

                html.Div(
                    [
                        html.Label("Do you know the real usage factor of your GPU?"),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id=ids.usageGPU_radio(aio_id),
                                    options=YES_NO_OPTIONS,
                                    className="radio-input",
                                ),

                                dcc.Input(
                                    min=0,
                                    max=1,
                                    # step=0.1,
                                    type='number',
                                    id=ids.usageGPU_input(aio_id),
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
                    id=ids.usageGPU_div(aio_id),
                ),

                ## PUE
                html.Div(
                    [
                        html.Label("Do you know the Power Usage Efficiency (PUE) of your local data centre?"),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id=ids.pue_radio(aio_id),
                                    options=YES_NO_OPTIONS,
                                    className='radio-input',
                                ),

                                dcc.Input(
                                    min=1,
                                    type='number',
                                    id=ids.PUE_input(aio_id),
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
                    id=ids.PUEquestion_div(aio_id),
                    style=dict(display='none'),
                ),

                ## PSF
                html.Div(
                    [
                        html.Label("Do you want to use a Pragmatic Scaling Factor (PSF)?"),
                        html.Div(
                            [
                                dcc.RadioItems(
                                    id=ids.PSF_radio(aio_id),
                                    options=YES_NO_OPTIONS,
                                    className="radio-input",
                                ),

                                dcc.Input(
                                    min=1,
                                    type='number',
                                    id=ids.PSF_input(aio_id),
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
                ),

                dcc.ConfirmDialog(
                    id=ids.confirm_reset(aio_id),
                    message='This will reset all the values you have entered so far!\n' \
                    'Are you sure you want to continue?',
                ),

                html.Div(
                    [
                        html.Div(
                            [
                                html.P("Reset", id=ids.reset_link(aio_id)),
                            ],
                            className='reset-button'
                        ),
                        # html.Div(
                        #     [
                        #         html.P("Change app version", id='oldVersion_link'),
                        #     ],
                        #     className='reset-button'
                        # ),
                    ],
                    className='two-buttons'
                ),

                # html.Div(
                #     [
                #         html.Label("App version"),

                #         html.Div(
                #             [
                #                 dcc.Dropdown(
                #                     id="appVersions_dropdown",
                #                     options=appVersions_options,
                #                     className='bottom-dropdown',
                #                     clearable=False,
                #                 ),
                #             ],
                #             className="box-fields"
                #         )
                #     ],
                #     className='form-row short-input',
                #     id='oldVersions_div',
                #     style=dict(display='none'),
                # ),

                html.P(
                    id="placeholder",
                    style={"display": "none"}
                )

            ]