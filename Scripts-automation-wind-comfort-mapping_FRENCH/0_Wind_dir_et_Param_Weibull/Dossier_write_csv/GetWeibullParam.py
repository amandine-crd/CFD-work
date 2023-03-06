#########################################################################################################################
# Ce code a ete principalement developpe par Arnaud Sanson. C'est le GetWeibullParam_V2.py modifie.                     #
# Les modifications ont ete apportees par Amandine Conrad, stagiaire Elioth Environnement, juin 2021.                   #
# Les modifications apportees sont l'ecriture d'un fichier contenant les parametres de Weibull et la vitesse moyenne.   #
# Ces donnees serviront pour le calcul de probabilites pour le confort au vent.                                         #
#########################################################################################################################

import numpy as np
from random import random as random
import matplotlib.pyplot as pl
from scipy import stats
import pandas as pd
import json
import os

# =============================================================================
#           UTILS
# =============================================================================

#-----------------------------------------------------------------------------------------------#
# Cette fonction permet, comme dans d'autres codes de lire un json et de retourner une liste.   # 
# Chaque membre de la liste est constitué des différentes données encadrées par {}              #
#-----------------------------------------------------------------------------------------------#

commentBeacon = "#"
def LoadJson(fileName):
    if '.json' not in fileName:
        fileName = fileName+'.json'

    with open(fileName) as JSON:
        content = json.loads(JSON.read())
    
    uncommentedContent = []
    for c in content:
        if commentBeacon in c.keys(): # Deleting pseudo commenting entries
            D = {k:c[k] for k in c.keys() if k != commentBeacon}
            
            if len(D) == 0: # If imported dict is only commentary, no importation
                continue
            else:
                uncommentedContent.append(D)

        else:
            D = c
            uncommentedContent.append(D)
    return uncommentedContent

# =============================================================================
#           SCRIPT
# =============================================================================

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Ici on définit une classe pour l'obtention des paramètres de Weibull. Ce qu'effectue la classe est définie dans la fonction __init__.                                             #
# La classe prend un case en entrée qui, dans notre cas, correspond aux données entre deux accolades du json.                                                                       #
# La classe va d'abord importer le CSV, puis convertir, effectuer une régresssion, afficher les résultats puis finalement lire et exporter les données (k, c et vitesse moyenne).   #
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#


class WeibullParameters():
    def __init__(self,case):
        # ************************************************
        self.name = case["name"]
        self.file = case["csvFile"]
        self.dataName = case["dataName"]
        self.logDataName = self.dataName + "_log"
        self.corDataName = self.dataName + "_Z"
        try:
            self.zero = case["zeros"]
        except:
            self.file = 0.05
        try:
            self.nbVals = case["histBars"]
        except:
            self.nbVals = 50
        # ************************************************
        self.ImportCSV()
        self.Convert()
        self.Regression()
        self.Display()
        self.Read_and_Export(self.k, self.c, self.moy)

#---------------------------------------------------------------------------------#
# La fonction Display permet de montrer à l'utilisateur les valeurs après calcul. #
#---------------------------------------------------------------------------------#

    def Display(self):
        print("*--------------------------*")
        print('  Loi de distribution :')
        print('  F(X) = 1 - exp(-(X/c)^k)')
        print("   k = {}".format(round(self.k,3)))
        print("   c = {}".format(round(self.c,3)))
        print("*--------------------------*")
        print("  Valeur moyenne : {}".format(round(self.moy,3)))
        print("*--------------------------*")
        
        self.DisplayPictures()

#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# La fonction Read_and_Export permet d'obtenir le fichier csv contenant les parametres de Weibull et la vitesse moyenne.                                                                    #
# Elle n'est pas ecrite de maniere tres simple car, du fait que pour chaque cas, le k et le c change.                                                                                       #
# La solution trouvee pour tout ecrire et obtenir le tout dans un csv a donc ete de lire le csv des parametres ecrit precedemment lors de la lecture d'un premier fichier de donnees csv,   #
# puis d'y ecrire les nouveaux parametres.                                                                                                                                                  #
# Si le fichier n'existe pas, il le cree en y ecrivant les premiers parametres.                                                                                                             #
#Si le fichier existe, il le lit, uniquement les colonnes k, c et vitesse moyenne puis rajoute les nouveaux parameters.                                                                     #
#-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

    def Read_and_Export (self, a, b, c):
        self.test = os.path.isfile('Param_Weibull.csv')
        if self.test == False:
            self.df_final = pd.DataFrame(data = None, index = None, columns = ['k','c', 'vitesse moyenne'])
            self.df = pd.DataFrame (data = [[a, b, c]], index = None, columns = ['k','c', 'vitesse moyenne'])
            self.df_final = self.df_final.append(self.df)
            self.df_final.to_csv('Param_Weibull.csv', index = False)
        else:
            self.df_final = pd.read_csv('Param_Weibull.csv', usecols = ['k','c', 'vitesse moyenne'])
            self.df = pd.DataFrame([[a, b, c]], index = None, columns = ['k','c', 'vitesse moyenne'])
            self.df_final = self.df_final.append(self.df)
            self.df_final.to_csv('Param_Weibull.csv', index = False)    

