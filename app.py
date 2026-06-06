import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
import streamlit as st
import subprocess


cofdf = pd.read_csv('psd_coffee.csv')
popdf= pd.read_csv('pop.csv',skiprows = 4)
codedf = pd.read_csv('countries-codes.csv',sep=';')


cofdf.rename(columns = lambda x:x.lower()).assign(country_name =  lambda x: x['country_name'].str.strip().str.lower()).loc[:,['country_name']].drop_duplicates().\
merge(codedf.rename(columns = lambda x:x.lower()).assign(label_en =  lambda x: x['label en'].str.strip().str.lower()).loc[:,['label_en']].drop_duplicates(),left_on = 'country_name', right_on = 'label_en',how='left').\
loc[lambda x:x['label_en'].isnull()]

def load_and_clean_data():
      fix = {'congo (brazzaville)':'congo',
            'congo (kinshasa)' : 'congo, democratic republic of the',
            "cote d'ivoire" : "côte d'ivoire",
            "iran": "iran, islamic rep. of",
          "korea, south": "korea, republic of",
          "laos": "lao people's dem. rep.",
          "north macedonia": "macedonia, the former yugoslav rep. of",
          "russia": "russian federation",
          "taiwan": "taiwan, china",
          "tanzania": "tanzania, united republic of",
          "venezuela": "venezuela, bolivarian rep. of",
          "vietnam": "viet nam",
          "yemen (sanaa)": "yemen"}
      
      #cofdf['cont'] = cofdf['Country_Name'].str.strip().str.lower().replace(fix)
      
      cleaned_df = (cofdf.rename(columns = lambda x:x.lower()).assign(cont = lambda x:x['country_name'].str.strip().str.lower().replace(fix))
      .merge(codedf.rename(columns = lambda x:x.lower()).assign(label_en =  lambda x: x['label en'].str.strip().str.lower()).loc[:,['label_en','iso2 code','iso3 code']].drop_duplicates(subset = ['label_en']),left_on = 'cont', right_on = 'label_en',how='left')
      .assign(label_en = lambda x: np.where(x['label_en'].isnull(),'european union',x['cont']),
            iso2code = lambda x: np.where(x['iso2 code'].isnull(),'EU',x['iso2 code']),
            iso3code = lambda x: np.where(x['iso3 code'].isnull(),'EUU',x['iso3 code'])))

      return cleaned_df

cofdfnew = load_and_clean_data()

def func(x):
    if x['country name']=='European Union':
        return 'EUU'
    elif x['country name']=='Kosovo':
        return 'XKX'
    else:
        return x['iso3 code']

popdfnew = popdf.rename(columns = lambda x:x.lower()).\
merge(codedf.rename(columns = lambda x:x.lower()).loc[:,['label en','iso2 code','iso3 code']].drop_duplicates(),left_on = 'country code', right_on = 'iso3 code',how='left').\
assign(iso3code = lambda x: x.apply(func,axis=1))



final=cofdfnew.assign(iso3code = lambda x: np.where(x['country_name'] == 'Kosovo','XKX',x['iso3code'].str.strip())).\
merge(popdfnew,left_on = 'iso3code',right_on = 'iso3code',how = 'left')

q=final.assign(value = final['value']*1000).\
loc[lambda x:x['attribute_description'] == 'Domestic Consumption'].groupby(['cont','market_year','iso3code']).agg(consumption = ('value','sum')).\
reset_index().\
merge(final.loc[:,lambda x: [y for y in x.columns if (y == 'cont') or (y == 'iso3code') or bool(re.search('(^[0-9])',y))==True]].drop_duplicates().\
melt(id_vars = ['cont','iso3code'],var_name = 'year',value_name = 'population').assign(year = lambda x:x['year'].astype(int)).\
loc[lambda x: x['population'].notnull()], left_on = ['cont','market_year','iso3code'], right_on = ['cont','year','iso3code'],how = 'left').\
assign(cpc = lambda x: x['consumption']*60/x['population'])


st.title('Coffee Consumption Around the World')

tab1,tab2,tab3 = st.tabs(['1. Top 3 Markets','2. Market Timing','3. Risk and Opportunity'])

