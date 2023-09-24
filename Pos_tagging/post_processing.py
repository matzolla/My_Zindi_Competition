import numpy as np 
import pandas as pd


luo_tagger={'ma':'ADP','e':'ADP','ni':'SCONJ','mar': 'ADP','gi':'ADP','en':'PRON','kendo':'SCONJ',
           'kaunti':'NOUN','ka':'SCONJ','owacho':'VERB','jo':'NOUN','bura':'NOUN','niya':'SCONJ','tich':'NOUN',
           'ji':'NOUN','sirkal':'NOUN','wach':'NOUN','kama':'SCONJ','pi':'NOUN','gavana':'NOUN','kot':'NOUN',
           'ahinya':'ADV','polise':'NOUN','-':'PUNCT','siaya':'PROPN','jatelo':'NOUN','nyithindo':'NOUN','(':'PUNCT',
           'polis':'NOUN','mi':'SCONJ','kane':'NOUN','adek':'PROPN','ja':'NOUN','omedo':'VERB','chik':'NOUN','komiti':'NOUN',
           'somo':'NOUN','otim':'VERB','jahigni':'NOUN','obedo':'VERB','jalup':'NOUN','nam':'NOUN','jatend':'NOUN','wachore':'VERB'} 



tsn_tagger={'ya': 'VERB','le':'ADP','e':'PRON','a':'DET','ka':'ADP','pele':'ADV','ke':'ADP','morago':'ADP','kgatlhanong':'ADP',
            'boitekanelo':'NOUN','komiti':'NOUN','neng':'AUX','ntse':'AUX','moporesidente':'NOUN','sesole':'NOUN','palamente':'NOUN',
            'lefapha':'NOUN','kgetse':'NOUN','nakwana':'ADV','-':'PUNCT','covid-19':'PROPN','bosetšhaba':'NOUN','porofense':'NOUN',
            'modulasetulo':'NOUN','tlase':'NOUN','moporesitente':'NOUN','setšhaba':'NOUN'}


csv_file = 'analysis.csv'
df = pd.read_csv(csv_file)

# Iterate through each row
for index, row in df.iterrows():
    if row['Language'] == 'luo':
        if row['Word'].lower() in set(luo_tagger.keys()):
            df.at[index, 'Pos'] = luo_tagger[row['Word'].lower()]
        else:
            df.at[index,'Pos']= row['luo']
    elif row['Language'] == 'tsn':
        if row['Word'].lower() in set(tsn_tagger.keys()):
            df.at[index,'Pos'] = tsn_tagger[row['Word'].lower()]
        else:
            df.at[index, 'Pos'] = row['setswana']
#df.to_csv('just_see.csv',index=False)
# Save the modified DataFrame back to a CSV file

df=df.drop(columns=['Language','setswana','luo','Word'],axis=0)
output_csv = 'post_processed.csv'
df.to_csv(output_csv, index=False)


