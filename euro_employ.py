import streamlit as st
import pandas as pd

# Ensure matplotlib is installed
import os
os.system('pip install matplotlib')

import matplotlib.pyplot as plt

st.title('Employment in Technology and Knowledge-Intensive Sectors by Level of Education')

# Load the data directly from the repository
file_path = '/mnt/data/estat_htec_emp_nisced2.tsv'
data = pd.read_csv(file_path, sep='\t')

# Clean and process the data
data.columns = data.columns.str.strip()  # Clean column names
data = data.rename(columns=lambda x: x.split('\\')[0])  # Remove extra characters from column names
data.replace(':', pd.NA, inplace=True)  # Handle missing values
data = data.dropna()  # Drop rows with missing values
for col in data.columns[5:]:
    data[col] = data[col].apply(lambda x: float(str(x).replace(' b', '')))

# Display the first few rows of the cleaned data
st.write(data.head())

# Transform data for easier plotting
data_long = pd.melt(data, id_vars=['freq', 'nace_r2', 'unit', 'isced11', 'geo'], var_name='Year', value_name='Employment')

# Calculate mean and standard deviation
mean_employment = data_long.groupby('isced11')['Employment'].mean()
std_employment = data_long.groupby('isced11')['Employment'].std()

st.write("Mean Employment by Level of Education:")
st.write(mean_employment)

st.write("Standard Deviation of Employment by Level of Education:")
st.write(std_employment)

# Create a line graph
fig, ax = plt.subplots()
for education_level in data_long['isced11'].unique():
    subset = data_long[data_long['isced11'] == education_level]
    subset = subset.sort_values('Year')
    ax.plot(subset['Year'], subset['Employment'], label=education_level)

ax.set_xlabel('Year')
ax.set_ylabel('Employment')
ax.set_title('Employment in Technology and Knowledge-Intensive Sectors by Level of Education')
ax.legend(title='Level of Education')

st.pyplot(fig)
