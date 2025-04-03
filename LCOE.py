import numpy as np
import numpy_financial as npf
import pandas as pd

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
          fv=[data.loc[tech].carbon_cost*data.loc[tech].carbon_intensity*1e-3*gen #gCO2/kWh = t/MWh * 1e-3
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