from dash_extensions.enrich import DashBlueprint, PrefixIdTransform, Output, Input

from blueprints.results.results_layout import get_green_algo_results_layout

def get_results_blueprint(id_prefix):

    results_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix
            )
        ]
    )
    
    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    results_blueprint.layout = get_green_algo_results_layout()


    ##### DEFINE ITS CALLBACKS
    ##########################


    @results_blueprint.callback(
        [
            Output("carbonEmissions_text", "children"),
            Output("energy_text", "children"),
            Output("treeMonths_text", "children"),
            Output("driving_text", "children"),
            Output("flying_text", "children"),
            Output("flying_label", "children"),
        ],
        [Input(f'aggregate_data', "data")],
    )
    def update_text(data):
        text_CE = data.get('text_CE')
        text_energy = data.get('text_energyNeeded')
        text_ty = data.get('text_treeYear')
        if (data['nkm_drivingEU'] != 0) & ((data['nkm_drivingEU'] >= 1e3) | (data['nkm_drivingEU'] < 0.1)):
            text_car = f"{data['nkm_drivingEU']:,.2e} km"
        else:
            text_car = f"{data['nkm_drivingEU']:,.2f} km"
        if data['flying_context'] == 0:
            text_fly = "0"
        elif data['flying_context'] > 1e6:
            text_fly = f"{data['flying_context']:,.0e}"
        elif data['flying_context'] >= 1:
            text_fly = f"{data['flying_context']:,.1f}"
        elif data['flying_context'] >= 0.01:
            text_fly = f"{data['flying_context']:,.0%}"
        elif data['flying_context'] >= 1e-4:
            text_fly = f"{data['flying_context']:,.2%}"
        else:
            text_fly = f"{data['flying_context']*100:,.0e} %"
        if (data['flying_context'] >= 1) | (data['flying_context'] == 0):
            label_fly = f"flights {data['flying_text']}"
        else:
            label_fly = f"of a flight {data['flying_text']}"
        return text_CE, text_energy, text_ty, text_car, text_fly, label_fly
    
    return results_blueprint
