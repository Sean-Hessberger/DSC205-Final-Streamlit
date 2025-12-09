import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------------------------------------------------------
# 1. Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Cost of Living Analysis")

st.title("U.S. Cost of Living and Economic Analysis Dashboard")
st.markdown("""
This dashboard analyzes cost of living, rent trends, tax burdens, and personal income 
across various regions and cities in the United States.
""")

# -----------------------------------------------------------------------------
# 2. Data Loading (Cached)
# -----------------------------------------------------------------------------
@st.cache_data
def load_and_clean_data():
    # Load raw data
    df_COL = pd.read_csv('https://raw.githubusercontent.com/Sean-Hessberger/DSC-205-Data-Sets/refs/heads/main/costofliving.csv')
    df_BEA = pd.read_csv('https://raw.githubusercontent.com/Sean-Hessberger/DSC-205-Data-Sets/refs/heads/main/Table.csv')
    df_zillow = pd.read_csv('https://raw.githubusercontent.com/Sean-Hessberger/DSC-205-Data-Sets/refs/heads/main/Metro_zori_uc_sfrcondomfr_sm_month.csv')
    df_tax = pd.read_csv('https://raw.githubusercontent.com/Sean-Hessberger/DSC-205-Data-Sets/refs/heads/main/Tax%20Per%20Capita.csv')

    # Dictionaries for Mapping
    state_to_region = {
        'CT': 'Northeast', 'ME': 'Northeast', 'MA': 'Northeast', 'NH': 'Northeast',
        'RI': 'Northeast', 'VT': 'Northeast', 'NJ': 'Northeast', 'NY': 'Northeast', 'PA': 'Northeast',
        'IL': 'Midwest', 'IN': 'Midwest', 'MI': 'Midwest', 'OH': 'Midwest', 'WI': 'Midwest',
        'IA': 'Midwest', 'KS': 'Midwest', 'MN': 'Midwest', 'MO': 'Midwest', 'NE': 'Midwest',
        'ND': 'Midwest', 'SD': 'Midwest',
        'DE': 'South', 'FL': 'South', 'GA': 'South', 'MD': 'South', 'NC': 'South',
        'SC': 'South', 'VA': 'South', 'WV': 'South', 'AL': 'South', 'KY': 'South',
        'MS': 'South', 'TN': 'South', 'AR': 'South', 'LA': 'South', 'OK': 'South',
        'TX': 'South', 'DC': 'South',
        'AZ': 'West', 'CO': 'West', 'ID': 'West', 'MT': 'West', 'NV': 'West',
        'NM': 'West', 'UT': 'West', 'WY': 'West', 'AK': 'West', 'CA': 'West',
        'HI': 'West', 'OR': 'West', 'WA': 'West'
    }

    state_abbreviation_to_name = {
        'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas', 'CA': 'California',
        'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware', 'FL': 'Florida', 'GA': 'Georgia',
        'HI': 'Hawaii', 'ID': 'Idaho', 'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa',
        'KS': 'Kansas', 'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
        'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi', 'MO': 'Missouri',
        'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada', 'NH': 'New Hampshire', 'NJ': 'New Jersey',
        'NM': 'New Mexico', 'NY': 'New York', 'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio',
        'OK': 'Oklahoma', 'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
        'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah', 'VT': 'Vermont',
        'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia', 'WI': 'Wisconsin', 'WY': 'Wyoming',
        'DC': 'District of Columbia'
    }
    
    name_to_abbreviation = {v: k for k, v in state_abbreviation_to_name.items()}

    # Clean Cost of Living Data
    df_COL_US = df_COL[df_COL['City'].str.contains('United States')].copy()
    df_COL_US['State_Abbr'] = df_COL_US['City'].str.extract(r',\s([A-Z]{2}),', expand=False)
    df_COL_US['State_Name'] = df_COL_US['State_Abbr'].map(state_abbreviation_to_name)
    df_COL_US['Region'] = df_COL_US['State_Abbr'].map(state_to_region)
    df_COL_US['City'] = df_COL_US['City'].str.replace(', United States', '')

    # Clean Bureau of Economic Analysis Data
    BEA_cols_to_keep = ['GeoFips', 'GeoName', '2020', '2021', '2022', '2023', '2024']
    df_BEA_clean = df_BEA[BEA_cols_to_keep].copy()
    df_BEA_clean['State_Abbr'] = df_BEA_clean['GeoName'].map(name_to_abbreviation)
    df_BEA_clean['Region'] = df_BEA_clean['State_Abbr'].map(state_to_region)

    # Clean Zillow Data
    df_zillow_copy = df_zillow.copy()
    metadata_cols = ['RegionID', 'SizeRank', 'RegionName', 'Region', 'StateName']
    date_cols = [col for col in df_zillow_copy.columns if col not in metadata_cols]
    
    # Calculate averages
    new_avg_data = {}
    for year in range(2020, 2025):
        cols_in_year = [col for col in date_cols if str(year) in col]
        new_avg_data[f'{year} Average'] = df_zillow_copy[cols_in_year].mean(axis=1)

    df_averages = pd.DataFrame(new_avg_data, index=df_zillow_copy.index)
    df_zillow_copy['Region'] = df_zillow_copy['StateName'].map(state_to_region)
    df_zillow_clean = df_zillow_copy[metadata_cols].join(df_averages).dropna()

    # Filter Intersection of Cities
    cities_COL = set(df_COL_US['City'])
    cities_Zillow = set(df_zillow_clean['RegionName'])
    common_cities = cities_COL.intersection(cities_Zillow)

    df_COL_filtered = df_COL_US[df_COL_US['City'].isin(common_cities)].copy()
    df_zillow_filtered = df_zillow_clean[df_zillow_clean['RegionName'].isin(common_cities)].copy()

    # Clean Tax Data
    df_tax['State_Abbr'] = df_tax['State'].map(name_to_abbreviation)
    df_tax['Region'] = df_tax['State_Abbr'].map(state_to_region)
    
    return df_COL_filtered, df_zillow_filtered, df_BEA_clean, df_tax

