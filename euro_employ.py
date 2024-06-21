import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import pycountry
from PIL import Image, UnidentifiedImageError
import requests
from io import BytesIO

# Load the data
file_path = 'estat_htec_emp_nisced2.tsv'  # Update this path
data = pd.read_csv(file_path, sep='\t')

# Clean and transform the data
data.columns = data.columns.str.strip()
data.rename(columns={'freq,nace_r2,unit,isced11,geo\\TIME_PERIOD': 'category'}, inplace=True)
data[['freq', 'nace_r2', 'unit', 'isced11', 'geo']] = data['category'].str.split(',', expand=True)
data.drop(columns=['category'], inplace=True)
data_long = pd.melt(data, id_vars=['freq', 'nace_r2', 'unit', 'isced11', 'geo'], var_name='year', value_name='employment_rate')
data_long['employment_rate'] = data_long['employment_rate'].str.replace(' b', '').str.replace(' p', '')
data_long['employment_rate'] = pd.to_numeric(data_long['employment_rate'], errors='coerce')
relevant_sectors = ['C_HTC', 'HTC', 'KIS', 'KIS_HTC']
data_filtered = data_long[(data_long['nace_r2'].isin(relevant_sectors)) & (data_long['unit'] == 'PC_EMP')]

# Calculate metrics
metrics = data_filtered.groupby(['year', 'isced11'])['employment_rate'].agg(['mean', 'std']).reset_index()
metrics_filtered = metrics[~metrics['isced11'].isin(['TOTAL', 'NRP'])]

# Country code to country name mapping
def get_country_name(code):
    if code == 'EL':
        code = 'GR'  # Correcting Greece code
    elif code == 'UK':
        code = 'GB'  # Correcting UK code
    elif code == 'EU27_2020':
        return 'European Union (27 countries)'
    elif code == 'EA20':
        return 'Euro Area (20 countries)'
    try:
        country = pycountry.countries.get(alpha_2=code)
        return country.name
    except:
        return code

# Country code to flag URL mapping
def get_flag_url(code):
    if code in ['EU27_2020', 'EA20']:
        return "https://upload.wikimedia.org/wikipedia/commons/b/b7/Flag_of_Europe.svg"
    if code == 'EL':
        code = 'GR'  # Correcting Greece code
    elif code == 'UK':
        code = 'GB'  # Correcting UK code
    return f"https://flagcdn.com/w40/{code.lower()}.png"


# Function to fetch and display SVG images
def display_svg(url):
    response = requests.get(url)
    response.raise_for_status()
    image_bytes = response.content
    return Image.open(BytesIO(image_bytes))


# Streamlit app
st.set_page_config(page_title="Euro Employ Tech by Education", page_icon=":bar_chart:", layout="wide")

st.title("Employment in Technology and Knowledge-Intensive Sectors")
st.write("""
**Research question:** How has employment in technology and knowledge-intensive sectors evolved over time for different levels of education in Europe?
""")

# About me
st.sidebar.title("About Me")
st.sidebar.info("""
- Name: Reza Maliki Akbar 
- Email: [rakb0002@student.monash.edu](mailto:rakb0002@student.monash.edu) 
- Student Number: 34292020 
- Master of Cybersecurity, Monash University
""")

# Dataset remarks
st.header("Dataset Remarks")
st.write(f"The dataset contains information about employment rates in technology and knowledge-intensive sectors for various education levels (ISCED categories) across multiple European countries.")
st.write(f"**Number of unique ISCED categories:** {data_filtered['isced11'].nunique()}")
st.write(f"**Number of unique countries (geo):** {data_filtered['geo'].nunique()}")

st.write("""
**ISCED Levels Explained:**
- **ISCED 0-2:** Lower levels of education (early childhood to lower secondary)
- **ISCED 3-4:** Upper secondary to post-secondary non-tertiary education
- **ISCED 5-8:** Tertiary education (short-cycle tertiary to doctoral level)
""")

