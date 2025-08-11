import pandas as pd
import tableauserverclient as TSC
import json
from credentials import PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID #Add the credentials info

#get the list of workbook using GraphQL query
def get_workbook_pb_datasource_list(PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	#Authorize the info
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

	with server.auth.sign_in(tableau_auth):
		#Write the graphQL query to extract the list of workbooks and published datasources
		data_resp = server.metadata.query("""
		query listwb_pbl_datasource{
			workbooks {
				id
				name
			}
			publishedDatasources{
				luid
				name
			}
		}
		""")
		#Extract the workbook data after querying
		wb = data_resp['data']['workbooks']

		#Extract the published datasource data after querying
		pb_ds = data_resp['data']['publishedDatasources']

	#Check if no workbooks or published datasources found
	if not wb:
		print("No workbooks found.")
		return pd.DataFrame()
	if not pb_ds:
		print("No published datasources found.")
		return pd.DataFrame()
	
	#Flatten and store the data in pandas dataframe
	wb_df = pd.json_normalize(wb)
	pb_ds_df = pd.json_normalize(pb_ds)

	#return the list of workbooks and published datasources
	return wb_df, pb_ds_df


#From the list of workbook above, let the user choose workbook to get detail info
def print_workbook_details(selected_wb_name,PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

    #Write the graphQL query with the workbook_name filter
	#It will retrieve the workbook details and also including the published datasources connected to the workbook
	wb_details = """
    query getworkbookDetails($workbook_name: String) {
        workbooks(filter: { name: $workbook_name }) {
            id
            name
            projectName
            owner {
                id
                name
            }
			upstreamDatasources {
				luid
				name
			}
        }
    }
	"""
    #Sign in with the tableau auth info
	with server.auth.sign_in(tableau_auth):
    	#run the graphQL query and get the response
		filtered_workbook = server.metadata.query(wb_details,variables={'workbook_name': selected_wb_name})

	#Flatten and store the workbook details in a pandas DataFrame
	workbooks_list = filtered_workbook['data']['workbooks']

	#After extracting the workbook details for 1 workbook seleteced, store it in wb
	wb = workbooks_list[0]

	# Flatten data and Print the workbook info separately
	print("\n=================================================")
	print("==> Workbook Details: ")
	print(f"Workbook ID: {wb['id']}")
	print(f"Workbook Name: {wb['name']}")
	print(f"Project Name: {wb['projectName']}")
	print(f"Owner ID: {wb['owner']['id']}")
	print(f"Owner Name: {wb['owner']['name']}")
	print("===================================================\n")

	#Initialize empty list for the upstreamDataSources which stored published data sources
	#If no published data sources are connected to the workbook, return empty DataFrame (None value)
	upstreams = wb.get("upstreamDatasources", [])
	if not upstreams:
		print("No published data sources are connected to this workbook.")
		return pd.DataFrame()

	# Initialize an empty list to store the published data sources if workbook connected to a published data source
	pds_rows = []
	#Store the luid and name of the published data sources 
	for pds in upstreams:
		pds_rows.append({
			'Published_DS_LUID': pds['luid'],
			'Published_DS_Name': pds['name']
		})

	# Return the published data sources and all info of the workbook by printing out the screen above
	pds_df = pd.DataFrame(pds_rows)
	return pds_df

#Same as the print workbook details function above, this function will print the details of the published data source
def print_published_ds_details(selected_pb_ds_name,PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	#Authorize the info
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

	#Write the graphQL query with the name of the published datasource filter
	#It will retrieve the published datasource details and also the workbooks connected to it
	pb_ds_details = """
	query getpbdsDetails($pb_ds_name: String) {
		publishedDatasources(filter: { name: $pb_ds_name }) {
			luid
			name
			downstreamWorkbooks {
				id
				name
				projectName
				owner {
					id
					name
				}
			}
		}
	}
	"""
	#Sign in with the tableau auth info
	with server.auth.sign_in(tableau_auth):
		#run the graphQL query
		filtered_pb_ds = server.metadata.query(pb_ds_details,variables={'pb_ds_name': selected_pb_ds_name})

	#Flatten and store the published datasource details in a pandas DataFrame
	pb_ds_df = pd.json_normalize(filtered_pb_ds['data']['publishedDatasources'],
					  record_path='downstreamWorkbooks',
						meta=['luid', 'name'],
						meta_prefix='pb_ds_',
						record_prefix='wb_')

	#Store the published datasource details in pb_ds
	pb_ds_list = filtered_pb_ds['data']['publishedDatasources']

	#By filtering the published datasource, we only get 1 published datasource
	ds = pb_ds_list[0]

	# Print the Published DS info separately
	print("\n=================================================")
	print("==> Published Data Source Details: ")
	print(f"Published DS LUID: {ds['luid']}")
	print(f"Published DS Name: {ds['name']}")
	print("===================================================\n")

	# Initialize an empty list for downstream workbooks in case not found any workbooks connected to the published datasource
	downstreams = ds.get("downstreamWorkbooks", [])
	#Return None value if no workbooks are connected to the published datasource
	if not downstreams:
		print("No workbooks are connected to this published data source.")
		return pd.DataFrame()

	#Initialize an empty list for the downstream workbooks
	wb_rows = []
	#Write the workbook details into the wb_rows list
	for wb in downstreams:
		wb_rows.append({
			'Workbook_ID': wb['id'],
			'Workbook_Name': wb['name'],
			'Project_Name': wb['projectName'],
			'Owner_ID': wb['owner']['id'],
			'Owner_Name': wb['owner']['name']
		})

	wb_df = pd.DataFrame(wb_rows)

	#Return the workbook details DataFrame and the published datasource details by printing out the screen above
	return wb_df

#Main function
def main():
	print("================================================")
	print("=== DataDevQuest - 2025_07 - Intermedate     ===")
	print("=== Challenged by: Jordan Woods              ===")
	print("=== Solved by: Le Luu                        ===")
	print("================================================")
	print()

	#Call function get_workbook_list to get the list of all workbooks and published data sources on server site
	wb_df, pb_ds_df = get_workbook_pb_datasource_list(PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)

	#if couldn't find any workbooks there
	if wb_df.empty:
		print(f"No workbooks on {SERVER_ADDRESS}/{SITE_ID}")
		return
	
	if pb_ds_df.empty:
		print(f"No published datasources on {SERVER_ADDRESS}/{SITE_ID}")
		return
	
	while True:
		#Show 3 options for the user to choose
		#Option 1: Viwe the details of a specific workbook
		#Option 2: View the details of a specific published datasource
		#Option 3: Exit the program
		print("\n================================================")
		print("Which option would you like to choose?")
		print("1. View details of a specific workbook")
		print("2. View details of a specific published datasource")
		print("3. Exit")

		#Get the user input
		choice = input("Enter your choice (1,2 or 3): ").strip()
		print("\n================================================")
		#If user choose option 1, then show available workbooks from the workbook list
		if choice == '1':
			print("Available workbooks:")
			for choice,name in enumerate(wb_df['name']):
				print(f"{choice+1}. {name}")
			try:
				#Let the user choose the workbook number to view details
				selected_wb = int(input("Enter the number of the workbook you want to view details for: "))
				print("\n=================================================")
				if 0 <= selected_wb <= len(wb_df):
					selected_wb_name = wb_df.iloc[selected_wb-1]['name']
					#call the print_workbook_details function to get the details of the selected workbook and published datasources connected to it
					wb_details_df = print_workbook_details(selected_wb_name, PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)
					if not wb_details_df.empty:
						print("==> Published data sources connected:")
						print(wb_details_df)
				else:
					print("Invalid selection. Please try again.")
			except ValueError:
				print("Invalid input. Please enter a number corresponding to the workbook.")

		#If user choose option 2, then show available published datasources from the published datasource list
		elif choice == '2':
			print("Available published datasources:")
			for choice,name in enumerate(pb_ds_df['name']):
				print(f"{choice+1}. {name}")
			try:
				#Let the user choose the published datasource number to view details
				selected_pb_ds = int(input("Enter the number of the published datasource you want to view details for: "))
				print("\n=================================================")
				if 0 <= selected_pb_ds <= len(pb_ds_df):
					selected_pb_ds_name = pb_ds_df.iloc[selected_pb_ds-1]['name']
					#Call the print_published_ds_details function to get the details of the selected published datasource and workbooks connected to it
					pb_ds_detail_df = print_published_ds_details(selected_pb_ds_name, PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)
					if not pb_ds_detail_df.empty:
						print("==> Workbooks connected:")
						print(pb_ds_detail_df)
				else:
					print("Invalid selection. Please try again.")
			except ValueError:
				print("Invalid input. Please enter a number corresponding to the published datasource.")

		elif choice == '3':
			print("Exiting the program. Thank you! See you next time!")
			break
		else:
			print("Invalid choice. Please enter only 1, 2, or 3.")

if __name__ == "__main__":
	main()