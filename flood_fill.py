import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import cv2 as cv
import numpy as np

class MouseCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Capture Example")

        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Botão para iniciar e parar a captura
        self.start_stop_button = tk.Button(root, text="Iniciar/Parar Desenho", command=self.toggle_capture)
        self.start_stop_button.pack(side=tk.LEFT)

        # Botão para balde de tinta
        self.save_button = tk.Button(root, text="Balde de Tinta", command=self.capture_tinta)
        self.save_button.pack(side=tk.LEFT)

        # Variável para rastrear se a captura está ativa
        self.capture_active = False

        # Lista para armazenar os pontos capturados
        self.points = []

        # Semente para o flood fill
        self.seed = None

        # Vincula evento de pressionar o botão esquerdo e direito do mouse
        self.canvas.bind("<ButtonPress-1>", self.capture_click_left)
        self.canvas.bind("<ButtonPress-3>", self.capture_click_right)

    def capture_click_left(self, event):
        if not self.capture_active:
            # Adiciona o ponto ao clicar com o botão esquerdo do mouse
            x, y = event.x, event.y
            self.points.append((x, y))

            # Se houver mais de um ponto, interpola para preencher a linha
            if len(self.points) >= 2:
                self.interpolate_points()

    def capture_click_right(self, event):
        if not self.capture_active:
            # Ao clicar com o botão direito, captura a posição do mouse como semente
            self.seed = (event.x, event.y)
            print(f"Semente (botão direito): {self.seed}")

    def interpolate_points(self):
        # Interpola os pontos entre os dois últimos pontos e adiciona à lista
        x1, y1 = self.points[-2]
        x2, y2 = self.points[-1]

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
            self.points.append((x, y))

        # Redesenha as linhas no canvas
        self.draw_lines()

    def draw_lines(self):
        # Limpa o canvas
        self.canvas.delete("all")

        # Desenha linhas pretas conectando os pontos
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=1)

    def capture_tinta(self):
        global result_img
        if self.seed is not None:
            # Cria uma imagem NumPy em branco com as linhas desenhadas
            height, width = 400, 400
            img = np.ones((height, width), dtype=np.uint8) * 255
            print(img)
            for ind, val in enumerate(self.points):
                img[val] = 0

            # Elemento estruturante (cruz 3x3)
            kernel = np.array([[0, 1, 0],
                               [1, 1, 1],
                               [0, 1, 0]], dtype=np.uint8)

            # Inicia o flood fill morfológico a partir do ponto capturado com o botão direito
            result_img = self.morphy_flood_fill(img, self.seed, kernel)
            #cv.imshow('janelaResult',result_img)

            # Salva a imagem resultante
            #cv.imwrite("imagem_pintada.bmp", result_img)

            # Atualiza o canvas com a imagem preenchida
            self.update_canvas(result_img)
        else:
            print("Clique com o botão direito para definir a semente antes de usar o balde de tinta.")

    def morphy_flood_fill(self, image, seed, kernel):
        global marker
        #print("ENTROU NO FLOOD FILL")
        height, width = image.shape[:2]

        # Imagem de marcação para o flood fill - é a que vou aplicar a convolucao
        marker = np.zeros((height, width), dtype=np.uint8)
        marker[seed] = 255

        dilated = marker.copy()
        ind = 0
        # Iterações de dilatação até que não possa mais pintar
        while True:
            ind += 1
            #print("ENTOU NO LAÇO")
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
                print("SAIU IGUAL")
                print(ind)
                break

            # Atualiza a marcação com a dilatação
            marker = dilated.copy()

            self.update_canvas(marker)

        #print("SAIU DO LAÇO WHILE")
        # Pinta os pixels na imagem original
        #result = image.copy()
        #result[marker > 0] = 255

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

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseCaptureApp(root)
    root.mainloop()
