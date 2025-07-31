# Developer guide

The developer guide is intended to ease contributions to the calculator. It is designed for external collaborators or any one who wants to contribute and should help you getting started with the code base of the tool. It covers the general development principles of the calculator. If you want to get a better idea of the main code blocks, please have a look at the next pages of this documentation.

## Overview

<!-- The following snippet is written in .yml so comments are indicated by '#'  -->
::: app
    # Corresponds to the app.py header docstring
    handler: python
    options:
        # The heading to be like "###"
        heading_level: 3
        # Display it as "Code organization" and not "app.py"
        heading: "Code organization"
        # Same in the table of contents (toc)
        toc_label: "Code organization"
        # Display the docstring snippet heading
        show_root_heading: true
        # Do not include any other docstring so we filter all other docstring with the regex "!"
        filters:
            - "!"

The app modules are [described below](#in-the-calculator). They are mostly independent blocks that can be instantiated several times and then embedded into the app. Modules communicate with each other through dedicated [`dcc.Store`](#the-dccstore-components) components, most of the time at the page level.

## Dash

The python [Dash](https://dash.plotly.com/) library is a light web development and data visualization framework. If you want a detailed description of the possibilities offered by Dash, please refer to the [official documentation](https://dash.plotly.com/). We go through the basics below.

### HTML components

Dash comes with two built-in modules implementing HTML **components**: `dash.html`and `dash.dcc`. These HTML components are used to build the app layout which is then made dynamic by connecting user actions and components through [callbacks](getting_started.md#callbacks). Most of the common HTML components are implemented by Dash, but we may sometimes use additional ones coming from third-party open source libraries like [Dash Mantine Components](https://www.dash-mantine-components.com/) or [Dash Bootstrap Components](https://www.dash-bootstrap-components.com/).

Just like for regular HTML, Dash components are nested into each other to build the HTML tree of the app. Components characteristics are defined through their **properties** (roughly correspond to HTML attributes), that are passed as arguments to the python Dash objects. The following table summarizes the most important properties and the code snippet below gives an example of how to use Dash components in our code.

| Property    | Type                                    | Description                                        |
|-------------|-----------------------------------------|----------------------------------------------------|
| `children`  | str, float, components or lists of them | The component inner content.                       |
| `id`        | str                                     | The component id, must be unique in the whole app. |
| `className` | str                                     | The component class, for CSS styling.              |

Components `id` are their **unique** identifier throughout the app. The `children` property is the only positional arguments of a Dash component, it is often a list of contents (sub-components, textual or numeric content). Many components also have additional properties, depending on their nature, as shown below.

??? danger "How to embed textual content in the app?"
    Many HTML components contain text that is displayed on the user interface. However, as we implemented a translation feature, the raw text cannot be directly embedded in the app layout. If you want to create new textual content, you must follow the process described in the [translation page](../developer_guide/blueprints/translation.md) of the documentation.

``` py title='Dash components example'
from dash import html, dcc

layout = html.Div(                           # the parent container
    [                                        # the children property, as a list of sub-components
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

#### The dcc.Store components

The [`dcc.Store`](https://dash.plotly.com/dash-core-components/store) are hidden components used to share data between callbacks. They are very important because [callbacks should not modify Python global variables](https://dash.plotly.com/sharing-data-between-callbacks). In the calculator, we use them as entry-point and end-point of the different modules.

### Callbacks

[Dash callbacks](https://dash.plotly.com/basic-callbacks) are used to automate the app behaviour. They are called whenever one of the input component properties is modified, either by the user or by another callback. Formally, callbacks are regular python functions wrapped within the `@app.callback` decorator implemented by Dash. This decorator has three main kinds of arguments:

| Argument  | Description                                                                |
|-----------|----------------------------------------------------------------------------|
| Input     | A component property that triggers the callback                            |
| Output    | A component property updated by the callback                               |
| State     | A component property accessed by the callback but that does not trigger it |

Inputs, Outputs and States (see the code snippet below) are called with the pair of strings `#!python ('component_id', 'property_name')`. The `callback` decorator also accepts some keywords arguments, but we do not dive into more details here.

A single callback can have an arbitrary number of Input, Output and State but:

1. the number and the order of the Input + State must match the number and the order of the decorated function arguments.
2. the number and the order of Output must match the number and the order of the variables returned by the decorated function

??? warning "One callback per Output"
    A component property should be updated by one callback only, which is one of the biggest constraint regarding callbacks implementation. This is compulsory for Dash to correctly optimize the callbacks chain. It is actually possible to bypass it thanks to the `allow

??? note "Callback functions name"
    The function name of a callback does not matter, but choose one that tells the callbacks purpose.

Callbacks are all registered before the app is launched so it is not possible to dynamically create new callbacks while running the app. Once callbacks are registered, they are all triggered once before the app is available to the user. Based on the dependencies deduced from this first run, callbacks are optimally organized by Dash.

``` py title='A dash callback example'
from dash import Input, Output, State
from utils.handle_inputs import availableOptions_servers

@app.callback(
    Output('server_dropdown','options'), # this callback defines the server options
    [
        Input('provider_dropdown', 'value'), # -->  argument: selected_provider
        Input('server_continent_dropdown', 'value'), # --> argument: selected_continent
        Input('versioned_data','data') # backend data --> argument: data
    ],
    State('toy_component', 'toy_attribute') # --> argument: toy
)
def set_server_options(selected_provider, selected_continent, data, toy):
    """
    This callback returns the list of available servers based on:
        - the provider and the continent selected by the user,
        - the corresponding backend data, called 'data"
    """
    availableOptions = availableOptions_servers(selected_provider,selected_continent,versioned_data=data)
    listOptions = [{'label': k['Name'], 'value': k['name_unique']} for k in availableOptions + [{'Name':"other", 'name_unique':'other'}]]
    return listOptions  
```

## Data

The data used to run the calculator is stored in csv files gathered in the [GA-data repository](https://github.com/GreenAlgorithms/GA-data). It is regularly updated depending on the newly available data (cores, servers, carbon intensities...) and the new features of the app (manufacturing impacts for instance). Therefore the data is versioned so anyone can access previous versions of the data through the calculator.

From the developer side, this involves **ensuring the retro-compatibility of new features with respect to the previous data versions**. To do so, we do not modify the data itself (except when changing header names for instance). We rather replace missing data by empty structures that match the expected format.

### The GA-data git submodule

The backend data of the app is stored in a dedicated and centralized github repository: [GA-data](https://github.com/GreenAlgorithms/GA-data). This avoids duplicated data files between the different Green Algorithms tools.

To connect with the GA-data repo, we use [git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules). These are a built-in feature from git and they are well documented. They are not natively designed for data storage but they match our expectations. Notably, it allows to manage data and app versioning separately. Also, it comes with very few settings stored in the `.gitmodules` file.

#### How to use git submodule in our app?

1. If you want to pull upstream changes from the submodule remote: run `git submodule update --remote GA-data`. At this point, if commits were pushed to the remote GA-data, these are fetched and updated, but still to be staged and committed in the current repo.
2. Run `git add <submodule_changes>` and `git commit -m '...'` to commit them. At this point, any one pulling this repo into their cloned version receives the changes from the submodule.

### Some functions

<!-- The following snippet is written in .yml so comments are indicated by '#'  -->
::: app.load_data_from_version
    # Corresponds to the load_data_from_version callback in app.py
    handler: python
    options:
        # Display the full function path
        show_root_full_path: true
        # Show the heading
        show_root_heading: true
        # Do not show the source code
        show_source: false

## CSS files

[CSS](https://developer.mozilla.org/en-US/docs/Web/CSS) is used to define the style of HTML components. It allows to set the value of many components attributes like their font, margin, size or alignment. CSS relies on **selectors** to target the HTML components. There exists a wide range of selectors but the basic ones are the component type (`Div`, `Dropdown`...), their `class` and their `id` (for fine-grained styling). As a single HTML component can only have a single `id` but multiple `class`. This allows to apply many styling rules to any component with a high level of flexibility.

### Our implementation

Our style sheets are all stored in the `assets\`folder. The base rules are implemented in `0_styles_typography.css` and `1_styles_layout.css` files. Remaining files contain rules that only apply to lower zoom levels (for bigger screen sizes). These are intended to overwrite the rules defined in  `0_styles_typography.css` and `1_styles_layout.css`, adapting the layout to wider screens.

??? note "The `style` argument"
    With Dash components, one can also set the styling attributes using the `style` argument. We sometimes use it for very specific cases (typically when we want to make the style clearly displayed in the layout code), but we recommend defining most styles in the css scripts. Still, the `style`argument is very useful when one wants to make dynamic styling. One simply has to implement a callback that outputs the `style` property of the targeted component.

??? warning "Style sheets must be thought from high zoom to low zoom levels"
    Cascading style sheets are implemented zoom-wise, starting from high zoom levels. So, when creating a new component in the layout, one should first think of its style in the smaller screens, and then adding styles for lower zoom levels that replace the previous ones.

### Tips

When working on the app layout, we recommend checking the compatibility with different web browsers among the most common ones (Google Chrome, Mozilla Firefox...). We also recommend using the 'Inspect mode' of your web browser.

??? tip "Use the Inspect mode of your web browser"
    Right-click ou your web page and open the **"Inspect"** mode. This is very useful to understand which rules apply to which component and allows you to dynamically evaluate CSS modifications. It also provides **screen emulators** (for regular phones or tablets) which is particularly useful as well.

## Blueprints

The app modularization was made compulsory by the creation of the AI page. Modularization allows to create standalone and possibly duplicated code blocks without duplicating the corresponding code. In the calculator, modularization relies on the [DashBlueprint](https://www.dash-extensions.com/sections/enrich#a-dashblueprint) class from the `dash_extensions.enrich module`. The current page provides an overview of the blueprints in the calculator code, but more details regarding our implementation are given in the dedicated [documentation page](../developer_guide/blueprints/our_implementation.md).

### The DashBlueprint class

Basically, a `DashBlueprint` emulates a `dash.app` object: one must define its `layout` attribute (its HTML components) and the callbacks attached to it (the components logic). However, contrary to a `dash.app`, `DashBlueprint` instances can be embedded into each other until the parent one is finally embedded into the `dash.app` layout attribute. This gives enough flexibility to build complex apps.

??? note "Blueprints callbacks are automatically attached to the final `dash.app`"
    When embedding a blueprint into a `dash.app` object, all the callbacks that are attached it or any of its nested blueprints are automatically attached to the final `dash.app`.

When one creates several instances of the same `DashBlueprint` class (see [our implementation](../developer_guide/blueprints/our_implementation.md#implementation) for more details), this is seemingly not compatible with the ID uniqueness requirement. Actually, `DashBlueprint` instances apply an automatic **'id prefixing'** mechanism to all its components through a [PrefixIdTransform](https://www.dash-extensions.com/transforms/prefix_id_transform) object. These prefix are automatically added to the blueprint components' ID and to the Inputs, Outputs and States of its callbacks.

??? info "Alternative to `DashBlueprint`"
    When building the app modules, we also explored the [All-in-One Components](https://dash.plotly.com/all-in-one-components#community-discussion) as modular and reusable objects. We faced the following two limitations. First, it is [not possible to embed in `All-in-One Component` into another one](https://community.plotly.com/t/improving-on-all-in-one-aio-components/58897). Second, building a high number of `All-in-One Component` lowers the app performance drastically.

### In the calculator

We define 5 different modules: the calculator form, the import-export section, the metrics section, the methodology section and the translatable texts. These modules are embedded in the app at the [**page level**](#pages). As explained above, **so blueprints communicate with each other through intermediate variables stored in `dcc.Store` instances** while the inner logic of the modules is implemented in the [blueprint class directly](../developer_guide/blueprints/our_implementation.md).

``` py title='Embedding a blueprint into a toy app'
import dash
from dash import html
from blueprints.form.form_blueprint import FormBlueprint

my_app = dash.Dash()
my_form = FormBlueprint(id_prefix='main')

my_app.layout = html.Div(                # the app layout definition
    [
        html.H1('App title'),
        html.Div(
            [
                html.H2('My form'),
                my_form.embed(my_app),   # we simply and directly embed the form into the app layout
            ]
        )
    ]
)
```

## Pages

Dash provides [built-in features for multi-pages app](https://dash.plotly.com/urls#dash-pages). These allow to implement pages in dedicated files, as if they were standalone apps: one has to define the page layout and its callbacks. Just like for blueprints, these callbacks are then automatically included in the app when pages are registered. [Our implementation](../developer_guide/pages/our_implementation.md) is slightly different compared to the generic recommendations of Dash.

Actually, because of our usage of `DashBlueprint`, we also implement the pages as blueprints. The pages are registered in the app and wrapped within a layout made of the HTML/Dash components that are common to both pages.

=== "Creating a toy page in a dedicated file"

    ``` py
    from dash_extensions.enrich import DashBlueprint
    from dash import html, Input, Output

    # --- Layout definition 
    HOME_PAGE = DashBlueprint()
    HOME_PAGE.layout = html.Div(...)

    # --- Callbacks definition 
    @HOME_PAGE.callback(
        Input('component_id_A', 'component_attribute_1'),
        Output('component_id_B', 'component_attribute_1')
    )
    def a_toy_callback(arg_1):
        ...
        return toy_attr
    ```

=== "Registering a page in the app"

    ``` py
    import dash
    from dahs import html
    from pages.home import HOME_PAGE, HOME_PAGE_ID_PREFIX
    
    app = dash.Dash(__name__, use_pages=True, ...)
    HOME_PAGE.register(app, module='home', path='/', title='Green Algorithms - Classic view')

    # In the app layout definition
    app.layout = html.Div(
        [
            ... # Header layout
            dash.page_container,
            ... # Footer layout
        ]
    )

    # App callbacks
    ```

Once pages are registered in the app, the navigation between them is made easy thanks to the `page.path` attribute. It is possible to embed the navigation feature in a custom navigation bar.
