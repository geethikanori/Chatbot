#!/usr/bin/env python3
"""
Setup script for Marketing KPIs Analytics Dashboard
This script helps you set up the environment and run the application.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header():
    """Print welcome header"""
    print("=" * 60)
    print("🚀 Marketing KPIs Analytics Dashboard Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")
    print()

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        sys.exit(1)
    print()

def create_env_file():
    """Create .env file from template"""
    print("⚙️ Setting up environment configuration...")
    
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file already exists")
    else:
        print("📝 Creating .env file...")
        env_content = """# GCP Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json
GOOGLE_CLOUD_PROJECT=your-project-id
BIGQUERY_DATASET=your-dataset-name

# OpenAI Configuration (if using OpenAI instead of Vertex AI)
OPENAI_API_KEY=your-openai-api-key

# App Configuration
APP_TITLE=Marketing KPIs Analytics Dashboard
APP_DESCRIPTION=Interactive dashboard for exploring marketing KPIs using natural language queries
"""
        with open(env_file, "w") as f:
            f.write(env_content)
        print("✅ .env file created")
    print()

def check_gcp_setup():
    """Check GCP setup"""
    print("🔍 Checking GCP setup...")
    
    # Check if gcloud is installed
    try:
        subprocess.check_call(["gcloud", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print("✅ Google Cloud SDK is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Google Cloud SDK not found. Please install it from: https://cloud.google.com/sdk/docs/install")
    
    # Check authentication
    try:
        result = subprocess.run(["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=value(account)"], 
                              capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            print(f"✅ Authenticated as: {result.stdout.strip()}")
        else:
            print("⚠️  Not authenticated with gcloud. Run: gcloud auth login")
    except FileNotFoundError:
        print("⚠️  gcloud command not found")
    
    print()

def create_sample_config():
    """Create sample configuration for common marketing tables"""
    print("📋 Creating sample table configuration...")
    
    sample_config = {
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
                "revenue": "float64",
                "campaign_type": "string",
                "channel": "string"
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
                "acquisition_cost": "float64",
                "retention_rate": "float64"
            }
        },
        "ad_performance": {
            "description": "Individual ad performance data",
            "columns": {
                "ad_id": "string",
                "campaign_id": "string",
                "ad_name": "string",
                "date": "date",
                "impressions": "int64",
                "clicks": "int64",
                "cost": "float64",
                "conversions": "int64",
                "revenue": "float64"
            }
        }
    }
    
    with open("sample_table_config.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    print("✅ Sample configuration created: sample_table_config.json")
    print()

def print_next_steps():
    """Print next steps for the user"""
    print("🎉 Setup completed successfully!")
    print()
    print("📋 Next steps:")
    print("1. Update the .env file with your GCP credentials:")
    print("   - Set GOOGLE_APPLICATION_CREDENTIALS to your service account key file")
    print("   - Set GOOGLE_CLOUD_PROJECT to your project ID")
    print("   - Set BIGQUERY_DATASET to your dataset name")
    print()
    print("2. If using OpenAI instead of Vertex AI:")
    print("   - Set OPENAI_API_KEY in the .env file")
    print()
    print("3. Update config.py with your actual table schemas")
    print()
    print("4. Run the application:")
    print("   streamlit run app.py")
    print()
    print("5. Open your browser to http://localhost:8501")
    print()
    print("💡 For more help, check the README.md file")
    print("=" * 60)

def main():
    """Main setup function"""
    print_header()
    
    check_python_version()
    install_requirements()
    create_env_file()
    check_gcp_setup()
    create_sample_config()
    print_next_steps()

if __name__ == "__main__":
    main()

