# DataDev Quest Challenge 2025_07

![image](https://github.com/le-luu/DataDevQuest_2025_03/blob/main/img/logo.svg)

### Challenged By: 
Jordan Woods

### Objective
- Apply the Tableau Metadata API to query the content on the site
- Learn writing GraphQL query to retrieve the data
- Apply filters, variables and pages through Tableau Metadata API
- Parse JSON and flatten data from the response in JSON structure format

### Solution Video
[![DDQ_2025_07](https://img.youtube.com/vi/DnZodzxS1HE/0.jpg)](https://www.youtube.com/watch?v=DnZodzxS1HE)

### Beginner Challenge
Link to the Beginner Challenge: https://datadevquest.com/ddq2025-07-tableau-metadata-api-beginner/

**Challenge:**
Write a query that gets out details about a workbook of your choosing. Retrieve its 
- ids
- The owner’s id
- The name of the project that it is in.
- Extra credit if you apply filters appropriately!

**Output**

![image](https://github.com/le-luu/DataDevQuest_2025_07/blob/main/img/beginner_graphql_query.png)

The GraphQL query to retrive the workbook details (id, name, project Name, owner) without using filter and with filter.

![image](https://github.com/le-luu/DataDevQuest_2025_07/blob/main/img/output_beginner_ddq_2025_07.png)

In the Python script, I listed all the workbooks on the site. Then, let the user choose 1 workbook to get more details.

### Intermediate Challenge
Link to the Intermediate Challenge: https://datadevquest.com/ddq2025-07-tableau-metadata-api-intermediate/

**Challenge:**
Write a query that gets out details about a workbook of your choosing. Retrieve its 
- ids
- The owner’s id
- The name of the project that it is in
- Apply the filter with variables

**Output**

![image](https://github.com/le-luu/DataDevQuest_2025_07/blob/main/img/Intermediate_schema.png)

One benefit of using MetaData API is I can combine multiple queries into one GraphQL query to extract the data I want. With REST API, I couldn't do that. To extract different data, I need to use different endpoint.

I built a Python program with this schema. First, I will write a query to list all workbooks and published data source in one GraphQL query. Then, I will let the user choose 2 options:
- Option 1: Select a workbook on the list to explore more details (including workbook id, name, project Name, owner id, owner name, published data source connected by that specified workbook)
- Option 2: Select a published data source on the list to explore more details (including luid, name, and the connected workbook to that published data source with its id, name, project Name, owner id, owner name)

![image](https://github.com/le-luu/DataDevQuest_2025_07/blob/main/img/intermediate_graphql_query.png)

- These are 3 GraphQL queries that I used to extract the metadata. The first query listwb_pbl_datasource will query all workbooks and published data source.
- The second query (getworkbookDetails) will apply the workbook_name variable in the filter for option 1 above
- The third query (getpbdsDetails) will apply the published data source name variable in the filter for option 2 above

![image](https://github.com/le-luu/DataDevQuest_2025_07/blob/main/img/output_intermediate_ddq_2025_07.png)

The output of the program.

### Instructions
- You need to install Python in your local computer first
- For this repository and clone it to your local computer
- Open the Command Prompt (for Windows) and Terminal (for Mac), change the directory to the DataDevQuest_2025_05
    ```
    cd DataDevQuest_2025_07
    ```
- Install and activate the virtual environment
    ```
    pip install virtualenv
    virtualenv venv
    venv\Scripts\activate
    ```    
- Install the packages in the Command Prompt
    ```
    pip install -r requirements.txt
    ```
    It may take a few seconds to install all packages:
    - pandas
    - tableauserverclient
- Open the credentials.py file and change the value for:
  - PAT_NAME
  - PAT_SECRET
  - SERVER_ADDRESS
  - SITE_ID
  - Then save the credentials.py file

**Beginner Challenge**
  
- To run the Beginner solution program, in the Command Prompt (or Terminal) type and enter:
    ```
    python Le_DDQ_2025_07_Beginner.py
    ```
**Intermediate Challenge**

- To run the Intermediate solution program, in the Command Prompt (or Terminal) type and enter:
    ```
    python Le_DDQ_2025_07_Intermediate.py
    ```
