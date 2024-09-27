import requests
from lxml import etree
import csv
import logging
import json


class Main:
    name="merinfo"
    base_url = "https://www.merinfo.se"
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "cookie": "testcookie=1; _ga=GA1.1.1671279360.1727362372; usprivacy=1N--; IABGPP_HDR_GppString=DBABLA~BVQqAAAACkA.QA; XSRF-TOKEN=eyJpdiI6InRtdWRhc3ZkbUhFL3MwYVREZTNsTEE9PSIsInZhbHVlIjoiRU5aOUlhdU1RMjFrd3BGR2pkcG5EdHlaNE5nRWJNbjEwQTRrVXVlUWl4Mjc2RVhkbWVrSjBrUUlEUmltaXF4aVFlaVRPZndEWUlON08raFZHeklwTUNLZCt4aDFwVGtBUTZ1b3R2MkhGVTFRbWNjaWk1RXRydFJNWHY5d2hMQ0UiLCJtYWMiOiJiZmI4ZmEwODBiNGQ0ZDdhZTQyNWM4MzVlZDU5M2FkODFhOWFiODRiMzNiZTMzZTEyYzNmYTk5YjU0ZmVkNTljIiwidGFnIjoiIn0%3D; merinfose_session=eyJpdiI6Im5rMmphM2c1TzlnNGZJUjUvN1c1UWc9PSIsInZhbHVlIjoieFppT0pLYVYvb0FLckh6WUVPdElPUFFiQUlyZEs5ZjFJekhJMUVlMkIwNFUyVm9HcURrNlJueU1IYUs3K2YxTFk4ZXNQK2JoTE1JeDRVelBPdnVJeGxQVG53b2RHcHRSYzErMkpldkZ4NzFYYk0zMEhvd3dTYW11cGtpSVp2WkYiLCJtYWMiOiI2ZjI0ZDA1ZGE3ZTRhMjMyMjAyNGFlNjQ0ZWU2Mjc2ZDk1NTA2ZThiZjdlMjZhMjFhZGIxOGJiYzgxODU1MDdmIiwidGFnIjoiIn0%3D; cf_clearance=wRThatp2iNcJ_LxSlzfibbFGSXKd9IsLIqfnBmAWOgA-1727450385-1.2.1.1-HuPd3uuA3iZwwy7IL1FK6t2Z5Rr4muC4vBsNL3yes8yx.ivf8AHzE5jXzcfHYJ2SOgnMtmOOhxsoiPr9hW_hJcnpf2wkvb8NLUYZNpwVOJn6olHx2at56Qw95Pxv1x.hJNU6rrqvSUUG6dCHSvm1v0ghxtTgd3fG7TwSbUeiwrqVoTY.O7aAcJBW0N.TVKpnPP_0.YKCOKQE928x84l3ljYeOwKwnXwppOjVOszJ.VdFSFKfkYn2diCfgstsp66Lh7m7DFOIRFkrBDx96gNnuPW2xmF0Ew11D2ohA3Q5jG9ml_U7IqM.KxPIPa1oXYqDslqlF9gBfV2.LltkgrFnl6ZPhaladZRr7URHCVYbDPCjBMa3iiHvaE9L6CqX0GuJ; _ga_1SCPZ1P8YF=GS1.1.1727450387.4.0.1727450387.60.0.0",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    }
    csv_headers = [
        "S.L no",
        "URL",
        "Phone number"
    ]
    use_log = False

    def __init__(self):
        self.session = requests.Session()
        self.writer = self.get_writer()
        if self.use_log:
            self.config_log()

    def run(self):
        try:
            urls = self.load_csv()
            for index, url in enumerate(urls):
                self.parse_person(url, index)
        except Exception as e:
            self.print_out(f"Error in run: {e}")

    def parse_person(self, url, index):
        response = self.session.get(url, headers=self.headers)
        tree = etree.HTML(response.text)
        phone_numbers = []
        try:
            data = json.loads(self.validate(tree.xpath('//phone-number-table/@*')[0]))
            phone_numbers = [item.get("display") for item in data]
        except:
            pass
        data = {
            "S.L no": index+4059,
            "URL": url,
            "Phone number": " | ".join(phone_numbers),
        }
        print(f"{data}")
        self.write(data)

    def get_writer(self):
        output_file = open(
            f'{self.name}.csv',
            mode='w',
            newline='',
            encoding="utf-8-sig"
        )
        output_writer = csv.writer(
            output_file,
            delimiter=',',
            quotechar='"',
            quoting=csv.QUOTE_ALL
        )
        output_writer.writerow(self.csv_headers)
        return output_writer
    
    def write(self, values):
        row = []
        for header in self.csv_headers:
            row.append(values.get(header, ''))
        self.writer.writerow(row)

    def validate(self, item):
        if item == None:
            item = ''
        if type(item) == int or type(item) == float:
            item = str(item)
        if type(item) == list:
            item = ' '.join(item)
        return item.strip()

    def eliminate_space(self, items):
        rets = []
        for item in items:
            item = self.validate(item)
            if item != '':
                rets.append(item)
        return rets

    def config_log(self):
        logging.basicConfig(
            filename=f"history.log",
            format='%(asctime)s %(levelname)-s %(message)s',
            level=logging.INFO,
            datefmt='%m/%d/%Y, %H:%M:%S')

    def print_out(self, value):
        if self.use_log:
            logging.info(value)
        else:
            print(value)

    def load_csv(self):
        data = []
        with open('input.csv', mode='r', newline='', encoding="utf-8-sig") as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                data.append(row[0])
        return data
    
    def convert(self):
        data = []
        with open('merinfo.csv', mode='r', newline='', encoding='utf-8') as file:
            csv_reader = csv.reader(file, delimiter='	')
            for row in csv_reader:
                data.append(row)

        with open('output_final.csv', mode='w', newline='', encoding='utf-8') as file:
            csv_writer = csv.writer(file, delimiter=',')
            csv_writer.writerows(data)

if __name__ == '__main__':
    main = Main()
    main.run()
