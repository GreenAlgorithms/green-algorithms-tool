'''
Implements the methodology blueprint.

Actually, as the methodology content is static, there is no callback to implement.
The reason for this file is mostly to respect the structure of the other blueprint folders.
'''

from dash_extensions.enrich import DashBlueprint, PrefixIdTransform
from dash import dcc

from blueprints.methodology.methodology_layout import get_green_algo_methodology_layout

def get_methodology_blueprint(
        id_prefix: str,
        additional_formula_content: dcc.Markdown = dcc.Markdown()
    ):

    methodo_blueprint = DashBlueprint(
        transforms=[
            PrefixIdTransform(
                prefix=id_prefix
            )
        ]
    )

    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    methodo_blueprint.layout = get_green_algo_methodology_layout(additional_formula_content)

    return methodo_blueprint