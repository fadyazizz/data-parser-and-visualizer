import xml.etree.cElementTree as ET
from skimage.draw import polygon
import xml.etree.ElementTree as E
import svgwrite
import copy
from xml.dom import minidom
import numpy as np
import cv2

def main():

    imgs_list = open('cubicasa5k/train.txt', 'r').readlines()
    for f in imgs_list:
        parse(f)

def parse(path):
    svg = minidom.parse('cubicasa5k'+path[:-1]+'model.svg')

    im = cv2.imread('cubicasa5k' + path[:-1] + 'F1_scaled.png')
    h, w, c = im.shape

    width=w
    height=h
    x_res, y_res = [], []
    results = np.array([])
    orientation = np.array([])
    for e in svg.getElementsByTagName('g'):

        id = e.getAttribute('id')

        #dont forget to add or
        if id == "Wall":


            x, y, orient = getBBox(e)
            if orient=='v' or orient=='h':
                segmentWallX, segmentWallY = segmentWall(e)
                count=0
                for l in segmentWallX:
                    x_res.append(l)
                    y_res.append(segmentWallY[count])
                    results=np.append(results,"Wall")
                    orientation = np.append(orientation, orient)
                    count=count+1

            if orient=='na':
                print('na')
                results = np.append(results, id)
                x_res.append(x)
                y_res.append(y)
                orientation = np.append(orientation, orient)
        #removed door
        if id=="Window":
            x, y, orient = getBBox(e)
            results = np.append(results, id)
            x_res.append(x)
            y_res.append(y)
            orientation = np.append(orientation, orient)

    validate(results,x_res,y_res,'cubicasa5k'+path[:-1])
    exportToXml(results,x_res,y_res,orientation,path,width,height)
def segmentWall(e):
    x,y,orient=getBBox(e)

    x.sort()
    y.sort()

    if orient=='v':

        yNew=[y[1],y[2]]

        newWallsX=[]
        newWallsY=[]
        kl=-1
        for seg in e.getElementsByTagName('g'):
            kl=kl+1
            id=seg.getAttribute('id')

            if id=='Door' or id=='Window':
                xSeg,ySeg,orientSeg=getBBox(e.getElementsByTagName('g')[kl])

                ySeg.sort()

                yNew.append(ySeg[1])
                yNew.append(ySeg[2])

        yNew.sort()
        count=0
        for i in range(len(yNew)):
            if i%2==0:

                newWallsX.append(x)

                newWallsY.append([yNew[i],yNew[i+1]])
                count = count + 1

        retWallsX = []
        retWallsY = []
        for i in range(len(newWallsX)):
            retWallsX.append([newWallsX[i][0],newWallsX[i][3],newWallsX[i][3],newWallsX[i][0]])
            retWallsY.append([newWallsY[i][0],newWallsY[i][0],newWallsY[i][1],newWallsY[i][1]])

        return retWallsX,retWallsY
    if orient=='h':

        xNew=[x[1],x[2]]

        newWallsX=[]
        newWallsY=[]
        kl=-1
        for seg in e.getElementsByTagName('g'):
            kl=kl+1
            id=seg.getAttribute('id')

            if id=='Door' or id=='Window':
                xSeg,ySeg,orientSeg=getBBox(e.getElementsByTagName('g')[kl])

                xSeg.sort()

                xNew.append(xSeg[1])
                xNew.append(xSeg[2])

        xNew.sort()
        count=0
        for i in range(len(xNew)):
            if i%2==0:

                newWallsY.append(y)

                newWallsX.append([xNew[i],xNew[i+1]])
                count = count + 1

        retWallsX = []
        retWallsY = []
        for i in range(len(newWallsY)):
            retWallsX.append([newWallsX[i][0],newWallsX[i][1],newWallsX[i][1],newWallsX[i][0]])
            retWallsY.append([newWallsY[i][0],newWallsY[i][0],newWallsY[i][3],newWallsY[i][3]])

        return retWallsX,retWallsY












