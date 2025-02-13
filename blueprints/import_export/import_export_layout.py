""" Import-export layout. """

from dash import html, dcc
import dash_bootstrap_components as dbc 


def get_green_algo_import_export_layout(
    csv_flushing_delay: int
):
    return html.Div(
        [

            #### BACKEND DATA ####
                
            # Intermediate variable used to read the uploaded data only once
            # Its is then forwared to the target form(s) depending on the page
            dcc.Store(id='import-content'),
            # Intermediate variable that is updated only when the user want to export data as csv.
            # It is useful as it allows to run the callback only once per export, not after each form modification.
            dcc.Store(id='export-content'),

    
            html.Div(
                [
                    #### EXPORT DATA ####

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
                    
                    #### IMPORT DATA ####

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

            #### ERROR MESSAGE ####

            dbc.Alert(
                [
                    html.B('Filling values from csv: error'),
                    html.Div(id='log-error-subtitle'),
                    html.Div(id='log-error-content'),
                ],
                className='container footer import-error-message',
                id='import-error-message',
                is_open=False,
                duration=60000,
            ),

            dcc.Interval(
                id='csv-input-timer',
                interval=csv_flushing_delay, 
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
