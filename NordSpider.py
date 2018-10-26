import scrapy

from scrapy.http import Request
from scrapy.selector import Selector

class PianoSpider(scrapy.Spider):
    name = 'pianospider'
    start_urls = ['http://www.nordkeyboards.com/sound-libraries/nord-piano-library/information']

    def parse(self, response):
        for next_page in response.css('nav.menu-block-wrapper.menu-block-3.menu-name-main-menu.parent-mlid-0.menu-level-3 a::attr(href)').extract():
            self.logger.info('Found %s', next_page)
            yield response.follow(next_page, self.parsePianos)

    def parsePianos(self, response):
        for piano_page in response.css('nav.menu-block-wrapper.menu-block-5.menu-name-main-menu.parent-mlid-0.menu-level-4 a::attr(href)').extract():
            yield response.follow(piano_page, self.downloadPiano)

    def downloadPiano(self, response):
        sel = Selector(response)
        for download in sel.xpath("//div[@id='node-sound-library-full-group-download']/div/span/a"):
            href = download.xpath('@href').extract()[0]
            text = download.xpath('text()').extract()[0]
            self.logger.info('Href: %s', href)
            self.logger.info('Name: %s', text)

            yield Request(
                url=response.urljoin(href),
                callback=self.save_file,
                meta={'name':text}
            )

    def save_file(self, response):
        path = response.meta['name']
        self.logger.info('Saving File %s', path)
        with open(path, 'wb') as f:
            f.write(response.body)