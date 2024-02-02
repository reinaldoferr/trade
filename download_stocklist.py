
# Sale de https://aronhack.com/download-stock-historical-data-with-python-and-yahoo-finance-api/
# pero no funcionó, sin embargo sirve me parece el ejemplo de como bajar una json a dataframe

import os
import requests
import numpy as np
import pandas as pd
link = 'https://quality.data.gov.tw/dq_download_json.php?nid=11549&md5_url=bb878d47ffbe7b83bfc1b41d0b24946e'
r = requests.get(link)
data = pd.DataFrame(r.json())


# Verificar si existe la carpeta en el disco donde se guardarán los archivos, sino la crea.
if not (os.path.exists('raw_data')):
    print ('Creado carpeta raw_data')
    os.mkdir('raw_data')
print(data.tail(5))
data.to_csv(f'raw_data/ticker_list.csv', index=False, encoding='utf-8-sig')