# Load data
df_COL_filtered, df_zillow_filtered, df_BEA_clean, df_tax = load_and_clean_data()

# -----------------------------------------------------------------------------
# 3. Sidebar
# -----------------------------------------------------------------------------
st.sidebar.header("Global Filters")

selected_year = st.sidebar.slider("Select Year:", 2020, 2024, 2020)

region_options = sorted(list(df_COL_filtered['Region'].unique()))
region_options.insert(0, 'All Regions')
selected_region = st.sidebar.selectbox("Select Region:", region_options)

if selected_region == 'All Regions':
    city_options = sorted(df_COL_filtered['City'].unique())
else:
    city_options = sorted(df_COL_filtered[df_COL_filtered['Region'] == selected_region]['City'].unique())

selected_city = st.sidebar.selectbox("Select City:", city_options)


# -----------------------------------------------------------------------------
# 4. Visualizations
# -----------------------------------------------------------------------------

# --- 1. Income Map ---
st.header(f"1. Income Potential: Personal Income by State ({selected_year})")

df_states = df_BEA_clean[df_BEA_clean['GeoName'] != 'United States'].copy()

# Filter by region if needed
if selected_region != 'All Regions':
    df_states = df_states[df_states['Region'] == selected_region]

fig_map = px.choropleth(
    df_states,
    locations='State_Abbr',
    locationmode="USA-states",
    color=str(selected_year),
    scope="usa",
    color_continuous_scale="Viridis",
    hover_name='GeoName',
    labels={str(selected_year): 'Personal Income (USD)'}
)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# --- 2. Cost of Living Bar Chart ---
st.header("2. Cost of Living Landscape")
st.subheader(f"Cost of Living Index Comparison ({selected_region})")

df_col_plot = df_COL_filtered.copy()
if selected_region != 'All Regions':
    df_col_plot = df_col_plot[df_col_plot['Region'] == selected_region]

df_col_plot = df_col_plot.sort_values(by='Cost of Living Index', ascending=False)

# Add color for the selected city
df_col_plot['Color'] = 'skyblue'
df_col_plot.loc[df_col_plot['City'] == selected_city, 'Color'] = 'red'

fig_col = px.bar(
    df_col_plot,
    x='City',
    y='Cost of Living Index',
    title='Cost of Living Index by City',
    color='Color',
    color_discrete_map={'skyblue': 'skyblue', 'red': 'red'}
)
st.plotly_chart(fig_col, use_container_width=True)


# --- 3. Scatter Plot ---
st.subheader(f"Value Analysis: Rent vs. Cost of Living ({selected_region})")

# Filter out the selected city to make it stand out
df_other_cities = df_col_plot[df_col_plot['City'] != selected_city]
df_selected_city = df_col_plot[df_col_plot['City'] == selected_city]

fig_scat = px.scatter(
    df_other_cities,
    x='Cost of Living Index',
    y='Rent Index',
    color='Local Purchasing Power Index',
    hover_name='City',
    title='Rent vs. Cost of Living (Color = Purchasing Power)',
    color_continuous_scale="Viridis",
)

