# -*- coding: utf-8 -*-
'''
    C:\Studia\licencjat\wejście\Powiaty_1937.shp
    C:\Studia\licencjat\wejście\Powiaty_2019.shp
    tab_test2.txt
    nazwa
    JPT_NAZWA_
    
    C:\Studia\licencjat\wyniki\lud.shp
    C:\Studia\licencjat\wyniki\txt\lud.txt
    C:\\Studia\\licencjat\\prezentacja5\\tabele
'''
import fiona
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon
from shapely.geometry import mapping
import math
import time
import sys
import collections
import itertools
import threading
t1 = time.time()

def get_polygon_from_feature_class(fc_pol):
    geom_type = fc_pol['geometry']['type']
    geom_coor = fc_pol['geometry']['coordinates']
    geom_no_part = len(geom_coor)
    
    if geom_type == 'Polygon':
        #Poligon bez pierscieni
        if geom_no_part == 1:
            shapely_pol =  Polygon(geom_coor[0])
        #Poligon z pierscieniami
        else:
            shapely_pol =  Polygon(geom_coor[0], geom_coor[1:])

    elif geom_type == 'MultiPolygon':
        pol_list = []
        for i in range(geom_no_part):
            geom_no_ring = len(geom_coor[i])
            #Multipoligon bez pierscieni
            if geom_no_ring == 1:
                shapely_multi_pol =  Polygon(geom_coor[i][0])
            #Multipoligon z pierscieniami
            else:
                shapely_multi_pol =  Polygon(geom_coor[i][0], geom_coor[i][1:])
            pol_list.append(shapely_multi_pol)
        shapely_pol = MultiPolygon(pol_list)

    return shapely_pol

def get_column_names_from_feature_class(fc_column_names):
    fc_column_names_print = ""
    list_column_names = []
    for name in fc_column_names:
        list_column_names.append(name)
        fc_column_names_print += "{},".format(name)
    return fc_column_names_print

def get_column_name_from_feature_class(fc_column_names):
    fc_column_names_print = ""
    list_column_names = []
    for name in fc_column_names:
        list_column_names.append(name)
        fc_column_names_print += "\t{} - {}\n".format(len(list_column_names), name)
    fc_column_names_print += "Wpisz liczbę która, odpowiada kolumnie w której znajduje się liczba ludności dla warstwy: "
    fc_col_name = int(input(fc_column_names_print))
    fc_column_name = list_column_names[fc_col_name-1]
    return fc_column_name

def set_column_value_to_txt(list_column_name_1, list_column_name_2, pol_1, pol_2, ind_old_in_present, ind_present_in_old, pre_lud, old_lud, list_column_name_3 = 0, list_column_name_4 = 0, pol_3 = 0, pol_4 = 0):
    result_value = ""
    for column_name in list_column_name_1:
        result_value += str(pol_1[2]["properties"][column_name]) + ","
    if list_column_name_3 != 0 and pol_3 != 0:
        for column_name in list_column_name_3:
            result_value += str(pol_3[2]["properties"][column_name]) + ","
    for column_name in list_column_name_2:
        result_value += str(pol_2[2]["properties"][column_name]) + ","
    if list_column_name_4 != 0 and pol_4 != 0:
        for column_name in list_column_name_4:
            result_value += str(pol_4[2]["properties"][column_name]) + ","
    result_value += str(ind_old_in_present) + ","
    result_value += str(ind_present_in_old) + ","
    result_value += str(pre_lud) + ","
    result_value += str(old_lud) + "\n"
    return result_value