# Interactive elements
selected_education_levels = st.multiselect(
    'Select Education Levels (ISCED)',
    options=metrics_filtered['isced11'].unique(),
    default=metrics_filtered['isced11'].unique()
)

selected_countries = st.multiselect(
    'Select Countries',
    options=data_filtered['geo'].unique(),
    default=data_filtered['geo'].unique(),
    format_func=lambda x: f"{get_country_name(x)} ({x})"
)

# Display selected countries with flags in a grid
st.write("### Selected Countries and Flags")
num_columns = 6  # You can adjust this number based on your preference
num_rows = (len(selected_countries) + num_columns - 1) // num_columns

for row in range(num_rows):
    cols = st.columns(num_columns)
    for col_index in range(num_columns):
        country_index = row * num_columns + col_index
        if country_index < len(selected_countries):
            country_code = selected_countries[country_index]
            country_name = get_country_name(country_code)
            flag_url = get_flag_url(country_code)
            try:
                response = requests.get(flag_url)
                response.raise_for_status()  # Ensure we handle HTTP errors
                img = Image.open(BytesIO(response.content))
                cols[col_index].image(img, width=40)
            except (requests.exceptions.RequestException, UnidentifiedImageError):
                cols[col_index].write(f"{country_name} (flag not available)")
            cols[col_index].write(country_name)

# Filter data based on selections
filtered_data = data_filtered[data_filtered['isced11'].isin(selected_education_levels) & data_filtered['geo'].isin(selected_countries)]
filtered_metrics = metrics_filtered[metrics_filtered['isced11'].isin(selected_education_levels)]

# Plotting
st.header("Mean Employment Rates Over Time by Education Level")
fig, ax = plt.subplots(figsize=(12, 8))
for level in filtered_metrics['isced11'].unique():
    subset = filtered_metrics[filtered_metrics['isced11'] == level]
    ax.plot(subset['year'], subset['mean'], label=level)
ax.set_xlabel('Year')
ax.set_ylabel('Mean Employment Rate (%)')
ax.set_title('Employment Rates in Technology and Knowledge-Intensive Sectors by Education Level')
ax.legend(title='Education Level')
ax.grid(True)
st.pyplot(fig)

# Table for mean
st.header("Mean Employment Rates by Education Level and Year")
mean_table = filtered_metrics.pivot(index='year', columns='isced11', values='mean')
st.dataframe(mean_table)

# Additional visualizations
st.header("Standard Deviation of Employment Rates Over Time by Education Level")
fig, ax = plt.subplots(figsize=(12, 8))
for level in filtered_metrics['isced11'].unique():
    subset = filtered_metrics[metrics_filtered['isced11'] == level]
    ax.plot(subset['year'], subset['std'], label=level)
ax.set_xlabel('Year')
ax.set_ylabel('Standard Deviation of Employment Rate (%)')
ax.set_title('Variability in Employment Rates by Education Level')
ax.legend(title='Education Level')
ax.grid(True)
st.pyplot(fig)

# Table for std
st.header("Standard Deviation of Employment Rates by Education Level and Year")
std_table = filtered_metrics.pivot(index='year', columns='isced11', values='std')
st.dataframe(std_table)

st.header("Box Plot of Employment Rates by Education Level")
fig, ax = plt.subplots(figsize=(12, 8))
filtered_data_box = filtered_data.dropna(subset=['employment_rate'])
filtered_data_box['year'] = filtered_data_box['year'].astype(int)
filtered_data_box.boxplot(column='employment_rate', by='isced11', ax=ax, grid=False)
ax.set_xlabel('Education Level')
ax.set_ylabel('Employment Rate (%)')
ax.set_title('Box Plot of Employment Rates by Education Level')
fig.suptitle('')
st.pyplot(fig)

# Display Data Table
st.header("Data Table")
st.write(filtered_metrics)



