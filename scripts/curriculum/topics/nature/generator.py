"""Deterministic additive weather and season practice; output stays beside this file."""
from pathlib import Path
import json, random, itertools, hashlib, copy
ROOT=Path(__file__).resolve().parent
(ROOT/'bundles').mkdir(exist_ok=True)
def T(i,e,z,a):return dict(id=i,en=e,zh=z,ar=a)
L={
'weather-sun':T('Cerah','Sunny','晴天','مشمس'),
'weather-clouds':T('Berawan','Cloudy','多云','غائم'),
'weather-rain':T('Hujan','Rainy','下雨','ممطر'),
'weather-wind':T('Berangin','Windy','刮风','عاصف بالرياح'),
'weather-rainbow':T('Pelangi','Rainbow','彩虹','قوس قزح'),
'weather-snow':T('Keping salju','Snowflake','雪花','ندفة ثلج'),
'season-spring':T('Musim semi','Spring','春季','الربيع'),
'season-summer':T('Musim panas','Summer','夏季','الصيف'),
'season-autumn':T('Musim gugur','Autumn','秋季','الخريف'),
'season-winter':T('Musim dingin','Winter','冬季','الشتاء'),
'season-wet':T('Musim hujan','Rainy season','雨季','موسم الأمطار'),
'season-dry':T('Musim kemarau','Dry season','旱季','موسم الجفاف'),
'weather-raincoat':T('Jas hujan','Raincoat','雨衣','معطف مطر'),
'weather-boots':T('Sepatu bot hujan','Rain boots','雨靴','حذاء مطر'),
'weather-sunhat':T('Topi matahari','Sun hat','遮阳帽','قبعة شمس'),
'weather-coat':T('Mantel musim dingin','Winter coat','冬季外套','معطف شتوي'),
'umbrella':T('Payung','Umbrella','雨伞','مظلة'),
'water-glass':T('Segelas air','Glass of water','一杯水','كوب ماء'),
'flower':T('Bunga','Flower','花','زهرة'),
'leaf':T('Daun','Leaf','叶子','ورقة شجر'),
'ice-cube':T('Es batu','Ice cube','冰块','مكعب ثلج'),
'book':T('Buku','Book','书','كتاب'),
'kite':T('Layang-layang','Kite','风筝','طائرة ورقية'),
'backpack':T('Tas punggung','Backpack','背包','حقيبة ظهر'),
'watering-can':T('Penyiram tanaman','Watering can','洒水壶','إبريق سقي'),
'raindrop':T('Tetes hujan','Raindrop','雨滴','قطرة مطر'),
'sun':T('Matahari','Sun','太阳','الشمس'),
'cloud':T('Awan','Cloud','云','سحابة'),
'car':T('Mobil','Car','汽车','سيارة'),
'chair':T('Kursi','Chair','椅子','كرسي'),
'apple':T('Apel','Apple','苹果','تفاحة'),
'banana':T('Pisang','Banana','香蕉','موز'),
}
CLUES={
'weather-sun':T('Matahari bersinar. Cuaca apa yang ditunjukkan gambar ini?','The sun is shining. Which picture shows this weather?','太阳照耀着。哪张图表示这样的天气？','الشمس ساطعة. أي صورة تمثل هذا الطقس؟'),
'weather-clouds':T('Langit tertutup awan. Pilih gambar cuacanya.','Clouds cover the sky. Choose the weather picture.','天空布满了云。选出对应的天气图。','تغطي السحب السماء. اختر صورة الطقس المناسبة.'),
'weather-rain':T('Air turun dari awan sebagai tetesan. Pilih gambar cuacanya.','Water falls from clouds in drops. Choose the weather picture.','水滴从云中落下。选出对应的天气图。','تسقط قطرات الماء من السحب. اختر صورة الطقس المناسبة.'),
'weather-wind':T('Udara bergerak dan membuat pohon bergoyang. Pilih gambar cuacanya.','Moving air makes a tree sway. Choose the weather picture.','流动的空气让树摇摆。选出对应的天气图。','يحرك الهواء أغصان الشجرة. اختر صورة الطقس المناسبة.'),
'weather-rainbow':T('Lengkungan berwarna-warni tampak di langit. Gambar apakah ini?','A colorful arc appears in the sky. Which picture is it?','天空中出现一道彩色的弧线。这是什么？','يظهر قوس ملون في السماء. ما هذه الصورة؟'),
'weather-snow':T('Kecil, dingin, dan berupa kristal es. Pilih gambar kepingnya.','It is a small, cold crystal of ice. Choose its picture.','它是小小的、冰冷的冰晶。选出它的图片。','إنها بلورة جليدية صغيرة وباردة. اختر صورتها.'),
'season-spring':T('Dalam gambar ini, pohon berbunga. Pilih ilustrasi musim semi.','In this picture, the tree has blossoms. Choose the spring illustration.','这张图里的树开花了。选出春季的插图。','تزهر الشجرة في هذه الصورة. اختر رسم الربيع.'),
'season-summer':T('Dalam gambar ini, pohon berdaun hijau di bawah matahari. Pilih ilustrasi musim panas.','This picture shows a leafy green tree in sunshine. Choose the summer illustration.','这张图里，绿树沐浴着阳光。选出夏季的插图。','تظهر شجرة خضراء تحت الشمس في هذه الصورة. اختر رسم الصيف.'),
'season-autumn':T('Dalam gambar ini, daun berwarna jingga. Pilih ilustrasi musim gugur.','The leaves are orange in this picture. Choose the autumn illustration.','这张图里的叶子是橙色的。选出秋季的插图。','أوراق الشجرة برتقالية في هذه الصورة. اختر رسم الخريف.'),
'season-winter':T('Dalam gambar ini, pohon tanpa daun berada di atas salju. Pilih ilustrasi musim dingin.','This picture shows a bare tree in snow. Choose the winter illustration.','这张图里，光秃秃的树立在雪中。选出冬季的插图。','تظهر شجرة بلا أوراق وسط الثلج في هذه الصورة. اختر رسم الشتاء.'),
'season-wet':T('Pada musim ini, hujan biasanya lebih sering turun. Pilih ilustrasi musim hujan.','Rain is usually more frequent in this season. Choose the rainy-season illustration.','这个季节通常下雨较多。选出雨季的插图。','عادة ما يكثر المطر في هذا الموسم. اختر رسم موسم الأمطار.'),
'season-dry':T('Pada musim ini, hujan biasanya lebih sedikit. Pilih ilustrasi musim kemarau.','There is usually less rain in this season. Choose the dry-season illustration.','这个季节通常下雨较少。选出旱季的插图。','عادة ما يقل المطر في هذا الموسم. اختر رسم موسم الجفاف.'),
'weather-raincoat':T('Aku dipakai pada tubuh untuk membantu melindungi pakaian dari hujan. Apakah aku?','You wear me to help keep rain off your clothes. What am I?','把我穿在身上，可以帮助衣服挡雨。我是什么？','ترتديني للمساعدة في حماية ملابسك من المطر. ما أنا؟'),
'weather-boots':T('Aku dipakai di kaki ketika tanah basah. Apakah aku?','You wear me on your feet when the ground is wet. What am I?','地面湿的时候，你可以把我穿在脚上。我是什么？','ترتديني في قدميك عندما تكون الأرض مبللة. ما أنا؟'),
'weather-sunhat':T('Aku dipakai di kepala untuk memberi teduh dari matahari. Apakah aku?','You wear me on your head for shade from the sun. What am I?','你把我戴在头上，用来遮阳。我是什么？','ترتديني على رأسك لأظلله من الشمس. ما أنا؟'),
'weather-coat':T('Aku pakaian tebal untuk membantu tubuh terasa hangat saat dingin. Apakah aku?','I am a thick garment that helps you stay warm in cold weather. What am I?','我是厚厚的衣服，天气冷时可以帮你保暖。我是什么？','أنا لباس سميك يساعد على الدفء في الطقس البارد. ما أنا؟'),
'umbrella':T('Aku dibuka dan dipegang di atas kepala saat hujan. Apakah aku?','You open me and hold me above your head in the rain. What am I?','下雨时，你把我打开，举在头顶。我是什么？','تفتحني وتحملني فوق رأسك في المطر. ما أنا؟'),
'water-glass':T('Aku berisi air yang bisa diminum. Pilih gambarku.','I hold water you can drink. Choose my picture.','我装着可以喝的水。选出我的图片。','أحتوي على ماء للشرب. اختر صورتي.'),
'flower':T('Aku punya kelopak dan tumbuh pada tanaman. Apakah aku?','I have petals and grow on a plant. What am I?','我长在植物上，有花瓣。我是什么？','لي بتلات وأنمو على نبات. ما أنا؟'),
'leaf':T('Aku tumbuh di ranting pohon. Pilih gambar daun.','I grow on a tree branch. Choose the leaf picture.','我长在树枝上。选出叶子的图片。','أنمو على غصن شجرة. اختر صورة الورقة.'),
'ice-cube':T('Aku air yang membeku, berbentuk kubus. Apakah aku?','I am frozen water shaped like a cube. What am I?','我是冻成方块的水。我是什么？','أنا ماء متجمد على شكل مكعب. ما أنا؟'),
'backpack':T('Aku dibawa di punggung untuk menyimpan bekal dan barang. Apakah aku?','You carry me on your back to hold your things. What am I?','你把我背在背上，用来装东西。我是什么？','تحملني على ظهرك لتضع أغراضك بداخلي. ما أنا؟'),
'watering-can':T('Aku memiliki pegangan dan corong untuk menyiram tanaman. Apakah aku?','I have a handle and spout for watering plants. What am I?','我有把手和壶嘴，用来给植物浇水。我是什么？','لي مقبض وفوهة لسقي النباتات. ما أنا؟'),
'raindrop':T('Aku satu tetes air yang turun dari awan. Apakah aku?','I am one drop of water falling from a cloud. What am I?','我是从云中落下的一滴水。我是什么？','أنا قطرة ماء تسقط من سحابة. ما أنا؟'),
}
WEATHER=['weather-sun','weather-clouds','weather-rain','weather-wind','weather-rainbow','weather-snow']
KIT=['weather-raincoat','weather-boots','weather-sunhat','weather-coat','umbrella','water-glass','backpack','watering-can']
SEASONS=['season-spring','season-summer','season-autumn','season-winter']
INDONESIA=['season-wet','season-dry','weather-rain','weather-sun','weather-raincoat','weather-boots','weather-sunhat','umbrella']
G={
'weather':(T('Gambar cuaca dan langit','Weather and sky pictures','天气和天空图片','صور الطقس والسماء'),WEATHER,'weather-clouds'),
'kit':(T('Perlengkapan','Equipment','用品','أدوات ومستلزمات'),KIT,'backpack'),
'wear':(T('Benda yang dikenakan','Things we wear','穿戴的物品','أشياء نرتديها'),KIT[:4],'weather-raincoat'),
'carry':(T('Benda yang dipegang','Things we hold','用手拿的物品','أشياء نمسكها'),['umbrella','water-glass','watering-can'],'umbrella'),
'seasons':(T('Ilustrasi empat musim','Four-season illustrations','四季插图','رسوم الفصول الأربعة'),SEASONS,'season-spring'),
'nature':(T('Benda alam','Natural objects','自然物品','أشياء من الطبيعة'),['flower','leaf','ice-cube','raindrop'],'flower'),
'indo':(T('Ilustrasi musim Indonesia','Indonesian season illustrations','印度尼西亚季节插图','رسوم مواسم إندونيسيا'),['season-wet','season-dry'],'season-wet'),
'rainwear':(T('Pakaian hujan','Rainwear','雨具服饰','ملابس المطر'),['weather-raincoat','weather-boots'],'weather-raincoat'),
'water':(T('Gambar air cair','Pictures of liquid water','液态水图片','صور الماء السائل'),['weather-rain','raindrop','water-glass'],'raindrop'),
'objects':(T('Benda buatan manusia','Human-made objects','人造物品','أشياء صنعها الإنسان'),['book','chair','car','umbrella','backpack','weather-sunhat'],'book'),
}
CATEGORIES=[
 dict(id='weather-signs',group='weather',asset='weather-rainbow',title=T('Cuaca & Langit','Weather & Sky','天气与天空','الطقس والسماء'),description=T('Kenali cerah, berawan, hujan, angin, pelangi, dan salju melalui beragam permainan.','Explore sunshine, clouds, rain, wind, rainbows, and snow through varied games.','用多种游戏认识晴天、云、雨、风、彩虹和雪。','تعرف إلى الشمس والسحب والمطر والرياح وقوس قزح والثلج عبر ألعاب متنوعة.'),pool=WEATHER,groups=[('weather','kit'),('weather','objects'),('weather','nature')],note=T('Lihat cuaca dari tempat yang nyaman bersama pendamping. Gambar cuaca adalah simbol sederhana.','Observe the weather with a grown-up from a comfortable place. Weather pictures are simple symbols.','和大人一起在舒适的地方观察天气。天气图片是简化的符号。','راقب الطقس مع شخص بالغ من مكان مريح. صور الطقس رموز مبسطة.')),
 dict(id='weather-kit',group='weather',asset='weather-raincoat',title=T('Siap untuk Cuaca','Ready for the Weather','为天气做准备','نستعد للطقس'),description=T('Temukan pakaian dan perlengkapan untuk hujan, matahari, dan udara dingin.','Discover clothing and equipment for rain, sunshine, and cold weather.','认识雨天、晴天和寒冷天气所需的衣物和用品。','اكتشف الملابس والمستلزمات للمطر والشمس والطقس البارد.'),pool=KIT,groups=[('wear','carry'),('kit','weather'),('wear','nature')],note=T('Bersama pendamping, lihat cuaca lalu pilih perlengkapan yang nyaman untuk kegiatan hari ini.','With a grown-up, check the weather and choose comfortable equipment for today’s activity.','和大人一起看看天气，为今天的活动选择合适的用品。','انظر إلى الطقس مع شخص بالغ واختر مستلزمات مريحة لنشاط اليوم.')),
 dict(id='seasons-world',group='seasons',asset='season-autumn',title=T('Empat Musim di Dunia','Four Seasons Around the World','认识世界四季','الفصول الأربعة حول العالم'),description=T('Jelajahi ilustrasi semi, panas, gugur, dan dingin yang dikenal di sebagian wilayah dunia.','Explore spring, summer, autumn, and winter illustrations from regions with four seasons.','通过插图认识一些地区的春、夏、秋、冬。','اكتشف رسوم الربيع والصيف والخريف والشتاء في مناطق تعرف أربعة فصول.'),pool=SEASONS+['flower','leaf','weather-snow','weather-sun'],groups=[('seasons','nature'),('seasons','kit'),('seasons','weather')],note=T('Sebagian wilayah mengenal empat musim. Tampilan dan waktu musim berbeda menurut tempat; gambar ini contoh sederhana.','Some regions have four seasons. Their timing and appearance vary by place; these pictures are simple examples.','有些地区有四季。季节的时间和景象因地区而异，这些图片只是简单的例子。','تعرف بعض المناطق أربعة فصول. يختلف توقيتها ومظهرها حسب المكان، وهذه الرسوم أمثلة مبسطة.')),
 dict(id='seasons-indonesia',group='seasons',asset='season-wet',title=T('Musim di Indonesia','Seasons in Indonesia','印度尼西亚的季节','المواسم في إندونيسيا'),description=T('Kenali musim hujan dan kemarau serta gambar cuaca dan perlengkapan sehari-hari.','Explore rainy and dry seasons, weather pictures, and everyday equipment.','认识雨季、旱季、天气图片和日常用品。','تعرف إلى موسمي الأمطار والجفاف وصور الطقس والمستلزمات اليومية.'),pool=INDONESIA,groups=[('indo','weather'),('indo','kit'),('rainwear','nature')],note=T('Banyak wilayah Indonesia mengenal musim hujan dan kemarau. Waktunya berbeda antarwilayah; hujan juga dapat turun saat kemarau.','Many Indonesian regions have rainy and dry seasons. Their timing varies by region; rain can also fall in the dry season.','印度尼西亚许多地区有雨季和旱季。时间因地区而异，旱季也可能下雨。','تعرف مناطق كثيرة في إندونيسيا موسمي الأمطار والجفاف. يختلف التوقيت بين المناطق، وقد يهطل المطر أيضا في موسم الجفاف.')),
]
KIND_TITLES={
'choose-one':T('Kenali gambar','Name the picture','认识图片','تعرف إلى الصورة'),
'clue':T('Tebak dari petunjuk','Guess from a clue','根据线索猜一猜','خمن من التلميح'),
'choose-many':T('Pilih semua yang sesuai','Choose all that belong','选出所有符合的图片','اختر كل ما ينتمي للمجموعة'),
'odd-one-out':T('Mana yang berbeda?','Which one is different?','找出不同类','ما المختلف؟'),
'match':T('Pasangkan gambar','Match the pictures','图片配对','طابق الصور'),
'memory':T('Temukan pasangan tersembunyi','Find the hidden pairs','找出隐藏的配对','اعثر على الأزواج المخفية'),
'pattern':T('Lanjutkan pola','Continue the pattern','继续规律','أكمل النمط'),
'sort':T('Kelompokkan gambar','Sort the pictures','图片分类','صنف الصور'),
}
def pic(asset,id=None,**extra):
 d=dict(kind='asset',asset=asset,label=copy.deepcopy(L[asset]),showLabel=True)
 if id is not None:d['id']=id
 d.update(extra);return d
