"""Deterministic formal curriculum variation. Reads source; writes only OUT.
Run: python generate.py [source checkout] [output directory]
The first twelve worksheets in each owned category remain byte-equivalent JSON.
"""
import copy, json, pathlib, sys, hashlib, re
if len(sys.argv)!=3: raise SystemExit('Usage: python generate_formal.py BASELINE_CHECKOUT OUTPUT_DIR')
SRC=pathlib.Path(sys.argv[1])
OUT=pathlib.Path(sys.argv[2])
OUT.mkdir(parents=True,exist_ok=True)
LANGS=['id','en','zh','ar']
def T(id,en,zh,ar): return dict(zip(LANGS,[id,en,zh,ar]))
def same(s): return {l:str(s) for l in LANGS}
def cp(v): return copy.deepcopy(v)
def fmt(t,**kw): return {l:t[l].format(**{k:(v[l] if isinstance(v,dict) else v) for k,v in kw.items()}) for l in LANGS}
def rotate(a,n): n%=len(a); return a[n:]+a[:n]
ASSETS={
 'apple':T('Apel','Apple','苹果','تفاحة'),'hen':T('Ayam','Hen','母鸡','دجاجة'),
 'cloud':T('Awan','Cloud','云','سحابة'),'dog':T('Anjing','Dog','狗','كلب'),
 'bird':T('Burung','Bird','鸟','طائر'),'bus':T('Bus','Bus','公共汽车','حافلة'),
 'flower':T('Bunga','Flower','花','زهرة'),'moon':T('Bulan','Moon','月亮','قمر'),
 'cat':T('Kucing','Cat','猫','قطة'),'rabbit':T('Kelinci','Rabbit','兔子','أرنب'),
 'horse':T('Kuda','Horse','马','حصان'),'butterfly':T('Kupu-kupu','Butterfly','蝴蝶','فراشة'),
 'car':T('Mobil','Car','汽车','سيارة'),'sun':T('Matahari','Sun','太阳','شمس'),
 'bee':T('Lebah','Bee','蜜蜂','نحلة'),'duck':T('Bebek','Duck','鸭子','بطة'),
 'tree':T('Pohon','Tree','树','شجرة'),'boat':T('Perahu','Boat','船','قارب'),
 'carrot':T('Wortel','Carrot','胡萝卜','جزرة'),'train':T('Kereta','Train','火车','قطار'),
 'airplane':T('Pesawat','Airplane','飞机','طائرة'),'dump-truck':T('Truk jungkit','Dump truck','自卸车','شاحنة قلابة')}
SHAPES={
 'circle':T('Lingkaran','Circle','圆形','دائرة'),'square':T('Persegi','Square','正方形','مربع'),
 'triangle':T('Segitiga','Triangle','三角形','مثلث'),'star':T('Bintang','Star','星形','نجمة'),
 'heart':T('Hati','Heart','心形','قلب'),'oval':T('Oval','Oval','椭圆形','شكل بيضاوي'),
 'rectangle':T('Persegi panjang','Rectangle','长方形','مستطيل'),'diamond':T('Belah ketupat','Rhombus','菱形','معين')}
COLORS=[('#EE5261',T('Merah','Red','红色','أحمر')),('#328EE6',T('Biru','Blue','蓝色','أزرق')),('#F4C542',T('Kuning','Yellow','黄色','أصفر')),('#55AE71',T('Hijau','Green','绿色','أخضر')),('#9467D6',T('Ungu','Purple','紫色','بنفسجي')),('#EE8C3D',T('Jingga','Orange','橙色','برتقالي'))]
def glyph(s,id='x',**extra): return dict(id=id,kind='glyph',symbol=str(s),label=same(s),**extra)
def asset(a,id='x',**extra): return dict(id=id,kind='asset',asset=a,label=cp(ASSETS[a]),**extra)
def shape(s,c=0,id='x',**extra):
 color,name=COLORS[c%len(COLORS)]; label=cp(SHAPES[s]); aria=fmt(T('{s}, {c}','{c} {s}','{c}{s}','{s}، {c}'),s=label,c=name)
 return dict(id=id,kind='shape',shape=s,color=color,colorName=cp(name),label=label,ariaLabel=aria,**extra)
def qty(n,id='x',a='apple'):
 label=fmt(T('Kelompok {n} gambar','Group of {n} pictures','{n}个图案的一组','مجموعة من {n} صور'),n=n)
 o=dict(id=id,kind='quantity',value=n,label=label,ariaLabel=cp(label))
 if a:o['groupAsset']=a
 return o
def numbered(opts):
 return [dict(cp(o),id=f'o{i}') for i,o in enumerate(opts)]
def task(kind,engine,instruction,options,answer=None,**extra):
 return dict(activityKind=kind,engine=engine,instruction=instruction,options=options,answer=answer or [],**extra)
def select(kind,instruction,opts,truth,**extra):
 opts=numbered(opts); answer=[o['id'] for o,t in zip(opts,truth) if t]
 return task(kind,'identify',instruction,opts,answer,**extra)
def pair(instruction,left,right=None,kind='match'):
 left=[dict(cp(o),id=f'l{i}') for i,o in enumerate(left)]; right=[dict(cp(o),id=f'r{i}') for i,o in enumerate(right or left)]
 return task(kind,'pair',instruction,left,[],rightOptions=right,pairs=[dict(left=f'l{i}',right=f'r{i}') for i in range(len(left))])
def memory(opts,instruction=None):
 return task('memory','memory',instruction or T('Balik kartu. Ingat letaknya dan temukan pasangan yang sama.','Turn the cards. Remember their places and find identical pairs.','翻开卡片，记住位置，找出相同的配对。','اقلب البطاقات وتذكر أماكنها واعثر على الأزواج المتطابقة.'),numbered(opts))
