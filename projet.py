import numpy as np
import cv2
import math
from matplotlib import pyplot as plt

##########################
##### Constantes
##########################
DISTANCE = 10
PRECISION = 0.01
NB_POINTS = 150
SEUIL = 0.97
TAILLE_FENETRE = 30

##########################
##### Variables Globales
##########################

global image1,image2,gray1,gray2

##########################
##### Fonctions 
##########################
def CheckForLess(val ,image , x, y, height, width,tfenetre):
    
    for i in range(-tfenetre,tfenetre+1) :
        for j in range(-tfenetre,tfenetre+1) :
            absy = x+i
            ordo = y+j
            if(i>=0 and j>=0 and i<width and j<height and all(x < val for x in image[ordo][absy])):
                return True
    return False 


def couple_to_s(couple) :
    return "[" + couple[0][0] + ":" + couple[0][1] +"]"+"[" + couple[1][0] + ":" + couple[1][1] +"]" + "->" + couple[2]


    
def score(m1,m2,taille) :
    '''Calcule le score entre deux points'''
    global image1,image2,gray1,gray2
    #print("Num1" + str(m1))
    #print("Num1" + str(m2))

    height1, width1, channels1 = image1.shape
    height2, width2, channels2 = image2.shape
    #print("Num : " + str(height1) + " " + str(width1))
    #print("Num : " + str(height2) + " " + str(width2))

    sumNum = 0
    sumDen1 = 0
    sumDen2 = 0
    nb_pixel = 0
    for i in range(-taille,taille+1) :
        for j in range(-taille,taille+1) :
            if((m1[0]+i) >= 0 and (m1[1]+j) >= 0 and (m1[0]+i) < width1 and (m1[1]+j) < height1 and (m2[0]+i) >= 0 and (m2[1]+j) >= 0 and (m2[0]+i) < width2 and (m2[1]+j) < height2) :
                #print("num true")
                sumNum += ((int(gray1[m1[1]+j][m1[0]+i])-int(gray1[m1[1]][m1[0]]))*(int(gray2[m2[1]+j][m2[0]+i])- int(gray2[m2[1]][m2[0]])))
                sumDen1 += (((int(gray1[m1[1]+j][m1[0]+i]) - int(gray1[m1[1]][m1[0]])))**2)
                sumDen2 += (((int(gray2[m2[1]+j][m2[0]+i]) - int(gray2[m2[1]][m2[0]])))**2)
                nb_pixel +=1
                
    #print("numSum " + str(sum))
    return (sumNum/(nb_pixel**2))/(math.sqrt(sumDen1/(nb_pixel**2))*math.sqrt(sumDen2/(nb_pixel**2)))


##########################
##### Main
##########################

print("Lecture des images")
image1 = cv2.imread('./Images_Fragments/Lena2.png')
image2 = cv2.imread('./Images_Fragments/Lena1.png')
img1Rouge = image1.copy()
img2Rouge = image2.copy()
img1Save = image1.copy()
img2Save = image2.copy()

gray1 = cv2.cvtColor(image1,cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)


print("Calculs des coins")
corners = cv2.goodFeaturesToTrack(gray1,NB_POINTS,PRECISION,DISTANCE)
corners = np.int0(corners)
corners2 = cv2.goodFeaturesToTrack(gray2,NB_POINTS,PRECISION,DISTANCE)
corners2 = np.int0(corners2)

##Affichege des points sur les images
for i in corners:
    x,y = i.ravel()
    #print("P1 : x = " + str(x) + "  y = " + str(y))
    cv2.circle(image1,(x,y),3,(0,0,255),-1)
    cv2.circle(img1Rouge,(x,y),3,(0,0,255),-1)


for i in corners2:
    x,y = i.ravel()
    #print("P2 : x = " + str(x) + "  y = " + str(y))
    cv2.circle(image2,(x,y),3,(0,0,255),-1)
    cv2.circle(img2Rouge,(x,y),3,(0,0,255),-1)


