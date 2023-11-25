## Overview
This is an Automation script, created to run Looker dashbaord queries,without having to manually open the dashbaord in a browser. This will help cache these queries on the Looker, hence getting improved performance right after data refresh.

Note: This script only runs the dashboard queries for the default filters set on the dashbaord.

## Key Steps:
Install the Looker SDK: Looker SDK provides a set of API's to interact with your Looker instance through programming Languages. This step involves using pip to install the Looker SDK (pip install looker-sdk) .

Set the paramters and keys: Set the parmaeters for the script, such as Environment, Sector. Also get the secret keys and set the global variables to initialise the Looker SDK

Initialise the Looker SDK: Use the secret keys to configure nad initialise a Looker SDK object, which will be used for the API calls.

Get Dashboard Details: Use the Looker API called dashboard, to get all details of the dashbaord as a JSON object.

Get Query Details of the visualisation: Parse the JSON dashboard object for each Visualisation's query details, which includes the fields, default filters and any sorting etc.

Create the Query: Create a query with the details retrieved from the dashboard JSON object using the Looker API called create_query.

Run the query of the visualisation: Run the query created by passing the query ID using the Looker API called create_query_task.
