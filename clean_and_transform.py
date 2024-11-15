import pandas as pd
import pymongo
from datetime import datetime

# client = pymongo.MongoClient("mongodb://172.31.99.238:27017")
# client = pymongo.MongoClient("mongodb://127.0.0.1:27017") # for without docker
# clinet = pymongo.MongoClient("mongodb://host.docker.internal:27017") # for docker on windows
client = pymongo.MongoClient("mongodb://172.17.0.1:27017") # for docker on linux (ubuntu)

db = client["advertisement_response_analysis"]
db_tf = client["ad_response_analysis_tf"]

def transform_response_date(df):
    def convert_to_datetime(date_value):
        if isinstance(date_value, datetime):
            return date_value.strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            parsed_date = pd.to_datetime(date_value, errors='coerce')
            if pd.notna(parsed_date):
                return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Error parsing date: {e}")
        
        return date_value  

    df['Response_Date'] = df['Response_Date'].apply(convert_to_datetime)

    for _, row in df.iterrows():
        # db["responses_to_ads"].update_one(
        #     {"_id": row["_id"]},
        #     {"$set": {"Response_Date": row["Response_Date"]}}
        # )

        # Insert into the new database
        db_tf["responses_to_ads"].update_one(
            {"_id": row["_id"]},
            {"$set": row.to_dict()},
            upsert=True
        )

    return df

def transform_engagement_time_and_rating(df):
    df['Rating'] = df['Rating'].astype(int)

    is_numeric_time = pd.to_numeric(df['Engagement_Time'], errors='coerce').notna()
    not_already_range = ~df['Engagement_Time'].astype(str).str.contains('-')

    df.loc[is_numeric_time & not_already_range, 'Engagement_Time'] = df.loc[is_numeric_time & not_already_range, 'Engagement_Time'] / 10

    bins = [0, 10, 20, 30, 40, 60, float('inf')]
    labels = ['0 - 10', '10 - 20', '20 - 30', '30 - 40', '40 - 60', '>60']

    df.loc[is_numeric_time & not_already_range, 'Engagement_Time'] = pd.cut(
        df.loc[is_numeric_time & not_already_range, 'Engagement_Time'], bins=bins, labels=labels
    )

    for _, row in df.iterrows():
        # db["responses_to_ads"].update_one(
        #     {"_id": row["_id"]},
        #     {"$set": {"Engagement_Time": row["Engagement_Time"], "Rating": row["Rating"]}}
        # )

        # Insert into the new database
        db_tf["responses_to_ads"].update_one(
            {"_id": row["_id"]},
            {"$set": row.to_dict()},
            upsert=True
        )

    return df

def transform_age(df):
    def convert_age(value):
        if '-' in value or '>' in value or '<' in value:
            return value
        age = int(value)
        if age < 18:
            return "0 - 18"
        elif age < 30:
            return "18 - 30"
        elif age < 45:
            return "30 - 45"
        elif age < 60:
            return "45 - 60"
        else:
            return ">60"

    df['Age'] = df['Age'].apply(lambda x: convert_age(str(x)))

    for _, row in df.iterrows():
        # db["survey_respondents"].update_one(
        #     {"_id": row["_id"]},
        #     {"$set": {"Age": row["Age"]}}
        # )

        # Insert into the new database
        db_tf["survey_respondents"].update_one(
            {"_id": row["_id"]},
            {"$set": row.to_dict()},
            upsert=True
        )

    return df

def transform_education_level(df):
    
    df['Education Level'] = df['Education Level'].str.lower()

    df['Education Level'] = df['Education Level'].replace({
        'high school': 'High School',
        'Highschool': 'High School',
        'bachelor\'s degree': 'Bachelors',
        'master\'s degree': 'Masters',
        'highschool': 'High School',
        'bachelor': 'Bachelors',
        'master': 'Masters'
    })

    df['Education Level'] = df['Education Level'].str.lower()

    for _, row in df.iterrows():
        # db["survey_respondents"].update_one(
        #     {"_id": row["_id"]},
        #     {"$set": {"Education Level": row["Education Level"]}}
        # )

        # Insert into the new database
        db_tf["survey_respondents"].update_one(
            {"_id": row["_id"]},
            {"$set": row.to_dict()},
            upsert=True
        )
    
    return df

def transform_income_level(df):
    def convert_income(value):
        if '-' in value or '>' in value or '<' in value:
            return value
        income = int(value)
        if income < 20000:
            return "<20k"
        elif income < 50000:
            return "20k-50k"
        elif income < 100000:
            return "50k-100k"
        else:
            return ">100k"

    df['Income Level'] = df['Income Level'].apply(lambda x: convert_income(str(x)))
    
    for _, row in df.iterrows():
        # db["survey_respondents"].update_one(
        #     {"_id": row["_id"]},
        #     {"$set": {"Income Level": row["Income Level"]}}
        # )

        # Insert into the new database
        db_tf["survey_respondents"].update_one(
            {"_id": row["_id"]},
            {"$set": row.to_dict()},
            upsert=True
        )

    return df

def drop_null_and_duplicates(df):
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def clean_advertisement_info(df):
    df = drop_null_and_duplicates(df)

    df['AdDuration'] = df.apply(lambda row: row['AdDuration'] if row['AdType'] == 'Video' else 0, axis=1)
    df['AdCost'] = df['AdCost'].replace('[\$,]', '', regex=True).astype(float).astype(int) 
    df['PurchaseAmount'] = df['PurchaseAmount'].astype(int)  

    for _, row in df.iterrows():
        update_data = row.to_dict()
        if "_id" in update_data:
            del update_data["_id"]

        # db["advertisement_info"].update_one(
        #     {"AdID": row["AdID"]},
        #     {"$set": update_data},
        #     upsert=True
        # )

        # Insert into the new database
        db_tf["advertisement_info"].update_one(
            {"AdID": row["AdID"]},
            {"$set": update_data},
            upsert=True
        )

    return df

