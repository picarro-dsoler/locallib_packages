import logging
import os
import time
import pandas as pd
from dotenv import load_dotenv
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from typing import Tuple
import uuid
import numpy as np
load_dotenv(override=True)


class PConnection:
    def __init__(self, host: str, database: str, user: str, password: str, dbtype: str = ''):
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.dbtype = dbtype
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
        super().__init__(host, database, user, password, dbtype = 'mssql')
            
    def set_engine(self):
        return create_engine(
            f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:1433/{self.database}?"
            "driver=ODBC+Driver+17+for+SQL+Server")
    
class DataHubConnection(PConnection):
    def __init__(self, host: str, database: str, user: str, password: str):
        super().__init__(host, database, user, password, dbtype = 'postgresql')
            
    def set_engine(self):
        return create_engine(
            f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:5432/{self.database}")


# Register as pandas accessor
@pd.api.extensions.register_dataframe_accessor("db")
class DBAccessor:
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self.parent = None
        self.child = None
        self.query = None
        self.conn = None
    
    def set_connection(self, conn):
        self.conn = conn
        return self._obj
    
    def set_query(self, query):
        self.query = query
        return self._obj

    def execute(self, Conn, source_col: str, temp_table_name: str = "#tmp_single_col", sql_col_name:  None = None, varchar_len: int = 4000, chunksize: int = 10000, erase_table: bool = True):
        temp_name, temp_conn = self.upload_single_column_to_temp_sqlserver(self._obj,Conn=Conn, source_col=source_col, temp_table_name=temp_table_name, sql_col_name=sql_col_name, varchar_len=varchar_len, chunksize=chunksize, erase_table=erase_table)
        with temp_conn.cursor() as cur:
            try:
                df = pd.read_sql(self.query, temp_conn)
            except Exception as e:
                print(f"Error executing query: {e}")
                df = None
        return df


    def upload_single_column_to_temp_sqlserver(self,
        df: pd.DataFrame,
        Conn,
        source_col: str,
        temp_table_name: str = "#tmp_single_col",
        sql_col_name:  None = None,
        varchar_len: int = 4000,
        chunksize: int = 10000,
        erase_table: bool = True
    ) -> Tuple[str, object]:
        """
        Create a one-column #temp table in SQL Server and upload that column from df.

        Returns
        -------
        (temp_table_name, dbapi_conn)
        - temp table name (str)
        - the open DBAPI connection (pyodbc) that owns the #temp session
        """
        if source_col not in df.columns:
            raise KeyError(f"Column '{source_col}' not found in DataFrame.")
        if not temp_table_name.startswith("#"):
            temp_table_name = f"#{temp_table_name}"
        if sql_col_name is None:
            sql_col_name = source_col

        s = df[source_col]

        # Detect UUID-like series (UUID objects or UUID-parsable strings)
        def looks_like_uuid_series(series: pd.Series) -> bool:
            sample = series.dropna().head(50)
            if sample.empty:
                return False

            def is_uuid_like(v):
                if isinstance(v, uuid.UUID):
                    return True
                if isinstance(v, str):
                    try:
                        uuid.UUID(v.strip())
                        return True
                    except Exception:
                        return False
                return False

            valid = sum(is_uuid_like(v) for v in sample)
            return valid >= max(3, int(0.8 * len(sample)))  # heuristic

        # Choose SQL type
        dtype = str(s.dtype)
        if looks_like_uuid_series(s):
            sql_type = "UNIQUEIDENTIFIER"
        elif dtype.startswith("int") and s.isna().any():
            sql_type = "BIGINT"            # safe for NA-containing integer series
        elif dtype.startswith("int"):
            sql_type = "BIGINT" if dtype == "int64" else "INT"
        elif dtype.startswith("float") or np.issubdtype(s.dtype, np.floating):
            sql_type = "FLOAT"
        elif dtype == "bool":
            sql_type = "BIT"
        elif "datetime64" in dtype:
            sql_type = "DATETIME2"
        else:
            sql_type = f"NVARCHAR({varchar_len})"

        create_sql = f"CREATE TABLE {temp_table_name} ([{sql_col_name}] {sql_type});"
        insert_sql = f"INSERT INTO {temp_table_name} ([{sql_col_name}]) VALUES (?);"

        # Coercion for DB insert
        def coerce(v):
            if pd.isna(v):
                return None
            if isinstance(v, uuid.UUID):
                return str(v)  # UNIQUEIDENTIFIER accepts canonical string
            if isinstance(v, pd.Timestamp):
                return v.to_pydatetime()
            if isinstance(v, pd.Timedelta):
                return str(v)
            if isinstance(v, np.integer):
                return int(v)
            if isinstance(v, np.floating):
                return float(v)
            if isinstance(v, np.bool_):
                return bool(v)
            return v

        rows = [(coerce(v),) for v in s.tolist()]

        # Use DBAPI connection to keep session (and #temp) alive
        conn = Conn.engine.raw_connection()  # pyodbc connection
        try:
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM tempdb.sys.tables WHERE name = '{temp_table_name.replace('#', '')}'")
                table_exists = cur.fetchone()[0] > 0
                if erase_table:
                    cur.execute(f"DROP TABLE IF EXISTS {temp_table_name};")
                    cur.execute(create_sql)
                else:
                    cur.execute(create_sql)
                cur.fast_executemany = True
                if chunksize and len(rows) > chunksize:
                    for i in range(0, len(rows), chunksize):
                        cur.executemany(insert_sql, rows[i:i+chunksize])
                else:
                    cur.executemany(insert_sql, rows)
            conn.commit()
        finally:
            # Intentionally do NOT close conn; caller should close when done with #temp.
            pass

        return temp_table_name, conn

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








