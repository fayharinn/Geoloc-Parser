#!/usr/bin/env python

# On importe les librairies qu'on va utiliser
from PIL import Image 
from PIL.ExifTags import TAGS
from PIL.ExifTags import GPSTAGS
import mimetypes
import os

#=============================

# On défini les fonctions qui seront utiles pour calculer les géolocs=================

def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")
        return

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]
    return geotagging


def get_decimal_from_dms(dms, ref):

    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    
    return round(degrees + minutes + seconds, 5)
def get_coordinates(geotags):
    if  "GPSLatitude" in geotags and "GPSLatitudeRef" in geotags and 'GPSLongitude' in geotags and 'GPSLongitudeRef' in geotags :

        lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])

        lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    else:
        print("No Latitude or Longitude.. pass")
        return

    return (lat,lon)

def get_extensions_for_type(general_type):
    for ext in mimetypes.types_map:
        if mimetypes.types_map[ext].split('/')[0] == general_type:
            yield ext


path = "."
mimetypes.init()
IMAGE = tuple(get_extensions_for_type('image'))

def getListOfFiles(dirName):
    # create a list of file and sub directories 
    # names in the given directory 
    listOfFile = os.listdir(dirName)
    allFiles = []
    # Iterate over all the entries
    for entry in listOfFile:
        # Create full path
        fullPath = os.path.join(dirName, entry)
        # If entry is a directory then get the list of files in this directory 
        if os.path.isdir(fullPath):
            #print("Digging in "+fullPath)
            allFiles.extend(getListOfFiles(fullPath))
        else:
            extension = fullPath.split(".")
            if len(extension)>1:
                extension = "."+extension[-1]
            if extension in IMAGE :
                allFiles.append(fullPath)
                
    return allFiles


#============================= C'est le début de notre programme ===============

print("============== DOX Geoloc 1.0 ==============")
print("Extensions to analyse : ")
print(IMAGE)
print("Start...")
print("Getting File Names from the actual directory and subdirs ...")
onlyfiles = getListOfFiles(path) # on stock la liste des images où on souhaite extraire des données exif dans la variable onlyfiles
print("Found "+str(len(onlyfiles))+" images") # on affiche la taille de la liste onlyfiles pour dire combien d'images notre fonction a trouvé
print("Calculating location now ...")
dico= {} # on crée un dictionnaire, équivalent à un hashmap de java

for file in onlyfiles:
    
    try: # on teste la ligne en dessous
        exif = get_exif(file)
    except : # s'il y a une erreur dans la récupération des données exif, on skip l'image
        #print("pass "+file)
        continue


    try:
        geotags = get_geotagging(exif)
    except ValueError: # s'il y a une erreur dans la récupération des données geotag, on skip l'image
        #print("No exif for "+file)
        continue
    try:

        coordinates = get_coordinates(geotags) # on appelle la fonction get_coordinates avec pour argument geotags
        if(coordinates != None): # si on a bien récupéré des coordonnées, donc que la variable coordinates est diff de None, on ajoute les coordonnées dans notre dico
            # rappel : dico équivalent à une table de hachage
            dico[file]= coordinates
    except:
        pass
        #print("pass "+file+" (no coordinate) ["+geotags+"]")

print(dico)
print("========================================================")
print("                       DONE                             ")
print("========================================================")
print("Found "+str(len(onlyfiles))+" images")
print("Found "+str(len(dico))+" locations")

# L'analyse étant terminée, on stock les données trouvées dans un fichier CSV
file = open("output.csv","w") # on crée le fichier output.csv avec open avec comme argument w pour write
file.write("Fichier;Latref;Latitude;Longref;Longitude\n") # on écrit cette ligne dans le fichier output
for image in dico: # on parcours notre dictionnaire et on écrit chaque nom d'image + géoloc trouvée dans une ligne
    file.write(image+";;"+str(dico[image][0])+";;"+str(dico[image][1])+"\n")
file.close()
print("Result saved as a CSV in output.csv")
print("========================================================")
print("========================================================")

input("Press Enter to continue")
