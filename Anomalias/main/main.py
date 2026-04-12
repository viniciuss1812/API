from fastapi import FastAPI, UploadFile
import os
import shutil
import ijson
import json
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import io
from collections import Counter
from models.Gaussiana import Gaussiana
from models.ZScore import ZScore


app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

if not os.path.exists(UPLOAD_DIR):
    print("Pasta uploads não existe, criando...")
    os.makedirs(UPLOAD_DIR)
else:
    print("Pasta uploads já existe")


@app.post("/upload/")
async def upload_arquivo(dados: UploadFile):

    caminho_arquivo = os.path.join(UPLOAD_DIR, dados.filename)

    with open(caminho_arquivo, "wb") as buffer:
        shutil.copyfileobj(dados.file, buffer)

    primeiros = []
    limite = 5

    with open(caminho_arquivo, "rb") as f: 
        parser = ijson.items(f, "item")
      

        for item in parser:
            primeiros.append(item)
            if len(primeiros) == limite:
                break

    return {
        
        "msg": "Arquivo salvo com sucesso",
        "arquivo": dados.filename,
        "preview": primeiros, 
    }

@app.get("/transactions/")
def getallcontas():
    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    return {
        "mensagem": "Retornando as 100 primeiras transações da base de dados",
        "transações": transacoes[:100]
    }


@app.get("/transactions/{id}")
def transactionsid(id: int):
    with open('transacoes_treino', 'r', encoding='utf-8') as arquivo:
       transacoes = json.load(arquivo)

       for transacao in transacoes: 
           if transacao["id"] == id:
               return transacao
           
    return {"erro" : "Transação não encontrado"}


    
@app.get("/contas/")
def getallcontas():
    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    contas = [item["conta"] for item in transacoes[:100]]

    return {
        "mensagem": "Retornando as 100 primmeiras contas da base de dados",
        "contas": contas
    }

@app.get("/calculogaussiana/")
def gaussiana():
    model = Gaussiana("uploads/transacoes_treino.json")

    return StreamingResponse(
        model.image,
        media_type="image/png"
    )


@app.get("/calculozscore/")
def zscore():

    model = ZScore("uploads/transacoes_treino.json")

    return StreamingResponse(
        model.image,
        media_type="image/png"
    )




@app.get("/cidadesmaisanomalas/")
def cidadesmaisanomalas():
    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    cidades_fraude = [t["cidade"] for t in transacoes if t["is_fraude"] == 1]

    contagem = Counter(cidades_fraude)

    cidades = [c[0] for c in contagem.most_common(10)]
    valores = [c[1] for c in contagem.most_common(10)]

    plt.figure(figsize=(10, 5))
    plt.bar(cidades, valores)
    plt.title("Top 10 Cidades com Mais Anomalias")
    plt.xticks(rotation=45)

    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")



@app.get("/numerodefraudes/")
def numerodefraudes():
    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    fraudes = sum(1 for t in transacoes if t["is_fraude"] == 1)
    nao_fraudes = sum(1 for t in transacoes if t["is_fraude"] == 0)

    labels = ["Fraudes", "Não fraudes"]
    valores = [fraudes, nao_fraudes]

    plt.figure()
    plt.bar(labels, valores)
    plt.title("Distribuição de Fraudes")

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

@app.get("/fraudes/tipos/")
def fraudes_tipos():

    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    tipos = [
        t["tipo_transacao"]
        for t in transacoes
        if t["is_fraude"] == 1
    ]

    contagem = Counter(tipos)

    tipos_top = [t[0] for t in contagem.most_common(10)]
    valores_top = [t[1] for t in contagem.most_common(10)]

    plt.figure(figsize=(10, 5))
    plt.bar(tipos_top, valores_top)
    plt.title("Tipos de Transação com Mais Fraudes")
    plt.xticks(rotation=45)

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

@app.get("/horariofraudes/")
def fraudes_horarios():

    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    horas = [
        t["hora"][:2]
        for t in transacoes
        if t["is_fraude"] == 1
    ]

    contagem = Counter(horas)

    horas_top = [h[0] for h in contagem.most_common(10)]
    valores_top = [h[1] for h in contagem.most_common(10)]

    plt.figure(figsize=(10, 5))
    plt.bar(horas_top, valores_top)
    plt.title("Horários com Mais Fraudes")
    plt.xlabel("Hora do Dia")
    plt.ylabel("Quantidade")
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")


@app.get("/numerodetentativas/")
def maiores_tentativas():

    with open('uploads/transacoes_treino.json', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)

    suspeitas = [
        t for t in transacoes
        if t.get("is_fraude") == 1 and t.get("tentativas", 0) >= 2
    ]

   
    if not suspeitas:
        return {"msg": "Nenhuma fraude com 2+ tentativas encontrada"}

  
    valor = [t["valor"] for t in suspeitas]
    tentativas = [t["tentativas"] for t in suspeitas]

   
    plt.figure(figsize=(14, 6))

    plt.bar(valor, tentativas, color="#d62728")

    plt.title("Numero de Tentativas Anômalas ")
    plt.xlabel("Valores")
    plt.ylabel("Número de Tentativas")

    plt.grid(axis="y", linestyle=":", alpha=0.5)

    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=300)
    buf.seek(0)
    plt.close()

    return StreamingResponse(buf, media_type="image/png")

