import os 
import math
from PIL import Image


#User Variables (mm)#

totalsize = 50 #Length of sides of the square
bordersize = 0 #Width of the border
totaldepth =  15 #Max depth of cuts
cuttingtoolDiameters = [3.175] #Diameters of the cutting tools in inches

#############################################################################################


def tool_fits(tool_diameter, image, ipp, imagesize, x, y):
    search_x_min = max([0, x - int(tool_diameter/(2*ipp))])
    search_x_max = min([imagesize, x + int(tool_diameter/(2*ipp))])
    search_y_min = max([0, y - int(tool_diameter/(2*ipp))])
    search_y_max = min([imagesize, y + int(tool_diameter/(2*ipp))])
    for s_x in range(search_x_min, search_x_max):
        if s_x - int(tool_diameter/(2*ipp)) < 0 or s_x + int(tool_diameter/(2*ipp)) > imagesize:
            continue
        for s_y in range(search_y_min, search_y_max):
            if s_y - int(tool_diameter/(2*ipp)) < 0 or s_y + int(tool_diameter/(2*ipp)) > imagesize:
                continue
            distance = (math.sqrt((s_x - x)**2 + (s_y - y)**2))*ipp
            if distance <= tool_diameter/2:
                if image.getpixel((s_x, s_y)) == (0, 0, 0):
                    return False
                    #image.putpixel((s_x, s_y), (255, 0, 0))            
    return True


mapsize = totalsize - 2*bordersize
imagesize = Image.open("./map.png").size[0]
mmPerPixel = mapsize / imagesize
colors = [(255, 0, 0), (255, 255, 0), (0, 255, 0)] #Red for biggest, yellow for medium, green for smallest
colors.reverse()
layers = os.listdir("./layers")
layers.sort()
prevlayer = None

# for layer in layers:
#     im = Image.open("./layers/" + layer)
#     if prevlayer != None:
#         for x in range (im.size[0]):
#             for y in range (im.size[1]):
#                 if prevlayer.getpixel((x,y)) == colors[0]:
#                     im.putpixel((x, y), colors[0])

#     for t in range(len(cuttingtoolDiameters)):
#         currentTool = cuttingtoolDiameters[t]
#         currentColor = colors[t]
#         space = int((1.2*currentTool)/(2*mmPerPixel))
#         print(space)
#         for x in range (imagesize):
#             if x % space != 0:
#                 continue
#             for y in range (imagesize):
#                 if y % space != 0:
#                     continue
#                 if im.getpixel((x,y)) == (255, 255, 255):
#                     if tool_fits(currentTool, im, mmPerPixel, imagesize, x, y):
#                         im.putpixel((x, y), currentColor)
    
#     im.save("./tools/" + layer)
#     print(layer)
#     prevlayer = im


######### Start by placing center of tool at upper left corner of piece #########
feed = 800 ##feed in mm/min
leftrightbuffer = 2 ##buffer on either side of map in mm
gcode = "G91\nG21\nG00 X-"+ str(leftrightbuffer) +" F" + str(feed)


#########            -
#########    - X +   Y
#########            +
spacemm = round((1.2*cuttingtoolDiameters[0])/2, 4)
spacepixels = int(spacemm/mmPerPixel)
currentDepth = 0
layers.reverse()
layerAdjustment = 4
onLeft = True

