class DatabaseConnector:

    def __init__(self, database, password):
        self.database = database
        self.password = password
        self.conn = None

    def initialize(self):
        import psycopg2

        self.conn = psycopg2.connect(
            host="127.0.0.1",
            database=self.database,
            port=5432,
            user="postgres",
            password=self.password
        )

        print(f"Database connected successfully: {self.database}")

    def ticker_initializer(self):

        import pandas as pd

        df = pd.read_json("NSE.json")

        df = df[df["instrument_type"] == "EQ"]

        cursor = self.conn.cursor()

        for _, row in df.iterrows():

            cursor.execute(
                """
                INSERT INTO securities
                    (isin, name, instrument_key, asset_type, exchange)
                VALUES
                    (%s, %s, %s, 'EQUITY', 'NSE')
                ON CONFLICT (isin) DO NOTHING
                """,
                (
                    row["isin"],
                    row["name"],
                    row["instrument_key"]
                )
            )

        self.conn.commit()
        cursor.close()

        print("ALL TICKERS FETCHED SUCCESSFULLY")


test=DatabaseConnector(database='quantdb',password='vinayak@123')

test.initialize()
test.ticker_initializer()




