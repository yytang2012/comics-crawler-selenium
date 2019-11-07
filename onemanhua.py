import json
from urllib.parse import urljoin

from parsel import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def verify_url_format(url):
    #  Example: https://www.onemanhua.com/10262/
    import re
    p = 'https://www.onemanhua.com/[\d]+'
    m = re.match(p, url)
    return m.group(0) if m else None


class Onemanhua:
    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        # chrome_options.add_argument("--window-size=1920x1080")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def start(self, url):
        homepage = verify_url_format(url)
        self.driver.get(homepage)
        title = self.parse_title()
        _subtitles = self.parse_subtitles()
        _subtitles = _subtitles[:]

        print(title)
        for sub in _subtitles:
            print(sub)

        subtitle_info = []
        for sub in _subtitles:
            subtitle_info.append({
                'subtitle': sub['subtitle'],
                'image_urls': self.parse_image(sub['subtitle_url'])
            })
            results = {
                "title": title,
                "subtitle_info": subtitle_info
            }
            with open('Downloads/{0}.json'.format(title), 'w') as f:
                f.write(json.dumps(results, indent=4))
        self.driver.quit()

    def parse_title(self):
        _driver = self.driver
        sel = Selector(text=_driver.page_source)
        title = sel.xpath('//h1/text()').extract()[0]
        return title

    def parse_subtitles(self):
        _driver = self.driver
        sel = Selector(text=_driver.page_source)
        subtitle_sel = sel.xpath('//div[@class="all_data_list"]')[0].xpath('ul[@class="fed-part-rows"]/li/a')
        subtitles = []
        for tmp_sel in subtitle_sel:
            subtitles.append({
                "subtitle": tmp_sel.xpath('text()').extract()[0],
                "subtitle_url": urljoin(_driver.current_url, tmp_sel.xpath('@href').extract()[0])
            })
        return subtitles[::-1]

    def parse_image(self, subtitle_url):
        _driver = self.driver
        _driver.get(subtitle_url)
        sel = Selector(text=_driver.page_source)

        img_sel = sel.xpath('//div[@id="mangalist"]/div[@class="mh_comicpic"]/img')
        img_cnt = len(img_sel)
        url_template = img_sel.xpath('@src').extract()[0]
        url_template = 'https:' + url_template.strip('https:')[:-8]
        url_template = url_template.strip().strip('/')
        return ['{prefix}/{page_id:04d}.jpg'.format(prefix=url_template, page_id=page_id) for page_id in
                range(1, img_cnt + 1)]


if __name__ == '__main__':
    url = 'https://www.onemanhua.com/12233/'
    comic = Onemanhua()
    comic.start(url)