#----------------------------------------------------------------------------------------------------------------#
# Le reste du code avait ete developpe par Arnaud Sanson. La repartition de Weibull des vitesses est recherchee. #
#----------------------------------------------------------------------------------------------------------------#

    def Regression(self):
        Y = self.data['Weibull']
        self.data[self.logDataName] = np.log(self.data[self.corDataName])
        # Xx = kX-k.ln(c)
        k,B,*t = stats.linregress(self.data[self.logDataName],Y)
        c = np.exp(-B / k)
        self.k, self.c, self.B = k,c,B
        self.moy = self.data[self.dataName].sum() / self.data[self.dataName].count()

    def WeibullInverse(self,p):
        inv = np.log(-np.log(1.0-p))
        return inv

    def Convert(self):
        # Supprimer les zeros
        dataMin = self.data[self.dataName].min()
        if dataMin == 0.0:
            self.data[self.corDataName] = self.data[self.dataName].replace(dataMin,self.zero)
        else:
            self.data[self.corDataName] = self.data[self.dataName]
        # Creer les probas
        self.data['p'] = (self.data.index - self.data.index[0]+1) / (len(self.data.index)+1)
        self.data['Weibull'] = self.WeibullInverse(self.data['p'])

    def ImportCSV(self):
        self.data = pd.read_csv(self.file)
        # self.data.columns = self.Columns()
        self.data = self.data.sort_values(by=self.dataName)
        self.data = self.data.reset_index(drop = True)

    def PlotData(self,column):
        pl.plot(self.data[column],'o')
        pl.grid()
        pl.xlabel('#Value')
        pl.ylabel('Value')
        pl.title('Repartition of values')
    
    def CheckPlot(self):
        # pl.figure()
        self.f.add_subplot(1,2,1) # XXX
        pl.plot(self.data[self.logDataName],self.data['Weibull'])
        pl.plot(self.data[self.logDataName],self.data['Weibull'],'*')
        x = np.arange(self.data[self.logDataName].iloc[0], self.data[self.logDataName].iloc[-1]+0.1,0.1)
        y = (lambda x : self.k * x + self.B)(x)
        pl.plot(x,y)
        pl.plot()
        pl.grid()
        pl.ylabel('log(-log(1 - Probability))')
        pl.xlabel('-log({})/m'.format(self.dataName))
        pl.title("Weibull Analysis of imported data - "+self.name)
        pl.legend(['Data','Data','Interpolation'])

    def HistData(self,column):
        pl.hist(self.data[column],self.nbVals)
        pl.grid()
        pl.xlabel(self.dataName)
        pl.ylabel('Quantity')
        pl.title('Repartition of values - ' + self.name)

    def DistributionPlot(self):
        # pl.figure()
        self.f.add_subplot(1,2,2) # XXX
        density = lambda x : (1 - np.exp(-(x/self.c)**self.k)) * self.data[self.dataName].count()
        self.HistData(self.dataName)
        step = self.data[self.dataName].max() / self.nbVals
        x_minus = np.arange(self.data[self.dataName].min(), self.data[self.dataName].max(),step)
        x_plus = np.arange(self.data[self.dataName].min()+step/2, self.data[self.dataName].max()+step/2,step)
        y = (density(x_plus) - density(x_minus)) / step
        F = self.data[self.dataName].count() / sum(y)
        pl.plot(x_plus,y*F)
        
    def DisplayPictures(self):
        self.f = pl.figure(figsize=(10.5,5))
        self.CheckPlot()
        self.DistributionPlot()
        pl.show(block=True)

if __name__ == "__main__":
    for L in LoadJson('input_Weibull'):
        WeibullParameters(L)
