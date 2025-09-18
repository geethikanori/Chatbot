import pandas as pd
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import streamlit as st
from config import Config

class BigQueryClient:
    def __init__(self):
        self.client = None
        self.project_id = Config.GOOGLE_CLOUD_PROJECT
        self.dataset_id = Config.BIGQUERY_DATASET
        
    def initialize_client(self):
        """Initialize BigQuery client with authentication"""
        try:
            if Config.GOOGLE_APPLICATION_CREDENTIALS:
                self.client = bigquery.Client.from_service_account_json(
                    Config.GOOGLE_APPLICATION_CREDENTIALS,
                    project=self.project_id
                )
            else:
                # Use default credentials (e.g., from gcloud auth)
                self.client = bigquery.Client(project=self.project_id)
            
            st.success("✅ BigQuery client initialized successfully!")
            return True
        except Exception as e:
            st.error(f"❌ Failed to initialize BigQuery client: {str(e)}")
            return False
    
    def get_table_schema(self, table_name):
        """Get schema information for a specific table"""
        try:
            if not self.client:
                return None
                
            table_ref = self.client.dataset(self.dataset_id).table(table_name)
            table = self.client.get_table(table_ref)
            
            schema_info = {
                "description": table.description or "No description available",
                "columns": {}
            }
            
            for field in table.schema:
                schema_info["columns"][field.name] = field.field_type
            
            return schema_info
        except NotFound:
            st.warning(f"Table '{table_name}' not found in dataset '{self.dataset_id}'")
            return None
        except Exception as e:
            st.error(f"Error getting schema for table '{table_name}': {str(e)}")
            return None
    
    def get_all_tables(self):
        """Get list of all tables in the dataset"""
        try:
            if not self.client:
                return []
                
            dataset_ref = self.client.dataset(self.dataset_id)
            tables = list(self.client.list_tables(dataset_ref))
            
            table_list = []
            for table in tables:
                table_info = {
                    "table_id": table.table_id,
                    "description": table.description or "No description available"
                }
                table_list.append(table_info)
            
            return table_list
        except Exception as e:
            st.error(f"Error listing tables: {str(e)}")
            return []
    
    def execute_query(self, query, max_results=None):
        """Execute a SQL query and return results as DataFrame"""
        try:
            if not self.client:
                st.error("BigQuery client not initialized")
                return None
            
            # Set query job configuration
            job_config = bigquery.QueryJobConfig()
            if max_results:
                job_config.maximum_bytes_billed = max_results * 1000  # Rough estimate
            
            # Execute query
            query_job = self.client.query(query, job_config=job_config)
            
            # Convert to DataFrame
            df = query_job.to_dataframe()
            
            return df
            
        except Exception as e:
            st.error(f"❌ Query execution failed: {str(e)}")
            return None
    
    def validate_query(self, query):
        """Validate SQL query syntax without executing"""
        try:
            if not self.client:
                return False, "BigQuery client not initialized"
            
            # Create a dry run query job
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(query, job_config=job_config)
            
            return True, "Query is valid"
            
        except Exception as e:
            return False, f"Query validation failed: {str(e)}"

