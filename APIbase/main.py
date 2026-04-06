#primeiro eu vou fazer um exemplo usando um arquivo, pegando 
# o caminho, lendo e fazendo a atv do discord

from fastapi import FastAPI
import json


app = FastAPI()

@app.get("/transactions")
def gettransactions():
    with open('dadosfalsos.txt', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)
        return transacoes



@app.get("/transactions/{id}")
def transactionsid(id: int):
    with open('dadosfalsos.txt', 'r', encoding='utf-8') as arquivo:
       transacoes = json.load(arquivo)

       for transacao in transacoes: 
           if transacao["id"] == id:
               return transacao
           
    return {"erro" : "Não encontrado"}
           
@app.delete("/transactions/{id}")
def deleteusuario (id : int):
    with open ('dadosfalsos.txt', 'r', encoding='utf-8') as arquivo:
        transacoes = json.load(arquivo)
        
        for transacao in transacoes:
            if transacao["id"] == id:
              transacoes.remove(transacao)
            with open('dadosfalsos.txt', 'w', encoding='utf-8') as arquivo:
                json.dump(transacoes, arquivo, indent=2, ensure_ascii=False)

            return {"mensagem": "Transação removida com sucesso"}

    return {"erro": "Transação não encontrada"}


@app.post("/transactions")
def inserir (id: int, tipo: str, descricao: str, valor: float):
    with open('dadosfalsos.txt', 'r', encoding= 'utf-8') as arquivo:
        transacoes = json.load(arquivo)

    nova_transacao = {
        "id": id,
        "type": tipo,
        "description": descricao,
        "amount": valor
    }

    # adiciona na lista
    transacoes.append(nova_transacao)

    # salva no arquivo
    with open('dadosfalsos.txt', 'w', encoding='utf-8') as arquivo:
        json.dump(transacoes, arquivo, indent=2, ensure_ascii=False)

    return {"mensagem": "Transação criada com sucesso"}







