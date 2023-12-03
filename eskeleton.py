import cv2
import numpy as np

img = cv2.imread('test-eskeleton.jpg',0)
img = cv2.resize(img,(400,400))
img_ori = img.copy()
size = np.size(img)
skel = np.zeros(img.shape,np.uint8)

ret,img = cv2.threshold(img,127,255,0)
element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
done = False

total = 0
imagens = []

while( not done):
    total += 1
    eroded = cv2.erode(img,element)
    temp = cv2.dilate(eroded,element)
    temp = cv2.subtract(img,temp)
    skel = cv2.bitwise_or(skel,temp)
    img = eroded.copy()

    if total%4 == 0:
        imgTemp = img.copy()
        skelTemp = skel.copy()
        imagens.append(imgTemp.copy())
        imagens.append(skelTemp.copy())

    zeros = size - cv2.countNonZero(img)
    if zeros==size:
        done = True

print(total)

cv2.imshow("original",img_ori)
cv2.imshow("skel",skel)
for i in range(0,len(imagens)):
    cv2.imshow('janela'+str(i),imagens[i])
cv2.waitKey(0)
cv2.destroyAllWindows()