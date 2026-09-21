#!/usr/bin/env python3
"""Author the vehicle, workshop, and hobby expansion. Writes only to --out.
Run: python scripts/curriculum/generate_vehicle_hobbies.py --out DIRECTORY
No network, dependencies, random state, dates, or reads from the Site checkout.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys


def T(id, en): return {'id': id, 'en': en}
NAMES = {
 'bus': ('Bus','Bus'), 'fire-truck': ('Truk pemadam','Fire truck'),
 'ambulance': ('Ambulans','Ambulance'), 'police-car': ('Mobil polisi','Police car'),
 'tractor': ('Traktor','Tractor'), 'excavator': ('Ekskavator','Excavator'),
 'bulldozer': ('Buldozer','Bulldozer'), 'crane': ('Derek','Crane'),
 'airplane': ('Pesawat','Airplane'), 'helicopter': ('Helikopter','Helicopter'),
 'ship': ('Kapal','Ship'), 'sailboat': ('Perahu layar','Sailboat'),
 'motorcycle': ('Sepeda motor','Motorcycle'), 'scooter': ('Skuter','Scooter'),
 'dump-truck': ('Truk jungkit','Dump truck'), 'submarine': ('Kapal selam','Submarine'),
 'hammer': ('Palu','Hammer'), 'wrench': ('Kunci pas','Wrench'),
 'screwdriver': ('Obeng','Screwdriver'), 'pliers': ('Tang','Pliers'),
 'saw': ('Gergaji','Saw'), 'drill': ('Bor','Drill'),
 'gear': ('Roda gigi','Gear'), 'wheel': ('Roda','Wheel'),
 'bolt': ('Baut','Bolt'), 'nut': ('Mur','Nut'), 'spring': ('Pegas','Spring'),
 'pulley': ('Katrol','Pulley'), 'robot': ('Robot','Robot'),
 'traffic-cone': ('Kerucut lalu lintas','Traffic cone'), 'helmet': ('Helm','Helmet'),
 'toolbox': ('Kotak perkakas','Toolbox'),
 'football': ('Bola sepak','Football'), 'basketball': ('Bola basket','Basketball'),
 'badminton-racket': ('Raket bulu tangkis','Badminton racket'),
 'tennis-racket': ('Raket tenis','Tennis racket'), 'kite': ('Layang-layang','Kite'),
 'skateboard': ('Papan luncur','Skateboard'), 'tent': ('Tenda','Tent'),
 'backpack': ('Ransel','Backpack'), 'compass': ('Kompas','Compass'),
 'binoculars': ('Teropong','Binoculars'), 'flashlight': ('Senter','Flashlight'),
 'building-blocks': ('Balok mainan','Building blocks'),
 't-rex': ('T. rex','T. rex'), 'triceratops': ('Triceratops','Triceratops'),
 'stegosaurus': ('Stegosaurus','Stegosaurus'), 'fossil': ('Fosil','Fossil'),
 'car': ('Mobil','Car'), 'bicycle': ('Sepeda','Bicycle'), 'train': ('Kereta','Train'),
 'boat': ('Perahu','Boat'), 'water-glass': ('Air minum','Drinking water'),
 'umbrella': ('Payung','Umbrella'),
}
ROAD = 'bus fire-truck ambulance police-car tractor motorcycle scooter dump-truck car bicycle'.split()
AIR = 'airplane helicopter'.split()
WATER = 'ship sailboat submarine boat'.split()
CONSTRUCTION = 'excavator bulldozer crane dump-truck tractor'.split()
TOOLS = 'hammer wrench screwdriver pliers saw drill'.split()
PARTS = 'gear wheel bolt nut spring pulley'.split()
SPORT = 'football basketball badminton-racket tennis-racket kite skateboard bicycle helmet'.split()
CAMP = 'tent backpack compass binoculars flashlight water-glass umbrella'.split()
DINO = 't-rex triceratops stegosaurus'.split()
HOBBY = SPORT + 'tent backpack compass binoculars flashlight building-blocks t-rex triceratops stegosaurus fossil'.split()
VEHICLES = ROAD + AIR + WATER + 'excavator bulldozer crane train'.split()


def rotate(items, seed):
    values=copy.deepcopy(items)
    if seed % 2: values.reverse()
    n=seed % len(values)
    return values[n:]+values[:n]


def subset(pool, count, v, r):
    # Coprime stride enumerates combinations before reuse; block changes vary later rounds.
    combinations=list(itertools.combinations(pool,count))
    stride=next(x for x in (5,7,11,13,17,19,23) if __import__('math').gcd(x,len(combinations))==1)
    return list(combinations[(v*stride+r*(1+v//len(combinations))+r*r*3)%len(combinations)])


def pic(asset, id):
    return {'id':id,'kind':'asset','asset':asset,'label':T(*NAMES[asset]),'showLabel':True}


def glyph(n):
    return {'id':f'n{n}','kind':'glyph','symbol':str(n),'value':n,'label':T(str(n),str(n))}


def dots(n,id):
    return {'id':id,'kind':'quantity','value':n,'label':T('Kelompok titik','Dot group'),
            'ariaLabel':T(f'{n} titik',f'{n} dots')}


def identify(pool,v,r,dinosaur=False):
    # First targets advance by a coprime stride; later target order also changes each block.
    stride=next(x for x in (5,7,11) if __import__('math').gcd(x,len(pool))==1)
    i=(v*stride+r*(1+v//len(pool))+r*r)%len(pool)
    if dinosaur:
        # Four ternary digits provide 24 distinct sequences, including varied first targets.
        i=((v//(3**r))*2+r)%3
    targets=[pool[i]]
    if (not dinosaur and v>=16) or (dinosaur and v>=18 and r==3):
        targets.append(pool[(i+1+(v+r)%(len(pool)-1))%len(pool)])
    n=min(len(pool),3+v//8)
    distractors=rotate([a for a in pool if a not in targets],v+r*3)[:n-len(targets)]
    assets=targets+distractors
    options=[pic(a,f'o{j}') for j,a in enumerate(assets)]
    return {'instruction':T('Pilih: '+', '.join(NAMES[a][0] for a in targets)+'.',
                             'Choose: '+', '.join(NAMES[a][1] for a in targets)+'.'),
            'options':rotate(options,v*7+r),'answer':[f'o{j}' for j in range(len(targets))]}


def matching(pool,v,r):
    n=3+v//8
    n=min(n,len(pool)-1)
    assets=subset(pool,n,v,r)
    left=[pic(a,f'l{j}') for j,a in enumerate(assets)]
    right=[pic(a,f'r{j}') for j,a in enumerate(assets)]
    return {'instruction':T('Pasangkan gambar dan nama yang sama.','Match the same pictures and names.'),
            'options':rotate(left,v+r*3),'rightOptions':rotate(right,v*3+r+1),
            'pairs':[{'left':f'l{j}','right':f'r{j}'} for j in range(n)],'answer':[]}


def sorting(cid,v,r):
    if cid=='air-water-vehicles':
        pools=[AIR,WATER]
        bins=[{'id':'air','label':T('Kendaraan udara','Air vehicles'),'asset':'airplane'},
              {'id':'water','label':T('Kendaraan air','Water vehicles'),'asset':'ship'}]
        prompt=T('Kelompokkan kendaraan udara dan kendaraan air. Pilih kartu, lalu kelompoknya.',
                 'Sort air vehicles and water vehicles. Choose a card, then its group.')
    elif cid=='workshop-sort':
        pools=[TOOLS,PARTS]
        bins=[{'id':'tools','label':T('Perkakas','Tools'),'asset':'toolbox'},
              {'id':'parts','label':T('Bagian mesin','Machine parts'),'asset':'gear'}]
        prompt=T('Kelompokkan perkakas dan bagian mesin. Pilih kartu, lalu kelompoknya.',
                 'Sort tools and machine parts. Choose a card, then its group.')
    else:
        # Fixed picture categories avoid judging whether a multi-use item belongs on an outing.
        pools=[CAMP[:5],DINO+['fossil']]
        bins=[{'id':'camp','label':T('Perlengkapan berkemah','Camping kit'),'asset':'tent'},
              {'id':'dino','label':T('Dinosaurus dan fosil','Dinosaurs and fossils'),'asset':'fossil'}]
        prompt=T('Kelompokkan perlengkapan berkemah serta dinosaurus dan fosil. Pilih kartu, lalu kelompoknya.',
                 'Sort camping kit and dinosaurs or fossils. Choose a card, then its group.')
    n=3+v//8
    n0=min(len(pools[0]),1+(v+r)%min(3,n-1))
    n1=n-n0
    if n1>len(pools[1]): n1=len(pools[1]); n0=n-n1
    assets=subset(pools[0],n0,v,r)+subset(pools[1],n1,v+3,r+2)
    options=[pic(a,f'o{j}') for j,a in enumerate(assets)]
    return {'instruction':prompt,'options':rotate(options,v*5+r),'bins':rotate(bins,v+r),
            'pairs':[{'left':o['id'],'right':bins[0 if o['asset'] in pools[0] else 1]['id']} for o in options],
            'answer':[]}


def counting(v,r):
    asset=VEHICLES[(v*7+r*3)%len(VEHICLES)]
    n=1+(v*5+r)%6
    choices=[n]+[x for x in rotate(list(range(1,7)),v+r) if x!=n][:2+v//8]
    return {'instruction':T('Ada berapa gambar kendaraan? Ketuk dan hitung semuanya.',
                             'How many vehicle pictures? Tap and count them all.'),
            'options':rotate([glyph(x) for x in choices],v+r),'answer':[f'n{n}'],
            'countAsset':asset,'countTarget':n}


def sequence(v,r):
    # This is an explicitly stated pretend card recipe, never a claim about vehicle mechanics.
    n=3+(v//12)
    parts=subset(['building-blocks','wheel','gear','bolt','nut','spring'],n-1,v,r)
    end=ROAD[(v*3+r*7)%len(ROAD)]
    assets=rotate(parts,v+r)+[end]
    return {'instruction':T('Urutan kartu rakitan kendaraan mainan kali ini: '+ ' → '.join(NAMES[a][0] for a in assets)+'. Pilih sesuai urutan.',
                             'This pretend toy vehicle uses this card order: '+ ' → '.join(NAMES[a][1] for a in assets)+'. Choose in that order.'),
            'options':rotate([pic(a,f'o{j}') for j,a in enumerate(assets)],v+r+1),
            'answer':[f'o{j}' for j in range(n)]}


def memory(v,r):
    assets=subset(CAMP,3+v//8,v,r)
    return {'instruction':T('Balik kartu berkemah. Temukan semua pasangan yang sama.',
                             'Turn over the camping cards. Find every matching pair.'),
            'options':rotate([pic(a,f'p{j}') for j,a in enumerate(assets)],v+r),'answer':[]}


def pattern(v,r):
    templates=[(0,1),(0,0,1),(0,1,1),(0,1,2)]
    template=templates[(v//6+r)%4]
    unit_assets=subset(HOBBY,max(template)+1,v,r)
    unit=[unit_assets[k] for k in template]
    # Two complete visible repetitions always precede the sole gap in repetition three.
    prefix=unit*2+unit[:(v+r)%len(unit)]
    target=unit[len(prefix)%len(unit)]
    assets=unit_assets+[x for x in rotate(HOBBY,v*5+r) if x not in unit_assets][:4-len(unit_assets)]
    return {'instruction':T('Pola ini berulang. Gambar apa yang mengisi tempat kosong?',
                             'This pattern repeats. Which picture fills the empty space?'),
            'options':rotate([pic(a,f'o{j}') for j,a in enumerate(assets)],v+r),
            'patternItems':[pic(a,f'p{j}') for j,a in enumerate(prefix)]+[None],
            'answer':[f'o{assets.index(target)}']}


def tracing(v,r):
    asset=VEHICLES[(v*7+r*3)%len(VEHICLES)]
    kind=(v+r)%6
    y=70+(v//6)*22+r*7
    paths=[f'M 45 {y} L 355 {y}',
           f'M 45 {y} L 355 {250-y//3}',
           f'M 45 {y} L 120 {y+85} L 195 {y} L 270 {y+85} L 355 {y}',
           f'M 45 {y+65} Q 120 {y-40} 195 {y+65} Q 270 {y+110} 355 {y+35}',
           f'M 65 {y+80} L 65 {y} L 330 {y} L 330 {y+80}',
           f'M 45 {y+45} C 100 {y-40} 150 {y+125} 200 {y+45} S 300 {y-40} 355 {y+45}']
    # All coordinates stay inside the existing 400 × 300 drawing surface.
    labels=[('lurus','straight'),('miring','sloping'),('zig-zag','zigzag'),('melengkung','curved'),('berbelok','turning'),('bergelombang','wavy')]
    return {'instruction':T(f'Bayangkan {NAMES[asset][0].lower()} mengikuti jalur. Telusuri garis {labels[kind][0]}.',
                             f'Imagine {"an" if NAMES[asset][1][0].lower() in "aeiou" else "a"} {NAMES[asset][1].lower()} on a path. Trace the {labels[kind][1]} line.'),
            'options':[],'answer':[],
            'canvas':{'viewBox':[0,0,400,300],'guide':[{'kind':'path','d':paths[kind],'fill':'none','stroke':'#94A7C5','strokeWidth':7}]},
            'completion':{'mode':'self-check','goals':[T('Aku sudah mencoba mengikuti jalur.','I tried following the path.')]}}


def drawing(v,r):
    n=1+(v+r)%4
    shape=[('lingkaran','circle','circles'),('garis','line','lines'),('persegi','square','squares')][(v//4+r)%3]
    zone=(v//12+r)%2
    frame=({'kind':'path','d':'M 65 55 H 335 V 245 H 65 Z','fill':'none','stroke':'#94A7C5','strokeWidth':3} if zone==0 else
           {'kind':'circle','cx':200,'cy':150,'r':108,'fill':'none','stroke':'#94A7C5','strokeWidth':3})
    return {'instruction':T(f'Bayangkan panel robot. Gambar {n} {shape[0]} di dalam bingkai.',
                             f'Imagine a robot panel. Draw {n} {shape[1] if n==1 else shape[2]} inside the frame.'),
            'options':[],'answer':[], 'canvas':{'viewBox':[0,0,400,300],'guide':[frame]},
            'completion':{'mode':'self-check','goals':[T(f'Aku mencoba membuat {n} {shape[0]}.',f'I tried drawing {n} {shape[1] if n==1 else shape[2]}.'),
                                                     T('Aku melihat hasilnya bersama pendamping.','I looked at my drawing with a grown-up.')]}}


def compare(v,r):
    mode=(v+r)%3
    vals=list(list(itertools.combinations(range(1,7),3))[(v*7+r*3)%20])
    options=[dots(n,f'o{j}') for j,n in enumerate(vals)]
    prompt=[('paling banyak','the most'),('paling sedikit','the fewest'),('sama banyak dengan contoh','the same number as the example')][mode]
    target=max(vals) if mode==0 else min(vals) if mode==1 else vals[(v//3+r)%3]
    result={'instruction':T(f'Titik adalah balok mainan kita. Pilih kelompok dengan titik {prompt[0]}.',
                            f'The dots are our pretend blocks. Choose the group with {prompt[1]} dots.' if mode<2 else
                            'The dots are our pretend blocks. Choose the group with the same number of dots as the example.'),
            'options':rotate(options,v+r),'answer':[f'o{vals.index(target)}']}
    if mode==2: result['reference']=dots(target,'example')
    return result


SPECS=[
 ('road-vehicles','vehicles','identify',2,'bus','Kendaraan di Jalan','Road Vehicles','Kenali nama kendaraan melalui gambar dan label.','Explore vehicle names through pictures and labels.'),
 ('air-water-vehicles','vehicles','sort',3,'airplane','Udara dan Air','Air and Water','Kelompokkan kendaraan udara dan kendaraan air.','Group air vehicles and water vehicles.'),
 ('construction-vehicles','vehicles','pair',3,'excavator','Pasangan Kendaraan Proyek','Construction Vehicle Pairs','Cocokkan gambar dan nama kendaraan proyek.','Match construction vehicle pictures and names.'),
 ('vehicle-count','vehicles','count',3,'dump-truck','Hitung Kendaraan','Count Vehicles','Hitung satu sampai enam gambar kendaraan.','Count one to six vehicle pictures.'),
 ('garage-tools','mechanics','pair',3,'toolbox','Pasangan Perkakas','Tool Pairs','Cocokkan gambar dan nama perkakas.','Match tool pictures and names.'),
 ('machine-parts','mechanics','identify',3,'gear','Nama Bagian Mesin','Machine Part Names','Kenali roda gigi, roda, baut, mur, pegas, dan katrol.','Explore gears, wheels, bolts, nuts, springs, and pulleys.'),
 ('build-a-vehicle','mechanics','sequence',4,'wheel','Urutan Rakitan Mainan','Toy Build Order','Ikuti urutan kartu rakitan mainan yang disebutkan.','Follow the stated card order for a pretend toy build.'),
 ('workshop-sort','mechanics','sort',3,'wrench','Kelompok Bengkel','Workshop Groups','Kelompokkan perkakas dan bagian mesin.','Group tools and machine parts.'),
 ('sports-kit','hobbies','pair',3,'football','Pasangan Perlengkapan Bermain','Play Kit Pairs','Cocokkan gambar perlengkapan olahraga dan bermain.','Match sports and play equipment pictures.'),
 ('camping-kit','hobbies','memory',3,'tent','Ingat Perlengkapan Berkemah','Camping Kit Memory','Balik kartu dan temukan pasangan gambar berkemah.','Turn cards and find matching camping pictures.'),
 ('hobby-patterns','hobbies','pattern',4,'kite','Pola Hobi','Hobby Patterns','Isi satu tempat kosong pada pola yang berulang.','Fill one empty space in a repeating pattern.'),
 ('vehicle-paths','vehicles','trace',2,'traffic-cone','Jalur Kendaraan','Vehicle Paths','Bayangkan kendaraan dan telusuri jalur geometrisnya.','Imagine vehicles and trace their geometric paths.'),
 ('dinosaur-names','hobbies','identify',3,'triceratops','Nama Dinosaurus','Dinosaur Names','Kenali tiga nama dinosaurus melalui kartu berlabel.','Explore three dinosaur names with labeled cards.'),
 ('robot-drawing','mechanics','draw',3,'robot','Gambar Panel Robot','Draw a Robot Panel','Tambahkan bentuk pada panel robot khayalan.','Add shapes to an imaginary robot panel.'),
 ('build-blocks','hobbies','compare',3,'building-blocks','Bandingkan Balok Mainan','Compare Pretend Blocks','Bandingkan jumlah titik yang mewakili balok mainan.','Compare dot groups that represent pretend blocks.'),
 ('adventure-sort','hobbies','sort',3,'backpack','Kelompok Petualangan','Adventure Groups','Pisahkan kartu berkemah dari kartu dinosaurus dan fosil.','Separate camping cards from dinosaur and fossil cards.'),
]


def round_for(cid,v,r):
    if cid=='road-vehicles': return identify(ROAD,v,r)
    if cid in ('air-water-vehicles','workshop-sort','adventure-sort'): return sorting(cid,v,r)
    if cid=='construction-vehicles': return matching(CONSTRUCTION,v,r)
    if cid=='vehicle-count': return counting(v,r)
    if cid=='garage-tools': return matching(TOOLS+['toolbox'],v,r)
    if cid=='machine-parts': return identify(PARTS,v,r)
    if cid=='build-a-vehicle': return sequence(v,r)
    if cid=='sports-kit': return matching(SPORT,v,r)
    if cid=='camping-kit': return memory(v,r)
    if cid=='hobby-patterns': return pattern(v,r)
    if cid=='vehicle-paths': return tracing(v,r)
    if cid=='dinosaur-names': return identify(DINO,v,r,True)
    if cid=='robot-drawing': return drawing(v,r)
    if cid=='build-blocks': return compare(v,r)
    raise ValueError(cid)


GENERIC=T('Bacakan petunjuk dan label. Anak boleh menunjuk, berbicara, atau memilih dengan bantuan. Ikuti minat dan kenyamanan anak.',
          'Read the prompt and labels aloud. Children may point, speak, or choose with help. Follow the child\'s interests and comfort.')
NOTES={
 'build-a-vehicle':T('Ini urutan kartu untuk mainan khayalan, bukan petunjuk merakit kendaraan nyata. Bacakan urutan yang tertera; urutan setiap cerita boleh berbeda.',
                    'This is a card order for an imaginary toy, not instructions for assembling a real vehicle. Read the stated order; each story may use a different order.'),
 'garage-tools':T('Kenali perkakas lewat gambar atau mainan yang sesuai usia bersama pendamping. Tidak perlu memakai perkakas sungguhan.',
                  'Explore tools through pictures or age-appropriate toys with a grown-up. Real tools are not needed.'),
 'workshop-sort':T('Bacakan nama kartu. Palu, kunci pas, obeng, tang, gergaji, dan bor adalah perkakas. Roda gigi, roda, baut, mur, pegas, dan katrol adalah bagian mesin dalam aktivitas ini.',
                   'Read the card names. Hammers, wrenches, screwdrivers, pliers, saws, and drills are tools. Gears, wheels, bolts, nuts, springs, and pulleys are machine parts in this activity.'),
 'machine-parts':T('Gunakan gambar atau mainan besar yang sesuai usia. Pendamping membacakan nama; anak tidak perlu memegang komponen kecil atau mesin nyata.',
                   'Use pictures or large age-appropriate toys. A grown-up reads the names; children do not need to handle small parts or real machines.'),
 'dinosaur-names':T('Bacakan tiga label nama: T. rex, Triceratops, dan Stegosaurus. Ilustrasi ini untuk latihan nama, bukan untuk membandingkan ukuran atau warna dinosaurus.',
                    'Read the three name labels: T. rex, Triceratops, and Stegosaurus. These pictures support naming, not comparisons of dinosaur size or color.'),
 'build-blocks':T('Setiap titik mewakili satu balok mainan dalam permainan ini. Hitung titik terpisah, bukan bagian-bagian di dalam ilustrasi balok.',
                  'Each dot stands for one pretend block in this game. Count separate dots, not parts inside a block illustration.'),
 'robot-drawing':T('Bingkai geometris adalah panel robot khayalan. Bacakan jumlah dan bentuk; anak boleh mencoba dengan caranya sendiri. Pendamping membahas hasil tanpa penilaian bentuk sempurna.',
                   'The geometric frame is an imaginary robot panel. Read the number and shape; children may try in their own way. Discuss the drawing without requiring perfect shapes.'),
 'vehicle-paths':T('Jalur ini untuk latihan gerak tangan dan imajinasi. Gunakan jari atau alat gambar. Anak boleh mengikuti sebagian jalur dan berhenti kapan saja.',
                   'These paths invite hand movement and imagination. Use a finger or drawing tool. Children may follow part of a path and stop whenever they like.'),
}
OFFSCREEN={
 'vehicles':T('Bersama pendamping, pilih kendaraan di buku atau mainan yang sesuai usia. Sebutkan namanya dan buat cerita perjalanan pendek.',
              'With a grown-up, choose a vehicle in a book or an age-appropriate toy. Say its name and tell a short travel story.'),
 'mechanics':T('Bersama pendamping, susun mainan besar atau gambar menjadi mesin khayalan. Ceritakan nama dan urutan pilihanmu.',
               'With a grown-up, arrange large toys or pictures into an imaginary machine. Talk about their names and your chosen order.'),
 'hobbies':T('Bersama pendamping, pilih permainan yang kamu sukai. Buat cerita, pasangan gambar, atau kelompok dengan mainan yang sesuai usia.',
             'With a grown-up, choose a game you enjoy. Make a story, picture pairs, or groups using age-appropriate toys.'),
}


def build():
    categories=[]; worksheets=[]
    for cid,group,engine,age,asset,ti,te,di,de in SPECS:
        categories.append({'id':cid,'group':group,'engine':engine,'age':age,'ageRange':[age,6],
                           'asset':asset,'title':T(ti,te),'description':T(di,de),'worksheetCount':24})
        for v in range(24):
            rounds=[round_for(cid,v,r) for r in range(4)]
            w={'id':f'{cid}-{v+1:02d}','category':cid,'engine':engine,'variant':v+1,
               'difficulty':1+v//8,'age':age,'ageRange':[age,6],'title':T(ti,te),
               'rounds':rounds,'note':NOTES.get(cid,GENERIC),'offscreen':OFFSCREEN[group]}
            w.update(copy.deepcopy(rounds[0])); worksheets.append(w)
    return categories,worksheets


def write_json(path,data):
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'
    path.write_text(payload,encoding='utf-8')
    return hashlib.sha256(payload.encode()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent)
    p.add_argument('--skip-audit',action='store_true',help='Write early artifacts for review before the independent audit.')
    args=p.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    categories,worksheets=build()
    hashes={name:write_json(args.out/name,data) for name,data in [('expansion-categories.json',categories),('expansion-worksheets.json',worksheets)]}
    manifest={'schema':'normalized Worksheet; root mirrors round 1; sort uses bins and pairs',
              'categoryCount':16,'worksheetCount':384,'roundCount':1536,'worksheetsPerCategory':24,'roundsPerWorksheet':4,
              'engines':sorted({c['engine'] for c in categories}),'requiredAssets':sorted(NAMES),
              'contentRules':['Bilingual Indonesian and English','Adult-guided ages 2–6','No gender labels',
                              'Explicit toy-card assembly orders','Canonical unique memory cards','Patterns show two full repetitions',
                              'Drawing and tracing use existing geometry','Block quantities count separate dots','No factual dinosaur claims'],
              'sourceFacts':'Naming and explicit picture classification only; no niche factual assertions.',
              'sha256':hashes}
    write_json(args.out/'expansion-manifest.json',manifest)
    if not args.skip_audit:
        subprocess.run([sys.executable,str(Path(__file__).with_name('validate_vehicle_hobbies.py')),'--out',str(args.out)],check=True)
    print(json.dumps({'categories':16,'worksheets':384,'rounds':1536,'out':str(args.out)}))


if __name__=='__main__': main()
