from lxml import etree
import requests
from bs4 import BeautifulSoup

URL = 'https://pcshop.ua/noutbuki-i-aksessuari/noutbuki/'


class XMLItemList:

    def __init__(self, *args):
        self.elements = list(args[0])
        self.soup = BeautifulSoup(features='xml')
        with open('ITvISH_schema.xsd') as schema_file:
            self.schema = etree.XMLSchema(etree.parse(schema_file))

    def toXml(self):
        root = self.soup.new_tag('ItemsList')
        self.soup.append(root)
        for element in self.elements:
            root.append(element.toXml())

        try:
            self.schema.assertValid(etree.fromstring(root.prettify()))
        except etree.XMLSyntaxError:
            raise Exception('Generated xml is not valid')

        return self.soup.prettify()


class XMLItem:

    def __init__(self, img, name, id, price):
        self._img = img
        self._name = name
        self._id = id
        self._price = price
        self.soup = BeautifulSoup(features='xml')

    @property
    def name(self):
        xml_name = self.soup.new_tag('Name')
        xml_name.string = self._name
        return xml_name

    @property
    def id(self):
        xml_id = self.soup.new_tag('Id')
        xml_id.string = self._id
        return xml_id

    @property
    def price(self):
        xml_price = self.soup.new_tag('Price')
        xml_price.string = self._price
        return xml_price

    @property
    def img(self):
        xml_img = self.soup.new_tag('Img')
        xml_img.string = self._img
        return xml_img

    def toXml(self):
        root_xml = self.soup.new_tag('Item')
        root_xml.append(self.name)
        root_xml.append(self.price),
        root_xml.append(self.id)
        root_xml.append(self.img)
        return root_xml


def getHtml(url, params=None):
    r = requests.get(url, params=params)
    return r


def getItemsList(html):
    soup = BeautifulSoup(html, 'html.parser')
    elements = soup.find_all('a', class_='product-thumb')
    nb_elements = []
    for element in elements[0:10]:
        nb_elements.append(XMLItem(
            element.find('img').attrs.get('src'),
            element.find('span', class_='product-thumb__name').get_text(),
            element.find('span', class_='product-thumb__id').get_text(),
            element.find('span', class_='product-thumb__price').get_text()
        ))
    return XMLItemList(nb_elements)


def save_to_xml(nb_items_list, file='elements.xml'):
    with open(file, 'w') as f:
        f.write(nb_items_list.toXml())


def parse():
    html = getHtml(URL)
    if html.status_code == 200:
        nb_items_list = getItemsList(html.text)
        save_to_xml(nb_items_list)
    else:
        print('Error')


if __name__ == '__main__':
    parse()
