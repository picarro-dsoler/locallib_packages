import logging
import os
import time
import pandas as pd
from dotenv import load_dotenv
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

load_dotenv(override=True)

class PConnection:
    def __init__(self, host: str, database: str, user: str, password: str):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.engine = self.set_engine()
        if self.engine is not None:
            self.session = Session(bind=self.engine, future=True)
        else:
            raise Exception("Engine not implemented set")
        self.Session = self.get_session()

    def set_engine(self):
        return None

    def get_session(self):
        return Session(bind=self.engine, future=True)
    
class EUConnection(PConnection):
    def __init__(self, host: str, database: str, user: str, password: str):
        super().__init__(host, database, user, password)
            
    def set_engine(self):
        return create_engine(
            f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:1433/{self.database}?"
            "driver=ODBC+Driver+17+for+SQL+Server")
    
class DataHubConnection(PConnection):
    def __init__(self, host: str, database: str, user: str, password: str):
        super().__init__(host, database, user, password)
            
    def set_engine(self):
        return create_engine(
            f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:5432/{self.database}")


class PDataFrame(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = None
        self.child = None
        self.query = None
        self.conn = None
    def set_connection(self, conn):
        self.conn = conn
    def set_query(self, query):
        self.query = query
    def set_parent(self, parent):
        self.parent = parent
    def set_child(self, child):
        self.child = child
    def get_parent(self):
        return self.parent


# EU1 credentials
EU1_USER = os.getenv("EUDBUSER")
EU1_PASSWORD = os.getenv("EUDBPW")

#EU2 credentials
EU2_USER = os.getenv("EU2DBUSER")
EU2_PASSWORD = os.getenv("EU2DBPW")

#DataHub credentials
DATAHUB_USER = os.getenv("DATAHUBUSER")
DATAHUB_PASSWORD = os.getenv("DATAHUBPW")
DATAHUB_DATABASE = os.getenv("DATAHUBDATABASE")

try:
    EU1_Conn = EUConnection(host="eu-prd-sqlsrv-ee-db01.czz1yneu9gmr.eu-central-1.rds.amazonaws.com", user=EU1_USER, password=EU1_PASSWORD, database="EU-SurveyorProduction")
    print("EU1_Conn created successfully")
except Exception as e:
    print(f"Error creating EU1_Conn: {e}")
    EU1_DB = None

try:
    EU2_Conn = EUConnection(host="eu-prd2-sqlsrv-ee-db01.czz1yneu9gmr.eu-central-1.rds.amazonaws.com", user=EU2_USER, password=EU2_PASSWORD, database="EU-SurveyorProduction2")
    print("EU2_Conn created successfully")
except Exception as e:
    print(f"Error creating EU2_Conn: {e}")
    EU2_Conn = None

try:
    DATAHUB_Conn = DataHubConnection(host="datahub.picarro.sensebird.net", user=DATAHUB_USER, password=DATAHUB_PASSWORD, database=DATAHUB_DATABASE)
    print("DataHub_Conn created successfully")
except Exception as e:
    print(f"Error creating DATAHUB_Conn: {e}")
    DATAHUB_Conn = None








