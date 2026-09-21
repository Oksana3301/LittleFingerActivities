"""Deterministic preschool curriculum: 56 categories × 24 worksheets × 4 rounds."""
from pathlib import Path
import json, random, hashlib, math

OUT=Path(__file__).parent
ASSET_NAMES={
'hen':('Ayam','Hen'),'duck':('Bebek','Duck'),'turtle':('Kura-kura','Turtle'),'cat':('Kucing','Cat'),'rabbit':('Kelinci','Rabbit'),'goat':('Kambing','Goat'),'squirrel':('Tupai','Squirrel'),'bird':('Burung','Bird'),'lion':('Singa','Lion'),'butterfly':('Kupu-kupu','Butterfly'),'snail':('Siput','Snail'),'ladybug':('Kepik','Ladybug'),'bee':('Lebah','Bee'),'cow':('Sapi','Cow'),'horse':('Kuda','Horse'),'dog':('Anjing','Dog'),
'carrot':('Wortel','Carrot'),'cucumber':('Mentimun','Cucumber'),'tomato':('Tomat','Tomato'),'apple':('Apel','Apple'),'banana':('Pisang','Banana'),'leaf':('Daun','Leaf'),'flower':('Bunga','Flower'),'tree':('Pohon','Tree'),'seed':('Biji','Seed'),'sprout':('Tunas','Sprout'),'sun':('Matahari','Sun'),'moon':('Bulan','Moon'),'cloud':('Awan','Cloud'),'raindrop':('Tetes air','Raindrop'),
'rocket':('Roket','Rocket'),'planet':('Planet','Planet'),'astronaut':('Astronaut','Astronaut'),'bicycle':('Sepeda','Bicycle'),'umbrella':('Payung','Umbrella'),'train':('Kereta','Train'),'boat':('Perahu','Boat'),'car':('Mobil','Car'),'watering-can':('Penyiram tanaman','Watering can'),'trowel':('Sekop kecil','Trowel'),'star':('Bintang','Star'),}
ASSETS=list(ASSET_NAMES)
ANIMALS=ASSETS[:16]
PRODUCE=['carrot','cucumber','tomato','apple','banana']
GARDEN=['leaf','flower','tree','seed','sprout','watering-can','trowel']
VEHICLES=['rocket','bicycle','train','boat','car']
SKY=['sun','moon','cloud','raindrop','planet','star']
HOME=['umbrella','bicycle','car','watering-can','trowel']
COLORS=[('red','Merah','Red','#EE5261'),('blue','Biru','Blue','#328EE6'),('yellow','Kuning','Yellow','#F4C542'),('green','Hijau','Green','#55AE71'),('purple','Ungu','Purple','#9468CF'),('orange','Jingga','Orange','#EE8C3D'),('pink','Merah muda','Pink','#F195BE'),('brown','Cokelat','Brown','#976346')]
SHAPES=[('circle','Lingkaran','Circle'),('square','Persegi','Square'),('triangle','Segitiga','Triangle'),('rectangle','Persegi panjang','Rectangle'),('oval','Oval','Oval'),('diamond','Belah ketupat','Rhombus'),('pentagon','Segilima','Pentagon'),('hexagon','Segienam','Hexagon'),('star','Bintang','Star'),('heart','Hati','Heart')]
COLOR={v[0]:v for v in COLORS}; SHAPE={v[0]:v for v in SHAPES}
LETTERS=list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
CAT=[]
def cat(id,title,en,engine,group,age): CAT.append(dict(id=id,title={'id':title,'en':en},engine=engine,group=group,ageRange=age,worksheetCount=24))
for c in [
('animal-names','Kenali Hewan','Animal Names','identify','recognition',[2,4]),
('produce-names','Buah dan Sayur','Fruit and Vegetables','identify','recognition',[2,4]),
('garden-names','Benda di Kebun','In the Garden','identify','recognition',[2,5]),
('vehicle-names','Kendaraan','Vehicles','identify','recognition',[2,4]),
('sky-names','Langit dan Antariksa','Sky and Space','identify','recognition',[3,5]),
('home-names','Benda Sehari-hari','Everyday Objects','identify','recognition',[2,4]),
('colors','Warna Ceria','Color Explorer','identify','visual',[2,4]),
('shapes','Kenali Bentuk','Shape Explorer','identify','visual',[2,5]),
('size','Besar dan Kecil','Big and Small','compare','visual',[2,4]),
('length','Panjang dan Pendek','Long and Short','compare','visual',[3,5]),
('height','Tinggi dan Rendah','Tall and Short','compare','visual',[3,5]),
('thickness','Tebal dan Tipis','Thick and Thin','compare','visual',[3,5]),
('same-different','Sama atau Berbeda','Same and Different','identify','visual',[3,5]),
('directions','Arah Panah','Arrow Directions','identify','visual',[4,6]),
('positions','Di Mana Letaknya?','Where Is It?','identify','visual',[4,6]),
('symmetry','Cermin Bentuk','Mirror Drawing','draw','visual',[5,6]),
('object-pairs','Pasangan Gambar','Picture Pairs','pair','matching',[2,4]),
('silhouette-pairs','Pasangan Bayangan','Silhouette Pairs','pair','matching',[3,5]),
('color-pairs','Pasangan Warna','Color Pairs','pair','matching',[2,4]),
('shape-pairs','Pasangan Bentuk','Shape Pairs','pair','matching',[2,5]),
('number-pairs','Pasangan Angka','Numeral Pairs','pair','matching',[3,5]),
('uppercase-pairs','Pasangan Huruf Besar','Capital Letter Pairs','pair','matching',[4,6]),
('lowercase-pairs','Pasangan Huruf Kecil','Lowercase Letter Pairs','pair','matching',[4,6]),
('letter-case','Huruf Besar dan Kecil','Capital and Small Letters','pair','matching',[5,6]),
('initial-letters','Huruf Awal Kata','Beginning Letters','identify','literacy',[5,6]),
('vowels','Cari Huruf Vokal','Find the Vowels','identify','literacy',[4,6]),
('consonants','Cari Huruf Konsonan','Find the Consonants','identify','literacy',[5,6]),
('count-to-5','Hitung 1–5','Count 1–5','count','numbers',[2,4]),
('count-to-10','Hitung 1–10','Count 1–10','count','numbers',[3,5]),
('count-6-to-15','Hitung 6–15','Count 6–15','count','numbers',[5,6]),
('quantity-pairs','Angka dan Jumlah','Numerals and Quantities','pair','numbers',[4,6]),
('compare-quantity','Lebih Banyak atau Sedikit','More and Fewer','compare','numbers',[3,6]),
('ascending','Urutkan Angka Naik','Numbers Going Up','sequence','numbers',[4,6]),
('descending','Urutkan Angka Turun','Numbers Going Down','sequence','numbers',[5,6]),
('missing-number','Angka yang Hilang','Missing Number','pattern','numbers',[4,6]),
('add-to-5','Tambah sampai 5','Addition to 5','count','numbers',[4,6]),
('add-to-10','Tambah sampai 10','Addition to 10','count','numbers',[5,6]),
('subtract-to-5','Kurang sampai 5','Subtraction to 5','count','numbers',[4,6]),
('subtract-to-10','Kurang sampai 10','Subtraction to 10','count','numbers',[5,6]),
('pattern-ab','Pola AB','AB Patterns','pattern','patterns',[3,5]),
('pattern-abc','Pola ABC','ABC Patterns','pattern','patterns',[4,6]),
('pattern-aab-abb','Pola AAB dan ABB','AAB and ABB Patterns','pattern','patterns',[4,6]),
('growing-pattern','Pola Bertambah','Growing Patterns','pattern','patterns',[5,6]),
('memory-objects','Ingat Gambar','Picture Memory','memory','memory',[3,6]),
('memory-shapes','Ingat Bentuk','Shape Memory','memory','memory',[3,6]),
('memory-colors','Ingat Warna','Color Memory','memory','memory',[3,6]),
('trace-lines','Telusuri Garis','Trace Lines','trace','motor',[2,5]),
('trace-curves','Telusuri Lengkung','Trace Curves','trace','motor',[3,5]),
('trace-shapes','Telusuri Bentuk','Trace Shapes','trace','motor',[3,6]),
('trace-numbers','Telusuri Angka','Trace Numerals','trace','motor',[4,6]),
('trace-letters','Telusuri Huruf','Trace Letters','trace','motor',[4,6]),
('finish-picture','Lengkapi Gambar','Finish the Picture','draw','drawing',[3,6]),
('draw-to-count','Gambar Sesuai Jumlah','Draw and Count','draw','drawing',[3,6]),
('draw-pattern','Gambar Pola','Draw a Pattern','draw','drawing',[4,6]),
('spatial-drawing','Gambar di Tempatnya','Draw in Position','draw','drawing',[4,6]),
('imagine-draw','Ayo Berimajinasi','Imagine and Draw','draw','drawing',[2,6])]: cat(*c)

