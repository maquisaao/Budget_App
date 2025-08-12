import re
import os
import httpx
import tkinter as tk
from tkinter import messagebox, simpledialog
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("EMAIL_LOGIN")
SENHA = os.getenv("SENHA_LOGIN")

if not EMAIL or not SENHA:
    raise ValueError("⚠️ Configure EMAIL_LOGIN e SENHA_LOGIN no arquivo .env")

def Sugador(info, email, senha, model_device):
    produtos = []
    try:
        with httpx.Client(base_url="https://flp.distribuidoracp.com.br") as client:
            client.post(
                "/conta/acessar",
                data={"email": email, "password": senha},
                headers={
                    "origin": "https://flp.distribuidoracp.com.br",
                    "referer": "https://flp.distribuidoracp.com.br/conta/acessar",
                },
            )

            busca = client.get(
                "/index.php", params={"route": "product/search", "search": info}
            )

            resultado = BeautifulSoup(busca.text, "html.parser")
            produtos_html = resultado.find_all("div", "product-list")

            palavras_modelo = model_device.lower().split()

            for produto in produtos_html:
                nome = produto.find("h4").text.strip()
                nome_lower = nome.lower()

                if all(palavra in nome_lower for palavra in palavras_modelo):
                    preco = produto.find("p", "price").text.strip()
                    preco_valor = re.search(r"R\$[\d\.,]+", preco)
                    preco_float = 0.0
                    if preco_valor:
                        preco_str = preco_valor.group()
                        preco_float = float(preco_str.replace("R$", "").replace(".", "").replace(",", "."))
                    produtos.append((nome, preco_float))

            # ordenar alfabeticamente pelo nome do produto
            produtos.sort(key=lambda x: x[0].lower())

            # limitar a 10 resultados
            return produtos[:10]

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro: {e}")
        return []

def calcular_valores(preco_base):
    valor_total = preco_base * 3
    return {
        "Pix": round(valor_total * 1.15, 2),
        "Cartão": round(valor_total * 1.40, 2),
        "Dinheiro": round(valor_total * 1.10, 2)
    }

class BudgetCellApp:
    def __init__(self, root):
        self.root = root
        root.title("BudgetCell - Orçamento de Peças")

        # Modelo
        tk.Label(root, text="Modelo do aparelho:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_modelo = tk.Entry(root, width=40)
        self.entry_modelo.grid(row=0, column=1, padx=5, pady=5)

        # Defeito
        tk.Label(root, text="Defeito:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_defeito = tk.Entry(root, width=40)
        self.entry_defeito.grid(row=1, column=1, padx=5, pady=5)

        # Botão buscar
        self.btn_buscar = tk.Button(root, text="Buscar Produtos", command=self.buscar_produtos)
        self.btn_buscar.grid(row=2, column=0, columnspan=2, pady=10)

        # Frame para Listbox + Scrollbar
        frame_lista = tk.Frame(root)
        frame_lista.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        # Lista de produtos
        self.listbox = tk.Listbox(frame_lista, width=70, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        # Scrollbar vertical
        self.scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Liga scrollbar com listbox
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.bind('<Double-1>', self.selecionar_produto)

        # Botão escolher
        self.btn_escolher = tk.Button(root, text="Escolher Produto", command=self.selecionar_produto)
        self.btn_escolher.grid(row=4, column=0, columnspan=2, pady=10)

        # Resultado dos valores
        self.resultado_text = tk.Text(root, width=70, height=7, state='disabled')
        self.resultado_text.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

    def buscar_produtos(self):
        modelo = self.entry_modelo.get().strip()
        defeito = self.entry_defeito.get().strip()

        if not modelo or not defeito:
            messagebox.showwarning("Aviso", "Por favor, preencha modelo e defeito.")
            return

        self.listbox.delete(0, tk.END)
        self.resultado_text.configure(state='normal')
        self.resultado_text.delete(1.0, tk.END)
        self.resultado_text.configure(state='disabled')

        info = f"{defeito} {modelo}"

        produtos = Sugador(info, EMAIL, SENHA, modelo)

        if not produtos:
            messagebox.showinfo("Resultado", "Nenhum produto encontrado.")
            return

        for i, (nome, preco) in enumerate(produtos, 1):
            self.listbox.insert(tk.END, f"{i}) {nome} - R$ {preco:.2f}")

        self.produtos = produtos

    def selecionar_produto(self, event=None):
        selecionado = self.listbox.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto da lista.")
            return
        index = selecionado[0]
        nome, preco = self.produtos[index]

        valores = calcular_valores(preco)

        texto = f"Produto escolhido:\n{nome}\n\nValores para o cliente:\n"
        for forma, valor in valores.items():
            texto += f"{forma}: R$ {valor:.2f}\n"

        self.resultado_text.configure(state='normal')
        self.resultado_text.delete(1.0, tk.END)
        self.resultado_text.insert(tk.END, texto)
        self.resultado_text.configure(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetCellApp(root)
    root.mainloop()
