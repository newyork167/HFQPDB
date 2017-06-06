import io
from io import BytesIO

import sqlalchemy
from bs4 import BeautifulSoup
import pandas as pd
import pandas.io.sql as pd_sql
import urllib
import requests
from sqlalchemy import create_engine, MetaData
from sqlalchemy.sql import select
from PIL import Image

engine = sqlalchemy.create_engine('sqlite:///hfqpdb.sqlite')

lot_no_split = 'Lot No.'

COUPON_LINK = 0
BEST_COUPON_LINK = 1
CURRENT_PRODUCT_LINK = 2

PRODUCT_COUPON = 0
FREEBIE_COUPON = 1


class Coupon:
    href = ""
    title = ""
    lot_nos = []
    valid_from = ""
    valid_to = ""
    price = ""
    image_url = ""

    base_image_url = "www.hfqpdb.com"

    def __init__(self, href="", title="", lot_nos=[], valid_from="", valid_to="", price="", image_url=""):
        self.href = href
        self.title = title
        self.lot_nos = lot_nos
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.price = price
        self.image_url = image_url

    def to_string(self):
        return "{title} - {lot_nos}\n\t{valid_from} - {valid_to}\n".format(title=self.title, lot_nos="/".join(self.lot_nos), valid_from=self.valid_from, valid_to=self.valid_to)

    def get_image_url(self):
        return "http://{base_url}{image_url}".format(base_url=self.base_image_url, image_url=self.image_url)

    def to_dict(self):
        return {'href': self.href, 'title': self.title, 'lot_nos': "/".join(self.lot_nos), 'valid_from': self.valid_from,
                'valid_to': self.valid_to, 'price': self.price, 'image_url': self.get_image_url()}


def test():
    import pandas as pd
    import base64, StringIO, sqlite3

    # Read sqlite query results into a pandas DataFrame
    con = sqlite3.connect("hfqpdb.sqlite")
    df = pd.read_sql_query("SELECT * from freebies", con)

    # verify that result of SQL query is stored in the dataframe
    imgstring = df['image'].iloc[0]
    imgdata = base64.b64decode(imgstring)
    tempBuff = StringIO.StringIO()
    tempBuff.write(imgdata)
    tempBuff.seek(0)
    img = Image.open(tempBuff)
    img.show()

    con.close()


def download_images(row):
    print(row['image_url'])
    response = requests.get(row['image_url'])
    image = Image.open(BytesIO(response.content))

    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    imagebytes = stream.getvalue()
    try:
        return imagebytes.encode('base64')
    except Exception as ex:
        print(ex)
        return ""


def parse_coupons(product_coupons, coupon_type=PRODUCT_COUPON):
    coupon_list = []
    for tag in product_coupons.findAll('p'):
        # Example links
        # <a href="./coupons/1701_ITEM_wireless_surveillance_system_4_channel_with_2_cameras_1491322293.3622.JPG" title="Harbor Freight Coupon wireless surveillance system 4 channel with 2 cameras Lot No. 62368 Valid Thru: 5/31/17 - $199.99">
        #   <img alt="Harbor Freight Coupon wireless surveillance system 4 channel with 2 cameras Lot No. 62368 Valid Thru: 5/31/17 - $199.99" class="thumb" src="/coupons/thumbs/tn_1701_ITEM_wireless_surveillance_system_4_channel_with_2_cameras_1491322293.3622.JPG"/>
        #   wireless surveillance system 4 channel with 2 cameras Lot No. 62368 Valid Thru: 5/31/17 - $199.99
        # </a>
        # <a href="/best_coupon/wireless+surveillance+system+4+channel+with+2+cameras">view all (1)</a>
        # <a href="http://www.harborfreight.com/4-channel-wireless-surveillance-system-with-2-cameras-62368.html" target="_blank">current price ($259.99)</a>
        link_count = 0
        for link in tag.findAll('a'):
            coupon = Coupon()
            if link_count == COUPON_LINK:
                try:
                    print(link)
                    coupon.href = link['href']
                    coupon.title = link['title'].replace("Harbor Freight Coupon", '')
                    coupon.image_url = link.find('img')['src']
                    coupon.image_url = link['href'][1:]
                    valid_to = ""
                    valid_from = ""
                    price = coupon.title.split('-')[-1]

                    if lot_no_split in coupon.title:
                        if 'valid thru' in coupon.title.lower():
                            valid_to = coupon.title.split('Valid Thru:')[-1].split('-')[0].strip()
                            lot_nos = coupon.title.split(lot_no_split)[-1].split('Valid Thru:')[0].split('/')
                        elif 'valid' in coupon.title.lower():
                            valid_from, valid_to = coupon.title.split('Valid:')[-1].split('-')[0].split()
                            lot_nos = coupon.title.split(lot_no_split)[-1].split('Valid')[0].split('/')
                        else:
                            valid_to = coupon.title.split('EXPIRES:')[-1].split('-')[0].strip()
                            lot_nos = coupon.title.split(lot_no_split)[-1].split('EXPIRES')[0].split('/')
                        lot_nos = [x.strip() for x in lot_nos]
                        coupon.lot_nos = lot_nos

                    coupon.price = price
                    coupon.valid_to = valid_to
                    coupon.valid_from = valid_from
                    if coupon_type == PRODUCT_COUPON:
                        coupon.title = coupon.title.split(lot_no_split)[0].title()
                    elif coupon_type == FREEBIE_COUPON:
                        coupon.title = coupon.title.split(lot_no_split)[0].split("Harbor Freight Free Coupon")[1].title()
                    coupon_list.append(coupon)
                except Exception as ex:
                    print("Could not add coupon: {ex}".format(ex=ex))
            elif link_count == BEST_COUPON_LINK:
                pass
            elif link_count == CURRENT_PRODUCT_LINK:
                pass
            else:
                pass
            link_count += 1
        print("\n")
    print("Added {num_coupons} coupons to database".format(num_coupons=len(coupon_list)))
    return coupon_list


def parse(hfqpdb_html):
    soup = BeautifulSoup(hfqpdb_html, "lxml")
    product_coupons = soup.find("div", {"id": "products"})
    pc_list = parse_coupons(product_coupons=product_coupons, coupon_type=PRODUCT_COUPON)
    hfqpdb_df = pd.DataFrame([x.to_dict() for x in pc_list])
    hfqpdb_df['image'] = hfqpdb_df.apply(lambda row: download_images(row=row), axis=1)
    hfqpdb_df.to_sql('products', engine, if_exists='replace')

    free_coupons = soup.find("div", {"id": "free"})
    fc_list = parse_coupons(product_coupons=free_coupons, coupon_type=FREEBIE_COUPON)
    hfqpdb_df = pd.DataFrame([x.to_dict() for x in fc_list])
    hfqpdb_df['image'] = hfqpdb_df.apply(lambda row: download_images(row=row), axis=1)

    hfqpdb_df.to_sql('freebies', engine, if_exists='replace')

    # test()
