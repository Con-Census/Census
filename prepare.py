import os
import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime
from sklearn.impute import SimpleImputer
from tabula import read_pdf
import math
import requests
import io
import zipfile
from urllib.request import urlopen
import csv
import shutil

def get_fema_data():
    '''Acquire the FEMA country data from original source and read it into a .csv (df has 365 columns and 3142 rows)'''
    
    url = 'https://hazards.fema.gov/nri/Content/StaticDocuments/DataDownload//NRI_Table_Counties/NRI_Table_Counties.zip'

    # Get url data
    response = requests.get(url)

    # Unlock the zipfile
    z = zipfile.ZipFile(io.BytesIO(response.content))

    # read the desired .csv file and drop secondary index column
    df = pd.read_csv(z.extract('NRI_Table_Counties.csv')).drop(columns='OID_')
    
    # lowercase all columns
    df.columns = df.columns.str.lower()
    
    return df

def prepare_fema(df):
    # Drop columns for additional ID columns or version info
    df.drop(columns=['nri_id', 'statefips', 'countytype', 'countyfips',
                     'nri_ver', 'stcofips'], inplace=True)
    
    '''We chose the 3 most costly disasters and removed the others. 
    We combined lighnting and strong wind to represent a severe storm'''
    
    # Social Vulnerability
    df = df[df.columns.drop(list(df.filter(regex='sovi')))]
    # Avalanche
    df = df[df.columns.drop(list(df.filter(regex='avln')))]
    # Coastal Flooding
    df = df[df.columns.drop(list(df.filter(regex='cfld')))]
    # Cold Wave
    df = df[df.columns.drop(list(df.filter(regex='cwav')))]
    # Earthquake
    df = df[df.columns.drop(list(df.filter(regex='erqk')))]
    # Hail
    df = df[df.columns.drop(list(df.filter(regex='hail')))]
    # Heat Wave
    df = df[df.columns.drop(list(df.filter(regex='hwav')))]
    # Ice Storm
    df = df[df.columns.drop(list(df.filter(regex='istm')))]
    # Landslide
    df = df[df.columns.drop(list(df.filter(regex='lnds')))]
    # Riverine Flooding
    df = df[df.columns.drop(list(df.filter(regex='rfld')))]
    # Tornado
    df = df[df.columns.drop(list(df.filter(regex='trnd')))]
    # Tsunami
    df = df[df.columns.drop(list(df.filter(regex='tsun')))]
    # Volcanic Activity
    df = df[df.columns.drop(list(df.filter(regex='vlcn')))]
    # Wildfire
    df = df[df.columns.drop(list(df.filter(regex='wfir')))]
    # Winter Storm
    df = df[df.columns.drop(list(df.filter(regex='wntw')))]
    # Remove string ratings for each factor
    df = df[df.columns.drop(list(df.filter(regex='ratng')))]
    # _EXPB, Exposure - Building Value
    df = df[df.columns.drop(list(df.filter(regex='expb')))]
    # Exposure - Agriculture Value
    df = df[df.columns.drop(list(df.filter(regex='expa')))]
    # Exposure - Total
    df = df[df.columns.drop(list(df.filter(regex='expt')))]
    # _EXPP, Exposure - Population
    df = df[df.columns.drop(list(df.filter(regex='expp')))]
    # _EXPPE, Exposure - Population Equivalence
    df = df[df.columns.drop(list(df.filter(regex='exppe')))]
    # _HLRB, Historic Loss Ratio - Buildings
    df = df[df.columns.drop(list(df.filter(regex='hlrb')))]
    # _HLRP, Historic Loss Ratio - Population
    df = df[df.columns.drop(list(df.filter(regex='hlrp')))]
    # _HLRA, Historic Loss Ratio - Agriculture
    df = df[df.columns.drop(list(df.filter(regex='hlra')))]
    # _HLRR, Historic Loss Ratio - Total Rating
    df = df[df.columns.drop(list(df.filter(regex='hlrr')))]
    # _EALB, Expected Annual Loss - Building Value
    df = df[df.columns.drop(list(df.filter(regex='ealb')))]
    # _EALP, Expected Annual Loss - Population
    df = df[df.columns.drop(list(df.filter(regex='ealp')))]
    # _EALPE, Expected Annual Loss - Population Equivalence
    df = df[df.columns.drop(list(df.filter(regex='ealpe')))]
    # _EALA, Expected Annual Loss - Agriculture Value
    df = df[df.columns.drop(list(df.filter(regex='eala')))]
    # Expected Annual Loss Score
    df = df[df.columns.drop(list(df.filter(regex='eals')))]
    # _EALR, Expected Annual Loss Rating
    df = df[df.columns.drop(list(df.filter(regex='ealr')))]
    # _RISKR, Hazard Type Risk Index Rating
    df = df[df.columns.drop(list(df.filter(regex='riskr')))]
    # _NPCTL, National Risk Index - National Percentile - Composite
    df = df[df.columns.drop(list(df.filter(regex='npctl')))]
    # _SPCTL, National Risk Index - State Percentile - Composite
    df = df[df.columns.drop(list(df.filter(regex='spctl')))]
    # Expected Annual Loss
    df = df[df.columns.drop(list(df.filter(regex='eal_')))]

    df['storm_evnts'] = df.ltng_evnts + df.swnd_evnts
    df['storm_freq'] = df['storm_evnts']/27
    df['storm_score'] = (df.ltng_risks + df.swnd_risks)/2
    df['storm_loss'] = df.ltng_ealt+df.swnd_ealt

    # Events are recorded over varyiong periods, so we'll only keep frequency
    df = df[df.columns.drop(list(df.filter(regex='evnts')))]
    # Lightning
    df = df[df.columns.drop(list(df.filter(regex='ltng')))]
    # Strong Wind
    df = df[df.columns.drop(list(df.filter(regex='swnd')))]
    
    # Make the names simpler
    df.rename(columns={'drgt_afreq':'drought_freq', 'drgt_risks':'drought_score',
                   'drgt_ealt':'drought_loss', 'hrcn_afreq':'hurricane_freq',
                   'hrcn_risks':'hurricane_score', 'hrcn_ealt':'hurricane_loss'}, inplace=True)
    
    # Sort alphabetically by state
    df = df.sort_values(by=['state','county'])
    
    # Get State funding data
    state_funding = pd.read_csv('state_funding_2022.csv', index_col=0)
    
    # Drop territories that we don't have data or in the FEMA data
    state_funding = state_funding.iloc[:51,:]
    
    states = ['AL','AK','AZ','AR','CA','CO','CT','DE','D.C.','FL','GA','HI','ID','IL','IN','IA','KS',
              'KY','LA','ME','MD','MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC',
              'ND','OH','OK','OR','PA','RI','SC', 'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY']
    
    # Create a columm that'll help with joining the two dataframes
    state_funding['stateabbrv'] = states
    
    # Drop $ and , to convert column type
    state_funding.funding = state_funding.funding.str.replace('$','', regex=True).replace(',','', regex=True)
    
    # Make the funding an integer type
    state_funding.funding = state_funding.funding.astype(int)
    
    # Join dataframes
    df = df.merge(state_funding[['stateabbrv','funding']], how='right', on='stateabbrv')
    
    # State Revenue per person, narrow df down to states, dropping regions, and changing column type to integer
    sr = pd.read_csv('state_revenue.csv')
    sr = sr.iloc[4:75]
    sr.dropna(inplace=True)
    sr = sr[['25-Aug-22','Unnamed: 23']]
    sr = sr.rename(columns={'Unnamed: 23': 'revenue_per_person', '25-Aug-22':'state'}).iloc[1:]
    sr = sr.iloc[2:].drop(index=[16,24,31,40,54,60,67])
    
    # Create new column
    sr['revenue_per_person'] = sr['revenue_per_person'].str.replace(',','')
    sr['revenue_per_person'] = sr['revenue_per_person'].astype(int)
    
    # sort states and reset index
    sr = sr.sort_values(by='state').reset_index(drop=True)
    
    # Create column to merge on
    sr['stateabbrv'] = states
    sr.drop(columns='state', inplace=True)
    
    # Merge dataframes
    df = df.merge(sr, how='right', on='stateabbrv')
    
    # Create columns that captures the estimated tax money each county makes based on population
    df['state_funding'] = df.population*df.revenue_per_person
    
    # Rearrange columns
    df = df[['state','stateabbrv', 'county', 'population', 'revenue_per_person', 'state_funding','funding','buildvalue',
         'agrivalue', 'area','risk_score', 'resl_score', 'resl_value','drought_freq', 'drought_score', 'drought_loss', 
         'hurricane_freq','hurricane_score', 'hurricane_loss', 'storm_freq', 'storm_score', 'storm_loss']]
    
    # Fill NA's as most are areas where a disaster will not strike
    df=df.fillna(0)
    
    df=df.rename(columns={'state':'full_state','stateabbrv':'state'})
    df.replace('D.C.','DC',inplace=True)
    
    # Create population density
    df['pop_density'] = df.population / df.area
    
    # Cost of multiple disasters
    df['cost']=(df.drought_loss + df.hurricane_loss + df.storm_loss)
    
    # How much funding is left over in case of multiple disasters
    df['support_value'] = (df.state_funding + df.funding) - (df.drought_loss + df.hurricane_loss + df.storm_loss)
    
    # Engineer a category for each county on where it falls in reference to "preparedness"
    df['support_level'] = pd.cut(df.support_value, 4, labels = ['bottom tier', 'below average', 'above average', 'top tier'])
    
    return df
    
    
    
    
    
    
    
    
    
    
    
    