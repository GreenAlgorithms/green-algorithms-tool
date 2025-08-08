# The form blueprint

## The FormBlueprint class

::: blueprints.form.form_blueprint.FormBlueprint
    handler: python
    options:
        show_source: false

## Form values assignment

The form values assignment is the first step after app loading because it encompasses form initialization. The corresponding callbacks are triggered directly after the url is entered (```py Input('url_content', 'search')```) and they trigger the remaining app functionalities. Thus it is a very important code block.

Values assignment is among the most tedious parts of our form implementation because each single callback that deals with it must distinguish between default value assignment and assignment from a csv imported by the user. It relies on two different mechanisms, depending on wether a component attribute is already the output of another callback. If an attribute is not an output, the assignment is implemented by the `filling_form` callback. Otherwise, each form attribute has its dedicated initialization callback.
