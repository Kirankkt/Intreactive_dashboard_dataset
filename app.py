import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image

# Load the dataset
file_path = 'Updated_Cleaned_Dataset (1).csv'  # Replace with the path to your dataset
dataset = pd.read_csv(file_path)

# Preprocessing: Ensure necessary columns are present
required_columns = [
    'Standardized_Location_Name', 'Plot__Price', 'Plot__Area',
    'Price_per_sqft', 'Plot__Area_Cents', 'Plot__DESC',
    'Build_to_Plot_Ratio', 'Latitude', 'Longitude', 'Listing_Date'  # Assuming these columns exist
]

for col in required_columns:
    if col not in dataset.columns:
        st.error(f"Missing required column: {col}")
        st.stop()

# Convert Listing_Date to datetime if not already
if not pd.api.types.is_datetime64_any_dtype(dataset['Listing_Date']):
    dataset['Listing_Date'] = pd.to_datetime(dataset['Listing_Date'], errors='coerce')

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
- **Visualize** data through interactive charts and maps.
- **Compare** different metrics across locations.
- **Analyze** trends and distributions effectively.
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

# Price Range Slider
min_price = int(dataset['Plot__Price'].min())
max_price = int(dataset['Plot__Price'].max())
selected_price = st.sidebar.slider(
    "Select Price Range",
    min_value=min_price,
    max_value=max_price,
    value=(min_price, max_price),
    step=10000
)

# Plot Area Range Slider
min_area = int(dataset['Plot__Area'].min())
max_area = int(dataset['Plot__Area'].max())
selected_area = st.sidebar.slider(
    "Select Plot Area (sqft)",
    min_value=min_area,
    max_value=max_area,
    value=(min_area, max_area),
    step=50
)

# Date Range Picker
min_date = dataset['Listing_Date'].min().date()
max_date = dataset['Listing_Date'].max().date()
selected_date = st.sidebar.date_input(
    "Select Listing Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Additional Filters (e.g., Build-to-Plot Ratio)
if 'Build_to_Plot_Ratio' in dataset.columns:
    min_ratio = float(dataset['Build_to_Plot_Ratio'].min())
    max_ratio = float(dataset['Build_to_Plot_Ratio'].max())
    selected_ratio = st.sidebar.slider(
        "Select Build-to-Plot Ratio",
        min_value=0.0,
        max_value=float(max_ratio),
        value=(float(min_ratio), float(max_ratio)),
        step=0.1
    )
else:
    selected_ratio = (0.0, 10.0)  # Default range

# Apply Filters
filtered_data = dataset[
    (dataset['Standardized_Location_Name'].isin(selected_locations)) &
    (dataset['Plot__Price'] >= selected_price[0]) &
    (dataset['Plot__Price'] <= selected_price[1]) &
    (dataset['Plot__Area'] >= selected_area[0]) &
    (dataset['Plot__Area'] <= selected_area[1]) &
    (dataset['Listing_Date'].dt.date >= selected_date[0]) &
    (dataset['Listing_Date'].dt.date <= selected_date[1])
]

if 'Build_to_Plot_Ratio' in dataset.columns:
    filtered_data = filtered_data[
        (dataset['Build_to_Plot_Ratio'] >= selected_ratio[0]) &
        (dataset['Build_to_Plot_Ratio'] <= selected_ratio[1])
    ]

# Sidebar Summary
st.sidebar.subheader("📊 Summary")
st.sidebar.write(f"**Total Listings:** {len(dataset)}")
st.sidebar.write(f"**Filtered Listings:** {len(filtered_data)}")

# KPIs
st.header("🚀 Key Performance Indicators")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Total Listings", len(filtered_data))
kpi2.metric("Average Price", f"${filtered_data['Plot__Price'].mean():,.2f}")
kpi3.metric("Median Plot Area", f"{filtered_data['Plot__Area'].median():,.0f} sqft")

# Interactive Map
st.header("🗺️ Listings Map")
if 'Latitude' in filtered_data.columns and 'Longitude' in filtered_data.columns:
    map_data = filtered_data.copy()
    map_data = map_data.dropna(subset=['Latitude', 'Longitude'])
    if not map_data.empty:
        fig_map = px.scatter_mapbox(
            map_data,
            lat="Latitude",
            lon="Longitude",
            hover_name="Standardized_Location_Name",
            hover_data={"Plot__Price": True, "Plot__Area": True, "Price_per_sqft": True},
            color="Plot__Price",
            size="Plot__Area",
            color_continuous_scale=px.colors.cyclical.IceFire,
            size_max=15,
            zoom=10,
            height=600,
            title="Geographical Distribution of Listings"
        )
        fig_map.update_layout(mapbox_style="open-street-map")
        fig_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.warning("No geographical data available for the selected filters.")
else:
    st.warning("Latitude and Longitude columns are required for the map visualization.")

# Advanced Visualizations
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
if 'Build_to_Plot_Ratio' in filtered_data.columns:
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
location_summary = filtered_data.groupby('Standardized_Location_Name').agg(
    Average_Price=('Plot__Price', 'mean'),
    Average_Price_per_Cent=('Price_per_cent', 'mean'),
    Total_Listings=('Plot__Price', 'count'),
    Median_Area=('Plot__Area', 'median')
).reset_index()

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

# Trend Analysis Over Time
st.header("📅 Listing Trends Over Time")
if 'Listing_Date' in filtered_data.columns:
    trend_data = filtered_data.set_index('Listing_Date').resample('M').size().reset_index(name='Listings')
    fig_trend = px.line(
        trend_data,
        x='Listing_Date',
        y='Listings',
        title="Monthly Listings Trend",
        labels={"Listing_Date": "Date", "Listings": "Number of Listings"},
        markers=True
    )
    st.plotly_chart(fig_trend, use_container_width=True)
else:
    st.warning("Listing_Date column is required for trend analysis.")

# Detailed Data Exploration
st.header("📋 Listings Data Table")
st.subheader("Filter and Sort Listings")
st.dataframe(
    filtered_data[[
        'Standardized_Location_Name', 'Plot__Price', 'Plot__Area',
        'Price_per_sqft', 'Plot__Area_Cents', 'Build_to_Plot_Ratio',
        'Listing_Date', 'Plot__DESC'
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

