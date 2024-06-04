import pandas as pd
from myhelpers import printme
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
import colorama
from myhelpers import printme
from functools import reduce
import seaborn as sns
plt.rcParams['figure.figsize'] = (10, 5)
plt.style.use('bmh')

pd.set_option("display.max_rows", 10)
pd.set_option("display.max_columns", 1000)

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
    def __init__(self, state, ImportExport):
        self.state = state
        self.ImportExport = ImportExport

    def maintradedata(self):
        trade_data1 = pd.read_csv(r"data\DOT_06-02-2024 11-13-24-61_timeSeries.csv")
        #printme(trade_data1)

        ######
        # merge iso3
        ######
        iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
        trade_data2 = trade_data1.merge(iso1, left_on="Country Code", right_on="imf_code", how = "left")
        trade_data2.rename(columns={"iso3_code": "iso3_code_importer"}, inplace = True)
        iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
        trade_data3 = trade_data2.merge(iso1, left_on="Counterpart Country Code", right_on="imf_code", how = "left")
        trade_data3.rename(columns={"iso3_code": "iso3_code_exporter"}, inplace = True)
        trade_data3.drop(columns=['Unnamed: 0_x', 'imf_code_x','Unnamed: 0_y', 'imf_code_y'], inplace=True)

        # Keep this, it helps with stacking below
        trade_data3.fillna(0, inplace=True)

        # necessary to remove 'e's from data, so already beginning to subsetting
        trade_data3 = trade_data3[trade_data3['Attribute'] == 'Value'] 

        # remove: dont want aggregates and 'lost'countries
        aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
        trade_data3 = trade_data3[~trade_data3['Counterpart Country Code'].isin(aggs)]
        aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
        trade_data3 = trade_data3[~trade_data3['Country Code'].isin(aggs)]

        return trade_data3

    #maintradedata1 = maintradedata(self)

    ##################
    ### Select state
    ##################

    def chooseImportCountry(self, mtd1):
        '''These are the countries that export to the given country'''

        state1 = mtd1[mtd1['iso3_code_importer']==self.state]

        if self.ImportExport == "Import_CIF":
            state1 = state1[state1['Indicator Name']=='Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars']
        elif self.ImportExport == "Export_FOB":
            state1 = state1[state1['Indicator Name']=='Goods, Value of Exports, Free on board (FOB), US Dollars']
        else: 
             print("You must choose Import_CIF or Export_FOB")


        ### choose index
        state1['Relationship_1'] = state1['Country Code'].astype(str) + "-" + state1['Counterpart Country Code'].astype(str)
        state1['Relationship_2'] = state1['iso3_code_importer'].astype(str) + "-" + state1['iso3_code_exporter'].astype(str)
        state1.set_index(['Relationship_2'], inplace = True)

        ### unique countries
        #print("Unique counter parties: ", state1['iso3_code_exporter'].nunique())
        
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

    def chooseExportCountry(self, mtd1):
        '''These are the countries that export to the given country'''

        state1 = mtd1[mtd1['iso3_code_exporter']==self.state]
        state1 = state1[state1['Indicator Name']=='Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars']

        ### choose index
        state1['Relationship_1'] = state1['Country Code'].astype(str) + "-" + state1['Counterpart Country Code'].astype(str)
        state1['index_tmp'] = state1['iso3_code_exporter'].astype(str) + "-" + state1['iso3_code_importer'].astype(str)
        state1.set_index(['index_tmp'], inplace = True)

        ### unique countries
        #print("Unique counter parties: ", state1['iso3_code_exporter'].nunique())
        
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
        state_stacked.columns = ['Export', 'Year']
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
        #printme(dist1)

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
        geo_cepii['iso3'] = geo_cepii['iso3'].replace('ROM', 'ROU', regex=True);
        geo_cepii['iso3'] = geo_cepii['iso3'].replace('YUG', 'MNE', regex=True);

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

        pwtdata = pwtdata[['tmp_key', 'countrycode', 'year', 'rgdpe', 'rgdpo', 'cgdpe', 'cgdpo', 'pop', 'tmp_key_2']]  # See orginal file: make selections here for pwt data ###############

        nld_pwt = pwtdata[pwtdata['countrycode'] == self.state]
       
        # first connect with NLD
        nld_mrg3 = pd.merge(nld_mrg2, nld_pwt, left_on="tmp_key", right_on="tmp_key", how="left")

        # now use all data, in pwtdata
        nld_mrg4 = pd.merge(nld_mrg3, pwtdata, left_on="tmp_key_2_x", right_on="tmp_key_2", how="left")

        # drop unused columns
        nld_mrg4.drop(columns = ['iso3', 'tmp_key_x', 'tmp_key_2_x', 'countrycode_x', 'year_x', 'tmp_key_2_y', 'tmp_key_y', 'countrycode_y', 'year_y', 'tmp_key_2'], inplace=True)

        return nld_mrg4

    #nld_mrg4 = pwtdata(nld_mrg2)

