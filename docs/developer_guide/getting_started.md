# Developer guide

The developper guide is intended to ease contributions to the calculator. It is designed for external collaborators or any one who wants to contribute and should help you getting started with the code base of the tool. It covers the general development principles of the calculator.If you want to get a better idea of the main code blocks, please have a look at the next pages of this documentation.

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

Just like for regular HTML, Dash components are nested into each other to build the HTML tree of the app. Components charcateristics are defined trhough their **properties**, that are passed as arguments to the python Dash objects. The following table summarizes the most important properties and the code snippet below gives an example of how to use Dash components in our code.

| Property    | Type                                    | Description                                        |
|-------------|-----------------------------------------|----------------------------------------------------|
| `children`  | str, float, components or lists of them | The component inner content.                       |
| `id`        | str                                     | The component id, must be unique in the whole app. |
| `className` | str                                     | The component class, for CSS styling.              |

Components `id` are their **unique** identifier throughout the app. The `children` property is the only positional arguments of a Dash component, it is often a list of contents (subcomponents, textual or numeric content). Many components also have additional properties, depending on their nature, as shown below.

``` py title='Dash components usage'
from dash import html, dcc

layout = html.Div(                                    # the parent container
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

Dash [callbacks](https://dash.plotly.com/basic-callbacks) are used to automate the app behaviour. They are called whenever one of the input
component properties is modified, either by the user or by another callback. Formally, callbacks are regular python functions wrapped within 
the `@app.callback` decorator implemented by Dash. This decorator has three main kinds of arguments:

| Argument                           | Description                                                              |
|------------------------------------|--------------------------------------------------------------------------|
| Input('component_id', 'property')  | A component property that triggers the callback                          |
| Output('component_id', 'property') | A component property updated by the callback                             |
| State('component_id', 'property')  | A component property accessed by the callback but it does not trigger it |

A single callback can have an arbitrary number of the above but:

- **the number of Input + State must match the number of arguments of the decorared function**
- **the number of Output must match the number of variable returned by the decorated function**

!!! warning
    A component property should be updated by one callback only, which is one of the biggest constraint regarding
    callbacks implementation. It is actually possible to bypass it thanks to the `allow


!!! info
    The function name of a callback does not matter, but choose one that tells the callbacks purpose.



## CSS files

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