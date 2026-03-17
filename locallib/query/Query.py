import logging
import os
import time
import pandas as pd
from apps_dal_sql.sessionfactory import SessionFactory
from apps_dal_sql.cursorfactory import CursorFactory
from dotenv import load_dotenv
# Removed PicarroDB import - functions are defined locally
load_dotenv(override=True)


class Query:
    def __init__(self, query):
        self.query = query
        self.parent = None
        self.child = None
    def set_parent(self, parent):
        self.parent = parent
    def set_child(self, child):
        self.child = child
    def execute(self,conn):
        pointer = self
        df = None
        with conn.engine.connect() as connection:
            while pointer.child is not None:
                connection.execute(pointer.query)
                pointer = pointer.child
            df = pd.read_sql(sql=pointer.query, con=connection)
        return df



    