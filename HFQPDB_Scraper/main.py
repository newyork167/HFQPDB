import parser as p

TESTING = True

if __name__ == '__main__':
    if TESTING:
        with open("hfqpdb_test.html", 'r') as myfile:
            hfqpdb_html = myfile.read()
    else:
        # TODO: Get from hfqpdb.com
        hfqpdb_html = ""
    p.parse(hfqpdb_html=hfqpdb_html)
