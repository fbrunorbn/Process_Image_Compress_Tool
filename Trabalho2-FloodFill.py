import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import cv2 as cv
import numpy as np
from tkinter import messagebox


class MouseCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flood Fill Morfolófico")

        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Botão para iniciar e parar a captura
        self.start_stop_button = tk.Button(root, text="Iniciar/Parar Desenho", command=self.toggle_capture)
        self.start_stop_button.pack(side=tk.LEFT)

        # Botão para balde de tinta
        self.save_button = tk.Button(root, text="Balde de Tinta", command=self.capture_click_right)
        self.save_button.pack(side=tk.LEFT)

        self.red_button = tk.Button(root, text="Vermelho", command=self.select_red_color, bg="red")
        self.red_button.pack(side=tk.LEFT)

        self.green_button = tk.Button(root, text="Verde", command=self.select_green_color, bg="green")
        self.green_button.pack(side=tk.LEFT)

        self.blue_button = tk.Button(root, text="Azul", command=self.select_blue_color, bg="blue")
        self.blue_button.pack(side=tk.LEFT)

        # Variável para rastrear se a captura está ativa
        self.capture_active = False
        self.capture_right_active = False

        # Lista para armazenar os pontos capturados
        self.points = {}
        self.pixelsColor = []
        self.indiceCaptura = 0
        self.cor = 255

        # Semente para o flood fill
        self.seed = None

        # Vincula evento de pressionar o botão esquerdo e direito do mouse
        self.canvas.bind("<ButtonPress-1>", self.capture_click_left)
        self.canvas.bind("<ButtonPress-3>", self.capture_tinta)

    def select_red_color(self):
        self.cor = 255
        self.show_spam("Vermelho")

    def select_green_color(self):
        self.cor = 150
        self.show_spam("Verde")

    def select_blue_color(self):
        self.cor = 200
        self.show_spam("Azul")

    def show_spam(self, color_name):
        messagebox.showinfo("Cor Selecionada", f"A cor selecionada é: {color_name}")


    def capture_click_left(self, event):
        if self.capture_active:
            # Adiciona o ponto ao clicar com o botão esquerdo do mouse
            x, y = event.x, event.y
            self.points[self.indiceCaptura].append((x, y))

            # Se houver mais de um ponto, interpola para preencher a linha
            if len(self.points[self.indiceCaptura]) >= 2:
                self.interpolate_points()

    def capture_click_right(self):
        self.capture_right_active = not self.capture_right_active            

    def interpolate_points(self):
        # Interpola os pontos entre os dois últimos pontos e adiciona à lista
        x1, y1 = self.points[self.indiceCaptura][-2]
        x2, y2 = self.points[self.indiceCaptura][-1]

        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        steps = max(dx, dy)

        if steps == 0:
            return

        x_increment = (x2 - x1) / steps
        y_increment = (y2 - y1) / steps

        for i in range(1, steps):
            x = int(x1 + i * x_increment)
            y = int(y1 + i * y_increment)
            self.points[self.indiceCaptura].append((x, y))

        # Redesenha as linhas no canvas
        self.draw_lines()

    def draw_lines(self):
        # Limpa o canvas
        self.canvas.delete("all")

        for i in range(0,len(self.pixelsColor)):
            pixel,cor = self.pixelsColor[i]
            x,y = pixel[0]
            if cor == 255:
                self.canvas.create_rectangle(x, y, x+1, y+1, fill="red", outline="red")
            elif cor == 200:
                self.canvas.create_rectangle(x, y, x+1, y+1, fill="blue", outline="blue")
            elif cor == 150:
                self.canvas.create_rectangle(x, y, x+1, y+1, fill="green", outline="green")

        # Desenha linhas pretas conectando os pontos
        for i in range(0,len(self.points)):
            for j in range(0,len(self.points[i])-1):
                x1, y1 = self.points[i][j]
                x2, y2 = self.points[i][j + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=1)

        


    def capture_tinta(self,event):
        global result_img
        if self.capture_right_active: # for falso entra
            self.seed = (event.y, event.x)
            print(f"Semente (botão direito): {self.seed}")
            # Cria uma imagem NumPy em branco com as linhas desenhadas
            height, width = 400, 400
            img = np.ones((height, width), dtype=np.uint8) * 255
            for i in range(0,len(self.points)):
                for j in range(0,len(self.points[i])-2):
                    x1, y1 = self.points[i][j]
                    img[y1,x1] = 0

            # Elemento estruturante (cruz 3x3)
            kernel = np.array([[0, 1, 0],
                               [1, 1, 1],
                               [0, 1, 0]], dtype=np.uint8)

            # Inicia o flood fill morfológico a partir do ponto capturado com o botão direito
            result_img = self.morphy_flood_fill(img, self.seed, kernel)
            pixels = cv.findNonZero(result_img)
            for i in range(0,len(pixels)):
                self.pixelsColor.append((pixels[i],self.cor))

            # Atualiza o canvas com a imagem preenchida
            self.update_canvas(result_img)
            self.capture_right_active = not self.capture_right_active
        else:
            print("Clique com o botão direito para definir a semente antes de usar o balde de tinta.")

    def morphy_flood_fill(self, image, seed, kernel):
        global marker
        height, width = image.shape[:2]

        # Imagem de marcação para o flood fill - é a que vou aplicar a convolucao
        marker = np.zeros((height, width), dtype=np.uint8)
        marker[seed] = 255

        dilated = marker.copy()
        ind = 0
        # Iterações de dilatação até que não possa mais pintar
        while True:
            ind += 1
            for y in range(1, image.shape[0] - 1):
                for x in range(1, image.shape[1] - 1):
                    # Se o pixel atual for branco, dilata os pixels vizinhos
                    if marker[y,x] == 255:
                        dilated[y, x-1:x+2] = 255  # Linha horizontal (1 acima, 1 atual, 1 abaixo)
                        dilated[y-1:y+2, x] = 255
                        #dilated = cv.bitwise_and(dilated, image, mask=image)

            #dilated = dilated * image
            dilated = cv.bitwise_and(dilated, image, mask=image)
            

            # Verifica se algo foi adicionado na dilatação
            if np.array_equal(marker, dilated):
                break

            # Atualiza a marcação com a dilatação
            marker = dilated.copy()

        return dilated

    def update_canvas(self, img):
        # Redesenha as linhas no canvas
        self.draw_lines()

        # Converte a imagem NumPy para o formato adequado para exibição no Tkinter
        img_pil = Image.fromarray(img)
        img_tk = ImageTk.PhotoImage(image=img_pil)

        # Atualiza o canvas com a imagem preenchida
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)

    def toggle_capture(self):
        # Alterna entre iniciar e parar a captura ao clicar no botão
        self.capture_active = not self.capture_active
        if self.capture_active:
            self.points[self.indiceCaptura] = []
        else:
            self.indiceCaptura += 1

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseCaptureApp(root)
    root.mainloop()
