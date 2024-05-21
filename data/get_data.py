import pandas as pd
from myhelpers import printme
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
import colorama


# based on: 
# main paper: chrome-extension://efaidnbmnnnibpcajpcglclefindmkaj/https://www.imf.org/external/pubs/ft/wp/2003/wp0337.pdf

# IMF: https://data.imf.org/?sk=9d6028d4f14a464ca2f259b2cd424b85
# see main paper for explanation of limits
# data should be logged

# IMF conversion codes
# https://www.imf.org/-/media/Websites/IMF/imported-datasets/external/pubs/ft/wp/2011/Data/_wp11154.ashx

# Nominal GDP and real GDP per capita, total population, Penn World tables: https://www.rug.nl/ggdc/productivity/pwt/?lang=en

# Geographical distance: http://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=6

######
# main trade data
######
dt1 = pd.read_csv(r"data\DOT_05-20-2024 10-49-23-10_timeSeries.csv")
dt1.to_csv("tmp1.csv")
printme(dt1)

######
# merge iso3
######
#importer
iso1 = pd.read_csv("data\pdf_extractor\imf_iso3codes_usethese.csv")
dt2 = dt1.merge(iso1, left_on="Country Code", right_on="imf_code", how = "left")
dt2.rename(columns={"iso3_code": "iso3_code_importer"}, inplace = True)
iso1 = pd.read_csv("data\pdf_extractor\imf_iso3codes_usethese.csv")
dt3 = dt2.merge(iso1, left_on="Counterpart Country Code", right_on="imf_code", how = "left")
dt3.rename(columns={"iso3_code": "iso3_code_exporter"}, inplace = True)
dt3.drop(columns=['Unnamed: 83', 'Unnamed: 0_x', 'imf_code_x','Unnamed: 0_y', 'imf_code_y'], inplace=True)

# ### NLD test
nld1 = dt3[dt3['iso3_code_importer']=='NLD']
nld1 = nld1[nld1['Indicator Name']=='Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars']
nld1 = nld1[nld1['Attribute'] == 'Value'] #this removes 'e'
nld1.iloc[:, np.r_[40:82]] =  nld1.iloc[:, np.r_[40:82]].astype(float)
printme(nld1)
nld1.to_csv("tmp4.csv")

# # dont want aggregates
# aggs = [1, 80, 92, 110, 163, 200, 205, 399, 400, 405, 489, 505, 598, 884, 901, 903, 910, 938, 998]
# nld2 = nld2[~nld2['Counterpart Country Code'].isin(aggs)]

# ###
# nld2['Relationship'] = nld2['Country Code'].astype(str) + "-" + nld2['Counterpart Country Code'].astype(str)
# printme(nld2)
# nld3 = nld2.iloc[:, np.r_[4:80]]
# nld3.set_index(['Relationship'], inplace = True)
# nld3 = nld3.astype(float)
# printme(nld3)


# nld3.T.plot()
# plt.show()
# nld3.to_csv('tmp3.csv')

# print(nld2)
