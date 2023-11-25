# Databricks notebook source


# Import Libraries
import looker_sdk
from looker_sdk import api_settings
from looker_sdk.sdk.api40 import models

# -------------------------------------------------------------------------------------- #
# Initialising global variables 

Looker_env_base_url = 'https://XXX.com'

# Credentials required for the SDK
base_url_api = 'https://XXX.com:19999'  # Base URL for API.
client_id = 'client_id'  # API 4 client id
client_secret = 'client_secret'  # API 4 client secret

verify_ssl = 'True'

# List of dashboards of each sectors
dashboard_ids = '528'


# Override SDK Configuration class Overriding the SDK configuration class to configure using the keys stored in a
# safe instead of the Looker.ini (A file to store credentials, which is mentioned in Looker documentation)

class MyApiSettings(api_settings.ApiSettings):
    def __init__(self, *args, **kw_args):
        self.my_var = kw_args.pop("my_var")
        super().__init__(*args, **kw_args)

    def read_config(self) -> api_settings.SettingsConfig:
        config = super().read_config()
        # assign the values based on the Looker environment

        config["client_id"] = client_id
        config["client_secret"] = client_secret
        config["base_url"] = base_url_api
        config["verify_ssl"] = verify_ssl
        return config


# Initializing Looker SDK

# Initialise the Looker SDK
sdk = looker_sdk.init40(config_settings=MyApiSettings(my_var=""))

# testing initialising
if sdk:
    print("Returned SDK initialisation Object:", sdk)
else:
    print("not initialised")


# Functions for Looker API calls

def create_query_api(sdk, model, view, fields, query_filters, sorts, limit, col_limit, total, pivots, dynamic_fields):
    """
      A Looker API for Creating a query.
        Paramters:
          sdk                      : The initialised Looker SDK object
          model                    : Looker Model Name
          view                     : Looker View name
          fields                   : The dimensions and measures used in the query
          pivots                   : Pivoted fields in the query
          query_filters            : Filtered Fields and their values
          sort                     : Sorting order, if any
          row                      : Number of rows to be selected
          col_limit                : Column Limit, if any
          total                    : Column Total, if enabled
          dynamic_fields           : Table Calculation or custom explore fields, if any
        Returns:
          response_create_query_api: A JSON object of the query created.
      """

    response_create_query_api = sdk.create_query(
        body=models.WriteQuery(
            model=model,
            view=view,
            fields=fields,
            filters=query_filters,
            sorts=sorts,
            limit=limit,
            column_limit=col_limit,
            total=total,
            pivots=pivots,
            dynamic_fields=dynamic_fields
        ))
    return response_create_query_api


def create_query_task_api(sdk, response_create_query_api_id):
    """Looker API to run a query that has been created, if it exists in cache it runs from cache,
    otherwise runs the query and caches it.
          Parameters:
            sdk                           : The initialised Looker SDK object
            response_create_query_api_id  : The ID of the query that had been created

          Returns:
            response_create_query_task    : A JSON object of the query Run.
      """
    response_create_query_task = sdk.create_query_task(
        body=models.WriteCreateQueryTask(
            query_id=response_create_query_api_id,
            result_format=models.ResultFormat.json,
            source="Dashboard",
            deferred=False
        ),
        cache=True)
    return response_create_query_task


# Function Definitions for extracting query details from the dashboard JSON Object
def get_vis_applicable_filters(response, vis_no):
    """
        Reads the dashboard details JSON object, for extracting the List of filters that are applicable
        to the current visualistion.
          parameter:
            response               : JSON object with details of dashboard.
            vis_no                 : The visualisation being parsed currently

          Returns:
            vis_applicable_filters : A dictionary with keys - Name of the filter
            and values - the Looker field being referred
      """
    vis_applicable_filters = {}
    for i in range(0, len(response.dashboard_elements[vis_no]["result_maker"]["filterables"][0]["listen"])):
        filter_name = response.dashboard_elements[vis_no]["result_maker"]["filterables"][0]["listen"][i][
            "dashboard_filter_name"]
        filter_dimension = response.dashboard_elements[vis_no]["result_maker"]["filterables"][0]["listen"][i]["field"]
        vis_applicable_filters[filter_name] = filter_dimension
    return vis_applicable_filters


