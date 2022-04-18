# -*- coding: utf-8 -*-

"""
扫描文件夹下md文件中图片引用 与 ./${filename}.asstes文件夹下图片文件 对比
删除或者移动没有引用的图片文件
详细步骤：

1. 获取path下的所有文件
2. 判定是否是md文件，是md文件放入md_list文件数组
3. 不是md文件，判定是否是文件夹，是文件夹并且不是'.assets'后缀结尾的话重复1步骤，直到列举出所有的md文件
4. 是'.assets'后缀结尾的文件夹就提取文件夹下的所有图片文件放到md_pic图片数组
5. 遍历md_list文件数组,获取文档的图片地址，与md_pic图片数组对比判断是否移除

正则表达式：
1. 常规引用 形如 ![]()
(?:!\[在这里插入图片描述\]\((.*?)\)) # 只提取url
(?:!\[(.*?)\]\((.*?)\)) # 提取描述与rul

2. html引用 形如 <img src="image-20220123110227320.png" alt="image-20220123110227320" style="zoom:50%;" />
src=\".*(?=\")\"
"""

import os
import re
import shutil

# 删除开关，请谨慎操作 0 dry_run; 1 force_delete; 2 move_trash; 'path' move to path
enable_delete = '/Users/ppphuang/Documents/typora/trash'
# enable_delete = 0
path = "/Users/ppphuang/Documents/typora"

if isinstance(enable_delete, str) and bool(1 - os.path.exists(enable_delete)):
    print("目标文件夹不存在：" + enable_delete)
    exit(0)

md_list = []
md_pic = {}
del_dir_list = []
del_pic_list = []


def listdirs(path):
    file_names = os.listdir(path)
    for file_name in file_names:
        suffix_name = file_name.split(".")[-1]
        full_path = path + '/' + file_name
        if suffix_name in ["md"]:
            print("发现Markdown：" + full_path)
            md_list.append(full_path)
            asset_path = path + '/.' + file_name[:-3] + '.assets'
            if os.path.exists(asset_path):
                asset_file_list = os.listdir(asset_path)
                if len(asset_file_list) == 0:
                    del_dir_list.append(asset_path)
                for asset_file in asset_file_list:
                    asset_file_suffix_name = asset_file.split(".")[-1]
                    if asset_file_suffix_name in ["png", "jpg", "jpeg", "gif", "svg"]:
                        print("发现图片：" + asset_path + '/' + asset_file)
                        if full_path in md_pic:
                            md_pic[full_path].append(asset_path + '/' + asset_file)
                        else:
                            md_pic[full_path] = [asset_path + '/' + asset_file]

        if os.path.isdir(full_path) and suffix_name not in ["asset"]:
            # 递归查找子文件夹中的文件
            listdirs(full_path)


listdirs(path)

print("--------------------------------------------------")
print("Markdown列表：", md_list)
print("--------------------------------------------------")

for md_name in md_list:
    print("--------------------------------------------------")
    print("文章：", md_name)
    if md_name not in md_pic:
        continue
    with open(md_name, 'r+') as f:
        content = f.read()
        # 查找常规引用
        pic_infos = re.findall(r'(?:!\[(.*?)\]\((.*?)\))', content)
        print("本文图片信息：", pic_infos.__len__(), pic_infos)
        pic_info_path = []
        for pic_info in pic_infos:
            pic_info_path.append(pic_info[1])
        # 查找HTML引用
        pic_info_htmls = re.findall(r'src=\".*(?=\")\"', content)
        print("本文HTML图片信息：", pic_info_htmls.__len__(), pic_info_htmls)
        for pic_info_html in pic_info_htmls:
            pic_info_path.append(pic_info_html.split("\"")[1])
        pic_list = md_pic[md_name]
        for pic in pic_list:
            pic_path = pic.split('/')[-2] + '/' + pic.split('/')[-1]
            if pic_path not in pic_info_path:
                print("发现未引用图片：", pic)
                del_pic_list.append(pic)

print("--------------------------------------------------")
print("未引用可删除图片列表：", del_pic_list.__len__(), del_pic_list)
print("--------------------------------------------------")


def remove(path):
    if enable_delete == 0:
        print("dry run 准备删除：", path)
    elif enable_delete == 1:
        print("force delete 准备删除：", path)
        # 文件夹需使用os.rmdir(path)删除
        if os.path.isdir(path):
            os.rmdir(path)
        else:
            os.remove(path)
    elif enable_delete == 2:
        print("move trash 准备删除：", path)
        shutil.move(path, '~/.Trash')
    elif isinstance(enable_delete, str) and os.path.exists(enable_delete):
        print("move virtual trash 准备删除：", path)
        shutil.move(path, enable_delete)


# 删除无用图片
for pic in del_pic_list:
    remove(pic)
    parent_path = pic[:pic.rindex('/')]
    # 删除图片后判断父文件夹是否为空
    if len(os.listdir(parent_path)) == 0:
        # 为空添加到待删除文件夹列表中
        del_dir_list.append(parent_path)

# 删除空文件夹
for dir in del_dir_list:
    remove(dir)
