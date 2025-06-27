# Developer guide

The developper guide is intended to ease contributions to the calculator. It is designed for external collaborators or any one who wants to contribute and should help you getting started with the code base of the tool. It covers the general development principles of the calculator. If you want to get a better idea of the main code blocks, please have a look at the next pages of this documentation.

<!-- The following snippet is written in .yml so comments are indicated by '#'  -->
::: app
    # Corresponds to the app.py header docstring
    handler: python
    options:
        # We want to display it as "Code organization" and not "app.py"
        heading: "Code organization"
        # Same in the table of contents (toc)
        toc_label: "Code organization"
        # We want to display the docstring snippet heading
        show_root_heading: true
        # We do not want to include any other docstring so we filter all other docstrings with the regex "!"
        filters:
            - "!"

## Dash

The python [Dash](https://dash.plotly.com/) library is a light web development and data visualization framework. If you want a detailed description of the possibilities offered by Dash, please refer to the [official documentation](https://dash.plotly.com/).

### HTML components

Dash comes with two built-in modules implementing HTML **components**: `dash.html`and `dash.dcc`. These HTML components are used to build the app layout which is then made dynamic by connecting user actions and components through [callbacks](getting_started.md#callbacks). Most of the common HTML components are implemented by Dash, but we may sometimes use additional ones coming from third-party open source libraries like [Dash Mantine Components](https://www.dash-mantine-components.com/) or [Dash Bootstrap Components](https://www.dash-bootstrap-components.com/).

Just like for regular HTML, Dash components are nested into each other to build the HTML tree of the app. Components charcateristics are defined trhough their **properties** (roughly correspond to HTML attributes), that are passed as arguments to the python Dash objects. The following table summarizes the most important properties and the code snippet below gives an example of how to use Dash components in our code.

| Property    | Type                                    | Description                                        |
|-------------|-----------------------------------------|----------------------------------------------------|
| `children`  | str, float, components or lists of them | The component inner content.                       |
| `id`        | str                                     | The component id, must be unique in the whole app. |
| `className` | str                                     | The component class, for CSS styling.              |

Components `id` are their **unique** identifier throughout the app. The `children` property is the only positional arguments of a Dash component, it is often a list of contents (subcomponents, textual or numeric content). Many components also have additional properties, depending on their nature, as shown below.

``` py title='Dash components usage'
from dash import html, dcc

layout = html.Div(                           # the parent container
    [                                        # the children property, as a list of subcomponents
        html.Label("Number of cores used"),

        dcc.Input(
            type='number',
            id='numberCPUs_input',           
            min=0,                           # additional property for Input components
        ),
    ],
    className='form-row short-input'         # two different class names
)
```

### Callbacks

Dash [callbacks](https://dash.plotly.com/basic-callbacks) are used to automate the app behaviour. They are called whenever one of the input component properties is modified, either by the user or by another callback. Formally, callbacks are regular python functions wrapped within the `@app.callback` decorator implemented by Dash. This decorator has three main kinds of arguments:

| Argument  | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| Input     | A component property that triggers the callback                            |
| Output    | A component property updated by the callback                               |
| State     | A component property accessed by the callback but that does not trigger it |

Inputs, Outputs and States (see the code snippet below) are called with the pair of strings `#!python ('component_id', 'property_name')`. The `callback` decorator also accepts some keywords argurments, but we do not dive into more details here.

A single callback can have an arbitrary number of Input, Output and State but:

1. the number and the order of the Input + State must match the number and the order of the decorared function arguments.
2. the number and the order of Output must match the number and the order of the variables returned by the decorated function

Callbacks are all registered before the app is launched so it is not possible to dynamically create new callbacks while running the app. Once callbacks are registered, they are all triggered once before the app is available to the user. Based on the dependencies deduced from this first run, callbacks are optimally organized by Dash. 

``` py title='Dash components usage'
@app.callback(
    Output('server_dropdown','options'), # this call
    [
        Input('provider_dropdown', 'value'), # --> selected_provider
        Input('server_continent_dropdown', 'value'), # --> selected_continent
        Input('versioned_data','data') #backend data --> data
    ]
)
def set_server_options(selected_provider, selected_continent, data):
    """
    This callback returns the list of available servers based on:
        - the provider and the contient selected by the user,
        - the corresponding backend data, called 'data"
    """
    availableOptions = availableOptions_servers(selected_provider,selected_continent,versioned_data=data)
    listOptions = [{'label': k['Name'], 'value': k['name_unique']} for k in availableOptions + [{'Name':"other", 'name_unique':'other'}]]
    return listOptions  
```

!!! warning
    A component property should be updated by one callback only, which is one of the biggest constraint regarding callbacks implementation. This is compulsory for Dash to correctly optimize the callbacks chain. It is actually possible to bypass it thanks to the `allow

!!! info
    The function name of a callback does not matter, but choose one that tells the callbacks purpose.

## CSS files

[CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) is used to define the style of HTML components. It allows to set the value of many components attributes like their font, margin, size or alignement. CSS relies on **selectors** to target the HTML components. There exists a wide range of selectors but the basic ones are the component type (`Div`, `Dropdown`...), their `class` and their `id` (for fine-grained styling). As a single HTML component can only have a single `id` but multiple `class`. This allows to apply many styling rules to any component with a high level of flexibility.

### Our implementation

- our files
- per zoom
- start from high zoom level to wide screens
- use the Inspect founctionnality of the web browser


## Pages

## Blueprints

The modularization relies on the [DashBlueprint](https://www.dash-extensions.com/sections/enrich#a-dashblueprint)
class from the `dash_extensions.enrich module`.

Each module <module> is implemented in a function defined in blueprints/<module>/<module>_blueprint.py.
These modules are inserted in the app at the page level (see pages/home.py and pages/ai.py).
They communicate with each other through intermediate variables stored in dcc.Store instances.
The callbacks between these intermediate variables are implemented at the page level too.

To ensure the uniqueness of each component's id, DashBlueprints rely on id prefix.
These prefix are automatically added to the blueprint components' id and 
to the Inputs, Outputs and States of its callbacks. Though, for outer callbacks,
the prefix needs to be manually added to the Inputs, Outputs and State ids.

The only app level variable is the backend data "versioned_data" used to run the calculator.
The "versioned_data" is loaded when the app is launched and then triggers all the callbacks 
that require backend data (cores, server, location, carbon intensity and "equivalent" callbacks).
As the name suggests, this data is versioned to ensure the results replicability accross the
different versions of the app data.

Because of our usage of DashBlueprint, we also implemented the pages as blueprints.
The pages are registered in the app and wrapped within a layout made of the
HTML/Dash components that are common to both pages.

This script generates and runs the app.