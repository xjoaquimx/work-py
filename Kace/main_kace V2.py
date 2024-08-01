from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time, re
from bs4 import BeautifulSoup
from winotify import Notification

chrome_options = Options()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)
driver.get("http://kace.br.lactadom.ad/adminui/computer_inventory.php")

def Verifica(tipo, valor:str):
    return WebDriverWait(driver, 10).until(EC.visibility_of_element_located((tipo, valor)))

Verifica(By.NAME, "LOGIN_NAME").send_keys("042006431")
Verifica(By.NAME, "LOGIN_PASSWORD").send_keys("L@ctali_S2024")
Verifica(By.NAME, "save").click()

def ValidarKace():
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, '//*[@id="computer"]/tbody/tr/td/div/span[1]').text
        return False
    except:
        return True

ids = pd.read_excel('Kace.xlsx')['Hostname'].tolist()

dados_busca = ['name', 'asset_location', 'asset_owner', 'cs_model', 'chassis_type', 'ip', 'mac', 'ram_total',
               'processors', 'os_name', 'user_name', 'last_inventory_formatted', 'created', 'disk_1']
dados_chamados = []
for id in ids:
    dados_id = {}
    driver.get(
        f'http://kace.br.lactadom.ad/adminui/computer_inventory.php?LABEL_ID=&SEARCH_SELECTION_TEXT={id}&SEARCH_SELECTION={id}')
    if ValidarKace():
        Verifica(By.XPATH, '//*[@id="computer"]/tbody/tr/td[2]').click()

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
            Verifica(By.XPATH, '//*[@id="k_section_customfields_header"]').click()
            time.sleep(1)
            hd_ssd = Verifica(By.XPATH, '//*[@id="k_section_customfields"]/tr[2]').text.split('\n')[2:-5]
            for item in hd_ssd:
                chave, valor = item.split(' : ', 1)
                dados_id[chave] = valor
            dados_chamados.append(dados_id)
        except:
            continue

driver.quit()
data_list = []
device = {}

for item in dados_chamados:
    key = list(item.keys())[0]
    value = list(item.values())[0]
    #if key == 'Nome do sistema' and device:  # novo dispositivo
    #data_list.append(device)
    device[key] = value

data_list.append(device)  # adicionar o último dispositivo

# Criar o DataFrame
df_pronto = pd.DataFrame(dados_chamados)

df = pd.read_excel('Kace.xlsx')['Hostname']

df_finalizado = pd.concat([df, df_pronto], axis=1)

notificacao = Notification(app_id="Kace", title="Notificação",
                    msg="script kace finalizado com sucesso",
                    duration="long")

notificacao.add_actions(label="Abrir", launch=r"C:\Users\042006431\PycharmProjects\pythonProject1\Kace\Dados_nomes.xlsx")

df_finalizado.to_excel('Dados_nomes.xlsx', index=False)
notificacao.show()