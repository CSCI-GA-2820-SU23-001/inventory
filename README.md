# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Inventory Service APIs

### Inventory Operations

| Endpoint | Methods | Rule
| -------------------------| ------- | --------------------------
| create_inventory| POST| ```/inventory```
| get_inventory | GET | ```/inventory```
| get_specific_inventory| GET | ```/inventory/<int:product_id>/<condition>```
| get_inventory_by_criteria| GET | ```/inventory/<_criteria>```
| update_inventory | PUT| ```/inventory/<int:product_id>/<string:condition>```
| delete_an_inventory| DELETE  | ```/inventory/<int:product_id>/<string:condition>```
| list_inventory | GET| ```/inventory```

## APIs Usage

### Create an Inventory

URL : `http://127.0.0.1:8000/inventory`

Method : POST

Auth required : No

Permissions required : No

Create an inventory using a JSON file that includes the product_id, condition, quantity, and restock level.

Example:

Request Body (JSON)

```JSON

{
  "product_id": 301,
  "condition": "NEW",
  "quantity": 10,
  "restock_level": 5
}


```

Success Response : `HTTP_201_CREATED`

```JSON

{
  "condition": "NEW",
  "last_updated_on": "Mon, 17 Jul 2023 17:26:07 GMT",
  "product_id": 301,
  "quantity": 10,
  "restock_level": 5
}
```

### Read an Inventory

URL : `http://127.0.0.1:8000/inventory/<int:product_id>/<condition>`

Method : GET

Auth required : No

Permissions required : No

Read all information of an inventory with given id and condition

Example:

Success Response : `HTTP_200_OK`

```JSON

{
  "condition": "NEW",
  "last_updated_on": "Mon, 17 Jul 2023 17:26:07 GMT",
  "product_id": 301,
  "quantity": 10,
  "restock_level": 5
}

```

Failure Response : `HTTP_404_NOT_FOUND`

```JSON

{
  "error": "Not Found",
  "message": "404 Not Found: Inventory with id '301' and condition 'USED' was not found.",
  "status": 404
}

```

### Update an Inventory

URL : `http://127.0.0.1:8000/inventory/<int:product_id>/<condition>`

Method : PUT

Auth required : No

Permissions required : No

Updates an inventory with id provided in the URL according to the updated fields provided in the body

Example:

Request Body (JSON)

```JSON

{
  "quantity": 25,
  "restock_level": 5
}

```

Success Response : `HTTP_200_OK`

```JSON

{
  "condition": "NEW",
  "last_updated_on": "Mon, 17 Jul 2023 17:32:01 GMT",
  "product_id": 301,
  "quantity": 25,
  "restock_level": 5
}

```

Failure Response : `HTTP_404_NOT_FOUND`

```JSON

{
  "error": "Not Found",
  "message": "404 Not Found: Inventory not found for product with ID 10 and condition NEW",
  "status": 404
}

```

### Delete an Inventory

URL : `http://127.0.0.1:8000/inventory/<int:product_id>/<condition>`

Method : DELETE

Auth required : No

Permissions required : No

Deletes an inventory with id and condition

Example:

Success Response : `204 NO CONTENT`

### List All Inventories

URL : `http://127.0.0.1:8000/inventory`

Method: GET

Auth required : No

Permissions required : No

List all inventory records

Example:

Success Response : `HTTP_200_OK`

```JSON

[
  {
    "condition": "NEW",
    "last_updated_on": "2023-07-17 17:26:07.460762",
    "product_id": 301,
    "quantity": 10,
    "restock_level": 5
  },
  {
    "condition": "NEW",
    "last_updated_on": "2023-07-17 02:36:08.305311",
    "product_id": 90,
    "quantity": 90,
    "restock_level": 90
  }
]

```

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
