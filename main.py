import feedparser
import time
import smtplib
from email.mime.text import MIMEText
import re
import os

def extract_link_and_clean_summary(raw_html):
    try:
        link_pattern = re.compile(r'<a href="(.*?)">Link</a>')
        links = link_pattern.findall(raw_html)
        product_link = links[0] if links else "无链接"
        
        clean_pattern = re.compile(r'<.*?>')
        clean_summary = re.sub(clean_pattern, '', raw_html)
        clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()
        
        return clean_summary, product_link
    except Exception as e:
        print("解析链接和摘要时出错:", e)
        return "解析失败", "无链接"

def send_email(content):
    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('EMAIL_AUTH_CODE')
    receiver = os.environ.get('RECEIVER_EMAIL')

    print("发件人:", sender)
    print("收件人:", receiver)

    if not all([sender, password, receiver]):
        print("错误：请先配置 Secrets")
        return

    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = f"Product Hunt 今日产品榜单 {time.strftime('%Y-%m-%d')}"

    try:
        print("正在连接 QQ 邮箱服务器...")
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        print("服务器连接成功")
        
        server.login(sender, password)
        print("邮箱登录成功")
        
        server.sendmail(sender, [receiver], msg.as_string())
        print("邮件发送成功！")
        server.quit()
    except Exception as e:
        print("发送邮件失败:", e)

def get_today_product_hunt():
    try:
        url = "https://www.producthunt.com/feed"
        print("正在抓取 Product Hunt...")
        feed = feedparser.parse(url)

        if feed.bozo != 0:
            print("抓取 RSS 失败:", feed.bozo_exception)
            return

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h3>Product Hunt 今日热门产品</h3>
            <p>更新时间：{time.ctime()}</p>
            <table border="1" style="border-collapse: collapse; width: 100%; font-size: 14px;">
              <tr style="background-color: #e6f7ff;">
                <th style="padding: 6px; text-align: center;">#</th>
                <th style="padding: 6px; text-align: left;">产品名称</th>
                <th style="padding: 6px; text-align: left;">产品介绍</th>
                <th style="padding: 6px; text-align: center;">产品链接</th>
              </tr>
        """

        for i, entry in enumerate(feed.entries[:10], 1):
            title = entry.get("title", "无标题")
            raw_summary = entry.get("summary", "无描述")
            clean_summary, product_link = extract_link_and_clean_summary(raw_summary)
            
            html += f"""
            <tr>
              <td style="padding: 6px; text-align: center;">{i}</td>
              <td style="padding: 6px; font-weight: bold;">{title}</td>
              <td style="padding: 6px;">{clean_summary}</td>
              <td style="padding: 6px; text-align: center;"><a href="{product_link}" target="_blank">点击访问</a></td>
            </tr>
            """

        html += """
            </table>
        </body>
        </html>
        """
        send_email(html)
        print("抓取完成，邮件已发送！")
    except Exception as e:
        print("抓取和发送流程失败:", e)

if __name__ == "__main__":
    get_today_product_hunt()
