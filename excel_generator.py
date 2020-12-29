#!/usr/bin/env python
# coding: utf-8

# In[69]:


import json
import pandas as pd
import pickle
import numpy as np
from pillarplus import math

# In[3]:


# identification = json.load(open('./sample3.json','rb'))


# In[16]:


# room_information = pickle.load(open('./new_rooms_information.pkl','rb'))


# In[6]:


def sheet_writer(list_entity):
    """
    extractis length width height for list of entities
    """
    df_n = pd.DataFrame()
    i=0
    for e in list_entity:
        name = e[0]['type']
        df_n.loc[i,'EntityName']=name
        i+=1
        for w in e:
            df_n.loc[i,'EntityName']=f"{name} {w['display_name']}"
            df_n.loc[i,'Length']=w['length']
            df_n.loc[i,'Width']=w['breadth']
            df_n.loc[i,'Height']=w['height']
            i+=1
    return df_n        


# In[7]:


def get_counts(entity:list)->dict:
    d={}
    for w in entity:
        tmp = w['length'],w['breadth'],w['height']
        if tmp in d:
            d[tmp]=d[tmp]+1
        else:
            d[tmp]=1
    return d        


# In[9]:


def get_doors_and_windows(entities:list):
    df = pd.DataFrame(columns=['Entity','No.','Length','Width','Height'])
    i=0
    for e in entities:
        freq=get_counts(e)
        name = e[0]['type']
        df.loc[i,'Entity']=name
        i=i+1
        for k in freq.keys():
            df.loc[i,'No.']=freq[k]
            df.loc[i,'Length']=k[0]
            df.loc[i,'Width']=k[1]
            df.loc[i,'Height']=k[2]
            i=i+1
    return df


# ### Sheet 2

# In[12]:


import networkx as nx
import pickle
from pillarplus import math


# In[13]:
def on_and_between(pt1,pt2,pt3):
    try:
        
        x1, x2, x3 = pt1[0], pt2[0], pt3[0]
        #defining each coordinate for points
        y1, y2, y3 = pt1[1], pt2[1], pt3[1]
        if x1!=x2:
            slope = (y2 - y1) / (x2 - x1)
            #calculating slope of first two points
            pt3_on = (y3 - y1) == slope * (x3 - x1)
            #checking conditions for `pt3` to be on line
            pt3_between = (min(x1, x2) <= x3 <= max(x1, x2)) and  (min(y1, y2) <= y3 <= max(y1, y2))
            on_and_between_out = pt3_on and pt3_between
        else:
            on_and_between_out= True if x2==x1 and (min(y1, y2) <= y3 <= max(y1, y2)) else False    
    except ZeroDivisionError:
        pass
        # on_and_between= True if x2==x1 and (min(y1, y2) <= y3 <= max(y1, y2)) else False
    return on_and_between_out

# def entity_on_wall(edge,entity):
#     return on_and_between(edge[0],edge[1],entity[0]) and on_and_between(edge[0],edge[1],entity[1])
#%%
def entity_on_wall(edge,entity):
    # print(entity,edge)
    return math.is_between(entity[0],edge[0],edge[1]) and math.is_between(entity[1],edge[0],edge[1])
#%%
def create_edge_from_ordered(list_w):
    walls=[]
    for i in range(len(list_w)-1):
        walls.append((list_w[i],list_w[i+1]))
    return walls
#%%
def room_info_ext(room_information):    
    df_inside_area = pd.DataFrame()
    i=0
    for rinfo in room_information:
        df_inside_area.loc[i,'Room']=rinfo['room']['room_name']
        g = rinfo['graph_component']
        walls = create_edge_from_ordered(rinfo['ordered_points'])
        i=i+1
        wall_name = ord('A')
        for w in walls:
            df_inside_area.loc[i,'Room']=f'InnerWall {chr(wall_name)}'
            df_inside_area.loc[i,'Length']=math.find_distance(w[0],w[1])
            df_inside_area.loc[i,'Height']=None
            df_inside_area.loc[i,'Area']=None
            wall_name=wall_name+1
            i+=1
            # for p1,p2 in nx.dfs_edges(g):
            for p1,p2,data in g.edges(data=True):
                # data = g.get_edge_data(p1,p2)
                if not 'entity' in data.keys():
                    continue
                
                # print(data)   
                #  and entity_on_wall(w,(p1,p2))    
                if 'entity' in data.keys() and entity_on_wall(w,(p1,p2)):
                    # print('hellos')
                    name=f'(-) {data["entity"]["type"]} {data["entity"]["display_name"]}'
                    df_inside_area.loc[i,'Room']=name
                    df_inside_area.loc[i,'Length']=data['entity']['length']
                    df_inside_area.loc[i,'Height']=None
                    i=i+1    
    return df_inside_area         

#%%


#%%

# In[17]:


# In[18]:

# In[19]:


def get_room_area(room_info):
    df = pd.DataFrame(columns=['Room No.','Area'])
    for i,room in enumerate(room_info):
        df.loc[i,'Room No.']=room['room']['room_name']
        df.loc[i,'Area']=room['area']
    return df    


# In[20]:


def generator_function(identification:dict,room_information:dict):
    windows = list(filter(lambda entity: entity['type']=='window' and entity['category'] == 'p', identification['entities']))
    doors = list(filter(lambda entity: entity['type']=='door' and entity['category'] == 'p', identification['entities']))
    df_door_window = sheet_writer([doors,windows])
    df_door_window_unique= get_doors_and_windows([doors,windows])
    df_room_info_ext = room_info_ext(room_information)
    df_room_area = get_room_area(room_information)
    return df_door_window,df_door_window_unique,df_room_info_ext,df_room_area


# In[21]:


# a,b,c,d = generator_function(identification,room_information)


# writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')


# In[338]:


# a.to_excel(writer,'doors&window',index=False)
# b.to_excel(writer,'doors_window_consolidated',index=False)
# c.to_excel(writer,'wall_info',index=False)
# d.to_excel(writer,'room_area',index=False)
# writer.save()


# #### Check Data

# # In[48]:


# name = 'PP-Room 6'
# target=filter(lambda room: room['room']['room_name']==f'{name}' ,room_information)
# out=list(target)
# out_g = out[0]['graph_component']


# # In[54]:


# out


# # In[67]:


# gr = nx.Graph()
# gr.add_edges_from(out[0]['ordered_points'])
# edges = list(gr.edges())


# # In[70]:


# nodeList = list(set([(i,j) for i,j in np.array(edges).reshape(-1,2).tolist()]))


# # In[86]:


# connections=[]
# for i in range(len(edges)-1):
#     connections.append((edges[i],edges[i+1]))


# # In[94]:


# gnew = nx.Graph()
# for i,node in enumerate(nodeList):
#     gnew.add_node(i,cord=node)
# for a,b in connections:
# #     print(a,b)
#     gnew.add_edge(nodeList.index(tuple(a)),nodeList.index(tuple(b)))    


# # In[97]:


# gnew.edges(data=True)


# # In[100]:


# nx.draw(gnew,pos=nx.get_node_attributes(gnew,'cord'),with_labels=True)


# # In[74]:


# gnew.nodes(data=True)








# %%
