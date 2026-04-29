from locallib.query.Query import Query

def setup_query(query_func):
    def wrapper(*args, **kwargs):
        query = query_func(*args, **kwargs)
        return Query(query = query)
    return wrapper

@setup_query
def get_reports(customer_name, table_name = None, years=None, final_checkbox = True):
    year_filter = ""
    if years:
        years_str = ", ".join(str(year) for year in years)
        year_filter = f"AND YEAR(R.DateStarted) IN ({years_str})"

    if table_name is not None:
        into_clause = f"INTO {table_name}"
    else:
        into_clause = ""

    if final_checkbox:
        label_filter = "AND L.Title = 'Final Checkbox'"
    else:
        label_filter = ""

    query = f"""
    SELECT 
        C.Name AS CustomerName,
        CASE
            WHEN ReportType.Description = 'Compliance' THEN CONCAT('CR-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
            WHEN ReportType.Description = 'Emissions' THEN CONCAT('ER-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
            ELSE CONCAT('CR-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
        END AS ReportName,
        R.Id AS ReportId,
        R.ReportTitle AS ReportTitle,
        L.Title AS Label,
        R.DateStarted AS ReportDate,
        RA.ExternalId AS BoundaryName,
        RAC.AssetLengthKM AS ReportAssetLengthKm,
        RC.PercentCoverageAssets AS ReportPercentCoverageAssets,
        RAC.AssetLengthKM * RC.PercentCoverageAssets AS AssetCoveredLengthKm,
        RAC.DistributionPipeCoveredKm,
        RAC.DistributionPipePercentCovered,
        RAC.ServicePipeKm,
        RAC.ServicePipeCoveredKm,
        YEAR(R.DateStarted) AS ReportYear,
        MONTH(R.DateStarted) AS ReportMonth
   
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
    LEFT JOIN ReportCompliance RC ON R.Id = RC.ReportId
    LEFT JOIN ReportAreaCovered RAC ON R.Id = RAC.ReportId
    WHERE
        LOWER(C.Name) = LOWER('{customer_name}')
        AND L.Title = 'Final Checkbox'
        AND RL.IsActive = 1
        {year_filter}
    """
    return query

