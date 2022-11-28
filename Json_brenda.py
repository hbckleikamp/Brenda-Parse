#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 28 15:35:48 2022

@author: hugokleikamp
"""


#%%  modules
import json
import pandas as pd


#%% files

#put your path here
json_file="/Users/hugokleikamp/Downloads/brenda_2022_2.json"
text_file="/Users/hugokleikamp/Downloads/brenda_2022_2.txt"

#%%
with open(json_file, "r") as f:
    j=json.load(f)
    

data=j.get("data")




# #%%
combineds=[]
for ix,item in enumerate(data.items()):
    print(str(ix/len(data)*100)+" % completed")
    i=item[1]

    id=i.get("id")
    name=i.get("name")
    
    
    #prganism
    if i.get("organisms"):
        organisms=pd.DataFrame([[k,v.get("value")] for k,v in i.get("organisms").items()],columns=["OX","OS"])
    else:
        organisms=pd.DataFrame([["",""]],columns=["OX","OS"])

    #reaction
    if i.get("reaction"):
        
        reactions=pd.DataFrame([[j.get("educts"),
                                 j.get("products"), 
                                 j.get("organisms")] for j in i.get("reaction")],columns=["educts","products","OX"])
        reactions=reactions.explode("OX").dropna()
        reactions["reaction"]=reactions.educts.str.join(" + ")+" -> "+reactions.products.str.join(" + ")
        reactions=reactions[["reaction","OX"]]
    else:
        reactions=pd.DataFrame([["",""]],columns=["reaction","OX"])
    
    #cofactor
    if i.get("cofactor"):
        cofactors=pd.DataFrame([[j.get("value"), 
                                 j.get("organisms")] for j in i.get("cofactor")],columns=["cofactor","OX"])
        cofactors=cofactors.explode("OX")
    else:
        cofactors=pd.DataFrame([["",""]],columns=["cofactor","OX"])
    
    combined=reactions.merge(organisms,on="OX").merge(cofactors,on="OX")
    combined["name"]=name
    combined["id"]=id
    combineds.append(combined)
    

    
json_df=pd.concat(combineds)

#%% add typing from text file

with open(text_file,"r") as f:
    lines=f.readlines()
    
IDs=""
RTs=[]
counter=0
parsed=[]
for ix,line in enumerate(lines):
    
    if line.startswith("ID\t"):
        
        #store
        parsed.append([IDs, # ECnumber
                       "; ".join(RTs)]) # Reaction type

        #reset
        IDs=line.split("\t")[1].split("\n")[0]
        RTs=[]
        counter+=1
        print(counter)
  
    if line.startswith("RT\t"):
        RTs.append(" ".join(line.split("\t")[1:]).replace("\n",""))       

    
text_df=pd.DataFrame(parsed,
                       columns=["id","Type"])


final=json_df.merge(text_df)
final.to_csv("parsed_brenda.tsv",sep="\t")


