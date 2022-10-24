# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 17:35:41 2022

@author: berezo
"""
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from tqdm import tqdm

class FeatureClass:
    def __init__(self, driver, crs, schema, encoding):
        self.driver = driver
        self.crs = crs
        self.schema = schema
        self.encoding = encoding
    
    def setColumnNames(self):
        self.columnNames = []
        for key in self.schema['properties'].keys():
            self.columnNames.append(key)
    
    def setPopColumnName(self, popColumnName):
        self.popColumnName = popColumnName

    def setPolygons(self, fcFiona):
        self.polygons = []
        for polygonFiona in fcFiona:
            polygonShapely = self.getPolygonFromFiona(polygonFiona)
            self.polygons.append([polygonShapely.bounds, polygonShapely, polygonFiona])
        self.mergesort(self.polygons)
    
    def setPolygonsDuo(self):
        self.polygonsDuo = []
        for i, polygon1 in enumerate(tqdm(self.polygons)):
            for j, polygon2 in enumerate(self.polygons):
                if j < i:
                    if polygon1[1].intersects(polygon2[1]):
                        polygonDuo = polygon1[1].union(polygon2[1])
                        self.polygonsDuo.append([[polygonDuo.bounds, polygonDuo, self.polygons[i][2]],[polygonDuo.bounds, polygonDuo, self.polygons[j][2]]])

    def getPolygonFromFiona(self, polFiona):
        geometryType = polFiona['geometry']['type']
        geometryCoor = polFiona['geometry']['coordinates']
        geometryPart = len(geometryCoor)
        
        if geometryType == 'Polygon':
            #Polygon without ring
            if geometryPart == 1:
                polygonShapely =  Polygon(geometryCoor[0])
            #Polygon with ring
            else:
                polygonShapely =  Polygon(geometryCoor[0], geometryCoor[1:])
    
        elif geometryType == 'MultiPolygon':
            polygonShapelyList = []
            for i in range(geometryPart):
                geometryPartRing = len(geometryCoor[i])
                #Multipolygon without ring
                if geometryPartRing == 1:
                    polygonShapelyPart =  Polygon(geometryCoor[i][0])
                #Multipolygon with ring
                else:
                    polygonShapelyPart =  Polygon(geometryCoor[i][0], geometryCoor[i][1:])
                polygonShapelyList.append(polygonShapelyPart)
            polygonShapely = MultiPolygon(polygonShapelyList)
    
        return polygonShapely
    
    def mergesort(self, polygonList):
        if len(polygonList)>1:
            mid = len(polygonList)//2
            polygonListLeft = polygonList[:mid]
            polygonListRight = polygonList[mid:]
            self.mergesort(polygonListLeft)
            self.mergesort(polygonListRight)
            i = 0
            j = 0
            k = 0
            while i<len(polygonListLeft) and j<len(polygonListRight):
                if polygonListLeft[i][0][0]<polygonListRight[j][0][0]:
                    polygonList[k] = polygonListLeft[i]
                    i += 1
                    k += 1
                else:
                    polygonList[k] = polygonListRight[j]
                    j += 1
                    k += 1
            while i<len(polygonListLeft):
                polygonList[k] = polygonListLeft[i]
                i += 1
                k += 1
            while j<len(polygonListRight):
                polygonList[k] = polygonListRight[j]
                j += 1
                k += 1

        
        