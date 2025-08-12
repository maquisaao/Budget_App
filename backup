import re
import os
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
EMAIL = os.getenv("EMAIL_LOGIN")
SENHA = os.getenv("SENHA_LOGIN")

if not EMAIL or not SENHA:
    raise ValueError("⚠️ Configure EMAIL_LOGIN e SENHA_LOGIN no arquivo .env")

def Sugador(info, email, senha):
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

            for produto in produtos_html[:3]:
                nome = produto.find("h4").text.strip()
                preco = produto.find("p", "price").text.strip()
                preco_valor = re.search(r"R\$[\d\.,]+", preco)
                preco_float = 0.0
                if preco_valor:
                    preco_str = preco_valor.group()
                    preco_float = float(preco_str.replace("R$", "").replace(".", "").replace(",", "."))
                produtos.append((nome, preco_float))
        return produtos

    except Exception as e:
        print("❌ Ocorreu um erro:", e)
        return []

def mostrar_opcoes(produtos):
    print("\n📦 Resultados encontrados:")
    for i, (nome, preco) in enumerate(produtos, 1):
        print(f"{i}) Nome: {nome[:150]}")
        print(f"   Preço: R$ {preco:.2f}")
        print()

def escolher_produto(produtos):
    while True:
        try:
            escolha = int(input(f"Escolha uma das opções (1-{len(produtos)}): "))
            if 1 <= escolha <= len(produtos):
                return produtos[escolha - 1]
            print("Escolha um número válido.")
        except ValueError:
            print("Digite um número válido.")

def calcular_valores(preco_base):
    valor_total = preco_base * 3
    return {
        "pix": round(valor_total * 1.15, 2),
        "cartao": round(valor_total * 1.40, 2),
        "dinheiro": round(valor_total, 2)
    }

def main():
    print("Seja bem-vindo ao BudgetCell!")
    while True:
        model_device = input("Informe o modelo do aparelho: \n").strip()
        fault_device = input("Informe o defeito do aparelho: \n").strip()

        info = f"{fault_device} {model_device}"

        produtos = Sugador(info, EMAIL, SENHA)
        if not produtos:
            print("Nenhum produto encontrado ou erro na busca.")
            continue

        mostrar_opcoes(produtos)

        nome_sel, preco_sel = escolher_produto(produtos)
        print(f"\nVocê escolheu: {nome_sel}")
        print(f"Preço base da peça: R$ {preco_sel:.2f}")

        valores = calcular_valores(preco_sel)
        print("\n💰 Valor final para o cliente (peça x 3):")
        print(f"1) Pix: R$ {valores['pix']:.2f}")
        print(f"2) Cartão(até 10x sem juros): R$ {valores['cartao']:.2f}")
        print(f"3) Dinheiro: R$ {valores['dinheiro']:.2f}")

        continuar = input("\nDeseja fazer outra busca? (s/n): ").strip().lower()
        if continuar != "s":
            print("Obrigado por usar o BudgetCell! Até mais!")
            break

if __name__ == "__main__":
    main()
