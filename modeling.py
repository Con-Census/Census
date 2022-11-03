import pandas as pd
import numpy as np
import scipy.stats as stats

# utilized for creating models and visualization
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier

# utilized for metrics on my models
from sklearn.metrics import confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.preprocessing import MinMaxScaler



def dtypes_to_list(df):
    num_type_list , cat_type_list = [], []

    for column in df:
        col_type = df[column].dtype
        if col_type == 'object':
            cat_type_list.append(column)
        if np.issubdtype(df[column], np.number) and \
             ((df[column].max() + 1) / df[column].nunique())  == 1 :
            cat_type_list.append(column)
        if np.issubdtype(df[column], np.number) and \
            ((df[column].max() + 1) / df[column].nunique()) != 1 :
            num_type_list.append(column)
    return num_type_list, cat_type_list


def train_validate_test(df, target):
    """
    this function takes in a dataframe and splits it into 3 samples,
    a test, which is 20% of the entire dataframe,
    a validate, which is 24% of the entire dataframe,
    and a train, which is 56% of the entire dataframe.
    It then splits each of the 3 samples into a dataframe with independent variables
    and a series with the dependent, or target variable.
    The function returns 3 dataframes and 3 series:
    X_train (df) & y_train (series), X_validate & y_validate, X_test & y_test.
    """
    # split df into test (20%) and train_validate (80%)
    train_validate, test = train_test_split(df, test_size=0.2, random_state=123)

    # split train_validate off into train (70% of 80% = 56%) and validate (30% of 80% = 24%)
    train, validate = train_test_split(train_validate, test_size=0.3, random_state=123)

    # split train into X (dataframe, drop target) & y (series, keep target only)
    X_train = train.drop(columns=[target, 'state', 'full_state', 'county', 'state_funding', 'federal_funding', 'drought_loss', 'hurricane_loss',
                                  'storm_loss', 'area', 'population', 'support_value'])
    y_train = train[target]

    # split validate into X (dataframe, drop target) & y (series, keep target only)
    X_validate = validate.drop(columns=[target, 'state', 'full_state', 'county', 'state_funding', 'federal_funding', 'drought_loss', 'hurricane_loss',
                                  'storm_loss','area', 'population', 'support_value'])
    y_validate = validate[target]

    # split test into X (dataframe, drop target) & y (series, keep target only)
    X_test = test.drop(columns=[target, 'state', 'full_state', 'county', 'state_funding', 'federal_funding', 'drought_loss', 'hurricane_loss',
                                  'storm_loss', 'area', 'population', 'support_value'])
    y_test = test[target]

    return X_train, y_train, X_validate, y_validate, X_test, y_test



def scale_data(X_train, X_validate, X_test):
    '''
    scales the data using MinMaxScaler from SKlearn
    should only be the X_train, X_validate, and X_test
    '''
    
#     Make the scaler
    scaler = MinMaxScaler()
    
#     Use the scaler
    X_train_scaled = scaler.fit_transform(X_train)
    X_validate_scaled = scaler.transform(X_validate)
    X_test_scaled = scaler.transform(X_test)
    
    return X_train_scaled, X_validate_scaled, X_test_scaled




def split_continuous(df):
    """
    Takes in a df
    Returns train, validate, and test DataFrames
    """
    # Create train_validate and test datasets
    train_validate, test = train_test_split(df, test_size=0.2, random_state=123)
    # Create train and validate datsets
    train, validate = train_test_split(train_validate, test_size=0.3, random_state=123)

    # Take a look at your split datasets

    print(f"train -> {train.shape}")
    print(f"validate -> {validate.shape}")
    print(f"test -> {test.shape}")
    return train, validate, test


# def x_y_split(train,validate,test):
#     # Create an 'X' variable that groups all features to be used within my models for my train, validate, and test
#     # dataset and a 'y' variable that is a series with just my target variable 'has_churned' within it
#     X_train = train.drop(columns=(['support_level', 'full_state'])
#     y_train = train.support_level
#     X_validate = validate.drop(columns=(['support_level', 'full_state'])
#     y_validate = validate.support_level
#     X_test = test.drop(columns=(['support_level', 'full_state'])
#     y_test = test.support_level
#     return X_train, X_validate, X_test, y_train, y_validate, y_test



# def model_metrics(model, 
#                   X_train, 
#                   y_train, 
#                   X_validate, 
#                   y_validate, 
#                   metric_df):
#     '''
#     model_metrics will use an sklearn model object to 
#     create predictions after fitting on our training set, and add
#     the model scores to a pre-established metric_df
#     returns: metric_df
#     **TODO: create a check to see if metric_df exists.  
#     Create it if not
#     '''
    
    
#     # fit our model object
#     model.fit(X_train, y_train['tax_value'])
#     in_sample_pred = model.predict(X_train)
#     out_sample_pred = model.predict(X_validate)
#     model_name = input('Name for model?')
#     y_train[model_name] = in_sample_pred
#     y_validate[model_name] = out_sample_pred
 
#     rmse_val = mean_squared_error(
#     y_validate['tax_value'], out_sample_pred, squared=False)
#     r_squared_val = explained_variance_score(
#         y_validate['tax_value'], out_sample_pred)
#     metric_df = metric_df.append({
#         'model': model_name,
#         'rmse': rmse_val,
#         'r^2': r_squared_val
#     }, ignore_index=True)
    
#     return metric_df

def modeling(X_train, y_train, X_validate, y_validate, dt_depth, rf_depth, n_n):
  lr = LogisticRegression(random_state=123)
  dt = DecisionTreeClassifier(max_depth=dt_depth, random_state=123)
  rf = RandomForestClassifier(max_depth=rf_depth, random_state=123)
  knn = KNeighborsClassifier(n_neighbors=n_n, weights='uniform')
  models = [lr, dt, rf, knn]
  for model in models:
    model.fit(X_train, y_train)
    actual_train = y_train
    pred_train = model.predict(X_train)
    actual_val = y_validate
    pred_val = model.predict(X_validate)
    print(model)
    print('              ')
    print('train score: ')
    print(classification_report(actual_train, pred_train))
    print('val score: ')
    print(classification_report(actual_val, pred_val))
    print('            ')
  return lr, dt, rf, knn