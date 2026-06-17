import logging
import os
import time
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import text
# Removed PicarroDB import - functions are defined locally
load_dotenv(override=True)


class Query:
    def __init__(self, query = None):
        if query is not None:
            self.query = query
        else:
            raise ValueError("Query is required")
        self.parent = None
        self.child = None
    def set_parent(self, parent):
        self.parent = parent

    def set_child(self, child):
        self.child = child
        
    def execute(self,conn, table_return = None):
        df = []
        if isinstance(conn, list):
            for conn in conn:
                df.append(self.execute_sql(conn, table_return))
            return pd.concat(df)
        else:
            return self.execute_sql(conn, table_return)

    def execute_sql(self,conn, table_return = None):
        if table_return is not None:
            df = {}
        else:
            df = None
        pointer = self
        #Classify the connection type, make a change only when there is sqllite
        if conn.dbtype == 'sqlite':
            with conn.engine as connection:
                while pointer.child is not None:
                    connection.execute(text(pointer.query)).close()
                    pointer = pointer.child
                if table_return is not None:
                    connection.execute(text(pointer.query)).close()
                    for table in table_return:
                        result = connection.execute(text(f"SELECT * FROM {table}"))
                        df[table] = pd.DataFrame(result.fetchall(), columns=list(result.keys()))
                else:
                    result = connection.execute(text(pointer.query))
                    df = pd.DataFrame(result.fetchall(), columns=list(result.keys()))
        else:
            with conn.engine.connect() as connection:
                connection.execute(text("SET NOCOUNT ON")).close()
                while pointer.child is not None:
                    connection.execute(text(pointer.query)).close()
                    pointer = pointer.child
                if table_return is not None:
                    connection.execute(text(pointer.query)).close()
                    for table in table_return:
                        result = connection.execute(text(f"SELECT * FROM {table}"))
                        df[table] = pd.DataFrame(result.fetchall(), columns=list(result.keys()))
                else:
                    result = connection.execute(text(pointer.query))
                    df = pd.DataFrame(result.fetchall(), columns=list(result.keys()))
        return df