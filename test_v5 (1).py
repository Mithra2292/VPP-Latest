import time, numpy as np, pandas as pd, vpp_backend_v5 as B
g=B.load_series("/root/solar_2025_fixed.csv","ghi"); w=B.load_series("/root/wind_2025_fixed.csv","wind_speed"); l=B.load_series("/root/load_2025_fixed.csv","load_kw")
df,_=B.align_inputs(g,w,l); p=B.Params(g_cases=[(0.02,.25),(0.03,.5),(0.045,.25)],active=("PV","WT","SMR"))
ub=[3000,1000,1000,0,0,0]
for name,pool_years in (("real only",0),("synthetic 100y",100)):
    t=time.time()
    pool=B.synth_pool(df,p,pool_years,seed=1) if pool_years else None
    bank=B.build_bank(df,p,1500,500,pool=pool)
    wsum=bank.w_t.sum()+bank.w_s.sum()+(bank.w_w.sum()*bank.info_w["days"] if bank.w_w is not None else 0)
    print(name,"| build s",round(time.time()-t,2),"| weights",round(wsum,2),"| Y",bank.Y,"| scen:",bank.scen_source)
    print(bank.info_s[["date","residual_load_score_kWh","weight_days_per_year"]].round(3).to_string(index=False))
    print("window",bank.info_w)
    ctx=B.Ctx(bank,p); res=B.run_nsga2(ctx,[0]*6,ub,30,25,0); i,ok=B.select_recommended(res)
    print(" rec",np.round(res["X"][i]),ok,round(-res["F"][i,0]/1e7,3),"cr | verify",round(B.verify_design(res["X"][i],ctx)["npv"]/1e7,3))
# does the synthetic mean match the data? 
pool=B.synth_pool(df,p,100,seed=1)
print("mean load real",df.load_kw.mean(),"syn",pool["L"].mean())
print("mean pv real",(df.ghi/1000*p.pr).mean(),"syn",pool["pv"].mean())
print("yr_pv spread",pool["yr_pv"].std()/pool["yr_pv"].mean())
# 3-year test: perturb to create inter-annual variability
d2=[]
for k,(yr,fs,fw,fl) in enumerate([(2023,0.90,0.85,0.97),(2024,1.04,1.10,1.00),(2025,1.0,1.0,1.0)]):
    x=df.copy(); x.index=x.index.map(lambda t: t.replace(year=yr)); x["ghi"]*=fs; x["wind_speed"]*=fw; x["load_kw"]*=fl; d2.append(x)
d3=pd.concat(d2); pool=B.synth_pool(d3,p,100,seed=2); bank=B.build_bank(d3,p,1500,500,pool=pool)
print("3yr:",bank.scen_source,"| yr_pv spread",round(pool["yr_pv"].std()/pool["yr_pv"].mean(),3),"| ver label",bank.ver["label"])