def runmodel(ImpExp):
    allstates = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")['iso3_code'].tolist()
    allstates = ['AFG']
    collect1 = []
    for i in allstates:
        print("state: ", i)
        tr1 = Trade_Regression(i, ImpExp)
        trade_data3 = tr1.maintradedata()
        trade_data4 = tr1.chooseImportCountry(trade_data3) #take in main trade data
        trade_data5 = tr1.chooseExportCountry(trade_data3) #take in main trade data
        
        ######
        # combine import and export data, then send it along
        ######
        trade_data4.index = trade_data4.index + "_" + trade_data4['Year']
        print(trade_data4)
        trade_data5.index = trade_data5.index + "_" + trade_data5['Year']
        print(trade_data5)

        merged1 = pd.merge(trade_data4, trade_data5, left_index=True, right_index=True, how = "left")
        merged1.drop(columns=['Year_y'], inplace=True)
        merged1.rename(columns={"Year_x": "Year"}, inplace=True)
        merged1.index = merged1.index.str[:-5] 
        #######

        trade_data6 = tr1.cepiidata(merged1)
        onestate1 = tr1.pwtdata(trade_data6)

        onestate1.dropna(subset = ['iso_o'], inplace=True)

        onestate1.columns = [x.replace("_x", "_importer") for x in onestate1.columns]
        onestate1.columns = [x.replace("_y", "_exporter") for x in onestate1.columns]

        #Trade balance
        onestate1['trade_balance'] = onestate1['Export'] - onestate1['Import']        

        #######
        # Trade instrument
        #######
        # Numerator: total trade between countries per year
        onestate1['gdpgdp_nominal'] = onestate1['cgdpe_exporter'] * onestate1['cgdpe_importer']

        # key
        onestate1["key1"] = onestate1['iso_o'] + "_" + onestate1['Year'].astype(str) + "_" + onestate1["iso_d"]


        collect1.append(onestate1)

    out1 = pd.concat(collect1)

    if ImpExp == "Import_CIF":
        out1.to_csv("data/allStates_AllYears_Imports_CIF.csv")
    else:
        out1.to_csv("data/allStates_AllYears_Export_FOB.csv")

# "Export_FOB" or "Import_CIF"
# runmodel("Import_CIF")

################
# Exports seperately
################

def exportsallcombinations():
    
    trade_data1 = pd.read_csv(r"data\DOT_06-02-2024 11-13-24-61_timeSeries.csv")
    
    ######
    # merge iso3
    ######
    iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
    trade_data2 = trade_data1.merge(iso1, left_on="Country Code", right_on="imf_code", how = "left")
    trade_data2.rename(columns={"iso3_code": "iso3_code_exporter"}, inplace = True)
    iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
    trade_data3 = trade_data2.merge(iso1, left_on="Counterpart Country Code", right_on="imf_code", how = "left")

    trade_data3.rename(columns={"iso3_code": "iso3_code_importer"}, inplace = True)
    trade_data3.drop(columns=['Unnamed: 0_x', 'imf_code_x','Unnamed: 0_y', 'imf_code_y'], inplace=True)

    # Keep this, it helps with stacking below
    trade_data3.fillna(0, inplace=True)

    # necessary to remove 'e's from data, so already beginning to subsetting
    trade_data3 = trade_data3[trade_data3['Attribute'] == 'Value'] 

    # remove: dont want aggregates and 'lost'countries
    aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
    trade_data3 = trade_data3[~trade_data3['Counterpart Country Code'].isin(aggs)]
    aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
    trade_data3 = trade_data3[~trade_data3['Country Code'].isin(aggs)]

    # exports
    trade_data3 = trade_data3[trade_data3['Indicator Name'] == 'Goods, Value of Exports, Free on board (FOB), US Dollars']

    # create index
    trade_data3['exporter_importer'] = trade_data3['iso3_code_exporter'].astype(str) + "_" + trade_data3['iso3_code_importer'].astype(str)

    # float needed (not sure why this happens)
    trade_data4 = trade_data3.iloc[:, np.r_[7:83]]
    trade_data4 = trade_data4.iloc[:, np.r_[0:76]].astype(float)

    # very helpful to reshape the dataframe
    long_trade = trade_data4.stack().to_frame()
  
    names = trade_data3['exporter_importer'].repeat(76)
  
    long_trade['exporter_to_importer'] = names.values
    long_trade.reset_index(inplace = True)
    long_trade.columns = ['blah', 'Year', 'ExportedValueFOB', 'Exporter_to_Importer']
    long_trade.drop(columns = ['blah'], inplace = True)
    long_trade['index'] = long_trade['Exporter_to_Importer'] + "_" + long_trade['Year'].astype(str)
    long_trade.set_index("index", inplace=True)
    
    long_trade.to_csv("data\ExportersFOB.csv")

    return long_trade

