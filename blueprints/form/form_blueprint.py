import pandas as pd

from dash_extensions.enrich import DashBlueprint, Output, Input, State, PrefixIdTransform, ctx
from types import SimpleNamespace

from utils.utils import put_value_first, is_shown, custom_prefix_escape
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region, DEFAULT_VALUES
from utils.graphics import MY_COLORS

from blueprints.form.form_layout import get_green_algo_form_layout

def get_form_blueprint(id_prefix, title, subtitle):

    form_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix,
                escape=custom_prefix_escape
            )
        ]
    )
    
    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    form_blueprint.layout = get_green_algo_form_layout(title, subtitle)


    ##### DEFINE ITS CALLBACKS
    ##########################

    ##################### INITIALIZATION ###

    @form_blueprint.callback(
        [
            ##################################################################
            ## WARNING: do not modify the order, unless modifying the order
            ## of the DEFAULT_VALUES accordingly
            Output('runTime_hour_input','value'),
            Output('runTime_min_input','value'),
            Output('coreType_dropdown','value'),
            Output('numberCPUs_input','value'),
            Output('CPUmodel_dropdown', 'value'),
            Output('tdpCPU_input','value'),
            Output('numberGPUs_input','value'),
            Output('GPUmodel_dropdown', 'value'),
            Output('tdpGPU_input','value'),
            Output('memory_input','value'),
            Output('platformType_dropdown','value'),
            Output('usageCPU_radio','value'),
            Output('usageCPU_input','value'),
            Output('usageGPU_radio','value'),
            Output('usageGPU_input','value'),
            Output('pue_radio','value'),
            Output('PSF_radio', 'value'),
            Output('PSF_input', 'value'),
        ],
        [
            # to allow initial triggering
            Input('url_content','search'),
            Input('from_input_data', 'data'),
        ],
    )
    def filling_form(_, upload_content): 
        if  ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            to_return = {k: upload_content[k] for k in DEFAULT_VALUES.keys()}
            return tuple(to_return.values())
        return tuple(DEFAULT_VALUES.values())
    

    ##################### PLATFORM AND PROVIDER ###

    @form_blueprint.callback(
        Output('platformType_dropdown', 'options'),
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

    @form_blueprint.callback(
        Output('provider_dropdown_div', 'style'),
        Input('platformType_dropdown', 'value'),
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
    
    @form_blueprint.callback(
        Output('provider_dropdown', 'options'),
        [
            Input('platformType_dropdown', 'value'),
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
        
    @form_blueprint.callback(
        Output('provider_dropdown','value'),
        [
            Input('platformType_dropdown', 'value'),
            Input('versioned_data','data'),
            Input('from_input_data', 'data'),
        ],
        [
            State('provider_dropdown', 'value'),
        ],
    )
    def set_provider(platform_type, versioned_data, upload_content, prev_provider):
        '''
        Sets the provider value, either from the csv content of as a default value.
        TODO: improve the choice of the default value.
        '''
        # reads data from input
        if ctx.triggered_id is not None:
            if 'from_input_data' in ctx.triggered_id:
                return upload_content['provider']
        
            # by default, when changing the platform type, we return the previously selected
            # providern, because properly handles the case when 'Cloud Computing' is selected 
            if 'platformType_dropdown' in ctx.triggered_id and prev_provider is not None:
                return prev_provider
                    
        return 'gcp'
    
    @form_blueprint.callback(
        Output('server_continent_dropdown','value'),
        [
            Input('provider_dropdown', 'value'),
            Input('versioned_data','data'),
            Input('from_input_data', 'data'),
        ],
        [
            State('server_continent_dropdown', 'value'),
        ]
    )
    def set_serverContinents_value(selected_provider, versioned_data, upload_content, prev_server_continent):
        '''
        Sets the value for server's continent, depending on the provider.
        We want to fetch the value based on csv input but also to display 
        a value selcted previously by the user.
        '''
        # reads data from input
        if ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            return upload_content['serverContinent']

        # otherwise we return a suitable default value
        availableOptions = availableLocations_continent(selected_provider, data=versioned_data)
        if prev_server_continent in availableOptions:
            defaultValue = prev_server_continent
        else:
            try: 
                defaultValue = availableOptions[0]
            except:
                defaultValue = None
        return defaultValue
    
    @form_blueprint.callback(
        Output('server_dropdown','value'),
        [
            Input('server_continent_dropdown', 'value'),
            Input('versioned_data','data'),
            Input('from_input_data', 'data'),
        ],
        [
            State('provider_dropdown', 'value'),
            State('server_dropdown','value'),
        ]
    )
    def set_server_value(selected_continent, versioned_data, upload_content, selected_provider, prev_server_value):
        '''
        Sets the value for servers, based on provider and continent.
        Here again we want to display a default value, to 
        fecth the value from a csv or to show a value previously selected by the user.
        '''
        # reads data from input
        if ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            return upload_content['server']
        
        # handles special case
        if selected_continent == 'other':
            return 'other'

        # Otherwise we return a suitable default value
        availableOptions = availableOptions_servers(selected_provider, selected_continent, data=versioned_data)
        try:
            # when the server continent value had previously been set by the user
            if prev_server_value in [server['name_unique'] for server in availableOptions]:
                defaultValue = prev_server_value
            else :
                defaultValue = availableOptions[0]['name_unique']
        except:
            defaultValue = None
        return defaultValue
    

    @form_blueprint.callback(
        Output('location_continent_dropdown', 'value'),
        [
            Input('server_div', 'style'),
            Input('from_input_data', 'data'),
        ],
        [
            State('server_continent_dropdown','value'),
            State('location_continent_dropdown', 'value'),
        ]
    )
    def set_continent_value(display_server, upload_content, selected_serverContinent, prev_locationContinent):
        '''
        Sets the value for location continent.
        Same as for server and server continent regarding the different inputs.
        '''
        # reads data from input
        if ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            return upload_content['locationContinent']
        
        # when the continent value had previously been set by the user
        if prev_locationContinent is not None :
            return prev_locationContinent
        
        # the server div is shown, so we pull the continent from there
        if (display_server['display'] != 'none') & (selected_serverContinent != 'other'):
            return selected_serverContinent
        
        return 'Europe'
    
    @form_blueprint.callback(
        [
            Output(f'location_country_dropdown', 'options'),
            Output(f'location_country_dropdown', 'value'),
            Output(f'location_country_dropdown_div', 'style'),
        ],
        [
            Input(f'location_continent_dropdown', 'value'),
            Input('versioned_data','data'),
            Input('from_input_data', 'data'),
        ],
        [
            State(f'location_country_dropdown', 'value')
        ]
    )
    def set_countries_options(selected_continent, versioned_data, upload_content, prev_selectedCountry):
        '''
        List of options and value for countries.
        Hides country dropdown if continent=World is selected.
        Must fetch the value from a csv as well.
        '''
        availableOptions = availableOptions_country(selected_continent, data=versioned_data)
        listOptions = [{'label': k, 'value': k} for k in availableOptions]
        defaultValue = None

        # reads data from input
        if ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            print('in set_countries, upload_content is: ', upload_content)
            defaultValue = upload_content['locationCountry']

        # otherwise we get a suitable default value    
        if defaultValue is None:
            # NOTE The following handles two cases: 
            if prev_selectedCountry in availableOptions :
                defaultValue = prev_selectedCountry
            else:
                try:
                    defaultValue = availableOptions[0]
                except:
                    defaultValue = None

        if selected_continent == 'World':
            country_style = {'display': 'none'}
        else:
            country_style = {'display': 'block'}

        return listOptions, defaultValue, country_style
    
    @form_blueprint.callback(
        [
            Output(f'location_region_dropdown', 'options'),
            Output(f'location_region_dropdown', 'value'),
            Output(f'location_region_dropdown_div', 'style'),
        ],
        [
            Input(f'location_continent_dropdown', 'value'),
            Input(f'location_country_dropdown', 'value'),
            Input('versioned_data','data'),
            Input('from_input_data', 'data'),
        ],
        [
            State(f'location_region_dropdown', 'value'),
        ]

    )
    def set_regions_options(selected_continent, selected_country, versioned_data, upload_content, prev_selectedRegion):
        '''
        List of options and value for regions.
        Hides region dropdown if only one possible region (or continent=World)
        '''
        locs = availableOptions_region(selected_continent, selected_country, data=versioned_data)
        if versioned_data is not None:
            listOptions = [{'label': versioned_data['CI_dict_byLoc'][loc]['regionName'], 'value': loc} for loc in locs]
        else:
            listOptions = []
        defaultValue = None

        # reads data from input
        if ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            defaultValue = upload_content['locationRegion']

        # otherwise we get a suitable default value  
        if defaultValue is None:
            # when the region value had previously been set by the user
            if prev_selectedRegion in locs:
                defaultValue = prev_selectedRegion
            else:
                try:
                        defaultValue = locs[0]
                except:
                    defaultValue = None

        if (selected_continent == 'World')|(len(listOptions) == 1):
            region_style = {'display': 'none'}
        else:
            region_style = {'display': 'block'}

        return listOptions, defaultValue, region_style
        

    ##################### COMPUTING CORES ###

    @form_blueprint.callback(
        Output('coreType_dropdown', 'options'),
        [
            Input('provider_dropdown', 'value'),
            Input('platformType_dropdown', 'value'),
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
            print('return nothing')
            return []
        
    @form_blueprint.callback(
        [
            Output('CPUmodel_dropdown', 'options'),
            Output('GPUmodel_dropdown', 'options')
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
        
    @form_blueprint.callback(
        [
            Output('CPU_div', 'style'),
            Output('title_CPU', 'style'),
            Output('usageCPU_div', 'style'),
            Output('GPU_div', 'style'),
            Output('title_GPU', 'style'),
            Output('usageGPU_div', 'style'),
        ],
        [
            Input('coreType_dropdown', 'value')
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
        
    @form_blueprint.callback(
        Output('tdpCPU_div', 'style'),
        [
            Input('CPUmodel_dropdown', 'value'),
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
        
    @form_blueprint.callback(
        Output('tdpGPU_div', 'style'),
        [
            Input('GPUmodel_dropdown', 'value'),
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

    @form_blueprint.callback(
        [
            Output('location_div', 'style'),
            Output('server_div', 'style'),
        ],
        [
            Input('platformType_dropdown', 'value'),
            Input('provider_dropdown', 'value'),
            Input('server_dropdown','value'),
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

    @form_blueprint.callback(
        Output('server_continent_dropdown','options'),
        [
            Input('provider_dropdown', 'value'),
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
    
    @form_blueprint.callback(
        Output('server_dropdown','style'),
        Input('server_continent_dropdown', 'value'),
    )
    def set_server_style(selected_continent):
        '''
        Show or not the choice of servers, don't if continent is on "Other"
        '''
        if selected_continent == 'other':
            return {'display': 'none'}

        else:
            return {'display': 'block'}
        
    @form_blueprint.callback(
        Output('server_dropdown','options'),
        [
            Input('provider_dropdown', 'value'),
            Input('server_continent_dropdown', 'value'),
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

    @form_blueprint.callback(
        Output('location_continent_dropdown', 'options'),
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

    @form_blueprint.callback(
        Output('usageCPU_input','style'),
        [
            Input('usageCPU_radio', 'value'),
            Input('usageCPU_input', 'disabled')
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

    @form_blueprint.callback(
        Output('usageGPU_input','style'),
        [
            Input('usageGPU_radio', 'value'),
            Input('usageGPU_input', 'disabled')
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

    @form_blueprint.callback(
        Output('PUEquestion_div','style'),
        [
            Input('location_region_dropdown','value'),
            Input('platformType_dropdown', 'value'),
            Input('provider_dropdown', 'value'),
            Input('server_dropdown', 'value')
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

    @form_blueprint.callback(
        Output('PUE_input','style'),
        [
            Input('pue_radio', 'value'),
            Input('PUE_input','disabled')
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
    
    
    @form_blueprint.callback(
        Output(f'PUE_input','value'),
        [
            Input(f'pue_radio', 'value'),
            Input('versioned_data','data'),
            Input('from_input_data', 'data'),
        ],
        [
            State(f'PUE_input','value'),
        ]
    )
    def set_PUE(radio, versioned_data, upload_content, prev_pue):
        '''
        Sets the PUE value, either from csv input or as a default value.
        '''
        if versioned_data is not None:
            data_dict = SimpleNamespace(**versioned_data)
            defaultPUE = data_dict.pueDefault_dict['Unknown']
        else:
            defaultPUE = 0

        if radio == 'No':
            return defaultPUE
        
        # reads data from input
        if ctx.triggered_id is not None and 'from_input_data' in ctx.triggered_id:
            return upload_content['PUE']

        return defaultPUE
    

    ##################### PSF INPUTS ###

    @form_blueprint.callback(
        Output('PSF_input','style'),
        [
            Input('PSF_radio', 'value'),
            Input('PSF_input', 'disabled')
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
    
    @form_blueprint.callback(
        Output('aggregate_data', "data"),
        [
            Input('versioned_data','data'),
            Input('coreType_dropdown', "value"),
            Input('numberCPUs_input', "value"),
            Input('CPUmodel_dropdown', "value"),
            Input('tdpCPU_div', "style"),
            Input('tdpCPU_input', "value"),
            Input('numberGPUs_input', "value"),
            Input('GPUmodel_dropdown', "value"),
            Input('tdpGPU_div', "style"),
            Input('tdpGPU_input', "value"),
            Input('memory_input', "value"),
            Input('runTime_hour_input', "value"),
            Input('runTime_min_input', "value"),
            Input('location_continent_dropdown', "value"),
            Input('location_country_dropdown', "value"),
            Input('location_region_dropdown', "value"),
            Input('server_continent_dropdown', "value"),
            Input('server_dropdown', "value"),
            Input('location_div', 'style'),
            Input('server_div','style'),
            Input('usageCPU_radio', "value"),
            Input('usageCPU_input', "value"),
            Input('usageGPU_radio', "value"),
            Input('usageGPU_input', "value"),
            Input('PUEquestion_div','style'),
            Input('pue_radio', "value"),
            Input('PUE_input', "value"),
            Input('PSF_radio', "value"),
            Input('PSF_input', "value"),
            Input('platformType_dropdown', 'value'),
            Input('provider_dropdown', 'value'),
            Input('provider_dropdown_div', 'style'),
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
    
    return form_blueprint
