import os
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import arxiv
import pytz
from tqdm import tqdm

password = os.getenv('EMAIL_PASSWORD')
now = datetime.now(pytz.utc)
yesterday = now - timedelta(days = 1.1)


def main():
    search = arxiv.Search(
        query = "cat:cs.CL OR cat:cs.AI OR cat:cs.LG OR cat:cs.CR OR cat:cs.SE",
        max_results = 1000,
        sort_by = arxiv.SortCriterion.LastUpdatedDate,
        sort_order = arxiv.SortOrder.Descending
    )
    search_results = arxiv.Client().results(search)
    filtered_papers = []
    for i in range(10):
        try:
            filtered_papers = filter_papers(search_results)
        except Exception as _:
            pass
        if len(filtered_papers) != 0:
            break
        time.sleep(60)
    email_content = "Here are the filtered papers:\n\n"
    for paper in filtered_papers:
        email_content += f"Title: {paper['title']}\n"
        email_content += f"Abstract: {paper['abstract']}\n"
        email_content += f"URL: {paper['url']}\n\n"
    # 配置邮件信息
    sender_email = "rucnyz@gmail.com"
    receiver_email = "rucnyz@gmail.com"
    subject = "Filtered ArXiv Papers"

    # 创建MIMEText对象
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(email_content, 'plain'))

    # 发送邮件
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail的SMTP服务器和端口
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def filter_papers(search_results):
    filter_times_span = None
    filtered_papers = []
    for result in tqdm(search_results, total = 1000):
        if filter_times_span is None:
            filter_times_max = result.updated
            filter_times_span = filter_times_max - timedelta(days = 1)
        if result.updated < filter_times_span:
            break
        title = result.title.lower()
        abstract = result.summary.lower()
        # code generation
        if (("code " in abstract or "coding" in abstract)
                and ("code" in title or "coding" in title)):
            # avoid false positive
            if "encode" not in title or "code" in title.replace("encode", ""):
                filtered_papers.append({
                    "title": result.title,
                    "abstract": result.summary,
                    "url": result.entry_id
                })
        # long context
        elif (("long context" in abstract or "long-context" in abstract)
              and ("context" in title or "scaling" in title or "scale" in title)):
            filtered_papers.append({
                "title": result.title,
                "abstract": result.summary,
                "url": result.entry_id
            })
        # privacy leakage
        elif "privacy leakage" in abstract and ("privacy" in title or "leakage" in title or "leak" in title):
            filtered_papers.append({
                "title": result.title,
                "abstract": result.summary,
                "url": result.entry_id
            })
        # agent
        elif (("poison" in abstract or "attack" in abstract or "red teaming" in abstract or "red-teaming" in abstract)
              and "agent" in title):
            filtered_papers.append({
                "title": result.title,
                "abstract": result.summary,
                "url": result.entry_id
            })
    return filtered_papers


if __name__ == '__main__':
    import time

    start_time = time.time()
    main()
    print("summary time:", time.time() - start_time)
