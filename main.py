# -*- coding: utf-8 -*-
"""
Created on Thu Oct 13 17:25:25 2022

@author: berezo


./input/Powiaty_1937.shp
./input/Powiaty_2019.shp
"""
import sys
import options

def main():
    fcPath1 = input('Give the name (or name including path) of the file containing the former administrative boundaries: ')
    fcPath2 = input('Provide the name (or name including path) of the file containing the current administrative boundaries: ')
    optionMenu = input('\t1 - one-to-one comparison of administrative units\n\t2 - two-to-two comparison of administrative units\n\t3 - two-to-one comparison of administrative units\n\t4 - one-to-two comparison of administrative units\nEnter the number corresponding to the method you want to perform: ')
    while optionMenu not in ['1','2','3','4']:
        optionMenu = input('\t1 - one-to-one comparison of administrative units\n\t2 - two-to-two comparison of administrative units\n\t3 - two-to-one comparison of administrative units\n\t4 - one-to-two comparison of administrative units\nInvalid key. Enter the number corresponding to the method you want to perform: ')
    
    try:
        minIntersect = float(input('Specify the minimum percentage (from 0 to 100) in which the layers must intersect to be included: '))
        while minIntersect < 0 or minIntersect > 100:
            minIntersect = float(input('Wpisana liczba jest spoza zakresu. Podaj minimalny procent w jakim muszą się przecinać warstwy, aby zostały uwzględnione: '))
    except ValueError:
        sys.exit("Błędny format liczby.")
        
    fcPathResult = input("Enter the name (or name including path) of the resulting file together with the extension (.txt or .shp): ")
    while fcPathResult[-3:] not in ['txt', 'shp']:
        fcPathResult = input("The location given does not have an extension or it is misspelled. Enter the name (or name including path) of the resulting file together with the extension (.txt or .shp): ")
    
    fc1 = options.openFC(fcPath1)
    fc2 = options.openFC(fcPath2)  
    schema, features = options.doComparisonMethod(optionMenu, fc1, fc2, minIntersect)
    
    if fcPathResult[-3:] == 'shp':
        options.saveFC(fcPathResult, fc1, schema, features)
    elif fcPathResult[-3:] == 'txt':
        options.saveTXT(fcPathResult, features)
    
if __name__ == '__main__':
    main()