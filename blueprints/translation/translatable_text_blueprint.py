from dash import html, dcc
from dash_extensions.enrich import DashBlueprint, Output, Input, State
from blueprints.translation.translation_dicts import TRANSLATIONS_DICT

def get_translatable_text_layout(text_key: str):
    return html.Div(
        [
            dcc.Store(id='text_key', data=text_key),
            html.Div(id='text_value')
        ]
    )

def translatable_text(text_key: str):

    translatable_text_blueprint = DashBlueprint()


    ##### IMPORT THE COMPONENT LAYOUT
    #################################

    translatable_text_blueprint.layout = get_translatable_text_layout(text_key)


    ##### DEFINE ITS CALLBACKS
    ##########################

    @translatable_text_blueprint.callback(
        Output('text_value', 'children'),
        Input('language_dropdown', 'value'),
        State('text_key', 'data')
    )
    def translate_text(language_id: str, text_key: str):
        return TRANSLATIONS_DICT[language_id][text_key]
    
    return translatable_text_blueprint
