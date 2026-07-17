import subprocess
import time
import webbrowser

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException

class RoboNUPCO:

    def __init__(self):
        self.driver = None

    def abrir_chrome(self):

        url = "https://efisco.sefaz.pe.gov.br/"

        webbrowser.open_new_tab(url)

        print("Chrome iniciado.")
        time.sleep(5)

    def aguardar_login_efisco(self):

        while True:

            # -----------------------------------
            # Usuário já está logado?
            # -----------------------------------
            try:

                self.driver.find_element(
                    By.XPATH,
                    '//*[@id="a_encerrar_sessao"]'
                )

                print("✅ Usuario Logado no eFisco")
                return "Usuario Logado no eFisco"

            except NoSuchElementException:
                pass

            # -----------------------------------
            # Usuário ainda não está logado
            # -----------------------------------
            try:

                botao_gov = self.driver.find_element(
                    By.XPATH,
                    '//*[@id="btt_gov"]'
                )

                print("🔐 Usuário não está logado.")
                print("Abrindo tela do Gov.br...")

                botao_gov.click()

                print("Aguardando usuário realizar o login...")

                while True:

                    try:

                        self.driver.find_element(
                            By.XPATH,
                            '//*[@id="a_encerrar_sessao"]'
                        )

                        print("✅ Usuario Logado no eFisco")
                        return "Usuario Logado no eFisco"

                    except NoSuchElementException:
                        time.sleep(1)

            except NoSuchElementException:
                pass

            time.sleep(1)

    def conectar(self):

        options = Options()
        options.debugger_address = "127.0.0.1:9222"

        self.driver = webdriver.Chrome(options=options)

        print("Selenium conectado ao Chrome.")

    def iniciar(self):

        self.abrir_chrome()
        self.conectar()

        status = self.aguardar_login_efisco()

        print(status)


if __name__ == "__main__":

    robo = RoboNUPCO()
    robo.iniciar()
