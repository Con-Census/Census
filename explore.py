#!/usr/bin/env python
# coding: utf-8

# In[8]:


# import os and csv functions
import os
import csv
# import libaries
import pandas as pd
import numpy as np
from tabulate import tabulate
from datetime import datetime
from sklearn.impute import SimpleImputer
from tabula import read_pdf
from sklearn.model_selection import train_test_split
import scipy.stats as stats
import math
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
# utilized for creating models and visualization
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
# utilized for metrics on my models
from sklearn.metrics import confusion_matrix, classification_report, ConfusionMatrixDisplay
# ignore warnings
import warnings
warnings.filterwarnings("ignore")
# Homemade module
import prepare
# explore.py
import scipy.stats
import modeling


# In[2]:


df=prepare.get_fema_data()


# In[3]:


df=prepare.prep_fema(df)


# In[5]:


# split df into test (20%) and train_validate (80%)
tv_df, test = train_test_split(df, test_size=0.2, random_state=123)
# split train_validate off into train (70% of 80% = 56%) and validate (30% of 80% = 24%)
train, validate = train_test_split(tv_df, test_size=0.3, random_state=123)


# In[4]:


def mapp(df):
    fig = px.choropleth(df,
                        locations='state', 
                        locationmode="USA-states", 
                        scope="usa",
                        color='support_level',
                        color_continuous_scale="", 
                        )
    fig.show()


# In[7]:


def explore1(q1):
    # bin the risk level to identify whether the higher the risk the higher the funding
    # bin the pop_level to identify whether the higher the population the higher the funding
    q1['risk_bin'] = pd.qcut(q1.risk_score, 4, labels=['low', 'medium', 'high', 'extremely_high'])
    q1['pop_bin'] = pd.qcut(q1.pop_density, 4, labels=['low', 'medium', 'high', 'extremely_high'])
    # Use pointplot to determine the relationship between population and state funding
    sns.pointplot(data=q1, x="pop_bin", y="state_amount", dodge=True)
    plt.show()
    # Use pointplot to determine the relationship between risk level and state funding
    sns.pointplot(data=q1, x="risk_bin", y="state_amount", dodge=True)
    plt.show()


# In[ ]:


def explore1m(xyz):
    # depicted in graph
    corr_matrix, p_matrix = scipy.stats.spearmanr(xyz, axis=0)
    fig, ax = plt.subplots()
    im = ax.imshow(corr_matrix)
    im.set_clim(-1, 1)
    ax.grid(False)
    ax.xaxis.set(ticks=(0, 1, 2), ticklabels=('pop_den', 'risk', 'disaster_fund'))
    ax.yaxis.set(ticks=(0, 1, 2), ticklabels=('pop_den', 'risk', 'disaster_fund'))
    ax.set_ylim(2.5, -0.5)
    cbar = ax.figure.colorbar(im, ax=ax, format='% .2f')
    plt.show()


# In[9]:


def explore2(q2):
    # use joint plot to 
    g = sns.jointplot(data=q2, x="risk_score", y="deficit", hue='Region')
    g.plot_joint(sns.kdeplot, color="r", zorder=0, levels=6)
    g.plot_marginals(sns.rugplot, color="r", height=-.15, clip_on=False)
    plt.show()


# In[10]:


def explore2m(q2):
    # Make a linear regression graph
    y=q2.deficit
    x=q2.risk_score
    slope, intercept, r, p, stderr = scipy.stats.linregress(x, y)
    line=f'Regression line: y={intercept:.2f}+{slope:.2f}, r={r:.2f}'
    fig, ax = plt.subplots()
    ax.plot(x, y, linewidth=0, marker='s', label='Data points')
    ax.plot(x, intercept + slope * x, label=line)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend(facecolor='white')
    plt.show()


# In[ ]:




