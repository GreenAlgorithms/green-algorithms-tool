# Green algorithms calculator

Introduction.

Relies on the following methodology.

## Overall description

Both calculator pages rely on the same modules:

- a form in which the user describes its computation requirements,
- a metrics sections that describes the resulting environmental impacts,
- an import/export section to share and replicate results,
- methodological and extra contents.


### Results sharing

### The CSV structure

The imported and exported csv are primarily designed for results sharing. The form reads the csv content to replicate its state but **results fields contained in the csv are not used by the app**. These are intended for users who would like to compare different csv for instance.

The csv contain three rows:

1. The first row contains the fields name (column header). The current implementation could be more robust because these headers are often directly related to the component names within the code.
2. The second row contains the fields unit. This is thought to ease csv readability for users who would open them.
3. The third row contains the fields value.

??? warning 'No thought for users manipulation'
    The imported/exported csv are designed for results sharing mostly. Even though some users may sometimes aggregate different csv to compare their results, the csv mechanism is not designed for it, so one should not try to deal with all possible use cases.

Note that the csv headers are radically different between a csv exported from the Home page and the AI page. They are not compatible with each other.