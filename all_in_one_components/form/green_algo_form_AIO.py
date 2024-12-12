'''
Green Algorithm form as an All-in-One component
See here http://dash.plotly.com/all-in-one-components for the original convention.
'''
import pandas as pd

from dash import Output, Input, html, callback, MATCH
from types import SimpleNamespace

from utils.utils import put_value_first, is_shown
from utils.handle_inputs import availableLocations_continent, availableOptions_servers
from utils.graphics import MY_COLORS

from all_in_one_components.form.green_algo_form_AIO_layout import get_green_algo_form_layout
from all_in_one_components.form.green_algo_form_AIO_ids import GreenAlgoFormIDS

MAIN_FORM_ID = 'main-form'
TRAINING_FORM_ID = 'training-form'
INFERENCE_FORM_ID = 'inference-form'

class GreenAlgoFormAIO(html.Form): 
    ''' 
    An All-in-One component for the Green Algorithms Form.
    Formally, this class is just a convention, building a convenient wrapper
    for both the layout and the corresponding callbacks.
    None of the class-oriented concepts are used below 
    because we just want to make it consistent with Dash framework.
    
    The class inherits from the html.Form of Dash allowing native 
    compatibility for the layout. It also contains the stateless 
    pattern-matching callback that will apply to every instance of this component.
    ''' 

    ids = GreenAlgoFormIDS()

    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    def __init__(self, aio_id, title, subtitle):
        super().__init__(
            get_green_algo_form_layout(aio_id, title, subtitle),
            className='container input-form'
        )
        self.aio_id = aio_id



    ##### DEFINE ITS CALLBACKS
    ##########################

    ##################### PLATFORM AND PROVIDER ###

    @callback(
        Output(ids.platformType_dropdown(MATCH), 'options'),
        Input('versioned_data','data'),
    )
    def set_platform(data):
        '''
        Loads platform options based on backend data.
        '''
        if data is not None:
            data_dict = SimpleNamespace(**data)
            platformType_options = [
                {'label': k,
                'value': v} for v, k in list(data_dict.providersTypes.items()) +
                                        [('personalComputer', 'Personal computer')] +
                                        [('localServer', 'Local server')]
            ]
            return platformType_options
        else:
            return []

    @callback(
        Output(ids.provider_dropdown_div(MATCH), 'style'),
        Input(ids.platformType_dropdown(MATCH), 'value'),
    )
    def set_providers(selected_platform):
        '''
        Shows or hide the "providers" box, based on the platform selected.
        '''
        if selected_platform in ['cloudComputing']:
            # Only Cloud Computing need the providers box
            outputStyle = {'display': 'block'}
        else:
            outputStyle = {'display': 'none'}
        return outputStyle
    
    @callback(
        Output(ids.provider_dropdown(MATCH), 'options'),
        [
            Input(ids.platformType_dropdown(MATCH), 'value'),
            Input('versioned_data','data')
        ],
    )
    def set_providers(selected_platform, data):
        '''
        List options for the "provider" box.
        '''
        if data is not None:
            data_dict = SimpleNamespace(**data)

            providers_dict = data_dict.platformName_byType.get(selected_platform)
            if providers_dict is not None:
                availableOptions = list(providers_dict.items())
            else:
                availableOptions = []

            listOptions = [
                {'label': v, 'value': k} for k, v in availableOptions + [("other","Other")]
            ]
            return listOptions
        else:
            return []
        

    ##################### COMPUTING CORES ###

    @callback(
        Output(ids.coreType_dropdown(MATCH), 'options'),
        [
            Input(ids.provider_dropdown(MATCH), 'value'),
            Input(ids.platformType_dropdown(MATCH), 'value'),
            Input('versioned_data','data')
        ]
    )
    def set_coreType_options(_, __, data):
        '''
        List of options for coreType (CPU or GPU), based on the platform/provider selected.
        Not really useful so far because we have no specific core types for a given provider.
        '''
        if data is not None:
            data_dict = SimpleNamespace(**data)

            availableOptions = data_dict.cores_dict.keys()
            listOptions = [{'label': k, 'value': k} for k in list(sorted(availableOptions))+['Both']]
            return listOptions
        else:
            return []
        
    @callback(
        [
            Output(ids.CPUmodel_dropdown(MATCH), 'options'),
            Output(ids.GPUmodel_dropdown(MATCH), 'options')
        ],
        [Input('versioned_data','data')]
    )
    def set_coreOptions(data):
        '''
        List of options for core models.
        '''
        if data is not None:
            data_dict = SimpleNamespace(**data)

            coreModels_options = dict()
            for coreType in ['CPU', 'GPU']:
                availableOptions = sorted(list(data_dict.cores_dict[coreType].keys()))
                availableOptions = put_value_first(availableOptions, 'Any')
                coreModels_options[coreType] = [
                    {'label': k, 'value': v} for k, v in list(zip(availableOptions, availableOptions)) +
                    [("Other", "other")]
                ]

            return coreModels_options['CPU'], coreModels_options['GPU']

        else:
            return [],[]
        
    @callback(
        [
            Output(ids.CPU_div(MATCH), 'style'),
            Output(ids.title_CPU(MATCH), 'style'),
            Output(ids.usageCPU_div(MATCH), 'style'),
            Output(ids.GPU_div(MATCH), 'style'),
            Output(ids.title_GPU(MATCH), 'style'),
            Output(ids.usageGPU_div(MATCH), 'style'),
        ],
        [
            Input(ids.coreType_dropdown(MATCH), 'value')
        ]
    )
    def show_CPUGPUdiv(selected_coreType):
        '''
        Shows or hides the CPU/GPU input blocks (and the titles) based on the selected core type.
        '''
        show = {'display': 'block'}
        showFlex = {'display': 'flex'}
        hide = {'display': 'none'}
        if selected_coreType == 'CPU':
            return show, hide, showFlex, hide, hide, hide
        elif selected_coreType == 'GPU':
            return hide, hide, hide, show, hide, showFlex
        else:
            return show, show, showFlex, show, show, showFlex
        
    @callback(
        Output(ids.tdpCPU_div(MATCH), 'style'),
        [
            Input(ids.CPUmodel_dropdown(MATCH), 'value'),
        ]
    )
    def display_TDP4CPU(selected_coreModel):
        '''
        Shows or hides the CPU TDP input box.
        '''
        if selected_coreModel == "other":
            return {'display': 'flex'}
        else:
            return {'display': 'none'}
        
    @callback(
        Output(ids.tdpGPU_div(MATCH), 'style'),
        [
            Input(ids.GPUmodel_dropdown(MATCH), 'value'),
        ]
    )
    def display_TDP4GPU(selected_coreModel):
        '''
        Shows or hides the GPU TDP input box.
        '''
        if selected_coreModel == "other":
            return {'display': 'flex'}
        else:
            return {'display': 'none'}
    

    ##################### LOCATION AND SERVER ###

    @callback(
        [
            Output(ids.location_div(MATCH), 'style'),
            Output(ids.server_div(MATCH), 'style'),
        ],
        [
            Input(ids.platformType_dropdown(MATCH), 'value'),
            Input(ids.provider_dropdown(MATCH), 'value'),
            Input(ids.server_dropdown(MATCH),'value'),
            Input('versioned_data','data')
        ]
    )
    def display_location(selected_platform, selected_provider, selected_server, data):
        '''
        Shows either LOCATION or SERVER depending on the platform.
        '''
        if data is not None:
            data_dict = SimpleNamespace(**data)
            providers_withoutDC = data_dict.providers_withoutDC
        else:
            providers_withoutDC = []

        show = {'display': 'flex'}
        hide = {'display': 'none'}
        if selected_platform == 'cloudComputing':
            if selected_provider in ['other'] + providers_withoutDC:
                return show, hide
            elif selected_server == 'other':
                return show, show
            else:
                return hide, show
        else:
            return show, hide
        
    ### Server (only for Cloud computing for now)

    @callback(
        Output(ids.server_continent_dropdown(MATCH),'options'),
        [
            Input(ids.provider_dropdown(MATCH), 'value'),
            Input('versioned_data','data')
        ]
    )
    def set_serverContinents_options(selected_provider, data):
        '''
        List of options and default value for server's continent, based on the provider
        '''
        availableOptions = availableLocations_continent(selected_provider, data=data)
        listOptions = [{'label': k, 'value': k} for k in sorted(availableOptions)] + [{'label': 'Other', 'value': 'other'}]
        return listOptions
    
    @callback(
        Output(ids.server_dropdown(MATCH),'style'),
        Input(ids.server_continent_dropdown(MATCH), 'value'),
    )
    def set_server_style(selected_continent):
        '''
        Show or not the choice of servers, don't if continent is on "Other"
        '''
        if selected_continent == 'other':
            return {'display': 'none'}

        else:
            return {'display': 'block'}
        
    @callback(
        Output(ids.server_dropdown(MATCH),'options'),
        [
            Input(ids.provider_dropdown(MATCH), 'value'),
            Input(ids.server_continent_dropdown(MATCH), 'value'),
            Input('versioned_data','data')
        ]
    )
    def set_server_options(selected_provider,selected_continent, data):
        '''
        List of options for servers, based on provider and continent
        '''
        availableOptions = availableOptions_servers(selected_provider,selected_continent,data=data)
        listOptions = [{'label': k['Name'], 'value': k['name_unique']} for k in availableOptions + [{'Name':"other", 'name_unique':'other'}]]
        return listOptions
    
    
    ## Location (only for local server, personal device or "other" cloud server)

    @callback(
        Output(ids.location_continent_dropdown(MATCH), 'options'),
        [Input('versioned_data','data')]
    )
    def set_continentOptions(data):
        if data is not None:
            data_dict = SimpleNamespace(**data)

            continentsList = list(data_dict.CI_dict_byName.keys())
            continentsDict = [{'label': k, 'value': k} for k in sorted(continentsList)]

            return continentsDict
        else:
            return []
        
        
    ##################### USAGE FACTORS ###

    @callback(
        Output(ids.usageCPU_input(MATCH),'style'),
        [
            Input(ids.usageCPU_radio(MATCH), 'value'),
            Input(ids.usageCPU_input(MATCH), 'disabled')
        ]
    )
    def display_usage_input(answer_usage, disabled):
        '''
        Show or hide the usage factor input box, based on Yes/No input
        '''
        if answer_usage == 'No':
            out = {'display': 'none'}
        else:
            out = {'display': 'block'}

        if disabled:
            out['background-color'] = MY_COLORS['boxesColor']

        return out

    @callback(
        Output(ids.usageGPU_input(MATCH),'style'),
        [
            Input(ids.usageGPU_radio(MATCH), 'value'),
            Input(ids.usageGPU_input(MATCH), 'disabled')
        ]
    )
    def display_usage_input(answer_usage, disabled):
        '''
        Show or hide the usage factor input box, based on Yes/No input
        '''
        if answer_usage == 'No':
            out = {'display': 'none'}
        else:
            out = {'display': 'block'}

        if disabled:
            out['background-color'] = MY_COLORS['boxesColor']

        return out

        
    ##################### PUE INPUTS ###

    @callback(
        Output(ids.PUEquestion_div(MATCH),'style'),
        [
            Input(ids.location_region_dropdown(MATCH),'value'),
            Input(ids.platformType_dropdown(MATCH), 'value'),
            Input(ids.provider_dropdown(MATCH), 'value'),
            Input(ids.server_dropdown(MATCH), 'value')
        ]
    )
    def display_pue_question(_, selected_platform, selected_provider, selected_server):
        '''
        Shows or hides the PUE question depending on the platform
        '''
        if selected_platform == 'localServer':
            return {'display': 'flex'}
        elif (selected_platform == 'cloudComputing')&((selected_provider == 'other')|(selected_server == 'other')):
            return {'display': 'flex'}
        else:
            return {'display': 'none'}

    @callback(
        Output(ids.PUE_input(MATCH),'style'),
        [
            Input(ids.pue_radio(MATCH), 'value'),
            Input(ids.PUE_input(MATCH),'disabled')
        ]
    )
    def display_pue_input(answer_pue, disabled):
        '''
        Shows or hides the PUE input box
        '''
        if answer_pue == 'No':
            out = {'display': 'none'}
        else:
            out = {'display': 'block'}

        if disabled:
            out['background-color'] = MY_COLORS['boxesColor']

        return out
    

    ##################### PSF INPUTS ###

    @callback(
        Output(ids.PSF_input(MATCH),'style'),
        [
            Input(ids.PSF_radio(MATCH), 'value'),
            Input(ids.PSF_input(MATCH), 'disabled')
        ]
    )
    def display_PSF_input(answer_PSF, disabled):
        '''
        Shows or hides the PSF input box
        '''
        if answer_PSF == 'No':
            out = {'display': 'none'}
        else:
            out = {'display': 'block'}

        if disabled:
            out['background-color'] = MY_COLORS['boxesColor']

        return out
       

    ##################### PROCESS INPUTS ###
    
    @callback(
        Output(ids.aggregate_data(MATCH), "data"),
        [
            Input('versioned_data','data'),
            Input(ids.coreType_dropdown(MATCH), "value"),
            Input(ids.numberCPUs_input(MATCH), "value"),
            Input(ids.CPUmodel_dropdown(MATCH), "value"),
            Input(ids.tdpCPU_div(MATCH), "style"),
            Input(ids.tdpCPU_input(MATCH), "value"),
            Input(ids.numberGPUs_input(MATCH), "value"),
            Input(ids.GPUmodel_dropdown(MATCH), "value"),
            Input(ids.tdpGPU_div(MATCH), "style"),
            Input(ids.tdpGPU_input(MATCH), "value"),
            Input(ids.memory_input(MATCH), "value"),
            Input(ids.runTime_hour_input(MATCH), "value"),
            Input(ids.runTime_min_input(MATCH), "value"),
            Input(ids.location_continent_dropdown(MATCH), "value"),
            Input(ids.location_country_dropdown(MATCH), "value"),
            Input(ids.location_region_dropdown(MATCH), "value"),
            Input(ids.server_continent_dropdown(MATCH), "value"),
            Input(ids.server_dropdown(MATCH), "value"),
            Input(ids.location_div(MATCH), 'style'),
            Input(ids.server_div(MATCH),'style'),
            Input(ids.usageCPU_radio(MATCH), "value"),
            Input(ids.usageCPU_input(MATCH), "value"),
            Input(ids.usageGPU_radio(MATCH), "value"),
            Input(ids.usageGPU_input(MATCH), "value"),
            Input(ids.PUEquestion_div(MATCH),'style'),
            Input(ids.pue_radio(MATCH), "value"),
            Input(ids.PUE_input(MATCH), "value"),
            Input(ids.PSF_radio(MATCH), "value"),
            Input(ids.PSF_input(MATCH), "value"),
            Input(ids.platformType_dropdown(MATCH), 'value'),
            Input(ids.provider_dropdown(MATCH), 'value'),
            Input(ids.provider_dropdown_div(MATCH), 'style'),
        ],
    )
    def aggregate_input_values(data, coreType, n_CPUcores, CPUmodel, tdpCPUstyle, tdpCPU, n_GPUs, GPUmodel, tdpGPUstyle, tdpGPU,
                            memory, runTime_hours, runTime_min, locationContinent, locationCountry, locationRegion,
                            serverContinent, server, locationStyle, serverStyle, usageCPUradio, usageCPU, usageGPUradio, usageGPU,
                            PUEdivStyle, PUEradio, PUE, PSFradio, PSF, selected_platform, selected_provider, providerStyle):
        '''
        Computes all the metrics and gathers the information provided by the inputs of the form.
        '''
        output = dict()

        #############################################
        ### PREPROCESS: check if computations can be performed

        notReady = False

        ### Runtime
        test_runTime = 0
        if runTime_hours is None:
            actual_runTime_hours = 0
            test_runTime += 1
        else:
            actual_runTime_hours = runTime_hours

        if runTime_min is None:
            actual_runTime_min = 0
            test_runTime += 1
        else:
            actual_runTime_min = runTime_min
        runTime = actual_runTime_hours + actual_runTime_min/60.

        ### Core type
        if coreType is None:
            notReady = True
        elif (coreType in ['CPU','Both'])&((n_CPUcores is None)|(CPUmodel is None)):
            notReady = True
        elif (coreType in ['GPU','Both'])&((n_GPUs is None)|(GPUmodel is None)):
            notReady = True

        ### Versioned data
        if data is not None:
            data_dict = SimpleNamespace(**data)
            version = data_dict.version
        else:
            version = None
            notReady = True

        ### Location
        if is_shown(locationStyle):
            # this means the "location" input is shown, so we use location instead of server
            locationVar = locationRegion
        elif (server is None) | (server == 'other') | (data is None):
            locationVar = None
        else:
            locationVar = data_dict.datacenters_dict_byName[server]['location']

        ### Platform
        if selected_platform is None:
            notReady = True
        elif (selected_platform == 'cloudComputing')&(selected_provider is None):
            notReady = True

        ### Other required inputs
        if (memory is None)|(tdpCPU is None)|(tdpGPU is None)|(locationVar is None)| \
                (usageCPU is None)|(usageGPU is None)|(PUE is None)|(PSF is None):
            notReady = True

        ### If any of the required inputs is note ready: do not compute
        if notReady:
            output['coreType'] = None
            output['CPUmodel'] = None
            output['numberCPUs'] = None
            output['usageCPU'] = None
            output['usageCPUradio'] = None
            output['tdpCPU'] = None
            output['GPUmodel'] = None
            output['numberGPUs'] = None
            output['tdpGPU'] = None
            output['usageGPU'] = None
            output['usageGPUradio'] = None
            output['GPUpower'] = None
            output['memory'] = None
            output['runTime_hour'] = None
            output['runTime_min'] = None
            output['runTime'] = None
            output['platformType'] = None
            output['location'] = None
            output['carbonIntensity'] = None
            output['PUE'] = None
            output['PUEradio'] = None
            output['PSF'] = None
            output['PSFradio'] = None
            output['carbonEmissions'] = 0
            output['CE_CPU'] = 0
            output['CE_GPU'] = 0
            output['CE_core'] = 0
            output['CE_memory'] = 0
            output['n_treeMonths'] = 0
            output['flying_context'] = 0
            output['nkm_drivingUS'] = 0
            output['nkm_drivingEU'] = 0
            output['nkm_train'] = 0
            output['energy_needed'] = 0
            output['power_needed'] = 0
            output['flying_text'] = None
            output['text_CE'] = '... g CO2e'
            output['appVersion'] = version

        #############################################
        ### PRE-COMPUTATIONS: update variables used in the calcul based on inputs

        else:
            ### PUE
            defaultPUE = data_dict.pueDefault_dict['Unknown']
            # the input PUE is used only if the PUE box is shown AND the radio button is "Yes"
            if (is_shown(PUEdivStyle)) & (PUEradio == 'Yes'):
                PUE_used = PUE
            
            ### PLATFORM ALONG WITH PUE
            else:
                if selected_platform == 'personalComputer':
                    PUE_used = 1
                elif selected_platform == 'localServer':
                    PUE_used = defaultPUE
                else:
                    # Cloud
                    if selected_provider == 'other':
                        PUE_used = defaultPUE
                    else:
                        # if we don't know the PUE of this specific data centre, or if we 
                        # don't know the data centre, we use the provider's default
                        server_data = data_dict.datacenters_dict_byName.get(server)
                        if server_data is not None:
                            if pd.isnull(server_data['PUE']):
                                PUE_used = data_dict.pueDefault_dict[selected_provider]
                            else:
                                PUE_used = server_data['PUE']
                        else:
                            PUE_used = data_dict.pueDefault_dict[selected_provider]

            ### CPUs
            if coreType in ['CPU', 'Both']:
                if is_shown(tdpCPUstyle):
                    # we asked the question about TDP
                    CPUpower = tdpCPU
                else:
                    if CPUmodel == 'other':
                        CPUpower = tdpCPU
                    else:
                        CPUpower = data_dict.cores_dict['CPU'][CPUmodel]
                if usageCPUradio == 'Yes':
                    usageCPU_used = usageCPU
                else:
                    usageCPU_used = 1.
                powerNeeded_CPU = PUE_used * n_CPUcores * CPUpower * usageCPU_used
            else:
                powerNeeded_CPU = 0
                CPUpower = 0
                usageCPU_used = 0

            if coreType in ['GPU', 'Both']:
                if is_shown(tdpGPUstyle):
                    GPUpower = tdpGPU
                else:
                    if GPUmodel == 'other':
                        GPUpower = tdpGPU
                    else:
                        GPUpower = data_dict.cores_dict['GPU'][GPUmodel]
                if usageGPUradio == 'Yes':
                    usageGPU_used = usageGPU
                else:
                    usageGPU_used = 1.
                powerNeeded_GPU = PUE_used * n_GPUs * GPUpower * usageGPU_used
            else:
                powerNeeded_GPU = 0
                GPUpower = 0
                usageGPU_used = 0

            ### SERVER/LOCATION
            carbonIntensity = data_dict.CI_dict_byLoc[locationVar]['carbonIntensity']

            ### PSF
            if PSFradio == 'Yes':
                PSF_used = PSF
            else:
                PSF_used = 1

            #############################################
            ### COMPUTATIONS: final outputs are computed

            # Power needed, in Watt
            powerNeeded_core = powerNeeded_CPU + powerNeeded_GPU
            powerNeeded_memory = PUE_used * (memory * data_dict.refValues_dict['memoryPower'])
            powerNeeded = powerNeeded_core + powerNeeded_memory

            # Energy needed, in kWh (so dividing by 1000 to convert to kW)
            energyNeeded_CPU = runTime * powerNeeded_CPU * PSF_used / 1000
            energyNeeded_GPU = runTime * powerNeeded_GPU * PSF_used / 1000
            energyNeeded_core = runTime * powerNeeded_core * PSF_used / 1000
            eneregyNeeded_memory = runTime * powerNeeded_memory * PSF_used / 1000
            energyNeeded = runTime * powerNeeded * PSF_used / 1000

            # Carbon emissions: carbonIntensity is in g per kWh, so results in gCO2
            CE_CPU = energyNeeded_CPU * carbonIntensity
            CE_GPU = energyNeeded_GPU * carbonIntensity
            CE_core = energyNeeded_core * carbonIntensity
            CE_memory  = eneregyNeeded_memory * carbonIntensity
            carbonEmissions = energyNeeded * carbonIntensity

            # Storing all outputs to catch the app state and adapt textual content
            output['coreType'] = coreType
            output['CPUmodel'] = CPUmodel
            output['numberCPUs'] = n_CPUcores
            output['tdpCPU'] = CPUpower
            output['usageCPUradio'] = usageCPUradio
            output['usageCPU'] = usageCPU_used
            output['GPUmodel'] = GPUmodel
            output['numberGPUs'] = n_GPUs
            output['tdpGPU'] = GPUpower
            output['usageGPUradio'] = usageGPUradio
            output['usageGPU'] = usageGPU_used
            output['memory'] = memory
            output['runTime_hour'] = actual_runTime_hours
            output['runTime_min'] = actual_runTime_min
            output['runTime'] = runTime
            output['platformType'] = selected_platform
            output['locationContinent'] = locationContinent
            output['locationCountry'] = locationCountry
            output['locationRegion'] = locationRegion
            output['provider'] = selected_provider
            output['serverContinent'] = serverContinent
            output['server'] = server
            output['location'] = locationVar
            output['carbonIntensity'] = carbonIntensity
            output['PUE'] = PUE_used
            output['PUEradio'] = PUEradio
            output['PSF'] = PSF_used
            output['PSFradio'] = PSFradio
            output['carbonEmissions'] = carbonEmissions
            output['CE_CPU'] = CE_CPU
            output['CE_GPU'] = CE_GPU
            output['CE_core'] = CE_core
            output['CE_memory'] = CE_memory
            output['energy_needed'] = energyNeeded
            output['power_needed'] = powerNeeded
            output['appVersion'] = version

            ### Context
            output['n_treeMonths'] = carbonEmissions / data_dict.refValues_dict['treeYear'] * 12
            output['nkm_drivingUS'] = carbonEmissions / data_dict.refValues_dict['passengerCar_US_perkm']
            output['nkm_drivingEU'] = carbonEmissions / data_dict.refValues_dict['passengerCar_EU_perkm']
            output['nkm_train'] = carbonEmissions / data_dict.refValues_dict['train_perkm']

            ### Text plane trips
            if carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NY-SF']:
                output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_PAR-LON']
                output['flying_text'] = "Paris-London"
            elif carbonEmissions < 0.5 * data_dict.refValues_dict['flight_NYC-MEL']:
                output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NY-SF']
                output['flying_text'] = "NYC-San Francisco"
            else:
                output['flying_context'] = carbonEmissions / data_dict.refValues_dict['flight_NYC-MEL']
                output['flying_text'] = "NYC-Melbourne"

            ### Text carbon emissions
            carbonEmissions_value = carbonEmissions  # in g CO2e
            carbonEmissions_unit = "g"
            if carbonEmissions_value >= 1e6:
                carbonEmissions_value /= 1e6
                carbonEmissions_unit = "T"
            elif carbonEmissions_value >= 1e3:
                carbonEmissions_value /= 1e3
                carbonEmissions_unit = "kg"
            elif carbonEmissions_value < 1:
                carbonEmissions_value *= 1e3
                carbonEmissions_unit = "mg"
            if (carbonEmissions_value != 0)&((carbonEmissions_value >= 1e3)|(carbonEmissions_value < 1)):
                output['text_CE'] = f"{carbonEmissions_value:,.2e} {carbonEmissions_unit} CO2e"
            else:
                output['text_CE'] = f"{carbonEmissions_value:,.2f} {carbonEmissions_unit} CO2e"

            ### Text energy
            energyNeeded_value = energyNeeded  # in kWh
            energyNeeded_unit = "kWh"
            if energyNeeded_value >= 1e3:
                energyNeeded_value /= 1e3
                energyNeeded_unit = "MWh"
            elif energyNeeded_value < 1:
                energyNeeded_value *= 1e3
                energyNeeded_unit = "Wh"
            if (energyNeeded_value != 0) & ((energyNeeded_value >= 1e3) | (energyNeeded_value < 1)):
                output['text_energyNeeded'] = f"{energyNeeded_value:,.2e} {energyNeeded_unit}"
            else:
                output['text_energyNeeded'] = f"{energyNeeded_value:,.2f} {energyNeeded_unit}"

            ### Text tree-months
            treeTime_value = output['n_treeMonths']  # in tree-months
            treeTime_unit = "tree-months"
            if treeTime_value >= 24:
                treeTime_value /= 12
                treeTime_unit = "tree-years"
            if (treeTime_value != 0) & ((treeTime_value >= 1e3) | (treeTime_value < 0.1)):
                output['text_treeYear'] = f"{treeTime_value:,.2e} {treeTime_unit}"
            else:
                output['text_treeYear'] = f"{treeTime_value:,.2f} {treeTime_unit}"

        return output
