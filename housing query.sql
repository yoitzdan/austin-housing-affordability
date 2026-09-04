-- ============================================================
-- AUSTIN HOUSING AFFORDABILITY & ECONOMIC ANALYSIS
-- SQL ANALYSIS
-- Cities: Austin, Dallas, Houston, San Antonio
-- Period: 2015-2024
-- ============================================================


-- ============================================================
-- PART 1: SUMMARY STATISTICS
-- Purpose:
-- Use aggregate functions to summarize the housing market.
-- AVG = average
-- MIN = smallest value
-- MAX = largest value
-- ============================================================

SELECT
    City,
    AVG(HomeValue) AS AverageHomeValue,
    AVG(Rent) AS AverageRent,
    AVG(MedianIncome) AS AverageIncome,
    MIN(HomeValue) AS LowestHomeValue,
    MAX(HomeValue) AS HighestHomeValue
FROM affordability
GROUP BY City
ORDER BY AverageHomeValue DESC;



-- ============================================================
-- PART 2: AFFORDABILITY COMPARISON
-- Purpose:
-- Compare the main affordability measures across the 4 cities.
-- Higher ratios generally mean housing is less affordable.
-- ============================================================

SELECT
    City,
    AVG(PriceToIncomeRatio) AS AveragePriceToIncome,
    AVG(RentToIncomeRatio) AS AverageRentToIncome,
    AVG(MortgagePaymentToIncome) AS AverageMortgageToIncome
FROM affordability
GROUP BY City
ORDER BY AveragePriceToIncome DESC;



-- ============================================================
-- PART 3: AUSTIN OVER TIME
-- Purpose:
-- Track how Austin's housing market and affordability changed
-- between 2015 and 2024.
-- ============================================================

SELECT
    Year,
    AVG(HomeValue) AS AverageHomeValue,
    AVG(Rent) AS AverageRent,
    AVG(MedianIncome) AS AverageIncome,
    AVG(PriceToIncomeRatio) AS PriceToIncome,
    AVG(RentToIncomeRatio) AS RentToIncome,
    AVG(MortgagePaymentToIncome) AS MortgageToIncome
FROM affordability
WHERE City = 'Austin'
GROUP BY Year
ORDER BY Year;



-- ============================================================
-- PART 4: CASE WHEN
-- Purpose:
-- Create categories based on affordability levels.
-- ============================================================

SELECT
    City,
    Year,
    AVG(PriceToIncomeRatio) AS PriceToIncome,

    CASE
        WHEN AVG(PriceToIncomeRatio) >= 7 THEN 'Very High'
        WHEN AVG(PriceToIncomeRatio) >= 5 THEN 'High'
        ELSE 'Lower'
    END AS AffordabilityLevel

FROM affordability
GROUP BY City, Year
ORDER BY City, Year;



-- ============================================================
-- PART 5: CTE + LAG()
-- Purpose:
-- Calculate year-over-year home value growth.
-- ============================================================

WITH yearly_housing AS (

    SELECT
        City,
        Year,
        AVG(HomeValue) AS AverageHomeValue

    FROM affordability
    GROUP BY City, Year
),

housing_growth AS (

    SELECT
        City,
        Year,
        AverageHomeValue,

        LAG(AverageHomeValue) OVER (
            PARTITION BY City
            ORDER BY Year
        ) AS PreviousYearHomeValue

    FROM yearly_housing
)

SELECT
    City,
    Year,
    AverageHomeValue,
    PreviousYearHomeValue,

    ROUND(
        (
            (AverageHomeValue - PreviousYearHomeValue)
            / PreviousYearHomeValue
        ) * 100,
        2
    ) AS HomeValueGrowthPercent

FROM housing_growth
ORDER BY City, Year;



-- ============================================================
-- PART 6: RANK()
-- Purpose:
-- Rank cities by housing affordability for each year.
-- ============================================================

WITH yearly_affordability AS (

    SELECT
        City,
        Year,
        AVG(PriceToIncomeRatio) AS PriceToIncome

    FROM affordability
    GROUP BY City, Year
)

SELECT
    City,
    Year,
    PriceToIncome,

    RANK() OVER (
        PARTITION BY Year
        ORDER BY PriceToIncome DESC
    ) AS AffordabilityRank

FROM yearly_affordability
ORDER BY Year, AffordabilityRank;

-- ============================================================
-- PART 9: JOIN MULTIPLE DATASETS
-- Purpose:
-- Combine housing, income, unemployment, and mortgage data.
-- ============================================================

SELECT
    h.City,
    h.Date,
    h.HomeValue,
    h.Rent,
    i.MedianIncome,
    u.UnemploymentRate,
    m.MortgageRate

FROM housing_data AS h

-- Match annual income by city and year
LEFT JOIN income_data AS i
    ON h.City = i.City
    AND h.Year = i.Year

-- Match monthly unemployment by city, year, and month
LEFT JOIN unemployment_data AS u
    ON h.City = u.City
    AND h.Year = u.Year
    AND h.Month = u.Month

-- Mortgage rate is national, so city is not needed
LEFT JOIN mortgage_data AS m
    ON h.Year = m.Year
    AND h.Month = m.Month

ORDER BY h.City, h.Date;