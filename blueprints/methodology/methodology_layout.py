'''
This script contains:
    - the layout of the home page's methodology sections
    - the layout of the training and inference help tabs
'''

from dash import html, dcc
import dash_mantine_components as dmc



def get_green_algo_methodology_layout():
    return html.Div(
        [
            #### PUBLICATION ####

            html.Div(
                [
                    # html.Center(
                    html.P(html.B(["🌱 More details about the methodology in the ",
                            html.A("methods paper",
                                   href='https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707',
                                   target='_blank'),
                            "."
                            ])),
                    # ),
                    html.P([
                        html.B("🌱 Other resources you may find interesting on this topic: "),
                        html.A("the GREENER principles", href="https://rdcu.be/dfpLM", target="_blank"),
                        " for environmentally sustainable computational science, ",
                        "or this ",
                        html.A("short primer",
                               href="https://www.green-algorithms.org/assets/publications/2023_Comment_NRPM.pdf",
                               target="_blank"),
                        " discussing different options for carbon footprint estimation."
                    ]),
                    html.P([
                        html.B("🌱 Using a SLURM-powered HPC server?"),
                        " Check out ",
                        html.A("GA4HPC",
                               href="https://github.com/GreenAlgorithms/GreenAlgorithms4HPC",
                               target="_blank"),
                        ", it uses the same calculation method but at scale."
                    ])
                ],
                className='container text-italic'
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

                        `runtime * (cores power draw * usage + memory power draw) * PUE * multiplicative factor`

                        The power draw of the computing cores depends on the model and number of cores, 
                        while the memory power draw only depends on the size of memory __available__. 
                        The usage factor corrects for the real core usage (default is 1, i.e. full usage).
                        The PUE (Power Usage Effectiveness) measures how much extra energy is needed 
                        to operate the data centre (cooling, lighting etc.). 
                        The Multiplicative Factor is used to take into account multiple identical runs 
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
            
            html.Div(
                [

                    html.H4('Overall description'),

                    dcc.Markdown(
                        '''
                        The training phase of your AI system covers __different kinds of computations__:
                        R&D experiments, the main training of your model and potential retrainings (more details are given below).
                        
                        We invite you to quantify all these computations through the training form. 
                        To do so, __fill-in the form based on your main training requirements.
                        Then use the input fields available at the bottom of the form to give an approximative 
                        estimate of your computations share due to R&D trainings or retrainings__.
                        Some R&D use cases are illustrated in more details below. 

                        This approach has limitations because different hardware might be used for different training phases but it offers a trade-off between the reporting effort and the final estimate quality.
                        If you wish to quantify more precisely the other computation phases, we invite you to fill a form especially for each of them. 
                        ''',
                        className='form-help-markdown'
                    ),
                ],
                className='form-help-subsection',
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div'
            ),

            html.Div(
                [
                    html.H4('Definitions and practical tips'),

                    dcc.Markdown(

                        ''' 
                        __Main training__: the computations performed to achieve the final model deployed in your AI solution. 
                        It can either correspond to the training from scrath of a custom model or to the fine-tuning of an existing model.

                        __R&D trainings__: corresponds to the different experimental trainings and computations performed before the final training of your model.
                        Such experiments may be useful to calibrate the final architecture or hyper-parameters set of your model.
                        R&D trainings are taken into account using a simple scaling factor corresponding to the ratio between your R&D and your main training computational needs.

                        __Retrainings__: any additional trainings performed after the deployment of your AI system.
                        For consistent reporting, you are invited to take into account all retrainings requirements over your reporting time scope.
                        To do so, we invite you to fill in the number of retrainings and a simple scaling factor corresponding to the ratio between a single average retraining and your main training computational needs.
                        '''
                    ),
                ],
                className='form-help-subsection',
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div',
            ),

            html.Div(
                [
                    html.H4('Some examples of R&D experiment scenarios'),

                    dcc.Markdown(
                        '''
                        The amount of computation requirements due to your R&D experiment stage may vary significantly depending on your project and AI system. 
                        __We invite you to consider both architectural and hyperparemeters experiments, performed on either the whole data set or a subset of it.__
                        We provide some qualitative examples to help you better understand what is expected.
                        ''',
                    ),
                ]
            ),

            html.Div(
                [
                
                    dcc.Markdown(
                        '''
                        When training classic machine learning models (XGBoots or SVM for instance), it is very frequent to run dozens or hundreds of real scale
                        experiments before choosing the final model. In this case, the scaling factor of your experiments stage may vary between 10 and 100 for instance.

                        Regarding "intermediate" neural networks training (less than 1 billon parameters), typically for small image classification models, the number of
                        real scale experiments may still be significant. The scaling factor will more likely be in the range of 10.

                        Eventually, among the few scientific papers that precisely quantify their computational needs due to the experiments preceding the main training, Luccioni et al. \[1\]
                        estimate that intermediate models training and evaluation account for approximately 150% of their main training consumption.
                        The final model is a 176 billon parameters LLM, developped in an academic context.
                        ''',
                        style={'margin-top': '8px'}
                    ),

                    dcc.Markdown(
                        '\[1\] A. S. Luccioni, S. Viguier, and A.-L. Ligozat, “Estimating the Carbon Footprint of BLOOM, a 176B Parameter Language Model,” Journal of Machine Learning Research, vol. 24, no. 253, pp. 1–15, 2023',
                        className='footnote citation-report',
                        style={'margin-top': '8px'}
                    ),
                ],
                className='form-help-subsection',
            )
        ],
        className='form-help-container pretty-container container'
    )

def get_inference_help_content(title: str):
    return html.Div(
        [
            html.H3(title),

            html.Div(
                [
                    html.H4('Overall description'),

                    dcc.Markdown(
                        '''
                        The inference form should enable you to quantify the environmental footprint of you AI system's inference phase over the whole reporting time scope.
                        __To do so, we distinguish between two inference schemes: block (or one-shot) inference and continuous inference defined below__.

                        By default, the form is in 'block inference' mode but you can actiave the continuous mode using the switcher at the top of the form.
                        '''
                    )
                ],
                className='form-help-subsection',
            ),

            html.Div(
                [
                    html.Hr(),
                ],
                className='Hr_div',
            ),

            html.Div(
                [
                    html.H4('Definitions and practical tips'),

                    dcc.Markdown(
                        '''
                        __Block (one-shot) inference__: corresponds to an AI service that is occasionally requested in a one-shot fashion. 
                        It may be used to process a data set as a whole or to build one-day or one-week strategy. 
                        As a number of them may happen over your reporting time scope, we invite you to quantify the computation requirements for one inference block and then to use the Multiplicative Scaling Factor.
                        ''',
                        style={'margin-bottom': '6px'}
                    ),

                    dcc.Markdown(
                        '''
                        __Continuous inference__: corresponds to an AI service that is requested on demand by users or other software systems. 
                        This inference workload does not follow a strict scheduling, making it harder to quantify. In this mode, we invite you to estimate the computations requirements over a time length of your choice, the so-called "input data time span”. 
                        Based on this and the reporting time scope value, your total inference footprint is computed with a simple scaling factor.
                        ''',
                        style={'margin-bottom': '12px'}
                    ),

                    dcc.Markdown(
                        '''
                        It is important to keep in mind that __the reporting time scope does have an influence on the computations only when choosing the 'continuous inference scheme'__.
                        In that case, the environmental impacts are automatically scaled from your "`input data time span`" to your reporting time scope.
                        For instance, if choosing a reporting scope of 1 year and filling the form in continuous inference mode with an "`input data time span`" of 1 month,
                        then your environmental impacts correspond to the intermediate metrics computed from the input fields, multiplied by 12.
                        ''',
                    ),

                ],
                className='form-help-subsection',
            )
        ],
        className='form-help-container container'
    )