# exp100 = exportsallcombinations()
# print(exp100)

################
# Exports seperately
################

def importsallcombinations():
    
    trade_data1 = pd.read_csv(r"data\DOT_06-02-2024 11-13-24-61_timeSeries.csv")
    
    ######
    # merge iso3
    ######
    iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
    trade_data2 = trade_data1.merge(iso1, left_on="Country Code", right_on="imf_code", how = "left")
    trade_data2.rename(columns={"iso3_code": "iso3_code_exporter"}, inplace = True)
    iso1 = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")
    trade_data3 = trade_data2.merge(iso1, left_on="Counterpart Country Code", right_on="imf_code", how = "left")

    trade_data3.rename(columns={"iso3_code": "iso3_code_importer"}, inplace = True)
    trade_data3.drop(columns=['Unnamed: 0_x', 'imf_code_x','Unnamed: 0_y', 'imf_code_y'], inplace=True)

    # Keep this, it helps with stacking below
    trade_data3.fillna(0, inplace=True)

    # necessary to remove 'e's from data, so already beginning to subsetting
    trade_data3 = trade_data3[trade_data3['Attribute'] == 'Value'] 

    # remove: dont want aggregates and 'lost'countries
    aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
    trade_data3 = trade_data3[~trade_data3['Counterpart Country Code'].isin(aggs)]
    aggs = [1, 80, 92, 110, 126,163, 188, 200, 205, 399, 400, 405, 459, 473, 489, 505, 598, 603, 799, 934, 965, 974,605, 884, 898, 899, 901, 903, 910, 938, 998]
    trade_data3 = trade_data3[~trade_data3['Country Code'].isin(aggs)]

    # exports
    trade_data3 = trade_data3[trade_data3['Indicator Name'] == 'Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars']

    # create index (THIS IS CORRECT but confusing)
    trade_data3['importer_exporter'] = trade_data3['iso3_code_exporter'].astype(str) + "_" + trade_data3['iso3_code_importer'].astype(str)

    # float needed (not sure why this happens)
    trade_data4 = trade_data3.iloc[:, np.r_[7:83]]
    trade_data4 = trade_data4.iloc[:, np.r_[0:76]].astype(float)

    # very helpful to reshape the dataframe
    long_trade = trade_data4.stack().to_frame()
  
    names = trade_data3['importer_exporter'].repeat(76)
  
    long_trade['importer_exporter'] = names.values
    long_trade.reset_index(inplace = True)
    long_trade.columns = ['blah', 'Year', 'ImporterValueCIF', 'Importer_from_Exporter']
    
    long_trade.drop(columns = ['blah'], inplace = True)
    long_trade['index'] = long_trade['Importer_from_Exporter'] + "_" + long_trade['Year'].astype(str)
    long_trade.set_index("index", inplace=True)
    long_trade.to_csv("data\ImporterCIF.csv")

    return long_trade


def totaltrade():
    exp100 = exportsallcombinations()
    imp100 = importsallcombinations()

    totalTradedata = pd.merge(exp100, imp100, left_index=True, right_index=True)
    totalTradedata.rename(columns={"Year_x": "Year"}, inplace=True)
    totalTradedata.drop(columns=['Year_y'], inplace=True)
    
    totalTradedata['total_trade'] = totalTradedata['ExportedValueFOB'] + totalTradedata['ImporterValueCIF']
    totalTradedata.to_csv(r"data\totalTradedata.csv")