def clean_demographic_data(df):
    df = drop_null_and_duplicates(df)

    df.drop(columns=['Occupation'], inplace=True, errors='ignore')

    for _, row in df.iterrows():
        update_data = row.to_dict()
        if "_id" in update_data:
            del update_data["_id"]

        # db["demographic_data"].update_one(
        #     {"DemographicID": row["DemographicID"]},
        #     {"$set": update_data},
        #     upsert=True
        # )

        # Insert into the new database
        db_tf["demographic_data"].update_one(
            {"DemographicID": row["DemographicID"]},
            {"$set": update_data},
            upsert=True
        )

    return df

def clean_ad_demographic_link(df):
    df = drop_null_and_duplicates(df)

    for _, row in df.iterrows():
        update_data = row.to_dict()
        if "_id" in update_data:
            del update_data["_id"]

        # db["ad_demographic_link"].update_one(
        #     {"AdID": row["AdID"], "DemographicID": row["DemographicID"]},
        #     {"$set": update_data},
        #     upsert=True
        # )

        # Insert into the new database
        db_tf["ad_demographic_link"].update_one(
            {"AdID": row["AdID"], "DemographicID": row["DemographicID"]},
            {"$set": update_data},
            upsert=True
        )

    return df

def clean_purchase_info(df):
    df = drop_null_and_duplicates(df)

    for _, row in df.iterrows():
        update_data = row.to_dict()
        if "_id" in update_data:
            del update_data["_id"]

        # db["purchase_info"].update_one(
        #     {"RespondentID": row["RespondentID"], "AdID": row["AdID"]},
        #     {"$set": update_data},
        #     upsert=True
        # )

        # Insert into the new database
        db_tf["purchase_info"].update_one(
            {"RespondentID": row["RespondentID"], "AdID": row["AdID"]},
            {"$set": update_data},
            upsert=True
        )

    return df

def get_new_entries(collection_name):
    # Get the IDs of already processed entries
    processed_ids = db_tf[collection_name].distinct("_id")
    
    # Fetch new entries from the original database
    new_entries = db[collection_name].find({"_id": {"$nin": processed_ids}})
    
    return pd.DataFrame(list(new_entries))

def clean_and_normalize_data():
    respondents_df = get_new_entries("survey_respondents")
    responses_df = get_new_entries("responses_to_ads")
    purchases_df = get_new_entries("purchase_info")
    advertisement_info_df = get_new_entries("advertisement_info")
    ad_demographic_link_df = get_new_entries("ad_demographic_link")
    demographic_data_df = get_new_entries("demographic_data")

    if not respondents_df.empty:
        respondents_df.dropna(inplace=True)
        respondents_df = transform_age(respondents_df)
        respondents_df = transform_education_level(respondents_df)
        respondents_df = transform_income_level(respondents_df)

    if not responses_df.empty:
        responses_df.dropna(inplace=True)
        responses_df = transform_engagement_time_and_rating(responses_df)
        responses_df = transform_response_date(responses_df)

    if not purchases_df.empty:
        purchases_df.dropna(inplace=True)
        purchases_df = clean_purchase_info(purchases_df)

    if not advertisement_info_df.empty:
        advertisement_info_df = clean_advertisement_info(advertisement_info_df)

    if not demographic_data_df.empty:
        demographic_data_df = clean_demographic_data(demographic_data_df)

    if not ad_demographic_link_df.empty:
        ad_demographic_link_df = clean_ad_demographic_link(ad_demographic_link_df)

    print("Data cleaned and normalized.")

def calculate_metrics():
    responses_df = pd.DataFrame(list(db["responses_to_ads"].find()))
    purchases_df = pd.DataFrame(list(db["purchase_info"].find()))

    ad_views = responses_df['AdID'].value_counts()
    ad_clicks = responses_df[responses_df['ResponseType'] == 'Clicked']['AdID'].value_counts()
    # print(ad_clicks)
    ctr_df = (ad_clicks / ad_views).fillna(0).to_frame(name="Click_Through_Rate")

    conversions = purchases_df['AdID'].value_counts()
    conversion_rate_df = (conversions / ad_views).fillna(0).to_frame(name="Conversion_Rate")

    mode_engagement_time = responses_df.groupby('AdID')['Engagement_Time'].agg(lambda x: x.mode().iloc[0] if not x.mode().empty else None)
    mode_engagement_df = mode_engagement_time.to_frame(name="Mode_Engagement_Time").reset_index()

    metrics_df = ctr_df.join(conversion_rate_df).reset_index().rename(columns={'index': 'AdID'})
    metrics_df = metrics_df.merge(mode_engagement_df, on='AdID', how='left')

    for _, row in metrics_df.iterrows():
        db["ad_metrics"].update_one(
            {"AdID": row["AdID"]},
            {"$set": {
                "Click_Through_Rate": row["Click_Through_Rate"],
                "Conversion_Rate": row["Conversion_Rate"],
                "Mode_Engagement_Time": row["Mode_Engagement_Time"]
            }},
            upsert=True
        )

        # Insert into the new database
        db_tf["ad_metrics"].update_one(
            {"AdID": row["AdID"]},
            {"$set": {
                "Click_Through_Rate": row["Click_Through_Rate"],
                "Conversion_Rate": row["Conversion_Rate"],
                "Mode_Engagement_Time": row["Mode_Engagement_Time"]
            }},
            upsert=True
        )

    print("Metrics calculated and stored in MongoDB.")

if __name__ == "__main__":
    clean_and_normalize_data()
    calculate_metrics()
