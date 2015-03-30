from time import strftime, gmtime, localtime
from apt.package import unicode

__author__ = 'chuffey'

from bs4 import BeautifulSoup
import lxml
import urllib3
from urllib.parse import *

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
url = 'http://www.dom43.ru/estate_base?object_type=0&operation=0&user_id=&object_id=4&oblast_id=37&town_id=99511&microregion_id=0&street_id=0&admin_region_id=226338&rooms=1&min_land_area=0&max_land_area=0&min_price=0&max_price=0&min_area=0&max_area=0&min_living_area=0&max_living_area=0&min_kitchen_area=0&max_kitchen_area=0&sort=0'
f = open('db/workfile-{0}.html'.format(strftime("%Y-%m-%d_%H:%M:%S", localtime())), 'w')
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
last_page = 80
ob = 0
for i in range(0, last_page):
    print("Индексация {0} из {1}".format(i+1, last_page))
    new_url = url + '&start=' + str(i*54)
    page = urllib3.PoolManager().request('GET', new_url).data
    soup = BeautifulSoup(page.decode("cp1251"))
    tds = soup.find("table", {"class": "boards_card"}).findAll("td")
    geocode = 'http://geocode-maps.yandex.ru/1.x/?'
    for td in tds:

        td_soup = BeautifulSoup(str(td))
        try:
            address = td_soup.findAll('td')[2].text + ' ' + td_soup.findAll('td')[4].text
            code_xml = urllib3.PoolManager().request('GET', geocode + urlencode({'geocode': str(address).replace('Р.Люксембург', 'Розы Люксембург')})).data
            cor = BeautifulSoup(code_xml).find('pos').string.split(' ')
            col = ")"
            if 'индивидуальная' in str(td_soup):
                col = ",{preset: 'islands#redIcon'})"
            ww = "var gO = new ymaps.GeoObject({\n geometry: { type: \"Point\", coordinates: [ " + str(cor[1]) + ", " + str(cor[0]) + "]},\n properties: {\nclusterCaption: '" + str(td_soup.find('th').text) + "', \nballoonContentBody: '" + str(td_soup).replace('\n','').replace('\r', '').replace('src="','src="http://www.dom43.ru/estate_base/') + "'\n}\n}" + \
                  col + '''; gO.events.add('parentchange', function (e) {
            var target = e.get('target');
            if (target.getParent() != null) {
                if (target.properties.get('balloonContentBody').indexOf('индивидуальная') > -1) {
                    target.getParent().options.set('preset', 'islands#redClusterIcons');
                } else {
                    target.getParent().options.set('preset', 'islands#blueClusterIcons');
                }
            }
			}''' + ");myGeoObjects.push(gO);"

            f.write(ww + '\n')
            ob +=1
            print("Добавлено {0} объявление".format(ob), end="\r")
        except:
            continue

print ('Готово!')
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
