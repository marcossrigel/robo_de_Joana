import pyautogui # Para automatizar o controle do mouse e teclado, útil quando o Selenium não consegue interagir com algum elemento na tela
import os # Usada para lidar com arquivos e diretórios no sistema operacional (Biblioteca da própria linguagem Python)
import time
import gspread

# ===== IMPORTANDO BIBLIOTECAS =======
from selenium import webdriver # Usada para controlar o navegador (abrir páginas, clicar, preencher formulários etc.)
from selenium.webdriver.common.by import By # Permite localizar elementos na página usando diferentes critérios (ID, classe, XPath, nome etc.)
from selenium.webdriver.chrome.options import Options # Permite configurar opções do navegador (como abrir em modo invisível, definir pasta de download, etc.)
from selenium.webdriver.support.ui import WebDriverWait, Select # WebDriverWait permite esperar até que um elemento esteja visível ou clicável; 
# Select é usada para lidar com menus suspensos (<select>)
from selenium.webdriver.support import expected_conditions as EC # Define condições para esperar um elemento (por exemplo: até ficar visível, clicável, etc.)
# as EC = apelido para escrever menos e deixar o código mais limpo.
from selenium.webdriver.common.action_chains import ActionChains # Permite realizar ações avançadas como mover o mouse, arrastar e soltar, passar o mouse por cima etc.
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException # Permite lidar com alertas (janelinhas de confirmação ou aviso que aparecem no navegador)

def aguardar_login():
    while True:

        try:
            driver.find_element(By.ID, "a_usuario")
            break

        except NoSuchElementException:
            pass

        try:
            driver.find_element(By.ID, "btt_gov").click()
            time.sleep(2)

        except NoSuchElementException:
            pass

def ler_pcs_pendentes():

    dados = aba_pcs.get_all_records()

    pcs = []

    for indice, linha in enumerate(dados, start=2):

        if str(linha["Status"]).strip().upper() != "PENDENTE":
            continue

        pc_completa = str(linha["Prestação Gerada (PC)"]).strip()

        if not pc_completa.startswith("2026PC"):
            print(f"⚠️ PC inválida ignorada: {pc_completa}")
            continue

        numero = pc_completa.replace("2026PC", "")

        pcs.append({

            "linha": indice,
            "ob": linha["Número da OB"],
            "pc_completa": pc_completa,
            "numero": numero

        })

    return pcs

def marcar_pc_como_ok(linha):

    aba_pcs.update_cell(
        linha,
        4,
        "OK"
    )

#pasta_download = r"C:\Users\marcos.rigel\Desktop\tramitados" # Caminho para pasta onde os PDFs serão salvos

#os.makedirs(
#    pasta_download,
#    exist_ok=True
#)

# ===== CONFIGURAÇÃO DO NAVEGADOR =====
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(300)

gc = gspread.service_account(filename="credenciais.json")

planilha = gc.open("NUPCO - base de dados")

aba_pcs = planilha.worksheet("numero_das_pcs")

print("Abrindo eFisco...")

driver.switch_to.new_window("tab")
driver.get("https://efisco.sefaz.pe.gov.br/")

print("Aguardando login...")
aguardar_login()

print("Abrindo Cadastro Individual...")

WebDriverWait(driver, 60).until(
    EC.element_to_be_clickable(
        (
            By.XPATH,
            '//*[@id="favoritos_carrossel_itens"]/div/ul/li[1]/a'
        )
    )
).click()

for pc in ler_pcs_pendentes():

    numero_pc = pc["numero"]

    print("=" * 60)
    print(f"Processando {pc['pc_completa']}")
    print("=" * 60)

    campo = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "sqPrestCta"))
    )

    campo.clear()
    campo.send_keys(numero_pc)

    print("✅ Número da PC informado.")

    WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "btt_localizar"))
    ).click()

    print("✅ Consulta realizada.")

    time.sleep(2)

    WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "chkSelecionarTodas"))
    ).click()

    print("✅ PC selecionada.")

    botao_tramitar = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.ID, "btt_tramite_coletivo_prestacao_conta")
        )
    )

    ActionChains(driver).move_to_element(botao_tramitar).perform()
    botao_tramitar.click()

    print("✅ Tramitar Coletivo.")

    botao_liberar = WebDriverWait(driver, 600).until(
        EC.element_to_be_clickable(
            (By.ID, "btt_liberar_tramite_prestacao_conta")
        )
    )

    ActionChains(driver).move_to_element(botao_liberar).perform()
    botao_liberar.click()

    WebDriverWait(driver, 10).until(
        EC.alert_is_present()
    ).accept()

    WebDriverWait(driver, 600).until(
        EC.element_to_be_clickable((By.NAME, "btt_pmu_acao_4"))
    ).click()

    WebDriverWait(driver, 600).until(
        EC.element_to_be_clickable((By.ID, "btt_prosseguir"))
    ).click()

    try:
        WebDriverWait(driver, 2).until(
            EC.alert_is_present()
        )
        driver.switch_to.alert.accept()
    except:
        pass

    marcar_pc_como_ok(
        pc["linha"]
    )

    print(f"✅ {pc['pc_completa']} concluída.")

try:
    WebDriverWait(driver, 2).until(EC.alert_is_present())
    driver.switch_to.alert.accept()
except:
    pass
