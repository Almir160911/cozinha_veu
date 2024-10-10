from tkinter.filedialog import askdirectory, askopenfilename
from tkinter.messagebox import askyesnocancel

pasta_computador = askdirectory(title="Selecione uma pasta do computador")
print(pasta_computador)

arquivo_computador = askopenfilename(title="Selecione um arquivo do computador")
print(arquivo_computador)