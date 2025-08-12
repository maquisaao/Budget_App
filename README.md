# Conecte-se comigo 

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/maxw-pinheiro/)
[![Instagram](https://img.shields.io/badge/-Instagram-%23E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/omaxwilson/)
[![WhatsApp](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/5548999089562)

## Minhas Skills:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![C#](https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white)
![Bootstrap](https://img.shields.io/badge/-boostrap-0D1117?style=for-the-badge&logo=bootstrap&labelColor=0D1117)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
 ![.NET](https://img.shields.io/badge/.NET-5C2D91?style=for-the-badge&logo=.net&logoColor=white)
 ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-000?style=for-the-badge&logo=postgresql)
 ![MySQL](https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white)
 ![Git](https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white)
 ![Figma](https://img.shields.io/badge/Figma-696969?style=for-the-badge&logo=figma&logoColor=figma)
 ![Vscode](https://img.shields.io/badge/Vscode-007ACC?style=for-the-badge&logo=visual-studio-code&logoColor=white)

 ## GitHub Stats
 ![GitHub Stats](https://github-readme-stats.vercel.app/api?username=maquisaao&theme=transparent&bg_color=000&border_color=30A3DC&show_icons=true&icon_color=30A3DC&title_color=E94D5F&text_color=FFF)
 
 
BudgetCell
Projeto em desenvolvimento para facilitar a pesquisa e cálculo de valores de peças de celular usadas em assistência técnica.

Descrição
O BudgetCell é uma ferramenta que automatiza a busca por preços de peças em distribuidores online, facilitando o orçamento rápido para técnicos de celulares. O aplicativo realiza login no site do distribuidor, busca as peças baseadas na descrição do defeito, marca e modelo, e apresenta os resultados para o usuário.

Funcionalidades atuais
Recebe entrada do usuário (marca, modelo e defeito do aparelho)

Realiza login seguro usando credenciais armazenadas em arquivo .env

Busca e exibe os principais resultados de peças no distribuidor

Permite a escolha da peça desejada

Calcula o valor final baseado no preço da peça multiplicado por 3

Apresenta opções de pagamento com acréscimos para Pix (+10%), cartão (+20%) e dinheiro (preço normal)

Loop para novas buscas até o usuário decidir encerrar

Próximos passos e possibilidades futuras
Implementar interface gráfica para facilitar o uso

Adicionar suporte para múltiplos distribuidores

Criar sistema de armazenamento local dos orçamentos realizados

Exportar relatórios em PDF para clientes

Implementar autenticação via OAuth ou outros métodos seguros

Construir versão mobile para acesso rápido em campo

Automatizar atualizações dos preços com agendamento

Integrar notificações via WhatsApp ou SMS para envio dos orçamentos aos clientes

Como usar
Clone este repositório

Crie um arquivo .env na raiz com suas credenciais:

ini
Copy
Edit
EMAIL_LOGIN=seu_email_aqui
SENHA_LOGIN=sua_senha_aqui
Instale as dependências:

nginx
Copy
Edit
pip install -r requirements.txt
Execute o script:

css
Copy
Edit
python main.py
