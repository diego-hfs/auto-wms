"""Simulação visual das automações WMS dentro de um desktop virtual Docker."""

from pathlib import Path
import os
import time

import pandas as pd
import pyautogui

BASE_DIR = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = BASE_DIR / "dados_exemplo_wms.xlsx"
FLOW = os.getenv("SIMULATION_FLOW", "cadastro").strip().lower()
SIM_DELAY = float(os.getenv("SIM_DELAY", "0.30"))
MAX_ITENS = int(os.getenv("MAX_ITENS", "10"))

pyautogui.FAILSAFE = False  # Simulação isolada dentro do desktop virtual Docker
pyautogui.PAUSE = SIM_DELAY

CADASTRO_POS = {
    "item": (340, 201),
    "unidade_medida": (880, 201),
    "descricao": (610, 291),
    "unidade": (340, 381),
    "lote": (880, 381),
    "validade": (340, 471),
    "unidade_medida_sku": (880, 471),
    "quantidade": (340, 561),
    "salvar": (980, 562),
}

ALTERACAO_POS = {
    "item": (340, 221),
    "pesquisar": (810, 221),
    "unidade_medida": (340, 371),
    "unidade_medida_sku": (880, 371),
    "salvar": (980, 482),
}


def texto(valor: object) -> str:
    if pd.isna(valor):
        return ""
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    return str(valor)


def preencher(posicao: tuple[int, int], valor: object) -> None:
    pyautogui.click(*posicao)
    pyautogui.hotkey("ctrl", "a")
    pyautogui.press("backspace")
    pyautogui.write(texto(valor), interval=0.03)


def simular_cadastro() -> None:
    dados = pd.read_excel(ARQUIVO_ENTRADA, sheet_name="cadastro_itens").head(MAX_ITENS)
    print(f"Simulação visual de cadastro: {len(dados)} registro(s).")

    for numero, (_, linha) in enumerate(dados.iterrows(), start=1):
        print(f"[{numero}/{len(dados)}] Cadastrando {linha['Item']} na tela virtual...")
        preencher(CADASTRO_POS["item"], linha["Item"])
        preencher(CADASTRO_POS["unidade_medida"], linha["Unidade de medida"])
        preencher(CADASTRO_POS["descricao"], linha["Descrição"])
        preencher(CADASTRO_POS["unidade"], linha["Unidade"])
        preencher(CADASTRO_POS["lote"], linha["Lote"])
        preencher(CADASTRO_POS["validade"], linha["Validade"])
        preencher(CADASTRO_POS["unidade_medida_sku"], linha["Unidade de medida1"])
        preencher(CADASTRO_POS["quantidade"], linha["Quantidade de unidades"])
        pyautogui.click(*CADASTRO_POS["salvar"])
        time.sleep(0.6)


def simular_alteracao() -> None:
    dados = pd.read_excel(ARQUIVO_ENTRADA, sheet_name="alteracao_unidade_medida").head(MAX_ITENS)
    print(f"Simulação visual de alteração: {len(dados)} registro(s).")

    for numero, (_, linha) in enumerate(dados.iterrows(), start=1):
        print(f"[{numero}/{len(dados)}] Alterando {linha['Item']} na tela virtual...")
        preencher(ALTERACAO_POS["item"], linha["Item"])
        pyautogui.click(*ALTERACAO_POS["pesquisar"])
        time.sleep(0.4)
        preencher(ALTERACAO_POS["unidade_medida"], linha["Unidade de medida"])
        preencher(ALTERACAO_POS["unidade_medida_sku"], linha["Unidade de medida1"])
        pyautogui.click(*ALTERACAO_POS["salvar"])
        time.sleep(0.6)


def main() -> None:
    if not ARQUIVO_ENTRADA.exists():
        raise FileNotFoundError(f"Planilha não encontrada: {ARQUIVO_ENTRADA}")

    print(f"DISPLAY: {os.getenv('DISPLAY', '(não definido)')}")
    print(f"Fluxo selecionado: {FLOW}")

    if FLOW == "cadastro":
        simular_cadastro()
    elif FLOW == "alteracao":
        simular_alteracao()
    else:
        raise ValueError(f"SIMULATION_FLOW inválido: {FLOW}")

    print("Simulação visual finalizada com sucesso.")


if __name__ == "__main__":
    main()
