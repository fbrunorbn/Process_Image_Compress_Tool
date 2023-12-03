import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk

listaImagensResultantesEsquel = []
indiceEsquel = 0

def esqueletonizacao(img):
    # Coloque aqui o código para esqueletonização
    img_ori = img.copy()
    size = np.size(img)
    skel = np.zeros(img.shape, np.uint8)

    ret, img = cv2.threshold(img, 127, 255, 0)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    done = False

    while not done:
        eroded = cv2.erode(img, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(img, temp)
        skel = cv2.bitwise_or(skel, temp)
        img = eroded.copy()

        zeros = size - cv2.countNonZero(img)
        if zeros == size:
            done = True

    return skel    

def proxima_imagem():
    global indiceEsquel
    indiceEsquel += 1
    if indiceEsquel == len(listaImagensResultantesEsquel):
        indiceEsquel = 0

    desenhaEsq()

# Função para carregar imagem na nova janela
def carregar_imagem(janela):
    global indiceEsquel
    indiceEsquel = 0
    listaImagensResultantesEsquel.clear()
    # Usando o filedialog para obter o caminho da imagem
    file_path = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])

    # Se o usuário selecionar uma imagem
    if file_path:
        img = cv2.imread(file_path, 0)
        img = cv2.resize(img, (400, 400))
        listaImagensResultantesEsquel.append(img.copy())
        # Executa a esqueletonização na nova imagem
        skel_result = esqueletonizacao(img)
        listaImagensResultantesEsquel.append(skel_result.copy())

        desenhaEsq()

def desenhaEsq():
    # Exibe o resultado na interface
    result_image = Image.fromarray(cv2.cvtColor(listaImagensResultantesEsquel[indiceEsquel], cv2.COLOR_BGR2RGB))
    result_image = ImageTk.PhotoImage(result_image)
    canvas.create_image(0, 0, anchor=tk.NW, image=result_image)
    canvas.image = result_image

# Inicialização da aplicação Tkinter
root = tk.Tk()
root.title("Processamento de Imagem")

root.title("Esqueletonização")
root.geometry("500x500")

# Adiciona um botão para carregar uma nova imagem
btn_carregar_imagem = ttk.Button(root, text="Carregar Imagem", command=lambda: carregar_imagem(root))
btn_carregar_imagem.pack(pady=5)

btn_prox_imagem = ttk.Button(root, text="Proxima Imagem", command=lambda: proxima_imagem())
btn_prox_imagem.pack(pady=5)

# Área para exibir a imagem
canvas = tk.Canvas(root, width=400, height=400)
canvas.pack(pady=5)

# Iniciar a interface
root.mainloop()