for i, l in enumerate(layers):
    # if (i < 230):
    #     continue
    if (i % layerAdjustment != 0):
        continue
    im = Image.open("./tools/" + l)
    gcode += "\nG00 Z-" + str(round(layerAdjustment*totaldepth/255,4)) + " F" + str(feed)
    currentDepth += round(layerAdjustment*totaldepth/255,4)
    print(l + ", Coding depth: " + str(round(currentDepth, 2)) + "mm")
    countx = 0
    resetx = 0
    for x in range (imagesize):
        county = 0
        if x % spacepixels != 0:
            continue

        ###Check if there are any cuts to make in this row###
        cutFlag = True
        # for y in range (imagesize):
        #     if y % spacepixels != 0:
        #         continue
        #     if im.getpixel((x,y)) == colors[0]:
        #         cutFlag = True
        ###If the cutting tool is on the left side
        if cutFlag:
            if onLeft:
                if im.getpixel((x,0)) == colors[0]:
                    gcode += "\nG00 X"+ str(leftrightbuffer) +"  F" + str(feed) #Move to edge of piece for next pass
                    cutting = True
                else:
                    gcode += "\nG00 Z" + str(currentDepth) + " F" + str(feed) #Move up
                    gcode += "\nG00 X"+ str(leftrightbuffer) +" F" + str(feed) #Move to edge of piece for next pass
                    cutting = False

                for y in range (imagesize):
                    if y % spacepixels != 0:
                        continue
                    if y + spacepixels >= imagesize:
                        break
                    if im.getpixel((x,y+spacepixels)) == colors[0]:
                        if cutting:
                            gcode += "\nG01 X" + str(spacemm) + " F" + str(feed)
                        else:
                            gcode += "\nG01 X" + str(spacemm) + " F" + str(feed)
                            gcode += "\nG00 Z-" + str(currentDepth) + " F" + str(feed)
                            cutting = True
                    else:
                        if cutting:
                            gcode += "\nG00 Z" + str(currentDepth) + " F" + str(feed)
                            gcode += "\nG01 X" + str(spacemm) + " F" + str(feed)
                            cutting = False
                        else:
                            gcode += "\nG01 X" + str(spacemm) + " F" + str(feed)
                    county += 1

                gcode += "\nG00 X"+ str(leftrightbuffer) +" F" + str(feed)
                if cutting == False:
                    gcode += "\nG00 Z-" + str(currentDepth) + " F" + str(feed)
                    cutting = True
                onLeft = False
                resetx = county


            else:
                if im.getpixel((x,imagesize - 1)) == colors[0]:
                    gcode += "\nG00 X-"+ str(leftrightbuffer) +" F" + str(feed) #Move to edge of piece for next pass
                    cutting = True
                else:
                    gcode += "\nG00 Z" + str(currentDepth) + " F" + str(feed) #Move up
                    gcode += "\nG00 X-"+ str(leftrightbuffer) +" F" + str(feed) #Move to edge of piece for next pass
                    cutting = False

                for y in reversed(range(imagesize)):
                    if y % spacepixels != 0:
                        continue
                    if y - spacepixels < 0:
                        break


                    if im.getpixel((x,y-spacepixels)) == colors[2]:
                        if cutting:
                            gcode += "\nG01 X-" + str(spacemm) + " F" + str(feed)
                        else:
                            gcode += "\nG01 X-" + str(spacemm) + " F" + str(feed)
                            gcode += "\nG00 Z-" + str(currentDepth) + " F" + str(feed)
                            cutting = True
                    else:
                        if cutting:
                            gcode += "\nG00 Z" + str(currentDepth) + " F" + str(feed)
                            gcode += "\nG01 X-" + str(spacemm) + " F" + str(feed)
                            cutting = False
                        else:
                            gcode += "\nG01 X-" + str(spacemm) + " F" + str(feed)
                    county += 1

                gcode += "\nG00 X-"+ str(leftrightbuffer) +" F" + str(feed)
                if cutting == False:
                    gcode += "\nG00 Z-" + str(currentDepth) + " F" + str(feed)
                    cutting = True
                onLeft = True
                resetx = county




        gcode += "\nG00 Y-" + str(spacemm) + " F" + str(feed) #Move down a row
        countx += 1


    if onLeft:
        gcode += "\nG00 Y" + str(spacemm*countx) + " F" + str(feed)
    else:
        gcode += "\nG00 Z" + str(currentDepth) + " F" + str(feed)
        gcode += "\nG00 X-" + str(spacemm*resetx + leftrightbuffer*2) + " F" + str(feed)
        gcode += "\nG00 Y" + str(spacemm*countx) + " F" + str(feed)
        gcode += "\nG00 Z-" + str(currentDepth) + " F" + str(feed)

    onLeft = True
    

file = open("./gcode.gcode", "w")
file.write(gcode)
file.close()