# Our blueprints

## Why do we use blueprints

## Implementation

Each module <blueprint> is implemented in a class inheriting from the [DashBlueprint](https://www.dash-extensions.com/sections/enrich#a-dashblueprint) class. Actually, our blueprints do not really match the 'class-oriented development' patterns as callbacks cannot be implemented as methods but it is the solution we chose to make it compatible with the translation feature.

!!! warning "ID prefix must be manually added for outer callbacks"
    The callbacks that benefit from automatic ID prefixing are only those that are directly attached to the `DashBlueprint` instance.

!!! warning
    When we define the layout of our blueprints, we still need to access the `DashBlueprint` instance itself somehow because translatabl" texts (that are part of the layout) are wrapped within blueprints as well. Like any other blueprints, these translatable texts must be embedded into an `dash.app` or a `DashBlueprint` instance.

## Other section
