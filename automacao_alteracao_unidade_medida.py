"""Automação para alteração de unidade de medida de produtos em um WMS.

A automação lê a aba ``alteracao_unidade_medida`` do arquivo
``dados_exemplo_wms.xlsx``.

Modos de execução:
- DRY_RUN=true: lê e valida o Excel e simula as ações no terminal, sem clicar.
- DRY_RUN=false: executa as ações reais com PyAutoGUI no computador local.

As coordenadas dependem da resolução, escala do Windows e layout da aplicação.
"""

from pathlib import Path
import os
import time

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = BASE_DIR / "dados_exemplo_wms.xlsx"
ABA_ENTRADA = "alteracao_unidade_medida"

DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "sim",
    "on",
}

COLUNAS_OBRIGATORIAS = {"Item", "Unidade de medida", "Unidade de medida1"}

# Configure a URL do ambiente WMS somente para uma futura execução real.
WMS_URL = "https://seu-wms.exemplo.com/wms/configuracao/produto"

TEMPO_CARREGAMENTO_WMS = 10
TEMPO_ENTRE_ACOES = 1

POS = {
    "pesquisa_avancada": (1201, 294),
    "campo_pesquisa": (643, 287),
    "menu_produto": (108, 487),
    "detalhes": (137, 530),
    "editar_dados_principais": (1151, 218),
    "campo_unidade_medida": (991, 371),
    "opcao_unidade_medida": (970, 420),
    "salvar_dados_principais": (1312, 217),
    "sku": (124, 573),
    "menu_sku": (764, 374),
    "editar_sku": (724, 413),
    "campo_unidade_medida_sku": (755, 376),
    "salvar_sku": (952, 279),
    "fechar": (1319, 157),
}

pyautogui = None


def configurar_interface() -> None:
    """Configura o PyAutoGUI somente quando a execução real for solicitada."""
    global pyautogui

    if DRY_RUN:
        print("Modo DRY-RUN ativo: nenhuma ação será executada na tela.")
        return

    import pyautogui as modulo_pyautogui

    modulo_pyautogui.FAILSAFE = True
    modulo_pyautogui.PAUSE = 0.1
    pyautogui = modulo_pyautogui


def carregar_dados(caminho: Path, aba: str) -> pd.DataFrame:
    """Carrega a aba de entrada e valida as colunas necessárias."""
    if not caminho.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {caminho}")

    try:
        dados = pd.read_excel(caminho, sheet_name=aba)
    except ValueError as erro:
        raise ValueError(f"A aba '{aba}' não foi encontrada em {caminho.name}.") from erro

    faltantes = COLUNAS_OBRIGATORIAS - set(dados.columns)
    if faltantes:
        raise ValueError(
            "A planilha não possui as colunas obrigatórias: "
            + ", ".join(sorted(faltantes))
        )

    return dados


def esperar(segundos: float) -> None:
    """Aguarda apenas durante a execução real."""
    if not DRY_RUN:
        time.sleep(segundos)


def clicar(nome: str) -> None:
    """Clica em uma posição configurada ou registra a ação no modo de teste."""
    if DRY_RUN:
        print(f"  [DRY-RUN] clicar '{nome}' em {POS[nome]}")
        return

    pyautogui.click(*POS[nome])


def escrever(valor: object, interval: float = 0.0) -> None:
    """Digita um valor ou registra a ação no modo de teste."""
    texto = str(valor)

    if DRY_RUN:
        print(f"  [DRY-RUN] digitar: {texto}")
        return

    pyautogui.write(texto, interval=interval)


def pressionar(tecla: str, presses: int = 1, interval: float = 0.0) -> None:
    """Pressiona uma tecla ou registra a ação no modo de teste."""
    if DRY_RUN:
        detalhe = f" x{presses}" if presses > 1 else ""
        print(f"  [DRY-RUN] pressionar '{tecla}'{detalhe}")
        return

    pyautogui.press(tecla, presses=presses, interval=interval)


def atalho(*teclas: str) -> None:
    """Executa um atalho ou registra a ação no modo de teste."""
    if DRY_RUN:
        print(f"  [DRY-RUN] atalho {' + '.join(teclas)}")
        return

    pyautogui.hotkey(*teclas)


