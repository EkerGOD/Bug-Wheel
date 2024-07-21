import requests
from lxml import html
import utils

url = "https://www.foodsafety.gov.mo/c/internews/table"
response = requests.get(url)
response.encoding = 'utf-8'
html_content = response.text
tree = html.fromstring(html_content)
"""
提取 table
    提取 tr
        提取 td
            提取 text
            提取 href
"""
new_actions = [
    {
        "name": "table",
        "xpath": '//*[@id="example"]/tbody',
        "type": "branch",
        "next": [
            {
                "name": "row",
                "xpath": "tr",
                "type": "branch",
                "next": [
                    {
                        "name": "time",
                        "xpath": "td[3]",
                        "type": "text",
                        "next": None
                    },
                    {
                        "name": "title",
                        "xpath": "td[5]/a",
                        "type": "text",
                        "next": None
                    },
                    {
                        "name": "url",
                        "xpath": "td[5]/a",
                        "type": "href",
                        "next": None
                    },
                ],
            },
        ],
    },
]
foodmate_actions = [
    {
        "name": "table",
        "xpath": '/html/body/div[11]/div[2]/div/div/ul',
        "type": "branch",
        "next": [
            {
                "name": "li",
                "xpath": "li",
                "type": "branch",
                "next": [
                    {
                        "name": "a",
                        "xpath": "a",
                        "type": "jump",
                        "next": [
                            {
                                "name": "title",
                                "xpath": '//*[@id="title"]',
                                "type": "text",
                                "next": None
                            },
                            {
                                "name": "content",
                                "xpath": '//*[@id="article"]',
                                "type": "all_text",
                                "next": None
                            },
                            {
                                "name": "time",
                                "xpath": '/html/body/div[11]/div[2]/div/div[6]/a',
                                "type": "text",
                                "next": None
                            }
                        ]
                    },
                ],
            },
        ],
    },
]


def extract(etree, actions):
    data = {}
    data_list = []
    is_branch = False
    for action in actions:
        # print(action)

        if action['type'] == 'text':
            if etree.xpath(action['xpath'] + "/text()"):
                data[action['name']] = utils.cleanText(etree.xpath(action['xpath'] + "/text()")[0])
        elif action['type'] == 'all_text':
            if etree.xpath(f"string({action['xpath']})"):
                data[action['name']] = utils.cleanText(etree.xpath(f"string({action['xpath']})"))
        elif action['type'] == 'href':
            if etree.xpath(action['xpath'] + "/@href"):
                data[action['name']] = utils.cleanText(etree.xpath(action['xpath'] + "/@href")[0])
        elif action['type'] == 'jump':
            # is_branch = True
            if etree.xpath(action['xpath'] + "/@href"):
                new_etree = utils.getTree(etree.xpath(action['xpath'] + "/@href")[0])
                data = extract(new_etree, action['next'])
                # data_list.append(extract(new_etree, action['next']))
            # data[action['name']] = data_list
        else:
            is_branch = True
            etree_list = etree.xpath(action['xpath'])
            for new_etree in etree_list:
                # print(html.tostring(new_etree, encoding='utf-8').decode('utf-8'))
                if len(etree_list) != 1:
                    if extract(new_etree, action['next']):
                        data_list.append(extract(new_etree, action['next']))
                else:
                    data_list = extract(new_etree, action['next'])
            # data[action['name']] = data_list

    if is_branch:
        return data_list
    else:
        return data


def test():
    data = extract(utils.getTree('http://news.foodmate.net/yujing/'), foodmate_actions)
    print(data)

    # tree3 = html.tostring(ul[0], encoding='utf-8').decode('utf-8')
    # print(tree3)