def get_dashboard_default_filters(response):
    """
          Reads the dashboard details JSON object, for extracting the List of default filters
          parameter:
            response               : JSON object with details of dashboard.

          Returns:
            dashboard_default_filters : A dictionary with keys - Name of the filter
            and values - the default value assigned
      """
    dashboard_default_filters = {}
    for i in range(0, len(response.dashboard_filters)):
        if (response.dashboard_filters[i]['default_value']) != "":
            dashboard_default_filters[response.dashboard_filters[i]['name']] = response.dashboard_filters[i][
                'default_value']
    return dashboard_default_filters


def get_query_filter_name_dimension(response, vis_no, dashboard_default_filters):
    """
          Creates a dictionary with the filter fields (dimension) applicable to the visualisation
          and the value to be passed to it from the dashboard.
          The dictionary will only have the fields that have some value to be filtered.
          parameter:
            response                  : JSON object with details of dashboard.
            vis_no                    : The visualisation being parsed currently
            dashboard_default_filters : A dictionary with default dashboard filters and their values
          Returns:
            query_filters             : A dictionary with keys - the Looker field being referred
            and values - the default value assigned
      """
    query_filters = {}

    # get the list of filter fields applicable to visualisation
    vis_applicable_filters = get_vis_applicable_filters(response, vis_no)

    # Find the filter fields which actually have some default value set from the dashbaord
    common_keys = set(dashboard_default_filters.keys()) & set(vis_applicable_filters.keys())

    # Assign the Key as the dimension name from the vis_applicable_filters
    # and the Value as the default value for filter from the dashboard_default_filters
    query_filters = {vis_applicable_filters[key]: dashboard_default_filters[key] for key in common_keys}

    # Return the dictionary which is in the correct format to be passed to the create query API
    return query_filters


def run_dashboard_queries(dashboard_id):
    """
        Gets the JSON object with all details of a dashboard.
        Creates the queries behind the visualisation with default filters applied and runs it.
          Parameters:
           dashboard_id : Slug ID of the dashboard to be triggered.
      """
    # Get JSON object of the dashboard, which has all the details of the visualisations and the filters in it.
    response = sdk.dashboard(
        dashboard_id=dashboard_id,
        fields="dashboard_elements,dashboard_filters")

    # Extract the default filters and the values set for them from the dashboard JSON
    dashboard_default_filters = get_dashboard_default_filters(response)

    # Loop through each Visualisation, create the query to be run and run it
    for vis_no in range(0, len(response.dashboard_elements)):
        print("visual:", vis_no, response.dashboard_elements[vis_no]["title"])

        if response.dashboard_elements[vis_no]["query"] != None:  # If the Tile is a HTML tile ignore it.

            # Read all the relevant metadata for the query

            q_id = (response.dashboard_elements[vis_no]["query"]["id"])
            fields = (response.dashboard_elements[vis_no]["query"]["fields"])
            pivots = (response.dashboard_elements[vis_no]["query"]["pivots"])
            sorts = (response.dashboard_elements[vis_no]["query"]["sorts"])
            limit = (response.dashboard_elements[vis_no]["query"]["limit"])
            col_limit = (response.dashboard_elements[vis_no]["query"]["column_limit"])
            total = (response.dashboard_elements[vis_no]["query"]["total"])
            row_total = (response.dashboard_elements[vis_no]["query"]["row_total"])
            subtotal = (response.dashboard_elements[vis_no]["query"]["subtotals"])
            filter_exp = (response.dashboard_elements[vis_no]["query"]["filter_expression"])
            model = (response.dashboard_elements[vis_no]["query"]["model"])
            view = (response.dashboard_elements[vis_no]["query"]["view"])
            dynamic_fields = (response.dashboard_elements[vis_no]["result_maker"]["dynamic_fields"])

            # Get all the filters to be applied to the query and
            query_filters = get_query_filter_name_dimension(response, vis_no, dashboard_default_filters)

            # Create the query for the visualisation
            response_create_query_api = create_query_api(sdk, model, view, fields, query_filters, sorts, limit,
                                                         col_limit, total, pivots, dynamic_fields)
            print(response_create_query_api["id"])

            # get the query ID for the query created
            response_create_query_api_id = response_create_query_api["id"]

            # Run the query
            response_create_query_task = create_query_task_api(sdk, response_create_query_api_id)


def main():
    # Trigger Looker Dashboard Visualizations
    run_dashboard_queries(dashboard_ids)


if __name__ == "__main__":
    main()





