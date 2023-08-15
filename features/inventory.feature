Feature: The inventory service back-end
    As a manager of our warehouse
    I need a RESTful catalog service
    So that I can keep track of all the inventory in our warehouse

Background:
    Given the following inventory
        | product_id | condition | quantity | restock_level  | last_updated_on   | can_update |
        | 1          | NEW       | 50       | 10             | 2019-11-18        | ENABLED |
        | 2          | OPEN_BOX  | 70       | 15             | 2020-08-13        | ENABLED |
        | 3          | USED      | 90       | 110            | 2021-04-01        | DISABLED |
        | 4          | NEW       | 100      | 20             | 2018-06-04        | ENABLED |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Inventory Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create an Inventory
    When I visit the "Home Page"
    And I set the "product_id" to "5"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "40"
    And I set the "restock_level" to "65"
    And I select "ENABLED" in the "can_update" dropdown
    And I press the "Create" button
    Then I should see the message "Successfully created product ID 5"
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW" in the results
    And I should see "2 OPEN_BOX" in the results
    And I should see "3 USED" in the results
    And I should see "4 NEW" in the results
    And I should see "5 NEW" in the results

Scenario: Retrieve an Inventory
    When I visit the "Home Page"
    And I set the "product_id" in the retrieve/delete form to "1"
    And I select "NEW" in the "condition" in the retrieve/delete form dropdown
    And I press the "Retrieve" button
    Then I should see the message "Successfully retrieved info of product ID 1"
    And I should see "1" in the "product_id" field
    And I should see "NEW" in the "condition" dropdown
    And I should see "50" in the "quantity" field
    And I should see "10" in the "restock_level" field
    And I should see "ENABLED" in the "can_update" dropdown

Scenario: Update an Inventory
    When I visit the "Home Page"
    And I set the "product_id" to "1"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "510"
    And I set the "restock_level" to "10"
    And I press the "Update" button
    Then I should see the message "Successfully updated product ID 1"
    When I set the "product_id" to "3"
    And I select "USED" in the "condition" dropdown
    And I set the "quantity" to "700"
    And I set the "restock_level" to "110"
    And I press the "Update" button
    Then I should not see the message "Successfully updated product ID 3"
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW 510 10" in the results
    And I should see "2 OPEN_BOX 70 15" in the results
    And I should see "3 USED 90 110" in the results
    And I should see "4 NEW 100 20 " in the results

Scenario: Delete an Inventory
    When I visit the "Home Page"
    And I set the "product_id" in the retrieve/delete form to "1"
    And I select "NEW" in the "condition" in the retrieve/delete form dropdown
    And I press the "Delete" button
    Then I should see the message "Successfully deleted product ID 1"
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "2 OPEN_BOX" in the results
    And I should see "3 USED" in the results
    And I should see "4 NEW" in the results
    But I should not see "1 NEW" in the results

Scenario: List all inventory
    When I visit the "Home Page"
    And I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW" in the results
    And I should see "2 OPEN_BOX" in the results
    And I should see "3 USED" in the results
    And I should see "4 NEW" in the results

Scenario: List only new inventory
    When I visit the "Home Page"
    And I press the "Search" new button
    Then I should see the message "Successfully returned a list of all NEW items"
    And I should see "1 NEW" in the results
    And I should see "4 NEW" in the results
    But I should not see "2 OPEN_BOX" in the results
    And I should not see "3 USED" in the results

Scenario: List only used inventory
    When I visit the "Home Page"
    And I press the "Search" used button
    Then I should see the message "Successfully returned a list of all USED items"
    And I should see "3 USED" in the results
    But I should not see "1 NEW" in the results
    And I should not see "2 OPEN_BOX" in the results
    And I should not see "4 NEW" in the results

Scenario: List only open box inventory
    When I visit the "Home Page"
    And I press the "Search" open box button
    Then I should see the message "Successfully returned a list of all OPEN_BOX items"
    And I should see "2 OPEN_BOX" in the results
    But I should not see "1 NEW" in the results
    And I should not see "3 USED" in the results
    And I should not see "4 NEW" in the results

