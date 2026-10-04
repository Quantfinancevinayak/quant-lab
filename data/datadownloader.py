from database import DatabaseConnector
import psycopg2
import requests
import pandas as pd
from dotenv import load_dotenv
import os
class dataloader:
    def __init__(self):
        self.connecter=None
        self.df=None
        self.main_df=None
        self.configure()
        
    def configure(self):
        load_dotenv()

        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.api_secret = os.getenv("UPSTOX_API_SECRET")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")

    def ticker(self):

        self.connecter=DatabaseConnector(database='quantdb',password='vinayak@123')
        self.connecter.initialize()
        cursor=self.connecter.conn.cursor()

        cursor.execute("SELECT id,name,isin,instrument_key FROM securities")
        dummy=cursor.fetchall()
        cursor.close()
        df=pd.DataFrame(dummy,columns=['id','name','isin','instrument_key'])

        self.df=df

    def api_initialize(self):
        
        
            for _,row in self.df.iterrows():
                try:
                    url = f"https://api.upstox.com/v3/historical-candle/{row['instrument_key']}/days/1/2026-09-23/2025-01-01"
                    headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {self.access_token}'
                    }

                    response = requests.get(url, headers=headers)

                    
                    if response.status_code == 200:
                    
                        print(f'Response sucessfull for {row['isin']}')
                    else:
                        # Print an error message if the request was not successful
                        print(f"Error: {response.status_code} - {response.text}")
                        print(f"The isin number was not download {row["isin"]}:-{row['name']}")
                        continue
                    api_data = response.json()

                    candles = api_data["data"]["candles"]

                    self.main_df = pd.DataFrame(
                        candles,
                        columns=[
                            "timestamp",
                            "open",
                            "high",
                            "low",
                            "close",
                            "volume",
                            "open_interest"
                        ]
                    )

                    self.main_df["id"] = row["id"]
                    self.main_df["isin"] = row["isin"]
                    self.main_df['name']=row['name']

                    database = self.connecter
                    cursor = database.conn.cursor()

                    for _, candle in self.main_df.iterrows():

                        cursor.execute(
                            """
                            INSERT INTO stockprices
                            (security_id, isin, date_time, open_price, high_price,
                            low_price, close_price, volume,name)
                            VALUES
                            (%s,%s,%s,%s,%s,%s,%s,%s)
                            ON CONFLICT (security_id, date_time) DO NOTHING
                            """,
                            (
                                candle["id"],
                                candle["isin"],
                                candle["timestamp"],
                                candle["open"],
                                candle["high"],
                                candle["low"],
                                candle["close"],
                                candle["volume"],
                                candle['name']
                            )
                        )

                    database.conn.commit()
                    print(f"data stored sucessfully for {row['isin']}:-{row['name']}")

                except Exception as e:
                    database.conn.rollback()
                    print(f"Database error for {row['isin']}: {e}")

                finally:
                    cursor.close()
print('1 started ')
store=dataloader()
print('2 started')
store.ticker()
print('3 started')
store.api_initialize()         



            