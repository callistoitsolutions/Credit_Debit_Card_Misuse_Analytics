import pandas as pd

data = {
    "txn_id": ["TXN001","TXN002","TXN003","TXN004","TXN005","TXN006","TXN007","TXN008"],
    "cust_id": ["CUST01","CUST01","CUST02","CUST03","CUST02","CUST03","CUST04","CUST04"],
    "date": [
        "2024-01-01 10:15","2024-01-01 10:20","2024-01-02 14:30",
        "2024-01-03 09:10","2024-01-03 09:15","2024-01-03 09:18",
        "2024-01-04 16:00","2024-01-04 16:05"
    ],
    "amount": [1200,45000,800,65000,700,68000,1500,32000],
    "location_city": ["Mumbai","Mumbai","Pune","Delhi","Pune","Noida","Chennai","Chennai"],
    "state": ["MH","MH","MH","DL","MH","UP","TN","TN"],
    "category": ["Grocery","Electronics","Restaurant","Jewellery","Grocery","Jewellery","Clothing","Electronics"],
    "mode": ["POS","Online","POS","Online","POS","Online","POS","Online"],
    "fraud_flag": [0,1,0,1,0,1,0,1]
}

df = pd.DataFrame(data)
df.to_excel("data/raw/sample_transactions.xlsx", index=False)

print("sample_transactions.xlsx created successfully")
