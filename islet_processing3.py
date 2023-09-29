# A new way to include fields from the geojson. In this case, I consider the distance to the border of the islet, using the contour of the nuclei
# by N.Verschueren nv13699@my.bristol.ac.uk last update 7/8/23
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog as fd
import json
from tkinter.filedialog import askdirectory
from scipy.spatial import distance_matrix
from scipy.spatial.distance import cdist
import os
# goal: include a new field in the annotations df with the distance to islet
# first we get the file with the annotations dataframe
print("Provide the cells file")
cells=fd.askopenfilename();

os.chdir(os.path.split(cells)[0])
cells=pd.read_csv(cells)

cells=cells.rename(columns={'Centroid X µm':'x','Centroid Y µm':'y'})


case=input("What is the name of this case?")
#new variables for the dataframe: case, distance to the border d2border, and distance to nones 
cells['case']=case;
cells['d2bordercm']=0;
cells['d2nonescm']=0;
dp=0.24999491876223942# micrometer_size.groovy, check in your qupath project
cells['d2bordernuc']=0;
cells['d2bordermem']=0;
cells['d2nonesnuc']=0;
cells['d2nonesmem']=0;

cells=cells[pd.to_numeric(cells['Parent'], errors='coerce').notnull()] # Making sure that we are only considering cells with a parent

list_islets=cells[['Image','Parent']].drop_duplicates()

json_path = askdirectory(title='Select the folder with *.json files for the islets') # shows dialog box and return the path

json_cell_path= askdirectory(title='Select the folder with *.json files for the cells') # shows dialog box and return the path

#cells.rename(columns={'Centroid X µm':'x','Centroid Y µm':'y'},inplace=True) #this is already satisfied

atr='_islets.geojson'
atr2='_cells.geojson'
for j in range(0,len(list_islets)): #j loops over the islets
    # for a given islet...
    imname=list_islets.iloc[j]['Image'] #get the image
    ide=list_islets.iloc[j]['Parent'] # and islet  name
    islet=json.load(open(json_path+'/'+imname+atr))['features'] #json file for that image, islet
    print('Islet'+str(j)+' of '+str(len(list_islets)),end='\r')
    islet_dic={int(islet[i]['properties']['name']):i for i in range(0,len(islet))} #dictionary for islets and cells
    ids=list(cells[(cells['Image']==imname) & (cells['Parent']==ide)]['Object ID'])#ids of those cells in the islet under study
    boundaries=dp*np.array([ xx for l in islet[islet_dic[int(ide)]]['geometry']['coordinates'] for xx in l])#here, I am ignoring the subcurves
    nones=cells[(cells['Image']==imname) & (cells['Parent']==ide) &(cells['Name']=='none')][['x','y','Object ID']]
    
    #the next 3 lines are necessary for the curves
    allcells=json.load(open(json_cell_path+'/'+imname+atr2))['features'] #json file for that image, cells
    cells_dict={allcells[i]['id']: i for i in range(0,len(allcells))}# dictionary fot the cells in that image
    lnones=nones['Object ID'].map(cells_dict)
    
    nones=np.array(nones[['x','y']])

    #Now for each cell in the islet, I want to compute the minimum distance to the islet border (boundaries), using the centre of mass
    #this is the left hand side
    cells.loc[(cells['Image']==imname) & (cells['Parent']==ide),'d2bordercm']=cells[(cells['Image']==imname) & (cells['Parent']==ide)].apply(lambda dd: cdist(np.array([[dd.x,dd.y]]),boundaries).min(),axis=1)
    if np.any(nones):
        #print('(im,is)=('+imname+','+str(ide)+') has nones')
        cells.loc[(cells['Image']==imname) & (cells['Parent']==ide),'d2nonescm']=cells[(cells['Image']==imname) & (cells['Parent']==ide)].apply(lambda dd: cdist(np.array([[dd.x,dd.y]]),nones).min(),axis=1) #distance to the closest none
    else:
        cells.loc[(cells['Image']==imname) & (cells['Parent']==ide),'d2nonescm']=1000# something too big to win!
    
    #now, using the curves for the cells.
    nonesnuc=[]; nonesmem=[]; #these lists will contain all the points for each (nuc)leus and (mem)brane
    #membrane
    aux=[allcells[t]['geometry']['coordinates'][0] for t in lnones]
    for i in range(0,len(aux)):
        for j in range(0,len(aux[i])):
                       nonesmem.append(aux[i][j])
    nonesmem=dp*np.array(nonesmem)
    #nuclus                   
    aux=[allcells[t]['nucleusGeometry']['coordinates'][0] for t in lnones]
    for i in range(0,len(aux)):
        for j in range(0,len(aux[i])):
                       nonesnuc.append(aux[i][j])
    nonesnuc=dp*np.array(nonesnuc)                   
    
    
    
    
    for j in range(0,len(ids)): 
        nuc=dp*np.array(allcells[cells_dict[ids[j]]]['nucleusGeometry']['coordinates'][0])
        mem=dp*np.array(allcells[cells_dict[ids[j]]]['geometry']['coordinates'][0])
        
        cells.loc[cells['Object ID']==ids[j],'d2bordernuc']=cdist(boundaries,nuc).min()
        cells.loc[cells['Object ID']==ids[j],'d2bordermem']=cdist(boundaries,mem).min()
        if np.any(nones):
            cells.loc[cells['Object ID']==ids[j],'d2nonesnuc']=cdist(nonesnuc,nuc).min()
            cells.loc[cells['Object ID']==ids[j],'d2nonesmem']=cdist(nonesmem,mem).min()
            

    



                       
#after the loop
cells['d2bordercmono']=cells[['d2bordercm','d2nonescm']].min(axis=1)
cells['d2bordermemono']=cells[['d2bordermem','d2nonesmem']].min(axis=1)
cells['d2bordernucono']=cells[['d2bordernuc','d2nonesnuc']].min(axis=1)
cells.to_csv('cells_'+case+'.csv')
print('we succesfully included the distance to the border. The updated dataframe is stored in ./cells_'+case+'.csv')


