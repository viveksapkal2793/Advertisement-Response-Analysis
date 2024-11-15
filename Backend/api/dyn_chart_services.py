from django.conf import settings
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io 
import base64
import plotly.express as px

def get_chart_names_list():
    chart_names = [
        {"value": "ad_platform_type_vs_ad_type", "label": "Ad Platform Type and Ad Type"},
        {"value": "purchase_location_vs_influence_factor", "label": "Purchase Location and Influence Factor"},
        {"value": "engagement_time_vs_rating", "label": "Engagement Time and Rating"},
        {"value": "response_type_vs_purchase_intent", "label": "Response Type and Purchase Intent"},
        {"value": "response_date_vs_response_count", "label": "Number of Responses Over Time"},
        {"value": "age_range_distribution", "label": "Number of Respondents in Various Age Ranges"},
        {"value": "income_level_vs_location", "label": "Income Level and Location"},
    ]
    return chart_names

def fetch_data_from_mongo(collection_name):
    collection = settings.MONGO_DB[collection_name]
    data = list(collection.find({}, {"_id": 0}))  # Exclude the MongoDB ID from the results
    return data

def generate_summary_from_metrics(data_description, metrics):
    """Generate a summary from metrics using a hard-coded template."""
    summary = f"Summary for {data_description}:\n\n"
    
    for column, metric in metrics.items():
        summary += f"Column: {column}\n"
        if 'mean' in metric:
            summary += f"  - Mean: {metric['mean']:.2f}\n"
            summary += f"  - Median: {metric['median']:.2f}\n"
            summary += f"  - Standard Deviation: {metric['std']:.2f}\n"
        else:
            summary += f"  - Unique Values: {metric['unique_values']}\n"
            summary += f"  - Value Counts: {metric['value_counts']}\n"
        summary += "\n"
    
    summary += "Key Insights:\n"
    summary += "  - The data shows significant patterns and trends.\n"
    summary += "  - Further analysis is recommended to derive actionable insights.\n"
    
    return summary

def create_analysis_metrics(df, columns):
    """Create analysis metrics based on column types"""
    metrics = {}
    
    for col in columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            metrics[col] = {
                'mean': df[col].mean(),
                'median': df[col].median(),
                'std': df[col].std()
            }
        else:
            metrics[col] = {
                'value_counts': df[col].value_counts().to_dict(),
                'unique_values': len(df[col].unique())
            }
    
    return metrics

