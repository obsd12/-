import wx
from lxml import etree
from selenium import webdriver
import requests
import sys
import importlib
import pymysql.cursors

importlib.reload(sys)

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='asdfghjkl',
                             db='test',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)


def spider(aid):
    global cid
    # 视频地址
    videoUrl = 'https://www.bilibili.com/video/av' + str(aid)
    # 打开驱动
    browser = webdriver.Chrome()
    # 打开视频
    browser.get(videoUrl)
    # 执行JavaScript语句，拿到网页的cid
    cid = browser.execute_script("return window.cid")

    if cid is None:
        browser.close()
        print("Video not found.")
        return

    # 弹幕URL
    barrageUrl = 'https://comment.bilibili.com/' + cid + '.xml'
    # 弹幕XML
    barrageXml = requests.get(barrageUrl)
    # 解析XML
    root = etree.fromstring(barrageXml.text.encode("utf-8"))
    # 拿到XML中所有的<d>标签，弹幕为<d>标签中的内容
    result = root.xpath("//d")
    # 创建表
    create_table_by_aid(aid)
    # 遍历标签集
    for barrage in result:
        # 插入一条数据到表中
        input_to_table(aid, barrage.text)
    # 关闭浏览器
    browser.close()
    connection.commit()
    return result


def create_table_by_aid(aid):
    with connection.cursor() as cursor:
        table_name = "av" + aid

        sql = "CREATE TABLE " + table_name + "(serial INT(10) AUTO_INCREMENT PRIMARY KEY, comment VARCHAR(100)) " \
                                             "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        cursor.execute(sql)



def input_to_table(aid, comment):
    with connection.cursor() as cursor:
        table_name = "av" + aid
        sql = "INSERT INTO " + table_name + " (comment) VALUES (%s)"
        cursor.execute(sql, comment)


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super(MyFrame, self).__init__(parent, title=title, size=(500, 300))
        self.panel = wx.Panel(self)
        self.tc = wx.TextCtrl(self.panel)
        self.tc2 = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE)
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        v_box = wx.BoxSizer(wx.VERTICAL)

        h_box1 = wx.BoxSizer(wx.HORIZONTAL)

        st1 = wx.StaticText(self.panel, label='av:')
        h_box1.Add(st1, flag=wx.RIGHT, border=8)

        h_box1.Add(self.tc, proportion=1)
        v_box.Add(h_box1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        v_box.Add((-1, 10))

        h_box3 = wx.BoxSizer(wx.HORIZONTAL)
        h_box3.Add(self.tc2, proportion=1, flag=wx.EXPAND)
        v_box.Add(h_box3, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                  border=10)

        v_box.Add((-1, 25))

        h_box5 = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(self.panel, label='Ok', size=(70, 30))
        h_box5.Add(btn1)
        self.Bind(wx.EVT_BUTTON, self.on_clock_ok, btn1)

        btn2 = wx.Button(self.panel, label='Close', size=(70, 30))
        h_box5.Add(btn2, flag=wx.LEFT | wx.BOTTOM, border=5)
        v_box.Add(h_box5, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=10)

        self.panel.SetSizer(v_box)

    def on_clock_ok(self, evt):
        aid = self.tc.GetValue()
        result = spider(aid)
        for i in result:
            self.tc2.AppendText(i.text + "\n")


if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame(None, title="请输入要爬取的av号：")
    frm.Show()
    app.MainLoop()