def get_properties_from_feature_class(fc_1, fc_2, menu_option):
    fc_end_prop = fc_1.schema
    fc_1_key = fc_end_prop['properties'].keys()
    fc_1_val = fc_end_prop['properties'].values()
    fc_2_key = fc_2.schema['properties'].keys()
    fc_2_val = fc_2.schema['properties'].values()
    
    fc_end_key_list = []
    fc_end_val_list = []
            
    for key in fc_1_key:
        fc_end_key_list.append(key)
        if menu_option == 2 or menu_option == 3:
            fc_end_key_list.append(key+"_1")
    for val in fc_1_val:
        fc_end_val_list.append(val)
        if menu_option == 2 or menu_option == 3:
            fc_end_val_list.append(val)
    for key in fc_2_key:
        fc_end_key_list.append(key)
        if menu_option == 2 or menu_option == 4:
            fc_end_key_list.append(key+"_1")
    for val in fc_2_val:
        fc_end_val_list.append(val)
        if menu_option == 2 or menu_option == 4:
            fc_end_val_list.append(val)
            
    fc_end_dict = {}
    for i in range(len(fc_end_key_list)):
        fc_end_dict[fc_end_key_list[i]] = fc_end_val_list[i]
    
    fc_end_dict['ind_old_in_pre'] = 'float:6.2'
    fc_end_dict['ind_pre_in_old'] = 'float:6.2'
    fc_end_dict['pre_lud'] = 'float:10'
    fc_end_dict['old_lud'] = 'float:10'
    
    fc_end_prop['properties'] = collections.OrderedDict(fc_end_dict)
    return fc_end_prop

def get_properties_from_shapely(fc_1, fc_2, ind_old_in_present, ind_present_in_old, old_lud, pre_lud, menu_option, fc_3 = 0, fc_4 = 0):
    fc_1_key = fc_1['properties'].keys()
    fc_1_val = fc_1['properties'].values()
    fc_2_key = fc_2['properties'].keys()
    fc_2_val = fc_2['properties'].values()
    
    fc_end_key_list = []
    fc_end_val_list = []
    
    if menu_option == 1:
        for key in fc_1_key:
            fc_end_key_list.append(key)
        for val in fc_1_val:
            fc_end_val_list.append(val)
        for key in fc_2_key:
            fc_end_key_list.append(key)
        for val in fc_2_val:
            fc_end_val_list.append(val)
    
    if menu_option == 2 or menu_option == 3:
        fc_3_val = fc_3['properties'].values()
        fc_1_val_list = []
        fc_3_val_list = []
        
        for key in fc_1_key:
            fc_end_key_list.append(key)
            fc_end_key_list.append(key+"_1")
    
        for val in fc_1_val:
            fc_1_val_list.append(val)
        
        
        for val in fc_3_val:
            fc_3_val_list.append(val)
        
        for i in range(len(fc_1_val_list)):
            fc_end_val_list.append(fc_1_val_list[i])
            fc_end_val_list.append(fc_3_val_list[i])
    
    if menu_option == 3:
        for key in fc_2_key:
            fc_end_key_list.append(key)
        for val in fc_2_val:
            fc_end_val_list.append(val)
            
    if menu_option == 4:
        for key in fc_1_key:
            fc_end_key_list.append(key)
        for val in fc_1_val:
            fc_end_val_list.append(val)
    
    if menu_option == 2 or menu_option == 4:
        fc_4_val = fc_4['properties'].values()
        fc_2_val_list = []
        fc_4_val_list = []
        
        for key in fc_2_key:
            fc_end_key_list.append(key)
            fc_end_key_list.append(key+"_1")
    
        for val in fc_2_val:
            fc_2_val_list.append(val)
        
        for val in fc_4_val:
            fc_4_val_list.append(val)
        
        for i in range(len(fc_2_val_list)):
            fc_end_val_list.append(fc_2_val_list[i])
            fc_end_val_list.append(fc_4_val_list[i])
            
    fc_end_dict = {}
    for i in range(len(fc_end_key_list)):
        fc_end_dict[fc_end_key_list[i]] = fc_end_val_list[i]
    
    fc_end_dict['ind_old_in_pre'] = ind_old_in_present
    fc_end_dict['ind_pre_in_old'] = ind_present_in_old
    fc_end_dict['pre_lud'] = pre_lud
    fc_end_dict['old_lud'] = old_lud
    
    fc_end_prop = collections.OrderedDict(fc_end_dict)
    return fc_end_prop