def bi(id,en): return {'id':id,'en':en}
def asset(key,**kw): return dict(kind='asset',asset=key,label=bi(*ASSET_NAMES[key]),**kw)
def shape(key,color='blue',**kw): return dict(kind='shape',shape=key,color=color,**kw)
def glyph(value,**kw): return dict(kind='glyph',text=str(value),**kw)
def quantity(n,key='apple',**kw): return dict(kind='quantity',count=n,item=asset(key),layout=kw.pop('layout','scattered'),**kw)
def choices(visuals,rng):
    out=[dict(id=f'o{i}',visual=x) for i,x in enumerate(visuals)]; rng.shuffle(out); return out
def identify(prompt,visuals,correct_indices,rng,**kw):
    return dict(prompt=prompt,options=choices(visuals,rng),correctIds=[f'o{i}' for i in correct_indices],**kw)
def choose_number(prompt,answer,rng,minimum=0,maximum=20,**kw):
    nums={answer}; pool=[x for x in range(max(minimum,answer-3),min(maximum,answer+3)+1) if x!=answer]
    rng.shuffle(pool); nums.update(pool[:3]); values=list(nums); rng.shuffle(values)
    return dict(prompt=prompt,options=[dict(id=f'n{x}',visual=glyph(x)) for x in values],correctIds=[f'n{answer}'],**kw)
