import requests
import json

productURL = 'https://www.magazineluiza.com.br/produto/calculo-frete/05335060/155556000/magazineluiza.json'
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
    
pprint.pprint(productData)