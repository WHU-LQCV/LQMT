#!/usr/bin/env python

#additionally needed libraries: openpyxl
#%%
import luxpy as lx
import numpy as np
import sys
import pandas as pd
import math
# import spectral_databases as dat
#%% 
def deltaCstar(source_SPD):
#%%
    #source_SPD=dat._CIE_D65[:,20:421]#lx.toolboxes.spdbuild.spd_builder()[:,20:] 
    #source_SPD= lx.spectrum.blackbody(6500)[:,20:421]
    #source_SPD= pd.read_excel('validateCP.xlsx',sheet_name='Sheet1',engine = 'openpyxl').iloc[:,:].to_numpy()   
    a=lx._MUNSELL
    cqs_r=pd.read_csv('CQS_colors.txt', sep=" ", header=None)
    #for key in CQS.keys():
       # print(key)
    b=list(a.keys())
    hue=a['H']
    value=a['V']
    chroma=a['C']
    R=a['R'][:,:401]
    munsell=np.hstack([hue,value,chroma])
    munsell_list=np.array([1094,1001,931,830,750,670,557,495,432,330,261,201,138,71,1231])
    munsell_R=R[0,:]
    for i in range(0,15):
        munsell_R=np.vstack([munsell_R,R[munsell_list[i],:]])
    dcs_list=[]
    cct=lx.color.cct.xyz_to_cct(lx.spectrum.spd_to_xyz(source_SPD))
    source_SPD=source_SPD[1,:]#:401]
    #cct=6500
    black_SPD=lx.spectrum.blackbody(cct)[1,20:421]
    CQS=lx._CRI_RFL['cqs']['v9.0'][:,20:421]
    
    for j in range(0,15):
        SPD=        CQS[j+1,range(0,401,int(math.ceil(401/len(source_SPD))))]    *source_SPD
        #SPD=        R[munsell_list[j],range(0,401,int(math.ceil(401/len(source_SPD))))]    *source_SPD
        SPD=np.vstack([range(380,781,int(math.ceil(401/len(source_SPD)))),SPD])
        SPD_black=  CQS[j+1,range(0,401,int(math.ceil(401/len(black_SPD))))]    *black_SPD
        #SPD_black=  R[munsell_list[j],range(0,401,int(math.ceil(401/len(black_SPD))))]    *black_SPD
        SPD_black=np.vstack([range(380,781,int(math.ceil(401/len(black_SPD)))),SPD_black])
        #print("len: "+str(len(source_SPD)))
        xyz_testsource=lx.spectrum.spd_to_xyz(SPD)
        xyzw_testsource=lx.spectrum.spd_to_xyz(np.vstack([range(380,781,int(math.ceil(401/len(source_SPD)))),source_SPD]))
        xyz_blackbody=lx.spectrum.spd_to_xyz(SPD_black)
        xyzw_blackbody=lx.spectrum.spd_to_xyz(np.vstack([range(380,781),black_SPD]))
        ab_testsource=lx.color.ctf.colortransforms.xyz_to_lab(xyz=xyz_testsource,xyzw=xyzw_testsource)[:,1:] # XYZ_W unmultipliziertes Spektrum!!?
        ab_blackbody=lx.color.ctf.colortransforms.xyz_to_lab(xyz=xyz_blackbody,xyzw=xyzw_blackbody)[:,1:]
        dcs_list.append(np.linalg.norm(ab_testsource)-np.linalg.norm(ab_blackbody))#(np.linalg.norm(ab_blackbody-ab_testsource))#fehler in abstandsbildung--> kann nicht negativ sein  
        dcs=sum(dcs_list)/len(dcs_list)  
# %%
    return dcs

def calc_cp(DC,E,sourceSPD):
    #%%
    cct=lx.color.cct.xyz_to_cct(lx.spectrum.spd_to_xyz(sourceSPD))
#%% return erweitern auf: cct, deltacstar, lab
    cp=(14.089*np.log(E*sv024(cct))-25.397)*(-0.003*DC**2+0.0252*DC+1.0192)+(-518.554*(sv024(cct))**2+864.872*sv024(cct)-356.578) #geändert: *1.0192
#%%
    return cp
    
def sv024(cct):
    return -0.0138*(cct/1000)**2+0.1769*cct/1000+0.2859

#%%
def test():
#%%
    source_SPD= pd.read_excel('validateCP.xlsx',sheet_name='Sheet1',engine = 'openpyxl').iloc[:,:].to_numpy()
    illuminance=171
    cp=calc_cp(source_SPD,illuminance)
# %%
