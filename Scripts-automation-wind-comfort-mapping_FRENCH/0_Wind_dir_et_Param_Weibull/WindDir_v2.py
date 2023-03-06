# -*- coding: utf-8 -*-
"""
Created on Fri Jun  4 18:03:37 2021

@author: a.conrad
"""
# AUTEUR : Amandine Conrad, stagiaire Elioth Environnement 04/2021 - 10/2021

###########################################################################################################################################################################################
# Ce code lit un fichier json intitule "input_dir.json" dans lequel se trouve les différentes informations nécessaires. Les informations qui sont nécéssaires sont indiquées dans le json. 
# Grace aux differentes donnees d'entree, le code suivant va diviser les directions de vent ainsi que leur vitesse associee (sur une annee) dans les differentes fractions souhaitees. 
###########################################################################################################################################################################################

import pandas as pd
import os
import json

#########################################################################################################################
# Cette fonction sert à lire le json et retourner une liste (sans les paragraphes commentes) de plusieurs sous-listes.  #
# Une sous-liste est composee des elements qui sont entre parentheses de ce type {} dans le json.                       #
#########################################################################################################################

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

####################################################################################################################################################
# Ici tout est reunie dans une classe pour l'export en csv par direction. Les differentes fonctions vont être explicitees dans d'autres commentaires.
####################################################################################################################################################

class Export_csv_par_dir():
    
    def __init__(self, case):
        #****************************#
        self.csv_div = case["csv_div"]
        self.nb_dir = case ["nb_dir"]
        self.nom_epw = case["nom_epw"]
        self.path_csv_write = case ["path_csv_write"]
        self.name_csv_write = case ["name_csv_write"]
        #****************************#
        self.SetUp()
        self.Division_by_direction()
        self.Fractions_vent()

#########################################################################################################################################################################################################################################   
# La fonction SetUp reunit toutes les fonctions et retourne une liste des dataframe utiles pour la division du dataframe/csv global et l'écriture des csv individuels.                                                                            #
# Ces dataframe retournes contiennent les directions de vent et leur vitesse associee.                                                                                                                                                  #
# La fonction SetUp a deux options de fonctionnement, en fonction de si c'est une division par défaut ou par l'utilisateur. Et en fonction de l'un et de l'autre les listes ne contiennent pas le 0 pour l'un ou le 360 pour l'autre.   # 
# Cela a un impact sur la boucle qui utilise la longueur de la liste wind_dir_med. Ainsi les deux options ont ete separees.                                                                                                             #
#########################################################################################################################################################################################################################################

    def SetUp (self):
        test = os.path.isfile(self.csv_div)
        if test == True : 
            self.wind_tuple = self.Division_option(self.csv_div)
        else :
            self.wind_tuple = self.Division_defaut(self.nb_dir)
        self.wind_division = self.wind_tuple[1]
        self.wind_dir_med = self.wind_tuple[0]
        self.wind_dir_speed = self.Read_and_sort_epw(self.nom_epw)
        if test==True :
            self.wind_div = [0]
            self.wind_div.extend(self.wind_division) 
        elif test == False:
            self.wind_div = self.wind_division
            self.wind_div.append(360)
        self.List_split=[]

######################################################################################################################################################################   
# La fonction Division_by_direction divise la liste contenant les différentes dataframe en dataframe indépendants et les assimile à des noms, qui serviront ensuite. #                                                                                                         #
######################################################################################################################################################################

    def Division_by_direction(self):
        self.fractions = []
        for i in range (len(self.wind_div)-1) : 
            self.nom_col = self.wind_dir_speed.columns[0]
            self.a = self.wind_div[i]
            self.b = self.wind_div[i+1]
            self.df = self.wind_dir_speed.loc[(self.wind_dir_speed[self.nom_col] > self.a)&
                                    (self.wind_dir_speed[self.nom_col]<= self.b)]
            self.List_split.append(self.df)
        for i in range (len(self.List_split)):
            self.j = self.wind_dir_med [i]
            self.extract = self.List_split[i]
            self.long = self.extract.shape[0]
            self.fractions.append(self.long/8760)
            self.extract.to_csv(os.path.join(self.path_csv_write, self.name_csv_write + '_dir_' + str(self.j) +'.csv' ))

            # self.extract.to_csv(self.path_csv_write +'/' + self.name_csv_write + '_dir_' + str(self.j) +'.csv')

