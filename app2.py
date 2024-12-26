# app.py

import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------
# Streamlit Page Configuration
# ---------------------------
st.set_page_config(
    page_title="Real Estate Multi-Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="🏠"
)

# ---------------------------
# Title and Description
# ---------------------------
st.title("🏠 Real Estate Multi-Dashboard")
st.markdown("""
Welcome to the **Real Estate Multi-Dashboard**! Navigate between the **Property Data Dashboard** and the **Plot Data Dashboard** using the sidebar.

- **Property Data Dashboard:** Explore comprehensive property listings with various filters and interactive visualizations.
- **Plot Data Dashboard:** Dive into plot-specific data with geospatial insights and detailed analytics.

Use the sidebar to switch between dashboards and apply filters as needed.
""")

# ---------------------------
# Sidebar Navigation
# ---------------------------
st.sidebar.header("📑 Navigation")
dashboard = st.sidebar.radio("Select Dashboard:", ["Property Data Dashboard", "Plot Data Dashboard"])

# ---------------------------
# Utility Functions
# ---------------------------
@st.cache_data
def load_property_data(path):
    return pd.read_csv(path)

@st.cache_data
def load_plot_data(path):
    return pd.read_csv(path)

def make_clickable(url):
    return f'<a href="{url}" target="_blank">View Listing</a>'

