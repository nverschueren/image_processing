# 2023 Nicolas Verschueren van Rees: nv13699@my.bristol.ac.uk
# update 29/6
# The purpose of this script is to  automate the process of dividing the tiles into manageable files for QuPath.
# This is done in  steps
# I) Ask for the directory where the tiles are (prompt)
# We compute the position and size of the tiles (top left pixel) in variable ll (line 23)
# we ask the user what is the maximum size your computer can hande (4gb for a laptop, 10gb for scan). Then we estimate how many big pictures (clusters) we suggest in variable N (line 35)
# useful additions:
# i) save the final figure with the respective clusters and colours next to the subdirectories
# ii) Create a file with the necessary information to compute the absolute distances 
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from tkinter import Tk
from tkinter.filedialog import askdirectory
import glob, os
import pandas as pd
import math
from bisect import bisect
from termcolor import colored
from sys import exit
path = askdirectory(title='Select the folder with *.tiff images') # shows dialog box and return the path
print(path)
pathor=os.getcwd()
os.chdir(path)
al=glob.glob("*.tif")
ll=[[al.index(file),
     file,
     Image.open(file).tag[286][0][0]/Image.open(file).tag[286][0][1],
     Image.open(file).tag[287][0][0]/Image.open(file).tag[287][0][1],
     os.path.getsize(file)/(1024*1024)]  for file in al]
p=pd.DataFrame(ll)
p.columns=['ind','name','x','y','size_mb'];

m=input("What is the maximum size, in GB, that your computer can handle in QuPath?")
print(m+"Gb")
os.chdir(pathor)
N=math.ceil(p['size_mb'].sum()/1024/int(m))

#Now I plot the points
dat=np.array(p[['ind','x','y']])
xmax=dat[:,1].max(); xmin=dat[:,1].min();
ymax=dat[:,2].max(); ymin=dat[:,2].min();
a=(ymax-ymin)/(xmax-xmin)

plt.scatter(dat[:,1],dat[:,2]);
plt.scatter(xmin,ymin,color='r')
plt.scatter(xmax,ymin,color='r')
plt.scatter(xmax,ymax,color='r')
plt.scatter(xmin,ymax,color='r')
ax=plt.gca()
ax.set_aspect(1)
ax.invert_yaxis()
plt.show(block=False)

print("The suggested number of clusters is: "+ str(N)+" and the width/height=" +str(a)+" .Based on these numbers and the picture displayed, you need to decide how many horizontal and vertical divisions use for the splitting. For example if N=6=2*3. Then you might want to put more divisions along the 'longest side' (horizontal if a>1, opposite otherwise). Assuming a>1, then I want 3-1=2 divisions in x and 2-1=1 divisions in y")
divx=input("How many divisions do you want in x? ")
divy=input("How many divisions do you want in y? ")
xs=[xmin+(xmax-xmin)*(i+1)/(int(divx)+1) for i in range(0,int(divx))]
ys=[ymin+(ymax-ymin)*(i+1)/(int(divy)+1) for i in range(0,int(divy))]

