from google.cloud import bigquery
import time
import logging
from sqlalchemy import create_engine
import os
import warnings



#  -------------------------------------------------------------- configure-------------------------------------------------
warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO, filename = 'log.log', filemode = "w", format = '%(asctime)s - %(levelname)s - %(message)s')
path = "C:/Users/nikhi/Downloads/amintiri-data-analytics-debecefd7136.json"
table_name = 'total_sales'
table_query = {
    "sales": "select * from amintiri-data-analytics.Amintiri_GA4.t_total_sales",
    "first_visit": "select * from amintiri-data-analytics.Amintiri_GA4.t_first_visit"
}



#-------------------------------------------------------------authentication--------------------------------------------
def authentication(path, query):
    try:
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path
        client = bigquery.Client()
        query_data = client.query(query)
        dataframe = query_data.to_dataframe()
        logging.info("Data successfully authenticated and stored into dataframe")
        return dataframe
    except Exception as e:
        logging.exception("An error occured during authentication")


#----------------------------------------------------------local database --------------------------------
def load(table_name, df):
    try:
        engine = create_engine('sqlite:///amin.db')
        start = time.time()
        df.to_sql(table_name, con = engine, if_exists= 'replace', index = False)
        end = time.time()
        logging.info("Database Successfully created: in",end-start)
    except Exception as e:
        logging.exception("An error occured during loading")


# ----------------------------------------------------main function -----------------------------------------
def main():
    try:
        logging.info("Process started")
        for table_name, query in table_query.items():
            df = authentication(path, query)
            if df is not None:
                load(table_name, df)
        logging.info("Ingestion success")
    except Exception as e:
        logging.exception("An error occured in main function")
if __name__ == "__main__":
    main()