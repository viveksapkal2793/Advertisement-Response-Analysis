import pandas as pd
import json
import joblib

# Define the categorical values for each column
INCOME_LEVELS = ['20k-50k', '50k-100k', '<20k', '>100k']
EDUCATION_LEVELS = ['Bachelors', 'High School', 'Masters', 'PhD']
OCCUPATIONS = ['Artist', 'Doctor', 'Engineer', 'Marketing Manager', 'Salesperson', 'Teacher']
PLATFORM_NAMES = {
    ["News Channel", "Movie Channel", "Sports Channel", "Music Channel", "Kids Channel", "Google", "Bing", "Yahoo", "Facebook", "YouTube", "Instagram", "Twitter", "LinkedIn", "Snapchat", "Threads","Netflix", "Amazon Prime", "Hotstar", "JioTV", "Zee5"],
}
PLATFORM_TYPES1 = ["TV", "Search Engine", "Social Media", "Streaming"]
PLATFORM_TYPES = ['Amazon Prime', 'Bing', 'Facebook', 'Google', 'Hotstar', 'Instagram', 'JioTV', 'Kids Channel', 'LinkedIn', 'Movie Channel', 'Music Channel', 'Netflix', 'News Channel', 'Snapchat', 'Sports Channel', 'Threads', 'Twitter', 'Yahoo', 'YouTube', 'Zee5']
AGE_RANGES = ['18-30', '30-45', '45-60', '<18' '>60']
GENDER_OPTIONS = ['Female', 'Male', 'Other']
LOCATION_OPTIONS = ['Rural', 'Sub-urban', 'Urban']
TOPICS = ['Automobile', 'Education', 'Entertainment', 'Fashion', 'Finance', 'Food', 'Healthcare', 'Political', 'Real Estate', 'Sports', 'Technology', 'Travel']
AD_TYPES = ["Video", "Banner", "Text"]

# Create a dictionary to map column names to their categorical values
categorical_values = {
    "Income Level": INCOME_LEVELS,
    "Education Level": EDUCATION_LEVELS,
    "Occupation": OCCUPATIONS,
    "AdPlatformType": PLATFORM_TYPES,
    "Age": AGE_RANGES,
    "Gender": GENDER_OPTIONS,
    "Location": LOCATION_OPTIONS,
    "AdTopic": TOPICS,
}

def get_dropdown_values():
    dropdown_values = {
        "AdTopic": TOPICS,
        "AdPlatformType": PLATFORM_TYPES1,
        "AdPlatformName": PLATFORM_NAMES,  # Assuming you have a list of platform names
        "AdType": AD_TYPES,
        "Age": AGE_RANGES,
        "Gender": GENDER_OPTIONS,
        "Education_Level": EDUCATION_LEVELS,
        "Income_Level": INCOME_LEVELS,
        "Occupation": OCCUPATIONS,
        "Location": LOCATION_OPTIONS
    }
    return dropdown_values

def predictions_cr_ctr(input_data):
    # Convert JSON input to DataFrame
    data = json.loads(input_data)
    df = pd.DataFrame(data)

    # Convert specified columns to integers
    df['AdCost'] = df['AdCost'].astype(int)
    df['PurchaseAmount'] = df['PurchaseAmount'].astype(int)
    df['ModeEngagementTime'] = df['ModeEngagementTime'].astype(int)

    # One-hot encode the specified columns
    encoded_df = pd.get_dummies(df, columns=['AdPlatformName', 'AdPlatformType', 'AdTopic', 'AdType'])

    # Load the models
    model_cr = joblib.load('models/model_cr.joblib')
    model_ctr = joblib.load('models/model_ctr.joblib')

    # Make predictions
    cr_predictions = model_cr.predict(encoded_df)
    ctr_predictions = model_ctr.predict(encoded_df)

    # Create response dictionary
    response = {
        'cr_predictions': cr_predictions.tolist(),
        'ctr_predictions': ctr_predictions.tolist()
    }

    # Convert response to JSON
    response_json = json.dumps(response)

    return response_json

def predictions_decision(input_data):
    # Convert JSON input to DataFrame
    data = json.loads(input_data)
    df = pd.DataFrame(data)

    # Replace strings with their corresponding index numbers
    for column, values in categorical_values.items():
        if column in df.columns:
            df[column] = df[column].apply(lambda x: values.index(x) if x in values else x)

    # Add a column 'Response_Type' with value 0
    df['Response_Type'] = 0

        # Load the decision tree model
    decision_tree = joblib.load('models/decision_tree.joblib')

    # Predict the response
    predictions = decision_tree.predict(df)

    # Convert the predictions to the corresponding topics
    predicted_topics = [TOPICS[pred] for pred in predictions]

    # Create response dictionary
    response = {
        'predicted_topics': predicted_topics
    }
    return response