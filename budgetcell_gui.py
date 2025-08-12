import re
import os
import httpx
import threading
import tkinter as tk
from tkinter import messagebox
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

            produtos.sort(key=lambda x: x[0].lower())

            return produtos[:10]

    except Exception as e:
        # Usar print aqui pois messagebox não pode ser chamado fora da thread principal
        print(f"Erro no Sugador: {e}")
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
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        largura = screen_width // 2
        altura = screen_height

        pos_x = screen_width - largura
        pos_y = 0
        root.geometry(f"{largura}x{altura}+{pos_x}+{pos_y}")

        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(3, weight=1)
        root.grid_rowconfigure(5, weight=1)

        root.title("BudgetApp By Max")

        tk.Label(root, text="Modelo do aparelho:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_modelo = tk.Entry(root, width=40)
        self.entry_modelo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Defeito:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_defeito = tk.Entry(root, width=40)
        self.entry_defeito.grid(row=1, column=1, padx=5, pady=5)

        self.entry_modelo.bind('<Return>', lambda event: self.buscar_produtos())
        self.entry_defeito.bind('<Return>', lambda event: self.buscar_produtos())

        self.btn_buscar = tk.Button(root, text="Buscar Produtos", command=self.buscar_produtos)
        self.btn_buscar.grid(row=2, column=0, columnspan=2, pady=10)

        frame_lista = tk.Frame(root)
        frame_lista.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.listbox = tk.Listbox(frame_lista, width=70, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.bind('<Double-1>', self.selecionar_produto)

        self.btn_escolher = tk.Button(root, text="Escolher Produto", command=self.selecionar_produto)
        self.btn_escolher.grid(row=4, column=0, columnspan=2, pady=10)

        self.frame_valores = tk.Frame(root)
        self.frame_valores.grid(row=0, column=2, rowspan=6, padx=10, pady=10, sticky="n")

        self.lbl_valores_titulo = tk.Label(self.frame_valores, text="Valores para o cliente", font=("Arial", 14, "bold"))
        self.lbl_valores_titulo.pack(pady=(0,10))

        # Label para mensagem de status
        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=6, column=0, columnspan=3, sticky="w", padx=5)

    def limpar_valores(self):
        for widget in self.frame_valores.winfo_children():
            if widget != self.lbl_valores_titulo:
                widget.destroy()

    def buscar_produtos(self):
        modelo = self.entry_modelo.get().strip()
        defeito = self.entry_defeito.get().strip()

        if not modelo or not defeito:
            messagebox.showwarning("Aviso", "Por favor, preencha modelo e defeito.")
            return

        # Mostrar mensagem de carregando
        self.status_label.config(text="Carregando...")

        # Desabilitar botão para evitar cliques múltiplos
        self.btn_buscar.config(state=tk.DISABLED)

        # Limpar lista e valores
        self.listbox.delete(0, tk.END)
        self.limpar_valores()

        # Rodar busca em thread para não travar GUI
        threading.Thread(target=self.busca_thread, args=(defeito, modelo), daemon=True).start()

    def busca_thread(self, defeito, modelo):
        info = f"{defeito} {modelo}"
        produtos = Sugador(info, EMAIL, SENHA, modelo)

        # Atualizar GUI na thread principal
        self.root.after(0, self.finalizar_busca, produtos)

    def finalizar_busca(self, produtos):
        self.status_label.config(text="")
        self.btn_buscar.config(state=tk.NORMAL)

        self.entry_modelo.delete(0, tk.END)
        self.entry_defeito.delete(0, tk.END)

        if not produtos:
            messagebox.showinfo("Resultado", "Nenhum produto encontrado.")
            return

        self.produtos = produtos
        for i, (nome, preco) in enumerate(produtos, 1):
            self.listbox.insert(tk.END, f"R$ {preco:.2f} - {nome}")

    def selecionar_produto(self, event=None):
        selecionado = self.listbox.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto da lista.")
            return
        index = selecionado[0]
        nome, preco = self.produtos[index]

        valores = calcular_valores(preco)

        self.limpar_valores()

        cores = {
            "Pix": "#a0d468",
            "Cartão": "#4a89dc",
            "Dinheiro": "#ed5565"
        }

        for forma, valor in valores.items():
            frame_caixa = tk.Frame(self.frame_valores, bg=cores[forma], bd=2, relief="groove", padx=10, pady=10)
            frame_caixa.pack(fill='x', pady=5)

            lbl_forma = tk.Label(frame_caixa, text=forma, bg=cores[forma], fg="white", font=("Arial", 12, "bold"))
            lbl_forma.pack(anchor='w')

            lbl_valor = tk.Label(frame_caixa, text=f"R$ {valor:.2f}", bg=cores[forma], fg="white", font=("Arial", 14))
            lbl_valor.pack(anchor='w')

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetCellApp(root)
    root.mainloop()
