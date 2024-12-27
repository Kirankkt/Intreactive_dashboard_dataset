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
    
    # Multi-select Location Filter with Improved UX
    prop_locations = sorted(property_data['Standardized_Location_Name'].unique())
    selected_prop_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=prop_locations,
        default=None  # No default selection
    )
    
    # Handle 'Select All' functionality
    if not selected_prop_locations:
        filtered_prop_data = property_data.copy()
    else:
        filtered_prop_data = property_data[property_data['Standardized_Location_Name'].isin(selected_prop_locations)]
    
    # Multi-select Bedrooms Filter
    prop_beds_options = sorted(property_data['Plot__Beds'].unique())
    selected_prop_beds = st.sidebar.multiselect(
        "Select Number of Bedrooms",
        options=prop_beds_options,
        default=prop_beds_options  # Select all by default
    )
    
    if selected_prop_beds:
        filtered_prop_data = filtered_prop_data[filtered_prop_data['Plot__Beds'].isin(selected_prop_beds)]
    
    # Price Range Slider
    prop_min_price = int(property_data['Plot__Price'].min())
    prop_max_price = int(property_data['Plot__Price'].max())
    selected_prop_price = st.sidebar.slider(
        "Select Price Range (₹)",
        min_value=prop_min_price,
        max_value=prop_max_price,
        value=(prop_min_price, prop_max_price),
        step=10000
    )
    
    filtered_prop_data = filtered_prop_data[
        (filtered_prop_data['Plot__Price'] >= selected_prop_price[0]) &
        (filtered_prop_data['Plot__Price'] <= selected_prop_price[1])
    ]
    
    # Plot Area in Cents Range Slider
    prop_min_plot_area_cents = float(property_data['Plot__Area_Cents'].min())
    prop_max_plot_area_cents = float(property_data['Plot__Area_Cents'].max())
    selected_prop_plot_area_cents = st.sidebar.slider(
        "Select Plot Area (Cents)",
        min_value=prop_min_plot_area_cents,
        max_value=prop_max_plot_area_cents,
        value=(prop_min_plot_area_cents, prop_max_plot_area_cents),
        step=0.1
    )
    
    filtered_prop_data = filtered_prop_data[
        (filtered_prop_data['Plot__Area_Cents'] >= selected_prop_plot_area_cents[0]) &
        (filtered_prop_data['Plot__Area_Cents'] <= selected_prop_plot_area_cents[1])
    ]
    
    # Build Area Range Slider
    prop_min_build_area = float(property_data['Build__Area'].min())
    prop_max_build_area = float(property_data['Build__Area'].max())
    selected_prop_build_area = st.sidebar.slider(
        "Select Build Area (sqft)",
        min_value=prop_min_build_area,
        max_value=prop_max_build_area,
        value=(prop_min_build_area, prop_max_build_area),
        step=50.0
    )
    
    filtered_prop_data = filtered_prop_data[
        (filtered_prop_data['Build__Area'] >= selected_prop_build_area[0]) &
        (filtered_prop_data['Build__Area'] <= selected_prop_build_area[1])
    ]
    
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
    
    filtered_prop_data = filtered_prop_data[
        (filtered_prop_data['Build_to_Plot_Ratio'] >= selected_prop_ratio[0]) &
        (filtered_prop_data['Build_to_Plot_Ratio'] <= selected_prop_ratio[1])
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
    prop_kpi1, prop_kpi2, prop_kpi3 = st.columns(3)
    prop_kpi1.metric("Average Price (₹)", f"₹{filtered_prop_data['Plot__Price'].mean():,.2f}")
    prop_kpi2.metric("Median Plot Area (Cents)", f"{filtered_prop_data['Plot__Area_Cents'].median():,.2f} cents")
    prop_kpi3.metric("Number of Listings", len(filtered_prop_data))
    
    prop_kpi4, prop_kpi5 = st.columns(2)
    
    # Updated Average Price per Cent Calculation
    total_price_prop = filtered_prop_data['Plot__Price'].sum()
    total_area_prop = filtered_prop_data['Plot__Area_Cents'].sum()
    average_price_per_cent_prop = total_price_prop / total_area_prop if total_area_prop != 0 else 0
    prop_kpi4.metric("Average Price per Cent (₹)", f"₹{average_price_per_cent_prop:,.2f}")
    
    prop_kpi5.metric("Average Build Area (sqft)", f"{filtered_prop_data['Build__Area'].mean():,.2f} sqft")
    
    # ---------------------------
    # Overview of Major Locations for Property Dashboard
    # ---------------------------
    st.header("📊 Overview of Major Locations")
    # Updated Average_Price_per_Cent calculation
    prop_location_summary = filtered_prop_data.groupby('Standardized_Location_Name').agg(
        Average_Price=('Plot__Price', 'mean'),
        Sum_Price=('Plot__Price', 'sum'),
        Sum_Area=('Plot__Area_Cents', 'sum'),
        Total_Listings=('Plot__Price', 'count'),
        Average_Build_Area=('Build__Area', 'mean'),
        Average_Plot_Area_Cents=('Plot__Area_Cents', 'mean')
    ).reset_index()
    
    prop_location_summary['Average_Price_per_Cent'] = prop_location_summary['Sum_Price'] / prop_location_summary['Sum_Area']
    
    prop_summary_chart = px.bar(
        prop_location_summary,
        x='Standardized_Location_Name',
        y='Average_Price',
        hover_data=['Average_Price_per_Cent', 'Total_Listings', 'Average_Build_Area', 'Average_Plot_Area_Cents'],
        labels={"Average_Price": "Average Price (₹)"},
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
        labels={"Plot__Price": "Price (₹)", "Standardized_Location_Name": "Location"},
        color='Standardized_Location_Name',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(prop_fig_price_dist, use_container_width=True)
    
    # 2. Plot Area (Cents) vs. Price with Regression Line
    st.subheader("📐 Plot Area (Cents) vs. Price")
    try:
        prop_fig_scatter = px.scatter(
            filtered_prop_data,
            x='Plot__Area_Cents',
            y='Plot__Price',
            trendline='ols',
            hover_data=['Price_per_sqft', 'Standardized_Location_Name'],
            title="Relationship Between Plot Area (Cents) and Price",
            labels={"Plot__Area_Cents": "Plot Area (Cents)", "Plot__Price": "Price (₹)"},
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
    st.header("🔄 Comparative Analysis")
    
    # Determine Top and Bottom Regions based on Average Price
    top_regions = prop_location_summary.sort_values(by='Average_Price', ascending=False).head(5)
    bottom_regions = prop_location_summary.sort_values(by='Average_Price', ascending=True).head(5)
    
    # Selected Regions
    selected_regions = selected_prop_locations if selected_prop_locations else prop_locations
    
    # Extract data for selected, top, and bottom regions
    selected_data = prop_location_summary[prop_location_summary['Standardized_Location_Name'].isin(selected_regions)]
    comparison_data = pd.concat([selected_data, top_regions, bottom_regions]).drop_duplicates()
    
    # Remove duplicates if any selected region is also in top or bottom
    comparison_data = comparison_data.reset_index(drop=True)
    
    # Create Grouped Bar Chart
    prop_fig_comparison = go.Figure()
    
    metrics = ['Average_Price', 'Average_Price_per_Cent', 'Total_Listings']
    colors = ['indianred', 'lightsalmon', 'darkseagreen']
    
    for metric, color in zip(metrics, colors):
        prop_fig_comparison.add_trace(go.Bar(
            x=comparison_data['Standardized_Location_Name'],
            y=comparison_data[metric],
            name=metric.replace('_', ' '),
            marker_color=color
        ))
    
    prop_fig_comparison.update_layout(
        barmode='group',
        title="Comparison of Key Metrics Across Locations",
        xaxis_title="Location",
        yaxis_title="Value",
        legend_title="Metrics",
        template="plotly_white",
        height=600
    )
    st.plotly_chart(prop_fig_comparison, use_container_width=True)
    
    # ---------------------------
    # Listings Data Table for Property Dashboard
    # ---------------------------
    st.header("📋 Listings Data Table")
    
    if selected_prop_locations:
        st.subheader("View Listings for Selected Location(s)")
        
        # Convert Plot__url to clickable links
        prop_filtered_data_display = filtered_prop_data.copy()
        prop_filtered_data_display['Plot__url'] = prop_filtered_data_display['Plot__url'].apply(make_clickable)
        
        # Select columns to display
        prop_display_columns = [
            'Standardized_Location_Name', 'Plot__Price', 'Plot__Beds', 'Build__Area',
            'Plot__Area_Cents', 'Price_per_sqft', 'Price_per_cent', 'Build_to_Plot_Ratio',
            'Total_Area', 'Plot__DESC', 'Plot__url'
        ]
        
        # Display as HTML table for clickable links
        st.markdown(
            prop_filtered_data_display[prop_display_columns].to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
    else:
        st.info("Please select at least one location to view the listings.")
    
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
    
    # Multi-select Location Filter with Improved UX
    plot_locations = sorted(plot_data['Location'].unique())
    selected_plot_locations = st.sidebar.multiselect(
        "Select Location(s)",
        options=plot_locations,
        default=None  # No default selection
    )
    
    # Handle 'Select All' functionality
    if not selected_plot_locations:
        filtered_plot_data = plot_data.copy()
    else:
        filtered_plot_data = plot_data[plot_data['Location'].isin(selected_plot_locations)]
    
    # Multi-select Density Filter
    plot_density_options = sorted(plot_data['density'].unique())
    selected_plot_density = st.sidebar.multiselect(
        "Select Density",
        options=plot_density_options,
        default=plot_density_options  # Select all by default
    )
    
    if selected_plot_density:
        filtered_plot_data = filtered_plot_data[filtered_plot_data['density'].isin(selected_plot_density)]
    
    # Price Range Slider
    plot_min_price = int(plot_data['Price'].min())
    plot_max_price = int(plot_data['Price'].max())
    selected_plot_price = st.sidebar.slider(
        "Select Price Range (₹)",
        min_value=plot_min_price,
        max_value=plot_max_price,
        value=(plot_min_price, plot_max_price),
        step=10000
    )
    
    filtered_plot_data = filtered_plot_data[
        (filtered_plot_data['Price'] >= selected_plot_price[0]) &
        (filtered_plot_data['Price'] <= selected_plot_price[1])
    ]
    
    # Area Range Slider (Assuming 'Area' is in Cents)
    plot_min_area = float(plot_data['Area'].min())
    plot_max_area = float(plot_data['Area'].max())
    selected_plot_area = st.sidebar.slider(
        "Select Area (Cents)",
        min_value=plot_min_area,
        max_value=plot_max_area,
        value=(plot_min_area, plot_max_area),
        step=0.1
    )
    
    filtered_plot_data = filtered_plot_data[
        (filtered_plot_data['Area'] >= selected_plot_area[0]) &
        (filtered_plot_data['Area'] <= selected_plot_area[1])
    ]
    
    # Price per Cent Range Slider
    plot_min_price_cent = float(plot_data['Price per cent'].min())
    plot_max_price_cent = float(plot_data['Price per cent'].max())
    selected_plot_price_cent = st.sidebar.slider(
        "Select Price per Cent Range (₹)",
        min_value=plot_min_price_cent,
        max_value=plot_max_price_cent,
        value=(plot_min_price_cent, plot_max_price_cent),
        step=1000.0
    )
    
    filtered_plot_data = filtered_plot_data[
        (filtered_plot_data['Price per cent'] >= selected_plot_price_cent[0]) &
        (filtered_plot_data['Price per cent'] <= selected_plot_price_cent[1])
    ]
    
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
    
    filtered_plot_data = filtered_plot_data[
        (filtered_plot_data['price_to_price_per_cent_ratio'] >= selected_plot_ratio[0]) &
        (filtered_plot_data['price_to_price_per_cent_ratio'] <= selected_plot_ratio[1])
    ]
    
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
    
    for col, (min_val, max_val) in plot_distance_filters.items():
        filtered_plot_data = filtered_plot_data[
            (filtered_plot_data[col] >= min_val) &
            (filtered_plot_data[col] <= max_val)
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
    plot_kpi1, plot_kpi2, plot_kpi3 = st.columns(3)
    plot_kpi1.metric("Average Price (₹)", f"₹{filtered_plot_data['Price'].mean():,.2f}")
    plot_kpi2.metric("Median Plot Area (Cents)", f"{filtered_plot_data['Area'].median():,.2f} cents")
    plot_kpi3.metric("Number of Listings", len(filtered_plot_data))
    
    plot_kpi4, plot_kpi5 = st.columns(2)
    
    # Updated Average Price per Cent Calculation
    total_price_plot = filtered_plot_data['Price'].sum()
    total_area_plot = filtered_plot_data['Area'].sum()
    average_price_per_cent_plot = total_price_plot / total_area_plot if total_area_plot != 0 else 0
    plot_kpi4.metric("Average Price per Cent (₹)", f"₹{average_price_per_cent_plot:,.2f}")
    
    # Uncomment and update if needed
    # plot_kpi5.metric("Average Build Area (sqft)", f"{filtered_plot_data['price_to_price_per_cent_ratio'].mean():,.2f} sqft")
    
    # ---------------------------
    # Interactive Map for Plot Dashboard with Price-Based Color Coding
    # ---------------------------
    st.header("🗺️ Plots Geographical Distribution")
    if not filtered_plot_data.empty:
        try:
            # Define price per cent bins for color coding using quantiles
            price_bins = [
                filtered_plot_data['Price per cent'].min(),
                filtered_plot_data['Price per cent'].quantile(0.25),
                filtered_plot_data['Price per cent'].median(),
                filtered_plot_data['Price per cent'].quantile(0.75),
                filtered_plot_data['Price per cent'].max()
            ]
            # Drop duplicate bin edges
            unique_bins = sorted(set(price_bins))
            if len(unique_bins) < len(price_bins):
                # Adjust the number of bins and labels accordingly
                price_bins = unique_bins
                num_bins = len(price_bins) - 1
                price_labels = [f"₹{int(price_bins[i])} - ₹{int(price_bins[i+1])}" for i in range(num_bins)]
            else:
                price_labels = [f"₹{int(price_bins[i])} - ₹{int(price_bins[i+1])}" for i in range(len(price_bins)-1)]
            
            # Assign Price_Category
            filtered_plot_data['Price_Category'] = pd.cut(
                filtered_plot_data['Price per cent'],
                bins=price_bins,
                labels=price_labels,
                include_lowest=True,
                duplicates='drop'
            )
            
            # Create color map
            color_map = {label: color for label, color in zip(price_labels, px.colors.qualitative.Safe)}
            
            fig_plot_map = px.scatter_mapbox(
                filtered_plot_data,
                lat="Latitude",
                lon="Longitude",
                hover_name="Location",
                hover_data={
                    "Price": True,
                    "Area": True,
                    "Price per cent": True,
                    "density": True,
                    "price_to_price_per_cent_ratio": True
                },
                color="Price_Category",
                color_discrete_map=color_map,
                size="Price per cent",
                size_max=15,
                zoom=10,
                height=600,
                title="Geographical Distribution of Plots with Price Categories",
                labels={"Price_Category": "Price per Cent (₹)"}
            )
            fig_plot_map.update_layout(
                mapbox_style="open-street-map",
                margin={"r":0,"t":50,"l":0,"b":0},
                legend_title_text='Price per Cent (₹)'
            )
            
            # Add captions and explanations
            st.plotly_chart(fig_plot_map, use_container_width=True)
            st.caption("**Note:** Each plot is color-coded based on its Price per Cent. The size of the marker represents the Price per Cent value.")
        except ValueError as e:
            st.error(f"Error in creating Price Categories: {e}")
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
        labels={"Price": "Price (₹)", "Location": "Location"},
        color='Location',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(plot_fig_price_dist, use_container_width=True)
    
    # 2. Area (Cents) vs. Price with Regression Line
    st.subheader("📐 Area (Cents) vs. Price")
    try:
        plot_fig_scatter = px.scatter(
            filtered_plot_data,
            x='Area',
            y='Price',
            trendline='ols',
            hover_data=['Price per cent', 'Location'],
            title="Relationship Between Area (Cents) and Price",
            labels={"Area": "Area (Cents)", "Price": "Price (₹)"},
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
    st.header("🔄 Comparative Analysis")
    
    # Determine Top and Bottom Locations based on Average Price
    plot_location_summary = filtered_plot_data.groupby('Location').agg(
        Average_Price=('Price', 'mean'),
        Sum_Price=('Price', 'sum'),
        Sum_Area=('Area', 'sum'),
        Total_Plots=('Price', 'count'),
        Average_Area=('Area', 'mean'),
        Median_Area=('Area', 'median')
    ).reset_index()
    
    # Calculate Average_Price_per_Cent as Sum_Price / Sum_Area
    plot_location_summary['Average_Price_per_Cent'] = plot_location_summary['Sum_Price'] / plot_location_summary['Sum_Area']
    
    top_plot_regions = plot_location_summary.sort_values(by='Average_Price', ascending=False).head(5)
    bottom_plot_regions = plot_location_summary.sort_values(by='Average_Price', ascending=True).head(5)
    
    # Selected Regions
    selected_plot_regions = selected_plot_locations if selected_plot_locations else plot_locations
    
    # Extract data for selected, top, and bottom regions
    selected_plot_data = plot_location_summary[plot_location_summary['Location'].isin(selected_plot_regions)]
    comparison_plot_data = pd.concat([selected_plot_data, top_plot_regions, bottom_plot_regions]).drop_duplicates()
    
    # Remove duplicates if any selected region is also in top or bottom
    comparison_plot_data = comparison_plot_data.reset_index(drop=True)
    
    # Create Grouped Bar Chart
    plot_fig_comparison = go.Figure()
    
    metrics = ['Average_Price', 'Average_Price_per_Cent', 'Total_Plots']
    colors = ['indianred', 'lightsalmon', 'darkseagreen']
    
    for metric, color in zip(metrics, colors):
        plot_fig_comparison.add_trace(go.Bar(
            x=comparison_plot_data['Location'],
            y=comparison_plot_data[metric],
            name=metric.replace('_', ' '),
            marker_color=color
        ))
    
    plot_fig_comparison.update_layout(
        barmode='group',
        title="Comparison of Key Metrics Across Locations",
        xaxis_title="Location",
        yaxis_title="Value",
        legend_title="Metrics",
        template="plotly_white",
        height=600
    )
    st.plotly_chart(plot_fig_comparison, use_container_width=True)
    
    # ---------------------------
    # Listings Data Table for Plot Dashboard
    # ---------------------------
    st.header("📋 Listings Data Table")
    
    if selected_plot_locations:
        st.subheader("View Listings for Selected Location(s)")
        
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
    else:
        st.info("Please select at least one location to view the listings.")
    
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
st.markdown("Developed by [Kiran KT] | © 2024 Real Estate Insights")