def exportToXml(elements,x,y,orientation,path,width,height):


    # create the file structure
    data = E.Element('annotation')
    folder = E.SubElement(data, 'folder')
    folder.text='Project5atirr'
    filename = E.SubElement(data, 'filename')
    filename.text=path
    pat=E.SubElement(data, 'path')
    pat.text='...'
    source=E.SubElement(data, 'source')
    database=E.SubElement(source, 'database')
    database.text='Unknown'
    size=E.SubElement(data, 'size')
    widthElement=E.SubElement(size, 'width')
    heightElement=E.SubElement(size, 'height')
    depth=E.SubElement(size, 'depth')
    depth.text=str(3)
    widthElement.text=str(width)
    heightElement.text=str(height)
    segmented=E.SubElement(data, 'segmented')
    segmented.text=str(0)
    i=-1
    for e in elements:
        i=i+1
        object=E.SubElement(data, 'object')
        name=E.SubElement(object, 'name')
        name.text=e
        pose=E.SubElement(object, 'pose')
        pose.text=orientation[i]
        points=E.SubElement(object, 'points')
        xTemp=x[i]
        yTemp=y[i]
        j=0
        for p in xTemp:
            point=E.SubElement(points, 'point')
            xElement=E.SubElement(point, 'x')
            xElement.text=str(xTemp[j])
            yElement=E.SubElement(point, 'y')
            yElement.text=str(yTemp[j])
            j=j+1
        xTemp.sort()
        yTemp.sort()
        truncated=E.SubElement(object, 'truncated')
        truncated.text=str(0)
        difficult=E.SubElement(object, 'difficult')
        difficult.text=str(0)
        bndbox=E.SubElement(object, 'bndbox')
        xmin=E.SubElement(bndbox, 'xmin')
        xmin.text=str(xTemp[0])
        ymin = E.SubElement(bndbox, 'ymin')
        ymin.text=str(yTemp[0])
        xmax=E.SubElement(bndbox, 'xmax')
        xmax.text=str(xTemp[3])
        ymax=E.SubElement(bndbox, 'ymax')
        ymax.text=str(yTemp[3])



    # create a new XML file with the results
    mydata = E.tostring(data)
    myfile = open("cubicasa5K"+path[:-1]+"annotation.xml", "wb")
    myfile.write(mydata)
def validate(results,x,y,path):
    dwg = svgwrite.Drawing(filename=path+'validate.svg', debug=True)
    i=0
    fill=''
    for obj in results:
        if obj=='Wall':
            fill='black'
        if obj=='Window':
            fill='blue'

        if obj =='Door':
            fill='white'

        g=dwg.add(dwg.g(id=obj,fill=fill))
        xCoord=x[i]
        yCoord=y[i]
        points=[[xCoord[0],yCoord[0]],[xCoord[1],yCoord[1]],[xCoord[2],yCoord[2]],[xCoord[3],yCoord[3]]]
        g.add(svgwrite.shapes.Polygon(points=points))
        i=i+1
    dwg.save()
def getBBox(e):
    pol = next(p for p in e.childNodes if p.nodeName == "polygon")
    points = pol.getAttribute("points").split(' ')
    points = points[:-1]
    X, Y = np.array([]), np.array([])

    for a in points:
        x,y = a.split(',')

        X = np.append(X, int(np.round(float(x))))
        Y = np.append(Y, int(np.round(float(y))))

    # h:horizontal v: vertical n:na
    directionToFix= getFixableDirection(X,Y)
    X,Y=fixCorners(directionToFix,X,Y)
    return X,Y,directionToFix


def fixCorners(directionToFix,x,y):
    if directionToFix=='na':

        return  x,y

    x.sort()
    y.sort()
    resX=np.array([x[0],x[3],x[3],x[0]])
    resY=np.array([y[0],y[0],y[3],y[3]])
    return resX ,resY




def getFixableDirection(x,y):
    temp1=copy.deepcopy(x)
    temp2=copy.deepcopy(y)
    temp1.sort()
    temp2.sort()

    if temp1[0]==temp1[1] and temp1[2]==temp1[3] and (temp1[2]-temp1[1]<temp2[2]-temp2[1]):
            return 'v'


    if temp2[0]==temp2[1] and temp2[2]==temp2[3]:
            return 'h'


    return 'na'



main()