def one_prompt(asset):
 a=L[asset]
 return T(f"Pilih gambar: {a['id']}.",f"Choose the picture: {a['en']}.",f"选出图片：{a['zh']}。",f"اختر الصورة: {a['ar']}.")
def choose_prompt(label):
 return T(f"Pilih semua yang termasuk kelompok: {label['id']}.",f"Choose everything in this group: {label['en']}.",f"选出这一类中的所有图片：{label['zh']}。",f"اختر كل ما ينتمي إلى هذه المجموعة: {label['ar']}.")
def odd_prompt(label):
 return T(f"Mana yang bukan anggota kelompok: {label['id']}?",f"Which one does not belong in this group: {label['en']}?",f"哪一张不属于这一类：{label['zh']}？",f"أي صورة لا تنتمي إلى هذه المجموعة: {label['ar']}؟")
def rnd(rng,values):
 out=list(values);rng.shuffle(out);return out
def semantic(r):
 # Choice order and picture IDs are excluded: rearrangement is not a new task.
 o={p['id']:p['asset'] for p in r['options']}
 core={'kind':r['activityKind'],'prompt':r['instruction']['en'],'options':sorted(o.values()),'answer':sorted(o[x] for x in r['answer'])}
 if 'patternItems'in r:core['pattern']=[p['asset']if p else None for p in r['patternItems']]
 if 'bins'in r:core['mapping']=sorted((o[p['left']],p['right'])for p in r['pairs'])
 return json.dumps(core,sort_keys=True)
