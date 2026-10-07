# 📦 Auto WMS — Automação de Processos WMS com Python

Projeto de portfólio desenvolvido em Python para demonstrar automações de cadastro e atualização de produtos em um sistema WMS (Warehouse Management System).

A solução combina **Python, Pandas, Excel, PyAutoGUI e Docker** e possui três formas de execução:

1. **DRY-RUN** — valida Excel e lógica sem realizar cliques;
2. **Simulação visual** — PyAutoGUI clica e digita de verdade em uma interface WMS fictícia dentro de um desktop virtual Docker;
3. **Execução real futura** — prevista para um ambiente gráfico autorizado, após validação das coordenadas e configuração do WMS.

> Todos os dados e telas demonstrativas deste repositório são fictícios.

## 🎯 Objetivo

Demonstrar uma aplicação prática de Python na automação de processos logísticos, incluindo leitura e validação de Excel, cadastro automatizado de itens, alteração de unidade de medida, simulação segura do fluxo e execução reproduzível por Docker.

## ⚙️ Automações

### Cadastro de produtos

`automacao_cadastro_item_wms.py`

Lê a aba `cadastro_itens` do arquivo `dados_exemplo_wms.xlsx`.

### Alteração de unidade de medida

`automacao_alteracao_unidade_medida.py`

Lê a aba `alteracao_unidade_medida` do mesmo arquivo.

## 🧪 Planilha de demonstração

`dados_exemplo_wms.xlsx` contém dados fictícios e duas abas:

| Aba | Finalidade | Registros |
|---|---|---:|
| `cadastro_itens` | Cadastro de produtos | 10 |
| `alteracao_unidade_medida` | Atualização de unidade | 10 |

## 🧰 Tecnologias

- Python 3.12
- Pandas
- openpyxl
- PyAutoGUI
- Docker
- Docker Compose
- Chromium
- Xvfb
- x11vnc
- noVNC
- Excel

## 📁 Estrutura

```text
auto-wms/
├── automacao_alteracao_unidade_medida.py
├── automacao_cadastro_item_wms.py
├── simulacao_visual_wms.py
├── dados_exemplo_wms.xlsx
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── docker/
│   └── start-simulation.sh
├── mock_wms/
│   ├── cadastro.html
│   └── alteracao.html
└── README.md
```

# 1. 🧪 Teste DRY-RUN

Construa a imagem:

```powershell
docker compose build
```

Cadastro:

```powershell
docker compose run --rm cadastro-item
```

Alteração:

```powershell
docker compose run --rm alteracao-unidade
```

Nesse modo o terminal mostra o que seria feito, mas nenhuma interface é clicada.

# 2. 🖥️ Simulação visual com PyAutoGUI

Neste modo o projeto cria um monitor virtual Linux dentro do Docker, abre o Chromium em uma interface WMS fictícia e usa PyAutoGUI para clicar e digitar de verdade nessa tela. O noVNC permite assistir à execução pelo navegador do Windows.

```text
Docker
  ↓
Xvfb (monitor virtual)
  ↓
Chromium + WMS fictício
  ↓
PyAutoGUI
  ↓
Excel
  ↓
Cliques e digitação reais na tela virtual
  ↓
noVNC
  ↓
Navegador do Windows
```

## Cadastro visual

Execute:

```powershell
docker compose up simulacao-cadastro
```

Depois abra no navegador:

```text
http://localhost:6080/vnc.html?autoconnect=1&resize=scale
```

A automação aguarda cerca de **20 segundos** antes de iniciar para dar tempo de abrir a tela. Você verá o mouse preencher e salvar os 10 produtos fictícios.

## Alteração visual

Encerre a simulação anterior com `Ctrl+C` e execute:

```powershell
docker compose up simulacao-alteracao
```

Abra:

```text
http://localhost:6081/vnc.html?autoconnect=1&resize=scale
```

Você verá o PyAutoGUI pesquisar cada item fictício, preencher as novas unidades e salvar as alterações.

## Encerrar

No terminal:

```text
Ctrl+C
```

Depois, se desejar limpar containers e rede:

```powershell
docker compose down
```

# 3. 🔐 Execução real futura

A simulação visual roda integralmente dentro do Docker e **não controla a área de trabalho do Windows**.

Uma execução real com PyAutoGUI contra um WMS verdadeiro precisa ocorrer em um ambiente gráfico autorizado e com URL, coordenadas, resolução, escala e acesso devidamente validados.

## 🧱 Arquitetura

Os scripts principais utilizam funções com responsabilidades separadas para carregamento de dados, validação, ações de interface, processamento de registros, tratamento básico de erros e ponto de entrada `main()`.

A simulação visual possui um script separado (`simulacao_visual_wms.py`) para controlar exclusivamente a interface fictícia.

## ⚠️ Segurança

- Nenhuma credencial real é versionada;
- URLs internas não são incluídas no repositório;
- A planilha contém apenas dados fictícios;
- DRY-RUN permanece disponível para teste sem interface;
- A simulação visual usa somente uma tela local e fictícia;
- A execução real permanece separada da demonstração pública.

## 📌 Status

| Componente | Status |
|---|---|
| Leitura do Excel | ✅ Validado |
| Docker | ✅ Validado |
| Docker Compose | ✅ Validado |
| DRY-RUN cadastro | ✅ Validado |
| DRY-RUN alteração | ✅ Validado |
| Simulação visual — cadastro | ✅ Validado |
| Simulação visual — alteração | ✅ Validado |
| PyAutoGUI em ambiente virtual | ✅ Validado |
| noVNC | ✅ Validado |
| WMS real | ⏳ Validação futura |

As duas automações foram validadas em ambiente Docker utilizando uma interface WMS fictícia, dados demonstrativos e PyAutoGUI executando interações reais dentro de um desktop virtual.

A integração com um ambiente WMS real não faz parte da demonstração pública e permanece como etapa futura.
## 👨‍💻 Autor

**Diego Hernando Ferreira**

Projeto de portfólio voltado para automação, logística, dados e melhoria de processos.


## 🔁 Persistência da simulação visual

Depois que os 10 registros são processados, o container continua ativo para manter o noVNC disponível. O script também monitora o processo `websockify/noVNC` e tenta reiniciá-lo automaticamente se ele cair.

Use `Ctrl+C` no terminal para encerrar a simulação e `docker compose down` para limpar os containers/rede.


## 🛠️ Diagnóstico do ambiente gráfico

O script aguarda o `Xvfb` responder antes de iniciar o PyAutoGUI. Isso evita falhas intermitentes como `Can't connect to display ":99"`.

Se o Xvfb não iniciar corretamente, o terminal mostra automaticamente o conteúdo de `/tmp/xvfb.log`.
