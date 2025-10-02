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
        print(f"Verifique a conexao e tente novamente. {e}")
        return []

def calcular_valores(preco_base):
    return {
        "Paralela": round(preco_base + 200, 2),
        "Premium": round(preco_base + 300, 2),
        "Original": round(preco_base + 300, 2)
    }

class PlaceholderEntry(tk.Entry):
    def __init__(self, master=None, placeholder="Digite aqui", color="grey", **kwargs):
        super().__init__(master, **kwargs)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self["fg"]

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self["fg"] == self.placeholder_color:
            self.delete(0, tk.END)
            self["fg"] = self.default_fg_color

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self["fg"] = self.placeholder_color

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

        root.title("BudgetApp By Max")
        
        # --- Guardar valores fixados ---
        self.valores_fixados = {"Paralela": None, "Premium": None, "Original": None}

        # --- Campos com placeholder ---
        tk.Label(root, text="Modelo do aparelho:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_modelo = PlaceholderEntry(root, width=50, placeholder="Exemplo: iPhone 12 Pro Max")
        self.entry_modelo.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Defeito:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_defeito = PlaceholderEntry(root, width=50, placeholder="Exemplo: Bateria, Tela, Tampa, etc")
        self.entry_defeito.grid(row=1, column=1, padx=5, pady=5)

        self.entry_modelo.bind('<Return>', lambda event: self.buscar_produtos())
        self.entry_defeito.bind('<Return>', lambda event: self.buscar_produtos())

        self.btn_buscar = tk.Button(root, text="Buscar", command=self.buscar_produtos)
        self.btn_buscar.grid(row=2, column=0, pady=10, sticky="ew", padx=(5,0))

        self.btn_reiniciar = tk.Button(root, text="Reiniciar", command=self.reiniciar)
        self.btn_reiniciar.grid(row=2, column=1, pady=10, sticky="ew", padx=(0,5))

        frame_lista = tk.Frame(root)
        frame_lista.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        self.listbox = tk.Listbox(frame_lista, width=70, height=10)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(frame_lista, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.listbox.bind('<Double-1>', self.selecionar_produto)

        self.btn_escolher = tk.Button(root, text="Gerar valores", command=self.selecionar_produto)
        self.btn_escolher.grid(row=4, column=0, columnspan=2, pady=10)

        self.frame_valores = tk.Frame(root)
        self.frame_valores.grid(row=0, column=2, rowspan=6, padx=10, pady=10, sticky="n")

        self.lbl_valores_titulo = tk.Label(self.frame_valores, text="Valores a cobrar", font=("Arial", 14, "bold"))
        self.lbl_valores_titulo.pack(pady=(0,10))

        self.status_label = tk.Label(root, text="", fg="blue")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky="w", padx=5)

        # --- Texto final AGORA LOGO ABAIXO DO ORÇAR ---
        self.texto_final = tk.Text(root, height=10, wrap="word")
        self.texto_final.grid(row=6, column=0, columnspan=3, padx=5, pady=10, sticky="nsew")

        self.btn_copiar = tk.Button(root, text="GERAR E COPIAR MENSAGEM", command=self.copiar_texto)
        self.btn_copiar.grid(row=7, column=0, columnspan=3, pady=5)

    def limpar_valores(self):
        for widget in self.frame_valores.winfo_children():
            if widget != self.lbl_valores_titulo:
                widget.destroy()

    def buscar_produtos(self):
        modelo = self.entry_modelo.get().strip()
        defeito = self.entry_defeito.get().strip()

        # Evita enviar placeholder como pesquisa
        if modelo in ["Exemplo: iPhone 12 Pro Max", ""] or defeito in ["Exemplo: Bateria, Tela, Tampa, etc", ""]:
            messagebox.showwarning("Aviso", "Por favor, preencha os dois campos.")
            return

        self.status_label.config(text="CARREGANDO...")
        self.btn_buscar.config(state=tk.DISABLED)
        self.listbox.delete(0, tk.END)
        self.limpar_valores()
        threading.Thread(target=self.busca_thread, args=(defeito, modelo), daemon=True).start()

    def busca_thread(self, defeito, modelo):
        info = f"{defeito} {modelo}"
        produtos = Sugador(info, EMAIL, SENHA, modelo)
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
            "Paralela": "#ed5565",
            "Premium": "#a0d468",
            "Original": "#4a89dc"
        }

        for forma in ["Paralela", "Premium", "Original"]:
            # Se já existe valor fixado, usa ele
            valor_mostrar = self.valores_fixados[forma] if self.valores_fixados[forma] is not None else valores[forma]

            frame_caixa = tk.Frame(self.frame_valores, bg=cores[forma], bd=2, relief="groove", padx=10, pady=10)
            frame_caixa.pack(fill='x', pady=5)

            lbl_forma = tk.Label(frame_caixa, text=forma, bg=cores[forma], fg="white", font=("Arial", 12, "bold"))
            lbl_forma.pack(anchor='w')

            lbl_valor = tk.Label(frame_caixa, text=f"R$ {valor_mostrar:.2f}", bg=cores[forma], fg="white", font=("Arial", 14))
            lbl_valor.pack(anchor='w')

            # Botão fixar atualiza valores_fixados
            btn_fixar = tk.Button(frame_caixa, text="Fixar", 
                                  command=lambda f=forma, v=valor_mostrar: self.fixar_valor(f, v))
            btn_fixar.pack(anchor='e', pady=5)

        # Habilitar botão de copiar apenas se todos os 3 valores estiverem fixados
        self.btn_copiar.config(state=tk.NORMAL if all(v is not None for v in self.valores_fixados.values()) else tk.DISABLED)


    def fixar_valor(self, forma, valor):
        self.valores_fixados[forma] = valor
        self.selecionar_produto()  # Atualiza os cards para mostrar os valores fixados

    def copiar_texto(self):
        if not all(v is not None for v in self.valores_fixados.values()):
            messagebox.showwarning("Aviso", "Fixe todos os valores antes de gerar a mensagem.")
            return

        msg = (
            f"✅ Perfeito, CLIENTE! Olhando o modelo e o defeito que você me falou, temos essas opções de peças:\n\n"
            f"Qualidade Paralela - garantia de 3 meses - R$ {self.valores_fixados['Paralela']:.2f}\n"
            "Essa escolha é pra quem procura o preço mais baixo, na maioria dos casos essa qualidade não tem os sensores \
de biometria e/ou proximidade. Recomendado para quem precisa de uma peça 'quebra-galho.\n\n"
            f"Qualidade Premium – garantia de 6 meses – R$ {self.valores_fixados['Premium']:.2f}\n" 
            "As peças premium são aquelas com as mesmas especificações técnicas da Original mas fabricados por outra empresa \
e tem o intuito de entregar toda funcionalidade do aparelho mas com uma qualidade e durabilidade menores. Boa \
opção se você pensa em trocar de celular em até 1 ano e não quer perder valor de mercado quando for vender.\n\n"
            f"Qualidade Original – garantia de 1 ano – R$ {self.valores_fixados['Original']:.2f}\n"
            "Melhor qualidade possível, além de ter a melhor garantia do mercado, você conta com um melhor acabamento e \
maior durabilidade pro seu celular. É a melhor escolha se você pretende dar uso por mais alguns anos ao \
seu aparelho.\n\n"
            "Tempo de serviço é de aproximadamente 2 horas e acompanha Película de Vidro 3D. Podendo ser parcelado em até 12x no cartão de crédito. Oferecemos também a possibilidade de COLETA E ENTREGA do seu aparelho ou REPARO NO SEU ENDEREÇO.\n"
            "Orçamento válido por 24h"
        )

        self.texto_final.delete("1.0", tk.END)
        self.texto_final.insert(tk.END, msg)
        self.root.clipboard_clear()
        self.root.clipboard_append(msg)
        self.root.update()
        messagebox.showinfo("Copiado", "Mensagem copiada para área de transferência!")

    def reiniciar(self):
        self.entry_modelo.delete(0, tk.END)
        self.entry_defeito.delete(0, tk.END)
        self.listbox.delete(0, tk.END)
        self.limpar_valores()
        self.texto_final.delete("1.0", tk.END)
        self.valores_fixados = {"Paralela": None, "Premium": None, "Original": None}
        self.btn_copiar.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = BudgetCellApp(root)
    root.mainloop()
