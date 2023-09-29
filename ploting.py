import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tkinter import filedialog as fd
import json
from tkinter.filedialog import askdirectory
from scipy.spatial import distance_matrix
from scipy.spatial.distance import cdist

print("Provide the cells file")
cells=fd.askopenfilename();cells=pd.read_csv(cells)

json_path = askdirectory(title='Select the folder with *.json files for the islets') # shows dialog box and return the path
list_ima=list(cells['Image'].drop_duplicates());
print("The available images are:")
print(list_ima)
t=input("Introduce the index (starting in 0) of the image you'd like to see")
t=int(t)
#t=2; # particular image
dp=0.24999491876223942# micrometer_size.groovy )
atr='_islets.geojson'

islet=json.load(open(json_path+'/'+list_ima[t]+atr))['features']
cells[cells['Image']==list_ima[t]][['x','y','Name']]
co={'alpha_cell':'m','delta_cell':'g','beta_cell':'r','none':'b','epsilon_cell':'y'}
cells_im=cells[cells['Image']==list_ima[t]]
for i in range(0,len(islet)):
    boundaries=dp*np.array([ xx for l in islet[i]['geometry']['coordinates'] for xx in l])
    plt.scatter(boundaries[:,0],boundaries[:,1],color='gray')


plt.scatter(cells_im['x'],cells_im['y'],color=cells_im['Name'].map(co))
plt.gca().invert_yaxis()
plt.gca().set_title(list_ima[t])
plt.show(block=False)

