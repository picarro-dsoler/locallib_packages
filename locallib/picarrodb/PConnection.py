import logging
import os
import time
import pandas as pd
from apps_dal_sql.sessionfactory import SessionFactory
from apps_dal_sql.cursorfactory import CursorFactory
from dotenv import load_dotenv

load_dotenv(override=True)

class PConnection:
    def __init__(self,host,user,password,database):
        self.session_factory = SessionFactory(
                host=host,
                user=user,
                password=password,
                database=database
            )

    def get_session(self):
        return self.session_factory.get_session()


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

try:
    EU1_Conn = PConnection(host="eu-prd-sqlsrv-ee-db01.czz1yneu9gmr.eu-central-1.rds.amazonaws.com", user=EU1_USER, password=EU1_PASSWORD, database="EU-SurveyorProduction")
    print("EU1_Conn created successfully")
except Exception as e:
    print(f"Error creating EU1_Conn: {e}")
    EU1_DB = None

try:
    EU2_Conn = PConnection(host="eu-prd2-sqlsrv-ee-db01.czz1yneu9gmr.eu-central-1.rds.amazonaws.com", user=EU2_USER, password=EU2_PASSWORD, database="EU-SurveyorProduction2")
    print("EU2_Conn created successfully")
except Exception as e:
    print(f"Error creating EU2_Conn: {e}")
    EU2_Conn = None








