from dash import html, dcc

def get_green_algo_methodology_layout():
    return html.Div(
        [
         #### PUBLICATION ####

            html.Div(
                [
                    html.Center(
                        html.P(["More details about the methodology in the ",
                                html.A("methods paper",
                                       href='https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707',
                                       target='_blank'),
                                "."
                                ]),
                    ),
                ],
                className='container footer preprint'
            ),
            #### FORMULA ####

            html.Div(
                [
                    html.H2("The formula"),

                    dcc.Markdown('''
                        The carbon footprint is calculated by estimating the energy draw of the algorithm
                        and the carbon intensity of producing this energy at a given location:

                        `carbon footprint = energy needed * carbon intensity`

                        Where the energy needed is: 

                        `runtime * (cores power draw cores * usage + memory power draw) * PUE * PSF`

                        The power draw of the computing cores depends on the model and number of cores, 
                        while the memory power draw only depends on the size of memory __available__. 
                        The usage factor corrects for the real core usage (default is 1, i.e. full usage).
                        The PUE (Power Usage Effectiveness) measures how much extra energy is needed 
                        to operate the data centre (cooling, lighting etc.). 
                        The PSF (Pragmatic Scaling Factor) is used to take into account multiple identical runs 
                        (e.g. for testing or optimisation).

                        The Carbon Intensity depends on the location and the technologies used to produce electricity.
                        If you want to check out the carbon intensity in real time, and see discrepancies between countries,
                        check out the [ElectricityMap website](https://app.electricitymaps.com/map).
                        Also, note that __the "energy needed" indicated at the top of this page is independent of the location.__
                        ''')
                ],
                className='container formula'
            ),

            #### DEFINITIONS ####

            html.Div(
                [
                    html.Div(
                        [
                            html.H2("About CO2e"),

                            dcc.Markdown('''
                            "Carbon dioxide equivalent" (CO2e) measures 
                            the global warming potential of a mixture of greenhouse gases.
                            __It represents the quantity of CO2 that would have 
                            the same impact on global warming__ as the mix of interest
                            and is used as a standardised unit to assess 
                            the environmental impact of human activities.
                            ''')
                        ],
                        className='container'
                    ),

                    html.Div(
                        [
                            html.H2("What is a tree-month?"),

                            dcc.Markdown('''
                            It's the amount of CO2 sequestered by a tree in a month.
                            __We use it to measure how long it would take to a mature tree
                            to absorb the CO2 emitted by an algorithm.__
                            We use the value of 11 kg CO2/year, which is roughly 1kg CO2/month.
                            '''),
                        ],
                        className='container'
                    ),
                ],
                className='super-section definitions'
            ),
        ],
        className='methodology-container'
    )


def get_training_help_content(title: str):
    return html.Div(
        [
            html.H3(title),

            html.Center(
                [

                    dcc.Markdown(
                        '''
                        The training phase of your AI system covers different kinds of computations:
                        __R&D experiments, the main training of your model and potential retrainings__ (more details are given below).
                        
                        We invite you to quantify all these computations through the training form. 
                        To do so, we recommend you to fill-in the form based on your main training requirements.
                        Then use the input fields available at the bottom of the form to give an approximative 
                        estimate of your computations share due to R&D trainings or retrainings.
                        Some use cases are illustrated in more details below.

                        This approach has limitations because different hardware might be used for different training phases but offers a trade-off between the reporting effort and the final estimate quality.
                        If you wish to quantify more precisely the other computation phases, we invite you to fill a form especially for each of them. 
                        '''
                    ),

                ]
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div',
                style = {'margin-top': '20px'}
            ),

            dcc.Markdown(
                '''
                - `main training`: The computations performed to achieve the final model to be deployed in your AI solution.
                It can either correspond to the training from scrath of a custom model or to the fine-tuning of an existing model. 

                - `R&D trainings`: Corresponds to the different experimental trainings and computations performed before the final training of your model. 
                Such experiments may be useful to calibrate the final architecture or hyper-parameters set of your model.

                - `retrainings`: Any additional trainings performed after the deployment of your AI system.
                For consistent reporting, you are invited to take into account all retrainings requirements over your reporting time scope.
                '''
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div',
                style = {'margin-top': '20px'}
            ),

            dcc.Markdown(
                '''
                > Ajouter des exemples de cas d'usage sur le R&D training par exemple ?
                '''
            ),
        ],
        className='form-help-container pretty-container container'
    )

def get_inference_help_content(title: str):
    return html.Div(
        [
            html.H3(title),
            html.Center(
                dcc.Markdown(
                    '''
                    The inference form should enable you to quantify the environmental footprint of you AI system's inference phase over the whole reporting time scope.
                    To do so, `we distinguish between two inference schemes: block (or one-shot) inference and continuous inference`:

                    - __continuous inference__: corresponds to an AI service that is requested on demand by users or other software systems. 
                    > In this mode, we invite you to quantify how long ...
                    For consistent reporting, we invite you to estimate the computations requirements associated with continuous inference over a well-known time length, the so-called "knowledge time scope'.
                    Based on this and the reporting time scope value, your total inference footprint is computed with a simple scaling factor.

                    - __block (one-shot) inference__: corresponds to an AI service that is occasionally requested in a one-shot fashion. 
                    It may be used to process a data set as a whole or to build one-day or one-week strategy.
                    As few of them should happen during over your reporting time scope, we invite you to quantify the computation requirements for one block and then use the Pragmatic Scaling Factor.

                    It is important to keep in mind that these two kind of inference have no clear border: 
                    you may prefer to use the knowledge time scope to automatically scale your block inference computations to the reporting scope.
                    Conversely, you can also estimate the whole continuous inference requirements as a block over the whole
                    '''
                )
            )
        ],
        className='form-help-container container'
    )