import tkinter as tk
from tkinter import ttk, filedialog
from PIL import Image, ImageTk
import zlib
import cv2
import numpy as np
from bitarray import bitarray
from collections import Counter
import heapq
from collections import defaultdict
import os
import struct

def carregar_imagem():
    file_path = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=[("Imagens", "*.png;*.jpg;*.jpeg;*.bmp")])

    if file_path:
        global image
        img = Image.open(file_path)
        img_width, img_height = img.size
        image = cv2.imread(file_path)

        # Tamanho em pixels
        tamanho_pixels = f"Tamanho: {img_width} x {img_height}"

        # Tamanho em kilobytes
        tamanho_kb = os.path.getsize(file_path) / 1024
        tamanho_kb_str = f"Tamanho em KB: {int(tamanho_kb)} KB"

        label_tamanho.config(text=f"{tamanho_pixels}\n{tamanho_kb_str}")

        imagem_original.image = ImageTk.PhotoImage(img)
        canvas_imagem_original.config(width=img_width, height=img_height)
        canvas_imagem_original.create_image(0, 0, anchor=tk.NW, image=imagem_original.image)

def aplicar_compressao():
    global dictsLZW
    global dictsHuff
    channel_r = (image[:, :, 2]).flatten()
    channel_g = (image[:, :, 1]).flatten()
    channel_b = (image[:, :, 0]).flatten()
    print(len(channel_r))
    print(len(channel_g))
    print(len(channel_b))

    dictsLZW  = []
    dictsHuff = []

    def compressao(channel,X):
        def lzw_compress(data):
            dictionary = {(i,): i for i in range(256)}
            result = [] #Codigo final comprimido
            current_code = 256 #Proximo codigo a ser criado para uma nova sequencia do dicionario
            current_sequence = [data[0]] #Lista atual da sequencia
            ind = 1
            
            while ind < len(data):
                pixel_value = data[ind]

                # Continuamente verifica se o próximo valor está no dicionário
                test = current_sequence.copy()
                test.append(pixel_value)
                test_key = tuple(test)

                if test_key in dictionary:
                    current_sequence = test
                    ind += 1
                else:
                    # Adiciona a sequência atual ao resultado
                    result.append(dictionary[tuple(current_sequence)])

                    # Adiciona a nova sequência ao dicionário se não atingiu o limite
                    if current_code < 65536:
                        dictionary[test_key] = current_code
                        current_code += 1

                    # Reinicia a sequência para o próximo valor
                    current_sequence = [pixel_value]
                    ind += 1

            return result, dictionary


        # Comprimir
        compressed_data, lzw_dict = lzw_compress(channel)
        dictsLZW.append(lzw_dict)

        ##################################################################################################INICANDO HUFFMAN

        def build_huffman_tree(data):
            frequency = defaultdict(int)
            for symbol in data:
                frequency[symbol] += 1

            heap = [[weight, [symbol, ""]] for symbol, weight in frequency.items()]
            heapq.heapify(heap)

            while len(heap) > 1:
                lo = heapq.heappop(heap)
                hi = heapq.heappop(heap)
                for pair in lo[1:]:
                    pair[1] = '0' + pair[1]
                for pair in hi[1:]:
                    pair[1] = '1' + pair[1]
                heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])

            return heap[0][1:]

        def compress_huffman(data, output_file):
            tree = build_huffman_tree(data)
            huffman_codes = {symbol: code for symbol, code in tree}
            compressed_data = ''.join(huffman_codes[symbol] for symbol in data)

            # Converte a sequência de bits em bytes
            compressed_bytes = bytearray()
            for i in range(0, len(compressed_data), 8):
                byte = compressed_data[i:i+8].zfill(8)
                compressed_bytes.append(int(byte, 2))

            # Salva os dados comprimidos no arquivo binário
            with open(output_file, 'wb') as file:
                file.write(compressed_bytes)

            return compressed_data, huffman_codes


        # Aplica compressão Huffman e salva no arquivo binário
        compressed_huffman_data, huffman_codes = compress_huffman(compressed_data, f'compressed_LZW_huffman_data_{X}.bin')
        dictsHuff.append(huffman_codes)


    compressao(channel_r,'r')
    compressao(channel_g,'g')
    compressao(channel_b,'b')

    def concatena_arquivos_com_cabecalho(arquivos_entrada, arquivo_saida):
        with open(arquivo_saida, 'wb') as saida:
            # Escreve o número de canais no cabeçalho
            saida.write(len(arquivos_entrada).to_bytes(4, byteorder='big'))

            # Escreve os dados de cada canal
            for arquivo_entrada in arquivos_entrada:
                with open(arquivo_entrada, 'rb') as entrada:
                    conteudo = entrada.read()

                    # Escreve o tamanho do canal no cabeçalho
                    saida.write(len(conteudo).to_bytes(4, byteorder='big'))

                    # Escreve os dados do canal
                    saida.write(conteudo)
        
        for arquivo_entrada in arquivos_entrada:
            os.remove(arquivo_entrada)

    # Nomes dos arquivos de entrada
    arquivos_entrada = ['compressed_LZW_huffman_data_r.bin', 'compressed_LZW_huffman_data_g.bin', 'compressed_LZW_huffman_data_b.bin']

    # Nome do arquivo de saída
    arquivo_saida = 'compressed_LZW_huffman_data_combined.bin'

    # Concatena os arquivos com um separador
    concatena_arquivos_com_cabecalho(arquivos_entrada, arquivo_saida)

