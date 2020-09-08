import requests
import json
import pandas
from datetime import datetime
import PySimpleGUI as sg

layout = [  
    [sg.Text('Selecione o arquivo (.xlsx)', font='Roboto 10')],
    [sg.In() ,sg.FileBrowse(file_types=(("Excel Files", "*.xlsx"),),key='file')],
    [sg.ProgressBar(100, orientation='h', size=(40, 5), key='progressbar')],
    [sg.Button('Buscar dados', key='enviar', font='Roboto 10')]
]

window = sg.Window('gamalu-crawler', layout, margins=(15, 15)).Finalize()

while True:

    event, values = window.read()
    progressBar = window['progressbar']

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    data = pandas.read_excel(r''+values['file'])
    dataFrame = pandas.DataFrame(data, columns=['CEP', 'Produto'])

    pbCurrent = 0
    pbUpdate = 100 / len(dataFrame.values)

    tempData = {
        'reference_row': [], 
        'zip_code': [], 
        'product': [], 
        'description': [], 
        'distribution_center': [],
        'name': [],
        'city': [],
        'sellers': [],
        'is_deadline': [],
        'price': [],
        'time': [],
        'zip_code_restriction': []
    }

    for index, row in enumerate(dataFrame.values):

        cep = str(row[0])
        product = str(row[1])

        productURL = 'https://www.magazineluiza.com.br/produto/calculo-frete/'+ cep +'/'+ product +'/magazineluiza.json'
        productHeaders = {
            'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            'referer': 'https://www.magazineluiza.com.br',
        }

        productRequest = requests.get(productURL, headers=productHeaders, verify='certificate.pem')
        productData = json.loads(productRequest.text)

        for deliveryOption in productData['delivery']:

            name = ""
            city = ""
            sellers = ""

            if deliveryOption['distribution_center'] > 0:

                distributionCenterURL = 'https://lojas.magazineluiza.com.br/filiais/' + str(deliveryOption['distribution_center'])
                distributionCenterRequest = requests.get(distributionCenterURL, verify='certificate.pem')
                distributionCenterHTML = distributionCenterRequest.text

                distributionCenterHTML.find("col-7 col-md-8 m-auto")

                firstCut = distributionCenterHTML[(103+distributionCenterHTML.find("col-7 col-md-8 m-auto")):]
                secondCut = firstCut[firstCut.find("data-v-12a79897")+16:]
                thirdCut = secondCut[secondCut.find("data-v-12a79897")+67:]

                name = firstCut.split("<")[0].strip()
                city = secondCut.split("<")[0]
                sellers = thirdCut.split("<")[0]

            deliveryOption['name'] = name
            deliveryOption['city'] = city
            deliveryOption['sellers'] = sellers

        for deliveryOption in productData['delivery']:
            tempData['reference_row'].append(index)
            tempData['zip_code'].append(cep)
            tempData['product'].append(product)

            for attribute in deliveryOption:
                tempData[str(attribute)].append(str(deliveryOption[attribute]))

        pbCurrent += pbUpdate
        progressBar.UpdateBar(pbCurrent)

    tempDataFrame = pandas.DataFrame(data=tempData)
    tempDataFrame.to_excel(r'Saida (gamalu-crawler).xlsx', index=False)

    sg.popup('Arquivo de saida criado: Saida (gamalu-crawler).xlsx')