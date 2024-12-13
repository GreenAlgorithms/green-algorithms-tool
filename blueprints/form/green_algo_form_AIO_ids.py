class GreenAlgoFormIDS:
    
    @staticmethod
    def id_template(aio_id, subcomponent_name):
        return {
            'component': 'GreenAlgoFormAIO',
            'subcomponent': subcomponent_name,
            'aio_id': aio_id
        }
    
    def __init__(self, aio_id=None):
        self.aio_id = aio_id
    
    def aggregate_data(self, id):
        return self.id_template(id, 'aggregate_data')

    ##################### RUNTIME ###

    def runTime_hour_input(self, id):
        return self.id_template(id, 'runTime_hour_input')
    
    def runTime_min_input(self, id):
        return self.id_template(id, 'runTime_min_input')
    
    ##################### CORES ###

    def coreType_dropdown(self, id):
        return self.id_template(id, 'coreType_dropdown')
    
    #----- CPUs

    def title_CPU(self, id):
        return self.id_template(id, 'title_CPU')

    def numberCPUs_input(self, id):
        return self.id_template(id, 'numberCPUs_input')

    def CPUmodel_dropdown(self, id):
        return self.id_template(id, 'CPUmodel_dropdown')

    def tdpCPU_input(self, id):
        return self.id_template(id, 'tdpCPU_input')

    def tdpCPU_div(self, id):
        return self.id_template(id, 'tdpCPU_div')

    def CPU_div(self, id):
        return self.id_template(id, 'CPU_div')

    #----- GPUs

    def title_GPU(self, id):
        return self.id_template(id, 'title_GPU')

    def numberGPUs_input(self, id):
        return self.id_template(id, 'numberGPUs_input')

    def GPUmodel_dropdown(self, id):
        return self.id_template(id, 'GPUmodel_dropdown')

    def tdpGPU_input(self, id):
        return self.id_template(id, 'tdpGPU_input')

    def tdpGPU_div(self, id):
        return self.id_template(id, 'tdpGPU_div')

    def GPU_div(self, id):
        return self.id_template(id, 'GPU_div')

    ##################### MEMORY ###

    def memory_input(self, id):
        return self.id_template(id, 'memory_input')

    def div_memory(self, id):
        return self.id_template(id, 'div_memory')

    ##################### PLATFORM ###

    def platformType_dropdown(self, id):
        return self.id_template(id, 'platformType_dropdown')

    #----- CLOUD

    def provider_dropdown(self, id):
        return self.id_template(id, 'provider_dropdown')

    def provider_dropdown_div(self, id):
        return self.id_template(id, 'provider_dropdown_div')

    #----- SERVER
    
    def server_continent_dropdown(self, id):
        return self.id_template(id, 'server_continent_dropdown')

    def server_dropdown(self, id):
        return self.id_template(id, 'server_dropdown')

    def server_div(self, id):
        return self.id_template(id, 'server_div')
    
    #-- LOCATION

    def location_continent_dropdown(self, id):
        return self.id_template(id, 'location_continent_dropdown')

    def location_country_dropdown(self, id):
        return self.id_template(id, 'location_country_dropdown')

    def location_country_dropdown_div(self, id):
        return self.id_template(id, 'location_country_dropdown_div')

    def location_region_dropdown(self, id):
        return self.id_template(id, 'location_region_dropdown')

    def location_region_dropdown_div(self, id):
        return self.id_template(id, 'location_region_dropdown_div')

    def location_div(self, id):
        return self.id_template(id, 'location_div')

    ##################### CORES USAGE ###

    def usageCPU_radio(self, id):
        return self.id_template(id, 'usageCPU_radio')

    def usageCPU_input(self, id):
        return self.id_template(id, 'usageCPU_input')

    def usageCPU_div(self, id):
        return self.id_template(id, 'usageCPU_div')

    def usageGPU_radio(self, id):
        return self.id_template(id, 'usageGPU_radio')

    def usageGPU_input(self, id):
        return self.id_template(id, 'usageGPU_input')

    def usageGPU_div(self, id):
        return self.id_template(id, 'usageGPU_div')

    ##################### PUE and PSF ###

    def pue_radio(self, id):
        return self.id_template(id, 'pue_radio')

    def PUE_input(self, id):
        return self.id_template(id, 'PUE_input')

    def PUEquestion_div(self, id):
        return self.id_template(id, 'PUEquestion_div')

    def PSF_radio(self, id):
        return self.id_template(id, 'PSF_radio')

    def PSF_input(self, id):
        return self.id_template(id, 'PSF_input')
        
    ##################### RESET ###

    def confirm_reset(self, id):
        return self.id_template(id, 'confirm_reset')

    def reset_link(self, id):
        return self.id_template(id, 'reset_link')

    
    
