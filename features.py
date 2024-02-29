import pandas as pd
import json

def _replace_to_application_date(initial_date, application_date, day_of_week):
    result = initial_date
    if(day_of_week == 5):
        result += pd.DateOffset(days=2)
    elif(day_of_week == 6):
        result += pd.DateOffset(days=1)

    return result

def _replace_to_zero_if_empty_string(value):
    if(value == ''):
        return 0
    else:
        return value

def calc_tot_claim(json_str, application_date):
    if (pd.isnull(json_str)):
        return -3
    else:
        current_ts = pd.to_datetime('today').normalize()
        #application_date = pd.to_datetime(application_date.split().str[0], format='%Y-%m-%d')
        application_date = pd.to_datetime(application_date).date()
        
        # transform json column into new df
        json_obj = json.loads(json_str)
        claim_df = pd.json_normalize(json_obj)

        # remove records with empty claim_date
        claim_df = claim_df[claim_df['claim_date'].astype(bool)] 

        #check if there are any records with non empty claim_date
        if(len(claim_df.index) == 0):
            return len(claim_df.index)

        claim_df['claim_date'] = pd.to_datetime(claim_df['claim_date'], format='%d.%m.%Y')

        # add day_of_week column to determine Saturdays and Sundays
        claim_df['day_of_week'] = claim_df['claim_date'].dt.dayofweek

        # set claim_date as a date of the next Monday if claim was created on Saturday or Sunday
        claim_df['claim_date'] = claim_df.apply(lambda row: _replace_to_application_date(row["claim_date"], application_date, row["day_of_week"]), axis=1)

        # filter out records older than 180 days
        claim_df = claim_df.loc[(claim_df['claim_date'] >= (current_ts - pd.DateOffset(days=180))) & (claim_df['claim_date'] <= current_ts)]

        return len(claim_df.index)

def calc_disb_active_bank_loan(json_str):

    if (pd.isnull(json_str)):
        return -3
    else:
        # transform json column into new df
        json_obj = json.loads(json_str)
        claim_df = pd.json_normalize(json_obj)

        # get records with not null summa field
        non_empty_summa_df = claim_df[claim_df['summa'].astype(bool)] 

        # remove records with empty claim_date
        claim_df = claim_df[claim_df['claim_date'].astype(bool)] 

        # check if there are any loans
        if(len(non_empty_summa_df.index) == 0 or len(claim_df.index) == 0):
            return -1
        
        # fill bank column gaps and remove records with TBC loans
        claim_df['bank'] = claim_df.apply(lambda row: row.get('bank', ''), axis=1)
        claim_df = claim_df[~claim_df.get('bank', '').isin(['LIZ', 'LOM', 'MKO', 'SUG', ''])]

        # replace empty strings with zeros
        claim_df['loan_summa_fixed'] = claim_df.apply(lambda row: _replace_to_zero_if_empty_string(row["loan_summa"]), axis=1)

        return int(claim_df['loan_summa_fixed'].sum())

def calc_day_sinlastloan(json_str, application_date):

    if (pd.isnull(json_str)):
        return -3
    else:
        current_ts = pd.to_datetime('today').normalize()
        application_date = pd.to_datetime(application_date).date()

        # transform json column into new df
        json_obj = json.loads(json_str)
        claim_df = pd.json_normalize(json_obj)

        # remove records with empty summa field
        claim_df = claim_df[claim_df['summa'].astype(bool)] 

        # get records with not null claim_date
        non_empty_claim_date_df = claim_df[claim_df['claim_date'].astype(bool)] 

        # check if there are any loans
        if(len(non_empty_claim_date_df.index) == 0 or len(claim_df.index) == 0):
            return -1
        
        claim_df['contract_date'] = pd.to_datetime(claim_df['contract_date'], format='%d.%m.%Y')

        # add day_of_week column to determine Saturdays and Sundays
        claim_df['day_of_week'] = claim_df['contract_date'].dt.dayofweek

        # set contract_date as a date of the next Monday if claim was created on Saturday or Sunday
        claim_df['contract_date'] = claim_df.apply(lambda row: _replace_to_application_date(row["contract_date"], application_date, row["day_of_week"]), axis=1)

        return (current_ts - claim_df['contract_date'].max()).days