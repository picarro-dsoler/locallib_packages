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
    def __init__(self, query = None):
        if query is not None:
            self.query = query
        else:
            raise ValueError("Query is required")
        self.parent = None
        self.child = None
    def set_parent(self, parent):
        self.parent = parent
    def _fix_tmp_table_name(self):
        """
        Checks for an INTO clause in the query and ensures that any temporary table with a 'tmp_' prefix
        has a '#' before its table name. Returns the name of the table if found and changed, else None.
        """
        import re

        table_name_modified = None

        def fix_into(match):
            nonlocal table_name_modified
            into_prefix = match.group(1)
            table_name = match.group(2)
            after_name = match.group(3) if match.group(3) else ""
            # Only add # if 'tmp_' is at the start and not already prefixed with #
            if table_name.startswith("tmp_") and not table_name.startswith("#tmp_"):
                table_name_modified = f"#{table_name}"
                return f"{into_prefix}#{table_name}{after_name}"
            else:
                return match.group(0)

        self.query = re.sub(
            r"(\bINTO\s+)([A-Za-z_][A-Za-z0-9_]*)(\b|\s|$)",
            fix_into,
            self.query,
            flags=re.IGNORECASE
        )
        return table_name_modified
    def set_child(self, child):
        self.child = child
        
    def execute(self,conn):
        df = None
        if isinstance(conn, list):
            for conn in conn:
                df_temp = self.execute_sql(conn)
                if df is None:
                    df = df_temp
                else:
                    df = pd.concat([df, df_temp])
            return df
        else:
            return self.execute_sql(conn)


    def execute_sql(self,conn):
        pointer = self
        df = None
        with conn.engine.connect() as connection:
            while pointer.child is not None:
                connection.execute(pointer.query)
                pointer = pointer.child
            df = pd.read_sql(sql=pointer.query, con=connection)                
        return df



    