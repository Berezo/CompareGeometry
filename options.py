# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 17:32:50 2022

@author: berezo
"""

import featureClass

import collections
import math

import fiona
from shapely.geometry import mapping, Polygon, MultiPolygon
from tqdm import tqdm

def openFC(path):
    with fiona.open(path, 'r', encoding='utf-8') as fcFiona:
        fc = featureClass.FeatureClass(fcFiona.driver, fcFiona.crs, fcFiona.schema, fcFiona.encoding)
        fc.setPolygons(fcFiona)
        fc.setPolygonsDuo()
        fc.setColumnNames()
        print(fc.columnNames,end='')
        popColumnName = input('Enter the name that corresponds to the column in which the population for the layer is located from: ')
        while popColumnName not in fc.columnNames:
             print(fc.columnNames,end='')
             popColumnName = input('Invalid name. Enter the name that corresponds to the column in which the population for the layer is located from: ')
        fc.setPopColumnName(popColumnName)
    
    print(path, 'is loaded.\n')
    return fc

def saveFC(path, fc, schema, features):
    with fiona.open(path, 'w', driver=fc.driver, crs = fc.crs, schema = schema, encoding = fc.encoding) as fcFiona:
        for feature in tqdm(features):
            if feature['geometry']['type'] == 'GeometryCollection':
                continue
            fcFiona.write(feature)
    print(path, 'is saved.')

def saveTXT(path, features):
    line = ''
    propertiesKeys = features[0]['properties'].keys()
    for key in propertiesKeys:
        line += key + ','
        
    with open(path,'w') as file:
        file.write(line[:-1])
        file.write('\n')
        for feature in features:
            line = ''
            for key in propertiesKeys:
                line += str(feature['properties'][key]) + ','
            file.write(line[:-1])
            file.write('\n')
    print(path, 'is saved.')
        
def doComparisonMethod(optionMenu, fc1, fc2, minIntersect):
    if optionMenu == '1':
        optionCount = input('\t1 - Population calculation based only on the geometry of the areas\n\t2 - Calculation of population only on the basis of area geometry and population density\nEnter the number corresponding to the method you want to perform: ')
        while optionCount not in ['1','2']:
            optionCount = input('\t1 - Population calculation based only on the geometry of the areas\n\t2 - Calculation of population only on the basis of area geometry and population density\nInvalid key. Enter the number corresponding to the method you want to perform: ')
        return comparisionOneToOne(fc1, fc2, minIntersect, optionCount)
    elif optionMenu == '2':
        return comparisionTwoToTwo(fc1, fc2, minIntersect)
    elif optionMenu == '3':
        return comparisionTwoToOne(fc1, fc2, minIntersect)
    elif optionMenu == '4':
        return comparisionOneToTwo(fc1, fc2, minIntersect)
    
        
def comparisionOneToOne(fc1, fc2, minIntersect, optionCount):
    features = []
    schema = getSchemaFromFiona(fc1, fc2)
    for polygonFC1 in tqdm(fc1.polygons):
        for polygonFC2 in fc2.polygons:
            indexOldInPre, indexPreInOld, polygonInter = comparisionPolygons(polygonFC1[1], polygonFC2[1])
            if(indexOldInPre > minIntersect and indexPreInOld > minIntersect):
                if optionCount == '1':
                    popPre, popOld = comparisionPopStatArea(polygonFC1, polygonFC2, fc1.popColumnName, fc2.popColumnName, indexOldInPre, indexPreInOld)
                else:
                    popPre, popOld = comparasionPopStatDensity(polygonFC1, polygonFC2, fc1.popColumnName, fc2.popColumnName, indexOldInPre, indexPreInOld)
                fcProperties = getPropertiesFromFiona(polygonFC1[2], polygonFC2[2], indexOldInPre, indexPreInOld, popPre, popOld)
                features.append({
                    "geometry" : mapping(polygonInter),
                    "properties" : fcProperties,
                })
    print('Comparision is done.\n')
    return schema, features

def comparisionTwoToTwo(fc1, fc2, minIntersect):
    features = []
    schema = getSchemaFromFiona(fc1, fc2, True, True)
    for polygonDuo1 in tqdm(fc1.polygonsDuo):
        for polygonDuo2 in fc2.polygonsDuo:
            indexOldInPre, indexPreInOld, polygonInter = comparisionPolygons(polygonDuo1[0][1], polygonDuo2[0][1])
            if(indexOldInPre > minIntersect and indexPreInOld > minIntersect):
                popPre, popOld = comparisionPopStatArea(polygonDuo1[0], polygonDuo2[0], fc1.popColumnName, fc2.popColumnName, indexOldInPre, indexPreInOld, polygonDuo1[1], polygonDuo2[1])
                fcProperties = getPropertiesFromFiona(polygonDuo1[0][2], polygonDuo2[0][2], indexOldInPre, indexPreInOld, popPre, popOld, polygonDuo1[1][2], polygonDuo2[1][2])
                if mapping(polygonInter)['type'] == 'GeometryCollection':
                    polygonInterElems = []
                    for geometryElement in polygonInter:
                        if geometryElement is Polygon:
                            polygonInterElems.append(geometryElement)
                    polygonInter = MultiPolygon(polygonInterElems)
                features.append({
                    "geometry" : mapping(polygonInter),
                    "properties" : fcProperties,
                })
    print('Comparision is done.\n')
    return schema, features

def comparisionTwoToOne(fc1, fc2, minIntersect):
    features = []
    schema = getSchemaFromFiona(fc1, fc2, True)
    for polygonDuo1 in tqdm(fc1.polygonsDuo):
        for polygonFC2 in fc2.polygons:
            indexOldInPre, indexPreInOld, polygonInter = comparisionPolygons(polygonDuo1[0][1], polygonFC2[1])
            if(indexOldInPre > minIntersect and indexPreInOld > minIntersect):
                popPre, popOld = comparisionPopStatArea(polygonDuo1[0], polygonFC2, fc1.popColumnName, fc2.popColumnName, indexOldInPre, indexPreInOld, polygonDuo1[1])
                fcProperties = getPropertiesFromFiona(polygonDuo1[0][2], polygonFC2[2], indexOldInPre, indexPreInOld, popPre, popOld, polygonDuo1[1][2])
                if mapping(polygonInter)['type'] == 'GeometryCollection':
                    polygonInterElems = []
                    for geometryElement in polygonInter:
                        if geometryElement is Polygon:
                            polygonInterElems.append(geometryElement)
                    polygonInter = MultiPolygon(polygonInterElems)
                features.append({
                    "geometry" : mapping(polygonInter),
                    "properties" : fcProperties,
                })
    print('Comparision is done.\n')
    return schema, features

def comparisionOneToTwo(fc1, fc2, minIntersect):
    features = []
    schema = getSchemaFromFiona(fc1, fc2, fc4=True)
    for polygonFC1 in tqdm(fc1.polygons):
        for polygonDuo2 in fc2.polygonsDuo:
            indexOldInPre, indexPreInOld, polygonInter = comparisionPolygons(polygonFC1[1], polygonDuo2[0][1])
            if(indexOldInPre > minIntersect and indexPreInOld > minIntersect):
                popPre, popOld = comparisionPopStatArea(polygonFC1, polygonDuo2[0], fc1.popColumnName, fc2.popColumnName, indexOldInPre, indexPreInOld, polygon4 = polygonDuo2[1])
                fcProperties = getPropertiesFromFiona(polygonFC1[2], polygonDuo2[0][2], indexOldInPre, indexPreInOld, popPre, popOld, fc4 = polygonDuo2[1][2])
                if mapping(polygonInter)['type'] == 'GeometryCollection':
                    polygonInterElems = []
                    for geometryElement in polygonInter:
                        if geometryElement is Polygon:
                            polygonInterElems.append(geometryElement)
                    polygonInter = MultiPolygon(polygonInterElems)
                features.append({
                    "geometry" : mapping(polygonInter),
                    "properties" : fcProperties,
                })
    print('Comparision is done.\n')
    return schema, features

def comparisionPolygons(polygon1, polygon2):
    if polygon1.intersects(polygon2):
        polygonInter = polygon1.intersection(polygon2)
        indexOldInPre = polygonInter.area/polygon1.area*100
        indexPreInOld = polygonInter.area/polygon2.area*100
        return indexOldInPre, indexPreInOld, polygonInter
    else:
        return 0, 0, 0

def comparisionPopStatArea(polygon1, polygon2, popColumnOld, popColumnPre, indexOldInPre, indexPreInOld, polygon3 = [0,0,{'properties':{'o_lud':0}}], polygon4 = [0,0,{'properties':{'lud':0}}]):
    if(indexOldInPre >= 95 and indexPreInOld >= 95):
        popOld = polygon1[2]['properties'][popColumnOld] + polygon3[2]['properties'][popColumnOld]
        popPre = polygon2[2]['properties'][popColumnPre] + polygon4[2]['properties'][popColumnPre]
    elif(indexOldInPre >= 95):
        popOld = polygon1[2]['properties'][popColumnOld] + polygon3[2]['properties'][popColumnOld]
        popPre = math.floor((indexPreInOld/100) * (polygon2[2]['properties'][popColumnPre] + (indexPreInOld/100) * polygon4[2]['properties'][popColumnPre]))
    elif(indexPreInOld >= 95): 
        popOld = math.floor((indexOldInPre/100) * (polygon1[2]['properties'][popColumnOld] + (indexOldInPre/100) * polygon3[2]['properties'][popColumnOld]))
        popPre = polygon2[2]['properties'][popColumnPre] + polygon4[2]['properties'][popColumnPre]
    else:
        popOld = math.floor((indexOldInPre/100) * (polygon1[2]['properties'][popColumnOld] + (indexOldInPre/100) * polygon3[2]['properties'][popColumnOld]))
        popPre = math.floor((indexPreInOld/100) * (polygon2[2]['properties'][popColumnPre] + (indexOldInPre/100) * polygon4[2]['properties'][popColumnPre]))
    return popPre, popOld

def comparasionPopStatDensity(polygonFC1, polygonFC2, popColumnOld, popColumnPre, indexOldInPre, indexPreInOld):
    if(indexOldInPre >= 95 and indexPreInOld >= 95):
        popOld = polygonFC1[2]['properties'][popColumnOld]
        popPre = polygonFC2[2]['properties'][popColumnPre]
    elif indexOldInPre >= 95:
        popOld = polygonFC1[2]['properties'][popColumnOld]
        popPre = math.floor((indexPreInOld/100) * polygonFC2[2]['properties']['ges_lud'] * polygonFC2[2]['properties']['POW_km2'])
    elif indexPreInOld >= 95:
        popPre = polygonFC2[2]['properties'][popColumnPre]
        if (polygonFC2[2]['properties']['rodzaj'] == "ziemski"):
            popOld = math.floor((indexOldInPre/100) * polygonFC1[2]['properties']['o_ges_w'] * polygonFC1[2]['properties']['o_pow'])
        elif (polygonFC2[2]['properties']['rodzaj'] == "miejski"):
            popOld = math.floor((indexOldInPre/100) * polygonFC1[2]['properties']['o_ges_m'] * polygonFC1[2]['properties']['o_pow'])
    else:
        if (polygonFC2[2]['properties']['rodzaj'] == "ziemski"):
            popOld = math.floor((indexOldInPre/100) * polygonFC1[2]['properties']['o_ges_w'] * polygonFC1[2]['properties']['o_pow'])
            popPre = math.floor((indexPreInOld/100) * polygonFC2[2]['properties']['ges_lud'] * polygonFC2[2]['properties']['POW_km2'])
        elif (polygonFC2[2]['properties']['rodzaj'] == "miejski"):
            popOld = math.floor((indexOldInPre/100) * polygonFC1[2]['properties']['o_ges_m'] * polygonFC1[2]['properties']['o_pow'])
            popPre = math.floor((indexPreInOld/100) * polygonFC2[2]['properties']['ges_lud'] * polygonFC2[2]['properties']['POW_km2'])
   
    return popPre, popOld

def getPropertiesFromFiona(fc1, fc2, indexOldInPre, indexPreInOld, popPre, popOld, fc3 = 0, fc4 = 0):
    fcProperties = collections.OrderedDict()
    fc1Keys = fc1['properties'].keys()
    fc2Keys = fc2['properties'].keys()
    
    if fc3 == 0:
        for key in fc1Keys:
            fcProperties[key] = fc1['properties'][key]
    else:
        for key in fc1Keys:
            fcProperties[key] = fc1['properties'][key]
            fcProperties[key + '_1'] = fc3['properties'][key]

    if fc4 == 0:
        for key in fc2Keys:
            fcProperties[key] = fc2['properties'][key]
    else:
        for key in fc2Keys:
            fcProperties[key] = fc2['properties'][key]
            fcProperties[key + '_1'] = fc4['properties'][key]
    
    fcProperties['ind_old_in_pre'] = indexOldInPre
    fcProperties['ind_pre_in_old'] = indexPreInOld
    fcProperties['pre_lud'] = popPre
    fcProperties['old_lud'] = popOld

    return fcProperties
            
def getSchemaFromFiona(fc1, fc2, fc3 = False, fc4 = False):
    fcSchema = {'properties': collections.OrderedDict(), 'geometry': 'Polygon'}
    fc1Keys = fc1.schema['properties'].keys()
    fc2Keys = fc2.schema['properties'].keys()
    
    if fc3 == False:
        for key in fc1Keys:
            fcSchema['properties'][key] = fc1.schema['properties'][key]
    else:
        for key in fc1Keys:
            fcSchema['properties'][key] = fc1.schema['properties'][key]
            fcSchema['properties'][key + '_1'] = fc1.schema['properties'][key]

    if fc4 == False:
        for key in fc2Keys:
            fcSchema['properties'][key] = fc2.schema['properties'][key]
    else:
        for key in fc2Keys:
            fcSchema['properties'][key] = fc2.schema['properties'][key]
            fcSchema['properties'][key + '_1'] = fc2.schema['properties'][key]
    
    fcSchema['properties']['ind_old_in_pre'] = 'float:6.2'
    fcSchema['properties']['ind_pre_in_old'] = 'float:6.2'
    fcSchema['properties']['pre_lud'] = 'float:10'
    fcSchema['properties']['old_lud'] = 'float:10'
    return fcSchema