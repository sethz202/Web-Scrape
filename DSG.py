from discord_webhook import DiscordWebhook, DiscordEmbed
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from time import sleep
from datetime import datetime


class DSG:
    def __init__(self):
        self.number = 0
        self.totalProducts = {}
        self.chrome = ChromeDriverManager().install()

    def runMonitor(self):
        options = Options()
        options.headless = True
        userAgent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15"
        options.add_argument("user-agent="+ userAgent)
        driver = webdriver.Chrome(self.chrome, options=options)
        driver.get("https://www.dickssportinggoods.com/search/SearchDisplay?searchTerm=air%20force%201&storeId=15108&catalogId=12301&langId=-1&sType=SimpleSearch&resultCatEntryType=2&showResultsPage=true&fromPage=Search&searchSource=Q&pageView=&beginIndex=0&DSGsearchType=Keyword&pageSize=48&selectedStore=407")
        sleep(5)
        driver.refresh()
        sleep(5)
        AF1HTML = driver.page_source
        driver.get("https://www.dickssportinggoods.com/search/SearchDisplay?searchTerm=Jordan%201&storeId=15108&catalogId=12301&langId=-1&sType=SimpleSearch&resultCatEntryType=2&showResultsPage=true&fromPage=Search&searchSource=Q&pageView=&beginIndex=0&DSGsearchType=Keyword&pageSize=48&selectedStore=407")
        sleep(5)
        driver.refresh()
        sleep(5)
        AJ1HTML = driver.page_source
        index = 0
        AF1Indexes = []
        AJ1Indexes = []
        differentProducts = []
        differentShoes = []
        while index < len(AF1HTML):
            index = AF1HTML.find('dsg-flex flex-column dsg-react-product-card rs_product_card dsg-react-product-card-col-4', index)
            if index == -1:
                break
            AF1Indexes.append(index)
            index += 88
        for i in AF1Indexes:
            editedAFHTML = AF1HTML[i:]
            replacedAFHTML = editedAFHTML.replace('</div>', 'XXXXXX', 8)
            lastAFDiv = replacedAFHTML.find('</div>')+6
            AFCheck = AF1HTML[i:lastAFDiv+i]
            AFW = 'Women'
            AFM = 'Men'
            if AFW in AFCheck:
                differentProducts.append(AFCheck)
            if AFM in AFCheck:
                differentProducts.append(AFCheck)
        index = 0
        while index < len(AJ1HTML):
            index = AJ1HTML.find('dsg-flex flex-column dsg-react-product-card rs_product_card dsg-react-product-card-col-4', index)
            if index == -1:
                break
            AJ1Indexes.append(index)
            index += 88
        for j in AJ1Indexes:
            editedAJHTML = AJ1HTML[j:]
            replacedAJHTML = editedAJHTML.replace('</div>', 'XXXXXX', 8)
            lastAJDiv = replacedAJHTML.find('</div>')+6
            AJCheck = AJ1HTML[j:lastAJDiv+j]
            AJ = 'Jordan 1'
            if AJ in AJCheck:
                differentProducts.append(AJCheck)
        for products in differentProducts:
            productLink = "https://www.dickssportinggoods.com"+products[products.find('href="')+6:products.find('title')-2]
            productColors = products.count('radio')
            driver.get(productLink)
            sleep(3)
            for x in range(productColors):
                driver.find_element(By.XPATH, '//*[@id="attr_Color"]/div[2]/pdp-color-attribute/div/div/button['+str(x+1)+']').click()
                shoeHTML = driver.page_source
                beginPage = shoeHTML.find('class="row no-gutters product-heading">')
                endPage = shoeHTML.find('Product Information') + 20
                finalShoeHTML = shoeHTML[beginPage:endPage]
                title = finalShoeHTML[finalShoeHTML.find('class="title"')+14:finalShoeHTML.find('</h1>')-6]
                productPrice = finalShoeHTML[finalShoeHTML.find('class="product-price ng-star-inserted"')+39:finalShoeHTML.find('</span>')]
                beginSize = finalShoeHTML.find('<div class="tfc-cfg-popup-indicator"></div>')
                endSize =  finalShoeHTML.find("Shoe Width")+10
                sizesHTML = finalShoeHTML[beginSize:endSize]
                index = 0
                sizeIndex = []
                individualSize = []
                while index < len(sizesHTML):
                    index = sizesHTML.find('<button', index)
                    if index == -1:
                        break
                    sizeIndex.append(index)
                    index += 7
                for k in sizeIndex:
                    editedSizeHTML = sizesHTML[k:]
                    individualSize.append(sizesHTML[k:editedSizeHTML.find('</button>')+9+k])
                availableSizes = []
                for singleSize in individualSize:
                    OOS = 'swatch-disabled'
                    if OOS not in singleSize:
                        availableSizes.append(singleSize[singleSize.find('class="ng-star-inserted">')+25:singleSize.find('</span>')])
                beginImage = finalShoeHTML.replace('srcset', 'xxxxxx', x).find('srcset')+8
                getImage = finalShoeHTML[beginImage:]
                endImage = getImage.find('"')
                imageLink = finalShoeHTML[beginImage:endImage+beginImage]
                differentShoes.append(imageLink)
                if imageLink not in self.totalProducts:
                    self.totalProducts[imageLink] = [title, imageLink, productLink, productPrice, availableSizes]
                    print("Adding", title, "to the monitor")
                    sleep(1)
                    DSG.sendWebhook(self, self.totalProducts[imageLink][0], self.totalProducts[imageLink][1], self.totalProducts[imageLink][2], self.totalProducts[imageLink][3], self.totalProducts[imageLink][4])
        productsInDictionary = []
        for key in self.totalProducts.keys():
            productsInDictionary.append(key)
        for x in range(len(productsInDictionary)):
            if productsInDictionary[x] not in differentShoes:
                print('Removing', self.totalProducts[productsInDictionary[x]][0], 'from monitor')
                del self.totalProducts[productsInDictionary[x]]

    def sendWebhook(self, title, imageLink, productLink, price, sizesList):
        webhook = DiscordWebhook(url='https://discord.com/api/webhooks/855550421555740672'
                                     '/LmeYPGGXNBDNvX2ihTcOO7vPjAOKmxc30v7dJ7RQBmtJl2Dk6jYopGYH4CTI-j2__yQD')
        embed = DiscordEmbed(title="New product added on DSG", description='**['+title+']('+productLink+')**')
        embed.set_thumbnail(url=imageLink)
        embed.set_footer(text='sethz202')
        embed.set_timestamp()
        if price != 0:
            embed.add_embed_field(name='Price:', value=price)
        else:
            embed.add_embed_field(name='Price:', value="Check website for price")
        sizesString = ''
        x = 2
        for size in sizesList:
            sizesString += size + "\t"
            if sizesString.count(".") == x:
                sizesString += "\n\t"
                x += 2
        embed.add_embed_field(name='Sizes:', value=sizesString)
        webhook.add_embed(embed)
        webhook.execute()


run = DSG()
while True:
    run.runMonitor()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("["+current_time+"]", "Waiting 30 seconds until next check")
    sleep(30)
