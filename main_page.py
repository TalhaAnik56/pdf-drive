import re
import csv
import requests
import sys
from html import unescape

def get_page_content(url):
    try:
        response=requests.get(url)
    except requests.exceptions.RequestException as e:
        sys.exit("The server is not responding")

    content=response.text
    return content


def get_book_list(content):
    res=book_pattern.findall(content)
    return res

def get_next_page(content):
    result=re.findall(r'<div class="Zebra_Pagination">.*?</div>',content,re.M|re.DOTALL)
    res=next_page_pat.findall(result[0])

    if len(res)==0:
        return None

    res=res[0]
    res=host_name+res
    return res    

def scrape_book_info(book_url,book_name,category_name):
    content=get_page_content(book_url)
    res=download_link.findall(content)
    if len(res)==0:
        download_url=None
    else:
        download_url=res[0]
        download_url=host_name+download_url

    res=details_pat.findall(content)
    if len(res)==0:
        pages=None
        year=None
        size=None
        downloads=None
        language=None
    else:
        details=res[0]
        pages,year,size,downloads,language=details

    csv_writer.writerow([book_name,category_name,pages,year,size,downloads,language,download_url])        



def crawl_category(category_url,category_name):
    while True:
        print(category_url)
        content=get_page_content(category_url)
        book_list=get_book_list(content)
        for book in book_list:
            book_url,book_name=book
            book_url=host_name+book_url
            book_name=unescape(book_name)
            scrape_book_info(book_url,book_name,category_name)
        
        next_page=get_next_page(content)
        if next_page==None:
            break
        category_url=next_page
    

def get_category_list(content):
    category_content=re.findall(r'<div class="categories-list">\s*<ul>.*?</ul>\s*</div>',content,re.M|re.DOTALL)
    category_list=category_pat.findall(category_content[0])
    return category_list

def crawl_website():
    url="https://www.pdfdrive.com/"
    content=get_page_content(url)
    category_list=get_category_list(content)
    for category in category_list:
        category_url,category_name=category
        category_url=host_name+category_url
        category_name=unescape(category_name)
        crawl_category(category_url,category_name)
        
        


#Main function starts here
if __name__=="__main__":
    host_name="https://www.pdfdrive.com"
    category_pat=re.compile(r'<a href="(/category/.*?)">.*?<p>(.*?)</p>',re.M|re.DOTALL)
    book_pattern=re.compile(r'<div class="file-right">\s*<a href="(/.*?)".*?<h2>(.*?)</h2>',re.M|re.DOTALL)
    next_page_pat=re.compile(r'<a href="/category/.*?" class="current">.*<a href="(/category/.*?)" class="navigation next".*?>Next</a>',re.M|re.DOTALL)

    download_link=re.compile(r'<div class="ebook-left">\s*<a href="(.*?)"',re.M|re.DOTALL)
    details_pat=re.compile(r'<div class="ebook-file-info">\s*<span class="info-green">\s*(\d+).*?</span>.*?<span class="info-green">\s*(\d+)\s*</span>.*?<span class="info-green">(.*?)</span>.*?<span class="info-green hidemobile">\s*([\d,]+).*?<span class="info-green">(.*?)</span>',re.M|re.DOTALL)


    with open("pdfDrive.csv","w",newline="",encoding="UTF-8")as f:
        csv_writer=csv.writer(f)
        csv_writer.writerow(["Book","Category","Pages","Year","Size","Downloads","Language","Download Link"])
        crawl_website()
        print("Crawling Done")

