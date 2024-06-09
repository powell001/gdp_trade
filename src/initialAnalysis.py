import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from myhelpers import printme, totalexportsperyear, totalimportsperyear
from linearmodels import PanelOLS

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
    regressiondata.to_csv("data/regressiondata.csv")

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

#loop_adf_gdppop()

###########################
# Estimated trade share
###########################

######################################################
# Panel Data
######################################################

# analysis run using MATLAB
# set up data for MATLAB
# https://bashtage.github.io/linearmodels/panel/examples/examples.html


#######
# Regression data
#######

data1 = pd.read_csv("data/regressiondata.csv")
data1['ImportingCountry'] = data1['key2'].astype(str).str[0:3]
data1['Year'] = data1['key2'].astype(str).str[-4:].astype(int)

###################################################################
# year data
data1 = data1[(data1['Year'] >= 1948) & (data1['Year'] <= 2019)]
###################################################################

data1.drop(columns=["Unnamed: 0", "key2", "key3"],inplace=True)
print(data1)
data1['area_importer'] = data1['area_importer'].astype(float)
printme(data1)

### select 10 countries
#countries = ["NLD","DEU","USA","KOR","JPN","CHN","CAN","FRA","ESP","GBR","ITA","POL","SWE","NOR","COL"]
countries = data1['ImportingCountry'].unique()
data1 = data1[data1['ImportingCountry'].isin(countries)]

#################
#data1['constant'] = 1
#################
data1[data1['instrument']==0] = np.nan
data1['instrument_log'] = np.where(~data1['instrument'].isnull(), np.log(data1['instrument']), data1['instrument'])
##################
data1['dist_log'] = np.log(data1['dist'])
##################
data1['pop_importer_log'] = np.log(data1['pop_importer'])
##################
data1['pop_exporter_log'] = np.log(data1['pop_exporter'])
##################
data1['area_importer_log'] = np.log(data1['area_importer'])
##################
data1['area_exporter_log'] = np.log(data1['area_exporter'])
##################
data1['landlocked'] = data1['landlocked_importer'] + data1['landlocked_exporter']

data1['dist_border_log'] = data1['dist_log'] * data1['border']
data1['pop_importer_border_log'] = data1['pop_importer_log'] * data1['border']
data1['pop_exporter_border_log'] = data1['pop_exporter_log'] * data1['border']
data1['area_importer_border_log'] = data1['area_importer_log'] * data1['border']
data1['area_exporter_border_log'] = data1['area_exporter_log'] * data1['border']

mi_data = data1.set_index(['ImportingCountry', 'Year'], drop = True)
#mi_data['Year'] = pd.Categorical(mi_data['Year'])


mi_data.corr().to_csv("corr.csv")

model_1948_2019 = PanelOLS(mi_data.instrument_log, mi_data[['dist_log','pop_importer_log','pop_exporter_log','area_importer_log','area_exporter_log',
                                                'landlocked','border', 'dist_border_log', 'pop_importer_border_log',
                                                'pop_exporter_border_log']], entity_effects=False, time_effects=True, drop_absorbed=True)
print(model_1948_2019.fit().summary)

plt.rc("figure", figsize=(12, 7))
plt.text(0.01, 0.05, model_1948_2019.fit(), {"fontsize": 10}, fontproperties="monospace")
plt.axis("off")
plt.tight_layout()
plt.gcf().tight_layout(pad=1.0)
plt.savefig("alldata_model.png", transparent=False)



######
# Estimated Effects
######
def estimatedEntityEffects():
    estEffect = model_1948_2019.fit().estimated_effects
    estEffect.to_csv("data\estEffect.csv")

    estEffect = pd.read_csv("data\estEffect.csv", index_col=[0])
    estEffect['ISO3'] = estEffect.index
    estEffect.drop_duplicates(keep='first', inplace=True)
    state1 = estEffect[estEffect['Year'] == 2019]
    state1.drop_duplicates(subset=['ISO3'] , keep='first', inplace=True, ignore_index=True)
    state1.drop(columns=['Year'], inplace=True)
    state1.sort_values('estimated_effects', ascending=False, inplace=True)
    print(state1)

    top25 = state1.iloc[0:24,:]
    bottom25 = state1.iloc[-24:,:]

    fig, (ax1, ax2) = plt.subplots(nrows=2,ncols=1, sharex=False, squeeze=True,  layout='constrained')
    top25.plot.bar(x="ISO3", y="estimated_effects", grid=True, ax=ax1)
    ax1.set_title("Top 25")
    bottom25.plot.bar(x="ISO3", y="estimated_effects", grid=True, ax=ax2)
    ax2.set_title("Bottom 25")

    plt.savefig("EntityEffects.png")
#estimatedEntityEffects()

def estimatedTimeEffects():

    estEffect = model_1948_2019.fit().estimated_effects
    print(estEffect)
    estEffect.to_csv("data\estEffect.csv")
    estEffect = pd.read_csv("data\estEffect.csv", index_col=[0])
    timeEffect = estEffect[['Year', 'estimated_effects']]
    timeEffect.drop_duplicates(subset=['Year'], inplace=True)
    timeEffect.sort_values(["Year"], ascending=True, inplace=True)
    timeEffect.set_index("Year", inplace=True)
    timeEffect.plot(title="Time Effects")
    plt.savefig("TimeEffects.png")
estimatedTimeEffects()

