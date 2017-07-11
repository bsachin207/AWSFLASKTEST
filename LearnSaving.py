# -*- coding: utf-8 -*-
"""

This programs consumes the transaction history of multiple accounts.

Output: The amount in a user'a checking account can be moved to 
savings without it affecting the user's spending habits or life style

@author: Sachin
"""
import pandas as pd
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split


pd.options.mode.chained_assignment = None

ACCOUNT_ID = 2177


def learning_model(debit_trans, avg_credit_days):
    learning  = learning  = debit_trans[['dates','balance','rolling_sum']]
    #remove NaN
    learning = learning[avg_credit_days:]
    
    #splitting testing and training data
    train, test = train_test_split(learning, test_size=0.1)
    
    #Very sensitive parameters for KNN
    knn = KNeighborsRegressor(n_neighbors=3,weights='distance')
    
    print 'Learning Model is -', knn
    
    knn.fit(train[['dates','balance']],train[['rolling_sum']])
    score = knn.score(test[['dates','balance']],test[['rolling_sum']])
    print '\n\nModel Prediction score - ', int(score*100) 
    return knn
    

def predict_the_expenditure(model, X):
    
    return model.predict(X)
    
def load_data(filepath):
    p=pd.read_csv(filepath, sep=";",usecols=[0,1,2,3,5,6])
    return p

def reformat_and_model_data(p, account_id=ACCOUNT_ID):
    #Assumed that the file format is fixed     
    #Do it for individual customer - We can pre-compute it on large dataset    
    cust_trans = p[p.account_id==account_id]
    cust_trans["date"] = pd.to_datetime(cust_trans["date"].astype(str), format='%y%m%d')
    cust_trans = cust_trans.sort_values("date")
    
    #credits and debit have fixed indicators  
    credit_trans = cust_trans[cust_trans.type=='PRIJEM']
    debit_trans = cust_trans[cust_trans.type=='VYDAJ']
    debit_trans = debit_trans.sort_values("date")
    
    #from credit data, find the avg days between 2 credits 
    credit_trans["prev_credit"] = credit_trans.date.diff().fillna(0).dt.days
    avg_credit_days = sum(credit_trans.prev_credit)/float(len(credit_trans))
    avg_credit_days = int(avg_credit_days)
   
    #create continous dates as index. If no transaction happend on a day the row will be 0
    s_date = min(debit_trans.date)
    e_date = max(debit_trans.date)
    date_reindex = pd.date_range(start=s_date, end=e_date)
    
    #make sum of all debit transaction in a day and retain all the rows   
    debit_trans["g_sum"]=debit_trans.groupby(['date'])['amount'].transform('sum')
    
    #retain the balance - Balance of the day  = balance at the time of last transaction in the day
    debit_trans=debit_trans[debit_trans.date.shift(-1) != debit_trans.date]
    debit_trans.set_index("date", inplace=True)
    debit_trans=debit_trans.reindex(date_reindex)
    #retain the balance for 'no transaction day'
    debit_trans["balance"].ffill(inplace=True)
    debit_trans.fillna(0,inplace=True)
    
    #calculate rolling sum of g_sum over next avg credit days  
    debit_trans["rolling_sum"] = debit_trans.g_sum.rolling(window=int(avg_credit_days)).sum()
    debit_trans=debit_trans.reset_index()
    debit_trans.rename(columns={'index':'dates'},inplace=True)
    
    #shift the balance- balance of 15/11 shift to (15/11 + avg credit days)
    #Reason: On current day- waht is the last avg_credit_days spend and what was the balance at that time    
    debit_trans["balance"] = debit_trans.balance.shift(avg_credit_days)
    debit_trans["dates"] = debit_trans["dates"].dt.day
    
    #Learn the data - Can be changed depending on the size of the data.
    model = learning_model(debit_trans,int(avg_credit_days))
    
    #predict the expenditure for next avg_credit_days
    return model, avg_credit_days
    

def execute(p,accid, day, balance):
    day = int(day)
    balance = int(balance)
    accid = int(accid)
    model, credit_days = reformat_and_model_data(p,account_id=accid)
    
    #predict the expenditure
    Y = predict_the_expenditure(model,[[day, balance]])
   
    #Let's start moving 10% of the spare money
    amount_to_move = (balance - Y[0][0]) * 0.1
    
    print 'Balance is-' , balance    
    print 'Day of month-', day  
    print 'Avg days between credit- ', credit_days
    print 'Predicted Expenditure-', Y[0][0]
    print 'Amount You should Move Today- ', amount_to_move
    return {"Account ID": accid, "Balance": balance,
            "Day":day, "Predicted Expenditure": Y[0][0], "Amount to Move": amount_to_move, "Credit frequency":credit_days}