def mergesort(list_1): #Sortowanie merge
    if len(list_1)>1:
        mid = len(list_1)//2
        list_left = list_1[:mid]
        list_right = list_1[mid:]
        mergesort(list_left)
        mergesort(list_right)
        i = 0
        j = 0
        k = 0
        while i<len(list_left) and j<len(list_right):
            if list_left[i][0][0]<list_right[j][0][0]:
                list_1[k] = list_left[i]
                i += 1
                k += 1
            else:
                list_1[k] = list_right[j]
                j += 1
                k += 1
        while i<len(list_left):
            list_1[k] = list_left[i]
            i += 1
            k += 1
        while j<len(list_right):
            list_1[k] = list_right[j]
            j += 1
            k += 1

def comparasion_one_to_one(pol1, pol2):
    if pol1.intersects(pol2):
        pol_inter = pol1.intersection(pol2)
        old_in_present_per = pol_inter.area/pol1.area*100
        present_in_old_per = pol_inter.area/pol2.area*100
        return old_in_present_per, present_in_old_per, pol_inter
    else:
        return 0, 0, 0

def create_duo_polygon_list(list_pol):
    list_pol_duo = []
    for i, shapely_pol_1_1 in enumerate(list_pol):
        for j, shapely_pol_1_2 in enumerate(list_pol):
            if j < i:
                if shapely_pol_1_1[1].intersects(shapely_pol_1_2[1]):
                    pol_duo = shapely_pol_1_1[1].union(shapely_pol_1_2[1])
                    list_pol_duo.append([pol_duo.bounds, pol_duo, i, j])
    return list_pol_duo

def comparasion_pop_stat(shapely_pol_1, shapely_pol_2, o_lud, lud, ind_old_in_present, ind_present_in_old, shapely_pol_3 = [0,0,{'properties':{'o_lud':0}}], shapely_pol_4 = [0,0,{'properties':{'lud':0}}]):
    if(ind_old_in_present >= 95 and ind_present_in_old >= 95):
        old_lud = shapely_pol_1[2]['properties'][o_lud] + shapely_pol_3[2]['properties'][o_lud]
        pre_lud = shapely_pol_2[2]['properties'][lud] + shapely_pol_4[2]['properties'][lud]
    elif(ind_old_in_present >= 95):
        old_lud = shapely_pol_1[2]['properties'][o_lud] + shapely_pol_3[2]['properties'][o_lud]
        pre_lud = math.floor((ind_present_in_old/100) * (shapely_pol_2[2]['properties'][lud] + shapely_pol_4[2]['properties'][lud]))
    elif(ind_present_in_old >= 95): 
        old_lud = math.floor((ind_old_in_present/100) * (shapely_pol_1[2]['properties'][o_lud] + shapely_pol_3[2]['properties'][o_lud]))
        pre_lud = shapely_pol_2[2]['properties'][lud] + shapely_pol_4[2]['properties'][lud]
    else:
        old_lud = math.floor((ind_old_in_present/100) * (shapely_pol_1[2]['properties'][o_lud] + shapely_pol_3[2]['properties'][o_lud]))
        pre_lud = math.floor((ind_present_in_old/100) * (shapely_pol_2[2]['properties'][lud] + shapely_pol_4[2]['properties'][lud]))
    return pre_lud, old_lud

