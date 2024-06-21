import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# Load the data
file_path = 'path_to_your_file/estat_htec_emp_nisced2.tsv'  # Update this path
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

# Streamlit app
st.title("Employment in Technology and Knowledge-Intensive Sectors")
st.write("""
How has employment in technology and knowledge-intensive sectors evolved over time for different levels of education in Europe?
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
- **ISCED 9:** Not applicable (used for miscellaneous categories or unknown education levels)
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
    default=data_filtered['geo'].unique()
)

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

# Additional visualizations
st.header("Standard Deviation of Employment Rates Over Time by Education Level")
fig, ax = plt.subplots(figsize=(12, 8))
for level in filtered_metrics['isced11'].unique():
    subset = filtered_metrics[filtered_metrics['isced11'] == level]
    ax.plot(subset['year'], subset['std'], label=level)
ax.set_xlabel('Year')
ax.set_ylabel('Standard Deviation of Employment Rate (%)')
ax.set_title('Variability in Employment Rates by Education Level')
ax.legend(title='Education Level')
ax.grid(True)
st.pyplot(fig)

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
