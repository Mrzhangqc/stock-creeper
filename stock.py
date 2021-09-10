import requests
requests.packages.urllib3.disable_warnings()
import sys
# from bs4 import BeautifulSoup
from decimal import Decimal
# import json
# import lxml
import threading
import time

import smtplib
from email.mime.text import MIMEText
from email.header import Header
# 第三方 SMTP 服务
mail_host="smtp.163.com"  #设置服务器
mail_user="xxxx"    #用户名
mail_pass="xx"   #口令
sender=mail_user # 发送邮件
receivers=['xx@qq.com'] # 接收邮件

buy = 0.00
up = 0.79
down = 0.59
timer = {}

def notify(curr = 0.00):
  global buy
  buy = float(Decimal(buy).quantize(Decimal('0.00')))
  curr = float(Decimal(curr).quantize(Decimal('0.00')))
  space = float(Decimal(curr - buy).quantize(Decimal('0.00')))

  print('')
  curr_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
  print('\033[7;30;46m----实时USoil: ' + str(curr) + '-----' + 'b:' + str(buy) + '--' + 'space:' + str(space) + '-----', curr_time, '\033[0m')

  messageInfo = ''
  if curr >= buy + up:
    timer.cancel()
    print('\033[1;5;31m**买**' + str(buy) + '-' + str(curr),'*****止盈*****\033[0m')
    messageInfo= '通知：' + curr_time + ' US oil ' + str(buy) + '-' + str(curr) + ' 已止盈'
  if curr <= buy - down:
    timer.cancel()
    print('\033[1;5;31m**卖**' + str(buy) + '-' + str(curr),'*****止盈*****\033[0m')
    messageInfo= '通知：' + curr_time + ' US oil ' + str(buy) + '-' + str(curr) + ' 已止损'

  if messageInfo:
    title = '【US oil】行权通知'
    content = '''
      <html>
        <head></head>
        <body>
          <b>%s</b>
        </body>
      </html>
    '''%(messageInfo)
    
    # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
    message = MIMEText(content, 'html', 'utf-8')
    message['From'] = Header(mail_user)   # 发送者
    message['To'] =  Header(receivers[0])    # 接收者
    message['Subject'] = Header(title, 'utf-8')
    
    try:
      smtpObj = smtplib.SMTP() 
      smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
      smtpObj.login(mail_user,mail_pass)  
      smtpObj.sendmail(sender, receivers, message.as_string())
      smtpObj.quit()
      print("邮件发送成功")
    except smtplib.SMTPException as e:
      print("Error: 无法发送邮件", e)
  pass

def pickPrice(str = ''):
  price = str.split(';')[0]
  s = price.find('"')+1
  e = price.find(',')
  result = price[s:e]
  notify(result)

def getUSoilPrice():
  global timer
  timer = threading.Timer(5, getUSoilPrice)
  timer.start()

  url = "https://info.usd-cny.com/data/oil.js"
  # 模拟浏览器访问
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
  }
  try:
    res = requests.get(url, headers=headers, timeout=10, verify=False)
  except requests.exceptions.ProxyError:
    print("代理出错,正在重试...")
    time.sleep(3)
  except requests.exceptions.ConnectTimeout:
    print("请求超时, 正在重试...")
    time.sleep(3)
  except requests.exceptions.ConnectionError as e:
    print('---请求异常--- ' + e)
  else:
    if res.status_code == 200:
      res.encoding = 'gbk'
      result_str = res.text
      pickPrice(result_str)
    else:
      print('爬取数据失败')
  pass

def startTask():
  print('------买入价格:'+ buy + ', 任务开启!-------')
  getUSoilPrice()
  pass

# 程序入口
if __name__ == "__main__":
  #买入价格
  buy = sys.argv[1]
  startTask()

