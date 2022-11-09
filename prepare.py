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
    df = pd.read_csv(z.extract('NRI_Table_Counties.csv'))
    
    return df

def prepare_fema(df):
    # Drop columns for additional ID columns or version info
    df.drop(columns={'nri_id', 'statefips', 'countytype', 'countyfips',
                     'nri_ver', 'stcofips', 'oid_'}, inplace=True)
    
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
    
    # Create column to merge on
    sr['stateabbrv'] = states
    sr.drop(columns='state', inplace=True)
    
    # sort states and reset index
    sr = sr.sort_values(by='stateabbrv').reset_index(drop=True)
    
    # Merge dataframes
    df = df.merge(sr, how='right', on='stateabbrv')
    
    # Create columns that captures the estimated tax money each county makes based on population
    df['state_funding'] = df.population*df.revenue_per_person
       
    # State disaster fund data (2018)
    efunds = {'stateabbrv':['AL', 'AK','AZ','AR','CA','CO','CT','DE','D.C.','FL','GA', 'HI','ID','IL','IN','IA','KS','KY','LA',
                            'ME','MD', 'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK', 'OR',
                            'PA', 'RI','SC', 'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'],
              'amount':[(56700 + 5287908 + 420000 + 500000),2000000, 8000000, 17569984, 1000000, 12500000, 0, 0, 0, 15284704,
                        11062041, 0, 0, 0, (114456+119004+485000), 0, 1315138, 0, 1100000, 0, 0, 0, 0, 10000000, 20000000, 0,
                        0,250000, 2000000, 0, 0, 0, 200000000, 22300000, 12292597, 7500000, 0, 0, 0, 250000, 0, 0, 4000000, 
                        100000000, (11113142+104100+7093015), 2000000, 0, 77483000, 0, 711200, 500000]}
    
    # Create a df
    efunds = pd.DataFrame(efunds)
    
    # Merge
    df = df.merge(efunds, on='stateabbrv', how='right')
    
    # Rearrange columns
    df = df[['state','stateabbrv', 'county', 'population', 'revenue_per_person', 'amount', 'buildvalue',
         'agrivalue', 'area','risk_score', 'resl_score', 'resl_value','drought_freq', 'drought_score', 'drought_loss', 
         'hurricane_freq','hurricane_score', 'hurricane_loss', 'storm_freq', 'storm_score', 'storm_loss']]#'funding',
    
    # Fill NA's as most are areas where certain disasters will not strike
    df=df.fillna(0)
    
    df=df.rename(columns={'state':'full_state','stateabbrv':'state'})
    df.replace('D.C.','DC',inplace=True)
    
    # Create population density
    df['pop_density'] = df.population / df.area
    
    # Cost of multiple disasters
    df['cost']=(df.drought_loss + df.hurricane_loss + df.storm_loss)
    
    # How much funding is left over in case of multiple disasters
    df['support_value'] = (df.amount) - (df.drought_loss + df.hurricane_loss + df.storm_loss) # + df.funding
    
    # Engineer a category for each county on where it falls in reference to "preparedness"
    df['support_level'] = pd.cut(df.support_value, 4, labels = ['bottom tier', 'below average', 'above average', 'top tier'])
    
    return df
    
    