def make_round(cat,kind,v,r,rng):
 pool=cat['pool'];engine={'match':'pair','memory':'memory','pattern':'pattern','sort':'sort'}.get(kind,'identify')
 out=dict(engine=engine,activityKind=kind,options=[],answer=[])
 if kind in ['choose-one','clue']:
  target=pool[(v*3+r)%len(pool)]
  assets=[target]+rng.sample([x for x in pool if x!=target],2+(v==2))
  out['options']=[pic(x,f'o{i}')for i,x in enumerate(rnd(rng,assets))]
  out['instruction']=one_prompt(target)if kind=='choose-one'else CLUES[target]
  out['answer']=[p['id']for p in out['options']if p['asset']==target]
 elif kind in ['choose-many','odd-one-out','sort']:
  ga,gb=cat['groups'][(v+r)%len(cat['groups'])]
  # Alternate the requested class to exercise both membership and exclusion.
  if (r+v)%2:ga,gb=gb,ga
  la,aa,art_a=G[ga];lb,bb,art_b=G[gb]
  assert not set(aa)&set(bb)
  if kind=='odd-one-out':
   # Two same-class cards plus exactly one outsider; never an unspecified criterion.
   assets=rng.sample(aa,2)+rng.sample(bb,1)
  else:assets=rng.sample(aa,2)+rng.sample(bb,2)
  out['options']=[pic(x,f'o{i}')for i,x in enumerate(rnd(rng,assets))]
  if kind=='sort':
   out['instruction']=T(f"Kelompokkan gambar: {la['id']} atau {lb['id']}. Pilih kartu, lalu kelompoknya.",f"Sort the pictures: {la['en']} or {lb['en']}. Choose a card, then its group.",f"把图片分为“{la['zh']}”和“{lb['zh']}”。先选卡片，再选类别。",f"صنف الصور إلى: {la['ar']} أو {lb['ar']}. اختر بطاقة ثم مجموعتها.")
   out['bins']=[dict(id=ga,label=la,asset=art_a),dict(id=gb,label=lb,asset=art_b)]
   out['pairs']=[dict(left=p['id'],right=ga if p['asset']in aa else gb)for p in out['options']]
  else:
   out['instruction']=choose_prompt(la)if kind=='choose-many'else odd_prompt(la)
   out['answer']=[p['id']for p in out['options']if (p['asset']in aa)==(kind=='choose-many')]
 elif kind in ['match','memory']:
  assets=rng.sample(pool,2+(v!=0))
  out['instruction']=T('Pasangkan gambar yang sama.','Match the identical pictures.','把相同的图片配成一对。','صل الصور المتطابقة.') if kind=='match' else T('Balik kartu. Temukan semua pasangan gambar yang sama.','Turn over the cards. Find all pairs of identical pictures.','翻开卡片，找出所有相同图片的配对。','اقلب البطاقات واعثر على جميع أزواج الصور المتطابقة.')
  if kind=='match':
   out['options']=[pic(x,f'l{i}',pairId=f'r{i}')for i,x in enumerate(assets)]
   out['rightOptions']=rnd(rng,[pic(x,f'r{i}')for i,x in enumerate(assets)])
   out['pairs']=[dict(left=f'l{i}',right=f'r{i}')for i in range(len(assets))]
  else:out['options']=[pic(x,f'm{i}')for i,x in enumerate(assets)]
 elif kind=='pattern':
  assets=rng.sample(pool,3);a,b,c=assets
  seq=[[a,b,a,b,a,b],[a,a,b,a,a,b],[a,b,c,a,b,c]][v]
  out['instruction']=T('Lihat pola gambar dari awal. Pilih gambar untuk tempat kosong.','Follow the picture pattern from the start. Choose the missing picture.','从头观察图片规律，选出空缺的图片。','اتبع نمط الصور من البداية واختر الصورة الناقصة.')
  out['options']=[pic(x,f'o{i}')for i,x in enumerate(rnd(rng,assets))]
  out['answer']=[p['id']for p in out['options']if p['asset']==seq[-1]]
  out['patternItems']=[pic(x)for x in seq[:-1]]+[None]
 return out

