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
def maintradedata():
    trade_data1 = pd.read_csv(r"data\DOT_05-20-2024 10-49-23-10_timeSeries.csv")
    printme(trade_data1)

    ######
    # merge iso3
    ######
    iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
    trade_data2 = trade_data1.merge(iso1, left_on="Country Code", right_on="imf_code", how = "left")
    trade_data2.rename(columns={"iso3_code": "iso3_code_importer"}, inplace = True)
    iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
    trade_data3 = trade_data2.merge(iso1, left_on="Counterpart Country Code", right_on="imf_code", how = "left")
    trade_data3.rename(columns={"iso3_code": "iso3_code_exporter"}, inplace = True)
    trade_data3.drop(columns=['Unnamed: 83', 'Unnamed: 0_x', 'imf_code_x','Unnamed: 0_y', 'imf_code_y'], inplace=True)

    # Keep this, it helps with stacking below
    trade_data3.fillna(0, inplace=True)

    # necessary to remove 'e's from data, so already beginning to subsetting
    trade_data3 = trade_data3[trade_data3['Attribute'] == 'Value'] 

    # remove: dont want aggregates and 'lost'countries
    aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
    trade_data3 = trade_data3[~trade_data3['Counterpart Country Code'].isin(aggs)]

    return trade_data3

maintradedata1 = maintradedata()

######
### Select state
######
def chooseCountry(mtd1, state):

    state1 = mtd1[mtd1['iso3_code_importer']==state]
    state1 = state1[state1['Indicator Name']=='Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars']

    ### choose index
    state1['Relationship_1'] = state1['Country Code'].astype(str) + "-" + state1['Counterpart Country Code'].astype(str)
    state1['Relationship_2'] = state1['iso3_code_importer'].astype(str) + "-" + state1['iso3_code_exporter'].astype(str)
    state1.set_index(['Relationship_2'], inplace = True)

    ### unique countries
    print("Unique counter parties: ", state1['iso3_code_exporter'].nunique())
    
    ### select only actual trade data
    state3 = state1.iloc[:, np.r_[7:83]]  # 19 is 1960, 52 is 1992 
    state3 = state3.astype(float)

    ######
    # pivot
    ######
    state_stacked = state3.stack().to_frame()
    state_stacked['Year'] = state_stacked.index.get_level_values(1)
    #state_stacked['Country'] = state_stacked.index.get_level_values(0)

    state_stacked.index = state_stacked.index.get_level_values(0)
    state_stacked.columns = ['Import', 'Year']
    print(state_stacked)

    ######
    # duplicates
    ######
    #state_stacked.drop_duplicates(inplace = True)

    return state_stacked

COUNTRY = "JPN"

dt1 = chooseCountry(maintradedata1, COUNTRY)
dt1.to_csv("tmpNLD.csv")

def checkindex():
    from itertools import groupby
    countitems = dt1.index.tolist()
    # Group and count similar records
    res = []
    x = list(set(countitems))
    for i in x:
        a = countitems.count(i)
        b = "".join(i)
        res.append((a, b))
    # printing result
    print("Grouped and counted list is : " + str(res))

#checkindex()

