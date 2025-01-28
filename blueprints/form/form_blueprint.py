'''
Implements the form blueprint.
'''

import pandas as pd

from dash_extensions.enrich import DashBlueprint, Output, Input, State, PrefixIdTransform, ctx, html
from types import SimpleNamespace

from utils.utils import put_value_first, is_shown, custom_prefix_escape
from utils.handle_inputs import availableLocations_continent, availableOptions_servers, availableOptions_country, availableOptions_region, DEFAULT_VALUES_FOR_PAGE_LOAD
from utils.graphics import MY_COLORS

from blueprints.form.form_layout import get_green_algo_form_layout

def get_form_blueprint(
    id_prefix:str,
    title: str,
    subtitle: html.P,
    continuous_inf_scheme_properties: dict = {'display': 'none'},
    mult_factor_properties: dict = {},
    additional_bottom_fields: html.Div = html.Div(),
):
    """
    TODO: remove the continuous inference section from the form blueprint,
    as it should not belong to the base Form module. Instead, the right 
    way to embed the continuous inference section in the inference form should 
    be to pass it as an argument to this function.

    Args:
        id_prefix (str): id prefix automatically applied to all components and callbacks.
        title (str): form title (at the top of the layout)
        subtitle (html.P): form subtitle (below the title)
        continuous_inf_scheme_properties (_type_, optional): used to hide the continuous inference scheme for the main
        form and the training form. Defaults to {'display': 'none'}.
        mult_factor_properties (dict, optional): used to hide the MF fields. Defaults to {}.
        additional_bottom_fields (html.Div, optional): used to add retraining and R&D training fields for instance.
        Defaults to html.Div().
    """

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

    form_blueprint.layout = get_green_algo_form_layout(
        title,
        subtitle,
        continuous_inf_scheme_properties,
        mult_factor_properties,
        additional_bottom_fields
    )


    ##### DEFINE ITS CALLBACKS
    ##########################

    ##################### INITIALIZATION ###

    @form_blueprint.callback(
        [
            ##################################################################
            ## WARNING: do not modify the order, unless modifying the order
            ## of the DEFAULT_VALUES_FOR_PAGE_LOAD accordingly. The issue is the strong 
            # dependency between the order of the keys in the utils/handle_inputs.py/DEFAULT_VALUES_FOR_PAGE_LOAD 
            # and the order of the Outputs of this callback.
            ## TODO: make it more robust.
            Output('runTime_hour_input', 'value'),
            Output('runTime_min_input', 'value'),
            Output('coreType_dropdown', 'value'),
            Output('numberCPUs_input', 'value'),
            Output('CPUmodel_dropdown', 'value'),
            Output('tdpCPU_input', 'value'),
            Output('numberGPUs_input', 'value'),
            Output('GPUmodel_dropdown', 'value'),
            Output('tdpGPU_input', 'value'),
            Output('memory_input', 'value'),
            Output('platformType_dropdown', 'value'),
            Output('usageCPU_radio', 'value'),
            Output('usageCPU_input', 'value'),
            Output('usageGPU_radio', 'value'),
            Output('usageGPU_input', 'value'),
            Output('pue_radio', 'value'),
            Output('mult_factor_radio', 'value'),
            Output('mult_factor_input', 'value'),
        ],
        [
            # To force initial triggering
            Input('url_content','search'),
            Input('form_data_imported_from_csv', 'data'),
        ],
    )
    def filling_form(_, upload_content): 
        if  ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
            to_return = {k: upload_content[k] for k in DEFAULT_VALUES_FOR_PAGE_LOAD.keys()}
            return tuple(to_return.values())
        return tuple(DEFAULT_VALUES_FOR_PAGE_LOAD.values())
    

    ##################### LOCATION AND SERVER ###

    ###########################################
    ### TODO: platform, location and server inputs sometimes do not 
    # render when uploaded from csv on AI page. Particularly frequent for server.
    #  
    # The first callback range (the one directly triggered by the upload) is almost
    # always not enough to render all inputs, and most of the time it is the 
    # second callback range (the one triggered by csv flushing) that allows to complete
    # the csv inputs rendering.
    #
    # The current workaround consists in applying a higher csv_flushing_delay for the
    # AI Page, so the second callback range almost always completes the inputs rendering.
    # With a flushing delay of 2 seconds, inputs are correctly rendered after the second
    # callback range when the app is run locally.  
    #
    # My best guess is that it is due to the callback chain being
    # congested or not correctly organised by Dash because of the number of callbacks 
    # that are triggered at upload time: both location(s)
    # (continent, country, region) options and value, provider options and value,
    # server continent options and value as well as server options and value callbacks.
    # 
    # Possible fix include : 
    #   - remove default values for location and server fields 
    #       ~ (maybe not very user compliant)
    #   - refactor the callback chain by implementing step by step callback chain:
    #       ~ if the server div is not rendered, never apply callback related to server
    #       (could be done by passing 'form_data_imported_from_csv' as a State, not as an Input)  
    ###########################################

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
        [
            Output('location_div', 'style'),
            Output('server_div', 'style'),
        ],
        [
            Input('platformType_dropdown', 'value'),
            Input('provider_dropdown', 'value'),
            Input('server_dropdown','value'),
            Input('versioned_data','data'),
            Input('form_data_imported_from_csv', 'data'),
        ]
    )
    def display_location(selected_platform, selected_provider, selected_server, data, upload_content):
        '''
        Shows either LOCATION or SERVER depending on the platform.

        NOTE: the input Input('form_data_imported_from_csv', 'data') should not be necessary because, when a csv is uploaded,
        this callback would be triggered by the other Inputs. However, because of the issue documented in 
        the above TODO (~ line 108), I have been thinking that adding Input('form_data_imported_from_csv', 'data') as
        an Input would help organizing the callback chain.
        '''
        if data is not None:
            data_dict = SimpleNamespace(**data)
            providers_withoutDC = data_dict.providers_withoutDC
        else:
            providers_withoutDC = []

        show = {'display': 'flex'}
        hide = {'display': 'none'}

        # The following is a kind of duplicata from the lines below,
        # should help to better take into account inputs uploaded from csv
        # TODO: should be removed when the callback chain is made simpler.
        # This simplification refers to the above TODO as well. In simple terms
        # it would be worth trying to refactor the callback chain using intermediate bottlenecks. 
        # For instance, if the server div is not rendered, never apply callback related to server
        # (could be done by passing 'form_data_imported_from_csv' as a State, not as an Input)
        if 'form_data_imported_from_csv' in ctx.triggered_id:
            if upload_content['platformType'] == 'cloudComputing':
                if upload_content['provider'] in ['other'] + providers_withoutDC:
                    return show, hide
                elif selected_server == 'other':
                    return show, show
                else:
                    return hide, show
            else:
                return show, hide

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
        Output('provider_dropdown_div', 'style'),
        Input('platformType_dropdown', 'value'),
    )
    def show_provider_field(selected_platform):
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
    def set_provider_options(selected_platform, data):
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
            Input('form_data_imported_from_csv', 'data'),
        ],
        [
            State('provider_dropdown', 'value'),
        ],
    )
    def set_provider_value(platform_type, versioned_data, upload_content, prev_provider):
        '''
        Sets the provider value, either from the csv content of as a default value.
        '''
        # reads data from input
        if ctx.triggered_id is not None:
            if 'form_data_imported_from_csv' in ctx.triggered_id:
                return upload_content['provider']
        
            # by default, when changing the platform type, we return the previously selected
            # provider, because it properly handles the case when 'Cloud Computing' is selected 
            if 'platformType_dropdown' in ctx.triggered_id and prev_provider is not None:
                return prev_provider
                    
        return 'gcp'
    
    
    @form_blueprint.callback(
        Output('server_continent_dropdown','options'),
        [
            Input('provider_dropdown', 'value'),
            Input('versioned_data','data')
        ]
    )
    def set_server_continents_options(selected_provider, data):
        '''
        List of options and default value for server's continent, based on the provider
        '''
        availableOptions = availableLocations_continent(selected_provider, versioned_data=data)
        listOptions = [{'label': k, 'value': k} for k in sorted(availableOptions)] + [{'label': 'Other', 'value': 'other'}]
        return listOptions

            
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
        availableOptions = availableOptions_servers(selected_provider,selected_continent,versioned_data=data)
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

    
    @form_blueprint.callback(
        Output('server_continent_dropdown','value'),
        [
            Input('provider_dropdown', 'value'),
            Input('versioned_data','data'),
            Input('form_data_imported_from_csv', 'data'),
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
        if ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
            return upload_content['serverContinent']

        # otherwise we return a suitable default value
        availableOptions = availableLocations_continent(selected_provider, versioned_data=versioned_data)
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
            Input('form_data_imported_from_csv', 'data'),
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
        if ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
            return upload_content['server']
        
        # handles special case
        if selected_continent == 'other':
            return 'other'

        # Otherwise we return a suitable default value
        availableOptions = availableOptions_servers(selected_provider, selected_continent, versioned_data=versioned_data)
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
            Input('form_data_imported_from_csv', 'data'),
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
        if ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
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
            Input('form_data_imported_from_csv', 'data'),
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
        availableOptions = availableOptions_country(selected_continent, versioned_data=versioned_data)
        listOptions = [{'label': k, 'value': k} for k in availableOptions]
        defaultValue = None

        # reads data from input
        if ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
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
            Input('form_data_imported_from_csv', 'data'),
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
        if ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
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
            Input('form_data_imported_from_csv', 'data'),
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
        if ctx.triggered_id is not None and 'form_data_imported_from_csv' in ctx.triggered_id:
            return upload_content['PUE']

        return defaultPUE
    

    ##################### MULTIPLICATIVE FACTOR INPUTS ###

    @form_blueprint.callback(
        Output('mult_factor_input','style'),
        [
            Input('mult_factor_radio', 'value'),
            Input('mult_factor_input', 'disabled')
        ]
    )
    def display_mult_factor_input(answer_mult_factor, disabled):
        '''
        Shows or hides the MULTIPLICATIVE FACTOR input box
        '''
        if answer_mult_factor == 'No':
            out = {'display': 'none'}
        else:
            out = {'display': 'block'}

        if disabled:
            out['background-color'] = MY_COLORS['boxesColor']

        return out
       

    ##################### PROCESS INPUTS ###
    
    @form_blueprint.callback(
        [
            Output('form_aggregate_data', "data"),
            Output('form_output_metrics', "data"),
        ],
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
            Input('mult_factor_radio', "value"),
            Input('mult_factor_input', "value"),
            Input('platformType_dropdown', 'value'),
            Input('provider_dropdown', 'value'),
            Input('provider_dropdown_div', 'style'),
        ],
    )
    def aggregate_input_values(data, coreType, n_CPUcores, CPUmodel, tdpCPUstyle, tdpCPU, n_GPUs, GPUmodel, tdpGPUstyle, tdpGPU,
                            memory, runTime_hours, runTime_min, locationContinent, locationCountry, locationRegion,
                            serverContinent, server, locationStyle, serverStyle, usageCPUradio, usageCPU, usageGPUradio, usageGPU,
                            PUEdivStyle, PUEradio, PUE, mult_factor_radio, mult_factor, selected_platform, selected_provider, providerStyle):
        '''
        Computes all the metrics and gathers the information provided by the inputs of the form.
        '''
        output = dict()
        metrics = dict()

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
                (usageCPU is None)|(usageGPU is None)|(PUE is None)|(mult_factor is None):
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
            output['platformType'] = None
            output['location'] = None
            output['carbonIntensity'] = None
            output['PUE'] = None
            output['PUEradio'] = None
            output['mult_factor'] = None
            output['mult_factor_radio'] = None
            output['appVersion'] = version
            metrics['energy_needed'] = 0
            metrics['carbonEmissions'] = 0
            metrics['runTime'] = None
            metrics['power_needed'] = 0
            metrics['CE_CPU'] = 0
            metrics['CE_GPU'] = 0
            metrics['CE_core'] = 0
            metrics['CE_memory'] = 0

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
                    # CPUmodel cannot be "other"
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
                    # GPUmodel cannot be "other"
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

            ### MULTIPLICATIVE FACTOR
            if mult_factor_radio == 'Yes':
                mult_factor_used = mult_factor
            else:
                mult_factor_used = 1

            #############################################
            ### COMPUTATIONS: final outputs are computed

            # Power needed, in Watt
            powerNeeded_core = powerNeeded_CPU + powerNeeded_GPU
            powerNeeded_memory = PUE_used * (memory * data_dict.refValues_dict['memoryPower'])
            powerNeeded = powerNeeded_core + powerNeeded_memory

            # Energy needed, in kWh (so dividing by 1000 to convert to kW)
            energyNeeded_CPU = runTime * powerNeeded_CPU * mult_factor_used / 1000
            energyNeeded_GPU = runTime * powerNeeded_GPU * mult_factor_used / 1000
            energyNeeded_core = runTime * powerNeeded_core * mult_factor_used / 1000
            eneregyNeeded_memory = runTime * powerNeeded_memory * mult_factor_used / 1000
            energyNeeded = runTime * powerNeeded * mult_factor_used / 1000

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
            output['mult_factor'] = mult_factor_used
            output['mult_factor_radio'] = mult_factor_radio
            output['appVersion'] = version
            metrics['energy_needed'] = energyNeeded
            metrics['carbonEmissions'] = carbonEmissions
            metrics['runTime'] = runTime
            metrics['power_needed'] = powerNeeded
            metrics['CE_CPU'] = CE_CPU
            metrics['CE_GPU'] = CE_GPU
            metrics['CE_core'] = CE_core
            metrics['CE_memory'] = CE_memory

        return output, metrics

    return form_blueprint