MATCH=T('Pasangkan gambar yang sama.','Match identical pictures.','配对相同的图片。','طابق الصور المتطابقة.')
MATCH_COLOR=T('Pasangkan warna yang sama. Bentuknya boleh berbeda.','Match the same colors. The shapes may differ.','配对相同的颜色，形状可以不同。','طابق الألوان المتشابهة، حتى لو اختلفت الأشكال.')
MATCH_SHAPE=T('Pasangkan bentuk yang sama. Abaikan warnanya.','Match the same shapes. Ignore their colors.','配对相同的形状，不用管颜色。','طابق الأشكال المتشابهة وتجاهل ألوانها.')
def identity_task(cat,mode,s):
 colorcat=cat in ['colors','color-pairs','memory-colors']; shapecat=cat in ['shapes','shape-pairs','memory-shapes']; shadow=cat=='silhouette-pairs'
 pool=list(range(6)) if colorcat else list(SHAPES) if shapecat else list(ASSETS)[:16]
 values=rotate(pool,s); target=values[0]
 def pic(v,i=0):
  if colorcat:return shape(list(SHAPES)[(s+i)%len(SHAPES)],v)
  if shapecat:return shape(v,s+i)
  return asset(v)
 if mode==0:
  ins=T('Pilih ketiga gambar yang sama dengan contoh.','Choose all three pictures matching the example.','选出与示例相同的全部三张图片。','اختر الصور الثلاث المطابقة للمثال.')
  if colorcat:ins=T('Pilih ketiga bentuk yang warnanya sama dengan contoh.','Choose all three shapes with the same color as the example.','选出与示例颜色相同的全部三个形状。','اختر الأشكال الثلاثة التي لها لون المثال نفسه.')
  if shapecat:ins=T('Pilih ketiga bentuk yang bentuknya sama dengan contoh. Abaikan warna.','Choose all three shapes matching the example. Ignore color.','选出与示例形状相同的全部三个图形，不用管颜色。','اختر الأشكال الثلاثة المطابقة لشكل المثال وتجاهل اللون.')
  opts=[pic(target,i) for i in range(3)]+[pic(values[1],3),pic(values[2],4)]
  reference=pic(target,5)
  if shadow:
   reference['silhouette']=True
   ins=T('Pilih ketiga gambar yang cocok dengan bayangan contoh.','Choose all three pictures that match the example shadow.','选出与示例影子相匹配的全部三张图片。','اختر الصور الثلاث التي تطابق ظل المثال.')
  return select('choose-many',ins,opts,[1,1,1,0,0],reference=reference)
 if mode==1:
  feature=T('gambar','picture','图案','الصورة')
  if colorcat:feature=T('warna','color','颜色','اللون')
  if shapecat:feature=T('bentuk','shape','形状','الشكل')
  ins=fmt(T('Tiga kartu memiliki {f} yang sama. Pilih satu yang berbeda.','Three cards share the same {f}. Choose the one that differs.','三张卡片的{f}相同，选出唯一不同的一张。','ثلاث بطاقات تشترك في {f}. اختر البطاقة الوحيدة المختلفة.'),f=feature)
  opts=[pic(target,i) for i in range(3)]+[pic(values[1],3)]
  if shadow:
   opts=[dict(o,silhouette=True) for o in opts]
   ins=T('Tiga bayangan menunjukkan benda yang sama. Pilih satu bayangan benda yang berbeda.','Three shadows show the same object. Choose the one shadow of a different object.','三个影子表示同一种物体，选出唯一不同物体的影子。','ثلاثة ظلال تمثل الشيء نفسه. اختر الظل الوحيد لشيء مختلف.')
  return select('odd-one-out',ins,opts,[0,0,0,1])
 if mode==2:
  left=[pic(v,i) for i,v in enumerate(values[:3])]; right=[pic(v,i+3) for i,v in enumerate(values[:3])]
  if shadow:
   right=[dict(o,silhouette=True) for o in right]
   return pair(T('Pasangkan setiap gambar dengan bayangannya.','Match each picture to its shadow.','把每张图片与它的影子配对。','طابق كل صورة مع ظلها.'),left,right,'shadow-match')
  return pair(MATCH_COLOR if colorcat else MATCH_SHAPE if shapecat else MATCH,left,right)
 return memory([shape('circle',v) if colorcat else dict(pic(v),silhouette=True) if shadow else pic(v) for v in values[:3]])

MEASURES={'size':('scale',T('ukuran','size','大小','الحجم')),'length':('width',T('panjang','length','长度','الطول')),'height':('height',T('tinggi','height','高度','الارتفاع')),'thickness':('strokeWidth',T('ketebalan','thickness','粗细','السماكة'))}
def measurement(cat,n,c=0):
 measure,word=MEASURES[cat]; color,name=COLORS[c%6]
 label=fmt(T('Contoh {w}, tingkat {n}','{w} sample, level {n}','{w}示例，第{n}级','نموذج {w}، المستوى {n}'),w=word,n=round(n*10))
 return dict(id='x',kind='measurement',measure=measure,value=n,shape='circle' if measure=='scale' else 'bar',scale=n if measure=='scale' else 1,color=color,colorName=cp(name),label=label,ariaLabel=fmt(T('{c}. {v}','{c}. {v}','{c}，{v}','{c}. {v}'),c=name,v=label))
def measurement_task(cat,mode,s):
 vals=rotate([.25,.45,.65,.85],s); n=vals[0]; word=MEASURES[cat][1]
 if mode==0:
  ins=fmt(T('Pilih ketiga gambar dengan {w} yang sama seperti contoh. Abaikan warna.','Choose all three pictures with the same {w} as the example. Ignore color.','选出与示例{w}相同的全部三张图片，不用管颜色。','اختر الصور الثلاث التي لها {w} المثال نفسه وتجاهل اللون.'),w=word)
  return select('choose-many',ins,[measurement(cat,n,s+i) for i in range(3)]+[measurement(cat,vals[1],s+3)],[1,1,1,0],reference=measurement(cat,n,s+4))
 if mode==1:
  ins=fmt(T('Tiga gambar memiliki {w} yang sama. Mana satu yang berbeda? Abaikan warna.','Three pictures have the same {w}. Which one differs? Ignore color.','三张图片的{w}相同，哪张不同？不用管颜色。','ثلاث صور لها {w} نفسه. أي صورة تختلف؟ تجاهل اللون.'),w=word)
  return select('odd-one-out',ins,[measurement(cat,n,s+i) for i in range(3)]+[measurement(cat,vals[1],s+3)],[0,0,0,1])
 if mode==2:
  return pair(fmt(T('Pasangkan {w} yang sama. Abaikan warna.','Match equal {w}. Ignore color.','配对{w}相同的图片，不用管颜色。','طابق الصور المتساوية في {w} وتجاهل اللون.'),w=word),[measurement(cat,v,s) for v in vals[:3]],[measurement(cat,v,s+1) for v in vals[:3]])
 desc=bool(s%2); opts=numbered([measurement(cat,v,s) for v in vals[:3]])
 ins=fmt(T('Urutkan menurut {w}, dari {order}.','Order by {w}, from {order}.','按{w}排列，{order}。','رتب حسب {w}، من {order}.'),w=word,order=T('besar ke kecil','greatest to least','从大到小','الأكبر إلى الأصغر') if desc else T('kecil ke besar','least to greatest','从小到大','الأصغر إلى الأكبر'))
 return task('sequence','sequence',ins,opts,[o['id'] for o in sorted(opts,key=lambda o:o['value'],reverse=desc)])

DIRECTIONS=[('up',0,T('atas','up','上','الأعلى')),('right',90,T('kanan','right','右','اليمين')),('down',180,T('bawah','down','下','الأسفل')),('left',270,T('kiri','left','左','اليسار')),('up-right',45,T('kanan atas','up and right','右上','أعلى اليمين')),('down-right',135,T('kanan bawah','down and right','右下','أسفل اليمين')),('down-left',225,T('kiri bawah','down and left','左下','أسفل اليسار')),('up-left',315,T('kiri atas','up and left','左上','أعلى اليسار'))]
def arrow(v,c=0):
 d,rot,label=DIRECTIONS[v%len(DIRECTIONS)]; o=shape('triangle',c); o.update(kind='arrow',shape='arrow',direction=d,rotation=rot,label=fmt(T('Panah ke {d}','Arrow pointing {d}','向{d}箭头','سهم نحو {d}'),d=label)); o['ariaLabel']=cp(o['label']); return o
def direction_task(mode,s):
 n=s%4
 if mode==0:return select('choose-many',fmt(T('Pilih ketiga panah yang mengarah ke {d}.','Choose all three arrows pointing {d}.','选出全部三个向{d}的箭头。','اختر الأسهم الثلاثة المتجهة إلى {d}.'),d=DIRECTIONS[n][2]),[arrow(n,s+i) for i in range(3)]+[arrow(n+1,s+3)],[1,1,1,0])
 if mode==1:return select('odd-one-out',T('Tiga panah mengarah ke arah yang sama. Pilih satu yang berbeda arah.','Three arrows point the same way. Choose the one pointing a different way.','三个箭头指向同一方向，选出方向不同的一个。','ثلاثة أسهم تشير إلى الاتجاه نفسه. اختر السهم الذي يشير إلى اتجاه مختلف.'),[arrow(n,s+i) for i in range(3)]+[arrow(n+1,s+3)],[0,0,0,1])
 count=2+s//4
 if mode==2:return pair(T('Pasangkan panah yang mengarah ke arah yang sama.','Match arrows pointing in the same direction.','配对方向相同的箭头。','طابق الأسهم التي تشير إلى الاتجاه نفسه.'),[arrow(s+i,0) for i in range(count)],[arrow(s+i,1) for i in range(count)])
 return memory([arrow(s+i,0) for i in range(count)])

