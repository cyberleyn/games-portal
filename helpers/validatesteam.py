import io
import xml

import requests
import xml.dom.minidom as xml_md


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/37.0.2062.120 Safari/537.36'}


def validate_link(link):
    try:
        link = link + "?xml=1"
        request_profile = requests.get(url=link, headers=HEADERS)
        # print(request_profile.content.decode("utf-8"))
        doc = xml_md.parse(io.StringIO(request_profile.content.decode("utf-8")))
        steam_id64 = doc.getElementsByTagName('steamID64')[0].childNodes[0].nodeValue
        print(steam_id64)
        return True
    except xml.parsers.expat.ExpatError:
        return False


def get_steamid64(link):
    if validate_link(link):
        link = link + "?xml=1"
        request_profile = requests.get(url=link, headers=HEADERS)
        doc = xml_md.parse(io.StringIO(request_profile.content.decode("utf-8")))
        steam_id64 = doc.getElementsByTagName('steamID64')[0].childNodes[0].nodeValue
        return steam_id64
    else:
        print("False")
        return None


