# Bimmer Scrape

This is a set of spiders based on the `scrapy` library that crawl dealer websites and extract data about vehicles in stock. It currently has BMW X3 hardcoded as that's what I was looking for, but it should theoretically work for any make and model as long as the dealer uses one of the three supported platforms - _dealeron_, _dealer.com_ and _dealerinspire_.

The goal of this project is to democratize data on available vehicle inventory and serve as a free tool in your search for your next car.

## Setup

The easiest way to set this up is to use a python virtual environment. These instructions have been tested on OSX with python 3:

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
cd dealers
scrapy crawl bimmer_dealerinspire -o dealerinspire_inventory.json
scrapy crawl bimmer_dealercom -o dealercom_inventory.json
scrapy crawl bimmer_dealeron -o dealeron_inventory.json
```

I've found it easy to browse inventory from the command line by using `jq`. You can sort and filter, for example:

```
cat dealerinspire_inventory.json | jq 'sort_by(.msrp)' | less
```

## TODO

- [ ] Onboard all dealers across the US. This should be as easy as copy/pasting their websites in the spider code.
- [ ] Auto-discover dealers. This can be done using a spider crawling https://bmwusa.com/
- [ ] Add links to vehicles.
- [ ] Follow vehicle links and scrape options and colors.
- [ ] Extend to other brands.
- [ ] Preserve output in a database. Elasticsearch should work very well.
- [ ] Build a UI.
