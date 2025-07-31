# The translation

## Overview

Translation relies on blueprints that are embedded instead of raw textual content. This is very useful because it allows to implement **a single callback for the whole translation mechanism**. This callback is automatically duplicated any time a new "translatable text" is embedded in the app.

As **an attribute can be the `Output` of one callback only**, when translation relates to attributes that already depend on an existing callback (typically the options of a dropdown that are defined dynamically), the translation must be inserted in this callback directly. Below [code snippet](#integration-in-the-code) gives an example of this kind of callbacks in the code.

## The translation blueprint

Actually, there exist two translation blueprints that follow the exact same structure. One is designed for regular `html.Div` textual contents and the second one is for the `dcc.Markdown` texts, *i.e* texts that rely on markdown formatting. **Markdown formatting must be used for bold fonts, formulas or clickable links.**

Note that the translatable text blueprints do not obey the abstract class structure described in the [introduction on our blueprints](../../developer_guide/blueprints/our_implementation.md). They are implemented with **functions** because they do not rely on any other blueprints to be embedded in their layout.

### Implementation

We only show the `translatable_div_text_blueprint` blueprint but note that its markdown version follows the same structure.

::: blueprints.translation.translatable_div_text_blueprint
    handler: python

## Integration in the code

Translatable text blueprints must be embedded in the layout of the other blueprints or dash objects. The following code snippet shows the two ways one may follow to add translatable texts in the app:

=== "Translatable texts embedded in the layout"

    ``` py
    from blueprints.translation.translatable_div_text_blueprint import translatable_div_text

    class MyBlueprint(DashBlueprint):
        
        def __init__(...):
            ...

        def _get_layout(self, ):
            ''' Defines the blueprint layout. Translatable texts are embedded here '''
            return html.Div(
                    [
                        html.H2(translatable_div_text("title").embed(self)),   # a first translatable text with key 'title'

                        html.Div(
                            [
                                html.Label(translatable_div_text("Input_data_time_span_label").embed(self)),

                                dcc.Input(type='number', id='input_data_time_scope_input'),
                            ],
                        )
                    ]
            )
    ```

=== "Translate text from an existing callback"

    ``` py
    from blueprints.translation.translation_dicts import TRANSLATIONS_DICT

    @self.callback(
        [
            Output('compo_A', 'options'),
        ],
        Input('language_dropdown', 'value'),
        Input('new_choice', 'value'),
    )
    def update_and_translate_options(language_id: str, new_value: int):
        """
        Args:
            language_id (str):  the language identifier for translation purpose
            new_value (str):  new value selected by the user
        """
        new_option_list = get_options(new_value)
        translated_options = [TRANSLATIONS_DICT[option_label][language_id] for option_label in new_option_list]

    ```

## The translation dictionary

All translations are stored in a dedicated dictionary with the following structure:

``` py  title="The translation dictionary structure"
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
```