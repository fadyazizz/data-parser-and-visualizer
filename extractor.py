import xml.etree.cElementTree as ET
from skimage.draw import polygon
import xml.etree.ElementTree as E
import svgwrite
import copy
from xml.dom import minidom
import numpy as np

def main():

    imgs_list = open('cubicasa5k/val.txt', 'r').readlines()
    for f in imgs_list:
        parse(f)

def parse(path):
    svg = minidom.parse('cubicasa5k'+path[:-1]+'model.svg')
    width=svg.getElementsByTagName('svg')[0].getAttribute('width')
    height=svg.getElementsByTagName('svg')[0].getAttribute('height')
    x_res, y_res = [], []
    results = np.array([])
    orientation = np.array([])
    for e in svg.getElementsByTagName('g'):

        id = e.getAttribute('id')
        if id == "Wall" or id == "Window" or id == "Door":
            x, y, orient = getBBox(e)
            results = np.append(results, id)
            x_res.append(x)
            y_res.append(y)
            orientation = np.append(orientation, orient)
    validate(results,x_res,y_res,'cubicasa5k'+path[:-1])
    exportToXml(results,x_res,y_res,orientation,path,width,height)
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


    if temp1[0]==temp1[1] and temp1[2]==temp1[3]:
            return 'v'
    temp2.sort()

    if temp2[0]==temp2[1] and temp2[2]==temp2[3]:
            return 'h'


    return 'na'



main()