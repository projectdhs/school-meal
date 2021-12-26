school_kor_name="" #개발자도구를 통해 알아낸 학교 한글 이름
school_code="" #개발자도구를 통해 알아낸 학교 코드
crsesc_code="" #개발자도구를 통해 알아낸 코드
kndsc_code="" #개발자도구를 통해 알아낸 코드
domain="" #교육청 나이스도메인

import requests, json, datetime
from datetime import timedelta
import collections
import os
import html
day = ['mon', 'tue', 'wed', 'the', 'fri', 'sat', 'sun']
fi = os.path.join(os.getcwd(),"bab.txt")
tod_bab = os.path.join(os.getcwd(),"tod_bab.txt")   
now = datetime.datetime.now() #오늘의 식단
#now = datetime.datetime(2021, 12, 6, 00, 00, 0, 000000) #가져오고 싶은 날을 지정

def get_bab(ju, year, mon2):
      s = requests.session()
      

      url = 'https://'+domain+'/edusys.jsp?page=sts_m40000'
      
      headers={'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'}
      h = s.get(url, headers=headers)
      for i in h.cookies:
            if i.name == 'JSESSIONID':
                  c=i.value

      url = 'https://'+domain+'/sts_sci_md00_001.ws'
      form={'ay' : str(year), 
            'insttNm' : school_kor_name,
            'mm' : mon2,
            'schulCode' : school_code,
            'schulCrseScCode' : crsesc_code,
            'schulKndScCode' : kndsc_code}
      headers={'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
            'Referer' : 'https://'+domain+'/edusys.jsp?page=sts_m42310',
            'Origin' : 'https://'+domain,
            'Accept-Encoding' : 'gzip, deflate, br',
            'Accept' : 'application/json',
            'Accept-Language' : 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json'}

      html = s.post(url, headers=headers,data=json.dumps(form))#,cookies={'JSESSIONID': c})
      jso = json.loads(html.text)


      #print(ju)
      
      return jso ['resultSVO'] ['mthDietList']

def sav_bab(menu):
      sav = collections.OrderedDict()

      for i in day:
            sav[str(i)] = menu [ju] [i]
      sav['year'] = year
      sav['ju'] = ju
      sav['month'] = mon2

      f = open(fi, 'w', encoding='utf-8')
      json.dump(sav, f, ensure_ascii=False, indent="\t")
      f.close()

def get_ju(date):
      first = date.replace(day=1)
      first_weekday = first.weekday()

      days = int("{:d}".format(date.day))+first_weekday
      ju = int(days / 7)
      return ju  

def chk_bab(year, ju, mon2):
      if not os.path.isfile(fi):
            print("chk_bab 생성")
            return False
      f = open(fi, 'r', encoding='utf8')
      jso=json.load(f)
      f.close()

      if(jso['year'] != year or jso['ju'] != ju or jso['month'] != mon2):
            return True
      else:
            return False


date = now.weekday()
days = "{:d}".format(now.day)
tom = now + timedelta(days=1)


mon2 = "{:%m}".format(now)
year = now.year

ju = get_ju(now)
s = chk_bab(year, ju, mon2)
if s == True:
      jso = get_bab(ju, year, mon2)
      sav_bab(jso)
      print("다시추출")
#print(tom)
first = now.replace(day=1)
if not os.path.isfile(fi):
      jso = get_bab(ju, year, mon2)
      sav_bab(jso)

f = open(fi, 'r', encoding='utf-8')
jso=json.load(f)
f.close()

text = jso[day[date]]
chk = text.split("<br />") [0]
#print(chk)
bab = {}
n=0
stop=0
while True:
      if(chk == days):
            #print("오늘이맞음")
            break
      else:
            if n>0:
                  stop=1
                  break
if(stop == 0):
      if '[중식]' in text:
            bab[0] = html.unescape(text.split("[중식]<br />") [1])
            bab[0] = bab[0].split("<br />[석식]") [0]
            bab[0] = bab[0].replace("<br />", "\n")
      else:
            bab[0] = 'No'
      if '[석식]' in text:
            bab[1] = html.unescape(text.split("[석식]<br />") [1])
            bab[1] = bab[1].replace("<br />", "\n") 
      else:
            bab[1] = 'No'
      if tom.month != now.month:
            ju = get_ju(tom)
            year = tom.year
            mon2 = "{:%m}".format(tom)
            dates = tom.weekday()

            jso = get_bab(ju, year, mon2) [ju]
            #print(jso)
      else:
            dates = date+1
            if(dates==7):
                  dates=0
      days = "{:d}".format(tom.day)
      text = jso [day[dates]]
      
      chk = text.split("<br />") [0]
      if chk == days:
            if '[조식]' in text:
                  bab[2] = html.unescape(text.split("[조식]<br />") [1])
                  bab[2] = bab[2].split("<br />[중식]") [0]
                  bab[2] = bab[2].replace("<br />", "\n")
            else:
                  bab[2] = 'No'
      elif text == tom.day:
            if '[조식]' in text:
                  bab[2] = html.unescape(text.split("[조식]<br />") [1])
                  bab[2] = bab[2].split("<br />[중식]") [0]
                  bab[2] = bab[2].replace("<br />", "\n")
            else:
                  bab[2] = 'No'
      else:
           bab[2] = 'No' 
else:
      print("프로그램 종료")
      exit()
bs = str(now.year) + "년 " + str(now.month) + "월 " + str(now.day) +"일 급식\n"
for i in range(0,3):
      btime = ['점심', '저녁', '내일아침']
      bs = bs + "==="+btime[i]+"===\n"
      bs = bs + bab[i]+'\n\n'

f = open(tod_bab, 'w', encoding='utf-8')
print(bs)
f.write(bs)
f.close()

