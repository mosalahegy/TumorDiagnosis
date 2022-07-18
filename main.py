import tkinter as tk
from tkinter import *
from tkinter import filedialog as fd
from PIL import ImageTk
from PIL import Image as PilImage
from tkinter import messagebox
# for multi circles in single image
import cv2
import math
import numpy as np
import ctypes


class Browse(tk.Frame):
    """ Creates a frame that contains a button when clicked lets the user to select
    a file and put its filepath into an entry.
    """

    def __init__(self, master, initialdir='', filetypes=()):
        super().__init__(master)
        self.filepath = None;
        self.tumor = tk.StringVar();
        self._initaldir = initialdir
        self._filetypes = filetypes
        self._create_widgets()
        
    def _create_widgets(self):
        c = Canvas(self,bg = "#81BEF7",height = "300",width = "500") 
        c.pack()

        labelframe1 = LabelFrame(self, text="",bg="#81BEF7",font=("bold",15))  
        labelframe1.pack(fill="both", expand="yes")

        self._label_1 = tk.Label(self, text="Tumor Dignosis", width=30, font=("bold",20),bg="#81BEF7")
        self._label_1.place(x= 10, y= 20)
        
        self._label2 = tk.Label(self, text="Select the x-rays images", width=30, font=("bold",13),bg="#81BEF7")
        self._label2.place(x= 10, y= 100)
        
        self._button = tk.Button(self, text="Browse...", command=self.browse, width=20, font=("bold",12),bd=5,
                                 fg="#000000",activebackground = "#2E9AFE")
        self._button.place(x= 280, y= 100)

        
      #  self._label2 = tk.Label(self, text="To get result", width=15, font=("bold",12))
       # self._label2.place(x= 37, y= 230)
        
        
        
        self._button = tk.Button(self, text="Classify", command=self.res, width=36, font=("bold",15),
                                 fg="#000000",activebackground = "#2E9AFE"
                                , bd=5)
        self._button.place(x= 60, y= 160)

        
        


        
        

    def browse(self):
        
        self.filepath = fd.askopenfile(initialdir=self._initaldir,
                                             filetypes=self._filetypes)
        
        img = PilImage.open(self.filepath.name)
        img = img.resize((300, 300), PilImage.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        panel = Label(root, image=img)
        panel.image = img
        panel.pack()
        
       # print(self.tumor.get())
       
       
      
    def res(self):
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
    
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
        
        curr_dpi = w*96/width_px
        
    
        # read image through path
        #img = cv2.imread('C:\\Users\\M.Glal\\JupeiterProjects\\.ipynb_checkpoints\\pic.jpeg')
        kernal = np.ones((7,7),np.uint8) 
        
        img = cv2.imread(self.filepath.name)
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
        #im2, contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        contours,hierachy=cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            # calculate moments for each contour
            M = cv2.moments(c)
            
            point_x = int(M["m10"] / (M["m00"]+.00001))
            point_y = int(M["m01"] / (M["m00"]+.00001))
            pord_x = c[0][0][0]
            pord_y = c[0][0][1]
            #print(c)
            distance = math.sqrt((point_x - pord_x )**2 + (point_y - pord_y )**2) * 10
            d = round((round(distance, 5)*2.54 / curr_dpi),5)
            if d > 1:
                cv2.circle(img,(point_x,point_y),1,(255,255,0),2)
                cv2.circle(img,(pord_x,pord_y),1,(255,0,255),4)
                #cv2.putText(img,"", (point_x,point_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))
                #cv2.putText(img,"", (pord_x,pord_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0))
                diameters.append(d)
            
        cv2.drawContours(img,contours,-1,(255,0,0),1)
        
        
        # displaying the matrix form of image
        height,width,depth = img.shape
        rgbs = []
        areas = []
        perimeters=[]
        for i in range(height):
            for j in range(width):
                rgbs.append(img[i,j])
        texture_mean = np.std(rgbs)
        #if len(diameters) <= 3:
         #   radius_mean = sum(diameters)/len(diameters)
        #else:
        #   diameters.sort()
         #   d1 = diameters[len(diameters) - 1]
          #  d2 = diameters[len(diameters) - 2]
          #  d3 = diameters[len(diameters) - 3]
          #  diameters = [d1, d2, d3]
        radius_mean = sum(diameters)/len(diameters)
        
        for r in diameters:
            areas.append(math.pi*(r**2))
            perimeters.append(2*r*math.pi)
            
        perimeter_mean = sum(perimeters)/len(perimeters)  
        area_mean =  sum(areas)/len(areas)
        
        radius_se = np.std(diameters) / np.sqrt(len(diameters))
        area_se = np.std(areas) / np.sqrt(len(areas))
        perimeter_se = np.std(perimeters) / np.sqrt(len(perimeters))
        texture_se = texture_mean / np.sqrt(len(rgbs))
        
        radius_data_mean = -9.998836 * 10e-16
        area_data_mean = -7.423275 * 10e-16
        perimeter_data_mean = 1.903086 * 10e-15
        texture_data_mean = -9.782255 * 10e-16
        
        radius_mean = (radius_mean - (-3.136331*10e-15)) / 1.00
        area_mean = (area_mean - (-8.339355*10e-16)) / 1.00
        perimeter_mean = (perimeter_mean - (-7.012551*10e-16)) / 1.00
        texture_mean = (texture_mean - (-6.558316*10e-15)) / 1.00
        
        radius_se = (radius_se - radius_data_mean) / 1.00
        area_se = (area_se - area_data_mean) / 1.00
        perimeter_se = (perimeter_se - perimeter_data_mean) / 1.00
        texture_se = (texture_se - texture_data_mean) / 1.00
      
    
        # #display the image
        cv2.waitKey(0)    
        finalTheats = [-0.2878857, -0.40019631, -1.62579705, 
                       -1.94472765, -0.21383718, -0.49317564,
                        0.93070392, -1.04126324, -0.68519593
                      ]
        dataFromImage = [1,radius_mean, texture_mean, 
                         perimeter_mean, area_mean, 
                         radius_se, texture_se, 
                         perimeter_se, area_se
                        ]
        finalTheats = np.matrix(finalTheats)
        dataFromImage = np.matrix(dataFromImage)
        
        z = dataFromImage * finalTheats.T
       
        zint = int(z)
        digit = len(str(abs(zint)))
        z = z / np.power(10,digit)
        prob = 1 / float((1 + np.exp(-1 * z)))
        threshould = 0.45
        if prob >= threshould:
            result = 1
        else:
            result = 0
        
        if(result == 0):    
            self.tumor.set("Malignant")
            self._entry = tk.Entry(self, textvariable=self.tumor, width=20,bd=5,bg="red", font=("bold",13),fg="#ffffff")
            self._entry.place(x= 280, y= 250)
            self._label3 = tk.Label(self, text="The Tumor is", width=15,bg="#81BEF7")
            self._label3.place(x= 37, y= 250)
        else:
            self.tumor.set("Benign")
            self._entry = tk.Entry(self, textvariable=self.tumor, width=20,bd=5,bg="green", font=("bold",13),fg="#ffffff")
            self._entry.place(x= 280, y= 250)
            self._label3 = tk.Label(self, text="The Tumor is", width=15,bg="#81BEF7")
            self._label3.place(x= 37, y= 250)
        
            
            

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('500x600')
    root.title("Tumor Dignosis")

    filetypes = (
                    ('Images','*.png'),
                    ('Images','*.jpg'),
                    ('Images','*.jpeg'),
                    ("All files", "*.*")
                )
    file_browser = Browse(root, initialdir=r"C:\Users",
                      filetypes=filetypes)

    file_browser.pack(fill='both', expand=True)

    root.mainloop()