import pandas as pd

# strange code to change Belgium-Luxembourg to Belgium for years before 1997

data = pd.read_csv(r"data\DOT_06-02-2024 11-13-24-61_timeSeries.csv")
print(data.head())
data.loc[data['Country Name'] == "Belgium-Luxembourg", "Country Name"] = "BEL"
data.loc[data['Country Code'] == 126, "Country Code"] = 124

data.to_csv(r"data\DOT_06-02-2024 11-13-24-61_timeSeries.csv")
