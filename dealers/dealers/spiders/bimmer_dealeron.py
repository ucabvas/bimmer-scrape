import scrapy


# spider for dealer.com templated websites
class BimmerDealeronSpider(scrapy.Spider):
    name = 'bimmer_dealeron'
    
    dealers = [
        {
            "name": 'BMW of Morristown',
            "url": 'https://www.morristownbmw.com/searchnew.aspx?pn=100&Model=X3&st=Price+desc',
            "settings": {}
        },
        {
            "name": 'BMW of Roxbury',
            "url": 'https://www.bmwrox.com/searchnew.aspx?pn=100&Model=X3&st=Price+desc',
            "settings": {}
        },
        {
            "name": 'BMW of Newton',
            "url": 'https://www.bmwnewton.com/searchnew.aspx?pn=100&Model=X3&st=Price+desc',
            "settings": {}
        },
        {
            "name": 'Open Road BMW',
            "url": 'https://www.bmwedison.com/searchnew.aspx?pn=100&Model=X3&st=Price+desc',
            "settings": {}
        },
        {
            "name": 'Flemington BMW',
            "url": 'https://www.flemingtonbmw.com/searchnew.aspx?pn=100&Model=X3&st=Price+desc',
            "settings": {}
        },
    ]

    def start_requests(self):
        for dealer in self.dealers:
            name, url, settings = dealer['name'], dealer['url'], dealer['settings']
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(dealer_name=name, settings=settings))

    def parse(self, response, dealer_name, settings):
        UL_XPATH = '//*[@class="row srpVehicle hasVehicleInfo"]'

        for ul in response.xpath(UL_XPATH):
                yield {
                    'dealer': dealer_name,
                    'title': "%s %s %s %s" % (ul.xpath('@data-year').get(), ul.xpath('@data-make').get(),ul.xpath('@data-model').get(),ul.xpath('@data-trim').get()),
                    'msrp': ul.xpath('@data-msrp').get(),
                    'price': ul.xpath('@data-price').get(),
                    'vin': ul.xpath('@data-vin').get(),
                    'ext_color': ul.xpath('@data-extcolor').get(),
                    'int_color': ul.xpath('@data-intcolor').get(),
                    'options': []
                }

        #NEXT_PAGE = '/html/body/div[3]/div[2]/div/div[3]/div[2]/div[2]/form/div/div[3]/div/div/div[2]/ul/li[3]/a/@href'
        #next_page = response.xpath(NEXT_PAGE).get()
        #if next_page is not None:
        #    yield response.follow(next_page, self.parse)



# StratosDealerEngine
#   scraping logic
# curl -XGET -H 'Content-Type: application/json' https://www.flemingtonbmw.com/api/InventoryWidget/Galleria/?vin=5UXTY9C03L9C80441

#  get options:  'https://www.flemingtonbmw.com/vehicleoptionscomments.aspx?id=5214&vin=5UXTY9C03L9C80441'
