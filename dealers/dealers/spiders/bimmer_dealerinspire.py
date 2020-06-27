import scrapy
import json
import js2py
import logging
from . import util

# spider for dealer.com templated websites
class BimmerDealerinspireSpider(scrapy.Spider):
    name = 'bimmer_dealerinspire'
    
    dealers = [
        {
            "name": 'BMW of Springfield',
            "url": 'https://www.bmwofspringfieldnj.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwofspringfieldnj.com/en',

        },
        {
            "name": 'BMW of Tenafly',
            "url": 'https://www.bmwoftenafly.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwoftenafly.com/en',
        },
        {
            "name": 'Circle BMW',
            "url": 'https://www.circlebmw.com/new-vehicles/x3/',
            "ajax_url": 'https://www.circlebmw.com/en',
            "settings": {
                "_referer": "/new-vehicles/new-bmw-x3-for-sale-eatontown-nj/"
            }
        },
        {
            "name": 'BMW of Turnersville',
            "url": 'https://www.bmwofturnersville.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwofturnersville.com/en',
        },
        {
            "name": 'BMW of Atlantic City',
            "url": 'https://www.bmwatlanticcity.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwatlanticcity.com/en',
        },
        {
            "name": 'BMW of Greenwich',
            "url": 'https://www.bmwofgreenwich.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwofgreenwich.com/en',
        },
        {
            "name": 'Continental BMW of Darien',
            "url": 'https://www.bmwdarien.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwdarien.com/en',
        },
        {
            "name": 'BMW of Ridgefield',
            "url": 'https://www.bmwofridgefield.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwofridgefield.com/en',
        },
        {
            "name": 'BMW of Bridgeport',
            "url": 'https://www.bmwofbridgeport.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwofbridgeport.com/en',
        },
        {
            "name": 'BMW of North Haven',
            "url": 'https://www.bmwofnorthhaven.com/new-vehicles/x3/',
            "ajax_url": 'https://www.bmwofnorthhaven.com/en',
        },
        {
            "name": "Otto \'s BMW",
            "url": 'https://www.ottosbmw.com/new-car/x3/',
            "ajax_url": 'https://www.ottosbmw.com/en',
            "settings": {
                "_referer": "/new-car/x3/"
            }
        },
    ]

    def start_requests(self):
        for dealer in self.dealers:
            yield scrapy.Request(url=dealer['url'], callback=self.request_ajax, meta={'cookiejar': dealer['name']}, cb_kwargs=dict(dealer=dealer))


    def request_ajax(self, response, dealer):
        # so the main page has loaded, we now want to find the ajax params and kick off the `/en` bit
        context = js2py.EvalJs()
        for script in response.xpath("//script/text()"):
            if "var inventory_localization" in script.get():
                # found it
                context.execute(script.get())

        ajax_nonce = context.inventory_localization['ajax_nonce']
        page_id = context.inventory_localization['page']['ID']
        _referer = "/new-vehicles/x3/"
        if ('settings' in dealer) and ('_referer' in dealer['settings']):
            _referer = dealer['settings']['_referer']

        yield scrapy.FormRequest(
            url=dealer['ajax_url'],
            headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
            formdata={
                "action": "im_ajax_call",
                "perform": "get_results",
                "page": "1",
                "_nonce": str(ajax_nonce),
                "_post_id": str(page_id),
                "_referer": _referer,
            },
            method='POST',
            callback=self.parse,
            meta={'cookiejar': dealer['name'], 'urlunencode': True},
            cb_kwargs=dict(dealer=dealer, page_number=1, page_id=page_id, ajax_nonce=ajax_nonce)
        )

    def parse(self, response, dealer, page_number, page_id, ajax_nonce):

        data = json.loads(response.text)
        selector = scrapy.Selector(text=data['results'], type="html")
        LI_XPATH = '//*[@class="vehicle list-view new-vehicle publish"]'

        for ul in selector.xpath(LI_XPATH):
            VIN_XPATH = '*//div[@class="vinstock"]/span[1]/text()'
            MSRP_XPATH = '*//span[@class="price"]/text()'

            yield {
                'dealer': dealer['name'],
                'title': "%s %s %s %s" % (ul.xpath('@data-year').get(), ul.xpath('@data-make').get(),ul.xpath('@data-model').get(),ul.xpath('@data-trim').get()),
                'msrp': util.parse_msrp(ul.xpath(MSRP_XPATH).get()),
                #'price': ul.xpath('@data-price').get(),
                'vin': ul.xpath(VIN_XPATH).get(),
                'odometer': ul.xpath('@data-mileage').get(),
                'ext_color': ul.xpath('@data-ext-color').get(), # data-ext-color
                'int_color': ul.xpath('@data-int-color').get(), # data-int-color
                'options': []
            }

        
        page_count = int(data['page_count'])
        if page_number < page_count:
            _referer = "/new-vehicles/x3/"
            if ('settings' in dealer) and ('_referer' in dealer['settings']):
                _referer = dealer['settings']['_referer']

            yield scrapy.FormRequest(
                url=dealer['ajax_url'],
                headers={"Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"},
                formdata={
                    "action": "im_ajax_call",
                    "perform": "get_results",
                    "page": str(page_number+1),
                    "_nonce": str(ajax_nonce),
                    "_post_id": str(page_id),
                    "_referer": _referer,
                },
                method='POST',
                callback=self.parse,
                meta={'cookiejar': dealer['name'], 'urlunencode': True},
                cb_kwargs=dict(dealer=dealer, page_number=page_number+1, page_id=page_id, ajax_nonce=ajax_nonce)
            )

# window.DealerInspireInventory
# window.DIDataLayer
# curl -XPOST 'https://www.bmwofgreenwich.com/en' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' --data-raw 'action=im_ajax_call&perform=get_results&model%5B%5D=X3&page=1&vrp_view=listview&order=DESC&orderby=price&_nonce=6163ceb5bab2327fb0a19c0b78f7a831&_post_id=6&_referer=/new-vehicles/'
# curl -XPOST 'https://www.bmwofgreenwich.com/en' -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' --data-raw 'action=im_ajax_call&perform=get_results&model%5B%5D=X3&page=2&vrp_view=listview&order=DESC'