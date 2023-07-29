$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#inventory_product_id").val(res.product_id);
        $("#inventory_condition").val(res.condition);
        $("#inventory_quantity").val(res.quantity);
        $("#inventory_restock_level").val(res.restock_level);
        $("#inventory_last_updated_on").val(res.last_updated_on);
        $("#inventory_can_update").val(res.can_update);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#inventory_product_id").val("");
        $("#inventory_condition").val("");
        $("#inventory_quantity").val("");
        $("#inventory_restock_level").val("");
        $("#inventory_last_updated_on").val("");
        $("#inventory_can_update").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Inventory object
    // ****************************************

    $("#create-btn").click(function () {

        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();
        let quantity = parseInt($("#inventory_quantity").val(), 10);
        let restock_level = parseInt($("#inventory_restock_level").val(), 10);
        let last_updated_on = $("#inventory_last_updated_on").val();
        let can_update = $("#inventory_can_update").val();

        let data = {
            "product_id": Math.floor(Math.random() * 1000),
            "condition": condition,
            "quantity": quantity,
            "restock_level": restock_level,
            "last_updated_on": last_updated_on,
            "can_update": can_update
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/inventory",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update an Inventory object
    // ****************************************

    $("#update-btn").click(function () {

        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();
        let quantity = parseInt($("#inventory_quantity").val(), 10);
        let restock_level = parseInt($("#inventory_restock_level").val(), 10);
        let last_updated_on = $("#inventory_last_updated_on").val();
        let can_update = $("#inventory_can_update").val();

        let data = {
            "product_id": product_id,
            "condition": condition,
            "quantity": quantity,
            "restock_level": restock_level,
            "last_updated_on": last_updated_on,
            "can_update": can_update
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/inventory/${product_id}/${condition}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Inventory object
    // ****************************************

    $("#retrieve-btn").click(function () {

        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/${product_id}/${condition}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Inventory object
    // ****************************************

    $("#delete-btn").click(function () {

        let product_id = $("#inventory_product_id").val();
        let condition = $("#inventory_condition").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/inventory/${product_id}/${condition}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Inventory has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#clear-btn").click(function () {
        $("#inventory_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Build a list of items that need to be restocked
    // ****************************************

    $("#search-btn-restock").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/RESTOCK`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())            
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Product_ID</th>'
            table += '<th class="col-md-2">Condition</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Restock_Level</th>'
            table += '<th class="col-md-2">Last_Updated_On</th>'
            table += '<th class="col-md-2">Can_Update</th>'
            table += '</tr></thead><tbody>'
            let firstInventory = "";
            for(let i = 0; i < res.length; i++) {
                let thisInventory = res[i];
                table +=  `<tr id="row_${i}"><td>${thisInventory.product_id}</td><td>${thisInventory.condition}</td><td>${thisInventory.quantity}</td><td>${thisInventory.restock_level}</td><td>${thisInventory.last_updated_on}</td><td>${thisInventory.can_update}</td></tr>`;
                if (i == 0) {
                    firstInventory = thisInventory;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Build a list of all items
    // ****************************************

    $("#search-btn-all").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())            
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Product_ID</th>'
            table += '<th class="col-md-2">Condition</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Restock_Level</th>'
            table += '<th class="col-md-2">Last_Updated_On</th>'
            table += '<th class="col-md-2">Can_Update</th>'
            table += '</tr></thead><tbody>'
            let firstInventory = "";
            for(let i = 0; i < res.length; i++) {
                let thisInventory = res[i];
                table +=  `<tr id="row_${i}"><td>${thisInventory.product_id}</td><td>${thisInventory.condition}</td><td>${thisInventory.quantity}</td><td>${thisInventory.restock_level}</td><td>${thisInventory.last_updated_on}</td><td>${thisInventory.can_update}</td></tr>`;
                if (i == 0) {
                    firstInventory = thisInventory;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Build a list of all new items
    // ****************************************

    $("#search-btn-new").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/NEW`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())            
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Product_ID</th>'
            table += '<th class="col-md-2">Condition</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Restock_Level</th>'
            table += '<th class="col-md-2">Last_Updated_On</th>'
            table += '<th class="col-md-2">Can_Update</th>'
            table += '</tr></thead><tbody>'
            let firstInventory = "";
            for(let i = 0; i < res.length; i++) {
                let thisInventory = res[i];
                table +=  `<tr id="row_${i}"><td>${thisInventory.product_id}</td><td>${thisInventory.condition}</td><td>${thisInventory.quantity}</td><td>${thisInventory.restock_level}</td><td>${thisInventory.last_updated_on}</td><td>${thisInventory.can_update}</td></tr>`;
                if (i == 0) {
                    firstInventory = thisInventory;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Build a list of all open-box items
    // ****************************************

    $("#search-btn-open-box").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/OPEN_BOX`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())            
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Product_ID</th>'
            table += '<th class="col-md-2">Condition</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Restock_Level</th>'
            table += '<th class="col-md-2">Last_Updated_On</th>'
            table += '<th class="col-md-2">Can_Update</th>'
            table += '</tr></thead><tbody>'
            let firstInventory = "";
            for(let i = 0; i < res.length; i++) {
                let thisInventory = res[i];
                table +=  `<tr id="row_${i}"><td>${thisInventory.product_id}</td><td>${thisInventory.condition}</td><td>${thisInventory.quantity}</td><td>${thisInventory.restock_level}</td><td>${thisInventory.last_updated_on}</td><td>${thisInventory.can_update}</td></tr>`;
                if (i == 0) {
                    firstInventory = thisInventory;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Build a list of all used items
    // ****************************************

    $("#search-btn-used").click(function () {
        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/inventory/USED`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())            
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">Product_ID</th>'
            table += '<th class="col-md-2">Condition</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Restock_Level</th>'
            table += '<th class="col-md-2">Last_Updated_On</th>'
            table += '<th class="col-md-2">Can_Update</th>'
            table += '</tr></thead><tbody>'
            let firstInventory = "";
            for(let i = 0; i < res.length; i++) {
                let thisInventory = res[i];
                table +=  `<tr id="row_${i}"><td>${thisInventory.product_id}</td><td>${thisInventory.condition}</td><td>${thisInventory.quantity}</td><td>${thisInventory.restock_level}</td><td>${thisInventory.last_updated_on}</td><td>${thisInventory.can_update}</td></tr>`;
                if (i == 0) {
                    firstInventory = thisInventory;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstInventory != "") {
                update_form_data(firstInventory)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

})
