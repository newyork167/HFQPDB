import parser as p
import Configuration
import urllib

TESTING = Configuration.getboolean('testing', 'testing')

if __name__ == '__main__':
    if not TESTING:
        urllib.urlretrieve('http://www.hfqpdb.com', filename="hfqpdb.html")
        filename = "hfqpdb.html"
    else:
        filename = "hfqpdb_test.html"
    with open(filename, 'r') as myfile:
        hfqpdb_html = myfile.read()
    p.parse(hfqpdb_html=hfqpdb_html)
