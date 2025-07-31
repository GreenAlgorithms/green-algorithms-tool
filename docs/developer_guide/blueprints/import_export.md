# The import-export blueprint

## The ImportExportBlueprint class

::: blueprints.import_export.import_export_blueprint.ImportExportBlueprint
    handler: python
    options:
        show_source: false

## The CSV

### The CSV structure

The imported and exported csv are primarily designed for results sharing. The form reads the csv content to replicate its state but **results fields contained in the csv are not used by the app**. These are intended for users who would like to compare different csv for instance.

The csv contain three rows:

1. The first row contains the fields name (column header). The current implementation could be more robust because these headers are often directly related to the component names within the code.
2. The second row contains the fields unit. This is thought to ease csv readability for users who would open them.
3. The third row contains the fields value.

??? warning "Not thought for users manipulation"
    The imported/exported csv are designed for results sharing mostly. Even though some users may sometimes aggregate different csv to compare their results, the csv mechanism is not designed for it, so one should not try to deal with all possible use cases.

Note that the csv headers are radically different between a csv exported from the Home page and the AI page. They are not compatible with each other.

### The CSV parsing

This process should extract all valid entries from the csv and raise a warning when errors are detected. The csv are read through different utils functions:

::: utils.handle_inputs.open_input_csv_and_comment
    handler: python

::: utils.handle_inputs.read_base_form_inputs_from_csv
    handler: python

::: utils.handle_inputs.validate_main_form_inputs
    handler: python

::: utils.utils.write_error_message
    handler: python