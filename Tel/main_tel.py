from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, pyautogui, re, json
from bs4 import BeautifulSoup
from datetime import datetime

driver = webdriver.Chrome()
driver.get("https://lactalis-smartit.onbmc.com/smartit/app/#/")
time.sleep(5)
pyautogui.hotkey("Esc")

def logon():
    time.sleep(3)
    try:
        driver.find_element(By.NAME, "AUTHENTICATION.LOGIN").send_keys("joaquim.junior.terceiro@br.lactalis.com")
        driver.find_element(By.NAME, "AUTHENTICATION.PASSWORD").send_keys("L@ctali_S2024")
        driver.find_element(By.NAME, "validateButton").click()
        return True
    except:
        return False
logon()

driver.find_element(By.XPATH, '//*[@id="main"]/div/div[1]/div[3]/div/button').click()
time.sleep(2)
total_chamados = driver.find_element(By.XPATH, '//*[@id="main"]/div/div[1]/div[3]/div[4]/h3/span').text
blocos_total = int(total_chamados)//75

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


def GerarDadosGeral():
    dados_chamados_geral = []

    for n in range(0, len(chamados_tel)):
        for chamado in chamados_tel[n][7::10]:
            dados_dict = {}
            for item in chamado.split('\n- ')[1:-5]:
                try:
                    chave, valor = item.split(':', 1)
                    dados_dict[chave.strip()] = valor.strip()
                except:
                    chave, valor = item.split('  ', 1)
                    dados_dict[chave.strip()] = valor.strip()
            dados_chamados_geral.append(dados_dict)
    return dados_chamados_geral

def dados_chamados(id:int):
    dados_chamado = []
    for tel in chamados_tel:
        dados_chamado.extend(tel[id::10])
    return dados_chamado

chamados_tel = []
for bloco in range(0, blocos_total+1):
    if bloco == 0:
        chamados_tel.append(list_chamados(driver.page_source))
    elif driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').text == 'Próximo Bloco':
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').click()
        chamados_tel.append(list_chamados(driver.page_source))
    elif driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button').text != 'Próximo Bloco':
        driver.find_element(By.XPATH, '//*[@id="main"]/div/div[2]/div[2]/div[2]/button[2]').click()
        chamados_tel.append(list_chamados(driver.page_source))
ResetBlocos(blocos_total)

def ExportDF(nome:str):
    try:
        df_dados_chamados = pd.DataFrame({
            'Número do Chamado': dados_chamados(0),
            'Cliente': dados_chamados(2),
            'Filial': dados_chamados(3),
            'Grupo designado': dados_chamados(8),
            'Tipo': dados_chamados(5),
            'Status': dados_chamados(6),
            'Data de criação': dados_chamados(1),
        })

        df_dados_chamados_geral = pd.DataFrame(GerarDadosGeral())
        df_full = pd.concat([df_dados_chamados, df_dados_chamados_geral], axis=1)

        dia = datetime.today().strftime('%d%m')
        df_full.to_excel(f'{nome}_{dia}.xlsx', index=False)
        return True
    except:
        return False