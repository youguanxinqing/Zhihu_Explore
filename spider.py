import time
import requests

from urllib import parse
from bs4 import BeautifulSoup

from CONFIG import *


def get_one_html(url, tries=3):
    """
    请求每一页的数据
    :param url:
    :param tries:
    :return:
    """
    try:
        response = requests.get(url=url, headers=HEADERS, allow_redirects=False)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        print("response.url:"+response.url)
    except:
        if tries <= 0:
            FAILURE_URL.append(url)
            return None
        else:
            get_one_html(url, tries-1)

    else:
        return response.text

def parse_html(html):
    """
    利用美丽汤提取数据
    :param html:
    :return:
    """
    soup = BeautifulSoup(html, "lxml")
    nodes = soup.find_all(class_="explore-feed feed-item")

    for node in nodes:

        yield {
            "title": node.find(class_="question_link").string,
            "vote": node.find(class_="zm-item-vote").a.string,
            "author": node.find(class_="summary-wrapper").text,
            "content": node.find(class_="zh-summary summary clearfix").text[:-5],
            "comment": node.find(attrs={"name": "addcomment"}).text,

        }

def save_data(data):
    """
    按照一定的格式写入数据
    :param data:
    :return:
    """
    with open("zhihu_explore.txt", "a", encoding="utf-8") as f:
        f.write("*"*20+"\n")
        f.write(data["title"].strip()+"\n")
        f.write(data["author"].strip()+"\n")
        f.write(data["content"].strip()+"\n")
        f.write(data["vote"].strip()+" 个支持"+"\t"+data["comment"].strip()+"\n")

def main():
    getBlankCount = 0

    for offset in range(0, 1000, 5):
        # 构建query参数
        params = "{\"offset\":%s,\"type\":\"day\"}"%str(offset)
        PARAMS["params"] = params
        print(PARAMS)
        print(URL + parse.urlencode(PARAMS))
        # 请求数据
        html = get_one_html(URL + parse.urlencode(PARAMS))

        # 连续4次请求为空，则退出程序
        if not html:
            getBlankCount += 1

            if getBlankCount == 5:
                return None
            else:
                continue

        getBlankCount = 0

        # 存储数据
        for data in parse_html(html):
            save_data(data)

        time.sleep(1)


if __name__ == "__main__":
    main()
    print("失败链接：",FAILURE_URL)