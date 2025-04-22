import pandas as pd
from visicom import VisicomAPI
from shiny import App, render, ui, reactive

app_ui = ui.page_fluid(
    ui.h2("Geocoding"),
    ui.input_text("api", "Enter API key:"),
    ui.download_button("download_template", "Download input template file"),
    ui.input_file("geofile", "Choose an xlsx file to geocode", accept=".xlsx"),
    ui.download_button("download", "Download geocoded file")
)

def server(input, output, session):
    
    @render.download()
    def download():
        # Validate the API key input
        if input.api() is None or input.api().strip() == '':
            ui.notification_show("Please provide a valid API key.", type="error")
            return None
        
        # Initialize the API with the provided key
        api = VisicomAPI(api_key=input.api())
        
        # Validate the uploaded file
        if input.geofile() is None:
            ui.notification_show("Please upload a file to geocode.", type="error")
            return None
        
        # Load the Excel file
        df = pd.read_excel(input.geofile()[0]["datapath"])
        
        # Validate required columns
        required_columns = ["raion", "hromada", "settlement", "street"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            ui.notification_show(f"Missing columns: {', '.join(missing_columns)}. Please ensure the file contains these columns.", type="error")
            return None

        # Prepare dataframe for geocoding results
        df["lat_visicome"] = None
        df["lon_visicome"] = None
        df["same"] = None
        df["found address"] = None
        no_result = []

        # Iterate over the rows to perform geocoding
        for idx, row in df.iterrows():
            hromada = row["hromada"]
            settlement = row["settlement"]
            street = row["street"]
            raion = row["raion"] if not pd.isna(row["raion"]) else ''
            if pd.isna(street) or pd.isna(settlement):
                continue
            street_clean = street.split('.')[1].split(',')[0].strip() if len(street.split('.')) > 1 else street.split(',')[0].strip()
            building_id = street.split(',')[-1].strip()
            settlement_clean = settlement.split(' ')[1].strip() if len(settlement.split(' ')) > 1 else settlement
            search_address = f'{raion} {hromada} {settlement} {street}' if raion != '' else f'{hromada} {settlement} {street}'
            
            try:
                result = api.get_geocode(text=search_address, limit=1)
            except Exception as e:
                ui.notification_show(f"Error during geocoding: {str(e)}", type="error")
                return None
            
            if "error" in result.keys():
                ui.notification_show(result["error"], type="error")
                return None
            
            if len(result.keys()) == 0:
                no_result.append(search_address)
                continue
            
            # Process the geocoding result
            block = result['features'][0] if "features" in result.keys() else result
            if "name" not in block['properties'].keys():
                continue

            if "settlement" not in block['properties'].keys():
                is_same = False
                df.loc[idx, "lat_visicome"] = block['geo_centroid']['coordinates'][1]
                df.loc[idx, "lon_visicome"] = block['geo_centroid']['coordinates'][0]
                df.loc[idx, "found address"] = block['properties']['name']
                df.loc[idx, "same"] = is_same
            elif "street" not in block['properties'].keys():
                is_same = False
                df.loc[idx, "lat_visicome"] = block['geo_centroid']['coordinates'][1]
                df.loc[idx, "lon_visicome"] = block['geo_centroid']['coordinates'][0]
                df.loc[idx, "found address"] = block['properties']['settlement'] + ' ' + block['properties']['name']
                df.loc[idx, "same"] = is_same
            else:
                is_same = (block['properties']['name'] == building_id and 
                           block['properties']['settlement'] == settlement_clean and 
                           block['properties']['street'].split('(')[0].strip() == street_clean)
                df.loc[idx, "lat_visicome"] = block['geo_centroid']['coordinates'][1]
                df.loc[idx, "lon_visicome"] = block['geo_centroid']['coordinates'][0]
                df.loc[idx, "found address"] = block['properties']['settlement'] + ' ' + block['properties']['street'] + ' ' + block['properties']['name']
                df.loc[idx, "same"] = is_same

        # Save the geocoded file
        output_path = 'output_dir/geocoding.xlsx'
        df.to_excel(output_path, index=False)

        # Display results in a modal
        if no_result:
            message = 'Such addresses were not found:\n' + '\n'.join(no_result)
        else:
            message = 'All addresses have been geocoded successfully'
        
        m = ui.modal(message, title="Results", easy_close=True, footer=None)
        ui.modal_show(m)
        ui.notification_show("File has been geocoded successfully!")

        return output_path

    @render.download()
    def download_template():
        return "template.xlsx"

app = App(app_ui, server)
# app.run()
