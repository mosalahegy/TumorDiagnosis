# for multi circles in single image
import cv2
import math
import numpy as np
import tkinter as tk

def my_DPI():
    root = tk.Tk()
    width_px = root.winfo_screenwidth()
    height_px = root.winfo_screenheight() 
    width_mm = root.winfo_screenmmwidth()
    height_mm = root.winfo_screenmmheight() 
    # 2.54 cm = in
    width_in = width_mm / 25.4
    height_in = height_mm / 25.4
    
    # dot per inch
    width_dpi = width_px/width_in
    height_dpi = height_px/height_in 
    
    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]

    curr_dpi = w*96/width_px
    return curr_dpi

# read image through path
#img = cv2.imread('C:\\Users\\M.Glal\\JupeiterProjects\\.ipynb_checkpoints\\pic.jpeg')
kernal = np.ones((7,7),np.uint8) 

img = cv2.imread("C:\\Users\\S Mohamed H\\Desktop\\Maligment-Tumers\\Picture1 (1).jpg")
output = img.copy()
# convert the image to grayscale
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binv = cv2.threshold(img, 50, 255, cv2.THRESH_BINARY_INV)
erosion = cv2.erode(binv, kernal, iterations = 2)
dilation = cv2.dilate(binv, kernal, iterations = 1)
closing = cv2.morphologyEx(dilation, cv2.MORPH_OPEN, kernal, iterations = 5)
openning = cv2.morphologyEx(erosion, cv2.MORPH_CLOSE, kernal, iterations = 1)

rr=cv2.cvtColor(openning, cv2.COLOR_BGR2GRAY);
# convert the grayscale image to binary image
ret,thresh = cv2.threshold(rr, 120, 255, 0)

diameters = []
#find contours in the binary image
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

for c in contours:
    # calculate moments for each contour
    M = cv2.moments(c)
    
    point_x = int(M["m10"] / (M["m00"]+.00001))
    point_y = int(M["m01"] / (M["m00"]+.00001))
    pord_x = c[0][0][0]
    pord_y = c[0][0][1]
    #print(c)
    distance = math.sqrt((point_x - pord_x )**2 + (point_y - pord_y )**2) * 10
    d = round((round(distance, 5)*2.54 / my_DPI()),5)
    if d > 1:
        cv2.circle(img,(point_x,point_y),1,(255,255,0),2)
        cv2.circle(img,(pord_x,pord_y),1,(255,0,255),4)
        #cv2.putText(img,"", (point_x,point_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
        #cv2.putText(img,"", (pord_x,pord_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0))
        diameters.append(d)

cv2.drawContours(img,contours,-1,(255,0,0),1)
radius_mean = sum(diameters)/len(diameters)

# displaying the matrix form of image
height,width,depth = img.shape
rgbs = []
areas = []
perimeters=[]
for i in range(height):
    for j in range(width):
        rgbs.append(img[i,j])
sd = np.std(rgbs)
for r in diameters:
    areas.append(math.pi*(r**2))
    perimeters.append(2*r*math.pi)
    
perimeter_mean = sum(perimeters)/len(perimeters)  
area_mean =  sum(areas)/len(areas)
compact = (perimeter_mean) / (area_mean-1.0)
print(radius_mean)
print(sd)
print(perimeter_mean)
print(area_mean)
print(compact)

# #display the image
cv2.imshow("Image", np.hstack([img, openning]))
cv2.waitKey(0)