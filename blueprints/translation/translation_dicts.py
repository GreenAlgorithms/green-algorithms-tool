'''
The translation dict containing all the app translations.
'''


TRANSLATIONS_DICT = {

    #### APP HEADER ####

    ## TOP HEADER AND NAVIGATION BAR

    "Green Algorithms calculator": {
        "en": "Green Algorithms calculator",
        "fr": "Calculateur Green Algorithms",
    },
    "Subtitle": {
        "en": "What's the carbon footprint of your computations?",
        "fr": "Quelle est l'empreinte carbone de vos calculs ?",
    },
    "Classic-view": {
        "en": "Classic view",
        "fr": "Interface classique",
    },
    "AI-view": {
        "en": "AI view",
        "fr": "Interface IA",
    },
    "Change language": {
        "en": "Change language",
        "fr": "Choix de la langue",
    },
    "Change data version": {
        "en": "Change data version",
        "fr": "Version des données",
    },
    "Version tooltip": {
        "en": "The calculator data (carbon intensities, hardware...) is regularly updated. "
        "If you want to replicate results obtained in the past, select the corresponding data version.",
        "fr": "The calculator data (carbon intensities, hardware...) is regularly updated. "
        "If you want to replicate results obtained in the past, select the corresponding data version."
    },

    ## NEWS SECTION

    "Some news": {
        "en": "Some news...",
        "fr": "Quelques actualités...",
    },
    "More on the project website": {
        "en": "More on the project website!",
        "fr": "En savoir plus sur le projet du site !",
    },
    "The GREENER principles": {
        "en": "The GREENER principles",
        "fr": "Les principes écologiques",
    },
    "for environmentally sustainable computational science": {
        "en": " for environmentally sustainable computational science.",
        "fr": " pour une science informatique durable.",
    },
    "A short primer": {
        "en": "A short primer",
        "fr": "Une courte revue",
    },
    "carbon footprint estimations": {
        "en": " discussing different options for carbon footprint estimation.",
        "fr": " des outils pour l'estimation de l'empreinte carbone.",
    },
    "Artificial intelligence dedicated page": {
        "en": "Artificial intelligence dedicated page",
        "fr": "Page dédiée à l'intelligence artificielle",
    },

    #### HOME PAGE ####

    ### FORM

    ### Header

    "Details about your algorithm": {
        "en": "Details about your algorithm",
        "fr": "Caractéristiques de votre algorithme",
    },
    "Home_form_subtitle": {
        "en": '''
                To understand how each parameter impacts your environmental footprint, 
                check out the formula below and the [methods article](https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707)
            ''',
        "fr": '''
                To understand how each parameter impacts your environmental footprint, 
                check out the formula below and the [methods article](https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707)
            ''',
    },

    ### Runtime

    "Runtime_label": {
        "en": "Runtime (HH:MM)",
        "fr": "Runtime (HH:MM)",
    },

    ### Cores

    "Type_of_cores_label": {
        "en": "Type of cores",
        "fr": "Type of cores",
    },
    "Type_of_cores_tooltip": {
        "en": "Select the type of hardware used.",
        "fr": "Select the type of hardware used.",
    },

    # CPUs

    "Number_of_cores_used_CPU": {
        "en": "Number of cores used",
        "fr": "Number of cores used",
    },
    "CPU_number_used_tooltip": {
        "en": "Refers to the number of cores used (a single CPU contains several cores).",
        "fr": "Refers to the number of cores used (a single CPU contains several cores).",
    },
    "CPU_Model": {
        "en": "Model",
        "fr": "Modèle",
    },
    "cpu_model_tooltip": {
        "en": '''
                Select 'Average' to run the calculator with the average CPU specs. If you want to enter custom  
                CPU characteristics, please select 'I can't find my CPU' at the top of the list.
            ''',
        "fr": '''
                Select 'Average' to run the calculator with the average CPU specs. If you want to enter custom  
                CPU characteristics, please select 'I can't find my CPU' at the top of the list.
            ''',
    },
    "custom_cpu_title": {
        "en": '''
                If your CPU is not in the list, you can manually input the few key specs used by the calculator. 
                Pre-filled values are average ones.
            ''',
        "fr": '''
                If your CPU is not in the list, you can manually input the few key specs used by the calculator. 
                Pre-filled values are average ones.
            ''',
    },
    "Number_of_cores": {
        "en": "Number of cores",
        "fr": "Number of cores",
    },
    "Number_of_cores_tooltip": {
        "en": "Refers to the number of cores of the CPU model. It is not the number of cores used.",
        "fr": "Refers to the number of cores of the CPU model. It is not the number of cores used.",
    },
    "CPU_TDP_(in_Watt)": {
        "en": "TDP (in Watt)",
        "fr": "TDP (in Watt)",
    },
    "CPU_TDP_tooltip": {
        "en": "The TDP is the Thermal Design Power (TDP) of your CPU, in Watt. It is not a 'per core' value.",
        "fr": "The TDP is the Thermal Design Power (TDP) of your CPU, in Watt. It is not a 'per core' value.",
    },
    "CPU_Die_area_(in_cm2)": {
        "en": "Die area (in cm2)",
        "fr": "Die area (in cm2)",
    },
    "CPU_die_area_tooltip": {
        "en": "The die area of your CPU is expected in cm2. Should include the I/O die size.",
        "fr": "The die area of your CPU is expected in cm2. Should include the I/O die size.",
    },

    # GPUs

    "Number_of_GPUs_used": {
        "en": "Number of GPUs used",
        "fr": "Number of GPUs used",
    },
    "Number_of_GPUs_used_tooltip": {
        "en": "Refers to the number of GPUs used (no cores here).",
        "fr": "Refers to the number of GPUs used (no cores here).",
    },
    "GPU_Model": {
        "en": "Model",
        "fr": "Modèle",
    },
    "gpu_model_tooltip": {
        "en": '''
                Select 'Average' to run the calculator with the average GPU specs. If you want to enter custom  
                GPU characteristics, please select 'I can't find my GPU' at the top of the list.
            ''',
        "fr": '''
                Select 'Average' to run the calculator with the average GPU specs. If you want to enter custom  
                GPU characteristics, please select 'I can't find my GPU' at the top of the list.
            ''',
    },
    "custom_gpu_title": {
        "en": '''
                If your GPU is not in the list, you can manually input the few key specs used by the calculator.
                Pre-filled values are average ones.
            ''',
        "fr": '''
                If your GPU is not in the list, you can manually input the few key specs used by the calculator.
                Pre-filled values are average ones.
            ''',
    },
    "GPU_TDP_(in_Watt)": {
        "en": "TDP (in Watt)",
        "fr": "TDP (in Watt)",
    },
    "GPU_TDP_tooltip": {
        "en": "The TDP is the Thermal Design Power (TDP) of your GPU, in Watt.",
        "fr": "The TDP is the Thermal Design Power (TDP) of your GPU, in Watt.",
    },
    "GPU_Die_area_(in_cm2)": {
        "en": "Die area (in cm2)",
        "fr": "Die area (in cm2)",
    },
    "GPU_die_area_tooltip": {
        "en": "The die size of your GPU is expected in cm2.",
        "fr": "The die size of your GPU is expected in cm2.",
    },
    "GPU_memory_(in_GB)": {
        "en": "Memory (in GB)",
        "fr": "Memory (in GB)",
    },
    "Memory_gpu_tooltip": {
        "en": "The GPU memory size.",
        "fr": "The GPU memory size.",
    },

    ### Memory

    "Memory_available": {
        "en": "Memory available (in GB)",
        "fr": "Memory available (in GB)",
    },
    "Memory_tooltip": {
        "en": "Refers to the total memory allocated to the task, not the memory actually used.",
        "fr": "Refers to the total memory allocated to the task, not the memory actually used.",
    },

    ### Computing platform

    "Select_the_platform_used": {
        "en": "Select the platform used for the computations",
        "fr": "Select the platform used for the computations",
    },
    "Select_the_platform_tooltip": {
        "en": "This field is used to retrieve specific data centre efficiency metricsand location energy mixes.",
        "fr": "This field is used to retrieve specific data centre efficiency metricsand location energy mixes.",
    },
    "Select_server": {
        "en": "Select server",
        "fr": "Select server",
    },
    "Select_location": {
        "en": "Select location",
        "fr": "Select location",
    },
    "Select_location_tooltip": {
        "en": '''
                The location section is used to retrieve the electricity mix and the associated carbon intensity.
                If you want to enter a custom value, please enter 'Use a custom carbon intensity' in the continent dropdown.
            ''',
        "fr": '''
                The location section is used to retrieve the electricity mix and the associated carbon intensity.
                If you want to enter a custom value, please enter 'Use a custom carbon intensity' in the continent dropdown.
            ''',
    },
    "Personal laptop": {
        "en": "Personal laptop",
        "fr": "Personal laptop",
    },
    "Personal workstation": {
        "en": "Personal workstation",
        "fr": "Personal workstation",
    },
    "Local server": {
        "en": "Local server",
        "fr": "Local server",
    },
    "Cloud computing": {
        "en": "Cloud computing",
        "fr": "Cloud computing",
    },

    # Custom carbon intensity

    "Custom_carbon_intensity_header": {
        "en": '''
                Enter your custom carbon intensity below in gCO2e/kWh. 
                The pre-filled value corresponds to the world average electricity mix.
            ''',
        "fr": '''
                Enter your custom carbon intensity below in gCO2e/kWh. 
                The pre-filled value corresponds to the world average electricity mix.
            ''',
    },
    "Carbon_intensity_title": {
        "en": 'Carbon intensity (in gCO2e/kWh)',
        "fr": 'Carbon intensity (in gCO2e/kWh)',
    },
    "Carbon_intensity_tooltip": {
        "en": 'Must be in gCO2e/kWh.',
        "fr": 'Must be in gCO2e/kWh.',
    },

    #### CORE USAGE (CPU and GPU)

    "CPU_usage_factor_label": {
        "en": 'Do you know the real usage factor of your CPU?',
        "fr": 'Do you know the real usage factor of your CPU?',
    },
    "CPU_usage_factor_tooltip": {
        "en": '''
                Between 0 and 1 (default: 1). This is the usage % of the cores, 
                e.g. % of the time the cores were active. 
                This can be obtained from log files for instance.
            ''',
        "fr": '''
                Between 0 and 1 (default: 1). This is the usage % of the cores, 
                e.g. % of the time the cores were active. 
                This can be obtained from log files for instance.
            ''',
    },
    "GPU_usage_factor_label": {
        "en": 'Do you know the real usage factor of your GPU?',
        "fr": 'Do you know the real usage factor of your GPU?',
    },
    "GPU_usage_factor_tooltip": {
        "en": '''
                Between 0 and 1 (default: 1). This is the usage % of the GPUs, 
                e.g. % of the time the GPUs were active. 
                This can be obtained from log files for instance.
            ''',
        "fr": '''
                Between 0 and 1 (default: 1). This is the usage % of the GPUs, 
                e.g. % of the time the GPUs were active. 
                This can be obtained from log files for instance.
            ''',
    },
    
    ### PUE

    "PUE_label": {
        "en": 'Do you know the Power Usage Efficiency (PUE) of your local data centre?',
        "fr": 'Do you know the Power Usage Efficiency (PUE) of your local data centre?',
    },
    "PUE_tooltip": {
        "en": '''
                PUE is a standardised efficiency metrics measuring the 
                energy consumption of data centre overheads (e.g. cooling).
            ''',
        "fr": '''
                PUE is a standardised efficiency metrics measuring the 
                energy consumption of data centre overheads (e.g. cooling).
            ''',
    },

    ### MULTIPLICATIVE FACTOR

    "MF_label": {
        "en": 'Do you want to use a multiplicative factor?',
        "fr": 'Do you want to use a multiplicative factor?',
    },
    "MF_tooltip": {
        "en": '''
                Used to multiply the final results, for example when a same task is repeated 
                multiple times.
            ''',
        "fr": '''
                Used to multiply the final results, for example when a same task is repeated 
                multiple times.
            ''',
    },

    ### AI PAGE ###

    ### TRAINING FORM

    ### Header

    "Training_form_subtitle": {
        "en": '''
                Report your training-related computations. For more information about R&D experiments, 
                retraining or overall tips regarding your reporting, please refer to the Help tab.
            ''',
        "fr": '''
                Report your training-related computations. For more information about R&D experiments, 
                retraining or overall tips regarding your reporting, please refer to the Help tab.
            ''',
    },

    ### R&D trainings

    "R&D_TRAINING_header": {
        "en": 'R&D TRAINING',
        "fr": 'R&D TRAINING',
    },
    "R&D_training_label": {
        "en": 'Do you want to add R&D compute time?',
        "fr": 'Do you want to add R&D compute time?',
    },
    "R&D_training_tooltip": {
        "en": '''
                Used to add R&D compute to the final training impact. 
                If in total you estimate your R&D training computes to represent 
                twice the compute of your final training run, input '2'. 
                If total R&D is about half of the final run, input '0.5'. 
                The resulting value will be added to your main training footprint.
            ''',
        "fr": '''
                Used to add R&D compute to the final training impact. 
                If in total you estimate your R&D training computes to represent 
                twice the compute of your final training run, input '2'. 
                If total R&D is about half of the final run, input '0.5'. 
                The resulting value will be added to your main training footprint.
            ''',
    },

    ### Retrainings

    "RETRAINING_header": {
        "en": 'RETRAINING',
        "fr": 'RETRAINING',
    },
    "retraining_label": {
        "en": 'Do you want to add retraining compute time?',
        "fr": 'Do you want to add retraining compute time?',
    },
    "retraining_tooltip": {
        "en": 'Used if you want to account for model retraining. ',
        "fr": 'Used if you want to account for model retraining. ',
    },
    "Number_of_runs_label": {
        "en": 'Number of runs',
        "fr": 'Number of runs',
    },
    "Number_of_runs_tooltip": {
        "en": 'Number of times you plan to retrain the model over the reporting period.',
        "fr": 'Number of times you plan to retrain the model over the reporting period.',
    },
    "Running_time_label": {
        "en": 'What is the relative runtime of an average retraining run compared to the main training?',
        "fr": 'What is the relative runtime of an average retraining run compared to the main training?',
    },
    "Running_time_tooltip": {
        "en": 'If retraining takes on average 10% of the runtime of the main training, input "0.1".',
        "fr": 'If retraining takes on average 10% of the runtime of the main training, input "0.1".',
    },

    ### INFERENCE FORM
    
    ### Header

    "Inference_form_subtitle": {
        "en": '''
                Report your inference-related computations. For more information about continuous inference, 
                or overall tips regarding your reporting, please refer to the Help tab..
            ''',
        "fr": '''
                Report your inference-related computations. For more information about continuous inference, 
                or overall tips regarding your reporting, please refer to the Help tab..
            ''',
    },

    ### Continuous inference section

    "Apply_continuous_inference_scheme": {
        "en": "Apply continuous inference scheme",
        "fr": "Apply continuous inference scheme",
    },
    "continuous_inference_tooltip": {
        "en": '''
                See the Help tab for more information about continuous inference. 
                If chosen, then only report the computations falling within your ‘input data time span’. 
                Scaling to the reporting period is done automatically.
            ''',
        "fr": '''
                See the Help tab for more information about continuous inference. 
                If chosen, then only report the computations falling within your ‘input data time span’. 
                Scaling to the reporting period is done automatically.
            ''',
    },
    "Input_data_time_span": {
        "en": "Input data time span",
        "fr": "Input data time span",
    },
    "input_data_time_span_tooltip": {
        "en": '''
                The `input data time span` is the length of time over which you are able 
                to estimate your resource usage for continuous inference.
            ''',
        "fr": '''
                The `input data time span` is the length of time over which you are able 
                to estimate your resource usage for continuous inference.
            ''',
    },

    #### IMPORT & EXPORT ####

    "Share_your_results": {
        "en": 'Share your results as a csv file!',
        "fr": 'Share your results as a csv file!',
    },
    "Import_results": {
        "en": '''**Import results**''',
        "fr": '''**Import results**''',
    },
    "drag_and_drop": {
        "en": 'Drag and drop or click to select your .csv file.',
        "fr": 'Drag and drop or click to select your .csv file.',
    },
    "error_message_header": {
        "en": '⚠️ Error when filling values from csv ⚠️',
        "fr": '⚠️ Error when filling values from csv ⚠️',
    },

    #### METRICS ####

    "Carbon_footprint": {
        "en": "Carbon footprint",
        "fr": "Carbon footprint",
    },
    "Energy_needed": {
        "en": "Energy needed",
        "fr": "Energy needed",
    },
    "Carbon_sequestration": {
        "en": "Carbon sequestration",
        "fr": "Carbon sequestration",
    },
    "in_a_passenger_car": {
        "en": "in a passenger car",
        "fr": "in a passenger car",
    },

    #### METHODOLOGY ####

    ### Header container

    "methodology_details_1": {
        "en": '''
                🌱 More details about the methodology in the [methods paper](https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707).
            ''',
        "fr": '''
                🌱 More details about the methodology in the [methods paper](https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707).
            ''',
    },
    "methodology_details_2": {
        "en": '''
                🌱 Other resources you may find interesting on this topic: 
                [the GREENER principles](https://rdcu.be/dfpLM) for environmentally sustainable computational science, 
                or this [short primer](https://www.green-algorithms.org/assets/publications/2023_Comment_NRPM.pdf) 
                discussing different options for carbon footprint estimation.
            ''',
        "fr": '''
                🌱 Other resources you may find interesting on this topic: 
                [the GREENER principles](https://rdcu.be/dfpLM) for environmentally sustainable computational science, 
                or this [short primer](https://www.green-algorithms.org/assets/publications/2023_Comment_NRPM.pdf) 
                discussing different options for carbon footprint estimation.
            ''',
    },
    "methodology_details_3": {
        "en": '''
                🌱 Using a SLURM-powered HPC server? Check out [GA4HPC](https://github.com/GreenAlgorithms/GreenAlgorithms4HPC), 
                it uses the same calculation method but at scale.
            ''',
        "fr": '''
                🌱 Using a SLURM-powered HPC server? Check out [GA4HPC](https://github.com/GreenAlgorithms/GreenAlgorithms4HPC), 
                it uses the same calculation method but at scale.
            ''',
    },
    
    ### Formula

    "The_formula_header": {
        "en": "The formula",
        "fr": "The formula",
    },
    "the_formula_detail": {
        "en": '''
                The carbon footprint is calculated by estimating the energy draw of the algorithm
                and the carbon intensity of producing this energy at a given location:

                `carbon footprint = energy needed * carbon intensity`

                Where the energy needed is: 

                `runtime * (cores power draw * usage + memory power draw) * PUE * multiplicative factor`

                The power draw of the computing cores depends on the model and number of cores, 
                while the memory power draw only depends on the size of memory _available_. 
                The usage factor corrects for the real core usage (default is 1, i.e. full usage).
                The PUE (Power Usage Effectiveness) measures how much extra energy is needed 
                to operate the data centre (cooling, lighting etc.). 
                The multiplicative factor is used to take into account multiple identical runs 
                (e.g. for testing or optimisation).

                The Carbon Intensity depends on the location and the technologies used to produce electricity.
                If you want to check out the carbon intensity in real time, and see discrepancies between countries,
                check out the [ElectricityMap website](https://app.electricitymaps.com/map).
                Also, note that __the "energy needed" indicated at the top of this page is independent of the location.__
            ''',
        "fr": '''
                The carbon footprint is calculated by estimating the energy draw of the algorithm
                and the carbon intensity of producing this energy at a given location:

                `carbon footprint = energy needed * carbon intensity`

                Where the energy needed is: 

                `runtime * (cores power draw * usage + memory power draw) * PUE * multiplicative factor`

                The power draw of the computing cores depends on the model and number of cores, 
                while the memory power draw only depends on the size of memory _available_. 
                The usage factor corrects for the real core usage (default is 1, i.e. full usage).
                The PUE (Power Usage Effectiveness) measures how much extra energy is needed 
                to operate the data centre (cooling, lighting etc.). 
                The multiplicative factor is used to take into account multiple identical runs 
                (e.g. for testing or optimisation).

                The Carbon Intensity depends on the location and the technologies used to produce electricity.
                If you want to check out the carbon intensity in real time, and see discrepancies between countries,
                check out the [ElectricityMap website](https://app.electricitymaps.com/map).
                Also, note that __the "energy needed" indicated at the top of this page is independent of the location.__
            ''',
    },
    
    ### Definitions

    "About_CO2e": {
        "en": "About CO2e",
        "fr": "About CO2e",
    },
    "about_co2_detail": {
        "en": '''
                "Carbon dioxide equivalent" (CO2e) measures 
                the global warming potential of a mixture of greenhouse gases.
                __It represents the quantity of CO2 that would have 
                the same impact on global warming__ as the mix of interest
                and is used as a standardised unit to assess 
                the environmental impact of human activities.
            ''',
        "fr": '''
                "Carbon dioxide equivalent" (CO2e) measures 
                the global warming potential of a mixture of greenhouse gases.
                __It represents the quantity of CO2 that would have 
                the same impact on global warming__ as the mix of interest
                and is used as a standardised unit to assess 
                the environmental impact of human activities.
            ''',
    },
    "What_is_a_tree-month": {
        "en": "What is a tree-month?",
        "fr": "What is a tree-month?",
    },
    "What_is_a_tree-month_details": {
        "en": '''
                It's the amount of CO2 sequestered by a tree in a month.
                __We use it to measure how long it would take to a mature tree
                to absorb the CO2 emitted by an algorithm.__
                We use the value of 11 kg CO2/year, which is roughly 1kg CO2/month.
            ''',
        "fr": '''
                It's the amount of CO2 sequestered by a tree in a month.
                __We use it to measure how long it would take to a mature tree
                to absorb the CO2 emitted by an algorithm.__
                We use the value of 11 kg CO2/year, which is roughly 1kg CO2/month.
            ''',
    },


    #### APP FOOTER ####

    ### DATA AND CODE

    "Data and code": {
        "en": "Data and code",
        "fr": "Code et données",
    },
    "Data_and_code_text": {
        "en": '''
                All the data and code used to run this calculator can be found on 
                [GitHub](https://github.com/GreenAlgorithms/green-algorithms-tool)
            ''',
        "fr": '''
                Toutes les données et le code du calculateur se trouvent sur 
                [GitHub](https://github.com/GreenAlgorithms/green-algorithms-tool)
            ''',
    },
    
    ### SUGGESTIONS

    "Questions_suggestions": {
        "en": "Questions / Suggestions?",
        "fr": "Questions / suggestions ?",
    },
    "Questions_suggestions_text": {
        "en": '''
                If you have questions or suggestions about the tool, you can 
                [open an issue](https://github.com/GreenAlgorithms/green-algorithms-tool/issues)
                on the Github or [email us](mailto:green.algorithms@gmail.com).
            ''',
        "fr": '''
                Si vous avez des questions ou des suggestions concernant l'outil, vous pouvez 
                [ouvrir une 'issue'](https://github.com/GreenAlgorithms/green-algorithms-tool/issues) 
                sur le Github ou [nous envoyer un mail](mailto:green.algorithms@gmail.com).
            ''',
    },

    ### HOW TO CITE

    "How to cite this work": {
        "en": "How to cite this work",
        "fr": "Citer ce travail",
    },
    "How_to_cite_text": {
        "en": '''
                Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. 
                Adv. Sci. 2021, 2100707 [https://doi.org/10.1002/advs.202100707](https://doi.org/10.1002/advs.202100707).
            ''',
        "fr": '''
                Lannelongue, L., Grealey, J., Inouye, M., Green Algorithms: Quantifying the Carbon Footprint of Computation. 
                Adv. Sci. 2021, 2100707 [https://doi.org/10.1002/advs.202100707](https://doi.org/10.1002/advs.202100707).
            ''',
    },


    ### ABOUT US

    "About us": {
        "en": "About us",
        "fr": "Qui nous sommes",
    },
    "About_us_text": {
        "en":  '''
                    The Green Algorithms project is led by [Loïc Lannelongue](www.lannelongue-group.org) and 
                    [Michael Inouye](https://www.inouyelab.org/home/people) at the University of Cambridge, 
                    but made possible by the contribution and support of many: [full list here](https://www.green-algorithms.org/about/).
                ''',
        "fr":  '''
                    Le projet Green Algorithms est piloté par [Loïc Lannelongue](www.lannelongue-group.org) et 
                    [Michael Inouye](https://www.inouyelab.org/home/people) à l'université de Cambridge,
                    mais a bénéficié de la contribution et du soutien de beaucoup : [liste complète des contributeurs](https://www.green-algorithms.org/about/).
                '''
    },
    "About_us_text_2": {
        "en":  '''
                    *In particular, we are thankful for the development work of Even Matencio and the support of the Wellcome Trust,
                    NIHR Cambridge Biomedical Research Centre, and French Department for the Ecological Transition.*
                ''',
        "fr":  '''
                    *En particulier, nous sommes reconnaissants pour le travail d'implémentation mené par Even Matencio et pour le soutien 
                    du Wellcome Trust, du NIHR Cambridge Biomedical Research Centre et celui du Ministère en charge de la transition écologique français.*
                '''
    },

    ### SHOW YOUR STRIPES

    "ShowYourStripes": {
        "en": "#ShowYourStripes",
        "fr": "#ShowYourStripes",
    },
    "ShowYourStripes_text": {
        "en": '''
                These coloured stripes in the background represent the change in world temperatures 
                from 1850 to 2018. This striking design was made by Ed Hawkins from the University of Reading. 
            ''',
        "fr": '''
                These coloured stripes in the background represent the change in world temperatures 
                from 1850 to 2018. This striking design was made by Ed Hawkins from the University of Reading. 
            ''',
    },
    "More_on": {
        "en": '''More on [ShowYourStripes.info](https://showyourstripes.info)''',
        "fr": '''More on [ShowYourStripes.info](https://showyourstripes.info)''',
    },
    "Additional_credits": {
        "en": '''
                Additional credits for the app can be found on the 
                [GitHub](https://github.com/GreenAlgorithms/green-algorithms-tool)
            ''',
        "fr": '''
                Additional credits for the app can be found on the 
                [GitHub](https://github.com/GreenAlgorithms/green-algorithms-tool)
            ''',
    },

    ### MISCELLANEOUS

    '': { # For empty texts
        "en": '',
        "fr": ''
    }

}