def limpar_campo() -> None:
    """Seleciona todo o conteúdo do campo ativo e o remove."""
    atalho("ctrl", "a")
    pressionar("delete")


def abrir_wms() -> None:
    """Abre o WMS ou apenas registra a ação no modo de teste."""
    if DRY_RUN:
        print(f"[DRY-RUN] abrir WMS: {WMS_URL}")
        return

    pressionar("win")
    esperar(1)
    escrever("microsoft edge", interval=0.1)
    pressionar("enter")
    esperar(1)
    escrever(WMS_URL)
    pressionar("enter")
    esperar(TEMPO_CARREGAMENTO_WMS)


def pesquisar_item(item: object) -> None:
    """Pesquisa um item na tela de produtos."""
    clicar("pesquisa_avancada")
    clicar("campo_pesquisa")
    limpar_campo()
    escrever(item)
    pressionar("tab", presses=8, interval=0.05)
    pressionar("enter")
    esperar(TEMPO_ENTRE_ACOES)


def alterar_dados_principais(unidade_medida: object) -> None:
    """Altera a unidade de medida nos dados principais do produto."""
    clicar("menu_produto")
    clicar("detalhes")
    esperar(2)

    clicar("editar_dados_principais")
    esperar(2)

    clicar("campo_unidade_medida")
    limpar_campo()
    escrever(unidade_medida)
    esperar(TEMPO_ENTRE_ACOES)
    clicar("opcao_unidade_medida")
    esperar(TEMPO_ENTRE_ACOES)

    clicar("salvar_dados_principais")
    esperar(5)

    # Mantém o comportamento do script original.
    clicar("salvar_dados_principais")
    esperar(2)


def alterar_sku(unidade_medida_sku: object) -> None:
    """Altera a unidade de medida do SKU do produto."""
    clicar("menu_produto")
    clicar("sku")
    esperar(2)

    clicar("menu_sku")
    clicar("editar_sku")
    esperar(TEMPO_ENTRE_ACOES)

    clicar("campo_unidade_medida_sku")
    limpar_campo()
    escrever(unidade_medida_sku)
    esperar(TEMPO_ENTRE_ACOES)

    clicar("salvar_sku")
    esperar(5)
    clicar("fechar")
    esperar(TEMPO_ENTRE_ACOES)


def processar_itens(dados: pd.DataFrame) -> None:
    """Executa ou simula a alteração para cada linha válida da planilha."""
    total = len(dados)

    for numero, (_, linha) in enumerate(dados.iterrows(), start=1):
        item = linha["Item"]
        unidade_medida = linha["Unidade de medida"]
        unidade_medida_sku = linha["Unidade de medida1"]

        if pd.isna(item) or pd.isna(unidade_medida) or pd.isna(unidade_medida_sku):
            print(f"[{numero}/{total}] Linha ignorada: existem campos obrigatórios vazios.")
            continue

        print(f"[{numero}/{total}] Processando item {item}...")
        pesquisar_item(item)
        alterar_dados_principais(unidade_medida)
        alterar_sku(unidade_medida_sku)
        print(f"[{numero}/{total}] Item {item}: fluxo concluído.")


def main() -> None:
    """Ponto de entrada da automação."""
    try:
        configurar_interface()
        dados = carregar_dados(ARQUIVO_ENTRADA, ABA_ENTRADA)
        print(f"{len(dados)} registro(s) carregado(s) da aba '{ABA_ENTRADA}'.")
        abrir_wms()
        processar_itens(dados)
        print("Automação finalizada.")
    except (FileNotFoundError, ValueError) as erro:
        print(f"Erro de configuração/dados: {erro}")
    except Exception as erro:
        if (
            not DRY_RUN
            and pyautogui is not None
            and isinstance(erro, pyautogui.FailSafeException)
        ):
            print("Automação interrompida pelo mecanismo de segurança do PyAutoGUI.")
            return

        print(f"Erro inesperado durante a automação: {erro}")
        raise


if __name__ == "__main__":
    main()
