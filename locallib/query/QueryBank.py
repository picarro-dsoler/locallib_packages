def get_final_reports(customer_name, table_name = None, years=None):
    year_filter = ""
    if years:
        years_str = ", ".join(str(year) for year in years)
        year_filter = f"AND YEAR(R.DateStarted) IN ({years_str})"

    if table_name is not None:
        into_clause = f"INTO {table_name}"
    else:
        into_clause = ""

    query = f"""
    SELECT 
        C.Name AS CustomerName,
        R.Id AS ReportId,
        R.ReportTitle AS ReportTitle,
        L.Title AS Label,
        R.DateStarted AS ReportDate,
        RA.ExternalId AS BoundaryName
    {into_clause}
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

def get_emission_soruces_for_RER(report_table, table_name = None):
    if table_name is not None:
        into_clause = f"INTO {table_name}"
    else:
        into_clause = ""

    query = f"""
    SELECT 
        Es.ReportId,
        YEAR(R.DateStarted) AS Year,
        R.DateStarted AS ReportDate,
        Es.Id,
        Es.Disposition,
        Es.IsFiltered,
        Es.CH4,
        RA.ExternalId AS BoundaryName,
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
    LEFT JOIN ReportArea RA ON ES.ReportId = RA.ReportId
    WHERE
        ES.ReportId IN (SELECT ReportId FROM {report_table})
        AND ES.EmissionRate > 0 
        AND (Es.Disposition = 1 OR Es.Disposition = 3)
    """
    return query