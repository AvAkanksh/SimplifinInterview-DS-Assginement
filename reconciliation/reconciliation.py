import pandas as pd
import datetime
from thefuzz import fuzz
from thefuzz import process

# Data Loading
oms_data = pd.read_excel('./data/raw/Data Assignment File.xlsx', sheet_name='OPD')
paytm_data = pd.read_excel('./data/raw/Data Assignment File.xlsx', sheet_name='PAYTM EDC')

# Data Cleaning

# OMS_DATA Cleaning

oms_data = oms_data.dropna(how='all')
oms_data.reset_index(drop=True, inplace=True)
oms_data_header = oms_data.iloc[0]
oms_data = oms_data[1:]
oms_data.reset_index(drop=True, inplace=True)
oms_data.columns = oms_data_header

# Drop all the unneccesary columns in oms_data dataframe:
oms_columns_to_drop = ['From Package', 'CHQ#/Transaction No.', 'Bank Transfer', 'Auth', 'Paid By', 'Transaction No']
oms_data = oms_data.drop(columns=oms_columns_to_drop)


# fill all the empty cells with 0 in [Amount, From Advance, Amount after Advance/Package, Cash, Card, CHQ/Wallet, Amount Due] columns
oms_columns_empty_cell_fill_with_zero = ['Amount', 'From Advance', 'Amount after Advance/Package', 'Cash', 'Card', 'CHQ/Wallet', 'Amount Due']
for column in oms_columns_empty_cell_fill_with_zero:
    oms_data[column] = oms_data[column].fillna(0)


# PAYTM_DATA Cleaning

# Need to drop all the columns which are NaN or empty in paytm_data dataframe.
for col in paytm_data.columns:
    if paytm_data[col].isnull().all() or paytm_data[col].empty:
        paytm_data.drop(columns=col,inplace=True)

# Drop all the unneccesary columns in paytm_data dataframe:
paytm_columns_to_drop = ['Transaction_Type', 'Status', 'MID', 'Amount', 'Channel', 'Payout_Date', 'Product_Code', 'Request_Type', 'Link_Description', 'Response_code', 'Response_message', 'Original_txn_value_before_promo', 'RRN', 'Prepaid_Card', 'Settle_Type']
paytm_data = paytm_data.drop(columns=paytm_columns_to_drop)


# The entries in each cell are of type string and all of them are having ' in them. so its time to clean that
# This function removes all the ' in the string as it is the last character in the string.
def clean_string(string):
    return string[:-1]

columns_to_clean = list(paytm_data.columns)
columns_to_clean.remove("Settled_Amount")

for col in columns_to_clean:
    paytm_data[col] = paytm_data[col].apply(clean_string)

# Standardize formats

# Standardizing the date and time format in oms_data dataframe
def standardizeDatetime(date_obj,time_obj):
    # Create a new datetime object with the date from the date object and the time from the time object
    combined_datetime = datetime.datetime(date_obj.year, date_obj.month, date_obj.day, time_obj.hour, time_obj.minute, time_obj.second).strftime("%Y%m%d%H%M%S")
    return combined_datetime

# Standardizing the date and time format in paytm_data dataframe
def changeFormat(date):
    return datetime.datetime.strptime(date,"%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")

def convertToUnixTimestamp(date):
    return datetime.datetime.strptime(date,"%Y%m%d%H%M%S").timestamp()

def fuzzyMatchString(unixTimestamp, cardAmount,chqWalletAmount=0):
    return str(int(unixTimestamp)) + f" {(cardAmount+chqWalletAmount):.2f}"

def finalAmountStr(amount1,amount2=0):
    return f"{(amount1+amount2):.2f}"

# Applying Standardization for OMS_DATA
oms_data["Standardized DateTime"] = oms_data.apply(lambda x: standardizeDatetime(x["Receipt Date"], x["Receipt Time"]), axis=1)
oms_data["UnixTimestamp"] = oms_data["Standardized DateTime"].apply(convertToUnixTimestamp)
oms_data["UnixTimestampAmount"] = oms_data.apply(lambda x: fuzzyMatchString(x["UnixTimestamp"], x["Card"], x["CHQ/Wallet"]), axis=1)
oms_data["DateTimeAmount"] = oms_data.apply(lambda x: fuzzyMatchString(x["Standardized DateTime"], x["Card"], x["CHQ/Wallet"]), axis=1)
oms_data["FinalAmount"] = oms_data.apply(lambda x : finalAmountStr(x["Card"], x["CHQ/Wallet"]), axis=1)
oms_data.drop(columns=["Receipt Date", "Receipt Time"], inplace=True)

# Applying Standardization for PAYTM_DATA
paytm_data["Standardized DateTime"] = paytm_data["Settled_Date"].apply(changeFormat)
paytm_data["UnixTimestamp"] = paytm_data["Standardized DateTime"].apply(convertToUnixTimestamp)
paytm_data["UnixTimestampAmount"] = paytm_data.apply(lambda x: fuzzyMatchString(x["UnixTimestamp"], x["Settled_Amount"]), axis=1)
paytm_data["DateTimeAmount"]= paytm_data.apply(lambda x : fuzzyMatchString(x['Standardized DateTime'], x["Settled_Amount"]), axis=1)
paytm_data["FinalAmount"] = paytm_data.apply(lambda x : finalAmountStr(x["Settled_Amount"]), axis=1)
paytm_data['Bank_Transaction_ID'] = paytm_data['Bank_Transaction_ID'].apply(lambda x : int(x))
paytm_data.drop(columns=["Transaction_Date","Updated_Date","Settled_Date","Pos_Date", "Pos_Time"], inplace=True)

