import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Load the dataset
file_path = 'Updated_Cleaned_Dataset (1).csv'  # Replace with the path to your dataset
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

dataset = load_data(file_path)

# Preprocessing: Check for required columns
required_columns = [
    'Plot__url', 'Plot__Price', 'Plot__Beds', 'Build__Area', 'Plot__Area',
    'Plot__DESC', 'Plot__Area_Cents', 'Price_per_sqft', 'Price_per_cent',
    'Total_Area', 'Build_to_Plot_Ratio', 'Standardized_Location_Name'
]

missing_columns = [col for col in required_columns if col not in dataset.columns]
if missing_columns:
    st.error(f"Missing required columns: {', '.join(missing_columns)}")
    st.stop()

# Streamlit Page Configuration
st.set_page_config(
    page_title="Enhanced Real Estate Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# Title and Description
st.title("🏠 Enhanced Real Estate Interactive Dashboard")
st.markdown("""
### Explore Comprehensive Data for Specific Locations and Gain Deeper Insights
- **Filter** listings based on multiple criteria.
- **Visualize** data through interactive charts.
- **Compare** different metrics across locations.
- **Analyze** distributions and relationships effectively.
""")

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Multi-select Location Filter
locations = sorted(dataset['Standardized_Location_Name'].unique())
selected_locations = st.sidebar.multiselect(
    "Select Location(s)",
    options=locations,
    default=[locations[0]]
)

# Multi-select Beds Filter
beds_options = sorted(dataset['Plot__Beds'].unique())
selected_beds = st.sidebar.multiselect(
    "Select Number of Bedrooms",
    options=beds_options,
    default=beds_options
)

# Price Range Slider
min_price = int(dataset['Plot__Price'].min())
max_price = int(dataset['Plot__Price'].max())
selected_price = st.sidebar.slider(
    "Select Price Range ($)",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=10000
)

# Plot Area Range Slider
min_plot_area = int(dataset['Plot__Area'].min())
max_plot_area = int(dataset['Plot__Area'].max())
selected_plot_area = st.sidebar.slider(
    "Select Plot Area (sqft)",
    min_value=min_plot_area,
    max_value=max_plot_area,
    value=(min_plot_area, max_plot_area),
    step=50
)

# Build Area Range Slider
min_build_area = int(dataset['Build__Area'].min())
max_build_area = int(dataset['Build__Area'].max())
selected_build_area = st.sidebar.slider(
    "Select Build Area (sqft)",
    min_value=min_build_area,
    max_value=max_build_area,
    value=(min_build_area, max_build_area),
    step=50
)

# Build-to-Plot Ratio Slider
min_ratio = float(dataset['Build_to_Plot_Ratio'].min())
max_ratio = float(dataset['Build_to_Plot_Ratio'].max())
selected_ratio = st.sidebar.slider(
    "Select Build-to-Plot Ratio",
    min_value=0.0,
    max_value=round(max_ratio, 2),
    value=(0.0, round(max_ratio, 2)),
    step=0.1
)

# Apply Filters
filtered_data = dataset[
    (dataset['Standardized_Location_Name'].isin(selected_locations)) &
    (dataset['Plot__Beds'].isin(selected_beds)) &
    (dataset['Plot__Price'] >= selected_price[0]) &
    (dataset['Plot__Price'] <= selected_price[1]) &
    (dataset['Plot__Area'] >= selected_plot_area[0]) &
    (dataset['Plot__Area'] <= selected_plot_area[1]) &
    (dataset['Build__Area'] >= selected_build_area[0]) &
    (dataset['Build__Area'] <= selected_build_area[1]) &
    (dataset['Build_to_Plot_Ratio'] >= selected_ratio[0]) &
    (dataset['Build_to_Plot_Ratio'] <= selected_ratio[1])
]

# Sidebar Summary
st.sidebar.subheader("📊 Summary")
st.sidebar.write(f"**Total Listings:** {len(dataset)}")
st.sidebar.write(f"**Filtered Listings:** {len(filtered_data)}")

# KPIs
st.header("🚀 Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Listings", len(filtered_data))
kpi2.metric("Average Price", f"${filtered_data['Plot__Price'].mean():,.2f}")
kpi3.metric("Median Plot Area", f"{filtered_data['Plot__Area'].median():,.0f} sqft")
kpi4.metric("Average Price per Sqft", f"${filtered_data['Price_per_sqft'].mean():,.2f}")

# Overview of Major Locations
st.header("📊 Overview of Major Locations")
location_summary = filtered_data.groupby('Standardized_Location_Name').agg(
    Average_Price=('Plot__Price', 'mean'),
    Average_Price_per_Cent=('Price_per_cent', 'mean'),
    Total_Listings=('Plot__Price', 'count'),
    Average_Build_Area=('Build__Area', 'mean'),
    Average_Plot_Area=('Plot__Area', 'mean')
).reset_index()

summary_chart = px.bar(
    location_summary,
    x='Standardized_Location_Name',
    y='Average_Price',
    hover_data=['Average_Price_per_Cent', 'Total_Listings', 'Average_Build_Area', 'Average_Plot_Area'],
    labels={"Average_Price": "Average Price ($)"},
    title="Average Price by Location",
    color='Average_Price',
    color_continuous_scale='Blues'
)
st.plotly_chart(summary_chart, use_container_width=True)

# Detailed Analytics
st.header("📈 Detailed Analytics")

# 1. Price Distribution by Location
st.subheader("💲 Price Distribution by Location")
fig_price_dist = px.box(
    filtered_data,
    x='Standardized_Location_Name',
    y='Plot__Price',
    points='outliers',
    title="Price Distribution Across Locations",
    labels={"Plot__Price": "Price ($)", "Standardized_Location_Name": "Location"},
    color='Standardized_Location_Name',
    color_discrete_sequence=px.colors.qualitative.Set3
)
st.plotly_chart(fig_price_dist, use_container_width=True)

# 2. Plot Area vs. Price with Regression Line
st.subheader("📐 Plot Area vs. Price")
fig_scatter = px.scatter(
    filtered_data,
    x='Plot__Area',
    y='Plot__Price',
    trendline='ols',
    hover_data=['Price_per_sqft', 'Standardized_Location_Name'],
    title="Relationship Between Plot Area and Price",
    labels={"Plot__Area": "Plot Area (sqft)", "Plot__Price": "Price ($)"},
    color='Standardized_Location_Name',
    color_discrete_sequence=px.colors.qualitative.Safe
)
st.plotly_chart(fig_scatter, use_container_width=True)

# 3. Build-to-Plot Ratio Analysis
st.subheader("🔍 Build-to-Plot Ratio Analysis")
fig_ratio = px.histogram(
    filtered_data,
    x='Build_to_Plot_Ratio',
    nbins=20,
    title="Distribution of Build-to-Plot Ratios",
    labels={"Build_to_Plot_Ratio": "Build-to-Plot Ratio"},
    color_discrete_sequence=['teal']
)
st.plotly_chart(fig_ratio, use_container_width=True)

# Comparative Analysis
st.header("🔄 Comparative Analysis Across Locations")
comparison_metrics = ['Average_Price', 'Average_Price_per_Cent', 'Total_Listings']
fig_comparison = go.Figure()

fig_comparison.add_trace(go.Bar(
    x=location_summary['Standardized_Location_Name'],
    y=location_summary['Average_Price'],
    name='Average Price',
    marker_color='indianred'
))
fig_comparison.add_trace(go.Bar(
    x=location_summary['Standardized_Location_Name'],
    y=location_summary['Average_Price_per_Cent'],
    name='Avg Price per Cent',
    marker_color='lightsalmon'
))
fig_comparison.add_trace(go.Bar(
    x=location_summary['Standardized_Location_Name'],
    y=location_summary['Total_Listings'],
    name='Total Listings',
    marker_color='darkseagreen'
))

fig_comparison.update_layout(
    barmode='group',
    title="Comparison of Key Metrics Across Locations",
    xaxis_title="Location",
    yaxis_title="Value",
    legend_title="Metrics",
    template="plotly_white"
)
st.plotly_chart(fig_comparison, use_container_width=True)

# Listings Data Table
st.header("📋 Listings Data Table")
st.subheader("Filter and Sort Listings")
st.dataframe(
    filtered_data[[
        'Standardized_Location_Name', 'Plot__Price', 'Plot__Beds', 'Build__Area',
        'Plot__Area', 'Price_per_sqft', 'Price_per_cent', 'Build_to_Plot_Ratio',
        'Total_Area', 'Plot__DESC', 'Plot__url'
    ]].sort_values(by='Plot__Price', ascending=False).reset_index(drop=True),
    height=600
)

# Export Option
st.header("💾 Export Data")
st.markdown("Download the filtered data for further analysis.")
def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df(filtered_data)

st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name='filtered_real_estate_data.csv',
    mime='text/csv',
)

# Footer
st.markdown("---")
st.markdown("Developed by [Your Name](https://yourwebsite.com) | © 2024 Real Estate Insights")
