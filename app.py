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
st.markdown("### Explore, Filter, and Visualize Real Estate Data")

# Sidebar Filters
st.sidebar.header("Filters")

# Price Range Filter
price_min, price_max = st.sidebar.slider(
    "Select Price Range",
    min_value=int(dataset['Plot__Price'].min()),
    max_value=int(dataset['Plot__Price'].max()),
    value=(int(dataset['Plot__Price'].min()), int(dataset['Plot__Price'].max()))
)

# Location Filter with Multiselect
locations = st.sidebar.multiselect(
    "Select Locations",
    options=dataset['Standardized_Location_Name'].unique(),
    default=dataset['Standardized_Location_Name'].unique()
)

# Plot Area Filter
area_min, area_max = st.sidebar.slider(
    "Select Plot Area Range (sqft)",
    min_value=int(dataset['Plot__Area'].min()),
    max_value=int(dataset['Plot__Area'].max()),
    value=(int(dataset['Plot__Area'].min()), int(dataset['Plot__Area'].max()))
)

# Apply Filters
filtered_data = dataset[
    (dataset['Plot__Price'] >= price_min) &
    (dataset['Plot__Price'] <= price_max) &
    (dataset['Standardized_Location_Name'].isin(locations)) &
    (dataset['Plot__Area'] >= area_min) &
    (dataset['Plot__Area'] <= area_max)
]

# Main Dashboard
st.header("Filtered Listings")
st.write(f"Displaying {len(filtered_data)} of {len(dataset)} listings")

# Data Table
st.dataframe(filtered_data[['Standardized_Location_Name', 'Plot__Price', 'Plot__Area', 'Price_per_sqft']])

# Visualizations
st.header("Key Insights")

# Price Distribution by Location
if len(filtered_data) > 0:
    st.subheader("Average Price by Location")
    price_by_location = filtered_data.groupby('Standardized_Location_Name')['Plot__Price'].mean().reset_index()
    price_chart = px.bar(
        price_by_location,
        x='Standardized_Location_Name',
        y='Plot__Price',
        labels={"Plot__Price": "Average Price"},
        title="Average Plot Price by Location",
        color='Plot__Price',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(price_chart, use_container_width=True)

    # Scatter Plot: Plot Area vs. Price
    st.subheader("Plot Area vs. Price")
    scatter_chart = px.scatter(
        filtered_data,
        x='Plot__Area',
        y='Plot__Price',
        labels={"Plot__Area": "Plot Area (sqft)", "Plot__Price": "Price"},
        title="Plot Area vs. Price",
        hover_data=['Standardized_Location_Name', 'Price_per_sqft']
    )
    st.plotly_chart(scatter_chart, use_container_width=True)

    # Interactive Map (Optional if Lat/Lon data is available)
    if 'Latitude' in dataset.columns and 'Longitude' in dataset.columns:
        st.subheader("Interactive Map of Listings")
        map_chart = px.scatter_mapbox(
            filtered_data,
            lat="Latitude",
            lon="Longitude",
            hover_name="Standardized_Location_Name",
            hover_data=["Plot__Price", "Plot__Area"],
            color="Plot__Price",
            size="Plot__Area",
            color_continuous_scale=px.colors.cyclical.IceFire,
            title="Map of Listings"
        )
        map_chart.update_layout(mapbox_style="open-street-map")
        st.plotly_chart(map_chart, use_container_width=True)

else:
    st.warning("No data matches your selected filters. Please adjust the filters.")

# Summary Section
st.sidebar.subheader("Summary")
st.sidebar.write(f"Total Listings: {len(dataset)}")
st.sidebar.write(f"Filtered Listings: {len(filtered_data)}")