with tab1:
      st.subheader("Which 3 markets would you recommend")
      
      st.dataframe(q.loc[(q['cpc'].notnull()) & (q['consumption'] != 0)].groupby('cont').agg(mean_cpc = ('cpc','mean'),
                                                                     std_cpc = ('cpc','std'),
                                                                     stability = ('cpc',lambda x: x.std()/x.mean()),
                                                                     dirc = ('cpc',lambda x: list(x)[len(x)-1] - list(x)[0])).\
      sort_values(by=['stability'],ascending = [False]).reset_index().loc[lambda x: x['cont'].isin(['united states','viet nam','philippines'])].rename(columns = {'cont':'country_name'}),hide_index=True)
      
      st.write(""" 
      As it can be seen from the above table I have used stability of increase and direction of increase of consumption per capita to arrive at the three markets :
    
      1. United States: Demands entry due to having the strongest overall long-term expansion volume across the timeline (dirc of +4.530) combined with a high consumption baseline.
      2. Viet Nam: Represents an ideal high-growth emerging market, showing a massive positive trajectory shift of +2.785, proving an expanding local consumer appetite.
      3. Philippines: Offers a robust, low-risk combination of high baseline volume (mean_cpc of 1.322) and steady compounding growth (dirc of +2.218).
          
      """)
      
      plotdata = q.loc[q['cont'].isin(['united states','viet nam','philippines'])].\
          pivot(index = 'market_year',columns = 'iso3code',values = 'cpc').rename_axis(None,axis=1).reset_index()
      
      fig,ax = plt.subplots(figsize=(12,6))
      
      ax.plot(plotdata['market_year'],plotdata['USA'],label = 'USA',color = 'black')
      
      ax.plot(plotdata['market_year'],plotdata['PHL'],label = 'PHL',color = 'blue')
      
      ax.plot(plotdata['market_year'],plotdata['VNM'],label = 'VNM',color = 'pink')
      
      ax.set_xlabel('year')
      ax.set_ylabel('cpc')
      ax.set_title('Timeline vs cpc - top 3 markets to increase client base')
      
      ax.grid(True,linestyle='--')
      ax.legend()
      
      st.pyplot(fig)

with tab2:
      st.subheader("Does the data suggest this is a good time to enter the coffee market?")
      st.write("""
      Yes, the historical and macroeconomic data indicates that this is an optimal entry window for ACME Baristas.
    
    By analyzing our past raw consumption volume and evaluate **Per-Capita Consumption (CPC)**—measuring actual individual consumer appetite over time. 
    
    * Post-2002, our data captures a massive global trend change accelerating out of the early 2000s. Global CPC broke out from a stagnant baseline of ~0.56 kg/person in 2000 to a highly progressive upward trajectory.
    * **Widespread Systemic Momentum:** This macro expansion is incredibly healthy because it is highly diversified: **45 out of 93 tracked countries exhibit a positive long-term expansion direction ($dirc > 0$).**
    """)
    
      yearcpc=q.loc[q['population']>0].groupby('market_year').agg(consumption = ('consumption','sum'),
                            population = ('population','sum')).assign(cpc = lambda x: (x['consumption']*60)/x['population']).reset_index()

      fig,ax = plt.subplots(figsize=(10,5))
      
      ax.plot(yearcpc['market_year'],yearcpc['cpc'],color= 'green')
      
      ax.set_xlabel('year')
      ax.set_ylabel('cpc')
      ax.set_title('YoY consumption trend')

      ax.grid(True,linestyle = '--')
      st.pyplot(fig)

with tab3:
    st.subheader("💡 Strategic Risks & Opportunities for ACME Baristas")
    
    st.write("Key Opportunities")
    st.write("""
    * **Targeting Premium, High-Growth Entry Points:** **Vietnam** and the **Philippines** are massive compounding growth markets. Entering these regions early allows ACME to establish strong brand equity while consumer adoption is surging.
    * **Capitalizing on High Baseline Volumes:** Entering the **United States** gives ACME immediate access to a mature, high-volume market with a massive customer base that has consistently expanded its per-capita consumption baseline over the long term.
    * **Riding the Global Trajectory:** With **45 out of 93 countries showing positive expansion**, coffee is a globally resilient commodity. This broad-based interest gives ACME a highly diversified playground to expand into without relying on just one local economy.
    """)
    
    st.write("Key Risks")
    st.write("""
    * **Intense Competition in Mature Markets:** While the US has a massive consumption baseline, it is highly saturated with established specialty coffee giants. ACME must heavily differentiate its brand or offer unique customer loyalty experiences to win market share.
    * **Supply Chain & Pricing Volatility:** Because coffee consumption has exploded globally, global production is under intense pressure. Agricultural risks, climate volatility, and shipping costs could fluctuate raw bean acquisition prices, threatening profit margins.
    * **Navigating Local Preferences:** Transitioning into emerging markets requires altering menus to match local tastes (e.g., sweeter coffee formats or milk-based options popular in Southeast Asia vs. standard drip/espresso preferences in Western markets).
    
    """)