def prep_fema(df):
    
    '''Beginning with a dateframe with 365 columns, removing columns with string ratings, columns that have separate values for
    various things that a disaster can affect, and adding various columns to determine the deficit an individual county will
    have if a disaster would occur '''
    # loweercase column names
    df.columns = df.columns.str.lower()
    
    # Drop columns for additional ID columns or version info (keep stcofips as a geographic identifier)
    df.drop(columns=['nri_id', 'statefips', 'countytype', 'countyfips', 'buildvalue', 'agrivalue',
                     'nri_ver', 'oid_'], inplace=True)
    
    # Social Vulnerability
    df = df[df.columns.drop(list(df.filter(regex='sovi')))]
    # Communitey Resilience
    df = df[df.columns.drop(list(df.filter(regex='resl')))]
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
    # Events are recorded over varyiong periods
    df = df[df.columns.drop(list(df.filter(regex='evnts')))]
    # frequency
    df = df[df.columns.drop(list(df.filter(regex='afreq')))]\
    # Risk Scores
    df = df[df.columns.drop(list(df.filter(regex='risks')))]
    
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
    #state_funding['stateabbrv'] = states
    
    # Drop $ and , to convert column type
    #state_funding.funding = state_funding.funding.str.replace('$','', regex=True).replace(',','', regex=True)
    
    # Make the funding an integer type
    #state_funding.funding = state_funding.funding.astype(int)
    
    # Join dataframes
    #df = df.merge(state_funding[['stateabbrv','funding']], how='right', on='stateabbrv')
    
    # State Revenue per person, narrow df down to states, dropping regions, and changing column type to integer
    sr = pd.read_csv('state_revenue.csv')
    sr = sr.iloc[4:75]
    
    # drop nulls
    sr.dropna(inplace=True)
    
    # Filter down columns and rename them
    sr = sr[['25-Aug-22','Unnamed: 23']]
    sr = sr.rename(columns={'Unnamed: 23': 'revenue_per_person', '25-Aug-22':'state'}).iloc[1:]
    
    # Drop non-state columns
    sr = sr.iloc[2:].drop(index=[16,24,31,40,54,60,67])
    
    # Create new column
    sr['revenue_per_person'] = sr['revenue_per_person'].str.replace(',','')
    sr['revenue_per_person'] = sr['revenue_per_person'].astype(int)
    
    # Create column to merge on
    sr['stateabbrv'] = states
    sr.drop(columns='state', inplace=True)
    
    # sort states and reset index
    sr = sr.sort_values(by='stateabbrv').reset_index(drop=True)
    
    # Merge
    df = df.merge(sr, how='right', on='stateabbrv')
    
    # Create columns that captures the estimated tax money each county makes based on population
    df['state_funding'] = df.population*df.revenue_per_person
       
    # State disaster fund data (2018)
    efunds = {'stateabbrv':['AL', 'AK','AZ','AR','CA','CO','CT','DE','D.C.','FL','GA', 'HI','ID','IL','IN','IA','KS','KY','LA',
                            'ME','MD', 'MA','MI','MN','MS','MO','MT','NE','NV','NH','NJ','NM','NY','NC','ND','OH','OK', 'OR',
                            'PA', 'RI','SC', 'SD','TN','TX','UT','VT','VA','WA','WV','WI','WY'],
              'state_amount':[(56700 + 5287908 + 420000 + 500000),2000000, 8000000, 17569984, 1000000, 12500000, 0, 0, 0, 
                              15284704, 11062041, 0, 0, 0, (114456+119004+485000), 0, 1315138, 0, 1100000, 0, 0, 0, 0, 
                              10000000, 20000000, 0, 0, 250000, 2000000, 0, 0, 0, 200000000, 22300000, 12292597, 7500000, 0, 0, 
                              0, 250000, 0, 0, 4000000, 100000000, (11113142+104100+7093015), 2000000, 0, 77483000, 0, 
                              711200, 500000]}
    
    # Create a df from the data
    efunds = pd.DataFrame(efunds)
    
    # Merge
    df = df.merge(efunds, on='stateabbrv', how='right')
    
    # Get total state population
    statepop = pd.DataFrame(df.groupby('state').population.sum())
    statepop.rename(columns={'population':'statepop'}, inplace=True)
    
    # Merge
    df = df.merge(statepop, on='state', how='right')
    
    # FY22 FEMA Funding to states listed under "other" award. 
    # https://www.usaspending.gov/search/?hash=68167b58af1378733e2e2fa03106dd49
    fema_funding = {'stateabbrv':states,
                    'fema_state':[19.31, 0.0922, 3.63, 6.16, 6.24, 0.378, 27.23, 6.95, 0.124, 29.68,
                                5.8, 4.55, 0.001409, 1.77, 1.29, 0.367, 0.496, 18.01, 700.46, 0.212,
                                11.96, 4.08, 1.73, 0.670, 11.59, 17.09, 4.94, 0.455, 0.346, 0.914,
                                364.778, 0.204, 160.08, 19.7, 0.192, 3.28, 6.31, 0.371, 113.3, 1.64,
                               1.58, 0.0916, 19.6, 30.77, 0.926, 0.135, 3.096, 31.26, 2.8, 0.462, 0.003]}

    # Another merge
    df = df.merge(pd.DataFrame(fema_funding), on='stateabbrv', how='right')
    
    # Adjusting FEMA funding to actual value
    df['fema_state_funding'] = (df.fema_state*1000000)
    
    # fema amount per county
    df['fema_per_county'] = df.fema_state_funding/df.statepop*df.population
    
    # Disaster that would cost the most
    df['max_cost'] = df[['drgt_ealt', 'hrcn_ealt', 'avln_ealt', 'cwav_ealt', 'erqk_ealt', 'hail_ealt', 
     'rfld_ealt','lnds_ealt','ltng_ealt','trnd_ealt','hwav_ealt','swnd_ealt',
     'tsun_ealt','vlcn_ealt','wfir_ealt','wntw_ealt']].max(axis=1)
    
    # How much a county would get when disaster strikes
    df['county_funding'] = df.state_amount/df.statepop*df.population
    
    # Define if there is a deficit between the funding they receive and the cost of disaster
    df['deficit'] = (df.county_funding) - df.max_cost
    
    # Fill NA's as most are areas where certain disasters will not strike
    df=df.fillna(0)
    
    # Rename columns
    df=df.rename(columns={'state':'full_state','stateabbrv':'state'})
    df.replace('D.C.','DC',inplace=True)
    
    # Create population density
    df['pop_density'] = df.population / df.area
    
    #creating bins
    btm = df.deficit.min()
    mid = df.deficit.mean()
    tp = df.deficit.max()
    btm_mid = (btm + mid)/2
    tp_mid = (tp + mid)/2
    
    # Engineer a category for each county on where it falls in reference to "preparedness"
    df['support_level'] = pd.cut(df.deficit, [btm, btm_mid, mid, tp_mid, tp], labels = ['bottom_tier',\
                                                                                        'below_average',\
                                                                                        'above_average',\
                                                                                        'top_tier'])
    
    # Change column order
    df = df[['full_state', 'state', 'county', 'stcofips', 'population', 'area', 'pop_density',
             'state_funding', 'fema_per_county',
             'risk_score','avln_ealt','cfld_ealt','cwav_ealt', 'drgt_ealt', 'erqk_ealt', 'hail_ealt', 'hwav_ealt',
             'hrcn_ealt', 'istm_ealt','lnds_ealt', 'ltng_ealt', 'rfld_ealt', 'swnd_ealt', 'trnd_ealt', 'tsun_ealt',
             'vlcn_ealt','wfir_ealt', 'wntw_ealt', 'max_cost', 'county_funding', 'deficit', 'support_level']]
    
    return df    
    
    
    
    
    