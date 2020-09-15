# -*- coding: utf-8 -*
import json
import os

DEFAULT_ROOT_DIR = '/media/yytang/DATA/yytang/comics'
DEFAULT_ROOT_DIR = os.path.expanduser(DEFAULT_ROOT_DIR)
if os.path.isdir(DEFAULT_ROOT_DIR) is True:
    root_dir = DEFAULT_ROOT_DIR
else:
    _here = os.path.dirname(os.path.realpath(__file__))
    root_dir = os.path.join(_here, 'Downloads')


def download_comics():
    for title in os.listdir(root_dir):
        comic_dir = os.path.join(root_dir, title)
        json_path = os.path.join(comic_dir, title + '.json')
        if os.path.isdir(comic_dir) is True and os.path.isfile(json_path) is True:
            with open(json_path, 'r') as f:
                comic_info = json.load(f)
            subtitle_info = comic_info['subtitle_info']
            print(comic_dir)
            for item in subtitle_info:
                subtitle = item['subtitle']
                image_urls = item['image_urls']
                subtitle_dir = os.path.join(comic_dir, subtitle)
                if os.path.isdir(subtitle_dir) is False:
                    os.makedirs(subtitle_dir)
                for url in image_urls:
                    image_file = url.split('/')[-1].strip()
                    image_path = os.path.join(subtitle_dir, image_file)
                    if os.path.isfile(image_path) is False:
                        cmd = 'wget "{url}" -P "{directory}"'.format(url=url, directory=subtitle_dir)
                        print(cmd)
                        os.system(cmd)
                    else:
                        # print("{image_path} was downloaded".format(image_path=image_path))
                        pass


if __name__ == '__main__':
    download_comics()