# ---------------------------
# Property Data Dashboard
# ---------------------------
if dashboard == "Property Data Dashboard":
    st.header("📊 Property Data Interactive Dashboard")
    
    # ---------------------------
    # Load Property Dataset
    # ---------------------------
    property_file_path = 'Updated_Cleaned_Dataset (1).csv'  # Replace with your actual Property Data CSV file name
    property_data = load_property_data(property_file_path)
    
    # ---------------------------
    # Preprocessing: Check for Required Columns
    # ---------------------------
    property_required_columns = [
        'Plot__url', 'Plot__Price', 'Plot__Beds', 'Build__Area', 'Plot__Area',
        'Plot__DESC', 'Plot__Area_Cents', 'Price_per_sqft', 'Price_per_cent',
        'Total_Area', 'Build_to_Plot_Ratio', 'Standardized_Location_Name'
    ]
    
    missing_prop_columns = [col for col in property_required_columns if col not in property_data.columns]
    if missing_prop_columns:
        st.error(f"Property Data Dashboard - Missing required columns: {', '.join(missing_prop_columns)}")
        st.stop()
    
    # ---------------------------
    # Sidebar Filters for Property Dashboard
    # ---------------------------
    st.sidebar.header("🔍 Property Filters")
    
    # Multi-select Location Filter
    prop_locations = sorted(property_data['Standardized_Location_Name'].unique())
    selected_prop_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=prop_locations,
        default=prop_locations  # Select all by default
    )
    
    # Multi-select Bedrooms Filter
    prop_beds_options = sorted(property_data['Plot__Beds'].unique())
    selected_prop_beds = st.sidebar.multiselect(
        "Select Number of Bedrooms",
        options=prop_beds_options,
        default=prop_beds_options
    )
    
    # Price Range Slider
    prop_min_price = int(property_data['Plot__Price'].min())
    prop_max_price = int(property_data['Plot__Price'].max())
    selected_prop_price = st.sidebar.slider(
        "Select Price Range ($)",
        min_value=prop_min_price,
        max_value=prop_max_price,
        value=(prop_min_price, prop_max_price),
        step=10000
    )
    
    # Plot Area Range Slider
    prop_min_plot_area = float(property_data['Plot__Area'].min())
    prop_max_plot_area = float(property_data['Plot__Area'].max())
    selected_prop_plot_area = st.sidebar.slider(
        "Select Plot Area (sqft)",
        min_value=prop_min_plot_area,
        max_value=prop_max_plot_area,
        value=(prop_min_plot_area, prop_max_plot_area),
        step=1.0
    )
    
    # Build Area Range Slider
    prop_min_build_area = float(property_data['Build__Area'].min())
    prop_max_build_area = float(property_data['Build__Area'].max())
    selected_prop_build_area = st.sidebar.slider(
        "Select Build Area (sqft)",
        min_value=prop_min_build_area,
        max_value=prop_max_build_area,
        value=(prop_min_build_area, prop_max_build_area),
        step=1.0
    )
    
    # Build-to-Plot Ratio Slider
    prop_min_ratio = float(property_data['Build_to_Plot_Ratio'].min())
    prop_max_ratio = float(property_data['Build_to_Plot_Ratio'].max())
    selected_prop_ratio = st.sidebar.slider(
        "Select Build-to-Plot Ratio",
        min_value=0.0,
        max_value=round(prop_max_ratio, 2),
        value=(0.0, round(prop_max_ratio, 2)),
        step=0.1
    )
    
    # ---------------------------
    # Apply Filters to Property Data
    # ---------------------------
    filtered_prop_data = property_data[
        (property_data['Standardized_Location_Name'].isin(selected_prop_locations)) &
        (property_data['Plot__Beds'].isin(selected_prop_beds)) &
        (property_data['Plot__Price'] >= selected_prop_price[0]) &
        (property_data['Plot__Price'] <= selected_prop_price[1]) &
        (property_data['Plot__Area'] >= selected_prop_plot_area[0]) &
        (property_data['Plot__Area'] <= selected_prop_plot_area[1]) &
        (property_data['Build__Area'] >= selected_prop_build_area[0]) &
        (property_data['Build__Area'] <= selected_prop_build_area[1]) &
        (property_data['Build_to_Plot_Ratio'] >= selected_prop_ratio[0]) &
        (property_data['Build_to_Plot_Ratio'] <= selected_prop_ratio[1])
    ]
    
    # ---------------------------
    # Sidebar Summary for Property Dashboard
    # ---------------------------
    st.sidebar.subheader("📊 Property Summary")
    st.sidebar.write(f"**Total Listings:** {len(property_data)}")
    st.sidebar.write(f"**Filtered Listings:** {len(filtered_prop_data)}")
    
    # ---------------------------
    # Key Performance Indicators (KPIs) for Property Dashboard
    # ---------------------------
    st.header("🚀 Key Performance Indicators")
    prop_kpi1, prop_kpi2, prop_kpi3, prop_kpi4 = st.columns(4)
    prop_kpi1.metric("Total Listings", len(filtered_prop_data))
    prop_kpi2.metric("Average Price", f"${filtered_prop_data['Plot__Price'].mean():,.2f}")
    prop_kpi3.metric("Median Plot Area", f"{filtered_prop_data['Plot__Area'].median():,.0f} sqft")
    prop_kpi4.metric("Average Price per Sqft", f"${filtered_prop_data['Price_per_sqft'].mean():,.2f}")
    
    # ---------------------------
    # Overview of Major Locations for Property Dashboard
    # ---------------------------
    st.header("📊 Overview of Major Locations")
    prop_location_summary = filtered_prop_data.groupby('Standardized_Location_Name').agg(
        Average_Price=('Plot__Price', 'mean'),
        Average_Price_per_Cent=('Price_per_cent', 'mean'),
        Total_Listings=('Plot__Price', 'count'),
        Average_Build_Area=('Build__Area', 'mean'),
        Average_Plot_Area=('Plot__Area', 'mean')
    ).reset_index()
    
    prop_summary_chart = px.bar(
        prop_location_summary,
        x='Standardized_Location_Name',
        y='Average_Price',
        hover_data=['Average_Price_per_Cent', 'Total_Listings', 'Average_Build_Area', 'Average_Plot_Area'],
        labels={"Average_Price": "Average Price ($)"},
        title="Average Price by Location",
        color='Average_Price',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(prop_summary_chart, use_container_width=True)
    
    # ---------------------------
    # Detailed Analytics for Property Dashboard
    # ---------------------------
    st.header("📈 Detailed Analytics")
    
    # 1. Price Distribution by Location
    st.subheader("💲 Price Distribution by Location")
    prop_fig_price_dist = px.box(
        filtered_prop_data,
        x='Standardized_Location_Name',
        y='Plot__Price',
        points='outliers',
        title="Price Distribution Across Locations",
        labels={"Plot__Price": "Price ($)", "Standardized_Location_Name": "Location"},
        color='Standardized_Location_Name',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(prop_fig_price_dist, use_container_width=True)
    
    # 2. Plot Area vs. Price with Regression Line
    st.subheader("📐 Plot Area vs. Price")
    try:
        prop_fig_scatter = px.scatter(
            filtered_prop_data,
            x='Plot__Area',
            y='Plot__Price',
            trendline='ols',
            hover_data=['Price_per_sqft', 'Standardized_Location_Name'],
            title="Relationship Between Plot Area and Price",
            labels={"Plot__Area": "Plot Area (sqft)", "Plot__Price": "Price ($)"},
            color='Standardized_Location_Name',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(prop_fig_scatter, use_container_width=True)
    except ModuleNotFoundError:
        st.warning("`statsmodels` is not installed. Install it to enable trendlines in scatter plots.")
    
    # 3. Build-to-Plot Ratio Analysis
    st.subheader("🔍 Build-to-Plot Ratio Analysis")
    prop_fig_ratio = px.histogram(
        filtered_prop_data,
        x='Build_to_Plot_Ratio',
        nbins=20,
        title="Distribution of Build-to-Plot Ratios",
        labels={"Build_to_Plot_Ratio": "Build-to-Plot Ratio"},
        color_discrete_sequence=['teal']
    )
    st.plotly_chart(prop_fig_ratio, use_container_width=True)
    
    # ---------------------------
    # Comparative Analysis for Property Dashboard
    # ---------------------------
    st.header("🔄 Comparative Analysis Across Locations")
    prop_comparison_metrics = ['Average_Price', 'Average_Price_per_Cent', 'Total_Listings']
    prop_fig_comparison = go.Figure()
    
    prop_fig_comparison.add_trace(go.Bar(
        x=prop_location_summary['Standardized_Location_Name'],
        y=prop_location_summary['Average_Price'],
        name='Average Price',
        marker_color='indianred'
    ))
    prop_fig_comparison.add_trace(go.Bar(
        x=prop_location_summary['Standardized_Location_Name'],
        y=prop_location_summary['Average_Price_per_Cent'],
        name='Avg Price per Cent',
        marker_color='lightsalmon'
    ))
    prop_fig_comparison.add_trace(go.Bar(
        x=prop_location_summary['Standardized_Location_Name'],
        y=prop_location_summary['Total_Listings'],
        name='Total Listings',
        marker_color='darkseagreen'
    ))
    
    prop_fig_comparison.update_layout(
        barmode='group',
        title="Comparison of Key Metrics Across Locations",
        xaxis_title="Location",
        yaxis_title="Value",
        legend_title="Metrics",
        template="plotly_white"
    )
    st.plotly_chart(prop_fig_comparison, use_container_width=True)
    
    # ---------------------------
    # Listings Data Table for Property Dashboard
    # ---------------------------
    st.header("📋 Listings Data Table")
    st.subheader("Filter and Sort Listings")
    
    # Convert Plot__url to clickable links
    prop_filtered_data_display = filtered_prop_data.copy()
    prop_filtered_data_display['Plot__url'] = prop_filtered_data_display['Plot__url'].apply(make_clickable)
    
    # Select columns to display
    prop_display_columns = [
        'Standardized_Location_Name', 'Plot__Price', 'Plot__Beds', 'Build__Area',
        'Plot__Area', 'Price_per_sqft', 'Price_per_cent', 'Build_to_Plot_Ratio',
        'Total_Area', 'Plot__DESC', 'Plot__url'
    ]
    
    # Display as HTML table for clickable links
    st.markdown(
        prop_filtered_data_display[prop_display_columns].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    
    # ---------------------------
    # Export Option for Property Dashboard
    # ---------------------------
    st.header("💾 Export Data")
    st.markdown("Download the filtered property data for further analysis.")
    
    def convert_prop_df(df):
        return df.to_csv(index=False).encode('utf-8')
    
    prop_csv = convert_prop_df(filtered_prop_data)
    
    st.download_button(
        label="📥 Download Property CSV",
        data=prop_csv,
        file_name='filtered_property_data.csv',
        mime='text/csv',
    )

# ---------------------------
# Plot Data Dashboard
# ---------------------------
elif dashboard == "Plot Data Dashboard":
    st.header("📍 Plot Data Interactive Dashboard")
    
    # ---------------------------
    # Load Plot Dataset
    # ---------------------------
    plot_file_path = 'standardized_locations_dataset.csv'  # Replace with your actual Plot Data CSV file name
    plot_data = load_plot_data(plot_file_path)
    
    # ---------------------------
    # Preprocessing: Check for Required Columns
    # ---------------------------
    plot_required_columns = [
        'Url', 'Price', 'Area', 'Price per cent', 'Location', 'Latitude',
        'Longitude', 'distance_to_technopark', 'distance_to_agasthyamalai_hills',
        'distance_to_ponmudi_hills', 'distance_to_nearest_beach',
        'distance_to_nearest_lake', 'density', 'price_to_price_per_cent_ratio',
        'beach_proximity', 'lake_proximity'
    ]
    
    missing_plot_columns = [col for col in plot_required_columns if col not in plot_data.columns]
    if missing_plot_columns:
        st.error(f"Plot Data Dashboard - Missing required columns: {', '.join(missing_plot_columns)}")
        st.stop()
    
    # ---------------------------
    # Sidebar Filters for Plot Dashboard
    # ---------------------------
    st.sidebar.header("🔍 Plot Filters")
    
    # Multi-select Location Filter
    plot_locations = sorted(plot_data['Location'].unique())
    selected_plot_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=plot_locations,
        default=plot_locations  # Select all by default
    )
    
    # Multi-select Density Filter
    plot_density_options = sorted(plot_data['density'].unique())
    selected_plot_density = st.sidebar.multiselect(
        "Select Density",
        options=plot_density_options,
        default=plot_density_options
    )
    
    # Price Range Slider
    plot_min_price = int(plot_data['Price'].min())
    plot_max_price = int(plot_data['Price'].max())
    selected_plot_price = st.sidebar.slider(
        "Select Price Range ($)",
        min_value=plot_min_price,
        max_value=plot_max_price,
        value=(plot_min_price, plot_max_price),
        step=10000
    )
    
    # Area Range Slider
    plot_min_area = float(plot_data['Area'].min())
    plot_max_area = float(plot_data['Area'].max())
    selected_plot_area = st.sidebar.slider(
        "Select Area (sqft)",
        min_value=plot_min_area,
        max_value=plot_max_area,
        value=(plot_min_area, plot_max_area),
        step=1.0
    )
    
    # Price per Cent Range Slider
    plot_min_price_cent = float(plot_data['Price per cent'].min())
    plot_max_price_cent = float(plot_data['Price per cent'].max())
    selected_plot_price_cent = st.sidebar.slider(
        "Select Price per Cent Range",
        min_value=plot_min_price_cent,
        max_value=plot_max_price_cent,
        value=(plot_min_price_cent, plot_max_price_cent),
        step=1000.0
    )
    
    # Price to Price per Cent Ratio Slider
    plot_min_ratio = float(plot_data['price_to_price_per_cent_ratio'].min())
    plot_max_ratio = float(plot_data['price_to_price_per_cent_ratio'].max())
    selected_plot_ratio = st.sidebar.slider(
        "Select Price to Price per Cent Ratio",
        min_value=0.0,
        max_value=round(plot_max_ratio, 2),
        value=(0.0, round(plot_max_ratio, 2)),
        step=0.1
    )
    
    # Distance Sliders
    plot_distance_columns = [
        'distance_to_technopark',
        'distance_to_agasthyamalai_hills',
        'distance_to_ponmudi_hills',
        'distance_to_nearest_beach',
        'distance_to_nearest_lake'
    ]
    
    plot_distance_filters = {}
    for col in plot_distance_columns:
        min_dist = float(plot_data[col].min())
        max_dist = float(plot_data[col].max())
        plot_distance_filters[col] = st.sidebar.slider(
            f"Select {col.replace('_', ' ').title()} (km)",
            min_value=min_dist,
            max_value=max_dist,
            value=(min_dist, max_dist),
            step=1.0
        )
    
    # ---------------------------
    # Apply Filters to Plot Data
    # ---------------------------
    filtered_plot_data = plot_data[
        (plot_data['Location'].isin(selected_plot_locations)) &
        (plot_data['density'].isin(selected_plot_density)) &
        (plot_data['Price'] >= selected_plot_price[0]) &
        (plot_data['Price'] <= selected_plot_price[1]) &
        (plot_data['Area'] >= selected_plot_area[0]) &
        (plot_data['Area'] <= selected_plot_area[1]) &
        (plot_data['Price per cent'] >= selected_plot_price_cent[0]) &
        (plot_data['Price per cent'] <= selected_plot_price_cent[1]) &
        (plot_data['price_to_price_per_cent_ratio'] >= selected_plot_ratio[0]) &
        (plot_data['price_to_price_per_cent_ratio'] <= selected_plot_ratio[1])
    ]
    
    for col, (min_val, max_val) in plot_distance_filters.items():
        filtered_plot_data = filtered_plot_data[
            (filtered_plot_data[col] >= min_val) & (filtered_plot_data[col] <= max_val)
        ]
    
    # ---------------------------
    # Sidebar Summary for Plot Dashboard
    # ---------------------------
    st.sidebar.subheader("📊 Plot Summary")
    st.sidebar.write(f"**Total Plots:** {len(plot_data)}")
    st.sidebar.write(f"**Filtered Plots:** {len(filtered_plot_data)}")
    
    # ---------------------------
    # Key Performance Indicators (KPIs) for Plot Dashboard
    # ---------------------------
    st.header("🚀 Key Performance Indicators")
    plot_kpi1, plot_kpi2, plot_kpi3, plot_kpi4 = st.columns(4)
    plot_kpi1.metric("Total Plots", len(filtered_plot_data))
    plot_kpi2.metric("Average Price", f"${filtered_plot_data['Price'].mean():,.2f}")
    plot_kpi3.metric("Median Area", f"{filtered_plot_data['Area'].median():,.2f} sqft")
    plot_kpi4.metric("Average Price per Sqft", f"${filtered_plot_data['Price per cent'].mean():,.2f}")
    
    # ---------------------------
    # Interactive Map for Plot Dashboard
    # ---------------------------
    st.header("🗺️ Plots Geographical Distribution")
    if not filtered_plot_data.empty:
        fig_plot_map = px.scatter_mapbox(
            filtered_plot_data,
            lat="Latitude",
            lon="Longitude",
            hover_name="Location",
            hover_data={
                "Price": True,
                "Area": True,
                "Price per cent": True,
                "distance_to_technopark": True,
                "distance_to_nearest_beach": True
            },
            color="Price",
            size="Area",
            color_continuous_scale=px.colors.cyclical.IceFire,
            size_max=15,
            zoom=10,
            height=600,
            title="Geographical Distribution of Plots"
        )
        fig_plot_map.update_layout(mapbox_style="open-street-map")
        fig_plot_map.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
        st.plotly_chart(fig_plot_map, use_container_width=True)
    else:
        st.warning("No data available for the selected filters.")
    
    # ---------------------------
    # Detailed Analytics for Plot Dashboard
    # ---------------------------
    st.header("📈 Detailed Analytics")
    
    # 1. Price Distribution by Location
    st.subheader("💲 Price Distribution by Location")
    plot_fig_price_dist = px.box(
        filtered_plot_data,
        x='Location',
        y='Price',
        points='outliers',
        title="Price Distribution Across Locations",
        labels={"Price": "Price ($)", "Location": "Location"},
        color='Location',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(plot_fig_price_dist, use_container_width=True)
    
    # 2. Area vs. Price with Regression Line
    st.subheader("📐 Area vs. Price")
    try:
        plot_fig_scatter = px.scatter(
            filtered_plot_data,
            x='Area',
            y='Price',
            trendline='ols',
            hover_data=['Price per cent', 'Location'],
            title="Relationship Between Area and Price",
            labels={"Area": "Area (sqft)", "Price": "Price ($)"},
            color='Location',
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        st.plotly_chart(plot_fig_scatter, use_container_width=True)
    except ModuleNotFoundError:
        st.warning("`statsmodels` is not installed. Install it to enable trendlines in scatter plots.")
    
    # 3. Price to Price per Cent Ratio Analysis
    st.subheader("🔍 Price to Price per Cent Ratio Analysis")
    plot_fig_ratio = px.histogram(
        filtered_plot_data,
        x='price_to_price_per_cent_ratio',
        nbins=20,
        title="Distribution of Price to Price per Cent Ratios",
        labels={"price_to_price_per_cent_ratio": "Price to Price per Cent Ratio"},
        color_discrete_sequence=['teal']
    )
    st.plotly_chart(plot_fig_ratio, use_container_width=True)
    
    # ---------------------------
    # Comparative Analysis for Plot Dashboard
    # ---------------------------
    st.header("🔄 Comparative Analysis Across Locations")
    plot_comparison_metrics = ['Price', 'Price per cent', 'Area']
    plot_location_summary = filtered_plot_data.groupby('Location').agg(
        Average_Price=('Price', 'mean'),
        Average_Price_per_Cent=('Price per cent', 'mean'),
        Total_Plots=('Price', 'count'),
        Average_Area=('Area', 'mean'),
        Median_Area=('Area', 'median')
    ).reset_index()
    
    plot_fig_comparison = go.Figure()
    
    plot_fig_comparison.add_trace(go.Bar(
        x=plot_location_summary['Location'],
        y=plot_location_summary['Average_Price'],
        name='Average Price',
        marker_color='indianred'
    ))
    plot_fig_comparison.add_trace(go.Bar(
        x=plot_location_summary['Location'],
        y=plot_location_summary['Average_Price_per_Cent'],
        name='Avg Price per Cent',
        marker_color='lightsalmon'
    ))
    plot_fig_comparison.add_trace(go.Bar(
        x=plot_location_summary['Location'],
        y=plot_location_summary['Total_Plots'],
        name='Total Plots',
        marker_color='darkseagreen'
    ))
    
    plot_fig_comparison.update_layout(
        barmode='group',
        title="Comparison of Key Metrics Across Locations",
        xaxis_title="Location",
        yaxis_title="Value",
        legend_title="Metrics",
        template="plotly_white"
    )
    st.plotly_chart(plot_fig_comparison, use_container_width=True)
    
    # ---------------------------
    # Listings Data Table for Plot Dashboard
    # ---------------------------
    st.header("📋 Listings Data Table")
    st.subheader("Filter and Sort Listings")
    
    # Convert Url to clickable links
    plot_filtered_data_display = filtered_plot_data.copy()
    plot_filtered_data_display['Url'] = plot_filtered_data_display['Url'].apply(make_clickable)
    
    # Select columns to display
    plot_display_columns = [
        'Location', 'Price', 'Area', 'Price per cent', 'density',
        'price_to_price_per_cent_ratio', 'beach_proximity', 'lake_proximity', 'Url'
    ]
    
    # Display as HTML table for clickable links
    st.markdown(
        plot_filtered_data_display[plot_display_columns].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    
    # ---------------------------
    # Export Option for Plot Dashboard
    # ---------------------------
    st.header("💾 Export Data")
    st.markdown("Download the filtered plot data for further analysis.")
    
    def convert_plot_df(df):
        return df.to_csv(index=False).encode('utf-8')
    
    plot_csv = convert_plot_df(filtered_plot_data)
    
    st.download_button(
        label="📥 Download Plot CSV",
        data=plot_csv,
        file_name='filtered_plot_data.csv',
        mime='text/csv',
    )

# ---------------------------
# Footer (Common for Both Dashboards)
# ---------------------------
st.markdown("---")
st.markdown("Developed by [Your Name](https://yourwebsite.com) | © 2024 Real Estate Insights")
