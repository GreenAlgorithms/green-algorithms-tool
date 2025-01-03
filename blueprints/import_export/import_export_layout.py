from dash import html, dcc
import dash_bootstrap_components as dbc 

def get_green_algo_import_export_layout():
    return html.Div(
        [
            dcc.Store(id='import-content'),
            dcc.Store(id='export-content'),

            html.Div(
                [
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.B("Share your results "),
                                    html.A(html.B('as a csv file!'), id='btn-download_csv', className='btn-download_csv'),
                                    dcc.Download(id="aggregate-data-csv"),
                                ],
                            )
                        ],
                        className='container footer import-export',
                        id='export-result',
                    ),

                    html.Div(
                        dcc.Upload(
                            html.Div(
                                [
                                    html.B("Import resuts"),
                                    html.Div(
                                        [
                                            html.A("Drag and drop or click to select your .csv file.")
                                        ],
                                        style={'font-size': '12px', 'margin-top': '3px', 'text-decoration': 'underline'}
                                    )
                                ]
                            ),
                            id='upload-data',
                            className='upload-data',
                        ),
                        className='container footer import-export import-result',
                        id='import-result',
                    ),
                ],
                className='import-export-buttons',
            ),

            dbc.Alert(
                [
                    html.B('Filling values from csv: error'),
                    html.Div(id='log-error-subtitle'),
                    html.Div(id='log-error-content'),
                ],
                className = 'container footer import-error-message',
                id='import-error-message',
                is_open=False,
                duration=60000,
            ),

            dcc.Interval(
                id='csv-input-timer',
                interval=2000, 
                # in milliseconds, should not be lower than 1000
                # otherwise the update of the upload csv content is done too soon
                # and there is not consistency between the state of the form and 
                # the content  of the csv
                disabled=True
            ),
        ],
        id='import-export',
        className='import-export-container'
    )