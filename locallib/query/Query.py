import logging
import os
import time
import pandas as pd
from dotenv import load_dotenv
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

    def execute(self, conn, table_return = None):
        df = []
        if isinstance(conn, list):
            for conn in conn:
                df.append(self.execute_sql(conn, table_return))
            return pd.concat(df)
        else:
            return self.execute_sql(conn, table_return)

    def execute_sql(self, conn, table_return = None):
        if table_return is not None:
            df = {}
        else:
            df = None
        pointer = self
        if conn.dbtype == 'sqlite':
            with conn.engine as connection:
                while pointer.child is not None:
                    connection.execute(pointer.query)
                    pointer = pointer.child
                if table_return is not None:
                    connection.execute(pointer.query)
                    for table in table_return:
                        df[table] = pd.read_sql(sql=f"SELECT * FROM {table}", con=connection)
                else:
                    df = pd.read_sql(sql=pointer.query, con=connection)
        else:
            with conn.engine.connect() as connection:
                while pointer.child is not None:
                    connection.execute(pointer.query)
                    pointer = pointer.child
                if table_return is not None:
                    connection.execute(pointer.query)
                    for table in table_return:
                        df[table] = pd.read_sql(sql=f"SELECT * FROM {table}", con=connection)
                else:
                    df = pd.read_sql(sql=pointer.query, con=connection)
        return df