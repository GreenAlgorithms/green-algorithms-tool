# Our blueprints

## Implementation

Each module <blueprint> is implemented in a class inheriting from the [DashBlueprint](https://www.dash-extensions.com/sections/enrich#a-dashblueprint) class. This is a **satisfying tradeoff** between code readability and functionality. Actually, blueprints do not really match the 'class-oriented development' patterns as callbacks cannot be implemented as methods but wrapping our blueprints in classes allows to:

1. Instantiate a blueprint as many times as required, with no duplicated code.
2. Respect a standardized pattern for implementation.
3. Customize a blueprint by implementing dedicated methods and calling them at instantiation.

The following code block illustrates our blueprint abstraction:

``` py title='Our blueprint "abstract" class'
from dash import html, dcc
from dash_extensions.enrich import DashBlueprint, Output, Input, State, PrefixIdTransform

class MyBlueprint(DashBlueprint):
    
    '''
    Blueprint documentation
    '''

    def __init__(self, id_prefix: str, customizing_arg):
        super().__init__(transforms = [PrefixIdTransform(prefix = id_prefix, escape = custom_prefix_escape)])
        ... # any customization 
        self.layout = self._get_layout(customizing_arg, ...)
        self._define_callbacks()

    def _get_layout(self, ...):
        ''' Defines the blueprint layout. Translatable texts are embedded here '''
        return html.Div(...)
    
    def _define_callbacks(self, ...):
        ''' List all the callbacks as inner functions of this method '''
        @self.callback(
            Output('comp_A', 'attr_A'),
            Input('comp_B', 'attr_B'),
        )
        def callback_1(arg_B): ...
        ...
```

??? danger "The `escape` must be defined in the `PrefixIdTransform` arguments"
    This is compulsory to let the [translatable texts](../../developer_guide/blueprints/translation.md) embedded in this blueprint work properly.

When we define the layout of our blueprints, we still need to access the `DashBlueprint` instance itself somehow because "translatable" texts (that are part of the layout) are wrapped within blueprints as well. Like any other blueprints, these translatable texts must be embedded into an `dash.app` or a `DashBlueprint` instance.