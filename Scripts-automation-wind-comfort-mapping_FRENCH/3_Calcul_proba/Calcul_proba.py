# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 16:40:37 2021

@author: a.conrad
"""
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Ce code permet de calculer les probabilites des vitesses de vent, selon le critere de Lawson.                                                                              #
# Il prend en entree un fichier json dans lequel sont indiques les noms des fichiers csv qu'il faut analyser, soit les extraits des zones d'interet des calculs.             #
# Il ne fonctionne pas avec une classe mais bien avec plusieurs fonctions. Cette maniere de fonctionner a ete jugee plus utile et rapide au moment du developpement du code. # 
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

import pandas as pd
import numpy as np
import json
import os

#-----------------------------------------------------------------------------------------------------------------------#
# Cette fonction sert à lire le json et retourner une liste (sans les paragraphes commentes) de plusieurs sous-listes.  #
# Une sous-liste est composee des elements qui sont entre parentheses de ce type {} dans le json.                       #
#-----------------------------------------------------------------------------------------------------------------------#

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

#-------------------------------------------------------------------------------------------#
# Cette fonction permet de sortir sous forme de listes les différents parametres suivants : #
#    k, c, vitesse moyenne et fractions asssociees a chaque direction.                      #
# La fonction lit les fichiers csv et retourne les listes contenant les informations.       #
#-------------------------------------------------------------------------------------------#

def Weibull_and_fraction():
    Weibull_param = pd.read_csv('Param_Weibull.csv', usecols = ['k', 'c', 'vitesse moyenne'])
    fractions_dir = pd.read_csv('Fractions_vent.csv', usecols = ['direction', 'wind_fraction'])
    k = Weibull_param ['k'].tolist()
    c = Weibull_param ['c'].tolist()
    speed = Weibull_param ['vitesse moyenne'].tolist()
    directions = fractions_dir ['direction'].tolist()
    fractions = fractions_dir ['wind_fraction'].tolist()
    # print (k,c, speed, directions, fractions)
    return k, c, speed, directions, fractions

#---------------------------------------------------------------------------------------------------------------------------------------------------#
# Cette fonction permet de calculer pour chaque fichier csv les probabilites de surpassement de la vitesse du vent.                                 #
# La fonction cree une liste grace aux numbers lu du fichier json. Ceci permettra a compter et associer une position pour chaque fichier.           #
# La liste num est utilisee pour lire les listes de k, c, vitesse moyenne et fractions.                                                             #
# La fonction calcule et ajoute une colonne au csv lu qui est la proba pour le csv en lui-même.                                                     #
# Il faudra ensuite sommer toutes les probas en leur appliquant surtout une fraction. La somme sera effectuee dans la fonction suivante (Proba_tot) #
# mais en attendant une colonne proba_tot_temp est creee dans chaque csv qui est egal au proba * fractions de la direction.                         #
#---------------------------------------------------------------------------------------------------------------------------------------------------#
 
def Calcul_proba (case, k, c, speed, directions, fractions,U_seuil):
    num = case ["number"]
    file = case ["csvFile"]
    c_w = c[num]
    k_w = k[num]
    df_extract = pd.read_csv(os.path.join(file))                                                                     # lecture du fichier csv et association en dataframe
    # df_extract["mag_U"] = (abs(df_extract["U_0"])**2 + abs(df_extract["U_1"])**2 + abs(df_extract["U_2"])**2)**(1/2) # ajout d'une colonne pour la magnitude de la vitesse grâce aux trois composantes de vitesse
    df_extract["G_i"]= df_extract["U_Magnitude"]/speed[num]           # ajout d'une colonne pour la fonction G_i
    df_extract["proba"] = np.exp(-((U_seuil/(df_extract["G_i"]*c_w))**k_w))*100                                         # ajout d'une colonne de probabilite, en fonction d'une vitesse seuil
    df_extract["proba_tot_temp"]=fractions[num]*df_extract["proba"]                                                  # ajout d'une colonne pour la proba totale partielle, associee a ce csv
    i = directions[num]
    df_extract.to_csv('Extrait_post_calcul_dir_' + str(i) + '.csv')                                                  # ecriture en csv des dataframe modifies
    return df_extract, num

# Cette fonction Proba_tot permet d'obtenir la probabilite totale, qui sera regardee et exploitee. 
# Cette fonction prend en entree un nombre. Ce nombre sera la longueur de la liste des directions, 
#       car cela correspond au nombre de fichiers csv obtenus apres calculs de la probabilite,
#       grace a la fonction precedente.
# La fonction retourne un dataframe contenant une colonne avec la proba totale. 

def Proba_tot(l):
    proba_tot = pd.DataFrame(data=None, index = None, columns = None)

    for i in range (l) :
        data_temp = pd.read_csv('Extrait_post_calcul_dir_' + str(directions[i]) + '.csv', usecols = ["proba_tot_temp"])
        proba_tot.insert(i,str(i),data_temp["proba_tot_temp"], allow_duplicates = True)
        proba_tot["proba_totale"] = proba_tot.sum(axis = 1)
        return proba_tot

#---------------------------------------------------------------------------------------------------------------------------------------#
# Cette fonction ecrit le dataframe sorti par Proba_tot dans la derniere colonne du csv du premier fichier csv (premiere direction).    #
# Elle ne retourne rien mais ecrit le fichier csv final.                                                                                #
#---------------------------------------------------------------------------------------------------------------------------------------#
        
def Ecriture_CSV_final(proba_tot):
    data_finale = pd.read_csv('Extrait_post_calcul_dir_' + str(directions[0]) + '.csv')
    data_finale.insert(18, 'proba_finale', proba_tot['proba_totale'], allow_duplicates=True)
    data_finale.to_csv('CSV_FINAL.csv')
    
##################################################################################
##### CE QUI TOURNE A LA FIN ET SE SERT DES FONCTIONS DEFINIES PRECEDEMMENT ######
##################################################################################

k, c, speed, directions, fractions = Weibull_and_fraction()

temp = LoadJson ('input_val_ref')
U_seuil = temp[0]['U_seuil']

for case in LoadJson('input_calcul_proba'):
    df_extract, num = Calcul_proba(case, k, c, speed, directions, fractions, U_seuil)

l = len(directions)
proba_tot = Proba_tot(l)

Ecriture_CSV_final(proba_tot)







