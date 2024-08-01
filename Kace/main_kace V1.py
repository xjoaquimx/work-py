from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time, pyautogui, re, json
from bs4 import BeautifulSoup

driver = webdriver.Chrome()
driver.get("http://kace.br.lactadom.ad/adminui/computer_inventory.php")
time.sleep(2)

while True:
    time.sleep(2)
    try:
        driver.find_element(By.NAME, "LOGIN_NAME").send_keys("042006431")
        driver.find_element(By.NAME, "LOGIN_PASSWORD").send_keys("L@ctali_S2024")
        driver.find_element(By.NAME, "save").click()
        break
    except:
        continue

def ValidarKace():
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, '//*[@id="computer"]/tbody/tr/td/div/span[1]').text
        return False
    except:
        return True

ids = pd.read_excel('Pasta2.xlsx')['nomes'].tolist()
print(ids)

dados_busca = ['name', 'asset_location', 'asset_owner', 'cs_model', 'chassis_type', 'ip', 'mac', 'ram_total',
               'processors', 'os_name', 'user_name', 'last_inventory_formatted', 'created', 'disk_1']
dados_chamados = []
for id in ids:
    dados_id = {}
    driver.get(
        f'http://kace.br.lactadom.ad/adminui/computer_inventory.php?LABEL_ID=&SEARCH_SELECTION_TEXT={id}&SEARCH_SELECTION={id}')
    if ValidarKace():
        driver.find_element(By.XPATH, '//*[@id="computer"]/tbody/tr/td[2]').click()

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        dados_dict = {}
        for busca in dados_busca:
            dados_maquina = soup.findAll('tr', id=re.compile(f'k_section_summary_row_{busca}'))
            dados_dict = {}
            try:
                chave, valor = dados_maquina[0].text.replace('\n', '').split(':', 1)
                dados_id[chave] = valor
            except:
                print(dados_maquina, id)
                break
        try:
            dados_hd = {}
            driver.find_element(By.XPATH, '//*[@id="k_section_customfields_header"]').click()
            time.sleep(1)
            hd_ssd = driver.find_element(By.XPATH, '//*[@id="k_section_customfields"]/tr[2]').text.split('\n')[2:-5]
            for item in hd_ssd:
                chave, valor = item.split(' : ', 1)
                dados_id[chave] = valor
            dados_chamados.append(dados_id)

dados_chamados