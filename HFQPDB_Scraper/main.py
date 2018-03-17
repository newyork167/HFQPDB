import parser as p
import Configuration
import urllib
import os

TESTING = Configuration.getboolean('testing', 'testing')

if __name__ == '__main__':
    # If we are testing and don't have a copy or we are not testing grab the latest copy
    if not TESTING or not os.path.exists("hfqpdb.html"):
        urllib.urlretrieve('http://www.hfqpdb.com', filename="hfqpdb.html")
        filename = "hfqpdb.html"
    else:
        filename = "hfqpdb_test.html"

    # Open the file and parse it
    with open(filename, 'r') as myfile:
        hfqpdb_html = myfile.read()
    p.parse(hfqpdb_html=hfqpdb_html)
