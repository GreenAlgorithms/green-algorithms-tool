import dash_bootstrap_components as dcc
import pandas as pd
import datetime

from dash import ctx
from dash_extensions.enrich import DashBlueprint, PrefixIdTransform, Output, Input, State
from dash.exceptions import PreventUpdate

from utils.handle_inputs import  open_input_csv_and_comment

from blueprints.import_export.import_export_layout import get_green_algo_import_export_layout

def get_import_expot_blueprint(id_prefix):

    import_export_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix
            )
        ]
    )
        
    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    import_export_blueprint.layout = get_green_algo_import_export_layout()


    ##### DEFINE ITS CALLBACKS
    ##########################

    ################## EXPORT DATA

    @import_export_blueprint.callback(
        Output("aggregate-data-csv", "data"),
        Input("btn-download_csv", "n_clicks"),
        State('aggregate_data', "data"),
        prevent_initial_call=True,
    )
    def export_as_csv(_, aggregate_data):
        '''
        Exports the aggregate_data.
        '''
        to_export_dict = {key: [str(val)] for key, val in aggregate_data.items()}
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        to_export = pd.DataFrame.from_dict(to_export_dict, orient='columns')
        return dcc.send_data_frame(to_export.to_csv, f"GreenAlgorithms_results_{now}.csv", index=False, sep=';')


    ################## IMPORT DATA

    @import_export_blueprint.callback(
            [
                Output('import-content', 'data'),
            ],
            [
                Input('upload-data', 'contents'),
            ],
            [
                State('import-content', 'data'),
            ],
    )
    def read_input(upload_content, current_import_data):
        '''
        Open input file and extract data from csv if possible.
        Does not process the content, just proceeds to raw extraction.
        '''
        # NOTE this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
        # this is also the case for most of the callbacks taking the csv upload content as input, and was already the case when using 
        # the url instead of csv files for sharing the results
        # TODO understand this behaviour
        if ctx.triggered_id is None:
            raise PreventUpdate 
        
        # when the upload_content is automatically flushed, we want to keep the same data
        if upload_content is None:
            return current_import_data
    
        return upload_content
        

    
    @import_export_blueprint.callback(
        Output('upload-data', 'contents'),
        Input('csv-input-timer', 'n_intervals'),
        prevent_initial_call=True,
    )
    def flush_input_csv_content(n):
        '''
        Flushes the input csv.
        This is required if we want to enable the user to load again the same csv.
        Otherwise, if not flushed, the csv content does not change so it does not trigger
        the reading of its content.
        '''
        return None
    
    @import_export_blueprint.callback(
        Output('csv-input-timer', 'disabled'),
        Input('upload-data', 'contents'),
        prevent_initial_call=True,
    )
    def trigger_timer_to_flush_input_csv(input_csv):
        '''
        When a csv is dropped, triggers a timer that allows to flush this csv.
        If the input is none, this means that we just flushed it so we do not
        trigger the timer again.
        '''
        if input_csv is None:
            return True
        return False
    
    return import_export_blueprint