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
        className='methodolgy-container'
    )