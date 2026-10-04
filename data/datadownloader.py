from database import DatabaseConnector
import psycopg2
import requests
import pandas as pd

class dataloader:
    def __init__(self,api_key,api_secret,access_token):
        self.api_key=api_key
        self.api_secret=api_secret
        self.access_token=access_token
        self.connecter=None
        self.df=None
        self.main_df=None

    def ticker(self):

        self.connecter=DatabaseConnector(database='quantdb',password='vinayak@123')
        self.connecter.initialize()
        cursor=self.connecter.conn.cursor()

        cursor.execute("SELECT id,isin,instrument_key FROM securities")
        dummy=cursor.fetchall()
        cursor.close()
        df=pd.DataFrame(dummy,columns=['id','isin','instrument_key'])

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
                        print(f"The isin number was not download{row["isin"]}")
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

                    database = self.connecter
                    cursor = database.conn.cursor()

                    for _, candle in self.main_df.iterrows():

                        cursor.execute(
                            """
                            INSERT INTO stockprices
                            (security_id, isin, date_time, open_price, high_price,
                            low_price, close_price, volume)
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
                                candle["volume"]
                            )
                        )

                    database.conn.commit()
                    print(f"data stored sucessfully for {row['isin']}")

                except Exception as e:
                    database.conn.rollback()
                    print(f"Database error for {row['isin']}: {e}")

                finally:
                    cursor.close()
print('1 started ')
store=dataloader(api_key='2e0378af-d87f-4672-857b-c1654a4c9b44',api_secret='awvwmlemol',access_token='eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiI4NEJIS1giLCJqdGkiOiI2YWI2MzUxY2I2MjNjMDc0YTZmNGJkOWUiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc5MDMyNjA0NCwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzkwMzczNjAwfQ.Ofeq6WE-0neDfBBWUKpaMemQSMzzCSqmc_CdndJknng')
print('2 started')
store.ticker()
print('3 started')
store.api_initialize()         



            