from PIL import Image

im = Image.open("./map.png")
print(im.format, im.size, im.mode)

max = -1
min = 300
arr = []
for x in range (im.size[0]):
    arr2 = []
    for y in range (im.size[1]):
        arr2.append(im.getpixel((x, y))[0])
        if arr2[y] > max:
            max = arr2[y]
        if arr2[y] < min:
            min = arr2[y]
    arr.append(arr2)

print("Level min and max: ", min, max)
fileString = ""
for z in range (min, max + 1):
    fileString += "\n\\\\Layer " + str(z) + "\\\\\n"
    #im2 = Image.new("RGB", im.size)
    for x in range (im.size[0]):
        for y in range (im.size[1]):
            pix = arr[x][y]
            if pix >= z:
                #im2.putpixel((x, y), (0, 0, 0))
                fileString += "1"
            else:
                #im2.putpixel((x, y), (255, 255, 255))  
                fileString += "0" 
        fileString += "\n"
    #im2.save("./layers/map_" + '{:03}'.format(z) + ".png")
    print("Layer " + str(z) + " saved.")


file = open("./layers.txt", "w")
file.write(fileString)
file.close()

#im.show()