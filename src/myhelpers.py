from colorama import Fore, Back, Style, init
import matplotlib.pyplot as plt
import pandas as pd


init(autoreset=True)

def printme(data):
    print(Fore.RED + "DataFrame type: \n", data.dtypes)
    print(Fore.RED + "DataFrame head: \n", data.head())
    print(Fore.RED + "DataFrame tail: \n", data.tail())
    print(Fore.RED + "DataFrame shape: \n", data.shape)
    print(Fore.RED + "DataFrame describe: \n", data.describe())
    print(Fore.RED + "DataFrame index type: \n", data.index.dtype)
    data.info(verbose = True)


################
# Helper functions for IMF trade data
################

def importersNLD(exportertoNLD):
    # checks--https://data.imf.org/regular.aspx?key=61013712
   
    nld1 = pd.read_csv('instrument101.csv', index_col=[0])
    nld1 = nld1[['ImporterValueCIF', 'Importer_from_Exporter', 'Year']]
    nld2 = nld1[nld1['Importer_from_Exporter'] == "NLD_DEU"]
    print(nld2)
    
    nld2['ImporterValueCIF'].plot()
    plt.show()

    return nld2
   
#importersNLD('DEU')

def exportersNLD(exportertoNLD):
    # checks--https://data.imf.org/regular.aspx?key=61013712
   
    nld1 = pd.read_csv('instrument101.csv', index_col=[0])
    nld1 = nld1[['ExportedValueFOB', 'Exporter_to_Importer', 'Year']]
    nld2 = nld1[nld1['Exporter_to_Importer'] == "NLD_DEU"]
    print(nld2)
    
    nld2['ExportedValueFOB'].plot()
    plt.show()

    return nld2
   
#exportersNLD('DEU')

def tradebalanceNLD(counterParty):
    nlddata = pd.read_csv('instrument101.csv', index_col=[0])
    exportfrom = nlddata[['ExportedValueFOB', 'Exporter_to_Importer', 'Year']]
    exportfrom = exportfrom[exportfrom['Exporter_to_Importer'] == counterParty]
    print(exportfrom)

    # trade balance
    # reverse order of countries
    counterParty1 = counterParty[-3:] + "_" + counterParty[0:3]
    importfrom = nlddata[['ImporterValueCIF', 'Importer_from_Exporter', 'Year']]
    importfrom = importfrom[importfrom['Importer_from_Exporter'] == counterParty1] # reverses string
    print(importfrom)

    combineddata = pd.merge(exportfrom, importfrom, left_on="Year", right_on="Year")
    combineddata.sort_values(['Year'], ascending=True, inplace=True)
    print(combineddata)
    combineddata['tradeBalance'] = combineddata['ExportedValueFOB'] - combineddata['ImporterValueCIF']

    country = counterParty[0:3]
    combineddata[['ExportedValueFOB', 'ImporterValueCIF', 'tradeBalance']].plot(title=f"Trade balance for {country}")
    plt.show()

# counterParty = "NLD_CHN"
# tradebalanceNLD(counterParty)

def totalexportsperyear(country1):
    # checked: https://data.imf.org/?sk=9d6028d4-f14a-464c-a2f2-59b2cd424b85&sid=1514498232936

    nlddata = pd.read_csv('instrument101.csv', index_col=[0])
    exportfrom = nlddata[['ExportedValueFOB', 'Exporter_to_Importer', 'Year']]
    
    exportfrom['Exporter'] = exportfrom['Exporter_to_Importer'].str[0:3]
    exportfrom = exportfrom[exportfrom['Exporter'] == country1]
    exportfrom.drop(columns=['Exporter_to_Importer', 'Exporter'], inplace=True)
    
    sumexports = exportfrom.groupby(['Year']).sum()

    return sumexports

def totalimportsperyear(country):
    # checked: https://data.imf.org/?sk=9d6028d4-f14a-464c-a2f2-59b2cd424b85&sid=1514498232936

    nlddata = pd.read_csv('instrument101.csv', index_col=[0])
    importfrom = nlddata[['ImporterValueCIF', 'Importer_from_Exporter', 'Year']]
    
    importfrom['Importer'] = importfrom['Importer_from_Exporter'].str[0:3]
    importfrom = importfrom[importfrom['Importer'] == country]
    importfrom.drop(columns=['Importer_from_Exporter', 'Importer'], inplace=True)
    
    sumimports = importfrom.groupby(['Year']).sum()
    
    return sumimports

#totalimportsperyear("CHN")

################
# END: Helper functions for IMF trade data
################
