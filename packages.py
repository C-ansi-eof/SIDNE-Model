import numpy as np
import pandas as pd
import numpy_financial as npf

def annualized(value,r,lifetime):
    '''
    This function returns annualized investment costs for a given overnight cost
    Structure annualized(value,r,lifetime) where
    value = overnight cost of a technology normally in USD/kWe
    r = discount rate between 0 and 1. For example a discount rates of 7% is 0.07
    lifetime = life to the technology in years
    
    '''
    AF=(1-(1+r)**(-lifetime))/r

    value=value/AF

    return value

def LCOE(tech, data, name_file):

     #Dictionary for cashflows
    res={"investment":[], "FOM":[], "VOM":[], "fuel":[], "carbon_cost":[], "tax":[], "generation":[]}

     #Dictionary for sum of annual cashflows
    res_sum={"technology":[tech], "investment":[], "FOM":[], "VOM":[], "fuel":[], "carbon_cost":[],
             "tax":[]}

     #Compute annual generation
    gen=data.loc[tech].capacity*365.*24.*data.loc[tech].load_factor

     #Compute cashflows
     #past=np.array(past)
     #future=np.array(future)

    res["investment"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[-int(data.loc[tech].construction_time)+i for i in range(int(data.loc[tech].construction_time))],
          pmt=0,
          fv=[data.loc[tech].investment*data.loc[tech].capacity*1000./int(data.loc[tech].construction_time)
              for i in range(int(data.loc[tech].construction_time))])

    res["FOM"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[i+1 for i in range(int(data.loc[tech].lifetime))],
          pmt=0,
          fv=[data.loc[tech].FOM*data.loc[tech].capacity*1000. for i in range(int(data.loc[tech].lifetime))])

    res["VOM"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[i+1 for i in range(int(data.loc[tech].lifetime))],
          pmt=0,
          fv=[data.loc[tech].VOM*gen for i in range(int(data.loc[tech].lifetime))])

    res["fuel"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[i+1 for i in range(int(data.loc[tech].lifetime))],
          pmt=0,
          fv=[data.loc[tech].fuel*gen for i in range(int(data.loc[tech].lifetime))])

    res["carbon_cost"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[i+1 for i in range(int(data.loc[tech].lifetime))],
          pmt=0,
          fv=[data.loc[tech].carbon_cost*data.loc[tech].carbon_intensity*gen # already done (gCO2/kWh = t/MWh * 1e-3)
              for i in range(int(data.loc[tech].lifetime))])

    res["tax"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[i+1 for i in range(int(data.loc[tech].lifetime))],
          pmt=0,
          fv=[data.loc[tech].tax*gen for i in range(int(data.loc[tech].lifetime))])

    res["generation"]=(-1)*npf.pv(
          rate=data.loc[tech].rate,
          nper=[i+1 for i in range(int(data.loc[tech].lifetime))],
          pmt=0,
          fv=[gen for i in range(int(data.loc[tech].lifetime))])

     #Compute LCOE components
    for val in res.keys():
        if val!="generation":
            res_sum[val]=res[val].sum()/res["generation"].sum()

    df = pd.DataFrame(res_sum)
    df = df.set_index(df.columns[0])
    df.to_csv(name_file+".csv")
    #print(df)

    return df
     

def get_cost_data(techs, data, r):
    '''
    This functions takes cost data in the format of the Cost_PyPSA file are returns a dataframe
    that allows for more concise cost modelling in PyPSA
    Structure get_cost_data(techs, data, r) where
    techs is the list of technologies with the same name than in Cost_PyPSA file
    data is the Cost_PyPSA dataframe
    r is the discount as a fraction
    '''
    #Definning a python dictionnary to be filled up iteratively     
    Dict={"technology": techs, "investment":[], "FOM":[], "VOM":[], 
    "fuel":[], "efficiency":[], "lifetime":[]}
    attributes=list(Dict.keys())
    attributes.pop(0)

    #Filling the dictionnary
    for tech in techs:
        for attr in attributes:
            try:
                Dict[attr].append(float(data.loc[data['technology'] ==tech]
                .loc[data['parameter'] ==attr].value))
            except TypeError:
                Dict[attr].append(0.)
    
    #Create DataFrame
    df=pd.DataFrame(Dict,index=Dict["technology"])

    #Add some columns
    lifetime= df["lifetime"].values
    annualized_inv=[annualized(val, r, lifetime[i])*1000 for i, val 
    in enumerate(df["investment"].values)]
    df["annualized_investment"]=annualized_inv
    return df   
