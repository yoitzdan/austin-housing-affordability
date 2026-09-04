import pandas as pd

### PART 1 FILTER HVI AND ORI

# home value dataset
zhvi = pd.read_csv("City_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")

# Rentals dataset
zori = pd.read_csv("City_zori_uc_sfrcondomfr_sm_month.csv")

# Inspect them
zhvi.head()
zori.head()

zhvi.shape 
zori.shape

zhvi.columns

# Creating a list of cities I prefer analyzing
cities = ["Austin", "Dallas", "Houston", "San Antonio"]

# New dataset that focus on cities in Texas
zhvi_tx = zhvi[
    (zhvi["StateName"] == "TX") &
    (zhvi["RegionName"].isin(cities))
]

zori_tx = zori[
    (zori["StateName"] == "TX") &
    (zori["RegionName"].isin(cities))
]

# Removing columns that aren't neccessary and keeping the dates
date_columns_zhvi = zhvi.columns[8:]
date_columns_zori = zori.columns[8:]

zhvi_tx = zhvi_tx[
    ["RegionName", "StateName", "Metro"] + list(date_columns_zhvi)
]

zori_tx = zori_tx[
    ["RegionName", "StateName", "Metro"] + list(date_columns_zori)
]

# using melt() to help shape the dataset in a certain way
zhvi_long = zhvi_tx.melt(
    id_vars=["RegionName", "StateName", "Metro"],
    var_name="Date",
    value_name="HomeValue"
)

zori_long = zori_tx.melt(
    id_vars=["RegionName", "StateName", "Metro"],
    var_name="Date",
    value_name="Rent"
)

zhvi_long.head()
zori_long.head()

# Convert in date datatype
zhvi_long["Date"] = pd.to_datetime(zhvi_long["Date"])
zori_long["Date"] = pd.to_datetime(zori_long["Date"])

# Rename RegionName to City
zhvi_long = zhvi_long.rename(
    columns={"RegionName": "City"}
)

zori_long = zori_long.rename(
    columns={"RegionName": "City"}
)

# Search for empty cells
zhvi_long.isna().sum()
zori_long.isna().sum()

# Keep home value data from 2015 onward to match rent data
zhvi_long = zhvi_long[
    zhvi_long["Date"] >= "2015-01-01"
]

# Merge both dataset
housing = pd.merge(
    zhvi_long,
    zori_long[["City", "Date", "Rent"]],
    on=["City", "Date"],
    how="inner"
)

# Sort by city and date
housing = housing.sort_values(["City", "Date"])

# Inspecting the filter data for HVI and ORI
housing.head()
housing.tail()
housing.shape

# Check final dataset that combines HVI and ORI
housing.isna().sum()
housing.duplicated(subset=["City", "Date"]).sum()


### PART 2 FILTER INCOME
years = list(range(2015, 2025))

income_list = []

# Create a loop to go over all the data from 2015 to 2024
for year in years:
    df = pd.read_csv(f"{year} Income.csv")

    # Keep certain columns
    df = df[
    [
        "Austin city, Texas!!Estimate",
        "Dallas city, Texas!!Estimate",
        "Houston city, Texas!!Estimate",
        "San Antonio city, Texas!!Estimate"
    ]
    ]

    # Restructure the table using melt() like the previous code
    df = df.melt(
    var_name="City",
    value_name="MedianIncome"
    )

    # Rename the rows
    df["City"] = [
    "Austin",
    "Dallas",
    "Houston",
    "San Antonio"
    ]

    # Add year in the column table
    df["Year"] = year

    # Replace string value into int values
    df["MedianIncome"] = (
    df["MedianIncome"]
    .str.replace(",", "")
    .astype(int)
    )

    income_list.append(df)

# Combine the all the dataframe into one big dataframe
income = pd.concat(
    income_list,
    ignore_index = True
)

### PART 3 FILTER MORTGAGE RATE
mortgage = pd.read_csv("Mortgage Rates.csv")

# Rename the columns
mortgage = mortgage.rename(
    columns = {
        "observation_date": "Date",
        "MORTGAGE30US": "MortgageRate"
    }
)

# Convert the text into Date datatype
mortgage["Date"] = pd.to_datetime(mortgage["Date"])

### PART 4 FILTER UNEMPLOYMENT RATE
austin_unemployment = pd.read_csv("AUST448UR.csv")
dallas_unemployment = pd.read_csv("DALL148UR.csv")
houston_unemployment = pd.read_csv("HOUS448UR.csv")
sanantonio_unemployment = pd.read_csv("SANA748UR.csv")

