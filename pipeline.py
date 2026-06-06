import pandas as pd
import numpy as np
import re
from sqlalchemy import create_engine

cofdf = pd.read_csv('/Users/akshay/Downloads/psd_coffee.csv')
popdf= pd.read_csv('/Users/akshay/Downloads/pop.csv',skiprows = 4)
codedf = pd.read_csv('/Users/akshay/Downloads/countries-codes.csv',sep=';')


cofdf.rename(columns = lambda x:x.lower()).assign(country_name =  lambda x: x['country_name'].str.strip().str.lower()).loc[:,['country_name']].drop_duplicates().\
merge(codedf.rename(columns = lambda x:x.lower()).assign(label_en =  lambda x: x['label en'].str.strip().str.lower()).loc[:,['label_en']].drop_duplicates(),left_on = 'country_name', right_on = 'label_en',how='left').\
loc[lambda x:x['label_en'].isnull()]

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

cofdfnew = cofdf.rename(columns = lambda x:x.lower()).assign(cont = lambda x:x['country_name'].str.strip().str.lower().replace(fix)).\
merge(codedf.rename(columns = lambda x:x.lower()).assign(label_en =  lambda x: x['label en'].str.strip().str.lower()).loc[:,['label_en','iso2 code','iso3 code']].drop_duplicates(subset = ['label_en']),left_on = 'cont', right_on = 'label_en',how='left').\
assign(label_en = lambda x: np.where(x['label_en'].isnull(),'european union',x['cont']),
      iso2code = lambda x: np.where(x['iso2 code'].isnull(),'EU',x['iso2 code']),
      iso3code = lambda x: np.where(x['iso3 code'].isnull(),'EUU',x['iso3 code']))


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


DATABASE_URL = "postgresql://postgres:[password]@db.ucvmqgtfrgthvmitmokq.supabase.co:5432/postgres"


engine = create_engine(DATABASE_URL)


q.to_sql('raw_coffee_market_data', engine, if_exists='replace', index=False)








# In[12]:


import os
print(os.getcwd())


# In[ ]:




