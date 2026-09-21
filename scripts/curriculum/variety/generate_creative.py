#!/usr/bin/env python3
"""Author motor, drawing and adjective activity variety. Reads --source; writes --out only."""
import argparse, collections, copy, importlib.util, itertools, json, pathlib
L=('en','id','zh','ar')
def T(en,id,zh,ar): return dict(zip(L,(en,id,zh,ar)))
def clone(x): return copy.deepcopy(x)
def rotate(a,n): return a[n%len(a):]+a[:n%len(a)]
SHAPES=[('circle',T('circle','lingkaran','圆形','دائرة')),('square',T('square','persegi','正方形','مربع')),('triangle',T('triangle','segitiga','三角形','مثلث')),('rectangle',T('rectangle','persegi panjang','长方形','مستطيل')),('oval',T('oval','oval','椭圆形','شكل بيضاوي')),('diamond',T('diamond','belah ketupat','菱形','معين')),('pentagon',T('pentagon','segilima','五边形','خماسي الأضلاع')),('hexagon',T('hexagon','segienam','六边形','سداسي الأضلاع'))]
COLORS=[('#328EE6',T('blue','biru','蓝色','أزرق')),('#EE5261',T('red','merah','红色','أحمر')),('#55AE71',T('green','hijau','绿色','أخضر')),('#9467D6',T('purple','ungu','紫色','بنفسجي'))]
LINES=[('—',T('horizontal line','garis mendatar','横线','خط أفقي'),'M 65 150 L 335 150'),('|',T('vertical line','garis tegak','竖线','خط عمودي'),'M 200 45 L 200 255'),('/',T('line sloping up','garis miring naik','向上斜线','خط مائل إلى أعلى'),'M 70 235 L 330 65'),('\\',T('line sloping down','garis miring turun','向下斜线','خط مائل إلى أسفل'),'M 70 65 L 330 235')]
CURVES=[('∩',T('arch','lengkungan atas','拱形线','قوس علوي'),'M 70 220 Q 200 10 330 220'),('∪',T('bowl curve','lengkungan bawah','碗形曲线','قوس سفلي'),'M 70 80 Q 200 290 330 80'),('∿',T('wave','gelombang','波浪线','خط متموج'),'M 50 150 Q 125 25 200 150 Q 275 275 350 150'),('C',T('curve open to the right','lengkungan terbuka ke kanan','向右开口的曲线','منحنى مفتوح إلى اليمين'),'M 300 60 C 65 5 65 295 300 240')]
ARROWS=[('up',0,T('up','atas','上','أعلى')),('right',90,T('right','kanan','右','يمين')),('down',180,T('down','bawah','下','أسفل')),('left',270,T('left','kiri','左','يسار'))]
MOTOR=['trace-lines','trace-curves','trace-shapes','trace-numbers','trace-letters']
DRAWING=['finish-picture','draw-to-count','draw-pattern','spatial-drawing','imagine-draw','symmetry','vehicle-paths','robot-drawing']

def shape(i,oid,color=0):
 key,name=SHAPES[i%len(SHAPES)];c,cn=COLORS[color%len(COLORS)]
 desc=T(f'{cn["en"]} {name["en"]}',f'{name["id"]} {cn["id"]}',f'{cn["zh"]}{name["zh"]}',f'{name["ar"]}، اللون {cn["ar"]}')
 return dict(id=oid,kind='shape',shape=key,color=c,colorName=clone(cn),label=clone(name),ariaLabel=desc,pictureText=clone(desc))
def glyph(symbol,oid,label=None):
 label=label or T(symbol,symbol,symbol,symbol)
 return dict(id=oid,kind='glyph',symbol=symbol,label=clone(label),ariaLabel=clone(label),pictureText=clone(label))
def arrow(i,oid):
 direction,rotation,name=ARROWS[i%4]
 label=T('Arrow pointing '+name['en'],'Panah ke '+name['id'],'箭头朝'+name['zh'],'سهم نحو '+name['ar'])
 return dict(id=oid,kind='arrow',shape='arrow',direction=direction,rotation=rotation,color='#328EE6',label=label,ariaLabel=clone(label),pictureText=clone(label))
def quantity(n,oid):
 label=T('Dot group','Kelompok titik','点组','مجموعة نقاط');aria=T(f'{n} dots',f'{n} titik',f'{n}个点',f'{n} نقاط')
 return dict(id=oid,kind='quantity',value=n,label=label,ariaLabel=aria,pictureText=clone(aria),hideLabel=True)
def item(cid,n,oid,color=0):
 if cid in ['trace-lines','vehicle-paths']:
  s,l,_=LINES[n%4];return glyph(s,oid,l)
 if cid=='trace-curves':
  s,l,_=CURVES[n%4];return glyph(s,oid,l)
 if cid=='trace-numbers':return glyph(str(n%10),oid,T(f'Number {n%10}',f'Angka {n%10}',f'数字{n%10}',f'الرقم {n%10}'))
 if cid=='trace-letters':
  ch=chr(65+n%26);return glyph(ch,oid,T('Letter '+ch,'Huruf '+ch,'字母'+ch,'الحرف '+ch))
 if cid in ['symmetry','spatial-drawing']:return arrow(n,oid)
 if cid=='draw-to-count':return quantity(1+n%7,oid)
 return shape(n,oid,color)
def goal():return T('I tried the task and talked about my marks.','Aku mencoba tugas dan bercerita tentang coretanku.','我尝试了任务，并说说自己画的线条。','حاولت أداء النشاط وتحدثت عن الخطوط التي رسمتها.')
def roundbase(instr,**fields):return dict(instruction=instr,options=[],answer=[],**fields)
def pairround(cid,k):
 size={'trace-letters':26,'trace-numbers':10,'draw-to-count':7}.get(cid,4 if cid in ['trace-lines','trace-curves','vehicle-paths','symmetry','spatial-drawing'] else 8)
 combinations=list(itertools.combinations(range(size),2))+list(itertools.combinations(range(size),3))
 indices=list(combinations[k%len(combinations)])
 left=[item(cid,i,'l'+str(j),k%4) for j,i in enumerate(indices)]
 right=[clone(o)|{'id':'r'+str(j)} for j,o in enumerate(left)]
 instr=T('Match the same marks before drawing.','Pasangkan tanda yang sama sebelum menggambar.','画之前，先把相同的图形配对。','طابق العلامات المتشابهة قبل الرسم.')
 criterion='same-visual'
 if cid=='symmetry':
  instr=T('Match each arrow to its mirror across a vertical line. Up and down stay the same; left and right swap.','Pasangkan setiap panah dengan cerminnya pada garis tegak. Atas dan bawah tetap; kiri dan kanan bertukar.','把箭头和它在竖直镜线另一边的镜像配对。上下不变，左右互换。','طابق كل سهم مع انعكاسه حول خط عمودي. يبقى الأعلى والأسفل كما هما ويتبادل اليمين واليسار.')
  right=[arrow({0:0,1:3,2:2,3:1}[i],'r'+str(j)) for j,i in enumerate(indices)];criterion='vertical-mirror-arrow'
 elif cid=='draw-to-count':
  instr=T('Match each group of dots to the number of marks you would draw.','Pasangkan setiap kelompok titik dengan jumlah tanda yang akan kamu gambar.','把每组点和你需要画的点数配对。','طابق كل مجموعة نقاط مع عدد العلامات التي سترسمها.')
  right=[glyph(str(1+i),'r'+str(j)) for j,i in enumerate(indices)];criterion='quantity-number'
 elif cid=='trace-letters':instr=T('Match the same capital letters, then draw one in the air.','Pasangkan huruf besar yang sama, lalu gambar satu di udara.','配对相同的大写字母，再在空中写一个。','طابق الحروف الكبيرة المتشابهة ثم ارسم واحدا في الهواء.')
 elif cid=='trace-numbers':instr=T('Match the same numerals, then draw one in the air.','Pasangkan angka yang sama, lalu gambar satu di udara.','配对相同的数字，再在空中写一个。','طابق الأرقام المتشابهة ثم ارسم واحدا في الهواء.')
 elif cid=='vehicle-paths':instr=T('Match paths with the same line direction. Imagine driving along one with your finger.','Pasangkan jalur dengan arah garis yang sama. Bayangkan mengendarai kendaraan dengan jarimu.','把方向相同的路线配对，再想象用手指沿路行驶。','طابق المسارات ذات الاتجاه نفسه وتخيل القيادة على أحدها بإصبعك.')
 elif cid=='spatial-drawing':instr=T('Match arrows that point the same way. These directions help place a drawing.','Pasangkan panah yang menunjuk arah yang sama. Arah ini membantu menempatkan gambar.','配对指向相同的箭头。这些方向可以帮助你确定画的位置。','طابق الأسهم التي تشير إلى الاتجاه نفسه. تساعد هذه الاتجاهات على تحديد موضع الرسم.')
 elif cid=='robot-drawing':instr=T('Match shapes for an imaginary robot panel. Find the same shape and color.','Pasangkan bentuk untuk panel robot khayalan. Cari bentuk dan warna yang sama.','为想象中的机器人面板配对，找到形状和颜色都相同的图形。','طابق أشكال لوحة روبوت خيالي. ابحث عن الشكل واللون نفسيهما.')
 elif cid=='imagine-draw':instr=T('Match the same shapes. Think of a picture you could begin with each shape.','Pasangkan bentuk yang sama. Bayangkan gambar yang dapat diawali setiap bentuk.','配对相同的图形。想一想，每个图形可以变成什么画。','طابق الأشكال المتشابهة. تخيل رسما يمكن أن يبدأ بكل شكل.')
 elif cid=='finish-picture':instr=T('Match the complete shapes. Notice the edges you could draw to finish them.','Pasangkan bentuk utuh yang sama. Perhatikan tepi yang dapat kamu gambar untuk melengkapinya.','配对完整的相同图形。观察需要画哪些边才能把它补完整。','طابق الأشكال الكاملة المتشابهة ولاحظ الحواف التي يمكنك رسمها لإكمالها.')
 return dict(instruction=instr,options=left,rightOptions=rotate(right,k+1),answer=[o['id'] for o in left],pairs=[{'left':o['id'],'right':'r'+str(j)} for j,o in enumerate(left)],semantic={'rule':criterion})
def patternround(cid,k):
 # Each round changes its marks and its repeating unit, never merely its choice order.
 size={'trace-letters':26,'trace-numbers':10,'draw-to-count':7}.get(cid,4 if cid in ['trace-lines','trace-curves','vehicle-paths','symmetry','spatial-drawing'] else 8)
 idx=[(k+j)%size for j in range(3)]
 opt=[item(cid,i,'o'+str(j),k%4) for j,i in enumerate(idx)]
 if cid=='symmetry':
  # Geometric left-right reflection about the middle of this strip, not a repeating rule.
  chosen=list(itertools.combinations(range(8),3))[k%56]
  opt=[shape(i,'o'+str(j),k%4) for j,i in enumerate(chosen)]
  seq=[0,1,2,2,1,0];hole=k%6
  instruction=T('The strip is a mirror pattern: the first and last match, the next pair match, and the middle pair match. Fill the gap.','Deret ini bercermin: awal dan akhir sama, pasangan berikutnya sama, dan pasangan tengah sama. Isi bagian kosong.','这是镜像排列：首尾相同，第二个和倒数第二个相同，中间两个也相同。填入空缺。','هذا ترتيب متناظر: يتطابق الأول والأخير، ثم الزوج التالي، ثم الزوج الأوسط. أكمل الفراغ.')
  rule='mirror-strip'
 else:
  unit=[[0,1],[0,0,1],[0,1,1],[0,1,2],[0,0,1,2],[0,1,1,2],[0,1,2,2],[0,0,1,1],[0,1,0,2],[0,1,2,1],[0,1,1,0],[0,0,0,1],[0,1,1,1],[0,0,2,2],[0,2,1,2],[0,1,0,0]][k%16];seq=(unit*3)[:len(unit)*2+1];hole=len(seq)-1
  instruction=T('Look at the repeating marks. Choose the missing mark, then draw it in the air.','Lihat tanda yang berulang. Pilih tanda yang hilang, lalu gambar di udara.','观察重复的图形，选出缺少的一个，再在空中画出来。','انظر إلى العلامات المتكررة. اختر العلامة الناقصة ثم ارسمها في الهواء.')
  rule='repeat-pattern'
  if cid=='vehicle-paths':instruction=T('Road markers repeat along an imaginary route. Choose the next line marker.','Tanda garis berulang di jalur khayalan. Pilih tanda garis berikutnya.','想象的路线上的线条标记不断重复。选出下一个线条标记。','تتكرر علامات الخطوط على طريق خيالي. اختر علامة الخط التالية.')
  elif cid=='robot-drawing':instruction=T('Buttons on an imaginary robot panel repeat. Choose the next shape.','Tombol pada panel robot khayalan berulang. Pilih bentuk berikutnya.','想象中的机器人面板上按钮重复排列。选出下一个形状。','تتكرر أزرار لوحة روبوت خيالي. اختر الشكل التالي.')
  elif cid=='spatial-drawing':instruction=T('Follow the repeating directions for placing marks. Which arrow comes next?','Ikuti arah berulang untuk menempatkan tanda. Panah apa berikutnya?','按照重复的方向放置图形。接下来是什么箭头？','اتبع الاتجاهات المتكررة لوضع العلامات. أي سهم يأتي بعد ذلك؟')
  elif cid=='draw-to-count':instruction=T('Groups of dots repeat. Choose the next group, then count the marks you would draw.','Kelompok titik berulang. Pilih kelompok berikutnya, lalu hitung tanda yang akan digambar.','点数组按规律重复。选出下一组，再数数需要画几个点。','تتكرر مجموعات النقاط. اختر المجموعة التالية ثم عد العلامات التي سترسمها.')
 strip=[None if j==hole else clone(opt[z])|{'id':'p'+str(j)} for j,z in enumerate(seq)]
 return dict(instruction=instruction,options=rotate(opt,k),answer=['o'+str(seq[hole])],patternItems=strip,semantic={'rule':rule,'sequence':seq,'gap':hole,'optionIndices':{o['id']:j for j,o in enumerate(opt)}})
def pathguide(d):return dict(kind='path',d=d,fill='none',stroke='#94A7C5',strokeWidth=5)
def canvasround(cid,k,engine):
 guide=[]
 copies=1+k//4
 if cid in ['trace-lines','vehicle-paths','trace-curves']:
  bank=CURVES if cid=='trace-curves' else LINES;_,name,d=bank[k%4]
  instr=T('Draw your own '+name['en']+' below the example.','Gambar '+name['id']+' buatanmu di bawah contoh.','在示例下面自己画一个'+name['zh']+'。','ارسم '+name['ar']+' من عندك أسفل المثال.')
  # Reference is intentionally small and high, leaving the lower region free.
  # Use the canonical path with an explicit in-bounds second path area through two guide dots.
  if cid=='trace-curves':
   d=['M 125 100 Q 200 10 275 100','M 125 45 Q 200 145 275 45','M 80 80 Q 140 10 200 80 Q 260 150 320 80','M 260 30 C 135 0 135 140 260 110'][k%4]
  else:d=['M 100 65 L 300 65','M 200 25 L 200 110','M 130 110 L 270 25','M 130 25 L 270 110'][k%4]
  guide=[pathguide(d)]
  instr=T(f'Draw {copies} examples of the {name["en"]} below the small guide.',f'Gambar {copies} contoh {name["id"]} di bawah panduan kecil.',f'在小示例下面画{copies}条{name["zh"]}。',f'ارسم {copies} أمثلة من {name["ar"]} أسفل الدليل الصغير.')
  if cid=='vehicle-paths':
   instr=T('The small line is a route idea. Draw your own '+name['en']+' below it for an imaginary vehicle.','Garis kecil adalah ide jalur. Gambar '+name['id']+' di bawahnya untuk kendaraan khayalan.','小线条是路线示例。在下面自己画一个'+name['zh']+'，作为想象中车辆的路线。','الخط الصغير فكرة لمسار. ارسم '+name['ar']+' أسفله لمركبة خيالية.')
  if cid=='vehicle-paths':
   extra=T(f'Make {copies} separate routes.',f'Buat {copies} jalur terpisah.',f'画出{copies}条分开的路线。',f'ارسم {copies} مسارات منفصلة.')
   instr={lang:instr[lang]+' '+extra[lang] for lang in L}
 elif cid in ['trace-numbers','trace-letters']:
  symbol=str(k%10) if cid=='trace-numbers' else chr(65+k%26)
  instr=T(f'Look at {symbol}. Try drawing the same symbol below it, then say its name.',f'Lihat {symbol}. Coba gambar simbol yang sama di bawahnya, lalu sebutkan namanya.',f'看一看{symbol}。试着在下面写出相同符号，再说出它的名称。',f'انظر إلى {symbol}. حاول رسم الرمز نفسه أسفله ثم قل اسمه.')
  guide=[dict(kind='trace-glyph',text=symbol,x=200,y=55,fontSize=75)]
 elif cid=='symmetry':
  x=50+20*(k%4);y=60+35*(k%5)
  guide=[dict(kind='line',x1=200,y1=25,x2=200,y2=275,dashed=True),dict(kind='circle',cx=x,cy=y,r=10,fill='none'),dict(kind='circle',cx=400-x,cy=y,r=10,fill='none')]
  instr=T('Trace the two mirror circles. They are level and equally far from the middle line.','Telusuri dua lingkaran cermin. Keduanya sejajar dan sama jauh dari garis tengah.','描画两个镜像圆。它们一样高，与中线的距离相同。','تتبع الدائرتين المتناظرتين. هما على الارتفاع نفسه وعلى بعد متساو من الخط الأوسط.')
 elif cid=='spatial-drawing':
  direction,_,word=ARROWS[k%4];distance=60+20*(k//4);end={'up':(200,150-distance),'down':(200,150+distance),'left':(200-distance,150),'right':(200+distance,150)}[direction]
  guide=[dict(kind='circle',cx=200,cy=150,r=8,fill='#328EE6'),pathguide(f'M 200 150 L {end[0]} {end[1]}')]
  instr=T('Start at the dot and trace toward the '+word['en']+'.','Mulai dari titik lalu telusuri ke '+word['id']+'.','从点出发，向'+word['zh']+'描线。','ابدأ من النقطة وتتبع نحو '+word['ar']+'.')
 elif cid=='draw-to-count':
  n=1+k%6;columns=2+k//4;guide=[dict(kind='circle',cx=60+(j%columns)*280/(columns-1),cy=65+(j//columns)*100,r=22,fill='none') for j in range(n)]
  instr=T(f'Trace {n} circles. Count each circle as you go.',f'Telusuri {n} lingkaran. Hitung setiap lingkaran saat ditelusuri.',f'描画{n}个圆，一边描一边数。',f'تتبع {n} دوائر وعد كل دائرة أثناء التتبع.')
 elif cid=='draw-pattern':
  # Exact geometric paths; no representational illustration.
  a,b=[(0,1),(0,2),(1,0),(1,2),(2,0),(2,1)][k%6]
  total=4+2*(k//4)
  for j in range(total):
   x=35+j*330/(total-1);s=[a,b][j%2];rad=min(22,130/total);guide.append(dict(kind='circle',cx=x,cy=150,r=rad,fill='none') if s==0 else pathguide(f'M {x-rad} {150-rad} H {x+rad} V {150+rad} H {x-rad} Z') if s==1 else pathguide(f'M {x} {150-rad} L {x+rad} {150+rad} H {x-rad} Z'))
  instr=T('Trace the alternating shape pattern. Say which shape would come next.','Telusuri pola bentuk bergantian. Sebutkan bentuk berikutnya.','描画交替排列的形状，说出接下来是什么形状。','تتبع نمط الأشكال المتناوبة وقل أي شكل سيأتي بعده.')
 else:
  i=k%8;name=SHAPES[i][1];guide=[dict(kind='shape-outline',shape=SHAPES[i][0],cx=200,cy=150,width=180,height=120 if i in [3,4] else 180)]
  if engine=='draw':
   guide=[dict(kind='shape-outline',shape=SHAPES[i][0],cx=200,cy=60,width=65,height=45 if i in [3,4] else 65)]
   instr=T('Draw your own '+name['en']+' below the example.','Gambar '+name['id']+' sendiri di bawah contoh.','在示例下面自己画一个'+name['zh']+'。','ارسم '+name['ar']+' من عندك أسفل المثال.')
  else:instr=T('Trace the '+name['en']+'. Notice how its outline closes.','Telusuri '+name['id']+'. Perhatikan tepinya yang menutup.','描画'+name['zh']+'，观察它的轮廓怎样闭合。','تتبع '+name['ar']+' ولاحظ كيف يغلق حدوده.')
  if cid=='robot-drawing':instr=T('Trace this shape for an imaginary robot panel. Then imagine what the button could do.','Telusuri bentuk untuk panel robot khayalan ini. Bayangkan fungsi tombolnya.','为想象中的机器人面板描画这个形状，再想象这个按钮有什么用。','تتبع هذا الشكل للوحة روبوت خيالي ثم تخيل وظيفة الزر.')
  elif cid=='imagine-draw':instr=T('Trace this starting shape. Tell a grown-up an idea for a picture that begins with it.','Telusuri bentuk awal ini. Ceritakan ide gambar yang diawali bentuk ini kepada pendamping.','描画这个起始形状，告诉大人你想把它变成什么画。','تتبع شكل البداية هذا وأخبر شخصا كبيرا بفكرة رسم يبدأ به.')
  elif cid=='finish-picture':instr=T('Trace the full outline. Look for the point where the line meets its start.','Telusuri garis tepi utuh. Cari tempat garis bertemu titik awalnya.','描画完整的轮廓，找一找线条在哪里回到起点。','تتبع الحدود الكاملة وابحث عن الموضع الذي يعود فيه الخط إلى بدايته.')
 if cid in ['trace-shapes','finish-picture','imagine-draw','robot-drawing']:
  if engine=='trace':
   centers={1:[(200,150)],2:[(115,150),(285,150)],3:[(80,150),(200,150),(320,150)],4:[(115,80),(285,80),(115,220),(285,220)]}[copies]
   width=160 if copies==1 else 90
   guide=[dict(kind='shape-outline',shape=SHAPES[k%8][0],cx=x,cy=y,width=width,height=width*.65 if k%8 in [3,4] else width) for x,y in centers]
  extra=T(f'Try {copies} separate shapes.',f'Coba buat {copies} bentuk terpisah.',f'尝试画{copies}个分开的图形。',f'حاول رسم {copies} أشكال منفصلة.')
  instr={lang:instr[lang]+' '+extra[lang] for lang in L}
 return dict(instruction=instr,options=[],answer=[],canvas={'viewBox':[0,0,400,300],'guide':guide},completion={'mode':'self-check','goals':[goal()]},semantic={'rule':'manual-drawing','objective':cid,'taskIndex':k})

def patch(ws,engine,kind,rounds):
 # Remove first-round convenience fields left behind by the previous renderer.
 meta={k:clone(ws[k]) for k in ['id','category','title','variant','difficulty','age','ageRange','note','offscreen'] if k in ws}
 for r in rounds:r['activityKind']=kind
 return meta|{'engine':engine,'activityKind':kind,'revision':'variety-1','rounds':rounds}|clone(rounds[0])
def inferred(ws):
 return ws.get('activityKind') or {'identify':'choose-many' if any(len(r.get('answer',[]))>1 for r in ws['rounds']) else 'choose-one','compare':'choose-one','pair':'match'}.get(ws['engine'],ws['engine'])
def signature(o):return tuple(o.get(k) for k in ['kind','asset','shape','symbol','value','color','rotation'])

def validate_round(r,engine):
 assert set(L)<=r['instruction'].keys(),'missing instruction language'
 for o in r['options']+r.get('rightOptions',[])+[x for x in r.get('patternItems',[]) if x]:
  assert set(L)<=o['label'].keys(),'missing picture label language'
  assert set(L)<=o['pictureText'].keys(),'missing pictureText language'
  if o.get('color') or o['kind'] in ['measurement','arrow','quantity']:assert set(L)<=o['ariaLabel'].keys(),'missing descriptive narration'
 ids=[o['id'] for o in r['options']];assert len(ids)==len(set(ids)),'duplicate option id'
 sem=r['semantic'];rule=sem['rule']
 if engine in ['identify','pattern']:assert set(r['answer'])<=set(ids),'answer not in choices'
 if engine=='pair':
  left={o['id']:o for o in r['options']};right={o['id']:o for o in r['rightOptions']};assert len(r['pairs'])==len(left)==len(right)
  assert len({p['right'] for p in r['pairs']})==len(right)
  for p in r['pairs']:
   a,b=left[p['left']],right[p['right']]
   if rule=='same-visual':assert signature(a)==signature(b),'incorrect visual pair'
   elif rule=='quantity-number':assert int(b['symbol'])==a['value'],'incorrect numeral pair'
   elif rule=='vertical-mirror-arrow':assert b['direction']=={'up':'up','down':'down','left':'right','right':'left'}[a['direction']],'incorrect reflected arrow'
 if engine=='pattern':
  seq=sem['sequence'];gap=sem['gap'];assert sum(x is None for x in r['patternItems'])==1
  assert sem['optionIndices'][r['answer'][0]]==seq[gap],'wrong pattern answer'
  options={o['id']:o for o in r['options']}
  for j,p in enumerate(r['patternItems']):
   if p:assert signature(p)==signature(options['o'+str(seq[j])]),'wrong visible pattern item'
  if rule=='mirror-strip':assert seq==seq[::-1],'non-mirror strip'
 if rule in ['adjective-clue','adjective-odd']:
  choices={o['id']:o for o in r['options']}
  expected=[o['id'] for o in r['options'] if (o['vocabularyKey']==sem['target'] if rule=='adjective-clue' else o['dimension']!=sem['dimension'])]
  assert expected==r['answer'] or set(expected)==set(r['answer']),'incorrect adjective answer'
  assert len(expected)==1,'non-unique adjective answer'
 if engine=='memory':assert len({signature(o) for o in r['options']})==len(r['options']),'ambiguous memory faces'
 if engine in ['draw','trace']:assert r['completion']['mode']=='self-check' and not r['answer']

def adjective_content(mod,cid,a,b,index,mode):
 C=mod.CARDS
 def pic(key,oid,form=0):
  o=mod.pic(key,oid)
  if form==1:o['label']=clone(C[key]['word'])
  elif form==2:o['label']=clone(C[key]['clue'])
  o['ariaLabel']=clone(o['label']);o['pictureText']=clone(o['label']);return o
 # Vocabulary dimensions are authored explicitly, not inferred from artwork.
 dims={key:spec[0] for spec in mod.SPECS if spec[0]!='kind-descriptions' for key in spec[1:3]}
 others=[key for key in dims if key not in [a,b]]
 rounds=[]
 dimension={'temperature':T('temperature','suhu','温度','الحرارة'),'soft-hard':T('softness or hardness','empuk atau keras','软硬','الطراوة أو الصلابة'),'smooth-rough':T('surface texture','tekstur permukaan','表面光滑或粗糙','ملمس السطح'),'wet-dry':T('wetness or dryness','basah atau kering','干湿','البلل أو الجفاف'),'open-closed':T('being open or closed','terbuka atau tertutup','开合状态','الفتح أو الإغلاق'),'full-empty':T('being full or empty','penuh atau kosong','满空状态','الامتلاء أو الفراغ'),'heavy-light':T('story weight','berat dalam cerita','故事中的重量','الوزن في القصة'),'bright-dim':T('brightness','terang atau redup','明暗','شدة الضوء'),'fast-slow':T('story speed','kecepatan dalam cerita','故事中的快慢','السرعة في القصة'),'loud-quiet':T('story sound volume','volume suara dalam cerita','故事中的音量','شدة الصوت في القصة'),'tidy-messy':T('how things are arranged','susunan benda','物品是否整齐','ترتيب الأشياء')}[cid]
 for r in range(4):
  target=[a,b,a,b][r];other=b if target==a else a
  if mode=='clue':
   cue=C[target if r<2 else other]['clue']
   instr={lang:cue[lang]+' '+(T('Choose the describing word that fits this clue.','Pilih kata sifat yang sesuai dengan petunjuk.','选出符合线索的描述词。','اختر كلمة الوصف التي تناسب هذه القرينة.') if r<2 else T('Now choose the opposite describing word.','Sekarang pilih kata sifat yang berlawanan.','现在选出意思相反的描述词。','اختر الآن كلمة الوصف المضادة.'))[lang] for lang in L}
   distract=others[(index*4+r)%len(others)]
   options=[pic(target,'o0'),pic(other,'o1'),pic(distract,'o2')]
   rounds.append(dict(instruction=instr,options=rotate(options,index+r),answer=['o0'],layout='story-choices',semantic={'rule':'adjective-clue','target':target,'clueKey':target if r<2 else other,'opposite':r>=2}))
  else:
   outsider=others[(index*4+r)%len(others)]
   opts=[pic(a,'o0',0),pic(b,'o1',0),pic([a,b][(index+r)%2],'o2',2),pic(outsider,'o3',0)]
   for o in opts:o['dimension']=dims[o['vocabularyKey']]
   instr={lang:T(f'Three cards describe {dimension["en"]}. Choose the one card whose describing words are about something else. Read or listen to every label.',f'Tiga kartu menjelaskan {dimension["id"]}. Pilih satu kartu dengan kata sifat tentang hal lain. Baca atau dengarkan semua label.',f'三张卡描述{dimension["zh"]}。选出描述其他方面的那一张。请阅读或听取每张卡的文字。',f'ثلاث بطاقات تصف {dimension["ar"]}. اختر البطاقة الوحيدة التي تصف شيئا آخر. اقرأ أو استمع إلى جميع الأوصاف.')[lang] for lang in L}
   rounds.append(dict(instruction=instr,options=rotate(opts,index+r),answer=['o3'],layout='story-choices',semantic={'rule':'adjective-odd','dimension':cid,'target':outsider}))
 return rounds

def kindround(mod,k,engine):
 # Safe quotation cards are about choices, comfort, gratitude and clothing; none ranks appearance.
 # A memory face has no caption: never put two quotations on the same artwork.
 keys=['self-choice','neat-clothes','flower-beauty','tidy','clean','fresh','open-book']
 pools=[['self-choice','neat-clothes','flower-beauty','tidy'],['self-choice','neat-clothes','flower-beauty','clean'],['self-choice','neat-clothes','tidy','clean'],['self-choice','flower-beauty','tidy','open-book']]
 keys=pools[(k//4)%4]
 opts=[]
 chosen=rotate(keys,k%4)[:3]
 for j,key in enumerate(chosen):
  o=mod.pic(key,'o'+str(j));o['ariaLabel']=clone(o['label']);o['pictureText']=clone(o['label']);opts.append(o)
 if engine=='memory':return dict(instruction=T('Remember the kind words and picture labels. Find two cards with the same picture and words.','Ingat kata ramah dan label gambar. Cari dua kartu dengan gambar dan kata yang sama.','记住友善的话语和图片标签，找出图片和文字都相同的两张卡。','تذكر الكلمات اللطيفة وأوصاف الصور. ابحث عن بطاقتين لهما الصورة والكلمات نفسها.'),options=opts,answer=[o['id'] for o in opts],semantic={'rule':'quote-memory'})
 unit=[[0,1],[0,0,1],[0,1,1],[0,1,2],[0,0,1,2],[0,1,1,2],[0,1,2,2],[0,0,1,1],[0,1,0,2],[0,1,2,1],[0,1,1,0],[0,0,0,1],[0,1,1,1],[0,0,2,2],[0,2,1,2],[0,1,0,0]][k%16];seq=(unit*3)[:len(unit)*2+1];gap=len(seq)-1
 return dict(instruction=T('Listen to the repeating picture labels and kind words. Which card fills the gap?','Dengarkan label gambar dan kata ramah yang berulang. Kartu mana mengisi bagian kosong?','听听重复的图片标签和友善话语，哪张卡可以填入空缺？','استمع إلى أوصاف الصور والكلمات اللطيفة المتكررة. أي بطاقة تكمل الفراغ؟'),options=rotate(opts,k),answer=['o'+str(seq[gap])],patternItems=[None if j==gap else clone(opts[i])|{'id':'p'+str(j)} for j,i in enumerate(seq)],semantic={'rule':'repeat-pattern','sequence':seq,'gap':gap,'optionIndices':{o['id']:j for j,o in enumerate(opts)}})

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=pathlib.Path,required=True);ap.add_argument('--out',type=pathlib.Path,required=True);args=ap.parse_args();src=args.source;out=args.out;out.mkdir(parents=True,exist_ok=True);(out/'bundles').mkdir(exist_ok=True)
 spec=importlib.util.spec_from_file_location('adjective_source',src/'scripts/curriculum/generate_adjectives.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 result={};originals={}
 for cid in MOTOR+DRAWING:
  originals[cid]=json.loads((src/'content/worksheets'/f'{cid}.json').read_text());data=clone(originals[cid]);original_engine=data[0]['engine'];other='draw' if original_engine=='trace' else 'trace'
  for i in range(12,24):
   block=(i-12)//4;seed=(i-12)%4*4
   engine=['pair','pattern',other][block];kind=['match','pattern',other][block]
   rounds=[pairround(cid,seed+r) if engine=='pair' else patternround(cid,seed+r) if engine=='pattern' else canvasround(cid,seed+r,engine) for r in range(4)]
   data[i]=patch(data[i],engine,kind,rounds)
  result[cid]=data
 for cid,a,b,title in mod.SPECS:
  originals[cid]=json.loads((src/'content/worksheets'/f'{cid}.json').read_text());data=clone(originals[cid])
  if cid=='kind-descriptions':
   for i in range(4,12):
    engine='memory' if i<8 else 'pattern';data[i]=patch(data[i],engine,engine,[kindround(mod,(i-4)*4+r,engine) for r in range(4)])
  else:
   for i in range(8):
    mode='clue' if i<4 else 'odd';data[i]=patch(data[i],'identify','clue' if mode=='clue' else 'odd-one-out',adjective_content(mod,cid,a,b,i%4,mode))
  result[cid]=data
 report={'owner':'creative','categories':{},'semanticAssertions':0,'negativeFixtures':{}}
 for cid,data in result.items():
  base=originals[cid];assert len(data)==24 and [x['id'] for x in data]==[x['id'] for x in base]
  changed=[(i,w) for i,w in enumerate(data) if w!=base[i]];assert len(changed)<=12 and len(changed)>=1
  worksheet_fingerprints=set()
  for i,w in changed:
   assert len(w['rounds'])==4
   assert w['instruction']==w['rounds'][0]['instruction'] and w['options']==w['rounds'][0]['options']
   for field in ['offscreen','note']:
    if field in base[i]:assert w[field]==base[i][field],f'{cid} safety copy changed'
   # Semantic round fingerprints ignore order/id but include the actual content or objective.
   fingerprints=[]
   for r in w['rounds']:
    validate_round(r,w['engine']);report['semanticAssertions']+=1
    fingerprint={'instruction':r['instruction'],'visuals':sorted([json.dumps({k:v for k,v in o.items() if k!='id'},sort_keys=True) for o in r['options']]),'canvas':r.get('canvas'),'pattern':r.get('patternItems')}
    fingerprints.append(json.dumps(fingerprint,sort_keys=True))
   assert len(set(fingerprints))==4,f'{w["id"]}: repeated task'
   worksheet_fingerprint=tuple(sorted(fingerprints))
   assert worksheet_fingerprint not in worksheet_fingerprints,f'{w["id"]}: repeated worksheet task set'
   worksheet_fingerprints.add(worksheet_fingerprint)
  engines=collections.Counter(w['engine'] for w in data);kinds=collections.Counter(inferred(w) for w in data)
  assert len(engines)>=3 and len(kinds)>=4,f'{cid}: insufficient variety'
  report['categories'][cid]={'worksheets':len(data),'rounds':sum(len(w['rounds']) for w in data),'preserved':24-len(changed),'changedIds':[w['id'] for _,w in changed],'engines':dict(engines),'activityKinds':dict(kinds)}
  (out/'bundles'/f'{cid}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
 # Independent corrupted inputs must be rejected by the same semantic gate.
 goodpair=pairround('symmetry',0);badpair=clone(goodpair);badpair['rightOptions'][0]['direction']='down' if badpair['rightOptions'][0]['direction']!='down' else 'up'
 badpat=patternround('trace-shapes',0);badpat['answer']=['o2']
 badlang=pairround('trace-lines',0);del badlang['instruction']['ar']
 badodd=adjective_content(mod,'temperature','hot','cold',0,'odd')[0];badodd['answer']=['o0']
 badmemory=kindround(mod,0,'memory');badmemory['options'][1]['asset']=badmemory['options'][0]['asset']
 fixtures=[('wrong-reflection',badpair,'pair'),('wrong-pattern',badpat,'pattern'),('missing-arabic',badlang,'pair'),('wrong-adjective-outsider',badodd,'identify'),('ambiguous-memory-art',badmemory,'memory')]
 for name,round_,engine in fixtures:
  try:validate_round(round_,engine)
  except (AssertionError,KeyError):report['negativeFixtures'][name]='rejected'
  else:raise AssertionError('negative fixture accepted: '+name)
 report['totalWorksheets']=sum(len(d) for d in result.values());report['changedWorksheets']=sum(24-v['preserved'] for v in report['categories'].values());report['sameCategoryDuplicateChangedWorksheets']=0;report['status']='passed'
 (out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:report[k] for k in ['status','totalWorksheets','changedWorksheets','semanticAssertions','negativeFixtures']}))
if __name__=='__main__':main()