#########################################################################################################################################################################################
# La fonction Fractions_vent genere un fichier csv dans lequel il est possible de lire ce que chaque direction de vent represente comme fraction par rapport au total des directions.   #
# Ce csv servira lors du calcul de proba suite aux calculs.                                                                                                                             #                                                                                                         #
#########################################################################################################################################################################################


    def Fractions_vent(self):
        self.df_final = pd.DataFrame(data=None, index = None, columns = ['direction','wind_fraction'])
        for i in range (len(self.fractions)):
            a = self.wind_dir_med [i]
            b = self.fractions [i]
            self.df = pd.DataFrame(data = [[a,b]], index = None, columns = ['direction','wind_fraction'])
            self.df_final = self.df_final.append(self.df)
        self.df_final.to_csv(self.path_csv_write +'/'+'Fractions_vent.csv', index = False)
            
##############################################################################################################################
# La fonction Read_and_sort_epw lit le fichier csv avec les directions et vitesses associees de vent sur une annee complete. #  
# La fonction retourne un dataframe, qui est la lecture du fichier csv.                                                                                                       #                                                                                                         #
##############################################################################################################################

        
    def Read_and_sort_epw(self, nom_csv):
        self.wind_dir_speed = pd.read_csv(nom_csv)
        self.wind_dir_speed = self.wind_dir_speed.sort_values(self.wind_dir_speed.columns[0])
        self.wind_dir_speed = self.wind_dir_speed.reset_index (drop = True)
        return self.wind_dir_speed
    
###############################################################################################################
# Cette première fonction lit le csv contenant les directions de vent et les vitesses de vent tirées de l'epw #
# La fonction retourne un DataFrame contenant les données.                                                    #
#  Celui-ci sera utilisé dans le cadre de d'autres fonctions dans la suite du programme                       #
###############################################################################################################
    
    def Division_defaut(self, nb_dir):
        # self.L = [1/self.nb_dir]*self.nb_dir
        self.div = 360/nb_dir
        self.m = self.div/2
        self.wind_dir_gr =[]
        for i in range (nb_dir):
            self.wind_dir_gr.append (i*self.div)
        self.wind_dir_med=[]
        for i in range (nb_dir):
            self.wind_dir_med.append(i*self.div + self.m)
        return  (self.wind_dir_med, self.wind_dir_gr)
    
####################################################################################################################################
#  Cette  fonction effectue la divsion par défaut en prenant comme paramètre d'entrée le nombre de division indiqué dans le json   #
#  La fonction retourne deux listes. Une liste contient les directions de vent médianes                                            #
#  et l'autre liste contient les directions de vent limites par groupe de direction.                                               #                                                  ###############
####################################################################################################################################
    
    def Division_option(self,csv_div):
        self.div_option = pd.read_csv(csv_div)
        self.wind_dir_med = [(self.div_option.iloc[0][1]-self.div_option.iloc[0][0])/2]
        for i in range (1,self.div_option.shape[0]) : 
            self.wind_dir_med.append((self.div_option.iloc[i][1]-self.div_option.iloc[i][0])/2 + self.div_option.iloc[i-1][1])
        self.wind_dir_gr =[]
        for i in range (self.div_option.shape[0]):
            self.wind_dir_gr.append (self.div_option.iloc[i][1])
        # self.L = []
        # for i in range (self.div_option.shape[0]):
        #     self.fraction = (self.div_option.iloc[i][1]-self.div_option.iloc[i][0])/360
        #     self.L.append(self.fraction)
        return self.wind_dir_med, self.wind_dir_gr
    
            
if __name__ == "__main__":
    for L in LoadJson('input_dir'):
        Export_csv_par_dir(L)