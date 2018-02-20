# coding=utf-8
from time import strftime, localtime
from urllib import urlencode

__author__ = 'chuffey'

from bs4 import BeautifulSoup
import urllib3
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
'''page = urllib3.PoolManager().request('GET', url).data
soup = BeautifulSoup(page.decode("cp1251"))
urls =  []
i = 0
for a in soup.find('div', {'class': 'pages'}).findAll('a'):
    if i == 18:
        break
    urls.append(a['href'])
    i += 1

i = 1'''
url = 'https://dom43.ru/realty/search/?operation=sell&price__lte=&floor__gte=&display_type=grid&object_type=flat&address=452a2ddf-88a1-4e35-8d8d-8635493768d4&rooms=&total_floors__gte=&total_floors__lte=&price__gte=&id=&floor__lte=&house_number=&area_total__gte=100&realtor=&area_total__lte='
f = open('db\\workfile-{0}.html'.format(strftime("%Y%m%d_%H%M_%S", localtime())), 'w')
f.write('''
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head> ''' +
        '<title>База от {0}</title>'.format(strftime("%Y-%m-%d_%H:%M:%S", localtime())) +
        '''<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <script src="http://api-maps.yandex.ru/2.1/?load=package.full&lang=ru_RU" type="text/javascript"></script>
        <script src="board.js" type="text/javascript"></script>
        <script src="jquery-1.11.2.min.js" type="text/javascript"></script>
        <link rel="stylesheet" type="text/css" href="styles.css">
        <link rel="stylesheet" type="text/css" href="board.css">
    
        <script type="text/javascript">
            ymaps.ready(init);
            var myMap,
                myGeoObjects;
    
            function getGeoObjects() {
                myGeoObjects = [];
    '''
        )
last_page = 4
ob = 0
for i in range(0, last_page):
    print("Индексация {0} из {1}".format(i + 1, last_page))
    new_url = url + '&page=' + str(i + 1)
    page = urllib3.PoolManager().request('GET', new_url).data
    soup = BeautifulSoup(page)
    items = soup.findAll("div", {"class": "property-card-grid"})
    geocode = 'http://geocode-maps.yandex.ru/1.x/?'
    for item in items:
        item_soup = BeautifulSoup(str(item))
        address = item_soup.find("div", {"class": "property-card-grid__address"}).text.strip()
        code_xml = urllib3.PoolManager().request('GET', geocode + urlencode(
            {'geocode': address.encode('cp1251')})).data
        cor = BeautifulSoup(code_xml).find('pos').string.split(' ')
        cor1 = str(cor[1])
        cor2 = str(cor[0])
        caption = item_soup.find('div', {'class': 'property-card-grid__title'}).text.replace('\n', '') \
            .replace(' ', '').replace('href="', 'href="https://dom43.ru') \
            .encode('utf-8')
        grid_body = item_soup.find('div', {'class': 'property-card-grid__body'}).encode('utf-8') \
            .replace('href="', 'href="https://dom43.ru') \
            .replace('src="', 'src="https://dom43.ru') \
            .replace('\n', '')
        grid_image = item_soup.find('div', {'class': 'property-card-grid__image'}).encode('utf-8') \
            .replace('href="', 'href="https://dom43.ru') \
            .replace('src="', 'src="https://dom43.ru') \
            .replace('\n', '')
        body = grid_image + grid_body
        ww = "var gO = new ymaps.GeoObject({\n geometry: { type: \"Point\", coordinates: [" + cor1 + ", " + cor2 + "]},\n properties: {\nclusterCaption: '" + caption + "', \nballoonContentBody: '" + body + "'\n}\n}" + \
             ')' + '''; gO.events.add('parentchange', function (e) {
            var target = e.get('target');
            if (target.getParent() != null) {
               
            }
			}''' + ");myGeoObjects.push(gO);"

        f.write(ww + '\n')
        ob += 1
        print("Добавлено {0} объявление".format(ob))

f.write('''
return myGeoObjects;

    	}

        function init() {
            myMap = new ymaps.Map("map", {
                center: [58.600309, 49.650066],
                zoom: 12
            });

	        myGeoObjects = getGeoObjects();
            var clusterer = new ymaps.Clusterer({ clusterDisableClickZoom: true });
			clusterer.add(myGeoObjects);
			myMap.geoObjects.add(clusterer);
        }
    </script>

</head>

<body>
    <div id="map" style="width: 1800px; height: 900px"></div>
</body>

</html>
''')
f.close()
print ('Готово!')