def comparasion_pop_stat_2(shapely_pol_1, shapely_pol_2, o_lud, lud, ind_old_in_present, ind_present_in_old):
    if(ind_old_in_present >= 95 and ind_present_in_old >= 95):
        old_lud = shapely_pol_1[2]['properties'][o_lud]
        pre_lud = shapely_pol_2[2]['properties'][lud]
    elif ind_old_in_present >= 95:
        old_lud = shapely_pol_1[2]['properties'][o_lud]
        pre_lud = math.floor((ind_present_in_old/100) * shapely_pol_2[2]['properties']['ges_lud'] * shapely_pol_2[2]['properties']['POW_km2'])
    elif ind_present_in_old >= 95:
        pre_lud = shapely_pol_2[2]['properties'][lud]
        if (shapely_pol_2[2]['properties']['rodzaj'] == "ziemski"):
            old_lud = math.floor((ind_old_in_present/100) * shapely_pol_1[2]['properties']['o_ges_w'] * shapely_pol_1[2]['properties']['o_pow'])
        elif (shapely_pol_2[2]['properties']['rodzaj'] == "miejski"):
            old_lud = math.floor((ind_old_in_present/100) * shapely_pol_1[2]['properties']['o_ges_m'] * shapely_pol_1[2]['properties']['o_pow'])
    else:
        if (shapely_pol_2[2]['properties']['rodzaj'] == "ziemski"):
            old_lud = math.floor((ind_old_in_present/100) * shapely_pol_1[2]['properties']['o_ges_w'] * shapely_pol_1[2]['properties']['o_pow'])
            pre_lud = math.floor((ind_present_in_old/100) * shapely_pol_2[2]['properties']['ges_lud'] * shapely_pol_2[2]['properties']['POW_km2'])
        elif (shapely_pol_2[2]['properties']['rodzaj'] == "miejski"):
            old_lud = math.floor((ind_old_in_present/100) * shapely_pol_1[2]['properties']['o_ges_m'] * shapely_pol_1[2]['properties']['o_pow'])
            pre_lud = math.floor((ind_present_in_old/100) * shapely_pol_2[2]['properties']['ges_lud'] * shapely_pol_2[2]['properties']['POW_km2'])
   
    return pre_lud, old_lud

done = False
def animate():
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if done:
            break
        sys.stdout.write('\rObliczanie ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rUdało się!     ')

