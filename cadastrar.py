import subprocess
import time
import gspread
import pandas as pd

from selenium.common.exceptions import (StaleElementReferenceException,TimeoutException)
from selenium import webdriver
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.support.ui import Select

class RoboNUPCO:

    def __init__(self):
        self.driver = None

    def ler_base_de_dados(self):

        gc = gspread.service_account(filename="credenciais.json")

        planilha = gc.open("NUPCO - base de dados")

        self.aba = planilha.sheet1

        dados = self.aba.get_all_records()

        return dados

    def marcar_como_cadastrado(self, numero_ob):

        celula = self.aba.find(str(numero_ob))

        self.aba.update_cell(
            celula.row,
            5,          # coluna E = Status
            "Já Cadastrado"
        )

        print(f"OB {numero_ob} marcada como Já Cadastrado.")
        
    def abrir_aba_efisco(self):

        self.driver.switch_to.new_window("tab")
        self.driver.get("https://efisco.sefaz.pe.gov.br/")

    def aguardar_login_efisco(self):

        while True:

            try:

                self.driver.find_element(
                    By.XPATH,
                    '//*[@id="a_usuario"]'
                )

                return "✅ Usuario Logado no eFisco"

            except NoSuchElementException:
                pass

            try:

                botao = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="btt_gov"]'
                )
                botao.click()
                time.sleep(2)
                continue

            except NoSuchElementException:
                pass

            try:

                WebDriverWait(self.driver, 300).until(
                    EC.presence_of_element_located(
                        (By.ID, "a_usuario")
                    )
                )

                print("✅ Usuário Logado no eFisco")
                return "Usuario Logado no eFisco"

            except:

                return None

    def esperar_elemento(self, by, valor, timeout=60):

        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(by, valor)) > 0
        )

        return self.driver.find_element(by, valor)

    def ir_para_aba_efisco(self):

        for aba in self.driver.window_handles:

            self.driver.switch_to.window(aba)

            if "efisco" in self.driver.current_url.lower():

                return
    
    def clicar(self, by, valor):

        while True:
            try:
                elemento = self.driver.find_element(by, valor)
                elemento.click()
                return

            except StaleElementReferenceException:
                print(f"{valor} ficou stale. Tentando novamente...")
                time.sleep(1)

    def etapa_01_cadastramento(self, linha):
        
        print(f"Iniciando cadastro da OB {linha['Número da OB']}")

        #
        # Já estamos na tela de Cadastro?
        #
        try:

            self.driver.find_element(By.ID, "btt_incluir")

        except NoSuchElementException:

            WebDriverWait(self.driver, 60).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        '//*[@id="favoritos_carrossel_itens"]/div/ul/li[1]/a'
                    )
                )
            ).click()

            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located(
                    (By.ID, "btt_incluir")
                )
            )

        #
        # Novo cadastro
        #
        self.driver.find_element(
            By.ID,
            "btt_incluir"
        ).click()

        #
        # Aguarda primeira tela
        #
        #WebDriverWait(self.driver, 60).until(
        #    EC.element_to_be_clickable(
        #        (By.ID, "cdGestao")
        #    )
        #)

        #
        # Aguarda a primeira tela terminar de carregar
        #
        self.esperar_elemento(By.ID, "sqOrdemBancaria")

        #
        # Unidade de Gestão
        #
        gestao = self.esperar_elemento(By.ID, "cdGestao")

        Select(gestao).select_by_index(1)

        #
        # Ano OB
        #
        Select(
            self.driver.find_element(
                By.ID,
                "dtAnoExercicioOB"
            )
        ).select_by_visible_text("2025")

        #
        # Processo SEI
        #
        self.driver.find_element(
            By.ID,
            "nuSei"
        ).send_keys("0060900077.000814/2025-96")

        #
        # Observação
        #
        self.driver.find_element(
            By.ID,
            "txObservacao"
        ).send_keys("AUXILIO MORADIA COMPETENCIA AGOSTO/2025")

        #
        # Número da OB
        #
        self.driver.find_element(
            By.ID,
            "sqOrdemBancaria"
        ).send_keys(
            linha["Número da OB"]
        )

        #
        # Ano NE
        #
        Select(
            self.driver.find_element(
                By.ID,
                "dtAnoExercicioEmpenho"
            )
        ).select_by_visible_text("2025")

        #
        # Número NE
        #
        self.driver.find_element(
            By.ID,
            "sqEmpenho"
        ).send_keys(
            linha["Nota Empenho"]
        )

        #
        # Atualiza tela
        #
        self.driver.find_element(
            By.ID,
            "txObservacao"
        ).click()

        #
        # Verifica se já existe
        #
        try:

            WebDriverWait(
                self.driver,
                1
            ).until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "btt_prosseguir"
                    )
                )
            )

            self.driver.find_element(
                By.ID,
                "btt_prosseguir"
            ).click()
            
            print(
                f"OB {linha['Número da OB']} já cadastrada."
            )

            WebDriverWait(
                self.driver,
                60
            ).until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "btt_desistir"
                    )
                )
            )

            self.driver.find_element(
                By.ID,
                "btt_desistir"
            ).click()

            WebDriverWait(
                self.driver,
                60
            ).until(
                EC.presence_of_element_located(
                    (By.ID, "btt_alterar")
                )
            )

            self.marcar_como_cadastrado(
                linha["Número da OB"]
            )

            return False

        except:

            print("Página 1 preenchida.")
            time.sleep(2)
            return True

    def conectar(self):
        options = Options()
        options.debugger_address = "127.0.0.1:9222"
        self.driver = webdriver.Chrome(options=options)
        
    def etapa_02_continua_cadastro(self, linha):

        print(f"Continuando cadastro da OB {linha['Número da OB']}")

        #
        # Marca Consulta
        #
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable(
                (By.ID, "rdb_consulta")
            )
        ).click()

        print("Consulta selecionada.")

        #
        # Clica em Incluir
        #
        WebDriverWait(self.driver, 60).until(
            EC.element_to_be_clickable(
                (By.ID, "btt_incluir")
            )
        ).click()

        #
        # Aguarda a segunda tela
        #
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located(
                (By.ID, "CdTpDocumentoPrestacaoConta")
            )
        )

        print("Segunda tela carregada.")

        # ==================================================
        # SEGUNDA TELA
        # ==================================================

        #
        # Tipo do Documento
        #
        Select(
            self.driver.find_element(
                By.ID,
                "CdTpDocumentoPrestacaoConta"
            )
        ).select_by_visible_text(
            "78 - D - RELAÇÃO EXTERNA CARIMBADA P/ BANCO"
        )

        #
        # Data
        #
        self.driver.find_element(
            By.ID,
            "dtDocPc"
        ).send_keys(
            str(linha["Data da OB"]).zfill(8)
        )

        #
        # Número da Remessa
        #
        self.driver.find_element(
            By.ID,
            "nuIdentificacao"
        ).send_keys(
            linha["Número da Remessa"]
        )

        #
        # Descrição
        #
        self.driver.find_element(
            By.ID,
            "txDescricao"
        ).send_keys(
            "AUXILIO MORADIA COMPETENCIA AGOSTO/2025"
        )

        #
        # Referência SEI
        #
        self.driver.find_element(
            By.ID,
            "txReferenciaPagina"
        ).send_keys(
            "0060900077.000814/2025-96"
        )

        #
        # Item do Empenho
        #
        self.driver.find_element(
            By.ID,
            "rdb_itemEmpenho[[*]]0"
        ).click()

        print("Página 2 preenchida.")

        # ==================================================
        # 11) CONFIRMA
        # ==================================================

        WebDriverWait(
            self.driver,
            60
        ).until(
            EC.element_to_be_clickable(
                (By.ID, "btt_confirmar")
            )
        ).click()

        print("Primeira confirmação realizada.")

        # ==================================================
        # 12) TERCEIRA TELA
        # ==================================================

        WebDriverWait(
            self.driver,
            60
        ).until(
            EC.presence_of_element_located(
                (By.ID, "btt_incluir")
            )
        )

        WebDriverWait(
            self.driver,
            60
        ).until(
            EC.element_to_be_clickable(
                (By.ID, "btt_confirmar")
            )
        ).click()

        print("Segunda confirmação realizada.")
        time.sleep(2)
        return True

    def etapa_03_finalizar_cadastro(self, linha):

        print("Finalizando cadastro...")

        #
        # Aguarda a quarta tela
        #
        WebDriverWait(
            self.driver,
            60
        ).until(
            EC.element_to_be_clickable(
                (
                    By.ID,
                    "btt_prosseguir"
                )
            )
        )

        #
        # Captura e salva a Prestação de Contas
        #
        self.salvar_prestacao(linha)

        #
        # Prosseguir
        #
        self.driver.find_element(
            By.ID,
            "btt_prosseguir"
        ).click()

        self.marcar_como_cadastrado(
            linha["Número da OB"]
        )

        print(f"✅ Cadastro da OB {linha['Número da OB']} concluído.")
        print("Aguardando próximo registro da planilha...")

        return True

    def salvar_prestacao(self, linha):

        #
        # Captura o número da Prestação de Contas (PC)
        #
        elemento = WebDriverWait(
            self.driver,
            30
        ).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//td[@class='campoformulario']/b/font"
                )
            )
        )

        numero_pc = elemento.text.strip()

        #
        # Salva no arquivo
        #
        with open(
            "numero_das_pcs.txt",
            "a",
            encoding="utf-8"
        ) as arquivo:

            arquivo.write(
                "=" * 60 + "\n"
            )

            arquivo.write(
                f"Data/Hora: {datetime.now():%d/%m/%Y %H:%M:%S}\n"
            )

            arquivo.write(
                f"Número da OB: {linha['Número da OB']}\n"
            )

            arquivo.write(
                f"Prestação Gerada (PC): {numero_pc}\n"
            )

            arquivo.write(
                "Status: PENDENTE\n"
            )

            arquivo.write(
                "=" * 60 + "\n\n"
            )

        print(
            f"PC Gerada: {numero_pc}"
        )

    def tratar_tela_ja_logado(self):

            try:
                self.driver.find_element(
                    By.XPATH,
                    '//*[@id="kc-info-message"]/p[1]'
                )

                self.driver.find_element(
                    By.XPATH,
                    '//*[@id="kc-info-message"]/p[2]/a'
                ).click()

                return True

            except NoSuchElementException:
                return False

    def iniciar(self):

        print("Conectando ao Chrome...")
        self.conectar()

        print("Abrindo eFisco...")
        self.abrir_aba_efisco()

        print("Verificando login...")
        self.aguardar_login_efisco()

        print("Lendo Google Sheets...")
        dados = self.ler_base_de_dados()

        print(f"{len(dados)} registros encontrados.")
        
        for linha in dados:

            status = str(linha.get("Status", "")).strip().lower()

            if status == "já cadastrado":
                continue

            print()
            print("=" * 60)
            print(f"OB {linha['Número da OB']}")
            print("=" * 60)

            #
            # Etapa 01
            #
            if not self.etapa_01_cadastramento(linha):
                continue

            time.sleep(2)

            #
            # Etapa 02
            #
            if not self.etapa_02_continua_cadastro(linha):
                continue

            time.sleep(2)

            #
            # Etapa 03
            #
            self.etapa_03_finalizar_cadastro(linha)

if __name__ == "__main__":

    robo = RoboNUPCO()
    robo.iniciar()
