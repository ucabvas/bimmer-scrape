import scrapy
import js2py
import logging
from . import util

# spider for dealer.com templated websites
class BimmerDealercomSpider(scrapy.Spider):
    name = 'bimmer_dealercom'

    dealers = [
        {
            "name": 'Paul Miller BMW',
            "url": 'https://www.paulmillerbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Bloomfield',
            "url": 'https://www.bmwofbloomfield.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'Park Avenue BMW',
            "url": 'https://www.parkavebmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Ramsey',
            "url": 'https://www.bmwramsey.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'Princeton BMW',
            "url": 'https://www.princetonbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Freehold',
            "url": 'https://www.bmwoffreehold.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Mt. Laurel',
            "url": 'https://www.bmwofmtlaurel.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Watertown',
            "url": 'https://www.bmwofwatertown.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'Thompson BMW',
            "url": 'https://www.thompsonbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'Daniels BMW',
            "url": 'https://www.danielsbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'West German BMW',
            "url": 'https://www.westgermanbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of the Main Line',
            "url": 'https://www.bmwmainline.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'Tom Hesser BMW',
            "url": 'https://www.tomhesserbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Devon',
            "url": 'https://www.bmwofdevon.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'Wyoming Valley BMW',
            "url": 'https://www.bmwofwyomingvalley.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
        {
            "name": 'BMW of Reading',
            "url": 'https://www.bmwofreading.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {
                "no_ddc": True
            }
        },
        {
            "name": 'Union Park BMW',
            "url": 'https://www.unionparkbmw.com/new-inventory/index.htm?model=X3&sortBy=internetPrice+desc&',
            "settings": {}
        },
    ]

    def start_requests(self):
        for dealer in self.dealers:
            name, url, settings = dealer['name'], dealer['url'], dealer['settings']
            yield scrapy.Request(url=url, callback=self.parse, cb_kwargs=dict(dealer_name=name, settings=settings))


    def __parse_ddc(self, response, settings):
        logging.info("DDC parsing.")

        # this one is default because it's more reliable
        DL_XPATH = '//div[@class=" ddc-content tracking-ddc-data-layer"]/script/text()'
        javascript = response.xpath(DL_XPATH)[0].get()
        prep = "window={DDC: {siteSettings:{proximityAccount:\'\'}}};\n"

        context = js2py.EvalJs()
        context.execute(prep+javascript)

        for vehicle in context.window.DDC.dataLayer.vehicles:
            options = (vehicle['optionCodes'] or []) + (vehicle['optionCodesOther'] or [])
            title = "%s %s %s %s" % (vehicle['modelYear'], vehicle['make'], vehicle['model'], vehicle['trim'])

            yield {
                'dealer': vehicle['accountName'],
                'title': title,
                'msrp': vehicle['msrp'],
                'odometer': vehicle['odometer'],
                'vin': vehicle['vin'],
                'options': options
            }

    def __parse_no_ddc(self, response, dealer_name, settings):
        logging.info("No DDC parsing.")

        # this one is less preferable as it uses the dom elements and not the DDC json
        LI_XPATH = "//ul[contains(@class, 'gv-inventory-list')]/li"

        for li in response.xpath(LI_XPATH):
                MSRP_XPATH = '*//li[contains(@class, "finalPrice")]//span[@class="value"]//text()'

                yield {
                    'dealer': dealer_name,
                    'title': "%s %s %s %s" % (li.xpath('@data-year').get(), li.xpath('@data-make').get(), li.xpath('@data-model').get(), li.xpath('@data-trim').get()),
                    'msrp': util.parse_msrp(li.xpath(MSRP_XPATH).get()),
                    'vin': li.xpath('@data-vin').get(),
                    'ext_color': li.xpath('@data-exteriorcolor').get(),
                    'int_color': li.xpath('@data-interiorcolor').get(),
                    'odometer': li.xpath('@data-odometer').get(),
                    'options': []
                }

    def parse(self, response, dealer_name, settings):
        if ('no_ddc' in settings) and settings['no_ddc']:
            for vehicle in self.__parse_no_ddc(response, dealer_name, settings):
                yield vehicle
        else:
            for vehicle in self.__parse_ddc(response, settings):
                yield vehicle

        next_page = response.xpath('(//a[@rel="next" and not(contains(@class, "disabled"))])[1]/@href').get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse, cb_kwargs=dict(dealer_name=dealer_name, settings=settings))

'''
UL_XPATH = "//ul[contains(@class, 'gv-inventory-list')]"
li[data-year]

'''