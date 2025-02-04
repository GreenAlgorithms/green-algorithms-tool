'''
Implements the translatable text blueprint for regular Div containers.

This blueprint should be used to wrap all the textual contents of the app.
It comes with a dcc.Store containing the translation key corresponding to the 
target textual content. This key must be given when the blueprint is created
as it also serves as id-prefix for the component id. 
'''

from dash import html, dcc
from dash_extensions.enrich import DashBlueprint, Output, Input, State, PrefixIdTransform
from blueprints.translation.translation_dicts import TRANSLATIONS_DICT
from utils.utils import custom_prefix_escape

def get_translatable_div_text_layout(text_key: str):
    return html.Div(
        [
            dcc.Store(id='text_key', data=text_key),
            html.Div(id='text_value')
        ],
        style={'display': 'inline-block'}
    )

def translatable_div_text(text_key: str):

    translatable_text_blueprint = DashBlueprint(        
        transforms=[
            PrefixIdTransform(
                prefix=text_key,
                escape=custom_prefix_escape,
            )
        ]
    )


    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    translatable_text_blueprint.layout = get_translatable_div_text_layout(text_key)


    ##### DEFINE ITS CALLBACKS
    ##########################

    @translatable_text_blueprint.callback(
        Output('text_value', 'children'),
        Input('language_dropdown', 'value'),
        State('text_key', 'data')
    )
    def translate_text(language_id: str, text_key: str):
        """
        Retrieve the right translation from the translation dict.
        The translation dict is built as follows:
        {
            'text_key_1': {
                'language_1': 'translation_key1_lang1',
                'language_2': 'translation_key1_lang2',
            },

            'text_key_2': {
                'language_1': 'translation_key2_lang1',
                'language_2': 'translation_key2_lang2',
            },
            ...
        }

        Args:
            text_key (str): the primary key of the translation dict.
            language_id (str): the language key, secondary key of the dictionnary.

        Returns:
            _type_: _description_
        """
        return TRANSLATIONS_DICT[text_key][language_id]
    
    return translatable_text_blueprint