# Add the selected city as a star
fig_scat.add_scatter(
    x=df_selected_city['Cost of Living Index'],
    y=df_selected_city['Rent Index'],
    mode='markers',
    marker=dict(color='red', size=15, symbol='star'),
    name=selected_city
)

st.plotly_chart(fig_scat, use_container_width=True)

st.markdown("---")

# --- 4. Tax Stacked Bar Chart ---
st.header(f"3. The 'Hidden' Costs: State Tax Breakdown ({selected_year})")

df_tax_filtered = df_tax.copy()
if selected_region != 'All Regions':
    df_tax_filtered = df_tax_filtered[df_tax_filtered['Region'] == selected_region]

# Columns for the specific year
tax_cols = [
    f"{selected_year} Property taxes(Per Capita)", 
    f"{selected_year} Sales and gross receipts taxes(Per Capita)", 
    f"{selected_year} Individual income(Per Capita)", 
]

# Melt for Plotly
plot_df = df_tax_filtered[['State'] + tax_cols]
plot_df_melted = plot_df.melt(id_vars='State', value_vars=tax_cols, var_name='Tax Type', value_name='Tax (USD)')

# Fix names for the legend
plot_df_melted['Tax Type'] = plot_df_melted['Tax Type'].str.replace(f"{selected_year} ", "").str.replace("(Per Capita)", "")

fig_tax = px.bar(
    plot_df_melted,
    x='State',
    y='Tax (USD)',
    color='Tax Type',
    title=f'Per Capita Tax Breakdown by State in {selected_year}'
)
st.plotly_chart(fig_tax, use_container_width=True)

st.markdown("---")

# --- 5. Deep Dive Trends ---
st.header(f"4. Deep Dive: {selected_city} Analysis")

# Get State Name for the selected city
state_name = df_COL_filtered[df_COL_filtered['City'] == selected_city]['State_Name'].values[0]

st.subheader(f"State-Level Personal Income Trend ({state_name})")

# Filter data for the state
state_income_data = df_BEA_clean[df_BEA_clean['GeoName'] == state_name]

# Prepare data for line chart
years = ['2020', '2021', '2022', '2023', '2024']
income_values = state_income_data[years].values[0]

df_income_trend = pd.DataFrame({'Year': years, 'Personal Income': income_values})

fig_income = px.line(
    df_income_trend, 
    x='Year', 
    y='Personal Income', 
    title=f"Personal Income Trend in {state_name}",
    markers=True
)
# Add red star for selected year
selected_year_data = df_income_trend[df_income_trend['Year'] == str(selected_year)]
fig_income.add_scatter(
    x=selected_year_data['Year'], 
    y=selected_year_data['Personal Income'],
    mode='markers',
    marker=dict(color='red', size=12, symbol='star'),
    name='Selected Year'
)
st.plotly_chart(fig_income, use_container_width=True)

# --- Rent and Specific Indices Side-by-Side ---
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"Rent Trend: {selected_city}")
    
    # Filter Zillow data
    rent_data = df_zillow_filtered[df_zillow_filtered["RegionName"] == selected_city]
    
    # Get values for years 2020-2024
    rent_vals = []
    years_int = [2020, 2021, 2022, 2023, 2024]
    for y in years_int:
        rent_vals.append(rent_data[f"{y} Average"].values[0])
        
    df_rent_trend = pd.DataFrame({'Year': years_int, 'Average Rent': rent_vals})
    
    fig_rent = px.line(
        df_rent_trend, 
        x='Year', 
        y='Average Rent', 
        markers=True,
        title=f"Average Rent Trend: {selected_city}"
    )
    st.plotly_chart(fig_rent, use_container_width=True)

with col2:
    st.subheader(f"Specific Cost Indices: {selected_city}")
    
    city_costs = df_COL_filtered[df_COL_filtered["City"] == selected_city]
    
    # Create simple dataframe for bar chart
    data = {
        'Index': ['Rent', 'Cost of Living', 'Groceries', 'Restaurant Price', 'Purchasing Power'],
        'Value': [
            city_costs['Rent Index'].values[0],
            city_costs['Cost of Living Index'].values[0],
            city_costs['Groceries Index'].values[0],
            city_costs['Restaurant Price Index'].values[0],
            city_costs['Local Purchasing Power Index'].values[0]
        ]
    }
    df_costs = pd.DataFrame(data)
    
    fig_indices = px.bar(
        df_costs, 
        x='Index', 
        y='Value', 
        color='Index',
        title='Cost Indices vs NYC Baseline (100)'
    )
    fig_indices.update_layout(showlegend=False)
    st.plotly_chart(fig_indices, use_container_width=True)