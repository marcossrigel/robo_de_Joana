import subprocess
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import SessionNotCreatedException

class RoboNUPCO:

    def __init__(self):
        self.driver = None

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
    
    def ir_para_aba_efisco(self):

        for aba in self.driver.window_handles:

            self.driver.switch_to.window(aba)

            if "efisco" in self.driver.current_url.lower():

                return

    def conectar(self):

        options = Options()
        options.debugger_address = "127.0.0.1:9222"

        self.driver = webdriver.Chrome(options=options)

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

        self.conectar()
        self.abrir_aba_efisco()
        status = self.aguardar_login_efisco()
        print(status)


if __name__ == "__main__":

    robo = RoboNUPCO()
    robo.iniciar()