print("Calcul des couples de points similaires")
couples_retenus = []
nbTotalCouple = len(corners) * len(corners2)
nbCoupleTraite = 0
for i in corners :
    couples_valides = []
    for j in corners2 :
            x1,y1 = i.ravel()
            x2,y2 = j.ravel()
            m1 = [x1,y1]
            m2 = [x2,y2]
            scorePoints = score(m1,m2,TAILLE_FENETRE)
            #print(scorePoints)
            if(scorePoints > SEUIL) :
                couples_valides.append((m1,m2,scorePoints))
                '''cv2.circle(image1,m1,3,(0,255,0),-1)
                cv2.circle(image2,m2,3,(0,255,0),-1)'''
            nbCoupleTraite = nbCoupleTraite+1


    ##On regarde dans tous les couples retenus le meilleur couple et on l'ajoute
    ##Cela évite les doublons de la première colonne
    if couples_valides != [] :
        couple_max = couples_valides[0]
        for c in couples_valides :
            couple_max = ( couple_max if (couple_max[2] > c[2]) else c )
        couples_retenus.append(couple_max);
    pourcentage = nbCoupleTraite/nbTotalCouple * 100
    print(str(round(pourcentage,2)) + "%")
    
##On enlève les possibles doublons de la deuxieme colonne
for couple in couples_retenus :
    couple_max = couple
    couple_supprime = []
    for j in range(couples_retenus.index(couple)+1,len(couples_retenus)) :
        if(couple_max[1] == couples_retenus[j][1]) :
            if (couple_max[2] >= couples_retenus[j][2]) :
                couple_supprime.append(couples_retenus[j])
            else :
                couple_supprime.append(couple_max)
                couple_max = couples_retenus[j]
    for csuprr in couple_supprime :
        #print(" Je supprime ")
        #print(csuprr)
        couples_retenus.remove(csuprr)
        

print("----------------------------")
##Affichages des points retenus sur l'image
for i in couples_retenus :
    cv2.circle(image1,tuple(i[0]),3,(0,255,0),-1)
    cv2.circle(image2,tuple(i[1]),3,(0,255,0),-1)
    print(i)

print("----------------------------")

if(len(couples_retenus) < 4) :
    print("Erreur, pas assez de points caractéristique")
    exit

##Affichage des images
height1, width1, channels = image1.shape
height2, width2, channels = image2.shape
h, status = cv2.findHomography(np.array([x[1] for x in couples_retenus]),np.array([x[0] for x in couples_retenus]),cv2.RANSAC)
imageTransfoCircles = cv2.warpPerspective(image2, h,(width2 + width1,height2 + height1))
imageTransfo = cv2.warpPerspective(img2Save, h,(width2 + width1,height2 + height1))

#cv2.imshow('partie1',image1)
#cv2.imshow('partie2',image2)
#cv2.imshow('partie2homographié',imageTransfo)
#print(imageTransfo)

imageRes = imageTransfo.copy()
for i in range(0,len(image1)) :
    for j in range(0,len(image1[i])) :
        imageRes[i][j] = img1Save[i][j]

####
## On coupe les bordures noirs
####
onlyBlack = True
widthRes = width2 + width1
while(onlyBlack and widthRes>0 ) :
    for i in range(0,height2 + height1) :
        if(not all(imageRes[i][widthRes-1] == [0,0,0])):
            onlyBlack = False
    if(onlyBlack) :
        widthRes = widthRes-1

onlyBlack = True
heightRes = height2 + height1
while(onlyBlack and heightRes>0 ) :
    for i in range(0,widthRes) :
        if(not all(imageRes[heightRes-1][i] == [0,0,0])):
            onlyBlack = False
    if(onlyBlack) :
        heightRes = heightRes-1

imageResFinale = []
imageResFinaleBis = []
for i in range(0,heightRes) :
    imageResFinale.append(imageRes[i][0:widthRes])

for i in range(0,height1) :
    imageResFinaleBis.append(imageRes[i][0:widthRes])

cv2.imwrite("./Resultat/partie1.jpg",image1)
cv2.imwrite("./Resultat/partie2.jpg",image2)
cv2.imwrite("./Resultat/partie1Rouge.jpg",img1Rouge)
cv2.imwrite("./Resultat/partie2Rouge.jpg",img2Rouge)
cv2.imwrite("./Resultat/partie2homographié.jpg",imageTransfoCircles)
cv2.imwrite("./Resultat/imageResultatavecnoir.jpg",imageTransfoCircles)
cv2.imwrite("./Resultat/imageResultat.jpg",np.float32(imageRes))
cv2.imwrite("./Resultat/imageResultatBis.jpg",np.float32(imageResFinaleBis))




cv2.waitKey(0)
        


