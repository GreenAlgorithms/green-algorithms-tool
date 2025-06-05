'''
Implements the import-export blueprint.

When a csv is uploaded, the dcc.Upload component (id=upload-data) is 
automatically flushed after few seconds to let the user upload the same file again.
Otherwise, the callbacks with Input upload-data would not trigger because upload-data 
actually remained the same.
'''

import pandas as pd
import datetime

from dash import ctx, dcc
from dash_extensions.enrich import DashBlueprint, PrefixIdTransform, Output, Input, State
from dash.exceptions import PreventUpdate

from blueprints.import_export.import_export_layout import get_green_algo_import_export_layout


def get_import_expot_blueprint(  # TODO correct typo
    id_prefix: str,
    csv_flushing_delay: int = 1500,
):
    """
    Args:
        id_prefix (str): id prefix automatically applied to all components.
        csv_flushing_delay (int, optional): time delay between csv upload and csv flushing.
        Given in miliseconds. Defaults to 1500.
    """
    import_export_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix
            )
        ]
    )
        
    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    import_export_blueprint.layout = get_green_algo_import_export_layout(csv_flushing_delay)


    ##### DEFINE ITS CALLBACKS
    ##########################

    ################## EXPORT DATA

    @import_export_blueprint.callback(
        Output("aggregate-data-csv", "data"),
        Input("export-content", "data"),
        prevent_initial_call=True,
    )
    def export_as_csv(aggregate_data):
        """
        Exports the aggregate_data.
        TODO: modify the suffix strategy because not robust with respect to the prefix of the AI page's components
        """
        file_suffixe = ''
        if ctx.triggered_id is not None and 'ai-' in ctx.triggered_id:
            file_suffixe = 'AI'
        to_export_dict = {key: [str(val)] for key, val in aggregate_data.items()}
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        to_export = pd.DataFrame.from_dict(to_export_dict, orient='columns')
        return dcc.send_data_frame(to_export.to_csv, f"GreenAlgorithms_results_{file_suffixe}_{now}.csv", index=False, sep=';')

    ################## IMPORT DATA

    @import_export_blueprint.callback(
        Output('import-content', 'data'),
        Input('upload-data', 'contents'),
        State('import-content', 'data'),
    )
    def read_input(upload_content: dict, current_import_data: dict):
        """
        Open input file and extract data from csv if possible.
        Does not process the content, just proceeds to raw extraction.
        """
        # NOTE this callback fires for no reason (ctx.triggered_id is None) which happens after each regular trigger of the callback
        # this is also the case for most of the callbacks taking the csv upload content as input, and was already the case when using 
        # the url instead of csv files for sharing the results
        # TODO understand this behaviour
        if ctx.triggered_id is None:
            raise PreventUpdate 
        
        # The following case only happens when the upload-data is automatically flushed 
        # Therefore, we want to return the data that was previously uploaded
        if upload_content is None:
            return current_import_data
    
        return upload_content
    
    @import_export_blueprint.callback(
        Output('upload-data', 'contents'),
        Input('csv-input-timer', 'n_intervals'),
        prevent_initial_call=True,
    )
    def flush_input_csv_content(n):
        """
        Flushes the input csv.
        This is required if we want to enable the user to load the same csv again.
        Otherwise, if not flushed, the csv content does not change so it does not trigger
        the reading of its content.
        """
        return None
    
    @import_export_blueprint.callback(
        Output('csv-input-timer', 'disabled'),
        Input('upload-data', 'contents'),
        prevent_initial_call=True,
    )
    def trigger_timer_to_flush_input_csv(input_csv):
        """
        When a csv is dropped, triggers a timer that allows to flush this csv.
        If the input is none, this means that we just flushed it so we do not
        trigger the timer again.
        """
        return input_csv is None
    
    return import_export_blueprint