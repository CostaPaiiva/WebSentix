# Gerar automaticamente um relatório em PDF com os resultados do treinamento.
# Ele transforma isso:
# Ranking dos modelos
# Qual foi o melhor
# Qual score
# Gráficos
# Informações do dataset

# Importa o tamanho de página A4 (padrão de folha) para usar na criação do PDF
from reportlab.lib.pagesizes import A4

# Importa o "canvas", que é a área de desenho do PDF
# É nele que escrevemos textos, desenhamos linhas e inserimos imagens
from reportlab.pdfgen import canvas

# Importa o ImageReader, que serve para ler imagens (PNG, JPG, etc)
# e permitir que elas sejam inseridas dentro do PDF
from reportlab.lib.utils import ImageReader

# Define a função que vai gerar o arquivo PDF
# caminho_pdf = onde o PDF será salvo
# texto = texto do relatório (resultado.txt)
# imagem = caminho da imagem do gráfico (ranking.png)
def gerar_pdf(caminho_pdf, texto, imagem):
    # Cria o "papel" do PDF usando o tamanho A4
    c = canvas.Canvas(caminho_pdf, pagesize=A4)
    largura, altura = A4
    # Define a posição inicial vertical (começa perto do topo da página)
    y = altura - 40
    # Define a fonte em negrito e tamanho 16 para o título
    c.setFont("Helvetica-Bold", 16)
    # Escreve o título do relatório no PDF
    c.drawString(40, y, "Relatório Automático - FábricaDeModelo")
    # Desce a posição Y para escrever o próximo conteúdo mais abaixo
    y -= 40
    # Define a fonte normal, tamanho 10, para o texto do relatório
    c.setFont("Helvetica", 10)

    for linha in texto.split("\n"):
        # Se a posição Y ficar muito baixa (perto do final da página)
        # ele cria automaticamente uma nova página
        if y < 100:
            c.showPage()            # Finaliza a página atual e cria uma nova
            y = altura - 40         # Volta o cursor para o topo da nova página
        # Escreve a linha atual do texto na posição (40, y)
        c.drawString(40, y, linha)
        # Desce o cursor para escrever a próxima linha abaixo
        y -= 14
    # Cria uma nova página só para colocar o gráfico/imagem
    c.showPage()
    # Insere a imagem (ranking.png) dentro do PDF
    # 40, 100 = posição da imagem na página
    # width=500 = largura da imagem no PDF
    # preserveAspectRatio=True = mantém a proporção da imagem
    c.drawImage(ImageReader(imagem), 40, 100, width=500, preserveAspectRatio=True)
    # Salva e fecha definitivamente o arquivo PDF no disco
    c.save()
