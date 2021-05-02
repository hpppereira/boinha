from math import *

def deltay2(x1,y1,z1,x2,y2,z2,zf,k1,C1,k2,C2):

    """
    x1 - teste
    """
    Li1=sqrt(x1**2+y1**2+z1**2)
    Li2=sqrt(x2**2+y2**2+z2**2)
    D=0
    R=(2*C1*((sqrt(x1**2+(y1-D)**2+zf**2))-Li1)*(y1-D))/(k1*Li1*(sqrt(x1**2+(y1-D)**2+zf**2))) + (C2*(sqrt(x2**2+(y2-D)**2+zf**2)-Li2)*(y2+D))/(k2*Li2*(sqrt(x2**2+(y2+D)**2+zf**2)))
    while R>0.05 or R<-0.05:
        D=D+0.0001
        R=(2*C1*((sqrt(x1**2+(y1-D)**2+zf**2))-Li1)*(y1-D))/(k1*Li1*(sqrt(x1**2+(y1-D)**2+zf**2))) + (C2*(sqrt(x2**2+(y2-D)**2+zf**2)-Li2)*(y2+D))/(k2*Li2*(sqrt(x2**2+(y2+D)**2+zf**2)))
        print ('R=%.5f --> D=%.5f' %(R, D))

x1 = 0
y1 = 31
z1 = 3.5
x2 = 0
y2 = -30
z2 = 3.5
zf = 5
k1 = 0.15
C1 = 500
k2 = 0.15
C2 = 100

deltay2(x1,y1,z1,x2,y2,z2,zf,k1,C1,k2,C2)
       
        
       
