import pandas as pd
import tableauserverclient as TSC
import json
from credentials import PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID

#get the list of workbook using GraphQL query
def get_workbook_list(PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	#Authorize the info
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

	with server.auth.sign_in(tableau_auth):
		#Write the graphQL query to extract workbook id and name
		workbook_list = server.metadata.query("""
		{
			workbooks {
				id
				name
			}
		}
		""")
		#get the data after quering
		wb = workbook_list['data']['workbooks']

	if not wb:
		print("No workbooks found.")
		return pd.DataFrame()
	#parse and store the data in pandas dataframe
	wb_df = pd.json_normalize(wb)
	return wb_df

#From the list of workbook above, let the user choose workbook to get detail info
def print_workbook_details(selected_wb_id,PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
    tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
    server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

    #Store the selected ID in JSON format before passing it to the filter in graphQL query
    selected_id = json.dumps(selected_wb_id) 

    #Write the graphQL query with the selected_id to filter
    query = f"""
    {{
        workbooks(filter: {{ id: {selected_id} }}) {{
            projectName
            owner {{
                id
                name
            }}
        }}
    }}
    """

    #Sign in with the tableau auth info
    with server.auth.sign_in(tableau_auth):
    	#run the graphQL query
        filtered_workbook = server.metadata.query(query)

    #Store the workbook details in wb_details
    wb_details = filtered_workbook['data']['workbooks']

    #Parse JSON 
    wb_details_df = pd.json_normalize(wb_details)

    #Rename the column in the dataframe
    wb_details_df = wb_details_df.rename(columns={
        'id': 'Workbook ID',
        'name': 'Workbook Name',
        'projectName': 'Project Name',
        'owner.id': 'Owner ID',
        'owner.name': 'Owner Name'
    })

    return wb_details_df


def main():
	print("================================================")
	print("=== DataDevQuest - 2025_07 - Beginner        ===")
	print("=== Challenged by: Jordan Woods              ===")
	print("=== Solved by: Le Luu                        ===")
	print("================================================")
	print()

	#Call function get_workbook_list to get the list of all workbooks on server site
	wb_df = get_workbook_list(PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)

	#if couldn't find any workbooks there
	if wb_df.empty:
		print(f"No workbooks on {SERVER_ADDRESS}/{SITE_ID}")
		return

	#Print the list of workbooks on the site
	print(f"List of Workbooks on site {SITE_ID}:")
	for i, row in wb_df.iterrows():
		print(f"{i+1}: {row['name']}")

	#Initialize empty for the selected workbook
	selected_wb = None  

	#From the list of workbooks, let the user choose the workbook want to see details
	while True:
		try:
			#From the lis
			choice = int(input("Select a workbook by number (or 0 to exit): "))
			if choice == 0:
				print("Exiting ... See you next time!")
				return
			elif 1 <= choice <= len(wb_df):
				selected_wb = wb_df.iloc[choice - 1]
				print("You selected:")
				print(f"Workbook name: {selected_wb['name']}")
				break
			else:
				print("Invalid choice, please try again.")
		except ValueError:
			print("Please enter a valid number.")

	# Access ID only if a workbook was selected
	if selected_wb is not None:
		selected_wb_id = selected_wb['id']
		print(f"Workbook ID: {selected_wb_id}")

	detail_df = print_workbook_details(selected_wb_id, PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)

	if not detail_df.empty:
		print("Workbook Details:")
		pd.set_option('display.max_columns', None)
		print(detail_df)
	else:
		print("No details found")

if __name__ == "__main__":
	main()