totaltrade()


################
# select signficant traders
################

def significanttraders():
    dt1 = pd.read_csv("allStates_AllYears_Imports_CIF.csv")

    gettoptraders = dt1[dt1['Year'] == 2018]
    gettoptraders = gettoptraders[['Import', 'iso_o']]
    gettoptraders = gettoptraders.groupby(['iso_o']).sum()
    gettoptraders.columns = ["TopImporters"]
    gettoptraders = gettoptraders.sort_values(by = ['TopImporters'], ascending=False)[0:125]  ############# Number of countries
    topers = gettoptraders.index.tolist()
    dt1 = dt1[dt1['iso_o'].isin(topers)]
    dt1 = dt1[dt1['iso_d'].isin(topers)]

    return dt1

# #################
# # summary
# #################

def summarystats():

    dt1 = pd.read_csv("allStates_AllYears_Imports_CIF.csv") 

    print(dt1.shape)
    printme(dt1)
    print(dt1['iso_o'].nunique()) #199 countries
    print(dt1['iso_d'].nunique()) #200 countries
    print(dt1['continent'].nunique()) # 5 continents
    print(dt1['langoff_1'].nunique()) # 65 languages
    print(dt1['colonizer1'].nunique()) # 15

# ##################
# # trade share: (exports + imports)/gdp
# # https://ourworldindata.org/grapher/trade-as-share-of-gdp#:~:text=Sum%20of%20exports%20and%20imports,product%2C%20expressed%20as%20apercentage.
# ##################

# dt1 = pd.read_csv("allStates_AllYears_Imports_CIF.csv") 
# # dt1['trade_share'] = (dt1['Import'] + dt1['Export'])/dt1['rgdpe_importer'])

def fig1(dt1):
    allstates = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")['iso3_code'].tolist()
    #allstates = ['NLD']
    collect1 = []
    for i in allstates:
        print(i)
        # select country
        t1 = dt1[dt1['iso_o'] == i]
        t1.to_csv("tmp3.csv")

        # sum imports
        impts = dt1[dt1['iso_o'] == i][['Year', 'Import']]
        impts = impts.groupby('Year').sum()

        # sum exports
        exprts = dt1[dt1['iso_d'] == i][['Year', 'Export']]
        exprts = exprts.groupby('Year').sum()

        # for figure 1 in orginal paper, get gdp NLD as well
        gdp1 = dt1[dt1['iso_o'] == i][['Year', 'cgdpo_importer']]
        gdp1 = gdp1.drop_duplicates()
        gdp1.set_index('Year', inplace=True)

        pop1 = dt1[dt1['iso_o'] == i][['Year', 'pop_importer']]
        pop1 = pop1.drop_duplicates()
        pop1.set_index('Year', inplace=True)

        dfs = [impts, exprts, gdp1, pop1]
        data1 = reduce(lambda  left,right: pd.merge(left,right,left_index=True, right_index=True, how='outer'), dfs)
        data1['GDP_perCapita'] = data1['cgdpo_importer']/data1['pop_importer']
        data1['Trade_share_percent'] = ((data1['Import'] + data1['Export'])/(data1['cgdpo_importer'] * 1000000)) * 100
        
        data2 = data1.loc[:,['GDP_perCapita', 'Trade_share_percent']]
        data2['importer_iso'] = i 

        collect1.append(data2)

    out1 = pd.concat(collect1)    
    
    return out1

# figure1 = fig1(dt1)
# figure1.to_csv("figure1_imports.csv")

def figure1plot():
    fig1 = pd.read_csv("figure1_imports.csv")
    #fig1 = fig1[~fig1['importer_iso'].isin(['ARE', 'BRN', 'QAT', 'MAC'])]

    fig1 = fig1[fig1['Trade_share_percent'] >= 0]
    #fig1 = fig1[(fig1['Year'] >= 1961) & (fig1['Year'] <= 1992)]


    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    plt.scatter(fig1['Trade_share_percent'], np.log(fig1['GDP_perCapita']))
    plt.ylabel("GDP_perCapita")
    plt.xlabel("Trade_share_percent")
    plt.title("Figure 1 from paper, outliers dropped")

    #ax.set_yscale('log')
    plt.show()

