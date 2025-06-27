"""
Implements the methodology blueprint.
"""

from dash_extensions.enrich import DashBlueprint, PrefixIdTransform
from dash import html, dcc

class MethodologyBlueprint(DashBlueprint):
    '''
    Actually, as the methodology content is static, there is no callback to implement.
    The reason for this file is mostly to respect the structure of the other blueprint folders.
    '''
    
    def __init__(
            self,
            id_prefix: str,
            additional_formula_content: dcc.Markdown = dcc.Markdown()
        ):
        '''
        Args:
            additional_formula_content (dcc.Markdown): textual content located below "The formula" header
        '''
        super().__init__(transforms = [PrefixIdTransform(prefix = id_prefix)])
        self.layout = self._get_layout(additional_formula_content)

    def _get_layout(self, additional_formula_content: dcc.Markdown):
        return html.Div(
        [
            #### PUBLICATION ####

            html.Div(
                [
                    html.P(
                        html.B(
                            [
                                "🌱 More details about the methodology in the ",
                                html.A("methods paper",
                                    href='https://onlinelibrary.wiley.com/doi/10.1002/advs.202100707',
                                    target='_blank'),
                                "."
                            ]
                        )
                    ),

                    html.P(
                        [
                            html.B("🌱 Other resources you may find interesting on this topic: "),
                            html.A("the GREENER principles", href="https://rdcu.be/dfpLM", target="_blank"),
                            " for environmentally sustainable computational science, ",
                            "or this ",
                            html.A("short primer",
                                href="https://www.green-algorithms.org/assets/publications/2023_Comment_NRPM.pdf",
                                target="_blank"),
                            " discussing different options for carbon footprint estimation."
                        ]
                    ),

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

                    additional_formula_content,

                    dcc.Markdown('''
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