def validate(categories,records):
 known=set(L);report=[]
 for c in categories:
  ws=records[c['id']];assert len(ws)==24
  whole=set()
  for w in ws:
   assert len(w['rounds'])==4
   fingerprints=[semantic(r)for r in w['rounds']]
   assert len(set(fingerprints))==4,(w['id'],'duplicate round')
   fp=tuple(sorted(fingerprints));assert fp not in whole,(w['id'],'duplicate worksheet');whole.add(fp)
   for r in w['rounds']:
    ids={p['id'] for p in r['options']};assert len(ids)==len(r['options'])
    assert set(r['answer'])<=ids
    assert all(p['asset']in known for p in r['options'])
    if r['engine']=='identify':assert len(r['answer'])==(2 if r['activityKind']=='choose-many'else 1)
    if r['engine']=='pair':
     assert set(p['right']for p in r['pairs'])==set(p['id']for p in r['rightOptions'])
    if r['engine']=='sort':
     assert set(p['left']for p in r['pairs'])==ids
     assert set(p['right']for p in r['pairs'])==set(b['id']for b in r['bins'])
   def checklangs(x):
    if isinstance(x,dict):
     if 'en'in x or 'zh'in x or 'ar'in x:assert all(isinstance(x.get(k),str)and x[k].strip()for k in ['id','en','zh','ar']),x
     for v in x.values():checklangs(v)
    elif isinstance(x,list):
     for v in x:checklangs(v)
   checklangs(w)
  report.append(dict(id=c['id'],worksheets=len(ws),rounds=sum(len(w['rounds'])for w in ws),kinds=sorted({w['activityKind']for w in ws}),engines=sorted({w['engine']for w in ws}),uniqueWorksheetTasksets=len(whole)))
 return report

