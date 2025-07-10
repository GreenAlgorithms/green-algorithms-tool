"""
Implements the methodology blueprint.
"""

from dash_extensions.enrich import DashBlueprint, PrefixIdTransform
from dash import html, dcc

from utils.utils import custom_prefix_escape

from blueprints.translation.translatable_markdown_text_blueprint import translatable_markdown_text
from blueprints.translation.translatable_div_text_blueprint import translatable_div_text

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
        super().__init__(transforms = [PrefixIdTransform(prefix = id_prefix, escape=custom_prefix_escape)])
        self.layout = self._get_layout(additional_formula_content)

    def _get_layout(self, additional_formula_content: dcc.Markdown):
        return html.Div(
        [
            #### PUBLICATION ####

            html.Div(
                [
                    html.P(translatable_markdown_text("methodology_details_1").embed(self)),

                    html.P(translatable_markdown_text("methodology_details_2").embed(self)),

                    html.P(translatable_markdown_text("methodology_details_3").embed(self))
                ],
                className='container text-italic'
            ),

            #### FORMULA ####

            html.Div(
                [
                    html.H2(translatable_div_text("The_formula_header").embed(self)),

                    additional_formula_content,

                    html.Div(translatable_markdown_text("the_formula_detail").embed(self)),

                ],
                className='container formula'
            ),

            #### DEFINITIONS ####

            html.Div(
                [
                    html.Div(
                        [
                            html.H2(translatable_div_text("About_CO2e").embed(self)),

                            html.Div(translatable_markdown_text('about_co2_detail').embed(self))
                        ],
                        className='container'
                    ),

                    html.Div(
                        [
                            html.H2(translatable_div_text("What_is_a_tree-month").embed(self)),

                            html.Div(translatable_markdown_text("What_is_a_tree-month_details").embed(self)),
                        ],
                        className='container'
                    ),
                ],
                className='super-section definitions'
            ),
        ],
        className='methodology-container'
    )