# Saving the dataframe to .csv file for faster operations as .csv file is very lightweight format.

oms_data.to_csv("./data/processed/oms_data.csv", index=False)
paytm_data.to_csv("./data/processed/paytm_data.csv", index=False)

# Reconciliation (Finding matches between the two datasets for checking the consistency of the records)

# Direct Matching
# Create a new column for matched status
paytm_data["Matched"] = False
paytm_data["Receipt #"] = ''
paytm_data["Discrepancy"] = ''
paytm_data["MatchingTechnique"] = ''
oms_data["Matched"] = False
oms_data["Transaction_ID"] = ''
oms_data["Discrepancy"] = ''
oms_data["MatchingTechnique"] = ''

# Match records using payment reference numbers
matches_from_direct_matching = 0

for i in range(len(paytm_data)):
    match = oms_data[(paytm_data['Bank_Transaction_ID'][i]) == oms_data['Payment Aggregator Transaction ID']]
    if len(match):
        for j, row in match.iterrows():
            if(str(match['Standardized DateTime'][j])[:8] == str(paytm_data['Standardized DateTime'][i])[:8]):
                paytm_data.loc[i,'Matched'] = True
                paytm_data.loc[i,'Receipt #'] = match['Receipt #'][j]
                paytm_data.loc[i,'MatchingTechnique'] = 'Direct'
                oms_data.loc[j,'Matched'] = True
                oms_data.loc[j,'Transaction_ID'] = paytm_data.loc[i,'Transaction_ID']
                oms_data.loc[j,'MatchingTechnique'] = 'Direct'
                matches_from_direct_matching+=1
                # All the payments in Paytm EDC are made by CreditCard / Debit card
                # Therefore, we can use the "Settled_Amount" column to check if the amounts match with the "Card" column amount in oms_data

                if(match['Card'][j] != paytm_data['Settled_Amount'][i]):
                    paytm_data['Discrepancy'][i] = "The amounts didn't match for Transaction ID : ",paytm_data['Bank_Transaction_ID'][i] , " The amounts are 'Amount after Advance/Package' : ",match['Amount after Advance/Package'][j]," Amount Due : ",match['Amount Due'][j] , " Settled Amount : ", paytm_data['Settled_Amount'][i]
                break
# print("Matches from Direct Matching Technique : ",matches_from_direct_matching)


# Fuzzy Matching
# Records which are not matched yet after Direct Matching Technique is applied
paytm_data_unmatched_records = paytm_data[~paytm_data['Matched']]


# Implement fuzzy matching algorithm
# Applying the Fuzzy Matching Technique and updating the entries in the dataframe

threshold = 90 # in seconds
fuzzySearchColumn = "UnixTimestampAmount"
matches_from_fuzzy_matching = 0

for index , row in paytm_data_unmatched_records.iterrows():
    # Performing fuzzy matching on UnixTimestampAmount column and limit the search space only on the records which are close by in time based on the Threshold value and matching amounts only.
    possible_matches = process.extractOne(row[fuzzySearchColumn],oms_data[(abs(row['UnixTimestamp']-oms_data['UnixTimestamp'])<=threshold ) & (row["FinalAmount"]==oms_data['FinalAmount']) & (oms_data['Matched']==False)][fuzzySearchColumn], scorer=fuzz.token_sort_ratio)
    # print((oms_data[(abs(row['UnixTimestamp']-oms_data['UnixTimestamp'])<=threshold ) & (row["FinalAmount"]==oms_data['FinalAmount']) & (oms_data['Matched']==False)][fuzzySearchColumn]))
    # print(possible_matches)
    if possible_matches:
        oms_data_index = possible_matches[2]
        # print(oms_data_index)
        paytm_data.loc[index,'Matched'] = True
        paytm_data.loc[index,'Receipt #'] = oms_data.loc[oms_data_index,'Receipt #']
        paytm_data.loc[index,'MatchingTechnique'] = 'Fuzzy'

        oms_data.loc[oms_data_index,'Matched'] = True
        oms_data.loc[oms_data_index,'Transaction_ID'] = paytm_data.loc[i,'Transaction_ID']
        oms_data.loc[oms_data_index,'MatchingTechnique'] = 'Fuzzy'
        matches_from_fuzzy_matching+=1

# print("Total Fuzzy Matches Found : ",matches_from_fuzzy_matching)


# Validation
# Manually validate matched records based on business context

# Analyze unmatched records to identify patterns or common discrepancies

# Reporting
# Generate a reconciliation report
matched_records = paytm_data[paytm_data['Matched']]
unmatched_records = paytm_data[~paytm_data['Matched']]


underline_code = "\033[4m"
reset_code = "\033[0m"

print(f"""
    > {underline_code}RECONCILIATION REPORT{reset_code}

    - {matches_from_direct_matching} Matches from Direct Matching Technique
    - {matches_from_fuzzy_matching} Matches from Fuzzy Matching Technique
    
    ------------------------------------------------------------
    
    Number of matched records: {len(matched_records)}
    Number of unmatched records: {len(unmatched_records)}
""")


# Save the results to a file
paytm_data.to_csv("./reports/final_processed_paytm_data.csv", index=False)
oms_data.to_csv("./reports/final_processed_oms_data.csv", index=False)


# Create a detailed report
report = pd.DataFrame({
    'Category': ['Matched Records', 'Unmatched Records'],
    'Count': [len(matched_records), len(unmatched_records)]
})

report.to_csv('./reports/reconciliation_report.csv', index=False)

# Analyze unmatched records to identify potential issues
# Check the Readme.md file in reports folder for more details on the analysis part of the unmatched records.