# Rename the columns
austin_unemployment = austin_unemployment.rename(
    columns={
        "observation_date": "Date",
        "AUST448UR": "UnemploymentRate"
    }
)

dallas_unemployment = dallas_unemployment.rename(
    columns={
        "observation_date": "Date",
        "DALL148UR": "UnemploymentRate"
    }
)

houston_unemployment = houston_unemployment.rename(
    columns={
        "observation_date": "Date",
        "HOUS448UR": "UnemploymentRate"
    }
)

sanantonio_unemployment = sanantonio_unemployment.rename(
    columns={
        "observation_date": "Date",
        "SANA748UR": "UnemploymentRate"
    }
)

# Add a column the cities
austin_unemployment["City"] = "Austin"
dallas_unemployment["City"] = "Dallas"
houston_unemployment["City"] = "Houston"
sanantonio_unemployment["City"] = "San Antonio"

# Combine all the datasets
unemployment = pd.concat(
    [
        austin_unemployment,
        dallas_unemployment,
        houston_unemployment,
        sanantonio_unemployment
    ],
    ignore_index = True
)

# Change text to Date datatype
unemployment["Date"] = pd.to_datetime(
    unemployment["Date"]
)

### PART 5 COMBING ALL FILTERED DATASETS

# Adding year and month to each dataset
housing["Year"] = housing["Date"].dt.year
housing["Month"] = housing["Date"].dt.month

mortgage["Year"] = mortgage["Date"].dt.year
mortgage["Month"] = mortgage["Date"].dt.month

unemployment["Year"] = unemployment["Date"].dt.year
unemployment["Month"] = unemployment["Date"].dt.month

# Merge mortgage rates into housing
analysis = pd.merge(
    housing,
    mortgage[["Year", "Month", "MortgageRate"]],
    on = ["Year", "Month"],
    how = "left"
)

# Merge umemployment
analysis = pd.merge(
    analysis,
    unemployment[["City", "Year", "Month", "UnemploymentRate"]],
    on = ["City", "Year", "Month"],
    how = "left"
)
# Check for missing values
analysis.isna().sum()

# Merge income
analysis = pd.merge(
    analysis,
    income[["City", "Year", "MedianIncome"]],
    on = ["City", "Year"],
    how = "left"
)

# PART 6 ADDING NEW CALCULATION

# Add home value-to-income ratio into the dataset
analysis["PriceToIncomeRatio"] = (
    analysis["HomeValue"] / analysis["MedianIncome"]
)

# Add rent-to-income ratio into the dataset
analysis["RentToIncomeRatio"] = (
    analysis["Rent"] / (analysis["MedianIncome"] / 12)
)

# 20% down, 30-year fixed mortgage, principal and interest only
analysis["LoanAmount"] = analysis["HomeValue"] * 0.80

# Add monthly rate in dataset
analysis["MonthlyRate"] = (
    analysis["MortgageRate"] / 100 / 12
)

# Mortgage payment formula
number_of_payments = 30 * 12

analysis["MortgagePayment"] = (
    analysis["LoanAmount"]
    * (
        analysis["MonthlyRate"]
        * (1 + analysis["MonthlyRate"]) ** number_of_payments
    )
    / (
        (1 + analysis["MonthlyRate"]) ** number_of_payments - 1
    )
)

# Add mortgage payment to income in dataset
analysis["MortgagePaymentToIncome"] = (
    analysis["MortgagePayment"] / (analysis["MedianIncome"] / 12)
)

### Part 6 Summary

# Create a new dataset with data up to 2024
affordability = analysis[
    analysis["Year"] <= 2024
].copy()

# Summary statistics
print(
    affordability[
        [
            "HomeValue",
            "Rent",
            "MedianIncome",
            "MortgageRate",
            "UnemploymentRate",
            "PriceToIncomeRatio",
            "RentToIncomeRatio",
            "MortgagePaymentToIncome"
        ]
    ].describe()
)

# Averages based on cities
city_summary = affordability.groupby("City")[
    [
        "HomeValue",
        "Rent",
        "MedianIncome",
        "PriceToIncomeRatio",
        "RentToIncomeRatio",
        "MortgagePaymentToIncome"
    ]
].mean()

print(city_summary)

affordability.to_csv("affordability_clean.csv", index=False)

# Export separate datasets for SQL JOIN practice

housing.to_csv("housing_data.csv", index=False)

income.to_csv("income_data.csv", index=False)

unemployment.to_csv("unemployment_data.csv", index=False)

mortgage.to_csv("mortgage_data.csv", index=False)