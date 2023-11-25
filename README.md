# Automate triggering Looker Dashboard using Looker API (looker-sdk Python)
## What was the 'issue'?
  1) Looker provides a datagroups to invalidate the cache but no feature to re cache the queries unless someone manually open the dashboard and runs it.
  2) I have a dashboard, whose underlying tables refreshes at odd hours once in a month. The tables are huge, so I cannot predict the time for the end of table load.
  3) The dashboard queries had better chance of performing better once the queries are cached, atleast the default ones on the dashboard.
  4) The script should trigger the dashboard from the data engineering job/workflow.

## Solutions:
There were 3 solutions to the problem,
  1) Create a script to open a url in a browser.<br>
     Challenges:
       1) The script gets executed in a cluster (Databricks Cluster), not a UI. The urlopen donot actually open a tab in a browser, and Looker requires dashbaord to be opened for the queries to get triggered.
       2) Requires embed user creation, which can get messy.
     
  2) Create a script using the Looker API, which builds the queries on the dashbaord with default filters applied to it and executes it.
  4) A Solution with cost associated is to use power automate: create a workflow to open a webbrowser based on a trigger. 