def pairing(left,right,rng,**kw):
    l=[dict(id=f'l{i}',visual=x) for i,x in enumerate(left)]; r=[dict(id=f'r{i}',visual=x) for i,x in enumerate(right)]; rng.shuffle(r)
    return dict(prompt=bi('Pasangkan kartu yang cocok.','Match the cards.'),left=l,right=r,correctPairs=[[f'l{i}',f'r{i}'] for i in range(len(l))],**kw)
def stroke(d): return dict(kind='path',d=d,stroke='#94A7C5',strokeWidth=7,fill='none')
def draw_round(prompt,guide,goals,**kw): return dict(prompt=prompt,canvas=dict(viewBox=[0,0,400,300],guide=guide),completion=dict(mode='self-check',goals=goals),**kw)
def trace_round(prompt,paths,**kw): return dict(prompt=prompt,canvas=dict(viewBox=[0,0,400,300],guide=[stroke(x) for x in paths]),trace=dict(paths=paths,strokeOrder='suggested',tolerance=18,minimumCoverage=0.7),**kw)

def make_round(cid,v,k):
    rng=random.Random(f'{cid}:{v}:{k}'); t=v*4+k; level=v//4+1
    if cid.endswith('-names'):
        pool={'animal-names':ANIMALS,'produce-names':PRODUCE,'garden-names':GARDEN,'vehicle-names':VEHICLES,'sky-names':SKY,'home-names':HOME}[cid]
        target=pool[t%len(pool)]; copies=1+(v//8); distractors=rng.sample([x for x in ASSETS if x!=target],3+v//8)
        return identify(bi(f'Pilih semua gambar {ASSET_NAMES[target][0].lower()}.',f'Choose every {ASSET_NAMES[target][1].lower()}.'),[asset(target) for _ in range(copies)]+[asset(x) for x in distractors],list(range(copies)),rng,target=asset(target))
    if cid in ['colors','shapes']:
        color_mode=cid=='colors'; pool=[x[0] for x in COLORS if x[0]!='pink'] if color_mode else [x[0] for x in SHAPES]
        target=pool[t%len(pool)]; copies=1+v//8; other=rng.sample([x for x in pool if x!=target],3)
        visuals=[shape(rng.choice(SHAPES)[0],x) if color_mode else shape(x,rng.choice(COLORS)[0]) for x in [target]*copies+other]
        names=COLOR[target][1:3] if color_mode else SHAPE[target][1:3]
        return identify(bi(f'Pilih semua bentuk {names[0].lower()}.',f'Choose all {names[1].lower()} shapes.'),visuals,list(range(copies)),rng,criterion='color' if color_mode else 'shape')
    if cid in ['size','length','height','thickness']:
        values=rng.sample([0.35,0.5,0.65,0.8,0.95,1.1],3+(level>=4)); large=t%2==0
        prop={'size':'scale','length':'width','height':'height','thickness':'strokeWidth'}[cid]
        names={'size':('paling besar','paling kecil','biggest','smallest'),'length':('paling panjang','paling pendek','longest','shortest'),'height':('paling tinggi','paling rendah','tallest','shortest'),'thickness':('paling tebal','paling tipis','thickest','thinnest')}[cid]
        visuals=[dict(kind='measurement',measure=prop,value=x,baseShape='circle' if cid=='size' else 'bar',color=COLORS[v%8][0],fixedViewport=True) for x in values]
        return identify(bi(f'Pilih yang {names[0 if large else 1]}.',f'Choose the {names[2 if large else 3]} one.'),visuals,[values.index(max(values) if large else min(values))],rng,measure=prop)
    if cid=='same-different':
        a,b=rng.sample(SHAPES,2); c,d=rng.sample(COLORS,2); same=t%2==0
        base=shape(a[0],c[0]); visuals=[base,shape(a[0],d[0]),shape(b[0],c[0]),dict(base)]
        return identify(bi('Pilih semua yang sama persis dengan contoh.' if same else 'Pilih semua yang berbeda dari contoh.','Choose every exact match to the example.' if same else 'Choose every card different from the example.'),visuals,[0,3] if same else [1,2],rng,reference=base)
    if cid=='directions':
        dirs=[('up','atas','up'),('down','bawah','down'),('left','kiri','left'),('right','kanan','right'),('up-left','kiri atas','up and left'),('up-right','kanan atas','up and right'),('down-left','kiri bawah','down and left'),('down-right','kanan bawah','down and right')]; available=dirs[:4] if v<8 else dirs; target=rng.choice(available); repeats=1+(v+k)%3
        vals=[target]*repeats+[rng.choice([d for d in available if d!=target]) for _ in range(2+v%4)]
        return identify(bi(f'Pilih panah yang mengarah ke {target[1]}.',f'Choose arrows pointing {target[2]}.'),[dict(kind='arrow',direction=d[0],color=rng.choice(COLORS)[0]) for d in vals],list(range(repeats)),rng)
    if cid=='positions':
        positions=[('top-left','kiri atas','top left'),('top-center','tengah atas','top center'),('top-right','kanan atas','top right'),('middle-left','kiri tengah','middle left'),('center','tengah','center'),('middle-right','kanan tengah','middle right'),('bottom-left','kiri bawah','bottom left'),('bottom-center','tengah bawah','bottom center'),('bottom-right','kanan bawah','bottom right')]; p=rng.choice(positions); obj=rng.choice(ANIMALS)
        opts=[dict(id=f'p{i}',position=q[0],visual=asset(obj)) for i,q in enumerate(positions)]
        if v>=8 and k%2==0:
            row=rng.randrange(3); by_row=v%2==0; names=['atas','tengah','bawah'] if by_row else ['kiri','tengah','kanan']; en=['top','middle','bottom'] if by_row else ['left','middle','right']; correct=[f'p{i}' for i in range(9) if (i//3 if by_row else i%3)==row]
            return dict(prompt=bi(f'Pilih semua gambar di {"baris" if by_row else "kolom"} {names[row]}.',f'Choose every picture in the {en[row]} {"row" if by_row else "column"}.'),options=opts,correctIds=correct,layout='fixed-3-by-3',positionLabels=False)
        return dict(prompt=bi(f'Pilih gambar di bagian {p[1]}.',f'Choose the picture at the {p[2]}.'),options=opts,correctIds=[f'p{positions.index(p)}'],layout='fixed-3-by-3',positionLabels=False)
    if cid=='symmetry':
        pts=rng.sample([(x,y) for x in [50,90,130,170] for y in [60,100,140,180,220]],3+v//8)
        guide=[dict(kind='line',x1=200,y1=25,x2=200,y2=275,dashed=True)]+[dict(kind='circle',cx=x,cy=y,r=9,fill=COLORS[v%8][3]) for x,y in pts]
        return draw_round(bi('Gambar titik cerminnya di sisi kanan garis.','Draw the mirror dots on the right of the line.'),guide,[bi('Setiap titik punya pasangan dengan jarak yang sama dari garis.','Every dot has a partner the same distance from the line.')],modelAnswer=[{'x':400-x,'y':y} for x,y in pts],gridSpacing=40)
    if cid in ['object-pairs','silhouette-pairs','color-pairs','shape-pairs','number-pairs','uppercase-pairs','lowercase-pairs','letter-case','quantity-pairs']:
        n=3+v//8
        if cid in ['object-pairs','silhouette-pairs']:
            keys=rng.sample(ASSETS,n); left=[asset(x) for x in keys]; right=[asset(x,silhouette=cid=='silhouette-pairs') for x in keys]
        elif cid=='color-pairs':
            keys=rng.sample([x[0] for x in COLORS],n); left=[shape('circle',x) for x in keys]; right=[shape('square',x) for x in keys]
        elif cid=='shape-pairs':
            keys=rng.sample([x[0] for x in SHAPES],n); left=[shape(x,'blue') for x in keys]; right=[shape(x,'orange') for x in keys]
        elif cid in ['number-pairs','quantity-pairs']:
            keys=rng.sample(range(1,7+min(v//4,4)),n); left=[glyph(x) for x in keys]; right=[glyph(x) if cid=='number-pairs' else quantity(x,rng.choice(PRODUCE)) for x in keys]
        else:
            keys=rng.sample(LETTERS,n); left=[glyph(x.lower() if cid=='lowercase-pairs' else x) for x in keys]; right=[glyph(x.lower() if cid in ['letter-case','lowercase-pairs'] else x) for x in keys]
        return pairing(left,right,rng,criterion={'color-pairs':'color','shape-pairs':'shape','letter-case':'letter-case','quantity-pairs':'quantity'}.get(cid,'identity'))
    if cid=='initial-letters':
        obj=ASSETS[t%len(ASSETS)]; letter=ASSET_NAMES[obj][0][0].upper(); pool=[x for x in ASSETS if ASSET_NAMES[x][0][0].upper()==letter]; correct=rng.sample(pool,min(2,len(pool))); other=rng.sample([x for x in ASSETS if x not in pool],3)
        return identify(bi(f'Pilih gambar dengan nama berawalan huruf {letter}.',f'Choose pictures whose Indonesian names begin with {letter}.'),[asset(x,showLabel=True) for x in correct+other],list(range(len(correct))),rng,reference=glyph(letter),languageOfTask='id')
    if cid in ['vowels','consonants']:
        vowel=list('AEIOU'); consonant=[x for x in LETTERS if x not in vowel]; target=vowel if cid=='vowels' else consonant; other=consonant if cid=='vowels' else vowel; n=2+v//8; values=rng.sample(target,n)+rng.sample(other,3); lower=v%2==1
        return identify(bi('Pilih semua huruf vokal.' if cid=='vowels' else 'Pilih semua huruf konsonan.','Choose all vowels.' if cid=='vowels' else 'Choose all consonants.'),[glyph(x.lower() if lower else x) for x in values],list(range(n)),rng,referenceText='A E I O U' if cid=='vowels' else None)
    if cid in ['count-to-5','count-to-10','count-6-to-15']:
        lo,hi={'count-to-5':(1,5),'count-to-10':(1,10),'count-6-to-15':(6,15)}[cid]; n=lo+t%(hi-lo+1); obj=ASSETS[(v*3+k)%len(ASSETS)]
        return choose_number(bi('Ada berapa gambar? Hitung semuanya.','How many pictures? Count them all.'),n,rng,minimum=1,maximum=hi,scene=quantity(n,obj,layout=['row','grid','scattered'][v%3],seed=t))
    if cid=='compare-quantity':
        numbers=rng.sample(range(1,6+v//4),3); obj=rng.choice(ASSETS); more=t%2==0
        return identify(bi('Pilih kelompok yang paling banyak.' if more else 'Pilih kelompok yang paling sedikit.','Choose the group with the most.' if more else 'Choose the group with the fewest.'),[quantity(n,obj) for n in numbers],[numbers.index(max(numbers) if more else min(numbers))],rng)
    if cid in ['ascending','descending']:
        values=sorted(rng.sample(range(1,11+v//4),3+v//8),reverse=cid=='descending'); visuals=[glyph(x) for x in values]; options=choices(visuals,rng)
        if [o['id'] for o in options]==[f'o{i}' for i in range(len(values))]: options=options[1:]+options[:1]
        return dict(prompt=bi('Urutkan dari angka paling kecil.' if cid=='ascending' else 'Urutkan dari angka paling besar.','Put the smallest number first.' if cid=='ascending' else 'Put the largest number first.'),options=options,correctOrder=[f'o{i}' for i in range(len(values))])
    if cid=='missing-number':
        start=(v+k)%10; values=list(range(start,start+5)); idx=1+t%3; answer=values[idx]
        return choose_number(bi('Angka apa yang hilang?','Which number is missing?'),answer,rng,sequence=[None if i==idx else glyph(x) for i,x in enumerate(values)],rule=dict(type='number-step',step=1))
    if cid.startswith('add-') or cid.startswith('subtract-'):
        maximum=5 if cid.endswith('-5') else 10; subtract=cid.startswith('subtract-'); a=1+t%maximum; b=rng.randrange(a+1) if subtract else rng.randrange(maximum-a+1); result=a-b if subtract else a+b; obj=PRODUCE[(v+k)%len(PRODUCE)]
        expr=f'{a} {"−" if subtract else "+"} {b} = ?'; scene=dict(kind='arithmetic',operation='subtract' if subtract else 'add',a=a,b=b,item=asset(obj),crossOutRemoved=subtract,groupGap=36)
        return choose_number(bi(f'{expr} Hitung gambarnya.',f'{expr} Count the pictures.'),result,rng,maximum=maximum,scene=scene,expression=expr)
    if cid in ['pattern-ab','pattern-abc','pattern-aab-abb']:
        labels={'pattern-ab':[0,1],'pattern-abc':[0,1,2],'pattern-aab-abb':[0,0,1] if v%2==0 else [0,1,1]}[cid]; keys=rng.sample(ASSETS,4); length=len(labels)*3; hidden=length-1-(v//8); seq=[asset(keys[labels[i%len(labels)]] ) for i in range(length)]; answer=seq[hidden]; seq[hidden]=None; opts=choices([asset(x) for x in keys],rng)
        return dict(prompt=bi('Gambar mana yang melengkapi pola?','Which picture completes the pattern?'),sequence=seq,options=opts,correctIds=[f'o{keys.index(answer["asset"])}'],rule=dict(type='repeating',unit=labels))
    if cid=='growing-pattern':
        start=1+v%3; step=1+v//12; values=[start+i*step for i in range(4)]; obj=rng.choice(PRODUCE); answer=values[-1]
        return choose_number(bi('Jumlahnya bertambah teratur. Ada berapa gambar berikutnya?','The groups grow by the same amount. How many come next?'),answer,rng,sequence=[quantity(x,obj) for x in values[:-1]]+[None],rule=dict(type='quantity-step',step=step))
    if cid.startswith('memory-'):
        n=3+v//8
        if cid=='memory-objects': visuals=[asset(x) for x in rng.sample(ASSETS,n)]
        elif cid=='memory-shapes': visuals=[shape(x[0],'blue') for x in rng.sample(SHAPES,n)]
        else: visuals=[shape('circle',x[0]) for x in rng.sample(COLORS,n)]
        cards=[dict(id=f'card{i}-{j}',pairKey=f'pair{i}',visual=x) for i,x in enumerate(visuals) for j in range(2)]; rng.shuffle(cards)
        return dict(prompt=bi('Balik kartu dan temukan semua pasangan.','Turn the cards and find every pair.'),cards=cards,previewSeconds=2 if level<=2 else 0,allowReplay=True)
    if cid=='trace-lines':
        y=55+v%6*25; family=v//6; paths=[]
        if family==0: paths=[f'M 45 {y} L 355 {y}',f'M {70+k*35} 50 L {70+k*35} 250']
        elif family==1: paths=[f'M 50 {55+k*15+v%6*4} L 350 {225-k*15-v%6*4}',f'M 50 {225-k*15-v%6*4} L 350 {55+k*15+v%6*4}']
        elif family==2: paths=[f'M 40 {220-k*12} L 110 {50+v%6*10} L 180 220 L 250 {60+v%6*8} L 320 {220-v%6*5}']
        else: paths=[f'M 40 {y} H 110 V {y+65} H 190 V {y} H 270 V {y+65} H 355']
        return trace_round(bi('Ikuti jalur garis dengan jarimu atau pensil.','Follow the line paths with your finger or pencil.'),paths)
    if cid=='trace-curves':
        a=35+(v%6)*7; family=v//6
        if family==0: d=f'M 40 {180-k*10} Q 110 {a} 180 180 Q 250 {300-a} 360 {120+k*12}'
        elif family==1: d=f'M 45 230 C {80+k*8} {a} 290 {a} 355 230'
        elif family==2: d=f'M 40 150 C 90 {a} 130 {300-a} 180 150 S 280 {a} 355 150'
        else: d=f'M 200 150 m {-80-v%6*6} 0 a {80+v%6*6} {65+k*8} 0 1 0 {160+v%6*12} 0 a {80+v%6*6} {65+k*8} 0 1 0 {-160-v%6*12} 0'
        return trace_round(bi('Telusuri jalur lengkungnya.','Trace the curved path.'),[d])
    if cid=='trace-shapes':
        key=SHAPES[t%len(SHAPES)][0]; size=100+v%6*12; return dict(prompt=bi(f'Telusuri bentuk {SHAPE[key][1].lower()}.',f'Trace the {SHAPE[key][2].lower()}.'),canvas=dict(viewBox=[0,0,400,300],guide=[dict(kind='shape-outline',shape=key,cx=200,cy=150,width=size,height=size)]),trace=dict(source='shape-outline',strokeOrder='suggested',tolerance=18,minimumCoverage=0.7))
    if cid in ['trace-numbers','trace-letters']:
        text=str((v%10+k*[1,3,7][v//10])%10) if cid=='trace-numbers' else LETTERS[t%26].lower() if v%2 else LETTERS[t%26]
        return dict(prompt=bi(f'Telusuri {"angka" if cid=="trace-numbers" else "huruf"} {text}.',f'Trace {text}.'),canvas=dict(viewBox=[0,0,400,300],guide=[dict(kind='trace-glyph',text=text,x=200,y=150,fontSize=140+v%4*12)]),trace=dict(source='glyph-outline',font='Nunito',strokeOrder='not-graded',tolerance=18,minimumCoverage=0.65),teacherNote='Use an outline or dotted glyph; do not invent handwriting stroke order from a font outline.')
    if cid=='finish-picture':
        templates=[('flower','Tambahkan kelopak pada bunga.','Add petals to the flower.',[dict(kind='circle',cx=200,cy=125,r=22,fill='#F4C542'),dict(kind='line',x1=200,y1=150,x2=200,y2=260)]),('sun','Tambahkan sinar pada matahari.','Add rays to the sun.',[dict(kind='circle',cx=200,cy=145,r=50,fill='#F4C542')]),('face','Lengkapi wajah dengan mata dan senyum.','Add eyes and a smile.',[dict(kind='circle',cx=200,cy=150,r=95,fill='#FBE1C4')]),('umbrella','Tambahkan garis pada payung.','Add lines to the umbrella.',[dict(kind='asset',asset='umbrella',x=140,y=50,width=150,height=200)]),('tree','Tambahkan daun pada pohon.','Add leaves to the tree.',[dict(kind='line',x1=200,y1=250,x2=200,y2=85,strokeWidth=20)]),('butterfly','Tambahkan pola pada sayap kupu-kupu.','Decorate the butterfly wings.',[dict(kind='asset',asset='butterfly',x=90,y=50,width=220,height=190)])]
        key,id,en,guide=templates[t%6]; n=2+v//4; color=COLORS[v%8]
        return draw_round(bi(id+f' Gunakan {n} tanda {color[1].lower()}.',en+f' Use {n} {color[2].lower()} marks.'),guide,[bi(f'Aku menambahkan {n} tanda.','I added the requested number of marks.'),bi(f'Aku memakai warna {color[1].lower()}.',f'I used {color[2].lower()}.')])
    if cid=='draw-to-count':
        n=1+t%8; s=SHAPES[(v+k)%len(SHAPES)]; color=COLORS[v%8]
        return draw_round(bi(f'Gambar {n} bentuk {s[1].lower()} berwarna {color[1].lower()}.',f'Draw {n} {color[2].lower()} {s[2].lower()} shapes.'),[],[bi(f'Aku menggambar {n} bentuk.','I drew the requested number of shapes.'),bi('Bentuk dan warnanya sesuai.','The shape and color match.')],target=dict(count=n,shape=s[0],color=color[0]))
    if cid=='draw-pattern':
        a,b=rng.sample(SHAPES,2); colors=rng.sample(COLORS,2); unit=[0,1] if v<12 else [0,0,1]; items=[shape(a[0],colors[0][0]),shape(b[0],colors[1][0])]; seq=[items[unit[i%len(unit)]] for i in range(6)]
        return draw_round(bi('Lanjutkan pola dengan menggambar tiga bentuk berikutnya.','Continue the pattern by drawing the next three shapes.'),[dict(kind='pattern-strip',items=seq,x=25,y=40,width=350)], [bi('Tiga bentuk berikutnya mengikuti pola contoh.','The next three shapes follow the example.')],modelAnswer=[items[unit[i%len(unit)]] for i in range(6,9)])
    if cid=='spatial-drawing':
        relation=[('di atas','above'),('di bawah','below'),('di sebelah kiri','to the left of'),('di sebelah kanan','to the right of')][t%4]; obj=ASSETS[v%len(ASSETS)]; s=SHAPES[(v+k)%10]
        return draw_round(bi(f'Gambar {s[1].lower()} {relation[0]} gambar {ASSET_NAMES[obj][0].lower()}.',f'Draw a {s[2].lower()} {relation[1]} the {ASSET_NAMES[obj][1].lower()}.'),[dict(kind='asset',asset=obj,x=165,y=115,width=70,height=70)],[bi('Bentukku berada di tempat yang diminta.','My shape is in the requested position.')],target=dict(shape=s[0],relation=relation[1]))
    if cid=='imagine-draw':
        prompts=[('Taman untuk {a}','A garden for the {b}'),('Rumah untuk {a}','A home for the {b}'),('Petualangan {a}','An adventure with the {b}'),('Pesta bersama {a}','A party with the {b}'),('Baju lucu untuk {a}','A funny outfit for the {b}'),('Teman baru untuk {a}','A new friend for the {b}')]; a,b=ASSET_NAMES[ANIMALS[v%len(ANIMALS)]]; p=prompts[(v+k)%len(prompts)]
        return draw_round(bi('Gambar: '+p[0].format(a=a.lower())+'. Ceritakan gambarmu.','Draw: '+p[1].format(b=b.lower())+'. Tell a story about it.'),[dict(kind='asset',asset=ANIMALS[v%len(ANIMALS)],x=175,y=135,width=50,height=50)],[bi('Aku menambahkan ideku sendiri.','I added my own ideas.'),bi('Aku bisa bercerita tentang gambarku.','I can tell a story about my picture.')],openEnded=True)
    raise ValueError(cid)

def fingerprint(worksheet):
    # Exclude IDs and display metadata. Shuffling alone never makes a new worksheet.
    def canonical(x):
        if isinstance(x,dict): return {k:canonical(v) for k,v in sorted(x.items()) if k not in ('id','label','correctIds','correctPairs','correctOrder','seed','teacherNote','completion')}
        if isinstance(x,list):
            y=[canonical(v) for v in x]
            return sorted(y,key=lambda z:json.dumps(z,sort_keys=True)) if all(isinstance(v,dict) and 'visual' in v for v in x) else y
        return x
    return hashlib.sha256(json.dumps(canonical(worksheet['rounds']),sort_keys=True).encode()).hexdigest()

def validate(catalogue):
    assert len(CAT)==56
    assert len({x['id'] for x in CAT})==56
    assert len(catalogue)==1344
    for c in CAT:
        ws=[w for w in catalogue if w['categoryId']==c['id']]; assert len(ws)==24
        sigs=[fingerprint(w) for w in ws]; assert len(set(sigs))==24, f"Duplicate substantive worksheets: {c['id']}"
    def visit(x):
        if isinstance(x,dict):
            if 'asset' in x: assert x['asset'] in ASSET_NAMES, x['asset']
            if x.get('kind')=='quantity': assert 0<=x['count']<=20
            for v in x.values(): visit(v)
        elif isinstance(x,list):
            for v in x: visit(v)
    visit(catalogue)
    for w in catalogue:
        assert len(w['rounds'])==4
        for r in w['rounds']:
            if 'correctIds' in r:
                ids=[o['id'] for o in r['options']]; assert len(ids)==len(set(ids)); assert r['correctIds']; assert set(r['correctIds'])<=set(ids)
            if 'correctPairs' in r:
                assert len(r['correctPairs'])==len(r['left'])==len(r['right'])
                assert {x[0] for x in r['correctPairs']}=={x['id'] for x in r['left']}
                assert {x[1] for x in r['correctPairs']}=={x['id'] for x in r['right']}
            if 'correctOrder' in r: assert set(r['correctOrder'])=={x['id'] for x in r['options']}
            if 'cards' in r:
                keys=[x['pairKey'] for x in r['cards']]; assert all(keys.count(x)==2 for x in keys)
            if r.get('scene',{}).get('kind')=='arithmetic':
                s=r['scene']; ans=s['a']-s['b'] if s['operation']=='subtract' else s['a']+s['b']; assert r['correctIds']==[f'n{ans}']; assert 0<=ans<=(5 if w['categoryId'].endswith('-5') else 10)
            if 'sequence' in r: assert r['sequence'].count(None)==1
    return dict(categories=len(CAT),worksheets=len(catalogue),rounds=sum(len(w['rounds']) for w in catalogue),assets=len(ASSETS),substantiveDuplicates=0,missingAssets=0,status='passed')

def flatten_visual(x):
    out={'kind':x['kind']}
    if 'asset' in x: out.update(asset=x['asset'],label=x.get('label',bi(*ASSET_NAMES[x['asset']])))
    if 'shape' in x: out.update(shape=x['shape'],label=bi(*SHAPE[x['shape']][1:]))
    if 'color' in x: out.update(color=COLOR[x['color']][3],colorName=bi(*COLOR[x['color']][1:3]))
    if x['kind']=='glyph': out.update(symbol=x['text'],label=bi(x['text'],x['text']))
    if x['kind']=='quantity': out.update(value=x['count'],groupAsset=x['item']['asset'],layout=x['layout'],label=bi('Kelompok gambar','Picture group'),ariaLabel=bi(f"{x['count']} {ASSET_NAMES[x['item']['asset']][0].lower()}",f"{x['count']} {ASSET_NAMES[x['item']['asset']][1].lower()} pictures"),hideLabel=True)
    if x['kind']=='measurement': out.update(value=x['value'],measure=x['measure'],shape=x['baseShape'],scale=x['value'],label=bi('Lingkaran' if x['baseShape']=='circle' else 'Batang','Circle' if x['baseShape']=='circle' else 'Bar'),hideLabel=True)
    if x['kind']=='arrow': out.update(shape='arrow',direction=x['direction'],rotation={'up':0,'right':90,'down':180,'left':270,'up-right':45,'down-right':135,'down-left':225,'up-left':315}[x['direction']],label=bi('Panah','Arrow'),hideLabel=True)
    for key in ['silhouette','showLabel']: 
        if key in x: out[key]=x[key]
    return out

def flatten_round(r,engine):
    f={'instruction':r['prompt'],'options':[],'answer':r.get('correctIds',r.get('correctOrder',[]))}
    if 'options' in r: f['options']=[dict(id=o['id'],**flatten_visual(o['visual']),**({'position':o['position']} if 'position' in o else {})) for o in r['options']]
    if 'left' in r:
        f['options']=[dict(id=o['id'],**flatten_visual(o['visual'])) for o in r['left']]
        f['rightOptions']=[dict(id=o['id'],**flatten_visual(o['visual'])) for o in r['right']]
        f['pairs']=r['correctPairs']; right={o['id']:o for o in f['rightOptions']}
        for o,(l,rid) in zip(f['options'],r['correctPairs']):
            rv=right[rid]; o.update(pairId=rid,pairLabel=rv.get('label',bi('','')),pairedSymbol=rv.get('symbol'),pairedAsset=rv.get('asset'),pairedValue=rv.get('value'))
    if 'cards' in r: f['options']=[dict(id=o['id'],pairKey=o['pairKey'],**flatten_visual(o['visual'])) for o in r['cards']]
    if 'sequence' in r: f['patternItems']=[flatten_visual(x) if x else None for x in r['sequence']]
    if 'reference' in r: f['reference']=flatten_visual(r['reference'])
    if 'scene' in r:
        s=r['scene']; f['scene']=s
        if s['kind']=='quantity': f.update(countTarget=s['count'],countAsset=s['item']['asset'])
        if s['kind']=='arithmetic': f.update(countTarget=s['a']-s['b'] if s['operation']=='subtract' else s['a']+s['b'],countAsset=s['item']['asset'],operation=s['operation'],operands=[s['a'],s['b']])
    for key in ['canvas','completion','trace','target','modelAnswer','layout','criterion','rule','referenceText','languageOfTask','previewSeconds','allowReplay','openEnded','expression']:
        if key in r: f[key]=r[key]
    return f

def flatten_worksheet(w):
    rounds=[flatten_round(r,w['engine']) for r in w['rounds']]
    return dict(id=w['id'],category=w['categoryId'],title=w['title'],engine=w['engine'],age=w['ageRange'],minAge=w['ageRange'][0],difficulty=w['difficulty'],variant=w['variant'],**rounds[0],rounds=rounds)

def main():
    catalogue=[]
    for c in CAT:
        for v in range(24):
            rounds=[make_round(c['id'],v,k) for k in range(4)]
            catalogue.append(dict(id=f"{c['id']}-{v+1:02}",categoryId=c['id'],variant=v+1,difficulty=v//4+1,engine=c['engine'],title=bi(f"{c['title']['id']} · Latihan {v+1}",f"{c['title']['en']} · Practice {v+1}"),ageRange=c['ageRange'],rounds=rounds))
    report=validate(catalogue)
    (OUT/'curriculum.json').write_text(json.dumps(dict(schemaVersion=1,locales=['id','en'],defaultLocale='id',categories=CAT,assets=[dict(id=k,label=bi(*v)) for k,v in ASSET_NAMES.items()],colors=[dict(id=c[0],label=bi(c[1],c[2]),hex=c[3]) for c in COLORS],shapes=[dict(id=s[0],label=bi(s[1],s[2])) for s in SHAPES]),ensure_ascii=False,indent=2))
    (OUT/'worksheets.json').write_text(json.dumps(catalogue,ensure_ascii=False,separators=(',',':')))
    (OUT/'worksheets-flat.json').write_text(json.dumps([flatten_worksheet(w) for w in catalogue],ensure_ascii=False,separators=(',',':')))
    (OUT/'validation-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report))
if __name__=='__main__': main()
