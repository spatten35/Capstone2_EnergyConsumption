# -*- coding: utf-8 -*-
"""
Created on Mon Jul  1 12:49:08 2019

@author: sarah
"""

import numpy as np
import pandas as pd
pd.set_option('display.max_columns', 90)
import warnings
warnings.filterwarnings('ignore')

def clean_data():
    energy_gdp_by_state_10_14 = pd.read_csv("Census_and_economic_2010_2014.csv", memory_map=True) 
    unemployment_90_16 = pd.read_csv("unemployment_by_county.csv", memory_map=True)
    gdp_per_cap_92_16 = pd.read_csv("gdp_per_capita.csv", memory_map=True)
    gdp_per_cap_92_16.drop('Unnamed: 0', axis=1, inplace=True) 
    
    
    # Get rid of all years not in our census dataset
    unemp_10_14 = unemployment_90_16[(unemployment_90_16['Year']>=2010) & (unemployment_90_16['Year']<=2014)]
    
    # Set index to index column
    unemp_10_14.set_index(unemp_10_14.index)
    
    # Remove columns that won't be used
    unemp_10_14_short = unemp_10_14.drop(['Month', 'County'], axis=1)
    
    # Set index to start at 0 again
    unemp_10_14_short.set_index(np.arange(0,len(unemp_10_14_short), 1), inplace=True)
    
    # Calculate the average unemployment rate for each state, by year. This removes all excess rows to keep just year, state and rate
    unemp_10_14_avg = pd.Series.to_frame(unemp_10_14_short.groupby(['Year','State'])['Rate'].mean())
    unemp_10_14_avg.reset_index(inplace=True)
    unemp_10_14_avg.head()
    
    # Shorten even farther to have 1 row per state. Unemployment rate will then have 1 column for each year. 
    # This format is to match the census file
    
    unemp_avg_by_state = unemp_10_14_avg.pivot(index='State', columns='Year', values='Rate')
    unemp_avg_by_state.reset_index(inplace=True)
    unemp_avg_by_state.columns = ['State', 'Unemp_rate2010', 'Unemp_rate2011', 'Unemp_rate2012', 'Unemp_rate2013', 'Unemp_rate2014']
    
    
    #Remove excess years not in the main table
    gdp_per_cap_10_14 = gdp_per_cap_92_16[(gdp_per_cap_92_16['YEAR'] >= 2010)& (gdp_per_cap_92_16['YEAR'] <= 2014)]
    gdp_per_cap_10_14.set_index(np.arange(0,len(gdp_per_cap_10_14),1), inplace=True)
    
    #Pivot table to have 1 row per state like in the main table
    gdp_by_state = gdp_per_cap_10_14.pivot(index='STATE', columns='YEAR', values='gdp_per_capita')
    gdp_by_state.reset_index(inplace=True)
    gdp_by_state.columns = ['State', 'GDP_per_cap2010', 'GDP_per_cap2011', 'GDP_per_cap2012', 'GDP_per_cap2013', 'GDP_per_cap2014']
    
    
    first_2 = pd.merge(energy_gdp_by_state_10_14, gdp_by_state, left_on='State', right_on='State', how='left')
    df = pd.merge(first_2, unemp_avg_by_state, left_on='State', right_on='State', how='left')
#    df.head()
#    df.info()
    
    # Separate out columns of our dataframe by year so we can have each row represent a year
    cols_2010 = [col for col in df.columns if '2010' in col]
    cols_2011 = [col for col in df.columns if '2011' in col]
    cols_2012 = [col for col in df.columns if '2012' in col]
    cols_2013 = [col for col in df.columns if '2013' in col]
    cols_2014 = [col for col in df.columns if '2014' in col]
    cols_diff_yrs = [col for col in df.columns if '-' in col]
    other_cols = list(set(df.columns) - set(cols_2010) - set(cols_2011) - set(cols_2012) - set(cols_2013) - set(cols_2014) - set(cols_diff_yrs))
    
    # Get columns of dataframe from previous lists of column names
    cols_other_2010 = list(other_cols + cols_2010)
    cols_other_2011 = list(other_cols + cols_2011)
    cols_other_2012 = list(other_cols + cols_2012)
    cols_other_2013 = list(other_cols + cols_2013)
    cols_other_2014 = list(other_cols + cols_2014)
    df_2010 = df[cols_other_2010]
    df_2011 = df[cols_other_2011]
    df_2012 = df[cols_other_2012]
    df_2013 = df[cols_other_2013]
    df_2014 = df[cols_other_2014]
    df_2010.head()
    
    # Add Year column to each and drop year from individual column names
    df_2010['Year'] = 2010
    df_2011['Year'] = 2011
    df_2012['Year'] = 2012
    df_2013['Year'] = 2013
    df_2014['Year'] = 2014
    
    df_2010.columns = [col.replace('2010', '') for col in df_2010.columns]
    df_2011.columns = [col.replace('2011', '') for col in df_2011.columns]
    df_2012.columns = [col.replace('2012', '') for col in df_2012.columns]
    df_2013.columns = [col.replace('2013', '') for col in df_2013.columns]
    df_2014.columns = [col.replace('2014', '') for col in df_2014.columns]
    
    
    df_full = pd.concat([df_2010, df_2011, df_2012, df_2013, df_2014], ignore_index=True, sort=True)
    df_full.head()
    