def cepiidata(data, COUNTRY):
    ##############################################
    ### NLD add additional data
    ##############################################
    ######
    # distance
    ######
    dist1 = pd.read_csv(r"C:\Users\jpark\VSCode\gdp_trade\data\dist_cepii.csv")
    print(dist1)
    printme(dist1)
    dist1['iso_o'].replace('ROM', 'ROU', regex=True, inplace=True)
    dist1['iso_d'].replace('ROM', 'ROU', regex=True, inplace=True)
    dist1['iso_o'].replace('YUG', 'MNE', regex=True, inplace=True)
    dist1['iso_d'].replace('YUG', 'MNE', regex=True, inplace=True)

    nld1 = dist1[dist1['iso_o'] == COUNTRY]
    nld1.to_csv("tmpnld1.csv")

    #nld1['Relationship_1'] = nld1['iso_o'].astype(str) + "-" + nld1['iso_d'].astype(str)
    nld1['Relationship_1'] = nld1['iso_o'] + "-" + nld1['iso_d']
    nld1.set_index(['Relationship_1'], inplace=True)

    ######## MERGE
    nld_mrd1 = pd.merge(data, nld1, left_index = True, right_index = True, how = "left")
    nld_mrd1.index = data.index
    ########


    selectthesecols = [0,1,2,3,4,5,6,7,8,11,13]
    nld_mrd1 = nld_mrd1.iloc[:, selectthesecols]
    nld_mrd1.to_csv("tmp40404.csv")

    ######
    # Country information (of counter country)
    ######
    geo_cepii = pd.read_csv(r"C:\Users\jpark\VSCode\gdp_trade\data\geo_cepii.csv")

    geo_cepii['iso3'].replace('ROM', 'ROU', regex=True, inplace=True)
    geo_cepii['iso3'].replace('YUG', 'MNE', regex=True, inplace=True)


    print(geo_cepii.columns)
    geo_cepii = geo_cepii.loc[:, ['iso3', 'area', 'landlocked', 'lat', 'lon', 'langoff_1', 'lang20_1', 'colonizer1']]
    geo_cepii.drop_duplicates(subset=['iso3'], keep='last', inplace=True)

    nld_mrg2 = pd.merge(nld_mrd1, geo_cepii, left_on="iso_d", right_on="iso3", how="left")
    nld_mrg2['Year'] = nld_mrg2['Year'].astype(int)

    nld_mrg2['tmp_key'] = nld_mrg2['iso_o'] + "_" + nld_mrg2['Year'].astype(str)
    nld_mrg2['tmp_key_2'] = nld_mrg2['iso_d'] + "_" + nld_mrg2['Year'].astype(str)
    nld_mrg2.to_csv("tmp666.csv")
    return nld_mrg2

nld_mrg2 = cepiidata(dt1, COUNTRY)

def pwtdata(state, nld_mrg2):

    #######
    # pwt1001 data (of both countries)
    #######
    pwtdata = pd.read_excel(r'C:\Users\jpark\VSCode\gdp_trade\data\pwt1001.xlsx', sheet_name="Data")
    pwtdata['tmp_key'] = pwtdata['countrycode'] + "_" + pwtdata['year'].astype(str)
    pwtdata['tmp_key_2'] = pwtdata['countrycode'] + "_" + pwtdata['year'].astype(str)
    pwtdata = pwtdata[['tmp_key', 'countrycode', 'year', 'rgdpo', 'pop', 'tmp_key_2']]  ############################## Make selections here for pwt data ###############

    pwtdata.to_csv("xyz.csv")

    nld_pwt = pwtdata[pwtdata['countrycode'] == state]
    nld_pwt.to_csv("nld_pwt.csv")

    # first connect with NLD
    nld_mrg3 = pd.merge(nld_mrg2, nld_pwt, left_on="tmp_key", right_on="tmp_key", how="left")
    print(nld_mrg3)
    nld_mrg3.to_csv("tmp1121.csv")

    # now use all data, in pwtdata
    nld_mrg4 = pd.merge(nld_mrg3, pwtdata, left_on="tmp_key_2_x", right_on="tmp_key_2", how="left")

    # drop unused columns
    nld_mrg4.drop(columns = ['iso3', 'tmp_key_x', 'tmp_key_2_x', 'countrycode_x', 'year_x', 'tmp_key_2_y', 'tmp_key_y', 'countrycode_y', 'year_y', 'tmp_key_2'], inplace=True)
    nld_mrg4.to_csv("tmp333333.csv")

    return nld_mrg4

nld_mrg4 = pwtdata(COUNTRY, nld_mrg2)
nld_mrg4.dropna(subset = ['iso_o'], inplace=True)
#nld_final = nld_mrg4.dropna()
nld_mrg4.to_csv("tmp22222222222222.csv")

print('Unique: ', nld_mrg4.nunique())