def create_ad_platform_type_chart():
    data = fetch_data_from_mongo("advertisement_info")
    df = pd.DataFrame(data)

    # Create the stacked bar plot
    pivot_df = df.pivot_table(index='AdPlatformType', columns='AdType', aggfunc='size', fill_value=0)
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis')
    plt.title('Ad Platform Type and Ad Type')
    plt.xlabel('Ad Platform Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Ad Type', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['AdPlatformType', 'AdType']
    metrics = create_analysis_metrics(df, columns)
    summary = generate_summary_from_metrics('Ad Platform Type and Ad Type', metrics)
    return buf, summary

def create_purchase_location_chart():
    data = fetch_data_from_mongo("purchase_info")
    df = pd.DataFrame(data)

    # Create the stacked bar plot
    pivot_df = df.pivot_table(index='PurchaseLocation', columns='InfluenceFactor', aggfunc='size', fill_value=0)
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis')
    plt.title('Purchase Location and Influence Factor')
    plt.xlabel('Purchase Location')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Influence Factor', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['PurchaseLocation', 'InfluenceFactor']
    metrics = create_analysis_metrics(df, columns)
    summary = generate_summary_from_metrics('Purchase Location and Influence Factor', metrics)

    return buf, summary

def create_engagement_time_chart():
    data = fetch_data_from_mongo("responses_to_ads")
    df = pd.DataFrame(data)

    # Create the stacked bar plot
    pivot_df = df.pivot_table(index='Engagement_Time', columns='Rating', aggfunc='size', fill_value=0)
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis')
    plt.title('Engagement Time and Rating')
    plt.xlabel('Engagement Time')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Rating', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['Engagement_Time', 'Rating']
    metrics = create_analysis_metrics(df, columns)
    summary = generate_summary_from_metrics('Engagement Time and Rating', metrics)
    return buf, summary

def create_response_type_chart():
    data = fetch_data_from_mongo("responses_to_ads")
    df = pd.DataFrame(data)

    # Create the stacked bar plot
    pivot_df = df.pivot_table(index='ResponseType', columns='PurchaseIntent', aggfunc='size', fill_value=0)
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis')
    plt.title('Response Type and Purchase Intent')
    plt.xlabel('Response Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Purchase Intent', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['ResponseType', 'PurchaseIntent']
    metrics = create_analysis_metrics(df, columns)
    summary = generate_summary_from_metrics('Response Type and Purchase Intent', metrics)
    return buf, summary

def create_response_date_chart():
    data = fetch_data_from_mongo("responses_to_ads")
    df = pd.DataFrame(data)

    # Convert date to datetime
    df['Response_Date'] = pd.to_datetime(df['Response_Date'])

    # Create the line chart
    df.set_index('Response_Date').resample('D').size().plot(kind='line', figsize=(12, 8))
    plt.title('Number of Responses Over Time')
    plt.xlabel('Date')
    plt.ylabel('Number of Responses')
    plt.xticks(rotation=45)
    plt.legend('')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['Response_Date']
    metrics = create_analysis_metrics(df, columns)
    summary = "Summary for Number of Responses Over Time:\n\nKey Insights:- The data shows significant patterns and trends.\n- Further analysis is recommended to derive actionable insights."

    return buf, summary

def create_age_range_pie_chart():
    data = fetch_data_from_mongo("survey_respondents")
    df = pd.DataFrame(data)

    # Create the pie chart using Plotly
    fig = px.pie(df, names='Age', title='Number of Respondents in Various Age Ranges', color_discrete_sequence=px.colors.sequential.Viridis)
    fig.update_traces(textposition='inside', textinfo='percent+label')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    fig.write_image(buf, format='png')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['Age']
    metrics = create_analysis_metrics(df, columns)
    summary = generate_summary_from_metrics('Number of Respondents in Various Age Ranges', metrics)

    return buf, summary

def create_income_range_chart():
    data = fetch_data_from_mongo("survey_respondents")
    df = pd.DataFrame(data)

    # Create the stacked bar plot
    pivot_df = df.pivot_table(index='Income Level', columns='Location', aggfunc='size', fill_value=0)
    pivot_df.plot(kind='bar', stacked=True, figsize=(12, 8), colormap='viridis')
    plt.title('Income Level and Location')
    plt.xlabel('Income Level')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.legend(title='Location', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Save the plot to a BytesIO object
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    plt.close()

    # Generate metrics and summary
    columns = ['Income Level', 'Location']
    metrics = create_analysis_metrics(df, columns)
    summary = generate_summary_from_metrics('Income Level and Location', metrics)

    return buf, summary

def create_custom_chart(chart_type):
    chart_mapping = {
        "ad_platform_type_vs_ad_type": create_ad_platform_type_chart,
        "purchase_location_vs_influence_factor": create_purchase_location_chart,
        "engagement_time_vs_rating": create_engagement_time_chart,
        "response_type_vs_purchase_intent": create_response_type_chart,
        "response_date_vs_response_count": create_response_date_chart,
        "age_range_distribution": create_age_range_pie_chart,
        "income_level_vs_location": create_income_range_chart,
    }

    if chart_type in chart_mapping:
        buf, summary = chart_mapping[chart_type]()
        chart = [
                    {
                        "title": chart_mapping[chart_type].__name__.replace('_', ' ').title(),
                        "image": base64.b64encode(buf.getvalue()).decode('utf-8'),
                        "summary": summary,
                    }
                ]
        return chart
    else:
        raise ValueError(f"Unknown chart type: {chart_type}")