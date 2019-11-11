# -*- coding: utf-8 -*
import json
import os
import shutil

comic_name = '妹子与科学'
root_dir = '/media/yytang/Data/comics/comics_downloads'

if __name__ == '__main__':
    src_dir = os.path.join(root_dir, comic_name)
    dst_dir = os.path.join(root_dir, comic_name + '-volumes')
    if os.path.isdir(dst_dir) is False:
        os.mkdir(dst_dir)
    json_file = os.path.join(src_dir, comic_name + '.json')
    with open(json_file, 'r') as f:
        comic_info = json.load(f)
    subtitles = [sub['subtitle'] for sub in comic_info['subtitle_info']]
    volume_id = 1
    volume_page_threshold = 200
    volume_page = 1
    for subtitle in subtitles:
        print(subtitle)
        volume_name = 'volume{0:02d}'.format(volume_id)
        volume_path = os.path.join(dst_dir, volume_name)
        if not os.path.isdir(volume_path):
            os.makedirs(volume_path)
        sub_dir = os.path.join(src_dir, subtitle)
        images = [img for img in os.listdir(sub_dir)]
        images.sort()
        for idx, img in enumerate(images):
            src = os.path.join(sub_dir, img)
            if os.path.isfile(src) and img[-4:] == '.jpg':
                dst = os.path.join(volume_path, '{0:03d}.jpg'.format(volume_page + idx))
                shutil.copy(src, dst)
        volume_page += len(images)
        if volume_page > volume_page_threshold:
            volume_page = 1
            volume_id += 1




