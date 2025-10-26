import datetime
import requests
import pyexcel as pe


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
        print(*lst2, sep='\n')

        del lst, sheets

    except Exception as e:
        print(f"Ошибка: {e}")
        return []
    return lst2


def clinical_recommendations(data: list):
    print('start')
    count = 0
    for line in data:
        doc_id = line[0]
        try:
            url = f"https://apicr.minzdrav.gov.ru/api.ashx?op=GetClinrecPdf&id={doc_id}"
            response = requests.get(url)
            count += 1
            print(response)
        except Exception as e:
            print(e)

    print(count)


e = minzdrav_excel()
# clinical_recommendations(e)

