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

class Trade_Regression:
    def __init__(self, state):
        self.state = state

    def maintradedata(self):
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

    #maintradedata1 = maintradedata(self)

    ##################
    ### Select state
    ##################

    def chooseCountry(self, mtd1):

        state1 = mtd1[mtd1['iso3_code_importer']==self.state]
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


    def checkindex(self, data):
        countitems = data.index.tolist()
        # Group and count similar records
        res = []
        x = list(set(countitems))
        for i in x:
            a = countitems.count(i)
            b = "".join(i)
            res.append((a, b))
        print("Grouped and counted list is : " + str(res))


    def cepiidata(self, data):
        ##############################################
        ### NLD add additional data
        ##############################################

        ######
        # distance and other measures of similarity
        ######
        dist1 = pd.read_csv(r"C:\Users\jpark\VSCode\gdp_trade\data\dist_cepii.csv")
        printme(dist1)

        ###### cepii has their own way of doing things
        dist1['iso_o'].replace('ROM', 'ROU', regex=True, inplace=True)
        dist1['iso_d'].replace('ROM', 'ROU', regex=True, inplace=True)
        dist1['iso_o'].replace('YUG', 'MNE', regex=True, inplace=True)
        dist1['iso_d'].replace('YUG', 'MNE', regex=True, inplace=True)

        ###### select the importing state 
        state1 = dist1[dist1['iso_o'] == self.state]
       
        ###### create index
        state1['Relationship_1'] = state1['iso_o'] + "-" + state1['iso_d']
        state1.set_index(['Relationship_1'], inplace=True)

        ######## MERGE ########
        nld_mrd1 = pd.merge(data, state1, left_index = True, right_index = True, how = "left")
        nld_mrd1.index = data.index
        ########

        ######## select only needed columns
        selectthesecols = [0,1,2,3,4,5,6,7,8,11,13]
        nld_mrd1 = nld_mrd1.iloc[:, selectthesecols]

        #########################
        # Country economic information (of counter country)
        ######################### 
        geo_cepii = pd.read_csv(r"C:\Users\jpark\VSCode\gdp_trade\data\geo_cepii.csv")

        ######## cepii has their own way of doing things
        geo_cepii['iso3'].replace('ROM', 'ROU', regex=True, inplace=True)
        geo_cepii['iso3'].replace('YUG', 'MNE', regex=True, inplace=True)

        ######## select only needed columns
        geo_cepii = geo_cepii.loc[:, ['iso3', 'area', 'landlocked', 'continent', 'lat', 'lon', 'langoff_1', 'lang20_1', 'colonizer1']]
        
        ######## in some cases there are two rows for same country
        geo_cepii.drop_duplicates(subset=['iso3'], keep='last', inplace=True)

        ######## MERGE ########
        nld_mrg2 = pd.merge(nld_mrd1, geo_cepii, left_on="iso_d", right_on="iso3", how="left")
        nld_mrg2['Year'] = nld_mrg2['Year'].astype(int)

        ######## Add importing state area
        area1 = geo_cepii[geo_cepii['iso3']=='NLD']['area']
        nld_mrg2['area_importer'] = np.repeat(area1.values, nld_mrg2.shape[0])
        
        ######## indices for later merges
        nld_mrg2['tmp_key'] = nld_mrg2['iso_o'] + "_" + nld_mrg2['Year'].astype(str)
        nld_mrg2['tmp_key_2'] = nld_mrg2['iso_d'] + "_" + nld_mrg2['Year'].astype(str)
       
        return nld_mrg2


    def pwtdata(self, nld_mrg2):

        #######
        # pwt1001 data (for both countries)
        #######
        pwtdata = pd.read_excel(r'C:\Users\jpark\VSCode\gdp_trade\data\pwt1001.xlsx', sheet_name="Data")
        pwtdata['tmp_key'] = pwtdata['countrycode'] + "_" + pwtdata['year'].astype(str)
        pwtdata['tmp_key_2'] = pwtdata['countrycode'] + "_" + pwtdata['year'].astype(str)

        # nominal gdp 
        #   rgdpe: Expenditure-side real GDP at chained PPPs (in mil. 2017US$)
        #   cgdpe: Expenditure-side real GDP at current PPPs (in mil. 2017US$)
        #   pop: population

        pwtdata = pwtdata[['tmp_key', 'countrycode', 'year', 'rgdpe', 'cgdpe', 'pop', 'tmp_key_2']]  # See orginal file: make selections here for pwt data ###############

        nld_pwt = pwtdata[pwtdata['countrycode'] == self.state]
       
        # first connect with NLD
        nld_mrg3 = pd.merge(nld_mrg2, nld_pwt, left_on="tmp_key", right_on="tmp_key", how="left")

        # now use all data, in pwtdata
        nld_mrg4 = pd.merge(nld_mrg3, pwtdata, left_on="tmp_key_2_x", right_on="tmp_key_2", how="left")

        # drop unused columns
        nld_mrg4.drop(columns = ['iso3', 'tmp_key_x', 'tmp_key_2_x', 'countrycode_x', 'year_x', 'tmp_key_2_y', 'tmp_key_y', 'countrycode_y', 'year_y', 'tmp_key_2'], inplace=True)

        return nld_mrg4

    #nld_mrg4 = pwtdata(nld_mrg2)


from functools import reduce
allstates = ['NLD', 'DEU']
collect1 = []
for i in allstates:

    tr1 = Trade_Regression(i)
    trade_data3 = tr1.maintradedata()
    trade_data4 = tr1.chooseCountry(trade_data3)
    trade_data5 = tr1.cepiidata(trade_data4)
    onestate1 = tr1.pwtdata(trade_data5)

    onestate1.dropna(subset = ['iso_o'], inplace=True)

    onestate1.columns = [x.replace("_x", "_exporter") for x in onestate1.columns]
    onestate1.columns = [x.replace("_y", "_importer") for x in onestate1.columns]

    collect1.append(onestate1)


print(pd.concat(collect1))

# onestate1.to_csv("onestate1.csv")
# print('Unique: ', onestate1.nunique())