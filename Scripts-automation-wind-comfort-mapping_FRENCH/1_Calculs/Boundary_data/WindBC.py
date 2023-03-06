from modules.tools import *
import colorama
from math import cos,sin
import numpy as np
import pandas as pd
from scipy.interpolate import interp1d as interp1d
import os
import shutil
workingPath = ""

class BC():
    def __init__(self, jsonInput,workingPath):
        self.epsilon = 0.01
        self.workingPath = workingPath
        
        self.Extract(jsonInput)
        self.BondBox()
        self.MakeMesh()
        self.MakeProfile()
        self.MakeVelocities()
        self.MakeOutput()

    def Log(self,txt,lvl=1):
        if lvl == 1:
            line = " ** " + txt
        if lvl == 2:
            line = "      - " + txt
        print(line)

    def Dot(self,X,Y):
        S = 0
        for x,y in zip(X,Y):
            S += x*y
        return S

    def BondBox(self):
        """
        Creates the wind vector
        Determines the type of the vertical BC :
            - inlet
            - outlet
            - side (can be symmetry or slip)
        """
        # Defining angles and vectors
        self.i = (self.windDirection + self.north) / 180 * np.pi
        Ux,Uy = np.array([1,0,0]),np.array([0,1,0])
        self.windVect = - sin(self.i)*Ux - cos(self.i)*Uy
        self.normal = {
            "XMin":Ux,
            "XMax":-Ux,
            "YMin":Uy,
            "YMax":-Uy
        }

        self.types = {}
        # Type of BC by face
        self.Log("Boundary conditions of the bonding box to be set as follow")
        for face in self.normal:
            if abs(self.Dot(self.windVect,self.normal[face])) < self.epsilon:
                self.types[face] = "side"
            elif self.Dot(self.windVect,self.normal[face]) > 0:
                self.types[face] = "inlet"
            elif self.Dot(self.windVect,self.normal[face]) < 0:
                self.types[face] = "outlet"
            self.Log("FACE: {} // BC: {}".format(face,self.types[face]),lvl=2)
        
    def MakeProfile(self):
        if self.source == "log":
            self.profile = self.LogProfile()
        elif self.source == "csv":
            self.profile = self.CSVProfile()

    def LogProfile(self):
        f = lambda Z: self.Uref * np.log(Z/self.Z0) / np.log(self.href / self.Z0)
        def pro(Z):
            if Z > 0:
                return f(Z)
            else:
                return 0

        self.Log("Wind profile created from log law with following parameters:")
        log = ["Z0","href","Uref"]
        for l in log:
            self.Log(l + " = " + str(getattr(self,l)),lvl=2)
        return pro

    def CSVProfile(self):
        """
        Reads the velocity profile from a csv file with 2 columns : height and velocity
        Interpolates
        Returns the interpolation function
        """
        # Extracting data from the CSV file
        if ".csv" not in self.file:
            self.file += ".csv"
        filePath = self.workingPath + self.file
        raw = pd.read_csv(filePath,sep=self.sep)
        try:
            int(self.Ucol)
            Ucol = raw.columns[self.Ucol]
        except:
            Ucol = self.Ucol
        try:
            int(self.Zcol)
            Zcol = raw.columns[self.Zcol]
        except:
            Zcol = self.Zcol
        raw[Zcol].values
        # Interpolating
        f = interp1d(raw[Zcol].values,raw[Ucol].values)

        self.Log("Wind profile created from csv file {}, column {}".format(self.file,Ucol))
        return f

    def MakeVelocities(self):
        """
        For each point in mesh, creates the velocity vector at its height
        """
        self.velocities = {}
        self.Log("Calculating boundary velocities for:")
        for face in self.meshes:
            self.Log(face,lvl=2)
            self.velocities[face] = []
            for point in self.meshes[face]:
                self.velocities[face].append([
                    self.windVect[0] * self.profile(point[2]), # x = windDir.x * profile(z), 
                    self.windVect[1] * self.profile(point[2]), # x = windDir.y * profile(z), 
                    0
                ])       

    def ClearOutput(self):
        bD = "boundaryData"
        self.Log("Clearing existing output boundaryData files")
        # Deleting the existing output file
        try:
            shutil.rmtree(self.workingPath+bD)
        except:
            1
        # Creating the new output file
        os.mkdir(self.workingPath+bD)

    def MakeOutput(self):
        self.ClearOutput()
        sep = os.path.sep
        bD = self.workingPath+"boundaryData"

        # Creating
        for face in self.meshes:
            self.Log("Creating output for " + face)
            os.mkdir(bD + sep + face)
            self.Log("Directory {} created".format(bD + sep + face),lvl=2)
            self.PrintVectors(bD + sep + face + sep + "points",self.meshes[face])
            os.mkdir(bD + sep + face + sep + "0")
            self.Log("Directory {} created".format(bD + sep + face+ sep + "0"),lvl=2)
            self.PrintVectors(bD + sep + face + sep + "0" + sep + "U",self.velocities[face])

    def PrintVectors(self,filePath,content):
        """
        Reads a list of points
        Formats it
        Creates the output file
        """
        outputLines = ["( "]
        for vec in content:
            line = "(" + "\t"
            line += str(round(vec[0],2)) + "\t"
            line += str(round(vec[1],2)) + "\t"
            line += str(round(vec[2],2)) + "\t"
            line += ")"
            outputLines.append(line)
        outputLines.append(")")

        with open(filePath,'w') as output:
            for line in outputLines:
                output.write(line + "\n")
        self.Log("File {} created".format(filePath),lvl=2)

    def MakeMesh(self):
        """
        Creates the points for the BC definition
        """
        inlets = [key for key in self.types if self.types[key]=="inlet"]
        self.meshes = {}
        log = ''
        for face in inlets:
            if "XM" in face:
                self.meshes[face] = self.MakeXFace(face)
            if "YM" in face:
                self.meshes[face] = self.MakeYFace(face)
            log += face + ' '
            
        self.Log("Point coordinates created for faces " + log)

    def MakeXFace(self,face):
        """
        Creates the points for the XMin and XMax faces
        """
        x = getattr(self,face)
        Ystep = (self.YMax-self.YMin) / self.Ny
        Zstep = (self.ZMax-self.ZMin) / self.Nz
        Yaxis = np.arange(self.YMin,self.YMax+Ystep,Ystep)
        Zaxis = np.arange(self.ZMin,self.ZMax+Zstep,Zstep)
        thisFace = []
        for y in Yaxis:
            for z in Zaxis:
                thisFace.append([x,y,z])
        return thisFace

    def MakeYFace(self,face):
        """
        Creates the points for the YMin and YMax faces
        """
        y = getattr(self,face)
        Xstep = (self.XMax-self.XMin) / self.Nx
        Zstep = (self.ZMax-self.ZMin) / self.Nz
        Xaxis = np.arange(self.XMin,self.XMax+Xstep,Xstep)
        Zaxis = np.arange(self.ZMin,self.ZMax+Zstep,Zstep)
        thisFace = []
        for x in Xaxis:
            for z in Zaxis:
                thisFace.append([x,y,z])
        return thisFace

    def Extract(self,jsonInput):
        """
        Extracting data from json input file
        """
        # BOUNDING BOX
        self.XMin = jsonInput["Xmin"]
        self.XMax = jsonInput["Xmax"]
        self.YMin = jsonInput["Ymin"]
        self.YMax = jsonInput["Ymax"]
        self.ZMin = jsonInput["Zmin"]
        self.ZMax = jsonInput["Zmax"]
        # MESH PROPERTIES
        self.Nx = jsonInput["Nx"]
        self.Ny = jsonInput["Ny"]
        self.Nz = jsonInput["Nz"]
        # NORTH DIRECTION
        try:    
            self.north = jsonInput["north"]
        except:
            self.north = 0
        # WIND DIRECTION
        self.windDirection = jsonInput["windDir"]

        if jsonInput["source"] == "csv":
            self.source = jsonInput["source"]
            self.file = jsonInput["file"]
            try:
                self.Ucol = jsonInput["U-column"]
            except:
                self.Ucol = 1
            try:
                self.Zcol = jsonInput["Z-column"]
            except:
                self.Zcol = 0
            try:
                self.sep = jsonInput["sep"]
            except:
                self.sep = ","
        elif jsonInput["source"] == "log":
            self.source = jsonInput["source"]
            self.Uref = jsonInput["Uref"]
            self.Z0 = jsonInput["Z0"]
            try:
                self.href = jsonInput["href"]
            except:
                self.href = 10 
        else:
            raise ValueError("In input.json, source must be : 'log' or 'csv'.")
        self.Log("File 'input.json' succesfully extracted.")



jsonContent = LoadJson('input')[0]
BC(jsonContent,workingPath)



