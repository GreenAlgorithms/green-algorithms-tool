# The AI page

<!-- The following snippet is written in .yml so comments are indicated by '#'  -->
::: pages.ai
    # Corresponds to the ai.py header docstring
    handler: python
    options:
        # The heading to be like "###"
        heading_level: 3
        # Display it as "Code organization"
        heading: "Overview"
        # Same in the table of contents (toc)
        toc_label: "Overview"
        # Display the docstring snippet heading
        show_root_heading: true
        # Do not include any other docstring so we filter all other docstring with the regex "!"
        filters:
            - "!"