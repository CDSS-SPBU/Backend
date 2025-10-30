import datetime
import time

import requests
import threading
import pyexcel as pe
from concurrent.futures import ThreadPoolExecutor
from db.postgres import DataManager

db_lock = threading.Lock()


def minzdrav_excel():
    '''с сайта скачивается документ, который имеет названия, которые не используются,
    поэтому подчищаем так чтобы было как можно меньше документов на выброс'''

    url = "https://apicr.minzdrav.gov.ru/api.ashx"
    params = {'op': 'GetJsonClinrecsFilterV2Excel'}
    data = {'filter': {"status": [1], "search": "",    "year": "",    "specialties": []}}

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'https://apicr.minzdrav.gov.ru',
        'Referer': 'https://apicr.minzdrav.gov.ru/',
    }
    try:
        response = requests.post(url, params=params, json=data, headers=headers)
        response.raise_for_status()

        sheets = pe.get_array(file_content=response.content, file_type='xlsx')
        lst = []
        for i in range(len(sheets)):
            if (type(sheets[i][6]) != datetime.datetime) or (sheets[i][5] == 'Нет'): continue

            lst.append(sheets[i])
        print(len(lst))

        lst.sort(key=lambda x: x[0])

        lst2 = [lst[-1]]
        for i in range(len(lst) - 1, 0, -1):
            if lst[i - 1][0][:-1] == lst[i][0][:-1]:
                continue
            lst2.append(lst[i - 1])
        print(len(lst2))
        # print(*lst2, sep='\n')

        del lst, sheets

    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    clinical_recommendations(lst2)


def clinical_recommendations(data: list):
    data_base = DataManager()
    if not data_base.creation_db():
        data_base.create_table()

        with ThreadPoolExecutor(max_workers=15) as pool:
            futures = [pool.submit(download, line, data_base) for line in data]

            completed = 0
            for future in futures:
                try:
                    future.result()
                    completed += 1
                except Exception as e:
                    print(f"Ошибка в потоке: {e}")
        print(f"Загрузка данных в БД ({len(data_base.upload_list)} записей)")
        data_base.upload_data()
    # check_relevance()


def download(line: list, data_base: DataManager):
    doc_id, title, MCB, age_category, developer, _, placement_data, _ = line
    try:
        url = f"https://apicr.minzdrav.gov.ru/api.ashx?op=GetClinrecPdf&id={doc_id[:-2]}"
        response = requests.get(url)

        if response.status_code == 200:
            file_content = response.content
            with db_lock:
                data_base.add_to_upload_list(doc_id, title, MCB, age_category, developer, placement_data, file_content)
        else:
            print(doc_id)

    except Exception as e:
        print(e)


# def check_relevance():
#     # не найдено по каким параметрам именно эти файлы отсутствуют в актуальных данных на момент 28.10.25
#     to_delete = ('1101212_1', '140_1', '142_1', '163_2', '171_2', '190_2', '258_2', '324_2', '326_4', '328_2', '45_1',
#                  '504_2', '546_3', '578_1', '589_2', '591_1', '634_1', '646_1', '649_1', '658_1', '659_1', '666_1',
#                  '667_1', '689_1', '690_2', '692_1', '693_1', '701_1', '705_1', '706_1', '707_1', '717_2', '727_1',
#                  '73_9')
#     data_base = DataManager()
#     data_base.delete_data(to_delete)
