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

    "Number_of_cores_used": {
        "en": "Number of cores used",
        "fr": "Number of cores used",
    },
    "CPU_number_used_tooltip": {
        "en": "Refers to the number of cores used (a single CPU contains several cores).",
        "fr": "Refers to the number of cores used (a single CPU contains several cores).",
    },
    "Model": {
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
    "TDP_(in_Watt)": {
        "en": "TDP (in Watt)",
        "fr": "TDP (in Watt)",
    },
    "TDP_tooltip": {
        "en": "The TDP is the Thermal Design Power (TDP) of your CPU, in Watt. It is not a 'per core' value.",
        "fr": "The TDP is the Thermal Design Power (TDP) of your CPU, in Watt. It is not a 'per core' value.",
    },
    "Die_area_(in_cm2)": {
        "en": "Die area (in cm2)",
        "fr": "Die area (in cm2)",
    },
    "die_area_tooltip": {
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
    "gpu_TDP_tooltip": {
        "en": "The TDP is the Thermal Design Power (TDP) of your GPU, in Watt.",
        "fr": "The TDP is the Thermal Design Power (TDP) of your GPU, in Watt.",
    },
    "gpu_die_area_tooltip": {
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