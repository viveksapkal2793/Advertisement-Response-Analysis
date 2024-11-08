from pymongo import MongoClient
import pandas as pd
import os

# client = pymongo.MongoClient("mongodb://172.31.99.238:27017")
client = pymongo.MongoClient("mongodb://docker.host.internal:27017")
db = client["advertisement_response_analysis"]

workbook1_path = "/app/data/survey_data_with_demographics.xlsx"

def load_workbook1_data(workbook1_path):

        collections_map = {
            "Survey_Respondents": "survey_respondents",
            "Advertisement_Info": "advertisement_info",
            "Responses_to_Ads": "responses_to_ads",
            "Ad_Demographic_Link": "ad_demographic_link",
            "Demographic_Data": "demographic_data",
            "Purchase_Info": "purchase_info"
        }
        
        for sheet_name, collection_name in collections_map.items():
            df = pd.read_excel(workbook1_path, sheet_name=sheet_name)
            
            records = df.to_dict(orient="records")
            
            db[collection_name].insert_many(records)
            print(f"Inserted {len(records)} records into {collection_name}")

        print("ext_and_load.py has successfully run.")

if __name__ == "__main__":
    run_flag_path = "/app/tmp/ext_and_load_ran.txt"
    if not os.path.exists(run_flag_path):
        load_workbook1_data(workbook1_path)
        with open(run_flag_path, "w") as f:
            f.write("Executed")
        print("Data load completed.")
    else:
        print("Data already loaded, skipping execution.")
