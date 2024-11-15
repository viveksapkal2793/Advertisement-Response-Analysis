from datetime import datetime
import pandas as pd
import pymongo
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

# Configuration
SERVICE_ACCOUNT_FILE = "/app/credentials/ad-response-analysis-project-key2-9803513e2f0e.json"  # for docker
# SERVICE_ACCOUNT_FILE = "/home/vivek/DE-Project/Advertisement-Response-Analysis/credentials/ad-response-analysis-project-key2-9803513e2f0e.json"  # for without docker
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")  
RANGE_NAME = "Form Responses 1!A:S"  
LAST_PROCESSED_TIMESTAMP_FILE = "/app/tmp/last_processed_timestamp.txt"  # for without docker
# LAST_PROCESSED_TIMESTAMP_FILE = "/home/vivek/DE-Project/Advertisement-Response-Analysis/tmp/last_processed_timestamp.txt"  # for docker

# client = pymongo.MongoClient("mongodb://172.31.99.238:27017")
# client = pymongo.MongoClient("mongodb://127.0.0.1:27017") # for without docker
# client = pymongo.MongoClient("mongodb://host.docker.internal:27017") # for docker on windows
client = pymongo.MongoClient("mongodb://172.17.0.1:27017") # for docker on linux (ubuntu)

db = client["advertisement_response_analysis"]

def get_google_sheet_data():
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE)
    service = build("sheets", "v4", credentials=creds)

    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    values = result.get("values", [])

    headers = values[0]  
    data = values[1:] 
    df = pd.DataFrame(data, columns=headers)
    return df

def load_new_entries():
    df = get_google_sheet_data()

    last_processed_timestamp = None
    if os.path.exists(LAST_PROCESSED_TIMESTAMP_FILE):
        with open(LAST_PROCESSED_TIMESTAMP_FILE, "r") as f:
            last_processed_timestamp = f.read().strip()

    if last_processed_timestamp:
        new_entries = df[df["Timestamp"] > last_processed_timestamp]
    else:
        new_entries = df

    if not new_entries.empty:
        ad_id_map = {
            "Titan Watch Ad": 1001,
            "Muscleblaze Ad": 1002,
            "neemans sneakers Ad": 1003,
            "cometuniverse sneakers Ad": 1004,
            "Logitech mouse Ad": 1005,
            "Dell Laptop Ad": 1006,
            "Samsung Galaxy Zflip6 Ad": 1007,
            "H&M Ad": 1008,
            "Zapvi Mobile Cover Ad": 1009,
            "Lenskart Ad": 1010
        }

        respondent_id_counter = 1001

        for _, row in new_entries.iterrows():
            respondent_data = {
                "RespondentID": int(respondent_id_counter),
                "Age": row["What is your age ?"],
                "Gender": row["What is your gender ?"],
                "Location": row["Where are you located ?"],
                "Education Level": row["What is your highest level of education ?"],
                "Income Level": row["What is your yearly income ?"],
                "Occupation": row["What is your occupation ?"]
            }
            db["survey_respondents"].insert_one(respondent_data)

            ad_name = row["Select any one of the Ads you have seen."]
            ad_id = ad_id_map.get(ad_name, None)

            response_data = {
                "RespondentID": int(respondent_data["RespondentID"]),
                "AdID": ad_id,
                "Response_Date": row["Timestamp"],
                "ResponseType": row["What was your response to the Ad ?"],
                "PurchaseIntent": row["Did you intend to purchase the product/service after seeing the ad ?"],
                "Relevant": row["Did you find the ad relevant to you ?"],
                "Engagement_Time": row["How much time did you spend viewing the ad ?"],
                "Rating": row["How would you rate your interest in the product after viewing the ad ?"],
                "DeviceType": row["What device did you mostly see this Ad on ?"]
            }
            db["responses_to_ads"].insert_one(response_data)

            if row["Have you purchased the product / service ?"] == "Yes":
                purchase_data = {
                    "RespondentID": int(respondent_data["RespondentID"]),
                    "AdID": response_data["AdID"],
                    "InfluenceFactor": row["Was your purchase influenced by other factors ?"],
                    "PurchaseLocation": row["Where did you purchase the product ?"],
                    "AdInfluence": row["Did the advertisement influence your purchase decision ?"]
                }
                db["purchase_info"].insert_one(purchase_data)

            respondent_id_counter += 1

        print(f"Loaded {len(new_entries)} new entries to MongoDB")
        last_processed_timestamp = new_entries["Timestamp"].max()
        with open(LAST_PROCESSED_TIMESTAMP_FILE, "w") as f:
            f.write(last_processed_timestamp)

if __name__ == "__main__":
    # load_new_entries()
    pass