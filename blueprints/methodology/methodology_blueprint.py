from dash_extensions.enrich import DashBlueprint, PrefixIdTransform

from blueprints.methodology.methodology_layout import get_green_algo_methodology_layout

def get_methodology_blueprint(id_prefix):

    methodo_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix
            )
        ]
    )

    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    methodo_blueprint.layout = get_green_algo_methodology_layout()

    return methodo_blueprint