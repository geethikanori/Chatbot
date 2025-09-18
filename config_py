import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # GCP Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    # Default to Brand Health project if env var not provided
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT', 'brand-health-gen-ai-prod-39df')
    # Default dataset for Brand Health project
    BIGQUERY_DATASET = os.getenv('BIGQUERY_DATASET', 'crm_kpi_dataset')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # App Configuration
    APP_TITLE = os.getenv('APP_TITLE', 'Marketing KPIs Analytics Dashboard')
    APP_DESCRIPTION = os.getenv('APP_DESCRIPTION', 'Interactive dashboard for exploring marketing KPIs using natural language queries')
    
    # Text-to-SQL Configuration
    MAX_QUERY_RESULTS = 1000
    QUERY_TIMEOUT = 30  # seconds
    
    # Sample table schemas for context (update with your actual tables)
    SAMPLE_TABLES = {
        "marketing_campaigns": {
            "description": "Marketing campaign performance data",
            "columns": {
                "campaign_id": "string",
                "campaign_name": "string", 
                "start_date": "date",
                "end_date": "date",
                "budget": "float64",
                "spend": "float64",
                "impressions": "int64",
                "clicks": "int64",
                "conversions": "int64",
                "revenue": "float64"
            }
        },
        "customer_metrics": {
            "description": "Customer acquisition and retention metrics",
            "columns": {
                "date": "date",
                "new_customers": "int64",
                "returning_customers": "int64",
                "churn_rate": "float64",
                "lifetime_value": "float64",
                "acquisition_cost": "float64"
            }
        }
    }

