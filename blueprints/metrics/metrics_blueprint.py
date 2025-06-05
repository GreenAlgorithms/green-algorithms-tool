from types import SimpleNamespace
from dash_extensions.enrich import DashBlueprint, PrefixIdTransform, Output, Input, State
from dash import html

from utils.utils import custom_prefix_escape
from blueprints.metrics.metrics_layout import get_green_algo_metrics_layout
import blueprints.metrics.utils as utils


def get_metrics_blueprint(
        id_prefix: str,
        energy_needed_details: html.Div = html.Div(style={"display": "none"}),
        carbon_footprint_details: html.Div = html.Div(style={"display": "none"}),
    ):

    results_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix,
                escape=custom_prefix_escape
            )
        ]

    )
    
    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    results_blueprint.layout = get_green_algo_metrics_layout(
            carbon_footprint_details,
            energy_needed_details
        )


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
        [
            Input(f'base_results', 'data'),
        ],
        State('versioned_data', 'data'),
    )
    def update_results_and_texts(results_dict, versioned_data):
        # Retrieve base results
        energy_needed = results_dict['energy_needed']  # in kWh
        text_energy = utils.format_energy_text(energy_needed)
        carbon_emissions = results_dict['carbonEmissions']  # in g CO2e
        text_CE = utils.format_CE_text(carbon_emissions)
        # Compute corresponding metrics
        if versioned_data is not None: 
            versioned_data = SimpleNamespace(**versioned_data)
            text_ty = utils.write_tree_months_equivalent(carbon_emissions, versioned_data.refValues_dict)
            text_car = utils.write_driving_equivalent(carbon_emissions, versioned_data.refValues_dict)
            text_trip_proportion, flying_text = utils.write_plane_trip_equivalent(carbon_emissions, versioned_data.refValues_dict)
        else:
            text_ty, text_car, text_trip_proportion, flying_text = '', '', '', ''
        return text_CE, text_energy, text_ty, text_car, text_trip_proportion, flying_text
    
    return results_blueprint