def get_final_reports(customer_name, table_name = None, years=None):
    if isinstance(customer_name, list):
        customer_name_clauses = []
        for name in customer_name:
            customer_name_clauses.append(f"LOWER(C.Name) = LOWER('{name}')")
        customer_name_filter = " OR ".join(customer_name_clauses)
        customer_name_filter = f"({customer_name_filter})"
    else:
        customer_name_filter = f"LOWER(C.Name) = LOWER('{customer_name}')"
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
        CASE
            WHEN ReportType.Description = 'Compliance' THEN CONCAT('CR-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
            WHEN ReportType.Description = 'Emissions' THEN CONCAT('ER-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
            ELSE CONCAT('CR-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
        END AS ReportName,
        R.Id AS ReportId,
        R.ReportTitle AS ReportTitle,
        L.Title AS Label,
        R.DateStarted AS ReportDate,
        RA.ExternalId AS BoundaryName,
        RAC.AssetLengthKM AS ReportAssetLengthKm,
        RC.PercentCoverageAssets AS ReportPercentCoverageAssets,
        RAC.AssetLengthKM * RC.PercentCoverageAssets AS AssetCoveredLengthKm,
        RAC.DistributionPipeCoveredKm,
        RAC.DistributionPipePercentCovered,
        RAC.ServicePipeKm,
        RAC.ServicePipeCoveredKm
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
    LEFT JOIN ReportCompliance RC ON R.Id = RC.ReportId
    LEFT JOIN ReportAreaCovered RAC ON R.Id = RAC.ReportId
    WHERE
        {customer_name_filter}
        AND L.Title = 'Final Checkbox'
        AND RL.IsActive = 1
        {year_filter}
    """
    return query

@setup_query
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

def query_reports_view(report_table):
    query =  f"""select 
    customer_shortname  as "CustomerShortName",
    rp_id  as "ReportId",
    rp_percentcoverageassets as "ReportPercentCoverageAssets_DH",
    lisa_count as "LisaCount",
    rp_label_final as "ReportLabelFinal",
    rp_label_other as "ReportLabelOther",
    bo_name as "BoundaryName",
    bo_mode as "BoundaryMode",
    bo_type as "BoundaryType",
    bo_plant as "BoundaryPlant",
    bo_subplant as "BoundarySubplant",
    bo_region as "BoundaryRegion",
    bo_subregion as "BoundarySubRegion",
    bo_km_network as "BoundaryKmNetwork"
    from dash.v_report 
    where rp_id IN (SELECT LOWER(ReportId::text)::uuid FROM {report_table})"""
    return query


def reports_view(customer_name, years, is_final_checkbox):
    # Convert the list of years to a string for the SQL IN clause
    years_str = ', '.join(map(str, years))
    
    # Start building the query
    query = f"""
    SELECT 
        customer_shortname AS "CustomerName",
        rp_id AS "ReportId",
        rp_name AS "ReportName",
        rp_title AS "ReportTitle",
        rp_date AS "ReportDate",
        rp_time AS "ReportTime",
        rp_percentcoverageassets AS "ReportPercentCoverageAssets",
        lisa_count AS "LisaCount",
        rp_label_final AS "ReportLabelFinal",
        rp_label_other AS "ReportLabelOther",
        bo_mode AS "BoundaryMode",
        bo_name AS "BoundaryName",
        bo_type AS "BoundaryType",
        bo_plant AS "BoundaryPlant",
        bo_subplant AS "BoundarySubplant",
        bo_region AS "BoundaryRegion",
        bo_subregion AS "BoundarySubRegion",
        bo_km_network AS "BoundaryKmNetwork"
    FROM dash.v_report vr 
    WHERE customer_shortname = '{customer_name}'
    AND EXTRACT(YEAR FROM rp_date) IN ({years_str})
    """
    
    # Conditionally add the rp_label_final filter
    if is_final_checkbox:
        query += "AND rp_label_final = 'Final Checkbox' "
    
    return query

def survey_query(report_table=None):
    query = f"""
    SELECT
        UPPER(C.Name) CustomerName,
        CASE
            WHEN ReportType.Description = 'Compliance' THEN CONCAT('CR-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
            WHEN ReportType.Description = 'Emissions' THEN CONCAT('ER-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
            ELSE CONCAT('CR-', SUBSTRING(CONVERT(nvarchar(50), R.Id), 1, 6))
        END AS ReportName,
        R.Id AS ReportId,
        S.Tag,
        U.UserName,
        A.SerialNumber AnalyzerSerialNumber,
        S.StartDateTime AS StartDateTimeSurvey,
        S.EndDateTime   AS EndDateTimeSurvey,
        U.FirstName UserFirstName,
        U.LastName UserLastName,
        U.FirstName + ' ' + U.LastName AS Driver,
        S.Id AS SurveyId,
        S.StartDateTime,
        S.EndDateTime,
        S.StabilityClass,
        S.Status,
        S.BuildNumber,
        S.AnalyzerId,
        S.ReferenceGasBottleId,
        SU.Description SurveyorUnit,
        SMT.Description SurveyMode,
        S.DrivingLengthMeters / 1000 AS DrivingLengthKM,
        S.DrivingLengthMeters / 1000 * 0.621371 AS DrivingLengthMiles,
        ROUND((SELECT SUM(DurationSeconds) FROM Segment WHERE SurveyId = S.Id AND Mode = 0), 0) DurationSeconds,
        (SELECT SUM(DurationSeconds) / 60.0
        FROM Segment
        WHERE SurveyId = S.Id AND Mode = 0) AS DurationMinutes,
    DATEDIFF(MINUTE, S.StartDateTime, S.EndDateTime) AS RawDurationMinutes,
        S.StartEpoch,
        S.EndEpoch,
        L.Description AS Zone ,
        TZ.Description AS TimeZone
    FROM Customer C
        INNER JOIN [User] U ON C.Id = U.CustomerId
        INNER JOIN Survey S ON U.Id = S.UserId
        INNER JOIN ReportDrivingSurvey RDS on S.Id = RDS.SurveyId
        INNER JOIN Report R on RDS.ReportId = R.Id
        INNER JOIN ReportType ON R.ReportTypeId = ReportType.Id
        INNER JOIN Location L ON S.LocationId  = L.Id
        INNER JOIN TimeZone TZ ON U.TimeZoneId = TZ.Id
        LEFT JOIN Analyzer A ON S.AnalyzerId = A.Id
        LEFT JOIN SurveyorUnit SU on S.SurveyorUnitId = SU.Id
        LEFT JOIN SurveyModeType SMT on S.SurveyModeTypeId = SMT.Id
    WHERE R.Id  IN (SELECT ReportId FROM {report_table})"""
    return query

def get_surveys(user_table, start_date = None, survey_table = None, end_date = None):
    if survey_table is not None:
        into_clause = f"INTO {survey_table}"
    else:
        into_clause = ""
    if start_date is not None:
        start_date_clause = f"AND s.StartDateTime >= '{start_date}'"
    else:
        start_date_clause = ""
    query = f"""
    SELECT 
        s.Id as SurveyId,
        s.UserId as UserId,
        u.UserName as UserName,
        su.Description as SurveyorUnit,
        a.SerialNumber as AnalyzerSerialNumber,
        s.Tag as SurveyTag,
        S.StartDateTime AS StartDateTimeSurvey,
        S.EndDateTime   AS EndDateTimeSurvey,
        U.FirstName + ' ' + U.LastName AS Driver,
        S.StartDateTime,
        S.EndDateTime,
        S.StabilityClass,
        S.Status,
        S.BuildNumber,
        S.AnalyzerId,
        S.ReferenceGasBottleId,
        S.DrivingLengthMeters / 1000 AS DrivingLengthKM,
        S.DrivingLengthMeters / 1000 * 0.621371 AS DrivingLengthMiles,
        ROUND((SELECT SUM(DurationSeconds) FROM Segment WHERE SurveyId = S.Id AND Mode = 0), 0) DurationSeconds,
        (SELECT SUM(DurationSeconds) / 60.0
        FROM Segment
        WHERE SurveyId = S.Id AND Mode = 0) AS DurationMinutes,
    DATEDIFF(MINUTE, S.StartDateTime, S.EndDateTime) AS RawDurationMinutes
    {into_clause} FROM Survey s
    JOIN [User] u ON s.UserId = u.Id
    INNER JOIN Analyzer a ON s.AnalyzerId = a.Id
    LEFT JOIN SurveyorUnit su ON s.SurveyorUnitId = su.Id
    WHERE UserId IN (SELECT UserId FROM {user_table})
    {start_date_clause}
    """
    if end_date:
        query += f"AND s.StartDateTime <= '{end_date}'"
    return query

def get_users(customer_name, user_table):
    query = f"""
    SELECT 
    u.Id as UserId,
    u.UserName as UserName
    INTO {user_table}
    FROM [User] u
    JOIN Customer c ON c.id = u.CustomerId 
    WHERE 
    LOWER(c.Name) = LOWER('{customer_name}')
    """
    return query

def emission_sources_table_query_given_report_id(report_table=None):
    query = f"""
    SELECT
        UPPER(CONVERT(NVARCHAR(50), ES.Id))     AS EmissionSourceId,
        ES.PeakNumber AS LisaNumber,
        CASE
            WHEN ES.UniqueIdentifier IS NOT NULL THEN ES.UniqueIdentifier
            ELSE
                CONCAT(
                    'CR-',
                    SUBSTRING(CONVERT(nvarchar(50), ES.ReportId), 1, 6),
                    CASE
                        WHEN ES.PeakNumber >= 0 THEN '-L-'
                        ELSE '-LF-'
                    END,
                    ABS(ES.PeakNumber)
                )
        END AS UniqueIdentifier,
        ES.CH4,
        ES.ClassificationConfidence,
        ES.RepresentativePeakId,
        ES.PriorityScore2,
        ES.Disposition,
        ES.DetectionProbability,
        ES.EmissionRate,
        ES.EmissionRateAMean,
        ES.EmissionRateAStd,
        ES.EmissionRateGMean,
        ES.EmissionRateGStd,
        ES.EmissionRateLowerBound,
        ES.EmissionRateUpperBound,
        ES.EthaneRatio,
        ES.EthaneRatioUncertainty,
        ES.GeocodeAddress,
        ES.GpsLatitude AS LisaLatitude,
        ES.GpsLongitude AS LisaLongitude,
        ES.Lisa.STAsText() AS LisaGeometry,
        ES.IsFiltered,
        ES.MaxAmplitude,
        ES.MaxCarSpeed,
        ROUND(CAST(ES.NumberOfPeaks AS FLOAT) / NULLIF(CAST(ES.NumberOfPasses AS FLOAT), 0), 2) AS Persistence,
        ES.MaxWindSpeed,
        ES.MinWindSpeed,
        ES.NumberOfPasses,
        ES.NumberOfPeaks,
        ES.PeakNumber,
        ES.PriorityScore,
        ES.RankingGroup AS RiskRankingBin,
        (SELECT SurveyId FROM Peak WHERE Id = ES.RepresentativePeakId) AS SurveyId,
        ES.ReportId,
        ES.EmissionRate * 0.471947 AS "EmissionRate(lpm)",
        ES.EmissionRate * 19.1 AS "EmissionRate(g/h)",
        ES.RepresentativeEmissionRate,
        ES.RepresentativeEmissionRate * 0.471947 AS "RepresentativeEmissionRate(lpm)",
        ES.RepresentativeEmissionRate * 19.1 AS "RepresentativeEmissionRate(g/h)",
        ES.RepresentativeBinLabel,
        P.EpochTime AS RepresentativePeakEpochTime,
        STUFF((SELECT DISTINCT ' | ' + L.Title
               FROM ReportLabel RL
               INNER JOIN Label L ON RL.LabelId = L.Id
               WHERE RL.ReportId = R.Id AND RL.IsActive = 1
               FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 2, '') AS Labels,
        (SELECT COUNT(DISTINCT L.Title)
         FROM ReportLabel RL
         INNER JOIN Label L ON RL.LabelId = L.Id
         WHERE RL.ReportId = R.Id AND RL.IsActive = 1) AS NumberOfLabels,
        TZ.Description AS CommonTimeZone
    FROM Customer C
        JOIN Report R ON C.Id = R.CustomerID
        JOIN EmissionSource ES ON R.Id = ES.ReportId
        LEFT JOIN Peak P ON ES.RepresentativePeakId = P.Id
        LEFT JOIN ReportCompliance RC ON R.Id = RC.ReportId
        LEFT JOIN ReportStatusType RST ON R.ReportStatusTypeId = RST.Id
        LEFT JOIN ReportAreaCovered RAC ON R.Id = RAC.ReportId
        INNER JOIN ReportType ON R.ReportTypeId = ReportType.Id
        INNER JOIN TimeZone TZ ON R.TimeZoneId = TZ.Id
    WHERE R.Id IN (SELECT ReportId FROM {report_table})
      AND (ES.Disposition = 1 OR ES.Disposition = 3)
    """
    return query

@setup_query
def query_box_table(report_table = None, table_name = None):
    if table_name is not None:
        into_clause = f"INTO {table_name}"
    else:
        into_clause = ""
    query = f"""SELECT B.Id as BoxId,
                B.BoxShape.STAsText() as BoxShape,
                (SELECT BT.Name FROM BoxTypes BT WHERE BT.Id = B.BoxTypeId) AS BoxType,
                B.ReportId, B.UniqueIdentifier
                {into_clause}
                FROM Box B 
                
                WHERE B.ReportId IN (SELECT ReportId FROM {report_table})
                """
    return query

@setup_query
def query_report_investigation(box_table = None, table_name = None):
    if table_name is not None:
        into_clause = f"INTO {table_name}"
    else:
        into_clause = ""
    query = f"""SELECT RI.* , 
    (
        SELECT ITT.Name 
        FROM InvestigationTemplateType ITT 
        WHERE ITT.Id = (
            SELECT IT.InvestigationTemplateTypeId 
            FROM InvestigationTemplate IT 
            WHERE IT.Id = RI.InvestigationTemplateId
        )
    ) AS InvestigationTemplateType
    FROM ReportInvestigation RI 
    WHERE RI.BoxId IN (SELECT BoxId FROM {box_table})"""
    return query