Scenario: List only by restock
    When I visit the "Home Page"
    And I press the "Search" restock button
    Then I should see the message "Successfully returned a list of items that need to be restocked"
    And I should see "3 USED" in the results
    But I should not see "1 NEW" in the results
    And I should not see "2 OPEN_BOX" in the results
    And I should not see "4 NEW" in the results

Scenario: Test the enable/disable item updates action
    When I visit the "Home Page"
    And I set the "product_id" in the enable/disable item updates form to "1"
    And I select "NEW" in the "condition" in the enable/disable item updates form dropdown
    And I press the "Disable-Update" button
    Then I should see the message "Disabled product ID 1 updates"
    When I set the "product_id" to "1"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "9000"
    And I set the "restock_level" to "8000"
    And I press the "Update" button
    Then I should not see the message "Successfully updated product ID 1"
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW 50 10" in the results
    And I should see "2 OPEN_BOX 70 15" in the results
    And I should see "3 USED 90 110" in the results
    And I should see "4 NEW 100 20 " in the results
    When I set the "product_id" in the enable/disable item updates form to "1"
    And I select "NEW" in the "condition" in the enable/disable item updates form dropdown
    And I press the "Enable-Update" button
    Then I should see the message "Enabled product ID 1 updates"
    When I set the "product_id" to "1"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "9000"
    And I set the "restock_level" to "8000"
    And I press the "Update" button
    Then I should see the message "Successfully updated product ID 1"
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW 9000 8000" in the results
    And I should see "2 OPEN_BOX 70 15" in the results
    And I should see "3 USED 90 110" in the results
    And I should see "4 NEW 100 20 " in the results

Scenario: Test to create inventory which exists in database
    When I visit the "Home Page"
    And I set the "product_id" to "1"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "200"
    And I set the "restock_level" to "20"
    And I select "ENABLED" in the "can_update" dropdown
    And I press the "Create" button
    Then I should not see the message "Successfully created product ID 1"
    And I should see the message "Inventory with id 1 and condition NEW already exists"
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW" in the results
    And I should see "2 OPEN_BOX" in the results
    And I should see "3 USED" in the results
    And I should see "4 NEW" in the results

Scenario: Test to update a record with negative quantity value
    When I visit the "Home Page"
    And I set the "product_id" to "1"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "-100"
    And I set the "restock_level" to "30"
    And I press the "Update" button
    Then I should not see the message "Successfully updated product ID 1"
    And I should see the message "Quantity is given as -100. It cannot be negative."
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW 50 10" in the results
    And I should not see "1 NEW -100 30" in the results
    And I should see "2 OPEN_BOX 70 15" in the results
    And I should see "3 USED 90 110" in the results
    And I should see "4 NEW 100 20 " in the results

Scenario: Test to update a record with negative restock value
    When I visit the "Home Page"
    And I set the "product_id" to "1"
    And I select "NEW" in the "condition" dropdown
    And I set the "quantity" to "100"
    And I set the "restock_level" to "-30"
    And I press the "Update" button
    Then I should not see the message "Successfully updated product ID 1"
    And I should see the message "Restock is given as -30. It cannot be negative."
    When I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW 50 10" in the results
    And I should not see "1 NEW 100 -30" in the results
    And I should see "2 OPEN_BOX 70 15" in the results
    And I should see "3 USED 90 110" in the results
    And I should see "4 NEW 100 20 " in the results

Scenario: Retrieve an Inventory that does not exist
    When I visit the "Home Page"
    And I press the "Search" all button
    Then I should see the message "Successfully returned a list of all the items"
    And I should see "1 NEW" in the results
    And I should see "2 OPEN_BOX" in the results
    And I should see "3 USED" in the results
    And I should see "4 NEW" in the results
    And I should not see "100 NEW" in the results
    When I visit the "Home Page"
    And I set the "product_id" in the retrieve/delete form to "100"
    And I select "NEW" in the "condition" in the retrieve/delete form dropdown
    And I press the "Retrieve" button
    Then I should not see the message "Successfully retrieved info of product ID 100"
    And I should see the message "Inventory with id '100' and condition 'NEW' was not found."