import json
import os
from urllib.parse import urljoin

from parsel import Selector
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

root_dir = os.path.dirname(os.path.realpath(__file__))
downloads_dir = os.path.join(root_dir, 'Downloads')


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

        comic_dir = os.path.join(downloads_dir, title)
        if os.path.isdir(comic_dir) is False:
            os.makedirs(comic_dir)
        json_path = os.path.join(comic_dir, title + '.json')
        if os.path.isfile(json_path) is True:
            with open(json_path) as f:
                comic_info = json.load(f)
        else:
            comic_info = {
                "title": title,
                "url": url,
                "subtitle_info": []
            }

        total_subtitles = len(_subtitles)
        for idx, sub in enumerate(_subtitles):
            print("{0:.1f}%: {1}".format(idx*100/total_subtitles, sub['subtitle']))
            subtitle_info = comic_info['subtitle_info']
            if len(subtitle_info) > idx:
                if subtitle_info[idx]['subtitle'] == sub['subtitle']:
                    continue
                else:
                    new_sub = {
                        'subtitle': sub['subtitle'],
                        'image_urls': self.parse_image(sub['subtitle_url'])
                    }
                    subtitle_info = subtitle_info[:idx] + [new_sub] + subtitle_info[idx:]
            else:
                subtitle_info.append({
                    'subtitle': sub['subtitle'],
                    'image_urls': self.parse_image(sub['subtitle_url'])
                })
            comic_info["subtitle_info"] = subtitle_info[:total_subtitles]
            with open(json_path, 'w') as f:
                f.write(json.dumps(comic_info, indent=4))
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
        tmp = img_sel.xpath('@src').extract()
        if tmp:
            url_template = img_sel.xpath('@src').extract()[0]
            url_template = 'https:' + url_template.strip('https:')[:-8]
            url_template = url_template.strip().strip('/')
            return ['{prefix}/{page_id:04d}.jpg'.format(prefix=url_template, page_id=page_id) for page_id in
                    range(1, img_cnt + 1)]
        else:
            return []


if __name__ == '__main__':
    urlpath = os.path.join(root_dir, 'urlfile.txt')
    if os.path.isfile(urlpath) is False:
        urlpath = os.path.join(root_dir, 'urlfile_default.txt')
    with open(urlpath, 'r') as f:
        for url in f.readlines():
            url = url.strip()
            print(url)
            # url = 'https://www.onemanhua.com/10263/'
            comic = Onemanhua()
            comic.start(url)
