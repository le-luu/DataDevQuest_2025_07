import pandas as pd
import tableauserverclient as TSC
import json
from credentials import PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID

#get the list of workbook using GraphQL query
def get_workbook_pb_datasource_list(PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	#Authorize the info
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

	with server.auth.sign_in(tableau_auth):
		#Write the graphQL query to extract workbook id and name
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
		#get the data after quering
		wb = data_resp['data']['workbooks']
		pb_ds = data_resp['data']['publishedDatasources']

	if not wb:
		print("No workbooks found.")
		return pd.DataFrame()
	if not pb_ds:
		print("No published datasources found.")
		return pd.DataFrame()
	#parse and store the data in pandas dataframe
	wb_df = pd.json_normalize(wb)
	pb_ds_df = pd.json_normalize(pb_ds)

	return wb_df, pb_ds_df


#From the list of workbook above, let the user choose workbook to get detail info
def print_workbook_details(selected_wb_name,PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

    #Write the graphQL query with the selected_id to filter
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
    	#run the graphQL query
		filtered_workbook = server.metadata.query(wb_details,variables={'workbook_name': selected_wb_name})

	workbooks_list = filtered_workbook['data']['workbooks']

	wb = workbooks_list[0]

	# Print the workbook info separately
	print("\n=== Workbook Details ===")
	print(f"Workbook ID: {wb['id']}")
	print(f"Workbook Name: {wb['name']}")
	print(f"Project Name: {wb['projectName']}")
	print(f"Owner ID: {wb['owner']['id']}")
	print(f"Owner Name: {wb['owner']['name']}")
	print("========================\n")

	# Build the upstream datasources table
	upstreams = wb.get("upstreamDatasources", [])
	if not upstreams:
		print("No published data sources are connected to this workbook.")
		return pd.DataFrame()

	pds_rows = []
	for pds in upstreams:
		pds_rows.append({
			'Published_DS_LUID': pds['luid'],
			'Published_DS_Name': pds['name']
		})

	pds_df = pd.DataFrame(pds_rows)
	return pds_df


def print_published_ds_details(selected_pb_ds_name,PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID):
	tableau_auth = TSC.PersonalAccessTokenAuth(PAT_NAME, PAT_SECRET, SITE_ID)
	server = TSC.Server(SERVER_ADDRESS, use_server_version=True)

	#Write the graphQL query with the selected_id to filter
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

	pb_ds_df = pd.json_normalize(filtered_pb_ds['data']['publishedDatasources'],
					  record_path='downstreamWorkbooks',
						meta=['luid', 'name'],
						meta_prefix='pb_ds_',
						record_prefix='wb_')

	pb_ds_list = filtered_pb_ds['data']['publishedDatasources']

	ds = pb_ds_list[0]

	# Print the Published DS info separately
	print("\n=== Published Data Source Details ===")
	print(f"Published DS LUID: {ds['luid']}")
	print(f"Published DS Name: {ds['name']}")
	print("=====================================\n")

	# Build the downstream workbooks table
	downstreams = ds.get("downstreamWorkbooks", [])

	if not downstreams:
		print("No workbooks are connected to this published data source.")
		return pd.DataFrame()

	wb_rows = []
	for wb in downstreams:
		wb_rows.append({
			'Workbook_ID': wb['id'],
			'Workbook_Name': wb['name'],
			'Project_Name': wb['projectName'],
			'Owner_ID': wb['owner']['id'],
			'Owner_Name': wb['owner']['name']
		})

	wb_df = pd.DataFrame(wb_rows)
	return wb_df


def main():
	print("================================================")
	print("=== DataDevQuest - 2025_07 - Intermedate     ===")
	print("=== Challenged by: Jordan Woods              ===")
	print("=== Solved by: Le Luu                        ===")
	print("================================================")
	print()

	#Call function get_workbook_list to get the list of all workbooks on server site
	wb_df, pb_ds_df = get_workbook_pb_datasource_list(PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)

	#if couldn't find any workbooks there
	if wb_df.empty:
		print(f"No workbooks on {SERVER_ADDRESS}/{SITE_ID}")
		return
	
	if pb_ds_df.empty:
		print(f"No published datasources on {SERVER_ADDRESS}/{SITE_ID}")
		return
	
	while True:
		
		print("Which option would you like to choose?")
		print("1. View details of a specific workbook")
		print("2. View details of a specific published datasource")
		print("3. Exit")

		choice = input("Enter your choice (1,2 or 3): ").strip()
		if choice == '1':
			print("Available workbooks:")
			for choice,name in enumerate(wb_df['name']):
				print(f"{choice+1}. {name}")
			try:
				selected_wb = int(input("Enter the number of the workbook you want to view details for: "))
				if 0 <= selected_wb <= len(wb_df):
					selected_wb_name = wb_df.iloc[selected_wb-1]['name']

					wb_details_df = print_workbook_details(selected_wb_name, PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)
					if not wb_details_df.empty:
						print("\n Workbook Details:")
						print(wb_details_df)
				else:
					print("Invalid selection. Please try again.")
			except ValueError:
				print("Invalid input. Please enter a number corresponding to the workbook.")

		elif choice == '2':
			print("Available published datasources:")
			for choice,name in enumerate(pb_ds_df['name']):
				print(f"{choice+1}. {name}")
			try:
				selected_pb_ds = int(input("Enter the number of the published datasource you want to view details for: "))
				if 0 <= selected_pb_ds <= len(pb_ds_df):
					selected_pb_ds_name = pb_ds_df.iloc[selected_pb_ds-1]['name']
					pb_ds_detail_df = print_published_ds_details(selected_pb_ds_name, PAT_NAME, PAT_SECRET, SERVER_ADDRESS, SITE_ID)
					if not pb_ds_detail_df.empty:
						print("\n Published Datasource Details:")
						print(pb_ds_detail_df)
				else:
					print("Invalid selection. Please try again.")
			except ValueError:
				print("Invalid input. Please enter a number corresponding to the published datasource.")

		elif choice == '3':
			print("Exiting the program.")
			break
		else:
			print("Invalid choice. Please enter only 1, 2, or 3.")

if __name__ == "__main__":
	main()