import cv2
import numpy as np

img = cv2.imread('026A-500x500.png',0)
img = cv2.resize(img,(400,400))
img_ori = img.copy()
size = np.size(img)
skel = np.zeros(img.shape,np.uint8)

ret,img = cv2.threshold(img,127,255,0)
element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
done = False

total = 0
imagens = []
ind = 0
while( not done):
    ind += 1
    #A cada iteração a imagem é erodida novamente e o esqueleto é refinado calculando a união da erosão atual menos a abertura desta erosão. Uma abertura é simplesmente uma erosão seguida de uma dilatação.
    total += 1
    eroded = cv2.erode(img,element)#primeiro erosa(A erode k.B)
    cv2.imshow("eroded"+str(ind),eroded)
    temp = cv2.dilate(eroded,element)#dilatacao do objeto ((A erode k.B) dilate B), temp agora é a abertura
    cv2.imshow("dilate"+str(ind),temp)
    temp = cv2.subtract(img,temp) #faz a subtração da erosao com a abertura da erosao
    cv2.imshow("subtracao"+str(ind),temp)
    skel = cv2.bitwise_or(skel,temp) #unindo todos os passos k, que vai juntar todos os "buracos" que sobraram na abertura (pedaço pequeno tirado no objeto)
    img = eroded.copy()

    if ind > 15:
        break

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