POSITIONS=[('top-left','↖',T('kiri atas','top left','左上','أعلى اليسار')),('top-center','↑',T('tengah atas','top center','上中','أعلى الوسط')),('top-right','↗',T('kanan atas','top right','右上','أعلى اليمين')),('middle-left','←',T('kiri tengah','middle left','左中','وسط اليسار')),('center','⊙',T('tengah','center','正中','الوسط')),('middle-right','→',T('kanan tengah','middle right','右中','وسط اليمين')),('bottom-left','↙',T('kiri bawah','bottom left','左下','أسفل اليسار')),('bottom-center','↓',T('tengah bawah','bottom center','下中','أسفل الوسط')),('bottom-right','↘',T('kanan bawah','bottom right','右下','أسفل اليمين'))]
def position_task(mode,s):
 if mode<2:
  a=list(ASSETS)[s%len(ASSETS)]; opts=[dict(asset(a,f'p{i}'),position=p,ariaLabel=fmt(T('{a}, {p}','{a}, {p}','{p}的{a}','{a}، {p}'),a=ASSETS[a],p=label)) for i,(p,sy,label) in enumerate(POSITIONS)]
  if mode==0:
   groups=[([0,1,2],T('baris atas','top row','最上面一行','الصف العلوي')),([6,7,8],T('baris bawah','bottom row','最下面一行','الصف السفلي')),([0,3,6],T('kolom kiri','left column','最左边一列','العمود الأيسر')),([2,5,8],T('kolom kanan','right column','最右边一列','العمود الأيمن'))]
   indexes,label=groups[s%4]
   return task('choose-many','identify',fmt(T('Pilih ketiga gambar di {p}.','Choose all three pictures in the {p}.','选出{p}的全部三张图片。','اختر الصور الثلاث في {p}.'),p=label),opts,[f'p{i}' for i in indexes],layout='fixed-3-by-3')
  i=[0,2,6,8][s%4]; label=POSITIONS[i][2]
  return task('clue','identify',fmt(T('Aku berada di sudut {p}. Pilih aku.','I am in the {p} corner. Choose me.','我在{p}角。选出我。','أنا في زاوية {p}. اخترني.'),p=label),opts,[f'p{i}'],layout='fixed-3-by-3')
 if mode==2:
  positions=rotate(POSITIONS,s)[:3]
  left=[dict(glyph(sy),label=cp(label)) for p,sy,label in positions]
  return pair(T('Panah menunjukkan letak dari tengah. Pasangkan penanda letak yang sama.','Arrows show a position from the center. Match identical position markers.','箭头表示从中心看去的位置。配对相同的位置标记。','تشير الأسهم إلى الموضع انطلاقا من الوسط. طابق علامات المواضع المتشابهة.'),left)
 index=[[0,2,6,8],[1,3,5,7],[4,0,5,7]][s//4][s%4]
 p,sy,label=POSITIONS[index]; x=[80,200,320][index%3]; y=[70,150,230][index//3]
 form=SHAPES[['circle','square','triangle'][s//4]]
 ins=fmt(T('Gambar bentuk {f} kecil di {p} bidang. Titik adalah petunjuk letaknya.','Draw a small {f} at the {p} of the page. The dot marks the place.','在画面的{p}画一个小{f}。小点标出了位置。','ارسم شكل {f} صغيرا في {p} الصفحة. تحدد النقطة الموضع.'),p=label,f=form)
 return task('draw','draw',ins,[],[],canvas={'viewBox':[0,0,400,300],'guide':[dict(kind='line',x1=200,y1=10,x2=200,y2=290,dashed=True),dict(kind='line',x1=10,y1=150,x2=390,y2=150,dashed=True),dict(kind='circle',cx=x,cy=y,r=3,fill='#73955c')]},completion={'mode':'self-review','goals':[ins]})

def letter_task(cat,mode,s):
 vowel=cat=='vowels'; consonant=cat=='consonants'; case=cat=='letter-case'; lower=cat=='lowercase-pairs'
 pool=list('AEIOU') if vowel else list('BCDFGHJKLMNPRSTV') if consonant else list('ABDEFGHLMNRT')
 vals=rotate(pool,s); target=vals[:3]
 if lower:target=[v.lower() for v in target]
 if mode in [0,1]:
  if vowel or consonant:
   bad=('BCDF'[s%4] if vowel else 'AEIOU'[s%5]); goods=target
   name=T('vokal Latin A, E, I, O, U','Latin vowels A, E, I, O, U','拉丁元音字母A、E、I、O、U','حروف العلة اللاتينية A، E، I، O، U') if vowel else T('konsonan Latin (bukan A, E, I, O, U)','Latin consonants (not A, E, I, O, U)','拉丁辅音字母（不是A、E、I、O、U）','الحروف اللاتينية الساكنة (ليست A، E، I، O، U)')
  else:
   goods=target; bad=vals[3].upper() if lower else vals[3].lower(); name=T('huruf kecil Latin','lowercase Latin letters','小写拉丁字母','الحروف اللاتينية الصغيرة') if lower else T('huruf besar Latin','uppercase Latin letters','大写拉丁字母','الحروف اللاتينية الكبيرة')
  ins=fmt(T('Pilih ketiga {f}.','Choose all three {f}.','选出全部三个{f}。','اختر {f} الثلاثة.'),f=name) if mode==0 else fmt(T('Tiga kartu adalah {f}. Pilih satu yang bukan.','Three cards are {f}. Choose the one that is not.','三张卡片是{f}。选出唯一不属于的一张。','ثلاث بطاقات هي {f}. اختر البطاقة الوحيدة التي ليست منها.'),f=name)
  return select('choose-many' if mode==0 else 'odd-one-out',ins,[glyph(v) for v in goods+[bad]],[1,1,1,0] if mode==0 else [0,0,0,1])
 if mode==2:
  return pair(T('Pasangkan setiap huruf besar dengan huruf kecilnya.','Match each uppercase letter to its lowercase form.','把每个大写字母与对应的小写字母配对。','طابق كل حرف كبير مع شكله الصغير.') if case else T('Pasangkan huruf yang sama.','Match identical letters.','配对相同的字母。','طابق الحروف المتشابهة.'),[glyph(v) for v in target],[glyph(v.lower() if case else v) for v in target])
 return memory([glyph(v) for v in target],T('Ingat kartu huruf dan temukan pasangan yang sama. Ucapkan hurufnya.','Remember the letter cards and find identical pairs. Say each letter.','记住字母卡片，找出相同的配对，并说出字母。','تذكر بطاقات الحروف واعثر على الأزواج المتشابهة ثم انطق كل حرف.'))

INITIAL_GROUPS=[['apple','hen','cloud','dog'],['bird','bus','flower','moon','duck'],['cat','rabbit','horse','butterfly']]
def initial_task(mode,s):
 group=rotate(INITIAL_GROUPS[s%3],s//3); target=ASSETS[group[0]]['id'][0]; bad=INITIAL_GROUPS[(s+1)%3][s%4]
 if mode<2:
  ins=fmt(T('Pilih ketiga gambar dengan nama Indonesia berawalan {l}.','Choose all three pictures whose Indonesian names begin with {l}.','选出印度尼西亚语名称以{l}开头的全部三张图片。','اختر الصور الثلاث التي تبدأ أسماؤها باللغة الإندونيسية بالحرف {l}.'),l=target) if mode==0 else fmt(T('Tiga nama Indonesia berawalan {l}. Nama gambar mana yang tidak?','Three Indonesian names begin with {l}. Which picture name does not?','三个印度尼西亚语名称以{l}开头，哪张图片的名称不是？','ثلاثة أسماء إندونيسية تبدأ بالحرف {l}. أي اسم صورة لا يبدأ به؟'),l=target)
  return select('choose-many' if mode==0 else 'odd-one-out',ins,[asset(v) for v in group[:3]+[bad]],[1,1,1,0] if mode==0 else [0,0,0,1],languageOfTask='id')
 picks=[g[s%len(g)] for g in INITIAL_GROUPS]
 if mode==2:
  r=pair(T('Baca nama Indonesia. Pasangkan gambar dengan huruf awal namanya.','Read the Indonesian names. Match each picture to its beginning letter.','读印度尼西亚语名称，把每张图片与名称的首字母配对。','اقرأ الأسماء الإندونيسية وطابق كل صورة مع الحرف الأول من اسمها.'),[asset(v) for v in picks],[glyph(ASSETS[v]['id'][0]) for v in picks]);r['languageOfTask']='id';return r
 r=memory([asset(v) for v in picks],T('Cari pasangan gambar. Ucapkan nama Indonesia dan huruf awalnya.','Find the picture pairs. Say each Indonesian name and its first letter.','找出图片配对，说出印度尼西亚语名称及首字母。','اعثر على أزواج الصور وانطق الاسم الإندونيسي والحرف الأول منه.'));r['languageOfTask']='id';return r

NUMBER_CATS=['count-to-5','count-to-10','count-6-to-15','quantity-pairs','compare-quantity','math-more-less','math-equal','ascending','descending','missing-number','number-neighbors','number-pairs','vehicle-count','build-blocks','growing-pattern']
ARITHMETIC=['add-to-5','add-to-10','subtract-to-5','subtract-to-10','math-stories']
def num_range(cat):return list(range(6,16)) if cat=='count-6-to-15' else list(range(1,6)) if cat=='count-to-5' else list(range(1,7)) if cat=='vehicle-count' else list(range(1,10))
def number_task(cat,mode,s):
 nums=num_range(cat); vals=rotate(nums,s); n=vals[0]; low=cat=='count-6-to-15'
 objects=['car','bus','boat','train','airplane','dump-truck'] if cat=='vehicle-count' else [None] if cat=='build-blocks' else ['apple','carrot','duck','flower']
 a=objects[s%len(objects)]; comparison=cat in ['compare-quantity','math-more-less','build-blocks']; ordering=cat in ['ascending','descending','missing-number','number-neighbors','growing-pattern']
 if mode==0:
  if comparison:
   n=1+s; ns=[n+1,n+2,n+3,n-1]; ins=fmt(T('Pilih ketiga kelompok yang lebih banyak dari {n}.','Choose all three groups with more than {n} pictures.','选出数量比{n}多的全部三组。','اختر المجموعات الثلاث التي تحتوي على أكثر من {n} صور.'),n=n)
  elif ordering:
   n=1+s%5; ns=[n+1,n+2,n+3,n+5]; ins=fmt(T('Kita menghitung naik dari {n}. Pilih tiga jumlah berikutnya: {x}, {y}, {z}.','Count up from {n}. Choose the next three quantities: {x}, {y}, {z}.','从{n}往上数。选出接下来的三个数量：{x}、{y}、{z}。','عد تصاعديا من {n}. اختر الكميات الثلاث التالية: {x}، {y}، {z}.'),n=n,x=n+1,y=n+2,z=n+3)
   if cat=='descending':
    n=5+s%5;ns=[n-1,n-2,n-3,n+1];ins=fmt(T('Kita menghitung turun dari {n}. Pilih tiga jumlah berikutnya: {x}, {y}, {z}.','Count down from {n}. Choose the next three quantities: {x}, {y}, {z}.','从{n}往下数。选出接下来的三个数量：{x}、{y}、{z}。','عد تنازليا من {n}. اختر الكميات الثلاث التالية: {x}، {y}، {z}.'),n=n,x=n-1,y=n-2,z=n-3)
  else:ns=[n,n,n,vals[1]];ins=fmt(T('Hitung setiap kelompok. Pilih ketiga kelompok berisi tepat {n} gambar.','Count each group. Choose all three groups with exactly {n} pictures.','数一数每组，选出恰好有{n}个图案的全部三组。','عد كل مجموعة واختر المجموعات الثلاث التي تحتوي على {n} صور بالضبط.'),n=n)
  return select('choose-many',ins,[qty(v,a=objects[(s+i)%len(objects)]) for i,v in enumerate(ns)],[1,1,1,0])
 if mode==1:
  if ordering:
   n=1+s%5;ns=[n,n+1,n+2,n+4]
   ins=fmt(T('Cari angka dari {n} sampai {end}. Pilih satu jumlah yang di luar rentang itu.','Look for numbers from {n} through {end}. Choose the one quantity outside that range.','找出从{n}到{end}的数量。选出唯一不在范围内的一组。','ابحث عن الأعداد من {n} إلى {end}. اختر الكمية الوحيدة خارج هذا النطاق.'),n=n,end=n+2)
  else:ns=[n,n,n,vals[1]];ins=fmt(T('Tiga kelompok masing-masing berisi {n} gambar. Pilih satu yang tidak sama banyak.','Three groups each have {n} pictures. Choose the one with a different quantity.','三组各有{n}个图案。选出唯一数量不同的一组。','ثلاث مجموعات تحتوي كل منها على {n} صور. اختر المجموعة الوحيدة ذات العدد المختلف.'),n=n)
  return select('odd-one-out',ins,[qty(v,a=objects[(s+i)%len(objects)]) for i,v in enumerate(ns)],[0,0,0,1])
 if mode==2:
  values=vals[:3]
  if ordering:
   n=1+s%5;values=[n,n+1,n+2];delta=-1 if cat=='descending' else 1
   return pair(T('Pasangkan setiap jumlah dengan angka satu lebih sedikit.','Match each quantity to the number that is one less.','把每组数量与小一的数字配对。','طابق كل كمية مع العدد الأقل منها بواحد.') if delta<0 else T('Pasangkan setiap jumlah dengan angka satu lebih banyak.','Match each quantity to the number that is one more.','把每组数量与大一的数字配对。','طابق كل كمية مع العدد الأكبر منها بواحد.'),[qty(v,a=a) for v in values],[glyph(v+delta,value=v+delta) for v in values])
  return pair(T('Hitung gambar. Pasangkan setiap kelompok dengan angkanya.','Count the pictures. Match each group to its numeral.','数一数图案，把每组与对应的数字配对。','عد الصور وطابق كل مجموعة مع رقمها.'),[qty(v,a=a) for v in values],[glyph(v,value=v) for v in values])
 desc=cat=='descending' or (comparison and s%2==1)
 values=vals[:3]
 if ordering:values=[1+s%5+i*(2 if cat=='growing-pattern' and s%2 else 1) for i in range(3)]
 opts=numbered([qty(v,a=a) for v in values])
 ins=T('Hitung, lalu urutkan kelompok dari paling banyak ke paling sedikit.','Count, then order the groups from most to fewest.','数一数，再把各组按数量从多到少排列。','عد ثم رتب المجموعات من الأكثر إلى الأقل.') if desc else T('Hitung, lalu urutkan kelompok dari paling sedikit ke paling banyak.','Count, then order the groups from fewest to most.','数一数，再把各组按数量从少到多排列。','عد ثم رتب المجموعات من الأقل إلى الأكثر.')
 return task('sequence','sequence',ins,opts,[o['id'] for o in sorted(opts,key=lambda o:o['value'],reverse=desc)])

def arithmetic_values(cat,s):
 limit=5 if cat.endswith('-5') else 10
 subtract=cat.startswith('subtract') or (cat=='math-stories' and s%2)
 if subtract:
  a=3+s%(limit-2);b=1+(s//2)%(a-1);return a,b,a-b,'subtract'
 a=1+s%(limit-1);b=1+(s//3)%(limit-a);return a,b,a+b,'add'
def arithmetic_task(cat,mode,s):
 a,b,n,op=arithmetic_values(cat,s); sign='−' if op=='subtract' else '+'; expr=f'{a} {sign} {b}'
 if mode==0:
  ins=fmt(T('Hitung {e}. Pilih ketiga kelompok yang jumlahnya sama dengan hasilnya.','Solve {e}. Choose all three groups equal to the answer.','计算{e}，选出数量等于答案的全部三组。','احسب {e}. اختر المجموعات الثلاث التي يساوي عددها الناتج.'),e=expr)
  return select('choose-many',ins,[qty(n,a=v) for v in ['apple','carrot','duck']]+[qty(n+1,a='flower')],[1,1,1,0])
 if mode==1:
  ins=fmt(T('Hitung {e}. Tiga kelompok menunjukkan hasilnya. Pilih satu yang tidak.','Solve {e}. Three groups show the answer. Choose the one that does not.','计算{e}。三组的数量等于答案，选出唯一不等于的一组。','احسب {e}. ثلاث مجموعات تمثل الناتج. اختر المجموعة الوحيدة التي لا تمثله.'),e=expr)
  return select('odd-one-out',ins,[qty(n,a=v) for v in ['apple','carrot','duck']]+[qty(n+1,a='flower')],[0,0,0,1])
 if mode==2:
  limit=5 if cat.endswith('-5') else 10; base=3+s%(limit-2)
  eq=[(min(limit,v+1+s%2),min(limit,v+1+s%2)-v,v) for v in rotate(list(range(limit)),s)[:3]] if op=='subtract' else [(1,v-1,v) for v in rotate(list(range(1,limit+1)),s)[:3]]
  left=[]
  for x,y,z in eq:
   o=glyph(f'{x}{sign}{y}',scale=.58)
   o['label']=fmt(T('{a} dikurangi {b}','{a} minus {b}','{a}减{b}','{a} ناقص {b}') if op=='subtract' else T('{a} ditambah {b}','{a} plus {b}','{a}加{b}','{a} زائد {b}'),a=x,b=y);left.append(o)
  return pair(T('Selesaikan setiap hitungan, lalu pasangkan dengan kelompok hasilnya.','Solve each calculation, then match it to the group showing its answer.','完成每个计算，再与表示答案的数量组配对。','حل كل عملية ثم طابقها مع المجموعة التي تمثل ناتجها.'),left,[qty(z,a='apple') for x,y,z in eq])
 ins=fmt(T('Ada {a} gambar. Ambil {b}. Berapa yang tersisa?','There are {a} pictures. Take away {b}. How many remain?','有{a}个图案，拿走{b}个，还剩几个？','هناك {a} صور. أزل {b}. كم بقي؟') if op=='subtract' else T('Ada {a} gambar. Tambahkan {b}. Berapa semuanya?','There are {a} pictures. Add {b}. How many altogether?','有{a}个图案，再加{b}个，一共有几个？','هناك {a} صور. أضف {b}. كم المجموع؟'),a=a,b=b)
 choices=sorted(set([n,max(0,n-1),n+1,n+2]))
 return task('clue','count',ins,[glyph(v,id=f'n{v}',value=v) for v in choices],[f'n{n}'],operation=op,operands=[a,b],expression=expr+' = ?',countTarget=n,countAsset=['apple','carrot','duck','flower'][s%4])

MOTIFS=[('○','△'),('□','☆'),('♡','◇'),('△','□'),('☆','○'),('◇','♡')]
def pattern_glyph(seq):
 o=glyph(''.join(seq),scale=max(.25,min(.6,1.7/len(seq))))
 names={'○':SHAPES['circle'],'△':SHAPES['triangle'],'□':SHAPES['square'],'☆':SHAPES['star'],'♡':SHAPES['heart'],'◇':SHAPES['diamond']}
 o['label']={l:', '.join(names[v][l] for v in seq) for l in LANGS};o['ariaLabel']=cp(o['label']);return o
def pattern_unit(cat,s):
 a,b=MOTIFS[s%len(MOTIFS)]
 if cat=='pattern-abc':return [a,b, next(x for x in ['○','△','□','☆','♡','◇'] if x not in [a,b])]
 if cat=='pattern-aab-abb':return [a,a,b] if s%2==0 else [a,b,b]
 return [a,b]
def pattern_task(cat,mode,s):
 unit=pattern_unit(cat,s);name='ABC' if cat=='pattern-abc' else 'AAB' if len(unit)==3 and unit[0]==unit[1] else 'ABB' if len(unit)==3 else 'AB'
 rule=fmt(T('Pola {p}: ulangi {u}.','{p} pattern: repeat {u}.','{p}规律：重复{u}。','نمط {p}: كرر {u}.'),p=name,u=pattern_glyph(unit)['label'])
 good=[unit*2,unit*3,unit*2+unit[:1]];bad=unit*2;bad[-1]=unit[0] if unit[-1]!=unit[0] else unit[-2]
 if mode<2:
  ins={l:rule[l]+' '+T('Pilih ketiga deret yang mengikuti pola itu.','Choose all three strips that follow this pattern.','选出遵循这个规律的全部三条。','اختر السلاسل الثلاث التي تتبع هذا النمط.')[l] for l in LANGS} if mode==0 else {l:rule[l]+' '+T('Pilih satu deret yang melanggar pola.','Choose the one strip that breaks the pattern.','选出唯一不符合规律的一条。','اختر السلسلة الوحيدة التي تخالف النمط.')[l] for l in LANGS}
  return select('choose-many' if mode==0 else 'odd-one-out',ins,[pattern_glyph(v) for v in good+[bad]],[1,1,1,0] if mode==0 else [0,0,0,1])
 if mode==2:
  units=[pattern_unit(cat,s+i) for i in range(3)]
  return pair(T('Pasangkan deret dengan bagian pendek yang berulang di dalamnya.','Match each strip to the short unit that repeats in it.','把每条规律与其中重复的短单元配对。','طابق كل سلسلة مع الوحدة القصيرة التي تتكرر فيها.'),[pattern_glyph(u*2) for u in units],[pattern_glyph(u) for u in units])
 seq=unit*3;missing=1+s%(len(seq)-1);target=seq[missing];shape_lookup={'○':'circle','△':'triangle','□':'square','☆':'star','♡':'heart','◇':'diamond'}
 opts=numbered([shape(shape_lookup[v],0) for v in dict.fromkeys(unit+['◇','☆'])]);answer=[o['id'] for o in opts if o['shape']==shape_lookup[target]]
 items=[None if i==missing else shape(shape_lookup[v],0,id=f'p{i}') for i,v in enumerate(seq)]
 return task('clue','pattern',{l:rule[l]+' '+T('Bentuk mana yang hilang di tempat tanda tanya?','Which shape is missing at the question mark?','问号处缺少哪个形状？','ما الشكل الناقص عند علامة الاستفهام؟')[l] for l in LANGS},opts,answer,patternItems=items)

def make_round(cat,mode,s):
 if cat in MEASURES:return measurement_task(cat,mode,s)
 if cat=='positions':return position_task(mode,s)
 if cat=='directions':return direction_task(mode,s)
 if cat in ['vowels','consonants','uppercase-pairs','lowercase-pairs','letter-case']:return letter_task(cat,mode,s)
 if cat=='initial-letters':return initial_task(mode,s)
 if cat in NUMBER_CATS:return number_task(cat,mode,s)
 if cat in ARITHMETIC:return arithmetic_task(cat,mode,s)
 if cat.startswith('pattern-'):return pattern_task(cat,mode,s)
 return identity_task(cat,mode,s)

def infer_kind(w):
 if 'activityKind'in w:return w['activityKind']
 e=w['engine'];cat=w['category']
 if e=='pair':return 'shadow-match' if cat=='silhouette-pairs' else 'match'
 if e in ['count','pattern','sequence','memory','trace','draw','sort']:return e
 return 'choose-many' if len(w.get('answer',[]))>1 else 'choose-one'

def visual_key(o):return tuple(o.get(k) for k in ['asset','shape','color','symbol','value','scale','rotation','silhouette','groupAsset'])
def fulltext(t):return isinstance(t,dict) and all(isinstance(t.get(l),str) and t[l] for l in LANGS)
def validate_round(r,cat):
 assert fulltext(r['instruction']), 'instruction translation'
 opts=r['options'];ids=[o['id'] for o in opts]
 assert len(set(ids))==len(ids),'unique option ids'
 assert all(x in ids for x in r['answer']),'answer exists'
 for o in opts+r.get('rightOptions',[])+[x for x in r.get('patternItems',[]) if x]+([r['reference']] if r.get('reference') else []):
  assert fulltext(o['label']),'label translation'
  if o.get('kind') in ['quantity','measurement','arrow'] or o.get('colorName') or o.get('position'):assert fulltext(o.get('ariaLabel')),'descriptive aria translation'
  if o.get('kind')=='quantity':assert str(o['value']) in o['label']['en'],'quantity label'
 if r['activityKind']=='choose-many':assert len(r['answer'])>=3 and len(opts)>len(r['answer']),'three-plus selection'
 if r['activityKind'] in ['odd-one-out','clue'] and r['engine'] not in ['draw','pair']:assert len(r['answer'])==1,'unique excluded or clue answer'
 if r['engine']=='pair':
  right=[o['id'] for o in r['rightOptions']];pairs=r['pairs']
  assert len(pairs)==len(opts)==len(right),'complete pair map'
  assert set(p['left'] for p in pairs)==set(ids),'left bijection'
  assert set(p['right'] for p in pairs)==set(right),'right bijection'
  assert len({visual_key(o) for o in opts})==len(opts),'left visually unique'
  assert len({visual_key(o) for o in r['rightOptions']})==len(right),'right visually unique'
 if r['engine']=='memory':assert 2<=len(opts)<=4 and len({visual_key(o) for o in opts})==len(opts),'memory distinctness'
 if r['engine']=='sequence':assert sorted(ids)==sorted(r['answer']),'sequence coverage'
 if r.get('layout')=='fixed-3-by-3':assert [o['position'] for o in opts]==[p[0] for p in POSITIONS],'fixed grid positions'
 if cat in ['uppercase-pairs','lowercase-pairs'] and r['engine']=='pair':
  for o in opts+r['rightOptions']:assert o['symbol'].isupper() if cat=='uppercase-pairs' else o['symbol'].islower(),'case curriculum'
 if r.get('operation'):
  a,b=r['operands'];v=a-b if r['operation']=='subtract' else a+b
  assert r['countTarget']==v,'arithmetic quantity'
  assert [o['value'] for o in opts if o['id'] in r['answer']]==[v],'arithmetic answer'

def validate_semantics(r,cat):
 validate_round(r,cat)
 kind=r['activityKind'];opts=r['options'];ans=set(r['answer'])
 if kind in ['choose-many','odd-one-out'] and cat in ['colors','color-pairs','memory-colors','shapes','shape-pairs','memory-shapes','same-different','object-pairs','silhouette-pairs','memory-objects']:
  field='color' if cat in ['colors','color-pairs','memory-colors'] else 'shape' if cat in ['shapes','shape-pairs','memory-shapes'] else 'asset'
  target=opts[0][field];expect={o['id'] for o in opts if (o[field]==target)==(kind=='choose-many')};assert ans==expect,'identity truth'
 if kind in ['choose-many','odd-one-out'] and cat in MEASURES:
  target=opts[0]['value'];assert ans=={o['id'] for o in opts if (o['value']==target)==(kind=='choose-many')},'measurement truth'
 if kind in ['choose-many','odd-one-out'] and cat=='directions':
  target=opts[0]['direction'];assert ans=={o['id'] for o in opts if (o['direction']==target)==(kind=='choose-many')},'direction truth'
 if cat in ['vowels','consonants'] and kind in ['choose-many','odd-one-out']:
  eligible=lambda o:(o['symbol'] in 'AEIOU')==(cat=='vowels')
  assert ans=={o['id'] for o in opts if eligible(o)==(kind=='choose-many')},'letter class truth'
 if cat in ['uppercase-pairs','lowercase-pairs','letter-case'] and kind in ['choose-many','odd-one-out']:
  eligible=lambda o:o['symbol'].islower() if cat=='lowercase-pairs' else o['symbol'].isupper()
  assert ans=={o['id'] for o in opts if eligible(o)==(kind=='choose-many')},'letter case truth'
 if cat=='initial-letters' and kind in ['choose-many','odd-one-out']:
  initial=opts[0]['label']['id'][0];assert ans=={o['id'] for o in opts if (o['label']['id'][0]==initial)==(kind=='choose-many')},'initial truth'
 if r['engine']=='sequence' and cat in NUMBER_CATS+list(MEASURES):
  values=[next(o['value'] for o in opts if o['id']==i) for i in r['answer']]
  assert len(set(values))==len(values) and (values==sorted(values) or values==sorted(values,reverse=True)),'numeric ordering'
 if r['engine']=='pair' and cat in NUMBER_CATS:
  for p in r['pairs']:
   l=next(o for o in opts if o['id']==p['left']);rr=next(o for o in r['rightOptions'] if o['id']==p['right'])
   delta=-1 if cat=='descending' else 1 if cat in ['ascending','missing-number','number-neighbors','growing-pattern'] else 0
   assert rr['value']==l['value']+delta,'numeric pair truth'
 if r['engine']=='pair' and cat in ARITHMETIC:
  for p in r['pairs']:
   l=next(o for o in opts if o['id']==p['left']);rr=next(o for o in r['rightOptions'] if o['id']==p['right']);sy=l['symbol']
   x,y=map(int,sy.split('−' if '−' in sy else '+'));assert rr['value']==(x-y if '−' in sy else x+y),'arithmetic pair truth'
 if cat in ARITHMETIC and kind in ['choose-many','odd-one-out']:
  x,sign,y=re.search(r'Solve (\d+) ([+−]) (\d+)',r['instruction']['en']).groups();result=int(x)+int(y) if sign=='+' else int(x)-int(y)
  assert ans=={o['id'] for o in opts if (o['value']==result)==(kind=='choose-many')},'arithmetic selection truth'
 if cat in NUMBER_CATS and kind in ['choose-many','odd-one-out']:
  ins=r['instruction']['en'];expect=None
  if 'more than' in ins:
   n=int(re.search(r'more than (\d+)',ins)[1]);expect={o['id'] for o in opts if o['value']>n}
  elif 'Count up from' in ins or 'Count down from' in ins:
   n=int(re.search(r'from (\d+)',ins)[1]);delta=-1 if 'down' in ins else 1;values={n+delta*i for i in [1,2,3]};expect={o['id'] for o in opts if o['value'] in values}
  elif 'exactly' in ins:
   n=int(re.search(r'exactly (\d+)',ins)[1]);expect={o['id'] for o in opts if o['value']==n}
  elif 'outside that range' in ins:
   lo,hi=map(int,re.search(r'from (\d+) through (\d+)',ins).groups());expect={o['id'] for o in opts if not lo<=o['value']<=hi}
  elif 'each have' in ins:
   n=int(re.search(r'each have (\d+)',ins)[1]);expect={o['id'] for o in opts if o['value']!=n}
  assert expect is not None and ans==expect,'numeric selection truth'
 if cat.startswith('pattern-'):
  if r['engine']=='pair':
   for p in r['pairs']:
    left=next(o['symbol'] for o in opts if o['id']==p['left']);right=next(o['symbol'] for o in r['rightOptions'] if o['id']==p['right']);assert left==right*2,'pattern unit truth'
  else:
   names={'circle':'○','triangle':'△','square':'□','star':'☆','heart':'♡','rhombus':'◇'}
   labels=re.search(r'pattern: repeat (.+?)\.',r['instruction']['en'])[1].lower().split(', ');unit=''.join(names[n] for n in labels)
   if kind in ['choose-many','odd-one-out']:
    valid=lambda sy:all(v==unit[i%len(unit)] for i,v in enumerate(sy))
    assert ans=={o['id'] for o in opts if valid(o['symbol'])==(kind=='choose-many')},'pattern classification truth'
   else:
    symbols={'circle':'○','triangle':'△','square':'□','star':'☆','heart':'♡','diamond':'◇'}
    items=r['patternItems'];missing=items.index(None)
    assert all(not o or symbols[o['shape']]==unit[i%len(unit)] for i,o in enumerate(items)),'pattern strip truth'
    assert ans=={o['id'] for o in opts if symbols[o['shape']]==unit[missing%len(unit)]},'pattern missing truth'
 if r['engine']=='pair' and cat not in NUMBER_CATS+ARITHMETIC and not cat.startswith('pattern-'):
  field='value' if cat in MEASURES else 'direction' if cat=='directions' else 'color' if cat in ['colors','color-pairs','memory-colors'] else 'shape' if cat in ['shapes','shape-pairs','memory-shapes'] else 'symbol' if cat in ['uppercase-pairs','lowercase-pairs','letter-case','vowels','consonants','positions'] else 'asset'
  for p in r['pairs']:
   left=next(o for o in opts if o['id']==p['left']);right=next(o for o in r['rightOptions'] if o['id']==p['right'])
   if cat=='initial-letters':assert left['label']['id'][0]==right['symbol'],'initial pair truth'
   elif cat=='letter-case':assert left['symbol'].lower()==right['symbol'],'case pair truth'
   else:assert left[field]==right[field],'feature pair truth'

def main():
 categories=json.loads((SRC/'app/data/worksheet-categories.json').read_text())
 owned=[c for c in categories if (c['group'] in ['visual','matching','literacy','numbers','patterns','memory'] and c['id']!='symmetry') or c['id'] in ['vehicle-count','build-blocks']]
 manifest={'revision':'variety-1','categories':[],'negativeFixtures':[]}
 for c in owned:
  cat=c['id'];original=json.loads((SRC/'content/worksheets'/f'{cat}.json').read_text());data=cp(original)
  for i in range(12,24):
   mode=(i-12)%4;batch=(i-12)//4;rounds=[make_round(cat,mode,batch*4+r) for r in range(4)]
   # The IDs and learning metadata remain stable; all inherited task fields are replaced.
   base={k:cp(v) for k,v in original[i].items() if k in ['id','category','title','age','ageRange','variant','difficulty','offscreen','note']}
   base.update(cp(rounds[0]));base.update(rounds=rounds,revision='variety-1');data[i]=base
   for r in rounds:validate_semantics(r,cat)
   assert len({json.dumps(r,sort_keys=True,ensure_ascii=False) for r in rounds})==4,(cat,i,'four distinct tasks')
  assert data[:12]==original[:12],(cat,'preserved originals')
  assert [w['id'] for w in data]==[w['id'] for w in original],(cat,'preserved ids')
  kinds=sorted({infer_kind(dict(w,**r)) for w in data for r in w['rounds']});engines=sorted({r.get('engine',w['engine']) for w in data for r in w['rounds']})
  assert len(kinds)>=4 and len(engines)>=3,(cat,kinds,engines)
  (OUT/f'{cat}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n')
  manifest['categories'].append(dict(id=cat,worksheets=24,preserved=12,replaced=12,rounds=96,activityKinds=kinds,engines=engines,sha256=hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()))
 # Mutation fixtures demonstrate that semantic failures are caught, not just schema defects.
 fixtures=[('wrong measurement answer','height',lambda r:r.update(answer=['o3'])),('duplicate memory faces','memory-shapes',lambda r:r['options'].__setitem__(1,dict(cp(r['options'][0]),id='o1'))),('non-bijective pairs','shape-pairs',lambda r:r['pairs'][1].update(right='r0')),('bad arithmetic target','add-to-5',lambda r:r.update(countTarget=99)),('moved fixed-grid position','positions',lambda r:r['options'][0].update(position='bottom-left')),('wrong vowel class','vowels',lambda r:r.update(answer=['o0','o1','o3'])),('wrong arithmetic selections','add-to-10',lambda r:r.update(answer=['o0','o1','o3'])),('wrong pattern classification','pattern-ab',lambda r:r.update(answer=['o0','o1','o3'])),('wrong quantity comparison','compare-quantity',lambda r:r.update(answer=['o0','o1','o3']))]
 for name,cat,mutate in fixtures:
  mode=3 if cat in ['memory-shapes','add-to-5'] else 2 if cat=='shape-pairs' else 0
  r=make_round(cat,mode,0);mutate(r)
  try:validate_semantics(r,cat)
  except AssertionError as e:manifest['negativeFixtures'].append(dict(name=name,status='rejected',reason=str(e)))
  else:raise AssertionError(('fixture accepted',name))
 manifest['summary']={'categories':len(owned),'worksheets':len(owned)*24,'newWorksheets':len(owned)*12,'newRounds':len(owned)*48,'semanticChecks':'schema, four-language copy, unique answers, 3+ selections, bijective pairs, distinct memory faces, fixed coordinates, letter classes/case, arithmetic quantities, numeric pair relations and monotone sequences'}
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(manifest['summary']));print('Negative fixtures rejected:',len(manifest['negativeFixtures']))
if __name__=='__main__':main()
