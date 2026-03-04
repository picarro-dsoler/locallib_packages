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
    def set_table(self, table):
        self.table = table
    def set_parent(self, parent):
        self.parent = parent
    def set_child(self, child):
        self.child = child
    def get_parent(self):
        return self.parent
    def get_child(self):
        return self.child
    
    def execute(self,conn):
        pointer = self.query
        df = None
        with conn.engine.connect() as connection:
            connection.execute(pointer)
            df = pd.read_sql(sql=get_emission_soruces('#TempFinalReports'), con=connection)
        return df

def get_emission_soruces(report_table):
    query = f"""
    SELECT 
        Es.ReportId,
        R.DateStarted AS ReportDate,
        Es.Id,
        Es.Disposition,
        Es.IsFiltered,
        Es.CH4,
        ES.EmissionRate,
        ES.EmissionRateAMean,
        ES.EmissionRateAStd,
        ES.EmissionRateGMean,
        ES.EmissionRateGStd,
        ES.EmissionRateLowerBound,
        ES.EmissionRateUpperBound,
        ES.EthaneRatio,
        ES.NumberOfPasses,
        ES.NumberOfPeaks,
        ES.PeakNumber,
        ES.RepresentativeEmissionRate,
        ES.RepresentativeBinLabel,
        ES.PriorityScore2,
        ES.EthaneRatioUncertainty
    FROM
        EmissionSource ES
    LEFT JOIN Report R ON ES.ReportId = R.Id
    WHERE
        ES.ReportId IN (SELECT ReportId FROM {report_table})
        AND (Es.Disposition = 1 OR Es.Disposition = 3)
    """
    return query


def get_final_reports(customer_name, years=None):
    year_filter = ""
    if years:
        years_str = ", ".join(str(year) for year in years)
        year_filter = f"AND YEAR(R.DateStarted) IN ({years_str})"

    query = f"""
    SELECT 
        C.Name AS CustomerName,
        R.Id AS ReportId,
        R.ReportTitle AS ReportTitle,
        L.Title AS Label,
        R.DateStarted AS ReportDate,
        RA.ExternalId AS BoundaryName
    INTO #TempFinalReports
    FROM
        Report R
    LEFT JOIN Customer C ON
        R.CustomerId = C.Id
    LEFT JOIN ReportLabel RL ON
        R.Id = RL.ReportId
    LEFT JOIN Label L ON
        RL.LabelId = L.Id
    LEFT JOIN ReportType ON
        R.ReportTypeId = ReportType.Id
    LEFT JOIN ReportArea RA ON R.Id = RA.ReportId
    WHERE
        LOWER(C.Name) = LOWER('{customer_name}')
        AND L.Title = 'Final Checkbox'
        AND RL.IsActive = 1
        {year_filter}
    
    """
    return query




    