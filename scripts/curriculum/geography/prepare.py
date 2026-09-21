from pathlib import Path
import json, urllib.request, concurrent.futures, hashlib, xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parent
CODES='id jp cn in sa tr au nz us ca mx br ar gb fr it de es eg ke za ng th my'.split()

def download(path,url):
 p=ROOT/path
 if not p.exists():
  with urllib.request.urlopen(url,timeout=45) as r: p.write_bytes(r.read())
 return (str(path),p.stat().st_size)

jobs=[('flags/'+c+'.svg','https://raw.githubusercontent.com/lipis/flag-icons/main/flags/4x3/'+c+'.svg') for c in CODES]+[('FLAGS-LICENSE.txt','https://raw.githubusercontent.com/lipis/flag-icons/main/LICENSE'),('flag-country-source.json','https://raw.githubusercontent.com/lipis/flag-icons/main/country.json')]
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
 for x in ex.map(lambda j:download(*j), jobs): print(*x,flush=True)

# All paths are a deterministic projection of the downloaded Natural Earth dataset.
source=json.loads((ROOT/'world-countries.geojson').read_text())
features={f['properties']['ISO_A2_EH'].lower():f for f in source['features']}

def project(lng,lat):return [round((lng+180)/360*1000,2),round((90-lat)/180*500,2)]

def path_geometry(g):
 polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
 paths=[]
 for poly in polys:
  for ring in poly:
   pts=[project(*p[:2]) for p in ring]
   paths.append('M'+'L'.join(str(x)+','+str(y) for x,y in pts)+'Z')
 return ''.join(paths)

paths=[]
for f in source['features']:
 p=f['properties']; paths.append({'code':p['ISO_A2_EH'].lower(),'id':p['ADM0_A3'],'d':path_geometry(f['geometry'])})
(ROOT/'world-map-paths.json').write_text(json.dumps({'viewBox':'0 0 1000 500','width':1000,'height':500,'projection':'equirectangular','source':'Natural Earth 1:110m admin-0 countries','attribution':'Made with Natural Earth.','paths':paths},separators=(',',':')))

names={
'id':['Indonesia','Indonesia','印度尼西亚','إندونيسيا'],
'jp':['Jepang','Japan','日本','اليابان'],
'cn':['Tiongkok','China','中国','الصين'],
'in':['India','India','印度','الهند'],
'sa':['Arab Saudi','Saudi Arabia','沙特阿拉伯','السعودية'],
'tr':['Turki','Türkiye','土耳其','تركيا'],
'au':['Australia','Australia','澳大利亚','أستراليا'],
'nz':['Selandia Baru','New Zealand','新西兰','نيوزيلندا'],
'us':['Amerika Serikat','United States','美国','الولايات المتحدة'],
'ca':['Kanada','Canada','加拿大','كندا'],
'mx':['Meksiko','Mexico','墨西哥','المكسيك'],
'br':['Brasil','Brazil','巴西','البرازيل'],
'ar':['Argentina','Argentina','阿根廷','الأرجنتين'],
'gb':['Britania Raya','United Kingdom','英国','المملكة المتحدة'],
'fr':['Prancis','France','法国','فرنسا'],
'it':['Italia','Italy','意大利','إيطاليا'],
'de':['Jerman','Germany','德国','ألمانيا'],
'es':['Spanyol','Spain','西班牙','إسبانيا'],
'eg':['Mesir','Egypt','埃及','مصر'],
'ke':['Kenya','Kenya','肯尼亚','كينيا'],
'za':['Afrika Selatan','South Africa','南非','جنوب أفريقيا'],
'ng':['Nigeria','Nigeria','尼日利亚','نيجيريا'],
'th':['Thailand','Thailand','泰国','تايلاند'],
'my':['Malaysia','Malaysia','马来西亚','ماليزيا'],
}
# Child-facing map labels use representative interior label points provided by Natural Earth;
# these are neither capitals nor computed geometric national centroids.
regions={'Asia':['Asia','Asia','亚洲','آسيا'],'Europe':['Eropa','Europe','欧洲','أوروبا'],'Oceania':['Oseania','Oceania','大洋洲','أوقيانوسيا'],'North America':['Amerika Utara','North America','北美洲','أمريكا الشمالية'],'South America':['Amerika Selatan','South America','南美洲','أمريكا الجنوبية'],'Africa':['Afrika','Africa','非洲','أفريقيا']}
countries=[]
for c in CODES:
 p=features[c]['properties']; lng,lat=p['LABEL_X'],p['LABEL_Y']
 if c=='nz': lng,lat=175.6,-39.2 # Interior of North Island; source label lies offshore.
 x,y=project(lng,lat)
 countries.append({'code':c,'iso3':p['ISO_A3_EH'],'name':dict(zip(['id','en','zh','ar'],names[c])),'region':dict(zip(['id','en','zh','ar'],regions[p['CONTINENT']])),'regionId':p['CONTINENT'].lower().replace(' ','-'),'flag':'/assets/flags/'+c+'.svg','lng':lng,'lat':lat,'x':x,'y':y,'markerKind':'representative-label-point'})
(ROOT/'countries.json').write_text(json.dumps(countries,ensure_ascii=False,indent=2)+'\n')
flag_country=json.loads((ROOT/'flag-country-source.json').read_text())
bycode={d['code']:d for d in flag_country}
checks=[]
for c in CODES:
 p=ROOT/'flags'/f'{c}.svg'; root=ET.fromstring(p.read_bytes())
 assert root.tag.endswith('svg') and 'viewBox' in root.attrib
 assert c in bycode,c
 checks.append({'code':c,'upstreamName':bycode[c]['name'],'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'viewBox':root.attrib['viewBox']})
manifest={'retrieved':'2026-09-18','countries':24,'geometryFeatures':len(paths),'mapSource':'https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_110m_admin_0_countries.geojson','mapTerms':'https://www.naturalearthdata.com/about/terms-of-use/','namesReference':'https://unstats.un.org/unsd/methodology/m49/','flagSource':'https://github.com/lipis/flag-icons','flagLicense':'MIT','mapLicense':'Public domain','flags':checks,'geometrySha256':hashlib.sha256((ROOT/'world-countries.geojson').read_bytes()).hexdigest()}
(ROOT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('READY', len(countries),'countries,',len(paths),'geometry features')