def carregar_compressao():
    global arquivo_combinado
    arquivo_combinado = filedialog.askopenfilename(title="Selecione um arquivo binário", filetypes=[("Arquivos Binários", "*.bin")])

def reconstruir_imagem():
    def le_arquivo_com_cabecalho(arquivo_entrada):
        with open(arquivo_entrada, 'rb') as entrada:
            # Lê o número de canais do cabeçalho
            num_canais = int.from_bytes(entrada.read(4), byteorder='big')

            # Lista para armazenar os dados de cada canal
            dados_canais = []

            # Lê os dados de cada canal com base no cabeçalho
            for _ in range(num_canais):
                # Lê o tamanho do canal do cabeçalho
                tamanho_canal = int.from_bytes(entrada.read(4), byteorder='big')

                # Lê os dados do canal
                dados = entrada.read(tamanho_canal)

                # Adiciona os dados à lista
                dados_canais.append(list(dados))

        return dados_canais

    dados_r, dados_g, dados_b = le_arquivo_com_cabecalho(arquivo_combinado)

    def descompressao(channel,X):
        indiceCanal = -1
        if X == 'r':
            indiceCanal = 0
        elif X == 'g':
            indiceCanal = 1
        else:
            indiceCanal = 2

        def decompress_huffman(data, huffman_codes):

            #with open(data, 'rb') as file:
            #    compressed_bytes = file.read()

            # Converte os bytes de volta para a sequência de bits
            compressed_data = ''.join(format(byte, '08b') for byte in data)

            # Inverta a tabela Huffman para mapear códigos para símbolos
            inverted_huffman_codes = {code: symbol for symbol, code in huffman_codes.items()}

            result = []
            current_code = ""
            for bit in compressed_data:
                current_code += bit
                if current_code in inverted_huffman_codes:
                    symbol = inverted_huffman_codes[current_code]
                    result.append(symbol)
                    current_code = ""


            return result

        # Descomprime os dados Huffman
        decompressed_data_huffman = decompress_huffman(channel, dictsHuff[indiceCanal])

        
        def lzw_decompress(dictionary, decHUFF):
            result_dec = []

            inverted_dict = {v: k for k, v in dictionary.items()}

            for i in range(0,len(decHUFF)):
                #value = decompressed_data[i]
                value = decHUFF[i]

                found_key = inverted_dict[value]

                for element in found_key:
                    result_dec.append(element)

            return result_dec

        # Descomprimir
        decompressed_data = lzw_decompress(dictsLZW[indiceCanal], decompressed_data_huffman)
        dadosRGB.append(decompressed_data)

    global dadosRGB
    dadosRGB = []
    # Descomprimir e processar cada canal
    #print("TOTAL EM DADOS_CANAIS", len(dados_canais))
    descompressao(dados_r,'r')
    descompressao(dados_g,'g')
    descompressao(dados_b,'b')

    dadosRGB.reverse()

    image_height, image_width = 444, 640
    decompressed_image = np.zeros((image_height, image_width, 3), dtype=np.uint8)
    for canal, valores in enumerate(dadosRGB):
        row, col = 0, 0
        for value in valores:
            decompressed_image[row, col, canal] = value
            col += 1
            if col == image_width:
                col = 0
                row += 1
            if row == image_height:
                break

    cv2.imwrite('Descompressao.bmp',decompressed_image)

    # Tamanho em pixels
    tamanho_pixels = f"Tamanho: {image_width} x {image_height}"

    # Tamanho em kilobytes
    tamanho_kb = decompressed_image.nbytes / 1024
    print("TAMANHO KB ",tamanho_kb)
    tamanho_kb_str = f"Tamanho em KB: {int(tamanho_kb)} KB"

    label_tamanho.config(text=f"{tamanho_pixels}\n{tamanho_kb_str}")

    label_imagem_original.config(text="Imagem Reconstruída")

    decompressed_image = decompressed_image[:, :, ::-1]
    decompressed_image = Image.fromarray(decompressed_image)
    imagem_original.image = ImageTk.PhotoImage(decompressed_image)
    canvas_imagem_original.config(width=image_width, height=image_height)
    canvas_imagem_original.create_image(0, 0, anchor=tk.NW, image=imagem_original.image)

