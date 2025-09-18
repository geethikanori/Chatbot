import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sqlparse
from bigquery_client import BigQueryClient
from text2sql import Text2SQLGenerator
from config import Config

# Page configuration
st.set_page_config(
    page_title=Config.APP_TITLE,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e, #2ca02c);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .query-box {
        background: linear-gradient(135deg, #f0f2f6 0%, #e8f4fd 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        animation: slideInLeft 0.5s ease-out;
    }
    
    .query-box:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .result-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e8f5e8 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #28a745;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideInRight 0.5s ease-out;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .error-box {
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        border-left: 5px solid #dc3545;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e9ecef;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
    }
    
    .interactive-button {
        background: linear-gradient(45deg, #1f77b4, #ff7f0e);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
        cursor: pointer;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .interactive-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #1f77b4;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .success-message {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        animation: slideInDown 0.5s ease-out;
    }
    
    @keyframes slideInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
    }
    
    .table-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border-left: 3px solid #1f77b4;
    }
    
    .table-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .query-history-item {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 3px solid #ff7f0e;
        transition: all 0.3s ease;
    }
    
    .query-history-item:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .progress-bar {
        width: 100%;
        height: 4px;
        background-color: #e9ecef;
        border-radius: 2px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        border-radius: 2px;
        animation: progress 2s ease-in-out;
    }
    
    @keyframes progress {
        from { width: 0%; }
        to { width: 100%; }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'bq_client' not in st.session_state:
        st.session_state.bq_client = BigQueryClient()
    
    if 'text2sql' not in st.session_state:
        st.session_state.text2sql = Text2SQLGenerator(use_vertex_ai=True)
    
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    
    if 'table_schemas' not in st.session_state:
        st.session_state.table_schemas = {}

def load_table_schemas():
    """Load table schemas from BigQuery"""
    if not st.session_state.bq_client.client:
        return
    
    with st.spinner("Loading table schemas..."):
        tables = st.session_state.bq_client.get_all_tables()
        
        for table in tables:
            table_name = table['table_id']
            schema_info = st.session_state.bq_client.get_table_schema(table_name)
            if schema_info:
                st.session_state.table_schemas[table_name] = schema_info

def display_query_results(df, query):
    """Display query results with visualizations"""
    if df is None or df.empty:
        st.warning("No results found for this query.")
        return
    
    # Display basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Rows", len(df))
    with col2:
        st.metric("Columns", len(df.columns))
    with col3:
        st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    
    # Display data
    st.subheader("📊 Query Results")
    st.dataframe(df, use_container_width=True)
    
    # Auto-generate visualizations based on data types
    generate_visualizations(df)

def generate_visualizations(df):
    """Auto-generate relevant visualizations with enhanced interactivity"""
    st.subheader("📈 Interactive Visualizations")
    
    # Get numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    string_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
    
    if len(numeric_cols) > 0:
        # Create tabs for different visualization types
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📈 Charts", "🔍 Analysis", "🎨 Custom"])
        
        with tab1:
            # Enhanced summary statistics
            st.subheader("📊 Data Summary")
            
            # Quick metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Numeric Columns", len(numeric_cols))
            with col3:
                st.metric("Date Columns", len(date_cols))
            with col4:
                st.metric("Text Columns", len(string_cols))
            
            # Summary statistics with better formatting
            st.subheader("Statistical Summary")
            summary_df = df[numeric_cols].describe()
            st.dataframe(summary_df, use_container_width=True)
            
            # Data quality insights
            st.subheader("🔍 Data Quality Insights")
            quality_col1, quality_col2 = st.columns(2)
            
            with quality_col1:
                missing_data = df.isnull().sum()
                if missing_data.sum() > 0:
                    st.warning(f"⚠️ Missing values detected in {missing_data[missing_data > 0].count()} columns")
                    st.dataframe(missing_data[missing_data > 0].to_frame("Missing Values"))
                else:
                    st.success("✅ No missing values found")
            
            with quality_col2:
                duplicate_rows = df.duplicated().sum()
                if duplicate_rows > 0:
                    st.warning(f"⚠️ {duplicate_rows} duplicate rows found")
                else:
                    st.success("✅ No duplicate rows found")
        
        with tab2:
            st.subheader("📈 Interactive Charts")
            
            # Chart type selection
            chart_type = st.selectbox(
                "Select Chart Type:",
                ["Scatter Plot", "Line Chart", "Bar Chart", "Histogram", "Box Plot", "Heatmap"]
            )
            
            if chart_type == "Scatter Plot" and len(numeric_cols) >= 2:
                col1, col2, col3 = st.columns(3)
                with col1:
                    x_col = st.selectbox("X-axis", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, key="scatter_y")
                with col3:
                    color_col = st.selectbox("Color by", ["None"] + string_cols, key="scatter_color")
                
                if x_col != y_col:
                    color_param = None if color_col == "None" else color_col
                    fig = px.scatter(df, x=x_col, y=y_col, color=color_param, 
                                   title=f"{y_col} vs {x_col}", 
                                   hover_data=df.columns.tolist())
                    fig.update_layout(height=500)
                    st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Line Chart" and len(numeric_cols) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    if date_cols:
                        x_col = st.selectbox("X-axis (Date)", date_cols, key="line_x")
                    else:
                        x_col = st.selectbox("X-axis", df.columns.tolist(), key="line_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, key="line_y")
                
                fig = px.line(df, x=x_col, y=y_col, title=f"{y_col} over time")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Bar Chart" and len(numeric_cols) > 0:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X-axis", string_cols if string_cols else df.columns.tolist(), key="bar_x")
                with col2:
                    y_col = st.selectbox("Y-axis", numeric_cols, key="bar_y")
                
                # Group by x_col and aggregate y_col
                if x_col in string_cols:
                    bar_data = df.groupby(x_col)[y_col].sum().reset_index()
                    fig = px.bar(bar_data, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                else:
                    fig = px.bar(df, x=x_col, y=y_col, title=f"{y_col} by {x_col}")
                
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Histogram" and len(numeric_cols) > 0:
                col = st.selectbox("Select Column", numeric_cols, key="hist_col")
                fig = px.histogram(df, x=col, title=f"Distribution of {col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Box Plot" and len(numeric_cols) > 0:
                col = st.selectbox("Select Column", numeric_cols, key="box_col")
                fig = px.box(df, y=col, title=f"Box Plot of {col}")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Heatmap" and len(numeric_cols) > 1:
                st.subheader("Correlation Heatmap")
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, 
                              text_auto=True, 
                              aspect="auto",
                              title="Correlation Matrix",
                              color_continuous_scale="RdBu")
                fig.update_layout(height=500)
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("🔍 Advanced Analysis")
            
            # Correlation analysis
            if len(numeric_cols) > 1:
                st.subheader("Correlation Analysis")
                corr_matrix = df[numeric_cols].corr()
                
                # Find strongest correlations
                corr_pairs = []
                for i in range(len(corr_matrix.columns)):
                    for j in range(i+1, len(corr_matrix.columns)):
                        corr_val = corr_matrix.iloc[i, j]
                        if not pd.isna(corr_val):
                            corr_pairs.append({
                                'Variable 1': corr_matrix.columns[i],
                                'Variable 2': corr_matrix.columns[j],
                                'Correlation': corr_val,
                                'Strength': 'Strong' if abs(corr_val) > 0.7 else 'Moderate' if abs(corr_val) > 0.3 else 'Weak'
                            })
                
                corr_df = pd.DataFrame(corr_pairs).sort_values('Correlation', key=abs, ascending=False)
                st.dataframe(corr_df, use_container_width=True)
            
            # Top values analysis
            if len(numeric_cols) > 0:
                st.subheader("Top Values Analysis")
                col = st.selectbox("Select Column for Analysis", numeric_cols, key="top_col")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Top 10 Values")
                    top_values = df.nlargest(10, col)[[col] + (string_cols[:2] if string_cols else [])]
                    st.dataframe(top_values, use_container_width=True)
                
                with col2:
                    st.subheader("Bottom 10 Values")
                    bottom_values = df.nsmallest(10, col)[[col] + (string_cols[:2] if string_cols else [])]
                    st.dataframe(bottom_values, use_container_width=True)
        
        with tab4:
            st.subheader("🎨 Custom Visualization")
            
            # Advanced chart builder
            st.write("Build your own custom visualization:")
            
            col1, col2 = st.columns(2)
            with col1:
                chart_type_custom = st.selectbox(
                    "Chart Type:",
                    ["scatter", "line", "bar", "histogram", "box", "violin", "sunburst", "treemap"],
                    key="custom_chart_type"
                )
            
            with col2:
                if chart_type_custom in ["scatter", "line", "bar"]:
                    x_col_custom = st.selectbox("X-axis", df.columns.tolist(), key="custom_x")
                    y_col_custom = st.selectbox("Y-axis", numeric_cols, key="custom_y")
                    
                    if st.button("Generate Custom Chart"):
                        if chart_type_custom == "scatter":
                            fig = px.scatter(df, x=x_col_custom, y=y_col_custom)
                        elif chart_type_custom == "line":
                            fig = px.line(df, x=x_col_custom, y=y_col_custom)
                        elif chart_type_custom == "bar":
                            fig = px.bar(df, x=x_col_custom, y=y_col_custom)
                        
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    col_custom = st.selectbox("Column", numeric_cols, key="custom_col")
                    
                    if st.button("Generate Custom Chart"):
                        if chart_type_custom == "histogram":
                            fig = px.histogram(df, x=col_custom)
                        elif chart_type_custom == "box":
                            fig = px.box(df, y=col_custom)
                        elif chart_type_custom == "violin":
                            fig = px.violin(df, y=col_custom)
                        
                        fig.update_layout(height=500)
                        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    st.markdown('<h1 class="main-header">📊 Marketing KPIs Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; color: #666; margin-bottom: 2rem;'>{Config.APP_DESCRIPTION}</p>", unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Auto-connect to BigQuery on startup using ADC if defaults are present
    if (not st.session_state.bq_client.client) and Config.GOOGLE_CLOUD_PROJECT and Config.BIGQUERY_DATASET:
        st.session_state.bq_client.project_id = Config.GOOGLE_CLOUD_PROJECT
        st.session_state.bq_client.dataset_id = Config.BIGQUERY_DATASET
        if st.session_state.bq_client.initialize_client():
            load_table_schemas()
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("⚙️ Configuration")
        
        # Connection Status
        if st.session_state.bq_client.client:
            st.markdown('<div class="success-message">✅ Connected to BigQuery</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="error-box">❌ Not connected to BigQuery</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # GCP Configuration
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("🔧 GCP Settings")
        project_id = st.text_input("Project ID", value=Config.GOOGLE_CLOUD_PROJECT or "", help="Your GCP Project ID")
        dataset_id = st.text_input("Dataset ID", value=Config.BIGQUERY_DATASET or "", help="Your BigQuery Dataset ID")
        
        # Initialize BigQuery connection with progress
        if st.button("🔌 Connect to BigQuery", type="primary", use_container_width=True):
            if project_id and dataset_id:
                Config.GOOGLE_CLOUD_PROJECT = project_id
                Config.BIGQUERY_DATASET = dataset_id
                st.session_state.bq_client.project_id = project_id
                st.session_state.bq_client.dataset_id = dataset_id
                
                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🔄 Initializing connection...")
                progress_bar.progress(25)
                
                if st.session_state.bq_client.initialize_client():
                    status_text.text("🔄 Loading table schemas...")
                    progress_bar.progress(75)
                    load_table_schemas()
                    progress_bar.progress(100)
                    status_text.text("✅ Connected successfully!")
                    st.success("🎉 BigQuery connection established!")
                else:
                    progress_bar.progress(0)
                    status_text.text("❌ Connection failed")
            else:
                st.error("Please enter both Project ID and Dataset ID")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Display available tables with enhanced UI
        if st.session_state.table_schemas:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.subheader("📋 Available Tables")
            
            # Search functionality
            search_term = st.text_input("🔍 Search tables", placeholder="Type to filter tables...")
            
            filtered_tables = {}
            if search_term:
                for table_name, schema in st.session_state.table_schemas.items():
                    if search_term.lower() in table_name.lower() or search_term.lower() in schema.get('description', '').lower():
                        filtered_tables[table_name] = schema
            else:
                filtered_tables = st.session_state.table_schemas
            
            for table_name, schema in filtered_tables.items():
                with st.expander(f"📊 {table_name}", expanded=False):
                    st.markdown(f"**Description:** {schema.get('description', 'No description')}")
                    st.markdown("**Columns:**")
                    
                    # Display columns in a more organized way
                    col_data = []
                    for col, dtype in schema.get('columns', {}).items():
                        col_data.append({"Column": col, "Type": dtype})
                    
                    if col_data:
                        st.dataframe(pd.DataFrame(col_data), use_container_width=True, hide_index=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Enhanced sample queries
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.subheader("💡 Sample Queries")
        
        # Query categories
        query_category = st.selectbox(
            "Choose category:",
            ["All", "Campaign Performance", "Customer Metrics", "Financial Analysis", "Trends & Insights"]
        )
        
        sample_queries = {
            "All": [
                "Show me the top 10 campaigns by revenue",
                "What is the average conversion rate by month?",
                "Which campaigns have the highest ROAS?",
                "Show customer acquisition trends over time",
                "What is the total spend by campaign type?"
            ],
            "Campaign Performance": [
                "Show me the top 10 campaigns by revenue",
                "Which campaigns have the highest ROAS?",
                "What is the average conversion rate by campaign?",
                "Show campaign performance by channel"
            ],
            "Customer Metrics": [
                "Show customer acquisition trends over time",
                "What is the average customer lifetime value?",
                "Show churn rate by month",
                "Which channels bring the highest value customers?"
            ],
            "Financial Analysis": [
                "What is the total spend by campaign type?",
                "Show revenue vs spend by month",
                "Which campaigns are most cost-effective?",
                "Calculate ROI by campaign"
            ],
            "Trends & Insights": [
                "Show monthly performance trends",
                "Compare this quarter vs last quarter",
                "Identify top performing time periods",
                "Show seasonal patterns in the data"
            ]
        }
        
        queries_to_show = sample_queries.get(query_category, sample_queries["All"])
        
        for i, query in enumerate(queries_to_show):
            if st.button(f"💬 {query}", key=f"sample_{i}", use_container_width=True):
                st.session_state.sample_query = query
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Welcome section for new users
    if not st.session_state.bq_client.client:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    border-radius: 1rem; margin: 2rem 0; border: 2px dashed #1f77b4;">
            <h2 style="color: #1f77b4; margin-bottom: 1rem;">🚀 Welcome to Marketing KPIs Analytics Dashboard!</h2>
            <p style="font-size: 1.1rem; color: #666; margin-bottom: 1.5rem;">
                Transform your marketing data into actionable insights using natural language queries.
            </p>
            <div style="display: flex; justify-content: center; gap: 1rem; flex-wrap: wrap;">
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 200px;">
                    <h4 style="color: #1f77b4; margin-bottom: 0.5rem;">🔧 Step 1</h4>
                    <p style="margin: 0; font-size: 0.9rem;">Configure your GCP settings in the sidebar</p>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 200px;">
                    <h4 style="color: #1f77b4; margin-bottom: 0.5rem;">🔌 Step 2</h4>
                    <p style="margin: 0; font-size: 0.9rem;">Connect to your BigQuery dataset</p>
                </div>
                <div style="background: white; padding: 1rem; border-radius: 0.5rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1); min-width: 200px;">
                    <h4 style="color: #1f77b4; margin-bottom: 0.5rem;">💬 Step 3</h4>
                    <p style="margin: 0; font-size: 0.9rem;">Ask questions in natural language</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature highlights
        st.subheader("✨ Key Features")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **🤖 AI-Powered Queries**
            - Natural language to SQL conversion
            - Smart query suggestions
            - Context-aware responses
            """)
        
        with col2:
            st.markdown("""
            **📊 Interactive Visualizations**
            - Auto-generated charts
            - Custom visualization builder
            - Real-time data exploration
            """)
        
        with col3:
            st.markdown("""
            **💾 Query Management**
            - Save favorite queries
            - Query history tracking
            - One-click re-execution
            """)
        
        st.info("👈 Please configure your GCP settings in the sidebar and connect to BigQuery to get started.")
        return
    
    # Dashboard overview for connected users
    st.subheader("📊 Dashboard Overview")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📋 Tables Available", len(st.session_state.table_schemas))
    with col2:
        st.metric("🕒 Queries Run", len(st.session_state.query_history))
    with col3:
        st.metric("💾 Saved Queries", len(st.session_state.get('saved_queries', [])))
    with col4:
        st.metric("🔗 Status", "Connected" if st.session_state.bq_client.client else "Disconnected")
    
    # Quick actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🔍 Browse Tables", use_container_width=True):
            st.session_state.show_tables = True
    
    with col2:
        if st.button("📝 View Samples", use_container_width=True):
            st.session_state.show_samples = True
    
    with col3:
        if st.button("📚 Query History", use_container_width=True):
            st.session_state.show_history = True
    
    with col4:
        if st.button("💾 Saved Queries", use_container_width=True):
            st.session_state.show_saved = True
    
    # Show tables if requested
    if st.session_state.get('show_tables', False):
        st.subheader("📋 Available Tables")
        for table_name, schema in st.session_state.table_schemas.items():
            with st.expander(f"📊 {table_name}", expanded=False):
                st.write(f"**Description:** {schema.get('description', 'No description')}")
                st.write("**Columns:**")
                col_data = []
                for col, dtype in schema.get('columns', {}).items():
                    col_data.append({"Column": col, "Type": dtype})
                if col_data:
                    st.dataframe(pd.DataFrame(col_data), use_container_width=True, hide_index=True)
    
    # Show samples if requested
    if st.session_state.get('show_samples', False):
        st.subheader("📝 Sample Queries")
        st.code(st.session_state.text2sql.get_sample_queries(), language="sql")
    
    # Enhanced Query input section
    st.markdown('<div class="query-box">', unsafe_allow_html=True)
    st.subheader("💬 Ask a Question")
    
    # Use sample query if selected
    default_query = ""
    if hasattr(st.session_state, 'sample_query'):
        default_query = st.session_state.sample_query
        delattr(st.session_state, 'sample_query')
    
    # Enhanced text area with better styling
    user_question = st.text_area(
        "Enter your question about the marketing data:",
        value=default_query,
        height=120,
        placeholder="e.g., 'Show me the top performing campaigns by ROAS for the last quarter'",
        help="💡 Tip: Be specific about time periods, metrics, and filters for better results"
    )
    
    # Interactive buttons with better layout
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        generate_sql = st.button("🔍 Generate SQL Query", type="primary", use_container_width=True)
    with col2:
        show_sample_queries = st.button("📝 Samples", use_container_width=True)
    with col3:
        clear_query = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_query:
        st.rerun()
    
    if show_sample_queries:
        st.subheader("📚 Sample SQL Queries")
        st.code(st.session_state.text2sql.get_sample_queries(), language="sql")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if generate_sql and user_question:
        # Enhanced progress tracking
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
        
        # Step 1: Generate SQL
        status_text.text("🤖 Generating SQL query...")
        progress_bar.progress(20)
        
        sql_query = st.session_state.text2sql.generate_sql(
            user_question, 
            st.session_state.table_schemas,
            st.session_state.text2sql.get_sample_queries()
        )
        
        if sql_query:
            progress_bar.progress(40)
            status_text.text("✅ SQL query generated successfully!")
            
            st.markdown('<div class="query-box">', unsafe_allow_html=True)
            st.subheader("🔍 Generated SQL Query")
            
            # Enhanced SQL display with copy functionality
            col1, col2 = st.columns([4, 1])
            with col1:
                st.code(sql_query, language="sql")
            with col2:
                if st.button("📋 Copy SQL", help="Copy SQL to clipboard"):
                    st.write("SQL copied! (Use Ctrl+V to paste)")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced query validation and execution
            st.subheader("⚡ Query Actions")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("✅ Validate Query", type="secondary", use_container_width=True):
                    status_text.text("🔍 Validating query syntax...")
                    progress_bar.progress(60)
                    
                    is_valid, message = st.session_state.bq_client.validate_query(sql_query)
                    if is_valid:
                        st.success("✅ Query is valid and ready to execute!")
                        progress_bar.progress(80)
                    else:
                        st.error(f"❌ {message}")
                        progress_bar.progress(0)
            
            with col2:
                if st.button("🚀 Execute Query", type="primary", use_container_width=True):
                    status_text.text("🚀 Executing query...")
                    progress_bar.progress(60)
                    
                    df = st.session_state.bq_client.execute_query(sql_query, Config.MAX_QUERY_RESULTS)
                    
                    if df is not None:
                        progress_bar.progress(100)
                        status_text.text("✅ Query executed successfully!")
                        
                        st.markdown('<div class="result-box">', unsafe_allow_html=True)
                        display_query_results(df, sql_query)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Add to query history
                        st.session_state.query_history.append({
                            'question': user_question,
                            'sql': sql_query,
                            'timestamp': datetime.now(),
                            'rows': len(df)
                        })
                        
                        # Success animation
                        st.balloons()
                        
                    else:
                        progress_bar.progress(0)
                        status_text.text("❌ Query execution failed")
                        st.markdown('<div class="error-box">', unsafe_allow_html=True)
                        st.error("Query execution failed. Please check your query and try again.")
                        st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                if st.button("💾 Save Query", type="secondary", use_container_width=True):
                    if 'saved_queries' not in st.session_state:
                        st.session_state.saved_queries = []
                    
                    st.session_state.saved_queries.append({
                        'name': f"Query {len(st.session_state.saved_queries) + 1}",
                        'question': user_question,
                        'sql': sql_query,
                        'timestamp': datetime.now()
                    })
                    st.success("💾 Query saved!")
            
            # Clear progress after a delay
            import time
            time.sleep(2)
            progress_bar.empty()
            status_text.empty()
    
    # Enhanced Query history and saved queries
    if st.session_state.query_history or st.session_state.get('saved_queries', []):
        st.subheader("📚 Query History & Saved Queries")
        
        # Tabs for different query types
        tab1, tab2 = st.tabs(["🕒 Recent Queries", "💾 Saved Queries"])
        
        with tab1:
            if st.session_state.query_history:
                # Search and filter functionality
                search_history = st.text_input("🔍 Search history", placeholder="Search by question or SQL...")
                
                filtered_history = st.session_state.query_history
                if search_history:
                    filtered_history = [
                        item for item in st.session_state.query_history
                        if search_history.lower() in item['question'].lower() or 
                           search_history.lower() in item['sql'].lower()
                    ]
                
                # Display history with enhanced UI
                for i, history_item in enumerate(reversed(filtered_history[-10:])):  # Show last 10 queries
                    with st.expander(f"Query {len(filtered_history) - i}: {history_item['question'][:60]}...", expanded=False):
                        st.markdown('<div class="query-history-item">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Question:** {history_item['question']}")
                            st.code(history_item['sql'], language="sql")
                            
                            # Action buttons for each history item
                            col1_1, col1_2, col1_3 = st.columns([1, 1, 1])
                            with col1_1:
                                if st.button("🔄 Re-run", key=f"rerun_{i}"):
                                    st.session_state.sample_query = history_item['question']
                                    st.rerun()
                            with col1_2:
                                if st.button("📋 Copy", key=f"copy_{i}"):
                                    st.write("SQL copied!")
                            with col1_3:
                                if st.button("💾 Save", key=f"save_{i}"):
                                    if 'saved_queries' not in st.session_state:
                                        st.session_state.saved_queries = []
                                    st.session_state.saved_queries.append(history_item)
                                    st.success("Query saved!")
                        
                        with col2:
                            st.write(f"**Timestamp:** {history_item['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                            st.write(f"**Rows:** {history_item['rows']}")
                            
                            # Quick stats
                            st.metric("Result Size", f"{history_item['rows']} rows")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No query history yet. Start by asking a question!")
        
        with tab2:
            if st.session_state.get('saved_queries', []):
                for i, saved_query in enumerate(st.session_state.saved_queries):
                    with st.expander(f"💾 {saved_query.get('name', f'Saved Query {i+1}')}", expanded=False):
                        st.markdown('<div class="query-history-item">', unsafe_allow_html=True)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Question:** {saved_query['question']}")
                            st.code(saved_query['sql'], language="sql")
                            
                            # Action buttons
                            col1_1, col1_2, col1_3 = st.columns([1, 1, 1])
                            with col1_1:
                                if st.button("🔄 Use", key=f"use_saved_{i}"):
                                    st.session_state.sample_query = saved_query['question']
                                    st.rerun()
                            with col1_2:
                                if st.button("📋 Copy", key=f"copy_saved_{i}"):
                                    st.write("SQL copied!")
                            with col1_3:
                                if st.button("🗑️ Delete", key=f"delete_saved_{i}"):
                                    st.session_state.saved_queries.pop(i)
                                    st.rerun()
                        
                        with col2:
                            st.write(f"**Saved:** {saved_query['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("No saved queries yet. Save queries you want to reuse later!")

if __name__ == "__main__":
    main()