#figure1plot()

#################
# figure 2
#################

def figure2plot():
    fig2 = pd.read_csv("figure1.csv")
    prct1 = fig2['GDP_perCapita'].pct_change()
    fig2['GDP_pp_percentage'] = prct1

    fig2 = fig2[~fig2['importer_iso'].isin(['ARE', 'BRN', 'QAT', 'MAC', 'SAU', 'VNM', 'LBR'])]
    fig2 = fig2[fig2['Trade_share_percent'] >= 0]
    #fig2 = fig2[(fig2['Year'] >= 1960) & (fig2['Year'] <= 1992)]
    fig2.to_csv("tmp_fig2.csv")

    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)

    plt.scatter(fig2['Trade_share_percent'], fig2['GDP_pp_percentage'] * 100)
    plt.ylabel("GDP_pp_percentage")
    plt.xlabel("Trade_share_percent")
    plt.title("Figure 2 from paper, outliers dropped")

    plt.show()

#figure2plot()

################
# new figure 3 (gdp per capita and trade share percent)
################

def plothist():

    fig3 = pd.read_csv("figure1.csv")
    fig3 = fig3[fig3['Year'] == 2018]

    n_bins = 20

    fig, axs = plt.subplots(1, 2, sharey=False, tight_layout=True)
    axs[0].hist(np.log(fig3['GDP_perCapita']), bins=n_bins)
    axs[1].hist(np.log(fig3['Trade_share_percent']), bins=n_bins)

    axs[0].title.set_text('GDP_perCapita 2018(logged)')
    axs[1].title.set_text('Trade_share_percent 2018 (logged)')


    plt.show()

#plothist()

################
# figures using all data
################

def exports_equal_imports():
    # So, do reported exports = reported imports?
    
    alldata = pd.read_csv("allStates_AllYears_Imports_CIF.csv")

    exports_perCountry = alldata[alldata['Year'] == 2018]
    exp1 = exports_perCountry[['Export', 'iso_d']]
    exp1 = exp1.groupby(['iso_d']).sum()
    exp1.sort_values(['Export'], ascending=False, inplace=True)
    print(exp1)

    imports_perCountry = alldata[alldata['Year'] == 2018]
    imp1 = exports_perCountry[['Import', 'iso_o']]
    imp1 = imp1.groupby(['iso_o']).sum()
    imp1.sort_values(['Import'], ascending=False, inplace=True)
    print(imp1)

    exp_imp = pd.merge(exp1, imp1, left_index=True, right_index=True)
    exp_imp['Exprt_min_Imprt'] = exp_imp['Export'] - exp_imp['Import']

    exp_imp.to_csv()

def topdutchthroughtime():
    alldata = pd.read_csv("allStates_AllYears_Imports_CIF.csv")
    # top dutch importers through time
    statimport = alldata[alldata['Year'] == 2018]
    statimport = statimport[statimport['iso_o'] == 'NLD']
    statimport = statimport[['iso_d', 'Export']].groupby('iso_d').sum()
    statimport.sort_values(['Export'], ascending=False, inplace=True)
    print(statimport)

def dutchexports():

    alldata = pd.read_csv("allStates_AllYears_Export_FOB.csv")

    ############################
    # this is Dutch exports
    ############################
    # check: https://data.imf.org/regular.aspx?key=61013712

    st1 = alldata[['Year', 'iso_d', 'iso_o', 'Export', 'Import']]
    #exporting country, NLD (orginating/destination)
    st1 = st1[st1['iso_o'] == 'NLD']

    st1 = st1[['Year', 'iso_d', 'Import']].groupby(['Year', 'iso_d']).sum()
    st1 = st1.pivot_table(index = ['iso_d'], columns = 'Year', values = 'Import')
    st1.sort_values([2023], ascending=False,inplace=True)
    print(st1)

    _, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    data1 = st1.iloc[0:10,:].T
    axs= np.log(data1).plot(linewidth=2, fontsize=8);
    axs.title.set_text('Dutch Exports FOB (logged)');
    plt.show()

# dutchexports()

