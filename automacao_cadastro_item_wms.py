"""Automação para cadastro de produtos em um WMS usando dados de Excel.

A automação lê a aba ``cadastro_itens`` do arquivo ``dados_exemplo_wms.xlsx``.

Modos de execução:
- DRY_RUN=true: lê e valida o Excel e simula as ações no terminal, sem clicar.
- DRY_RUN=false: executa as ações reais com PyAutoGUI no computador local.
"""

from pathlib import Path
import os
import time

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = BASE_DIR / "dados_exemplo_wms.xlsx"
ABA_ENTRADA = "cadastro_itens"

DRY_RUN = os.getenv("DRY_RUN", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "sim",
    "on",
}

COLUNAS_OBRIGATORIAS = {
    "Item",
    "Unidade de medida",
    "Descrição",
    "Unidade",
    "Lote",
    "Validade",
    "Unidade de medida1",
    "Quantidade de unidades",
}

POS = {
    "novo_produto": (168, 400),
    "opcao_unidade": (114, 665),
    "opcao_lote": (535, 661),
    "campo_validade": (882, 568),
    "opcao_validade": (534, 619),
    "adicionar_sku": (124, 704),
    "salvar": (1308, 217),
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


def pressionar(tecla: str, presses: int = 1, interval: float = 0.0) -> None:
    """Pressiona uma tecla ou registra a ação no modo de teste."""
    if DRY_RUN:
        detalhe = f" x{presses}" if presses > 1 else ""
        print(f"  [DRY-RUN] pressionar '{tecla}'{detalhe}")
        return

    pyautogui.press(tecla, presses=presses, interval=interval)


def atalho(*teclas: str) -> None:
    """Executa um atalho de teclado ou registra a ação no modo de teste."""
    if DRY_RUN:
        print(f"  [DRY-RUN] atalho {' + '.join(teclas)}")
        return

    pyautogui.hotkey(*teclas)


def rolar(valor: int) -> None:
    """Executa o scroll ou registra a ação no modo de teste."""
    if DRY_RUN:
        print(f"  [DRY-RUN] scroll {valor}")
        return

    pyautogui.scroll(valor)


def preencher_texto(valor: object) -> None:
    """Digita um valor no campo ativo ou o exibe no modo de teste."""
    texto = str(valor)

    if DRY_RUN:
        print(f"  [DRY-RUN] digitar: {texto}")
        return

    pyautogui.write(texto)


def preencher_dados_principais(linha: pd.Series) -> None:
    """Preenche item, unidade de medida e descrições do produto."""
    preencher_texto(linha["Item"])
    pressionar("tab", presses=2)
    esperar(0.5)

    preencher_texto(linha["Unidade de medida"])
    pressionar("tab")
    esperar(0.5)

    preencher_texto(linha["Descrição"])
    pressionar("tab")
    esperar(0.5)

    # O fluxo original preenche a mesma descrição em dois campos consecutivos.
    preencher_texto(linha["Descrição"])
    pressionar("tab", presses=2)
    esperar(0.5)


def preencher_unidade(linha: pd.Series) -> None:
    """Seleciona a unidade operacional do produto."""
    rolar(-1000)
    esperar(1)
    pressionar("enter")
    preencher_texto(linha["Unidade"])
    esperar(1.5)
    clicar("opcao_unidade")
    pressionar("tab")
    esperar(1)


def preencher_lote_validade(linha: pd.Series) -> None:
    """Preenche as características de lote e validade."""
    pressionar("enter")
    preencher_texto(linha["Lote"])
    esperar(1.5)
    clicar("opcao_lote")
    esperar(1)

    clicar("campo_validade")
    atalho("ctrl", "a")
    pressionar("delete")
    preencher_texto(linha["Validade"])
    esperar(1.5)
    clicar("opcao_validade")
    pressionar("tab")
    esperar(1)


def adicionar_sku(linha: pd.Series) -> None:
    """Adiciona a unidade de medida e a quantidade de unidades do SKU."""
    pressionar("enter")
    pressionar("tab", presses=2)
    esperar(0.5)

    preencher_texto(linha["Unidade de medida1"])
    pressionar("tab")
    preencher_texto(linha["Quantidade de unidades"])
    clicar("adicionar_sku")


def cadastrar_item(linha: pd.Series) -> None:
    """Executa o fluxo completo de cadastro de um item."""
    preencher_dados_principais(linha)
    preencher_unidade(linha)
    preencher_lote_validade(linha)
    adicionar_sku(linha)

    esperar(1)
    clicar("salvar")
    esperar(3)


def linha_valida(linha: pd.Series) -> bool:
    """Retorna True quando todos os campos obrigatórios possuem valor."""
    return not linha[list(COLUNAS_OBRIGATORIAS)].isna().any()


def processar_itens(dados: pd.DataFrame) -> None:
    """Cadastra ou simula o cadastro de todos os registros válidos."""
    total = len(dados)
    clicar("novo_produto")
    esperar(1)

    for numero, (_, linha) in enumerate(dados.iterrows(), start=1):
        item = linha["Item"]

        if not linha_valida(linha):
            print(f"[{numero}/{total}] Item {item}: linha ignorada por campo obrigatório vazio.")
            continue

        print(f"[{numero}/{total}] Processando cadastro do item {item}...")
        cadastrar_item(linha)
        print(f"[{numero}/{total}] Item {item}: fluxo concluído.")

        if numero < total:
            clicar("novo_produto")
            esperar(1)


def main() -> None:
    """Ponto de entrada da automação."""
    try:
        configurar_interface()
        dados = carregar_dados(ARQUIVO_ENTRADA, ABA_ENTRADA)
        print(f"{len(dados)} registro(s) carregado(s) da aba '{ABA_ENTRADA}'.")
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
