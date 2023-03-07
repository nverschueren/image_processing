# Feb. 2023 Nicolas Verschueren van Rees: nv13699@my.bristol.ac.uk
import os
from tkinter.filedialog import askdirectory
path=askdirectory(title='Select the parent directory of the subset')
print(path)
Nu=input('how many subsets?')
print(Nu)
oupath=askdirectory(title='move files back to?')
#i=0
for i in range(1,int(Nu)):
    sd=os.path.join(path,str(i))
    allfiles=os.listdir(sd)
    print(sd)
    [os.rename(
        os.path.join(sd,j),
        os.path.join(oupath,j)) for j in allfiles] 
