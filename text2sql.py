import os
import openai
from langchain_community.llms import OpenAI
from vertexai import init as vertexai_init
from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import streamlit as st
from config import Config

class Text2SQLGenerator:
    def __init__(self, use_vertex_ai=True):
        self.use_vertex_ai = use_vertex_ai
        self.llm = None
        self.chain = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the language model"""
        try:
            if self.use_vertex_ai:
                # Use Google Vertex AI
                # Ensure Vertex AI is initialized with project/region
                if not Config.GOOGLE_CLOUD_PROJECT:
                    raise ValueError("GOOGLE_CLOUD_PROJECT is not set. Set env var or Config.GOOGLE_CLOUD_PROJECT.")
                # Default region can be customized if your resources live elsewhere
                vertexai_init(project=Config.GOOGLE_CLOUD_PROJECT, location=os.getenv("VERTEX_AI_LOCATION", "us-central1"))
                self.llm = VertexAI(
                    model_name="text-bison@001",
                    temperature=0.1,
                    max_output_tokens=1024
                )
            else:
                # Use OpenAI
                if not Config.OPENAI_API_KEY:
                    st.error("OpenAI API key not found. Please set OPENAI_API_KEY in your environment.")
                    return
                
                openai.api_key = Config.OPENAI_API_KEY
                self.llm = OpenAI(
                    model_name="gpt-3.5-turbo",
                    temperature=0.1,
                    max_tokens=1024
                )
            
            self._create_chain()
            st.success("✅ Text-to-SQL model initialized successfully!")
            
        except Exception as e:
            st.error(f"❌ Failed to initialize text-to-SQL model: {str(e)}")
    
    def _create_chain(self):
        """Create the LLM chain for text-to-SQL conversion"""
        prompt_template = PromptTemplate(
            input_variables=["question", "table_schemas", "sample_queries"],
            template="""
You are an expert SQL analyst specializing in BigQuery. Convert the user's natural language question into a BigQuery SQL query.

Available tables and their schemas:
{table_schemas}

Sample queries for reference:
{sample_queries}

User Question: {question}

Instructions:
1. Generate a valid BigQuery SQL query that answers the user's question
2. Use proper BigQuery syntax and functions
3. Include appropriate WHERE clauses for filtering
4. Add LIMIT clause if the result might be large (max 1000 rows)
5. Use descriptive column aliases when needed
6. Only return the SQL query, no explanations

SQL Query:
"""
        )
        
        self.chain = LLMChain(llm=self.llm, prompt=prompt_template)
    
    def generate_sql(self, question, table_schemas, sample_queries=""):
        """Generate SQL query from natural language question"""
        try:
            if not self.chain:
                st.error("Text-to-SQL model not initialized")
                return None
            
            # Format table schemas for the prompt
            schemas_text = self._format_table_schemas(table_schemas)
            
            # Generate SQL query
            result = self.chain.run(
                question=question,
                table_schemas=schemas_text,
                sample_queries=sample_queries
            )
            
            # Clean up the result (remove any extra text)
            sql_query = result.strip()
            if sql_query.startswith("```sql"):
                sql_query = sql_query[6:]
            if sql_query.endswith("```"):
                sql_query = sql_query[:-3]
            
            return sql_query.strip()
            
        except Exception as e:
            st.error(f"❌ Failed to generate SQL query: {str(e)}")
            return None
    
    def _format_table_schemas(self, table_schemas):
        """Format table schemas for the prompt"""
        schemas_text = ""
        for table_name, schema_info in table_schemas.items():
            schemas_text += f"\nTable: {table_name}\n"
            schemas_text += f"Description: {schema_info.get('description', 'No description')}\n"
            schemas_text += "Columns:\n"
            
            for col_name, col_type in schema_info.get('columns', {}).items():
                schemas_text += f"  - {col_name}: {col_type}\n"
            
            schemas_text += "\n"
        
        return schemas_text
    
    def get_sample_queries(self):
        """Return sample queries for common marketing KPI questions"""
        return """
-- Sample Marketing KPI Queries:

-- 1. Campaign Performance Analysis
SELECT 
    campaign_name,
    SUM(spend) as total_spend,
    SUM(impressions) as total_impressions,
    SUM(clicks) as total_clicks,
    SUM(conversions) as total_conversions,
    ROUND(SUM(clicks) / SUM(impressions) * 100, 2) as ctr_percentage,
    ROUND(SUM(conversions) / SUM(clicks) * 100, 2) as conversion_rate,
    ROUND(SUM(revenue) / SUM(spend), 2) as roas
FROM marketing_campaigns 
WHERE start_date >= '2024-01-01'
GROUP BY campaign_name
ORDER BY total_revenue DESC;

-- 2. Monthly Customer Metrics
SELECT 
    DATE_TRUNC(date, MONTH) as month,
    SUM(new_customers) as new_customers,
    SUM(returning_customers) as returning_customers,
    AVG(churn_rate) as avg_churn_rate,
    AVG(lifetime_value) as avg_ltv,
    AVG(acquisition_cost) as avg_cac
FROM customer_metrics 
WHERE date >= '2024-01-01'
GROUP BY month
ORDER BY month;

-- 3. Top Performing Campaigns by ROAS
SELECT 
    campaign_name,
    SUM(revenue) as total_revenue,
    SUM(spend) as total_spend,
    ROUND(SUM(revenue) / SUM(spend), 2) as roas
FROM marketing_campaigns 
WHERE start_date >= '2024-01-01'
GROUP BY campaign_name
HAVING SUM(spend) > 1000
ORDER BY roas DESC
LIMIT 10;
"""
