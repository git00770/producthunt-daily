import feedparser
import time
import smtplib
from email.mime.text import MIMEText
import re
import os

def extract_link_and_clean_summary(raw_html):
    link_pattern = re.compile(r'<a href="(.*?)">Link</a>')
    links = link_pattern.findall(raw_html)
    product_link = links[0] if links else "无链接"
    
    clean_pattern = re.compile(r'<.*?>')
    clean_summary = re.sub(clean_pattern, '', raw_html)
    clean_summary = re.sub(r'\s+', ' ', clean_summary).strip()
    
    return clean_summary, product_link

def send_email(content):
    sender = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('EMAIL_AUTH_CODE')
    receiver = os.environ.get('RECEIVER_EMAIL')

    if not all([sender, password, receiver]):
        print("请先配置 Secrets")
        return

    msg = MIMEText(content, 'html', 'utf-8')
    msg['From'] = sender
    msg['To'] = receiver
    msg['Subject'] = f"Product Hunt 今日产品榜单 {time.strftime('%Y-%m-%d')}"

    try:
        server = smtplib.SMTP_SSL("smtp.qq.com", 465)
        server.login(sender, password)
        server.sendmail(sender, [receiver], msg.as_string())
        server.quit()
        print("邮件发送成功！")
    except Exception as e:
        print("发送失败：", e)

def get_today_product_hunt():
    url = "https://www.producthunt.com/feed"
    print("正在抓取 Product Hunt...")
    feed = feedparser.parse(url)

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
        clean_summary, product_link = extract_link_and_clean_summary(raw_html)
        
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

if __name__ == "__main__":
    get_today_product_hunt()
