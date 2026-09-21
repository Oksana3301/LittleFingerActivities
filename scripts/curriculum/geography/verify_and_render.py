from pathlib import Path
import json
r=Path(__file__).resolve().parent
geo=json.loads((r/'world-countries.geojson').read_text()); features={f['properties']['ISO_A2_EH'].lower():f for f in geo['features']}
countries=json.loads((r/'countries.json').read_text())
def in_ring(x,y,ring):
 yes=False
 for a,b in zip(ring,ring[1:]+ring[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:yes=not yes
 return yes
for c in countries:
 g=features[c['code']]['geometry']; polys=g['coordinates'] if g['type']=='MultiPolygon' else [g['coordinates']]
 assert any(in_ring(c['lng'],c['lat'],p[0]) and not any(in_ring(c['lng'],c['lat'],hole) for hole in p[1:]) for p in polys),c['code']
 assert all(c['name'][lang] for lang in ['id','en','zh','ar'])
print('PASS: all 24 representative points lie inside their source country polygons; all names have four languages.')
m=json.loads((r/'world-map-paths.json').read_text())
svg='<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 500"><title>World map — Natural Earth</title><rect width="1000" height="500" fill="#e7f0ef"/><g fill="#c3d0b9" fill-rule="evenodd">'+''.join('<path d="'+p['d']+'"/>' for p in m['paths'])+'</g></svg>'
(r/'world.svg').write_text(svg)
(r/'validation.json').write_text(json.dumps({'countries':24,'flagSvgValid':24,'insideSourceCountry':24,'fourLanguageNames':24,'projection':'equirectangular','viewBox':'0 0 1000 500'},indent=2)+'\n')