# Inicialização da aplicação Tkinter
root = tk.Tk()
root.title("Visualizador de Imagem")

# Frame da esquerda
frame_esquerda = ttk.Frame(root, padding=10)
frame_esquerda.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Botão para carregar imagem
btn_carregar_imagem = ttk.Button(frame_esquerda, text="Carregar Imagem", command=carregar_imagem)
btn_carregar_imagem.grid(row=0, column=0, pady=5)

# Label para mostrar as dimensões e o tamanho em KB da imagem
label_tamanho = ttk.Label(frame_esquerda, text="Tamanho: N/A")
label_tamanho.grid(row=4, column=0, pady=5)

# Botão para aplicar compressão
btn_aplicar_compressao = ttk.Button(frame_esquerda, text="Aplicar Compressão", command=aplicar_compressao)
btn_aplicar_compressao.grid(row=1, column=0, pady=5)

# Botão para carregar compressão
btn_carregar_compressao = ttk.Button(frame_esquerda, text="Carregar Compressão", command=carregar_compressao)
btn_carregar_compressao.grid(row=2, column=0, pady=5)

# Botão para reconstruir a imagem
btn_reconstruir_imagem = ttk.Button(frame_esquerda, text="Reconstruir a Imagem", command=reconstruir_imagem)
btn_reconstruir_imagem.grid(row=3, column=0, pady=5)

# Frame da direita
frame_direita = ttk.Frame(root, padding=10)
frame_direita.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

# Label "Imagem Original"
global label_imagem_original
label_imagem_original = ttk.Label(frame_direita, text="Imagem Original")
label_imagem_original.grid(row=0, column=0, pady=5)

# Canvas para exibir a imagem original
canvas_imagem_original = tk.Canvas(frame_direita, bg="white")
canvas_imagem_original.grid(row=1, column=0, pady=5)

# Imagem original (será atualizada quando uma imagem for carregada)
imagem_original = ImageTk.PhotoImage(Image.new("RGB", (1, 1)))

# Imagem comprimida e binário comprimido
imagem_comprimida = None
binario_comprimido = None

# Iniciar a interface
root.mainloop()
