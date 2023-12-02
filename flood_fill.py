import tkinter as tk
from PIL import Image, ImageDraw, ImageTk

class MouseCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Capture Example")

        self.canvas = tk.Canvas(root, width=400, height=400, bg="white")
        self.canvas.pack(expand=tk.YES, fill=tk.BOTH)

        # Botão para iniciar e parar a captura
        self.start_stop_button = tk.Button(root, text="Iniciar/Parar Desenho", command=self.toggle_capture)
        self.start_stop_button.pack(side=tk.LEFT)

        # Botão para salvar a imagem
        self.save_button = tk.Button(root, text="Salvar Imagem", command=self.save_image)
        self.save_button.pack(side=tk.LEFT)

        # Variável para rastrear se a captura está ativa
        self.capture_active = False

        # Lista para armazenar os pontos capturados
        self.points = []

        # Vincula eventos de pressionar e soltar o botão esquerdo do mouse
        self.canvas.bind("<ButtonPress-1>", self.start_capture)
        self.canvas.bind("<ButtonRelease-1>", self.stop_capture)
        self.canvas.bind("<B1-Motion>", self.capture_motion)

    def start_capture(self, event):
        # Inicia a captura quando o botão é pressionado
        self.capture_active = True
        self.points = []

    def stop_capture(self, event):
        # Para a captura quando o botão é solto
        self.capture_active = False
        # Desenha as linhas pretas conectando os pontos
        self.draw_lines()

    def capture_motion(self, event):
        # Captura pontos enquanto o botão do mouse está em movimento
        if self.capture_active:
            x, y = event.x, event.y
            self.points.append((x, y))

    def draw_lines(self):
        # Desenha linhas pretas conectando os pontos
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

    def save_image(self):
        # Obtém as dimensões do canvas
        width = self.canvas.winfo_reqwidth()
        height = self.canvas.winfo_reqheight()

        # Cria uma imagem RGB em branco
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)

        # Redesenha as linhas no novo objeto de desenho
        for i in range(len(self.points) - 1):
            x1, y1 = self.points[i]
            x2, y2 = self.points[i + 1]
            draw.line([(x1, y1), (x2, y2)], fill="black", width=2)

        # Salva a imagem
        img.save("canvas_image_rgb.png", format="PNG")

        print("Imagem salva com sucesso!")

    def toggle_capture(self):
        # Alterna entre iniciar e parar a captura ao clicar no botão
        if self.capture_active:
            self.capture_active = False
        else:
            self.capture_active = True
            self.points = []

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseCaptureApp(root)
    root.mainloop()