def getallExports():
    alldata = pd.read_csv("allStates_AllYears_Export_FOB.csv")

    ############################
    # this is Dutch exports
    ############################
    # check: https://data.imf.org/regular.aspx?key=61013712

    st1 = alldata[['Year', 'iso_d', 'iso_o', 'Export', 'Import']]
    #exporting country, NLD (orginating/destination)

    allstates = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")['iso3_code'].tolist()
    #allstates = ['NLD', 'DEU']
    collect1 = []
    for i in allstates:
        st2 = st1[st1['iso_o'] == i]

        st2 = st2[['Year', 'iso_d', 'Import']].groupby(['Year', 'iso_d']).sum()
        st2['ExportingCountry'] = i
        collect1.append(st2)

    return collect1

# allexp = getallExports()
# allexp = pd.concat(allexp)
# allexp.to_csv("all_Exp.csv")

def dutchimports():
    ############################
    # this is Dutch imports
    ############################
    # check: https://tradingeconomics.com/netherlands/exports-by-country
    # check: https://data.imf.org/regular.aspx?key=61013712

    alldata = pd.read_csv("allStates_AllYears_Imports_CIF.csv")

    st1 = alldata[['Year', 'iso_d', 'iso_o', 'Import', 'Export']]
    
    # importing country, NLD (orginating/destination)
    st1 = st1[st1['iso_d'] == 'NLD']
    # who are the exporters to NLD
    st1 = st1[['Year', 'iso_o', 'Export']].groupby(['Year', 'iso_o']).sum()
    st1 = st1.pivot_table(index = ['iso_o'], columns = 'Year', values = 'Export')
    st1.sort_values([2023], ascending=False,inplace=True)
    print(st1)

    _, axs = plt.subplots(1, 1, sharey=True, tight_layout=True)
    data1 = st1.iloc[0:10,:].T
    axs= np.log(data1).plot(linewidth=2, fontsize=8);
    axs.title.set_text('Dutch Imports CIF (logged)');
    
    plt.show();

#dutchimports()

def getallImports():
    alldata = pd.read_csv("allStates_AllYears_Export_FOB.csv")

    ############################
    # this is Dutch exports
    ############################
    # check: https://data.imf.org/regular.aspx?key=61013712

    st1 = alldata[['Year', 'iso_d', 'iso_o', 'Export', 'Import']]
  
    allstates = pd.read_csv(r"data\pdf_extractor\imf_iso3codes_usethese.csv")['iso3_code'].tolist()
    #allstates = ['NLD']
    collect1 = []
    for i in allstates:
        st2 = st1[st1['iso_d'] == i]
        st2 = st2[['Year', 'iso_o', 'Export']].groupby(['Year', 'iso_o']).sum()
        st2['ImportingCountry'] = i
        collect1.append(st2)

    return collect1

# allimp = getallImports()
# allimp = pd.concat(allimp)
# allimp.to_csv("all_Imp.csv")

# x = pd.read_csv("all_Imp.csv")
# x = x[x['ImportingCountry'] == 'NLD']
# x.to_csv("tmpx.csv")

def instrument_tau():
    
    exports1 = pd.read_csv("allExp.csv")
    exports1['key1'] = exports1['ExportingCountry'] + "_" + exports1['Year'].astype(str) + "_" +  exports1['iso_d']
    exports1.drop(columns = ["Year", "iso_d", "ExportingCountry"], inplace=True)

    imports1 = pd.read_csv("allImp.csv")
    imports1['key1'] = imports1['ImportingCountry'] + "_" + imports1['Year'].astype(str) + "_" +  imports1['iso_o']
    imports1.drop(columns = ["Year", "iso_o", "ImportingCountry"], inplace=True)

    tau1 = pd.merge(exports1, imports1, left_on="key1", right_on="key1")

    tau1['total_trade_new'] = tau1['Import'] + tau1['Export']

    return tau1

# new_tau = instrument_tau()

def combine_tau(new_tau):

    maindata = pd.read_csv("allStates_AllYears_Imports_CIF.csv")
    maindata = pd.merge(maindata, new_tau, left_on="key1", right_on="key1", how="left")
    maindata.drop(columns=['key1'], inplace=True)
    maindata['instrument'] = (maindata['total_trade_new']/maindata['gdpgdp_nominal'])*100

    maindata.to_csv("data/maindata_forRegressions.csv")
    return maindata

# maindata = combine_tau(new_tau)
# print(maindata['instrument'])