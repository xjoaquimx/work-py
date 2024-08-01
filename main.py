from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, pyautogui, re, json
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

email = "joaquim.junior.terceiro@br.lactalis.com"
psw = 'L@ctali_S2024'
def Login(email:str, psw:str):
    driver.get("https://lactalis-smartit.onbmc.com/smartit/app/#/")
    time.sleep(5)
    pyautogui.hotkey("Esc")
    try:
        driver.find_element(By.NAME, "AUTHENTICATION.LOGIN").send_keys(email)
        driver.find_element(By.NAME, "AUTHENTICATION.PASSWORD").send_keys(psw)
        driver.find_element(By.NAME, "validateButton").click()
        return True
    except:
        return False
Login(email, psw)
def ContTicket():
    driver.find_element(By.XPATH, '//*[@id="main"]/div/div[1]/div[3]/div/button').click()
    time.sleep(2)
    total_chamados = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[1]/div[3]/div[4]/h3/span').text
    blocos_total = int(total_chamados) // 75
    return blocos_total

def list_chamados(html):
    soup = BeautifulSoup(html, 'html.parser')
    chamados = soup.findAll('span', class_=re.compile('ng-binding ng-scope'))[7:]
    chamados_geral = []
    for chamado in chamados:
        chamados_geral.append(chamado.getText())
    return chamados_geral

def ResetBlocos(blocos_total):
    for bloco in range(0, blocos_total):
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').click()


chamados_tel = []

blocos_total = ContTicket()

def SaveTicket(blocos_total:int):
    for bloco in range(0, blocos_total + 1):
        if bloco == 0:
            time.sleep(2)
            chamados_tel.append(list_chamados(driver.page_source))
        elif driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').text == 'Próximo Bloco':
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').click()
            chamados_tel.append(list_chamados(driver.page_source))
        elif driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').text != 'Próximo Bloco':
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button[2]').click()
            chamados_tel.append(list_chamados(driver.page_source))


dados_chamados = []
for chamado in chamados_tel[0][7::10]:
    dados_dict = {}
    for item in chamado.split('\n- ')[1:-5]:
        chave, valor = item.split(' : ', 1)
        dados_dict[chave.strip()] = valor.strip()

    # Converter o dicionário para JSON
    dados_json = json.dumps(dados_dict, indent=4, ensure_ascii=False)
    dados_chamados.append(dados_dict)
pd.DataFrame(dados_chamados)