def modelsforComparison():

    #######
    # Regression data
    #######

    data1 = pd.read_csv("data/regressiondata.csv")
    data1['ImportingCountry'] = data1['key2'].astype(str).str[0:3]
    data1['Year'] = data1['key2'].astype(str).str[-4:].astype(int)

    ###################################################################
    # year data
    data1 = data1[(data1['Year'] >= 1960) & (data1['Year'] <= 1992)]
    ###################################################################

    data1.drop(columns=["Unnamed: 0", "key2", "key3"],inplace=True)
    print(data1)
    data1['area_importer'] = data1['area_importer'].astype(float)
    printme(data1)

    ### select 10 countries
    #countries = ["NLD","DEU","USA","KOR","JPN","CHN","CAN","FRA","ESP","GBR","ITA","POL","SWE","NOR","COL"]
    countries = data1['ImportingCountry'].unique()
    data1 = data1[data1['ImportingCountry'].isin(countries)]

    #################
    #data1['constant'] = 1
    #################
    data1[data1['instrument']==0] = np.nan
    data1['instrument_log'] = np.where(~data1['instrument'].isnull(), np.log(data1['instrument']), data1['instrument'])
    ##################
    data1['dist_log'] = np.log(data1['dist'])
    ##################
    data1['pop_importer_log'] = np.log(data1['pop_importer'])
    ##################
    data1['pop_exporter_log'] = np.log(data1['pop_exporter'])
    ##################
    data1['area_importer_log'] = np.log(data1['area_importer'])
    ##################
    data1['area_exporter_log'] = np.log(data1['area_exporter'])
    ##################
    data1['landlocked'] = data1['landlocked_importer'] + data1['landlocked_exporter']

    data1['dist_border_log'] = data1['dist_log'] * data1['border']
    data1['pop_importer_border_log'] = data1['pop_importer_log'] * data1['border']
    data1['pop_exporter_border_log'] = data1['pop_exporter_log'] * data1['border']
    data1['area_importer_border_log'] = data1['area_importer_log'] * data1['border']
    data1['area_exporter_border_log'] = data1['area_exporter_log'] * data1['border']

    mi_data = data1.set_index(['ImportingCountry', 'Year'], drop = True)
    #mi_data['Year'] = pd.Categorical(mi_data['Year'])


    mi_data.corr().to_csv("corr.csv")

    model_1960_1992 = PanelOLS(mi_data.instrument_log, mi_data[['dist_log','pop_importer_log','pop_exporter_log','area_importer_log','area_exporter_log',
                                                    'landlocked','border', 'dist_border_log', 'pop_importer_border_log',
                                                    'pop_exporter_border_log']], entity_effects=True, drop_absorbed=True)
    print(model_1960_1992.fit().summary)



    #######
    # Regression data
    #######

    data1 = pd.read_csv("data/regressiondata.csv")
    data1['ImportingCountry'] = data1['key2'].astype(str).str[0:3]
    data1['Year'] = data1['key2'].astype(str).str[-4:].astype(int)

    ###################################################################
    # year data
    data1 = data1[(data1['Year'] >= 1948) & (data1['Year'] <= 2019)]
    ###################################################################

    data1.drop(columns=["Unnamed: 0", "key2", "key3"],inplace=True)
    print(data1)
    data1['area_importer'] = data1['area_importer'].astype(float)
    printme(data1)

    ### select 10 countries
    countries = ["NLD","DEU","USA","KOR","JPN","CHN","CAN","FRA","ESP","GBR","ITA","POL","SWE","NOR","COL","IND","ARG","ZAF","IRL", "PAK"]
    #countries = data1['ImportingCountry'].unique()
    data1 = data1[data1['ImportingCountry'].isin(countries)]

    #################
    #data1['constant'] = 1
    #################
    data1[data1['instrument']==0] = np.nan
    data1['instrument_log'] = np.where(~data1['instrument'].isnull(), np.log(data1['instrument']), data1['instrument'])
    ##################
    data1['dist_log'] = np.log(data1['dist'])
    ##################
    data1['pop_importer_log'] = np.log(data1['pop_importer'])
    ##################
    data1['pop_exporter_log'] = np.log(data1['pop_exporter'])
    ##################
    data1['area_importer_log'] = np.log(data1['area_importer'])
    ##################
    data1['area_exporter_log'] = np.log(data1['area_exporter'])
    ##################
    data1['landlocked'] = data1['landlocked_importer'] + data1['landlocked_exporter']

    data1['dist_border_log'] = data1['dist_log'] * data1['border']
    data1['pop_importer_border_log'] = data1['pop_importer_log'] * data1['border']
    data1['pop_exporter_border_log'] = data1['pop_exporter_log'] * data1['border']
    data1['area_importer_border_log'] = data1['area_importer_log'] * data1['border']
    data1['area_exporter_border_log'] = data1['area_exporter_log'] * data1['border']

    mi_data = data1.set_index(['ImportingCountry', 'Year'], drop = True)
    #mi_data['Year'] = pd.Categorical(mi_data['Year'])

    mi_data['constant'] = 1

    mi_data.corr().to_csv("corr.csv")

    model_largeStates = PanelOLS(mi_data.instrument_log, mi_data[['constant',  'dist_log','pop_importer_log','pop_exporter_log','area_importer_log','area_exporter_log',
                                                    'landlocked','border', 'dist_border_log', 'pop_importer_border_log',
                                                    'pop_exporter_border_log']], entity_effects=True, drop_absorbed=True)
    print(model_largeStates.fit().summary)


    from linearmodels.panel import compare
    xx = compare({"OriginalFE": model_1960_1992.fit(), "AllData": model_1948_2019.fit(), "LargeStates": model_largeStates.fit()}).summary.as_csv


    plt.rc("figure", figsize=(12, 7))
    plt.text(0.01, 0.05, xx, {"fontsize": 10}, fontproperties="monospace")
    plt.axis("off")
    plt.tight_layout()
    plt.gcf().tight_layout(pad=1.0)
    plt.savefig("iv_model.png", transparent=False)
