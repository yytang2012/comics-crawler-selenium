import json
import os
import time
from urllib.parse import urljoin, quote
import re
from parsel import Selector
from selenium import webdriver

root_dir = os.path.dirname(os.path.realpath(__file__))
downloads_dir = os.path.join(root_dir, 'Downloads')


def verify_url_format(url):
    #  Example: https://www.ohmanhua.com/10262/
    p = 'https://www.ohmanhua.com/([\d]+)'
    m = re.match(p, url)

    return (m.group(0), m.group(1)) if m else None


def subtitle_analysis(subtitle_string):
    p = '([^(]+)\(([\d]+)P\)'
    m = re.search(p, subtitle_string)
    subtitle = m.group(1).strip()
    pages = int(m.group(2).strip())
    return subtitle, pages


class Onemanhua:
    def __init__(self, headless=False):
        self.driver = self.initialize_driver(headless=headless)

    def start(self, url):
        res = verify_url_format(url)
        if res is None:
            return
        homepage, cid = res
        self.driver.get(homepage)
        title = self.parse_title()
        _subtitles = self.parse_subtitles()

        print(title)
        for sub in _subtitles:
            print(sub)

        comic_dir = os.path.join(downloads_dir, title)
        if os.path.isdir(comic_dir) is False:
            os.makedirs(comic_dir)
        json_path = os.path.join(comic_dir, title + '.json')
        if os.path.isfile(json_path) is True:
            with open(json_path) as fp:
                comic_info = json.load(fp)
        else:
            comic_info = {
                "title": title,
                "url": url,
                "subtitle_info": []
            }

        total_subtitles = len(_subtitles)
        subtitle_info = comic_info['subtitle_info']
        for idx, sub in enumerate(_subtitles):
            print("{0:.1f}%: {1}".format(idx * 100 / total_subtitles, sub['subtitle']))
            if len(subtitle_info) > idx:
                if subtitle_info[idx]['subtitle'] == sub['subtitle']:
                    subtitle_info[idx]['subtitle_url'] = sub['subtitle_url']
                    continue
                else:
                    new_sub = {
                        'subtitle': sub['subtitle'],
                        'subtitle_url': sub['subtitle_url'],
                        'image_urls': self.parse_image(sub['subtitle'], sub['subtitle_url'], cid)
                    }
                    subtitle_info = subtitle_info[:idx] + [new_sub] + subtitle_info[idx:]
            else:
                subtitle_info.append({
                    'subtitle': sub['subtitle'],
                    'subtitle_url': sub['subtitle_url'],
                    'image_urls': self.parse_image(sub['subtitle'], sub['subtitle_url'], cid)
                })
            comic_info["subtitle_info"] = subtitle_info[:total_subtitles]
            with open(json_path, 'w') as fp:
                fp.write(json.dumps(comic_info, indent=4))

        comic_info["subtitle_info"] = subtitle_info[:total_subtitles]
        with open(json_path, 'w') as fp:
            fp.write(json.dumps(comic_info, indent=4))
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
                "subtitle": tmp_sel.xpath('text()').extract()[0].strip(),
                "subtitle_url": urljoin(_driver.current_url, tmp_sel.xpath('@href').extract()[0].strip())
            })
        return subtitles[::-1]

    def initialize_driver(self, headless=False):
        options = webdriver.FirefoxOptions()
        if headless is True:
            options.add_argument("--headless")
        _driver = webdriver.Firefox(options=options)
        return _driver

    def get_selector(self, web_url):
        _driver = self.driver
        _fetched = False
        attempt_count = 5
        selector = None
        while _fetched is False and attempt_count > 0:
            try:
                _driver.execute_script("window.scrollTo(0, 3000);")
                _driver.get(web_url)
                selector = Selector(text=_driver.page_source)
                _fetched = True
            except Exception as e:
                attempt_count -= 1
                print(web_url)
                time.sleep(1)
                _driver = self.initialize_driver()
        self.driver = _driver
        return selector

    def parse_image(self, subtitle, subtitle_url, cid):
        selector = self.get_selector(subtitle_url)
        img_sel = selector.xpath('//div[@class="mh_mangalist tc"]/div[@class="mh_comicpic"]')
        pages = len(img_sel)

        return ['https://img.ohmanhua.com//comic/{cid}/{subtitle}/{page_id:04d}.jpg'.format(
            cid=cid, subtitle=quote(subtitle), page_id=pid
        ) for pid in range(1, pages + 1)]


    def parse_image2(self, subtitle_string, cid):
        subtitle, page = subtitle_analysis(subtitle_string)
        # https://img.onemanhua.com/comic/10895/%E7%AC%AC3%E5%AD%A340%E8%AF%9D%20%E5%96%84%E5%90%8E/0001.jpg
        url_template = 'https://img.onemanhua.com/comic/{cid}/{subtitle}/{page_id:04d}.jpg'
        return ['https://img.onemanhua.com/comic/{cid}/{subtitle}/{page_id:04d}.jpg'.format(
            cid=cid, subtitle=quote(subtitle), page_id=pid
        ) for pid in range(1, page + 1)]


if __name__ == '__main__':
    urlpath = os.path.join(root_dir, 'urlfile.txt')
    hide_browser = os.environ.get('HIDE_BROWSER', "No")
    headless = True if hide_browser.lower() in ["y", "yes"] else False
    if os.path.isfile(urlpath) is False:
        urlpath = os.path.join(root_dir, 'urlfile_default.txt')
    with open(urlpath, 'r') as f:
        for url in f.readlines():
            url = url.strip()
            if not url:
                continue
            print(url)
            # url = 'https://www.onemanhua.com/10263/'
            comic = Onemanhua(headless=headless)
            comic.start(url)