#    df_full.describe()
    
    # Dropping CENSUSPOP column due to missing ~80% of the data
    df_full.drop(['CENSUSPOP'], axis=1, inplace=True)
    
    # Break up consumption, expenditure, and production columns
    consumption_cols = [col for col in df_full.columns if col[-1] == 'C']
    expenditure_cols = [col for col in df_full.columns if col[-1] == 'E']
    production_cols = [col for col in df_full.columns if col[-1] == 'P']
    other_cols = list(set(df_full.columns) - set(consumption_cols) - set(expenditure_cols) - set(production_cols))
    
#    print(consumption_cols)
#    print(expenditure_cols)
#    print(production_cols)
#    print(other_cols)
    
    
    # Get column names for each energy type 
    energy_types = ['Biomass', 'Coal', 'Elec', 'Geo', 'Hydro', 'NatGas', 'LPG', 'FossFuel']
    energy_lists = [[], [], [], [], [], [], [], []]
    non_energy = df_full.columns
    for idx, energy in enumerate(energy_types):
        energy_lists[idx] = [col for col in df_full.columns if energy in col]
        non_energy = list(set(non_energy) - set(energy_lists[idx]))
#    print(energy_lists)
#    print(non_energy)
    
    
    # Create separate dataframes for each energy type
    df_list = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]
    for idx, en_list in enumerate(energy_lists):
        df_list[idx] = df_full[list(non_energy + en_list)]
    
    
    # Drop energy type from column, create new column for energy type
    for idx, df_mini in enumerate(df_list):
        df_mini['Energy_type'] = energy_types[idx]
        df_mini.columns = [col.replace(energy_types[idx], '') for col in df_mini.columns]
#    print(df_list[1].columns)
    
    # Recombine the dataFrames, then rename the 'C', 'E', and 'P' columns
    import functools
    #df = reduce(lambda df1,df2: pd.merge(df1,df2,on='id'), dfList)
    df_after = functools.reduce(lambda df1, df2: pd.merge(df1, df2, how='outer'), df_list)
    df_after.rename(columns={'C':'Consumption', 'E':'Expenditure', 'P':'Production', 'TotalE':'TotalExpenditures', 'TotalP':'TotalProduction', 'TotalC':'TotalConsumption'}, inplace=True)
    
    
#    df_after[df_after.Energy_type == 'FossFuel'].info()
    
    
    # Fill missing price and expenditure values with 0, since energy types that are missing price are hydro, geo, and bio
    # These don't cost anything 
    df_after[df_after.Price.isnull()]['Energy_type'].unique()
    df_after['Price'].fillna(0, inplace=True)
    df_after['Expenditure'].fillna(0,inplace=True)
    
    # The missing values for production are for 'Biomass', 'Elec', 'NatGas', 'LPG' which are types that can't be produced
    df_after[df_after.Production.isnull()]['Energy_type'].unique()
    df_after['Production'].fillna(0, inplace=True)
    
    
    # Missing migration rates for 2010, will fill those with the average for the column
    df_after[df_after.RNETMIG.isnull()]['Year'].unique()
    df_after['RNATURALINC'].fillna(df_after['RNATURALINC'].mean(), inplace=True)
    df_after['RBIRTH'].fillna(df_after['RBIRTH'].mean(), inplace=True)
    df_after['RDOMESTICMIG'].fillna(df_after['RDOMESTICMIG'].mean(), inplace=True)
    df_after['RDEATH'].fillna(df_after['RDEATH'].mean(), inplace=True)
    df_after['RINTERNATIONALMIG'].fillna(df_after['RINTERNATIONALMIG'].mean(), inplace=True)
    df_after['RNETMIG'].fillna(df_after['RNETMIG'].mean(), inplace=True)
    
    
    # Since United States isn't a state, and its the only one missing values in 'Division', 'Great Lakes', 'Coast', 'Region'
    df_after[df_after['Region'].isnull()]['State'].unique()
    df_after = df_after[df_after.State != 'United States']
    
    
    df_after['Unemp_rate'].fillna(df_after['Unemp_rate'].mean(), inplace=True)
#    df_after.describe()
    
    
    # Set up categorical variables
    df_after['StateCodes'] = df_after['StateCodes'].astype('category')
    df_after['State'] = df_after['State'].astype('category')
    df_after['Energy_type'] = df_after['Energy_type'].astype('category')
    df_after['Region'] = df_after['Region'].astype('category')
    df_after['Coast'] = df_after['Coast'].astype('category')
    df_after['Division'] = df_after['Division'].astype('category')
    df_after['Year'] = df_after['Year'].astype('category')
    return df_after