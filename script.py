from bs4 import BeautifulSoup
import datetime
from random import randint
from random import shuffle
import requests
from time import sleep

base_url = 'https://www.michaeleastick.com'

def get_html(url):
    
    html_content = ''
    try:
        page = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        html_content = BeautifulSoup(page.content, "html.parser")
    except: 
        pass
    
    return html_content

def get_value(html, info_name):
    
    info_value = None
       
    try:
        info_items = html.select('.LabelText')
        for info_item in info_items:
            info_text = info_item.get_text().strip()
            if info_name in info_text:
                info_value = info_text.replace(info_name, '').strip()
                break
    except:
        pass
    
    return info_value 

def get_details(url, base_category):
    
    stamp = {}
    
    try:
        html = get_html(url)
    except:
        return stamp
    
    try:
        title = html.select('.DetailTitle')[0].get_text().strip()
        stamp['title'] = title
    except:
        stamp['title'] = None      
    
    try:
        raw_text = html.select('.ProductDetails')[0].get_text().strip()
        raw_text = raw_text.replace('\n', ' ').strip()
        raw_text = raw_text.replace(u'\xa0', u' ').strip()
        stamp['raw_text'] = raw_text
    except:
        stamp['raw_text'] = None
        
    try:
        sku = html.select('.invNumberDetail')[0].get_text().strip()
        sku = sku.replace('Item #:', '').strip()
        stamp['sku'] = sku
    except:
        stamp['sku'] = None        
    
    try:
        price = ''
        for price_item in html.select('td p strong'):
            price_heading = price_item.get_text().strip()
            if price_heading == 'Outside Australia':
                price = price_item.find_next('em').get_text().strip()
                price = price.replace('A$', '').strip()
        stamp['price'] = price
    except:
        stamp['price'] = None  
        
    stamp['condition'] = get_value(html, 'Condition') 
    stamp['grade'] = get_value(html, 'Grade')
    
    stamp['base_category'] = base_category
    
    try:
        category = html.select('.BreadCrumb a')[1].get_text().strip()
        stamp['category'] = category
    except:
        stamp['category'] = None  
       
    try:
        subcategory = html.select('.BreadCrumb a')[2].get_text().strip()
        stamp['subcategory'] = subcategory
    except:
        stamp['subcategory'] = None     
        
       

    stamp['currency'] = 'AUD'
    
    # image_urls should be a list
    images = []                    
    try:
        image_items = html.select('form tr td img')
        for image_item in image_items:
            img_src = image_item.get('src')
            if 'Ext.JPG' in img_src:
                img = base_url + '/' + img_src
                if img not in images:
                    images.append(img)
    except:
        pass
    
    stamp['image_urls'] = images 
        
    # scrape date in format YYYY-MM-DD
    scrape_date = datetime.date.today().strftime('%Y-%m-%d')
    stamp['scrape_date'] = scrape_date
    
    stamp['url'] = url
    
    print(stamp)
    print('+++++++++++++')
    sleep(randint(25, 65))
           
    return stamp

def get_page_items(url):
    
    items = []
    next_url = ''

    try:
        html = get_html(url)
    except:
        return items, next_url

    try:
        for item in html.select('td a.head2'):
            item_link = base_url + item.get('href')
            if item_link not in items:
                items.append(item_link)
    except:
        pass
    
    try:
        next_items = html.select('a.NavBar')
        for next_item in next_items:
            next_text = next_item.get_text().strip()
            next_href = next_item.get('href')
            if((next_text == 'Next >>') and (next_href != 'javascript:void(0)')):
                next_url = base_url + next_href
    except:
        pass   
    
    shuffle(items)
    
    return items, next_url

def get_categories(url, element_class):
   
    items = []

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('a.' + element_class):
            item_link = base_url  + '/' + item.get('href')
            if item_link not in items: 
                items.append(item_link)
    except: 
        pass
    
    shuffle(items)
    
    return items

def get_main_categories():
   
    url = 'https://www.michaeleastick.com/rhome1d.asp'
   
    items = {}

    try:
        html = get_html(url)
    except:
        return items

    try:
        for item in html.select('#suckertree1 > li > a'):
            item_link = base_url  + '/' + item.get('href')
            item_text = item.get_text().strip()
            if item_link not in items: 
                items[item_text] = item_link
    except: 
        pass
    
    return items

def get_page_items_details(page_url, base_category):
    while(page_url):
        page_items, page_url = get_page_items(page_url)
        for page_item in page_items:
            stamp = get_details(page_item, base_category) 
                    
main_categories = get_main_categories()
for key in main_categories:
    print(key + ': ' + main_categories[key])   

selection = input('Choose category: ')

selected_main_category = main_categories[selection]

categories = get_categories(selected_main_category, 'HeadCat')   
for category in categories:
    subcategories = get_categories(category, 'HeadSub') 
    if len(subcategories):
        for subcategory in subcategories:
            page_url = subcategory
            get_page_items_details(page_url, selection)
    else:
        get_page_items_details(category, selection)