def main():
    fc_file_name_1 = input("Podaj nazwę (lub nazwę wraz ze sciezką) pliku zawierającego dawne granice administracyjne: ")
    fc_file_name_2 = input("Podaj nazwę (lub nazwę wraz ze sciezką) pliku zawierającego obecne granice administracyjne: ")

    try:
        result_file_name = input("Podaj nazwę (lub nazwę wraz ze sciezką) pliku wynikowego wraz z rozszerzeniem (.txt lub .shp): ")
        while result_file_name[result_file_name.index('.'):] != '.txt' and result_file_name[result_file_name.index('.'):] != '.shp':
            result_file_name = input("Podana lokalizacja nie ma rozszerzenia albo jest ono napisane błędnie. Podaj nazwę (lub nazwę wraz ze sciezką) pliku wynikowego wraz z rozszerzeniem (.txt lub .shp): ")    
    except ValueError:
        sys.exit("W nazwie nie znajduje się \".\"")

    try:
        menu_option = int(input('''    1 - porównywanie jednostek administracyjych jeden do jeden
    2 - porównywanie jednostek administracyjych dwa do dwa
    3 - porównywanie jednostek administracyjych dwa do jeden
    4 - porównywanie jednostek administracyjych jeden do dwa
Wpisz liczbę odpowiadającą metodzie którą chcesz wykonać: '''))
        while menu_option < 1 or menu_option > 4:
            menu_option = int(input('''Wpisana liczba jest spoza zakresu
    1 - porównywanie jednostek administracyjych jeden do jeden
    2 - porównywanie jednostek administracyjych dwa do dwa
    3 - porównywanie jednostek administracyjych dwa do jeden
    4 - porównywanie jednostek administracyjych jeden do dwa
Wpisz liczbę odpowiadającą metodzie którą chcesz wykonać: '''))
    except ValueError:
        sys.exit("Błędny format liczby.")

    if menu_option == 1:
        try:
            method_option = int(input('''    1 - Obliczanie liczby ludnosci jedynie na podstawie geometrii obszarów
    2 - Obliczanie liczby ludnosci jedynie na podstawie geometrii obszarów i gęstosci zaludnienia
Wpisz liczbę odpowiadającą metodzie którą chcesz wykonać: '''))
            while method_option < 1 or method_option > 2:
                method_option = int(input('''Wpisana liczba jest spoza zakresu
    1 - Obliczanie liczby ludnosci na podstawie geometrii obszarów
    2 - Obliczanie liczby ludnosci na podstawie geometrii obszarów i gęstosci zaludnienia
Wpisz liczbę odpowiadającą metodzie którą chcesz wykonać: '''))
        except ValueError:
            sys.exit("Błędny format liczby.")

    try:
        min_inter_per = float(input("Podaj minimalny procent (od 0 do 100) w jakim muszą się przecinać warstwy, aby zostały uwzględnione: "))
        while min_inter_per < 0 or min_inter_per > 100:
            min_inter_per = float(input('''Wpisana liczba jest spoza zakresu
Podaj minimalny procent w jakim muszą się przecinać warstwy, aby zostały uwzględnione: '''))
    except ValueError:
        sys.exit("Błędny format liczby.")

    list_pol_1 = []
    list_pol_2 = []
    fc_end_prop = ''
    fc_column_name_1 = ''
    fc_column_name_2 = ''

    with fiona.open(fc_file_name_1, "r", encoding="utf-8") as fc_1:
        with fiona.open(fc_file_name_2, "r", encoding="utf-8") as fc_2:

            fc_end_prop = get_properties_from_feature_class(fc_1, fc_2, menu_option)
            fc_end_driver = fc_1.driver
            fc_end_crs = fc_1.crs

            fc_column_names_1 = fc_1[0]["properties"]
            fc_column_name_1 = get_column_name_from_feature_class(fc_column_names_1)
        
            fc_column_names_2 = fc_2[0]["properties"]
            fc_column_name_2 = get_column_name_from_feature_class(fc_column_names_2)
        
            for fc_pol_1 in fc_1:
                shapely_pol_1 = get_polygon_from_feature_class(fc_pol_1)
                list_pol_1.append([shapely_pol_1.bounds, shapely_pol_1, fc_pol_1])
            
            for fc_pol_2 in fc_2:
                shapely_pol_2 = get_polygon_from_feature_class(fc_pol_2)
                list_pol_2.append([shapely_pol_2.bounds, shapely_pol_2, fc_pol_2])

    mergesort(list_pol_1)
    mergesort(list_pol_2)
    
    
    t = threading.Thread(target=animate)
    t.start()
    
    if result_file_name[result_file_name.index('.'):] == '.txt':
        with open(result_file_name,"w") as result_file:
            t3 = time.time()
    
            if menu_option == 1:
                column_trigger = 0
                for shapely_pol_1 in list_pol_1:
                    for shapely_pol_2 in list_pol_2:
                        if column_trigger == 0:
                            result_column_name_1 = get_column_names_from_feature_class(shapely_pol_1[2]["properties"])
                            result_column_name_2 = get_column_names_from_feature_class(shapely_pol_2[2]["properties"])
                            result_column_name = result_column_name_1 + result_column_name_2 + "ind_old_in,ind_pre_in,pre_lud,old_lud\n"
                            column_trigger += 1
                            result_file.write(result_column_name)
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(shapely_pol_1[1], shapely_pol_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            if method_option == 1:
                                pre_lud, old_lud = comparasion_pop_stat(shapely_pol_1, shapely_pol_2, fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old)
                            else:
                                pre_lud, old_lud = comparasion_pop_stat_2(shapely_pol_1, shapely_pol_2, fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old)
                            list_column_name_1 =  result_column_name_1.strip().split(",")
                            list_column_name_1.pop(-1)
                            list_column_name_2 =  result_column_name_2.strip().split(",")
                            list_column_name_2.pop(-1)
                            result_value = set_column_value_to_txt(list_column_name_1, list_column_name_2, shapely_pol_1, shapely_pol_2, ind_old_in_present, ind_present_in_old, pre_lud, old_lud)
                            result_file.write(result_value)

            elif menu_option == 2:
                list_pol_duo_1 = create_duo_polygon_list(list_pol_1)
                list_pol_duo_2 = create_duo_polygon_list(list_pol_2)
                
                column_trigger = 0
                for pol_duo_1 in list_pol_duo_1:
                    for pol_duo_2 in list_pol_duo_2:
                        if (column_trigger == 0):
                            result_column_name_1 = get_column_names_from_feature_class(list_pol_1[pol_duo_1[2]][2]["properties"])
                            result_column_name_2 = get_column_names_from_feature_class(list_pol_2[pol_duo_2[2]][2]["properties"])
                            result_column_name_3 = get_column_names_from_feature_class(list_pol_1[pol_duo_1[3]][2]["properties"])
                            result_column_name_4 = get_column_names_from_feature_class(list_pol_2[pol_duo_2[3]][2]["properties"])
                            result_column_name = result_column_name_1 + result_column_name_2 + result_column_name_3 + result_column_name_4 + "ind_old_in,ind_pre_in,pre_lud,old_lud\n"
                            column_trigger += 1
                            result_file.write(result_column_name)
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(pol_duo_1[1], pol_duo_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            pre_lud, old_lud = comparasion_pop_stat(list_pol_1[pol_duo_1[2]], list_pol_2[pol_duo_2[2]], fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old, list_pol_1[pol_duo_1[3]], list_pol_2[pol_duo_2[3]])
                            list_column_name_1 =  result_column_name_1.strip().split(",")
                            list_column_name_1.pop(-1)
                            list_column_name_2 =  result_column_name_2.strip().split(",")
                            list_column_name_2.pop(-1)
                            list_column_name_3 =  result_column_name_3.strip().split(",")
                            list_column_name_3.pop(-1)
                            list_column_name_4 =  result_column_name_4.strip().split(",")
                            list_column_name_4.pop(-1)
                            result_value = set_column_value_to_txt(list_column_name_1, list_column_name_2, list_pol_1[pol_duo_1[2]], list_pol_2[pol_duo_2[2]], ind_old_in_present, ind_present_in_old, pre_lud, old_lud, list_column_name_3, list_column_name_4, list_pol_1[pol_duo_1[3]], list_pol_2[pol_duo_2[3]])
                            result_file.write(result_value)

            elif menu_option == 3:
                list_pol_duo_1 = create_duo_polygon_list(list_pol_1)
                
                column_trigger = 0
                for pol_duo_1 in list_pol_duo_1:
                    for shapely_pol_2 in list_pol_2:
                        if (column_trigger == 0):
                            result_column_name_1 = get_column_names_from_feature_class(list_pol_1[pol_duo_1[2]][2]["properties"])
                            result_column_name_2 = get_column_names_from_feature_class(shapely_pol_2[2]["properties"])
                            result_column_name_3 = get_column_names_from_feature_class(list_pol_1[pol_duo_1[3]][2]["properties"])
                            result_column_name = result_column_name_1 + result_column_name_2 + result_column_name_3 + "ind_old_in,ind_pre_in,pre_lud,old_lud\n"
                            column_trigger += 1
                            result_file.write(result_column_name)
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(pol_duo_1[1], shapely_pol_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            pre_lud, old_lud = comparasion_pop_stat(list_pol_1[pol_duo_1[2]], shapely_pol_2, fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old, list_pol_1[pol_duo_1[3]])
                            list_column_name_1 =  result_column_name_1.strip().split(",")
                            list_column_name_1.pop(-1)
                            list_column_name_2 =  result_column_name_2.strip().split(",")
                            list_column_name_2.pop(-1)
                            list_column_name_3 =  result_column_name_3.strip().split(",")
                            list_column_name_3.pop(-1)
                            result_value = set_column_value_to_txt(list_column_name_1, list_column_name_2, list_pol_1[pol_duo_1[2]], shapely_pol_2, ind_old_in_present, ind_present_in_old, pre_lud, old_lud, list_column_name_3, 0, list_pol_1[pol_duo_1[3]])
                            result_file.write(result_value)
    
            elif menu_option == 4:
                list_pol_duo_2 = create_duo_polygon_list(list_pol_2)
                
                column_trigger = 0
                for shapely_pol_1 in list_pol_1:
                    for pol_duo_2 in list_pol_duo_2:
                        if (column_trigger == 0):
                            result_column_name_1 = get_column_names_from_feature_class(shapely_pol_1[2]["properties"])
                            result_column_name_2 = get_column_names_from_feature_class(list_pol_2[pol_duo_2[2]][2]["properties"])
                            result_column_name_4 = get_column_names_from_feature_class(list_pol_2[pol_duo_2[3]][2]["properties"])
                            result_column_name = result_column_name_1 + result_column_name_2 + result_column_name_4 + "ind_old_in,ind_pre_in,pre_lud,old_lud\n"
                            column_trigger += 1
                            result_file.write(result_column_name)
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(shapely_pol_1[1], pol_duo_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            pre_lud, old_lud = comparasion_pop_stat(shapely_pol_1, list_pol_2[pol_duo_2[2]], fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old, shapely_pol_4 = list_pol_2[pol_duo_2[3]])
                            list_column_name_1 =  result_column_name_1.strip().split(",")
                            list_column_name_1.pop(-1)
                            list_column_name_2 =  result_column_name_2.strip().split(",")
                            list_column_name_2.pop(-1)
                            list_column_name_4 =  result_column_name_4.strip().split(",")
                            list_column_name_4.pop(-1)
                            result_value = set_column_value_to_txt(list_column_name_1, list_column_name_2, shapely_pol_1, list_pol_2[pol_duo_2[2]], ind_old_in_present, ind_present_in_old, pre_lud, old_lud, 0, list_column_name_4, 0, list_pol_2[pol_duo_2[3]])
                            result_file.write(result_value)
        t2 = time.time()
        return t1, t2, t3
    
    elif result_file_name[result_file_name.index('.'):] == '.shp':
        with fiona.open(result_file_name, "w", 
                        driver = fc_end_driver, 
                        crs = fc_end_crs,
                        schema = fc_end_prop, 
                        encoding="utf-8") as fc_end:
            t3 = time.time()
            if menu_option == 1:
                for shapely_pol_1 in list_pol_1:
                    for shapely_pol_2 in list_pol_2:
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(shapely_pol_1[1], shapely_pol_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            if method_option == 1:
                                pre_lud, old_lud = comparasion_pop_stat(shapely_pol_1, shapely_pol_2, fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old)
                            else:
                                pre_lud, old_lud = comparasion_pop_stat_2(shapely_pol_1, shapely_pol_2, fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old)
                            fc_end_prop = get_properties_from_shapely(shapely_pol_1[2], shapely_pol_2[2], ind_old_in_present, ind_present_in_old, old_lud, pre_lud, menu_option, 0, 0)
                            feature = {
                                "geometry" : mapping(pol_inter),
                                "properties" : fc_end_prop,
                                }
                            fc_end.write(feature)
            
            if menu_option == 2:
                list_pol_duo_1 = create_duo_polygon_list(list_pol_1)
                list_pol_duo_2 = create_duo_polygon_list(list_pol_2)
                
                for pol_duo_1 in list_pol_duo_1:
                    for pol_duo_2 in list_pol_duo_2:
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(pol_duo_1[1], pol_duo_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            pre_lud, old_lud = comparasion_pop_stat(list_pol_1[pol_duo_1[2]], list_pol_2[pol_duo_2[2]], fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old, list_pol_1[pol_duo_1[3]], list_pol_2[pol_duo_2[3]])
                            fc_end_prop = get_properties_from_shapely(list_pol_1[pol_duo_1[2]][2], list_pol_2[pol_duo_2[2]][2], ind_old_in_present, ind_present_in_old,  old_lud, pre_lud, menu_option, list_pol_1[pol_duo_1[3]][2], list_pol_2[pol_duo_2[3]][2])
                            if mapping(pol_inter)['type'] == 'GeometryCollection':
                                pol_inter_multi = []
                                
                                for geom_el in pol_inter:
                                    if geom_el is Polygon:
                                        pol_inter_multi.append(geom_el)
                                pol_inter = MultiPolygon(pol_inter_multi)
                            
                            feature = {
                                "geometry" : mapping(pol_inter),
                                "properties" : fc_end_prop,
                                }
                            fc_end.write(feature)
                            
            if menu_option == 3:
                list_pol_duo_1 = create_duo_polygon_list(list_pol_1)
                
                for pol_duo_1 in list_pol_duo_1:
                    for shapely_pol_2 in list_pol_2:
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(pol_duo_1[1], shapely_pol_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            pre_lud, old_lud = comparasion_pop_stat(list_pol_1[pol_duo_1[2]], shapely_pol_2, fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old, list_pol_1[pol_duo_1[3]])
                            fc_end_prop = get_properties_from_shapely(list_pol_1[pol_duo_1[2]][2], shapely_pol_2[2], ind_old_in_present, ind_present_in_old, old_lud, pre_lud, menu_option, list_pol_1[pol_duo_1[3]][2])
                            if mapping(pol_inter)['type'] == 'GeometryCollection':
                                pol_inter_multi = []
                                
                                for geom_el in pol_inter:
                                    if geom_el is Polygon:
                                        pol_inter_multi.append(geom_el)
                                pol_inter = MultiPolygon(pol_inter_multi)
                            
                            feature = {
                                "geometry" : mapping(pol_inter),
                                "properties" : fc_end_prop,
                                }
                            fc_end.write(feature)

            if menu_option == 4:
                list_pol_duo_2 = create_duo_polygon_list(list_pol_2)
                for shapely_pol_1 in list_pol_1:
                    for pol_duo_2 in list_pol_duo_2:
                        ind_old_in_present, ind_present_in_old, pol_inter = comparasion_one_to_one(shapely_pol_1[1], pol_duo_2[1])
                        if(ind_old_in_present > min_inter_per and ind_present_in_old > min_inter_per):
                            pre_lud, old_lud = comparasion_pop_stat(shapely_pol_1, list_pol_2[pol_duo_2[2]], fc_column_name_1, fc_column_name_2, ind_old_in_present, ind_present_in_old, shapely_pol_4 = list_pol_2[pol_duo_2[3]])
                            fc_end_prop = get_properties_from_shapely(shapely_pol_1[2], list_pol_2[pol_duo_2[2]][2], ind_old_in_present, ind_present_in_old, old_lud, pre_lud, menu_option, 0, list_pol_2[pol_duo_2[3]][2])
                            if mapping(pol_inter)['type'] == 'GeometryCollection':
                                pol_inter_multi = []
                                
                                for geom_el in pol_inter:
                                    if geom_el is Polygon:
                                        pol_inter_multi.append(geom_el)
                                pol_inter = MultiPolygon(pol_inter_multi)
                            
                            feature = {
                                "geometry" : mapping(pol_inter),
                                "properties" : fc_end_prop,
                                }
                            fc_end.write(feature)

        t2 = time.time()
        return t1, t2, t3
        

t1, t2, t3 = main()
done = True
print("\nObliczenia wykonywały się {} s. Program wykonywał się w czasie {} s.".format(t2-t3, t2-t1))