readivision=False
undecided=True
while undecided:
    
    if readivision:
        plt.clf()
        plt.scatter(dat[:,1],dat[:,2]);
        plt.scatter(xmin,ymin,color='r')
        plt.scatter(xmax,ymin,color='r')
        plt.scatter(xmax,ymax,color='r')
        plt.scatter(xmin,ymax,color='r')
        for i in range(0,len(xs)):
            plt.plot([xs[i],xs[i]],[ymin,ymax])

        for i in range(0,len(ys)):
            plt.plot([xmin,xmax],[ys[i],ys[i]])
            
        ax=plt.gca()
        ax.set_aspect(1)
        ax.invert_yaxis()
        plt.show(block=False)

        print("Here's the divisions in xs and ys, you can rewrite them here")
        print("xs"); print(xs);
        print("ys");print(ys)
        aux=input("X: write the new divisions separated by a space (leave it blank if you are happy with the old divisions): ")
        aux=aux.split()
        for i in range(0,len(aux)):
            aux[i]=float(aux[i])
            
        if len(aux)>0:
            xs=aux
        aux=input("Y: write the new divisions separated by a space (leave it blank if you are happy with the old divisions: ")
        aux=aux.split()
        for i in range(0,len(aux)):
            aux[i]=float(aux[i])
            
        if len(aux)>0:
            ys=aux    
        
        readivision=False
        
    
    N=(int(divx)+1)*(int(divy)+1); print("the total number of clusters is N="+str(N))

    p['clx']=[bisect(xs,p['x'].iloc[i]) for i in range(0,len(p))]
    p['cly']=[bisect(ys,p['y'].iloc[i]) for i in range(0,len(p))]

    p['cluster']=len(p['cly'].drop_duplicates())*p['clx']+p['cly']
    p=p.drop(columns=['clx','cly'])

    cmap= plt.cm.get_cmap('Paired')
    coco=np.linspace(0,1,N)
    co={i:cmap(coco[i]) for i in range(0,N)}
    cenofmass=np.array(p.groupby(by=['cluster']).agg({'x':'mean','y':'mean'}))
    plt.clf()
    plt.scatter(dat[:,1],dat[:,2]);
    plt.scatter(xmin,ymin,color='r')
    plt.scatter(xmax,ymin,color='r')
    plt.scatter(xmax,ymax,color='r')
    plt.scatter(xmin,ymax,color='r')
    for i in range(0,len(xs)):
        plt.plot([xs[i],xs[i]],[ymin,ymax])
    for i in range(0,len(ys)):
        plt.plot([xmin,xmax],[ys[i],ys[i]])
    ax=plt.gca()
    ax.set_aspect(1)
    plt.scatter(p['x'],p['y'],color=p['cluster'].map(co))
    [plt.text(cenofmass[i][0],cenofmass[i][1],str(i),fontsize=20) for i in range(0,len(cenofmass))]
    ax.invert_yaxis()
    plt.show(block=False)

    #now, print the space on each cluster
    q=p.groupby(by=['cluster']).agg({'cluster':'count','size_mb':'sum'}).rename(columns={'cluster':'tiles','size_mb':'size_gb'}).reset_index(); q['size_gb']=q['size_gb']/1024;
    print("The number of tiles and space on each cluster is")
    print(q)

    print("The number of clusters exceeding "+str(m)+" GB is "+colored(str(len(q[q['size_gb']>int(m)])),'red'))
    #ask if we should proceed
    print(" What is the next step?")
    print("[p]: proceed")
    print("[r] : readjust the divisions")
    print("pressing a different key will exit the program")
    nn=input("...")
    if nn=="p":
        undecided=False
    elif nn=="r":
        print("readjusting divisions")
        readivision=True
    else:
        print("exiting the program")
        exit()

dd=input("I will create one subdirectory for each cluster and move the tiles accordingly. Are you sure? [y/n]?")
if dd=="n":
    exit()
cl=list(q['cluster'])

outpath=askdirectory(title='Select a folder for the subdirectories') # shows dialog box and return the path
os.chdir(outpath)
[os.mkdir('./'+str(d)+'/') for d in cl]
os.mkdir('./extra_information/')
plt.savefig('./extra_information/clusters.png',dpi=150)
q=p.groupby(by=['cluster']).agg({'cluster':'count','size_mb':'sum','x':['min','max','mean'],'y':['min','max','mean']})
q.to_csv('./extra_information/points.csv');#this is in pixel units, I think
for cc in cl:
    ima=list(p[p['cluster']==cc]['name'])
    for i in range(0,len(ima)):
             os.rename(path+"/"+ima[i],outpath+"/"+str(cc)+"/"+ima[i])

fin=input("check if the images have been moved as expected. Unless you want to revert these changes, the program will exit. Do you want to revert? [y/other]")
if fin=="y":
    print("This has not implemented yet! sorry. You can use the script undo_dir.py in the local directory for this task")
    
