import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from myhelpers import printme, totalexportsperyear, totalimportsperyear

################
# Data for regressions
################

def selectdataRegression():
    ### Select then merge

    #main
    maindata1 = pd.read_csv("data/allStates_AllYears_Imports_CIF.csv")
    maindata1.rename(columns={'area': 'area_exporter', 'landlocked': 'landlocked_exporter', 'contig': 'border'}, inplace = True)
    maindata1['key2'] = maindata1['iso_o'].astype(str) + "_" + maindata1['iso_d'].astype(str) + "_" + maindata1['Year'].astype(str)
    data1 = maindata1.loc[:, ['key2', 'dist','pop_importer', 'pop_exporter', 'area_importer', 'area_exporter', 'landlocked_importer', 'landlocked_exporter', 'border']]

    #tau
    taudata1 = pd.read_csv("instrument101.csv")
    taudata1 = taudata1[['key3', 'instrument']]

    regressiondata = pd.merge(data1, taudata1, left_on="key2", right_on="key3")
    regressiondata.to_csv("regressiondata.csv")

#selectdataRegression()

################
# Agumented Dickey-Fuller
################

def allexp_imp_allcountries_years():

    maindata1 = pd.read_csv("data/allStates_AllYears_Imports_CIF.csv", usecols=['iso_o'])
    allcountries = list(set(maindata1['iso_o'].values.tolist()))

    allexports = []
    allimports = []  
    for i in allcountries:
        print(i)
        expt1 = totalexportsperyear(i)
        expt1['Year'] = expt1.index
        expt1['exporter'] = i
        expt1['key1'] = expt1['exporter'] + "_" + expt1['Year'].astype(str)
        expt1.drop(columns = ['Year', 'exporter'], inplace = True)
        allexports.append(expt1)
    pd.concat(allexports).to_csv("allexports_eachcountry.csv")

    for j in allcountries:
        print(j)
        imp1 = totalimportsperyear(j)
        imp1['Year'] = imp1.index
        imp1['importer'] = j
        imp1['key1'] = imp1['importer'] + "_" + imp1['Year'].astype(str)        
        imp1.drop(columns = ['Year', 'importer'], inplace = True)
        allimports.append(imp1)
    pd.concat(allimports).to_csv("allimports_eachcountry.csv")

#allexp_imp_allcountries_years()

def trade_share():
    #### Trade share
    # combine exports per year wiht imports per year
    exp1 = pd.read_csv("allexports_eachcountry.csv")
    imp1 = pd.read_csv("allimports_eachcountry.csv")

    tshare1 = pd.merge(exp1, imp1, left_on="key1", right_on="key1")
    tshare1 = tshare1[['key1', 'ExportedValueFOB', 'ImporterValueCIF']]

    maindata = pd.read_csv(r"data/allStates_AllYears_Imports_CIF.csv", usecols=['iso_o', 'Year', 'cgdpe_importer'])
    maindata['key1'] = maindata['iso_o'] + "_" + maindata['Year'].astype(str)
    maindata.drop(columns=['Year', 'iso_o'],inplace=True)
    maindata.drop_duplicates(inplace=True)

    data1 = pd.merge(tshare1, maindata, left_on="key1", right_on="key1", how="left")
    data1["trade_share"] = 100*((data1['ExportedValueFOB'] + data1['ImporterValueCIF'])/(data1['cgdpe_importer']*1000000))
    data1.to_csv("trade_share_data.csv")

    data1.dropna(inplace=True)
    data1 = data1[(data1['trade_share'] > 0) & (data1['trade_share'] < 100)]

    #print(data1)

    return data1

#trade_share()
import statsmodels.tsa.stattools as ts

############################
# unit test trade share
############################

rejectunitroot = []
def adf_trade_share(dataseries):

    ###########################
    result = ts.adfuller(dataseries['trade_share'].diff().dropna(), maxlag=1, regression="c") ######################
    ###########################
    return result

def loop_adf_test_trade_share():

    maindata1 = pd.read_csv("data/allStates_AllYears_Imports_CIF.csv", usecols=['iso_o'])
    allcountries = list(set(maindata1['iso_o'].values.tolist()))

    trd1 = trade_share()
    trd1 = trd1[['key1', 'trade_share']]

    print(trd1)
    ### Year for selection
    trd1['Year'] = trd1['key1'].str[-4:].astype(int)

    count_rejections = 0
    count_fail_rejections = 0
    for i in allcountries:
        print(i)

        # select country
        trd2 = trd1[trd1['key1'].str.startswith(i)]
    
        ########################
        # less than 1969 1992
        ########################
        trd2 = trd2[(trd2['Year'] >= 1969) & (trd2['Year'] <= 1992)]
        print(trd2[['key1', 'trade_share']])

        if trd2.empty:
            continue
        if trd2.shape[0] < 10:
            continue
        else:
            result = adf_trade_share(trd2)

        if result[1] <= 0.05:  #################################
            print("reject unit root, data does not have unit root: ",  result[1])
            count_rejections = count_rejections + 1
        else:
            print("fail to reject unit root, data has unit root: ", result[1])
            count_fail_rejections = count_fail_rejections + 1 

    print("Reject Unit Root: ", count_rejections)
    print("Fail to reject Unit Root: ", count_fail_rejections)

#loop_adf_test_trade_share()

###########################
# log real gdp per capita
###########################

rejectunitroot = []
def adf_gdppop_share(dataseries):

    ###########################
    result = ts.adfuller(dataseries['gdp_per_pop'].dropna(), maxlag=1, regression="ct") ##########################
    ###########################
    return result

def loop_adf_gdppop():

    maindata1 = pd.read_csv("data/allStates_AllYears_Imports_CIF.csv", usecols=['Year', 'iso_o', 'rgdpo_importer', 'pop_importer'])
    maindata1['key1'] = maindata1['iso_o'] + "_" + maindata1['Year'].astype(str)
    maindata1.drop_duplicates(subset=['key1'], keep='last', inplace=True)
    maindata1['gdp_per_pop'] = maindata1['rgdpo_importer']/maindata1['pop_importer']

    gdp_pop = maindata1.copy()
    gdp_pop.dropna(inplace=True)
    allcountries = list(set(gdp_pop['iso_o'].values.tolist()))

    print(gdp_pop)
    count_rejections = 0
    count_fail_rejections = 0

    for i in allcountries:
        print(i)

        # select country
        gdp_pop2 = gdp_pop[gdp_pop['iso_o'] == i]

        ########################
        # less than 1969 1992
        ########################
        #gdp_pop2 = gdp_pop2[(gdp_pop2['Year'] >= 1969) & (gdp_pop2['Year'] <= 1992)]
        print(gdp_pop2[['key1', 'gdp_per_pop']])

        if gdp_pop2.empty:
            continue
        if gdp_pop2.shape[0] < 10:
            continue
        else:
            result = adf_gdppop_share(gdp_pop2)

        if result[1] <= 0.05:####################################
            print("reject unit root, data does not have unit root: ",  result[1])
            count_rejections = count_rejections + 1
        else:
            print("fail to reject unit root, data has unit root: ", result[1])
            count_fail_rejections = count_fail_rejections + 1 

    print("Reject Unit Root: ", count_rejections)
    print("Fail to reject Unit Root: ", count_fail_rejections)

loop_adf_gdppop()

###########################
# Estimated trade share
###########################





# trade share
# def adf_tradeShare():
#     pass

# adf_tradeShare()

# trade share instrument