def run():
 categories=[];records={}
 for ci,cat in enumerate(CATEGORIES):
  ws=[]
  for ki,kind in enumerate(KIND_TITLES):
   used_whole=set()
   for v in range(3):
    rng=random.Random(20260918+ci*10000+ki*100+v)
    rounds=[];seen=set()
    for r in range(4):
     for attempt in range(100):
      value=make_round(cat,kind,v,r,rng);fp=semantic(value)
      if fp not in seen:break
     else:raise AssertionError(('round uniqueness',cat['id'],kind,v,r))
     seen.add(fp);rounds.append(value)
    title={lang:f"{KIND_TITLES[kind][lang]} · {cat['title'][lang]}"for lang in ['id','en','zh','ar']}
    num=ki*3+v+1
    w=dict(id=f"{cat['id']}-{num:02}",category=cat['id'],title=title,variant=num,difficulty=1+v,age=3,ageRange=[3,6],revision='topics-v1',offscreen=cat['note'],note=T('Bacakan petunjuk dan dengarkan nama gambar. Anak boleh memilih dengan bantuan pendamping.','Read the prompt and listen to the picture names. Children may choose with a grown-up’s help.','读一读提示，听一听图片名称。孩子可以在大人帮助下选择。','اقرأ التعليمات واستمع إلى أسماء الصور. يمكن للطفل الاختيار بمساعدة شخص بالغ.'),**copy.deepcopy(rounds[0]),rounds=rounds)
    ws.append(w)
  records[cat['id']]=ws
  category={k:v for k,v in cat.items()if k not in ['pool','groups','note']}
  category.update(engine='identify',age=3,ageRange=[3,6],worksheetCount=24,activityKinds=list(KIND_TITLES))
  categories.append(category)
 audit=validate(categories,records)
 for c in categories:(ROOT/'bundles'/f"{c['id']}.json").write_text(json.dumps(records[c['id']],ensure_ascii=False,separators=(',',':')))
 (ROOT/'categories.json').write_text(json.dumps(categories,ensure_ascii=False,indent=2))
 (ROOT/'labels.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
 (ROOT/'art-labels.json').write_text(json.dumps({k:v for k,v in L.items()if k.startswith('weather-')or k.startswith('season-')},ensure_ascii=False,indent=2))
 report=dict(worksheets=96,rounds=384,categories=audit,languages=['id','en','zh','ar'],checks=['four semantically distinct rounds per worksheet','unique whole tasksets ignoring option order and IDs','choice answer counts and membership','pair and sorting referential integrity','four-language text coverage'],facts=['Four-season illustrations describe examples in some regions, not a universal calendar.','Rainy/dry season timing varies across Indonesia; rain can occur during the dry season.','No month, medical, or development outcome claims.'],sources=[dict(title='BMKG Prediksi Musim',url='https://www.bmkg.go.id/iklim/prediksi-musim',verified='2026-09-18',supports='Rainy and dry seasons in Indonesia; regional timing variation.'),dict(title='NASA Space Place: What Causes the Seasons?',url='https://spaceplace.nasa.gov/seasons/en/',verified='2026-09-18',supports='Four-season cycle and geographic differences; no calendar claims used.')])
 (ROOT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'worksheets':96,'rounds':384,'categories':len(categories),'engines':5,'kinds':8}))
if __name__=='__main__':run()
