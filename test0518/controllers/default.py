import os
import sys
import urllib2
import httplib
import time
conn = httplib.HTTPConnection("192.168.0.16")
data =''
co2 = ''
def getWebpage(url, referer=''):
    debug = 0
    if debug:
        return file(url.split('/')[-1], 'rt').read()
    else:
        opener = urllib2.build_opener()
        opener.addheaders = [
            ('User-Agent', 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)'),
            ('Referer', referer),
        ]
        return opener.open(url).read()

def getDataPage():
    return getWebpage('http://www.airkorea.or.kr/index')
    #url ê°€?¸ì˜¤ê¸?
    
def normailize(s):
    return s.replace('<td>','').replace('</td>','').replace(' ','')
    #ë¶ˆí•„?”í•œ ì½”ë“œ ?œê±°
def printUsing():
    print sys.argv[0], '<output file name>'

def getDatetime(buffers):
    return buffers.split('<p class="now_time">')[1].split('<strong>')[1].split('</strong>')[0]
    #url ?ŒìŠ¤?ì„œ ? ì§œ ë¶€ë¶?ì¶”ì¶œ
def getDatablocks(buffers):
    a = buffers.split('<tbody id="mt_mmc2_10007">')[1]
    b = a.split('</tbody>')[0].replace('<tr>','').replace('</tr>','').replace('</td>','')
    r = ''
    for line in b.split('<td>'):
       if len(line) < 30:
           line = line.strip()
           r = r+line+' '
       else:
           line = line.strip()
           r = r+line+'\n'
    return r.split('\n')[1:-1]
    #url ?ŒìŠ¤?ì„œ ?°ì´??ë¶€ë¶?ì¶”ì¶œ


def hue2on():
    global data
    conn.request("PUT", "/api/newdeveloper/lights/2/state", '{"on":true}')
    responses = conn.getresponse()
    data = responses.read()
    time.sleep(2)
    return redirect(URL('index'))

def hue2off():
    global data
    conn.request("PUT", "/api/newdeveloper/lights/2/state", '{"on":false}')
    responses = conn.getresponse()
    data = responses.read()
    time.sleep(2)
    return redirect(URL('index'))

def hue2change():
    global data
    conn.request("PUT", "/api/newdeveloper/lights/2/state", '{"on":true, "sat":255, "bri":255, "hue":10000}')
    responses = conn.getresponse()
    data = responses.read()
    time.sleep(2)
    #return redirect(URL('index'))
    
def co2get():
    infile = open(os.path.join(request.folder, 'static', 'log_tos.log'))
    co2=infile.readlines()[-1]
    infile.close()
    co2int=int(co2[-9:-5])
    """
    global data
    conn.request("PUT", "/api/newdeveloper/lights/2/state", '{"on":true, "sat":255, "bri":255, "hue":%d} '% (co2int*10))
    responses = conn.getresponse()
    data = responses.read()
    time.sleep(2)
    return dict(co2=co2[-10:-1])
    """
    return dict(co2=co2, co2int=co2int)
    
def index():
    global data
    if len(sys.argv) <> 1:
        printUsing()
        sys.exit(1)
    pnt = "%s \n" % getDatetime(getDataPage())
    pnt2 = getDatablocks(getDataPage())
    pnt3 = ""
    conn.request("GET", "/api/newdeveloper/lights/2")
    responses = conn.getresponse()
    data = responses.read()
    state2 = data[1:52]
    #co2=co2get()
    for i in pnt2:
        pnt3+=i
        pnt3+="\n"
    return locals()
