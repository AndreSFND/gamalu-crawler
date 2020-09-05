import requests
import json
import pprint
import PySimpleGUI as sg

layout = [  
    [sg.Text('Insira o CEP (somente numeros)', font='Roboto 10')],
    [sg.InputText(key='cep', do_not_clear=True, font='Roboto 10')],
    [sg.Text('Insira o codigo do produto (somente numeros)', font='Roboto 10')],
    [sg.InputText(key='codigo', do_not_clear=True, font='Roboto 10')],
    [sg.Text('')],
    [sg.Button('Enviar', key='enviar', font='Roboto 10')],
    [sg.Multiline(size=(50, 10), key='result')],
]

window = sg.Window('gamalu-crawler', layout, margins=(15, 15)).Finalize()

while True:

    event, values = window.read()

    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        break

    productURL = 'https://www.magazineluiza.com.br/produto/calculo-frete/'+ values['cep'] +'/'+ values['codigo'] +'/magazineluiza.json'
    productHeaders = {
        'user-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'referer': 'https://www.magazineluiza.com.br',
    }

    productRequest = requests.get(productURL, headers=productHeaders)
    productData = json.loads(productRequest.text)

    for deliveryOption in productData['delivery']:

        if deliveryOption['distribution_center'] > 0:

            distributionCenterURL = 'https://lojas.magazineluiza.com.br/filiais/' + str(deliveryOption['distribution_center'])
            distributionCenterRequest = requests.get(distributionCenterURL)
            distributionCenterHTML = distributionCenterRequest.text

            firstCut = distributionCenterHTML[(103+distributionCenterHTML.find("col-7 col-md-8 m-auto")):]
            secondCut = firstCut[firstCut.find("data-v-12a79897")+16:]
            thirdCut = secondCut[secondCut.find("data-v-12a79897")+67:]

            name = firstCut.split("<")[0].strip()
            city = secondCut.split("<")[0]
            sellers = thirdCut.split("<")[0]

            deliveryOption['name'] = name
            deliveryOption['city'] = city
            deliveryOption['sellers'] = sellers

    result = "Formas de entrega: [\n"

    for deliveryOption in productData['delivery']:
        result += "   {\n"

        for attribute in deliveryOption:
            result += "      " + str(attribute) + ": " + str(deliveryOption[attribute]) + "\n"
    
        result += "   }\n"

    result += "]\n"

    window['result'].update(result)

window.close()