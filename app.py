import pandas as pd
import streamlit as st
import plotly.express as px

# Load the dataset
file_path = 'Updated_Cleaned_Dataset (1).csv'  # Replace with the path to your dataset
dataset = pd.read_csv(file_path)

# Streamlit Page Configuration
st.set_page_config(
    page_title="Real Estate Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("Real Estate Interactive Dashboard")
st.markdown("### Explore Data for Specific Locations and Gain Insights")

# Sidebar Filters
st.sidebar.header("Location Selection")

# Location Dropdown Filter
location = st.sidebar.selectbox(
    "Select a Location",
    options=sorted(dataset['Standardized_Location_Name'].unique()),
    index=0
)

# Filter Data by Selected Location
filtered_data = dataset[dataset['Standardized_Location_Name'] == location]

# Major Insights for All Locations
st.header("Overview of Major Locations")
location_summary = dataset.groupby('Standardized_Location_Name').agg(
    Average_Price=('Plot__Price', 'mean'),
    Average_Price_per_Cent=('Price_per_cent', 'mean'),
    Total_Listings=('Plot__Price', 'count')
).reset_index()

summary_chart = px.bar(
    location_summary,
    x='Standardized_Location_Name',
    y='Average_Price',
    hover_data=['Average_Price_per_Cent', 'Total_Listings'],
    labels={"Average_Price": "Average Price"},
    title="Average Price by Location",
    color='Average_Price',
    color_continuous_scale='Blues'
)
st.plotly_chart(summary_chart, use_container_width=True)

# Display Filtered Data
st.header(f"Data for {location}")

if not filtered_data.empty:
    st.write(f"Displaying data for {location} ({len(filtered_data)} listings)")
    st.dataframe(filtered_data[['Plot__Price', 'Plot__Area', 'Price_per_sqft', 'Plot__Area_Cents', 'Plot__DESC']])

    # Price Distribution
    st.subheader("Price Distribution")
    price_histogram = px.histogram(
        filtered_data,
        x='Plot__Price',
        nbins=10,
        title="Price Distribution in Selected Location",
        labels={"Plot__Price": "Price"},
        color_discrete_sequence=['blue']
    )
    st.plotly_chart(price_histogram, use_container_width=True)

    # Scatter Plot: Plot Area vs. Price
    st.subheader("Plot Area vs. Price")
    scatter_chart = px.scatter(
        filtered_data,
        x='Plot__Area',
        y='Plot__Price',
        labels={"Plot__Area": "Plot Area (sqft)", "Plot__Price": "Price"},
        title="Plot Area vs. Price",
        hover_data=['Price_per_sqft']
    )
    st.plotly_chart(scatter_chart, use_container_width=True)

    # Build-to-Plot Ratio Analysis
    if 'Build_to_Plot_Ratio' in filtered_data.columns:
        st.subheader("Build-to-Plot Ratio Analysis")
        ratio_chart = px.box(
            filtered_data,
            y='Build_to_Plot_Ratio',
            title="Distribution of Build-to-Plot Ratio",
            labels={"Build_to_Plot_Ratio": "Ratio"}
        )
        st.plotly_chart(ratio_chart, use_container_width=True)

else:
    st.warning(f"No data available for {location}. Please select another location.")

# Key Comparisons
st.header("Comparisons Across Major Locations")
comparison_chart = px.bar(
    location_summary,
    x='Standardized_Location_Name',
    y=['Average_Price', 'Average_Price_per_Cent'],
    barmode='group',
    labels={"value": "Amount", "variable": "Metric"},
    title="Comparison of Average Prices and Price per Cent",
    color_discrete_sequence=px.colors.qualitative.Set2
)
st.plotly_chart(comparison_chart, use_container_width=True)

# Summary Section
st.sidebar.subheader("Summary")
st.sidebar.write(f"Total Listings: {len(dataset)}")
st.sidebar.write(f"Filtered Listings: {len(filtered_data)}")
