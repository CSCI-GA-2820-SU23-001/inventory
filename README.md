# Inventory Microservice

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![Build Status](https://github.com/CSCI-GA-2820-SU23-001/inventory/actions/workflows/tdd.yml/badge.svg)](https://github.com/CSCI-GA-2820-SU23-001/inventory/actions)

## Overview

The inventory service keeps track of how many of each product we have in our warehouse. It references a product id and the quantity on hand. This service also tracks restock levels and the condition of the item (i.e., new, open box, used) as an enumeration. Restock levels will help you know when to order more products. Each item has a "last updated on" field that tells the user when this item was added/updated/etc.

The user also has the ability to enable/disable updates of a given product ID and condition. This can prevent us from having too many copies of an item in our warehouse

## HomePage

## Documentation

Please click on the "documentation" button on the homepage to bring up the Swagger Docs UI. The Swagger Docs UI explains how to call our API

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

.github/                   - Folder for CI
└── ISSUE_TEMPLATE         - Templates for Zenhub items
    ├── bug_report.md      - Template for bug reports
    ├── user-story.md      - Template for user stories
└── workflows              - Folder for workflows
    ├── bdd.yml            - Steps that auto-run BDD tests
    ├── tdd.yml            - Steps that auto-run TDD tests

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## Running the service

The project uses *honcho* which gets it's commands from the `Procfile`. To start the service simply use:

```shell
 honcho start
```

You should be able to reach the service at: `http://localhost:8000`. The port that is used is controlled by an environment variable defined in the `.flaskenv` file which Flask uses to load it's configuration from the environment by default.

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
