import pandas as pd
import streamlit as st

# Load the dataset
file_path = 'Updated_Cleaned_Dataset (1).csv'  # Replace with the path to your dataset
dataset = pd.read_csv(file_path)

# Title
st.title("Real Estate Interactive Dashboard")

# Sidebar Filters
st.sidebar.header("Filter Options")
price_min, price_max = st.sidebar.slider(
    "Select Price Range",
    min_value=int(dataset['Plot__Price'].min()),
    max_value=int(dataset['Plot__Price'].max()),
    value=(int(dataset['Plot__Price'].min()), int(dataset['Plot__Price'].max()))
)

locations = st.sidebar.multiselect(
    "Select Location(s)",
    options=dataset['Standardized_Location_Name'].unique(),
    default=dataset['Standardized_Location_Name'].unique()
)

area_min, area_max = st.sidebar.slider(
    "Select Plot Area Range (sqft)",
    min_value=int(dataset['Plot__Area'].min()),
    max_value=int(dataset['Plot__Area'].max()),
    value=(int(dataset['Plot__Area'].min()), int(dataset['Plot__Area'].max()))
)

# Filtered Dataset
filtered_data = dataset[
    (dataset['Plot__Price'] >= price_min) &
    (dataset['Plot__Price'] <= price_max) &
    (dataset['Standardized_Location_Name'].isin(locations)) &
    (dataset['Plot__Area'] >= area_min) &
    (dataset['Plot__Area'] <= area_max)
]

# Display Data
st.header("Filtered Listings")
st.write(f"Displaying {len(filtered_data)} of {len(dataset)} listings")
st.dataframe(filtered_data)

# Additional Visualizations
st.header("Visualizations")

# Price Distribution
st.subheader("Price Distribution")
st.bar_chart(filtered_data[['Standardized_Location_Name', 'Plot__Price']].groupby('Standardized_Location_Name').mean())

# Plot Area vs. Price
st.subheader("Plot Area vs. Price")
st.scatter_chart(filtered_data[['Plot__Area', 'Plot__Price']])

# Detailed Plot Description
st.subheader("Explore Plot Descriptions")
selected_plot = st.selectbox(
    "Select a Plot for Details",
    options=filtered_data.index,
    format_func=lambda x: f"Plot ID {x} - {filtered_data.loc[x, 'Standardized_Location_Name']}"
)
st.write(filtered_data.loc[selected_plot, 'Plot__DESC'])
