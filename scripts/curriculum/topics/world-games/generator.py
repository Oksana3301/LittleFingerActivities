"""Additive geography and play curriculum. Inputs: verified country metadata.

Run: python generator.py [output-directory] [countries.json]
All activity illustrations are existing assets or separately commissioned art.
"""
import json, random, itertools, math, sys
from pathlib import Path
OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).parent
GEO=Path(sys.argv[2]) if len(sys.argv)>2 else Path(__file__).resolve().parents[4]/'app/data/world-countries.json'
OUT.mkdir(parents=True,exist_ok=True); (OUT/'bundles').mkdir(exist_ok=True)
LANGS=('id','en','zh','ar')
def T(i,e,z,a): return dict(zip(LANGS,(i,e,z,a)))
def fmt(t, **values): return {l:s.format(**{k:(v[l] if isinstance(v,dict) else v) for k,v in values.items()}) for l,s in t.items()}
R=random.Random(81926)
countries=json.loads(GEO.read_text()); C={c['code']:c for c in countries}
C['gb']['name']['id']='Britania Raya dan Irlandia Utara'
L={f"flag-{c['code']}":c['name'] for c in countries}
L.update({
 'game-top':T('Gasing','Spinning top','陀螺','بلبل دوار'),
 'game-congklak':T('Congklak','Congklak board','康克拉棋盘','لوح لعبة كونغكلاك'),
 'game-hopscotch':T('Engklek','Hopscotch','跳房子','الحجلة'),
 'game-puzzle':T('Puzzle gambar','Jigsaw puzzle','拼图','أحجية الصور'),
 'football':T('Bola sepak','Football','足球','كرة قدم'),
 'basketball':T('Bola basket','Basketball','篮球','كرة سلة'),
 'badminton-racket':T('Raket bulu tangkis','Badminton racket','羽毛球拍','مضرب ريشة'),
 'tennis-racket':T('Raket tenis','Tennis racket','网球拍','مضرب تنس'),
 'kite':T('Layang-layang','Kite','风筝','طائرة ورقية'),
 'building-blocks':T('Balok mainan','Building blocks','积木','مكعبات لعب'),
 'skateboard':T('Papan luncur','Skateboard','滑板','لوح تزلج'),
 'tent':T('Tenda','Tent','帐篷','خيمة'),
 'habit-sharing':T('Berbagi balok','Sharing blocks','分享积木','مشاركة المكعبات'),
 'habit-waiting':T('Menunggu giliran','Waiting for a turn','等待轮到自己','انتظار الدور'),
 'habit-tidying':T('Merapikan mainan','Putting toys away','收好玩具','ترتيب الألعاب'),
 'habit-helping':T('Membantu membawa bantal','Helping carry a cushion','帮忙搬靠垫','المساعدة في حمل وسادة'),
 'habit-greeting':T('Menyapa dengan ramah','Greeting kindly','友好地打招呼','إلقاء التحية بلطف'),
 'habit-thanking':T('Mengucapkan terima kasih','Saying thank you','说谢谢','قول شكرا'),
 'habit-asking-help':T('Meminta bantuan pendamping','Asking a grown-up for help','请大人帮忙','طلب المساعدة من شخص بالغ'),
 'habit-gentle':T('Bermain lembut bersama adik','Playing gently with a younger child','温柔地陪小朋友玩','اللعب برفق مع طفل أصغر'),
 'habit-apologizing':T('Mengucapkan maaf','Saying sorry','说对不起','قول آسف'),
 'habit-toy-basket':T('Keranjang mainan','Toy basket','玩具篮','سلة الألعاب'),
})
def pic(asset,id=None):
 p=dict(kind='asset',asset=asset,label=L[asset],showLabel=True)
 if id is not None:p['id']=id
 return p
def shuffled(xs): xs=list(xs);R.shuffle(xs);return xs
def roundbase(engine,kind,instruction,assets):
 return dict(engine=engine,activityKind=kind,instruction=instruction,options=[pic(a,f'o{i}') for i,a in enumerate(assets)],answer=[])
MATCH=T('Pasangkan dua gambar yang sama.','Match the identical pictures.','把相同的图片配成一对。','صل الصور المتطابقة.')
MEMORY=T('Balik kartu dan temukan setiap pasangan gambar yang sama.','Turn the cards and find every pair of identical pictures.','翻开卡片，找出每一对相同的图片。','اقلب البطاقات واعثر على كل زوج من الصور المتطابقة.')
PATTERN=T('Lihat urutan gambar. Pilih gambar untuk mengisi tempat kosong.','Look at the picture pattern. Choose the picture for the empty space.','观察图片规律，选出空格中的图片。','انظر إلى نمط الصور واختر صورة للمكان الفارغ.')
def match(assets):
 r=roundbase('pair','match',MATCH,assets)
 r['pairs']=[dict(left=f'o{i}',right=f'r{i}') for i in range(len(assets))]
 r['rightOptions']=shuffled([pic(a,f'r{i}') for i,a in enumerate(assets)])
 return r
def memory(assets):return roundbase('memory','memory',MEMORY,assets)
def pattern(assets,n):
 a,b,c=assets
 patterns=[[a,b,a,b,a,None],[a,a,b,a,a,None],[a,b,c,a,b,None],[a,b,b,a,b,None]]
 answer=[b,b,c,b][n%4]
 r=roundbase('pattern','pattern',PATTERN,shuffled(assets))
 r['answer']=[next(o['id'] for o in r['options'] if o['asset']==answer)]
 r['patternItems']=[pic(x) if x else None for x in patterns[n%4]]
 return r
def choose(assets,targets,instruction,kind='choose-one'):
 r=roundbase('identify',kind,instruction,shuffled(assets))
 r['answer']=[o['id'] for o in r['options'] if o['asset'] in targets]
 return r
def sets(pool,count,size=2,seed=1):
 combos=list(itertools.combinations(pool,size)); random.Random(seed).shuffle(combos)
 assert len(combos)>=count
 return combos[:count]
titles={
 'map-find':T('Jelajahi peta dunia','Explore the world map','探索世界地图','استكشف خريطة العالم'),
 'match':T('Temukan pasangannya','Find the matching pictures','找出配对的图片','اعثر على الصور المتطابقة'),
 'memory':T('Ingat lalu temukan','Remember and find','记住并找出来','تذكر ثم اعثر'),
 'pattern':T('Lanjutkan pola gambar','Continue the picture pattern','继续图片规律','أكمل نمط الصور'),
 'clue':T('Dengarkan petunjuknya','Listen to the clue','听一听线索','استمع إلى الدليل'),
 'choose-one':T('Pilih sikap dalam cerita','Choose the action in the story','选择故事中的行为','اختر التصرف في القصة'),
 'choose-many':T('Temukan dua sikap baik','Find two kind actions','找出两种友善的行为','اعثر على تصرفين لطيفين'),
}
def worksheets(category,groups):
 out=[]
 for kind,rounds in groups:
  assert len(rounds)%4==0
  for start in range(0,len(rounds),4):
   rs=rounds[start:start+4]; idx=len(out)+1
   w=dict(id=f'{category}-{idx:02}',category=category,title=titles[kind],variant=idx,difficulty=1 if kind in ['match','memory'] else 2,age=3,ageRange=[3,6],revision='topics-v1',**rs[0],rounds=rs)
   out.append(w)
 assert len(out)==24,(category,len(out))
 return out

# Country map rounds: labels identify approximate markers; each triple is widely spaced.
MAP=T('Temukan penanda {name} di peta. Nomor pada peta sama dengan nomor kartu.','Find the {name} marker on the map. Map numbers match the cards.','在地图上找到{name}的标记。地图上的数字与卡片相对应。','اعثر على علامة {name} على الخريطة. أرقام الخريطة تطابق أرقام البطاقات.')
codes=list(C)
# Both axes are normalized by the map width. The equirectangular map is 2:1,
# so latitude must also use 360 degrees to measure physical on-screen spacing.
def distance(a,b):return math.hypot((C[a]['lng']-C[b]['lng'])/360,(C[a]['lat']-C[b]['lat'])/360)
maprounds=[];used=set()
for n in range(32):
 target=codes[n%len(codes)]
 candidates=[p for p in itertools.combinations([x for x in codes if x!=target],2) if min(distance(target,p[0]),distance(target,p[1]),distance(*p))>=.22]
 candidates=shuffled(candidates)
 pair=next(p for p in candidates if (target,tuple(sorted(p))) not in used);used.add((target,tuple(sorted(pair))))
 picks=shuffled([target,*pair]);assets=[f'flag-{x}' for x in picks]
 r=roundbase('map','map-find',fmt(MAP,name=C[target]['name']),assets)
 r['answer']=[f'o{picks.index(target)}'];r['map']={'places':[dict(option=f'o{i}',lat=C[c]['lat'],lng=C[c]['lng'],country=c) for i,c in enumerate(picks)]}
 maprounds.append(r)
flagassets=list(L)[:24]
world=worksheets('world-countries',[
 ('map-find',maprounds),
 ('match',[match(x) for x in sets(flagassets,24,2,11)]),
 ('memory',[memory(x) for x in sets(flagassets,20,3,12)]),
 ('pattern',[pattern(x,i) for i,x in enumerate(sets(flagassets,20,3,13))]),
])

# Flag clues describe visible geometry and colors in the sourced flag-icons SVGs.
descriptions={
 'id':T('dua pita mendatar: merah di atas, putih di bawah','two horizontal bands: red above white','两条横带：上红下白','شريطان أفقيان: أحمر فوق أبيض'),
 'jp':T('lingkaran merah pada latar putih','a red circle on a white background','白底上的红色圆形','دائرة حمراء على خلفية بيضاء'),
 'cn':T('satu bintang kuning besar dan empat bintang kecil pada latar merah','one large yellow star and four small stars on red','红底上一颗大黄星和四颗小黄星','نجمة صفراء كبيرة وأربع نجوم صغيرة على خلفية حمراء'),
 'in':T('pita jingga, putih, hijau, dan roda biru di tengah','orange, white and green bands, with a blue wheel in the center','橙、白、绿横带，中间有蓝色轮子','أشرطة برتقالية وبيضاء وخضراء مع عجلة زرقاء في الوسط'),
 'sa':T('tulisan putih dan pedang pada latar hijau','white writing and a sword on green','绿底上的白色文字和剑','كتابة بيضاء وسيف على خلفية خضراء'),
 'tr':T('bulan sabit dan bintang putih pada latar merah','a white crescent and star on red','红底上的白色新月和星星','هلال ونجمة أبيضان على خلفية حمراء'),
 'au':T('bintang-bintang putih pada latar biru dengan bendera kecil di sudut','white stars on blue with a small flag in the corner','蓝底、白色星星，角上有一面小旗','نجوم بيضاء على خلفية زرقاء وعلم صغير في الزاوية'),
 'nz':T('empat bintang merah bertepi putih pada latar biru','four red stars with white edges on blue','蓝底上四颗镶白边的红星','أربع نجوم حمراء بحواف بيضاء على خلفية زرقاء'),
 'us':T('banyak garis merah-putih dan kotak biru berisi bintang putih','many red and white stripes and a blue box of white stars','许多红白条纹和带白星的蓝色方框','خطوط حمراء وبيضاء كثيرة ومربع أزرق فيه نجوم بيضاء'),
 'ca':T('daun maple merah di antara dua pita merah','a red maple leaf between two red bands','两条红带之间的红色枫叶','ورقة قيقب حمراء بين شريطين أحمرين'),
 'mx':T('tiga pita tegak hijau-putih-merah dengan lambang burung di tengah','three vertical green, white and red bands with a bird emblem in the middle','绿、白、红三条竖带，中间有鸟形徽章','ثلاثة أشرطة عمودية خضراء وبيضاء وحمراء وشعار طائر في الوسط'),
 'br':T('belah ketupat kuning dan lingkaran biru pada latar hijau','a yellow diamond and a blue circle on green','绿底上的黄色菱形和蓝色圆形','معين أصفر ودائرة زرقاء على خلفية خضراء'),
 'ar':T('pita biru muda-putih-biru muda dengan matahari di tengah','light blue, white and light blue bands with a sun in the center','浅蓝、白、浅蓝横带，中间有太阳','أشرطة زرقاء فاتحة وبيضاء وزرقاء فاتحة مع شمس في الوسط'),
 'gb':T('garis silang merah-putih pada latar biru','red and white crossing lines on blue','蓝底上的红白交叉线','خطوط حمراء وبيضاء متقاطعة على خلفية زرقاء'),
 'fr':T('tiga pita tegak biru-putih-merah tanpa lambang','three vertical blue, white and red bands with no emblem','蓝、白、红三条竖带，没有徽章','ثلاثة أشرطة عمودية زرقاء وبيضاء وحمراء دون شعار'),
 'it':T('tiga pita tegak hijau-putih-merah tanpa lambang','three vertical green, white and red bands with no emblem','绿、白、红三条竖带，没有徽章','ثلاثة أشرطة عمودية خضراء وبيضاء وحمراء دون شعار'),
 'de':T('tiga pita mendatar hitam-merah-kuning','three horizontal black, red and yellow bands','黑、红、黄三条横带','ثلاثة أشرطة أفقية سوداء وحمراء وصفراء'),
 'es':T('pita merah-kuning-merah dengan lambang pada pita kuning','red, yellow and red bands with an emblem on the yellow band','红、黄、红横带，黄色带上有徽章','أشرطة حمراء وصفراء وحمراء مع شعار على الشريط الأصفر'),
 'eg':T('pita merah-putih-hitam dengan burung emas di tengah','red, white and black bands with a golden bird in the center','红、白、黑横带，中间有金色鸟','أشرطة حمراء وبيضاء وسوداء مع طائر ذهبي في الوسط'),
 'ke':T('pita hitam-merah-hijau dengan perisai di tengah','black, red and green bands with a shield in the center','黑、红、绿横带，中间有盾牌','أشرطة سوداء وحمراء وخضراء مع درع في الوسط'),
 'za':T('bentuk huruf Y hijau dengan enam warna pada bendera','a green Y shape on a flag with six colors','六色旗上的绿色Y形','شكل حرف Y أخضر على علم بستة ألوان'),
 'ng':T('tiga pita tegak hijau-putih-hijau','three vertical green, white and green bands','绿、白、绿三条竖带','ثلاثة أشرطة عمودية خضراء وبيضاء وخضراء'),
 'th':T('lima pita mendatar merah-putih-biru-putih-merah','five horizontal red, white, blue, white and red bands','红、白、蓝、白、红五条横带','خمسة أشرطة أفقية حمراء وبيضاء وزرقاء وبيضاء وحمراء'),
 'my':T('garis merah-putih dengan bulan sabit kuning dalam kotak biru','red and white stripes with a yellow crescent in a blue box','红白条纹，蓝色方框内有黄色新月','خطوط حمراء وبيضاء وهلال أصفر داخل مربع أزرق'),
}
CLUE=T('Bendera mana yang memiliki {detail}?','Which flag has {detail}?','哪面国旗有{detail}？','أي علم فيه {detail}؟')
flagclues=[]
for code in codes:
 target=f'flag-{code}';others=R.sample([a for a in flagassets if a!=target],2)
 flagclues.append(choose([target,*others],[target],fmt(CLUE,detail=descriptions[code]),'clue'))
flags=worksheets('world-flags',[
 ('clue',flagclues),('match',[match(x) for x in sets(flagassets,24,2,21)]),
 ('memory',[memory(x) for x in sets(flagassets,24,3,22)]),
 ('pattern',[pattern(x,i) for i,x in enumerate(sets(flagassets,24,3,23))]),
])

toys=['game-top','game-congklak','game-hopscotch','game-puzzle','football','basketball','badminton-racket','tennis-racket','kite','building-blocks','skateboard','tent']
toy_clues={
 'game-top':T('Aku bisa berputar dengan satu ujung di bawah. Mainan apakah aku?','I spin on one pointed end. Which toy am I?','我能用一端着地旋转。我是什么玩具？','أدور على طرف واحد مدبب. أي لعبة أنا؟'),
 'game-congklak':T('Aku adalah papan panjang dengan banyak lubang kecil untuk biji permainan. Apakah aku?','I am a long board with small cups for game counters. What am I?','我是带有许多放棋子的小洞的长棋盘。我是什么？','أنا لوح طويل فيه حفر صغيرة لقطع اللعب. ما أنا؟'),
 'game-hopscotch':T('Di permainanku, kamu melompat dari kotak ke kotak di lantai. Permainan apa ini?','In this game you hop from one ground square to another. Which game is it?','这个游戏要在地上的格子之间跳跃。是什么游戏？','في هذه اللعبة تقفز بين مربعات على الأرض. ما اللعبة؟'),
 'game-puzzle':T('Potonganku saling menyambung untuk menjadi satu gambar. Apakah aku?','My pieces fit together to make one picture. What am I?','我的小块能拼成一幅图。我是什么？','تتصل قطعي لتكون صورة واحدة. ما أنا؟'),
 'football':T('Bola yang mana biasa ditendang menuju gawang dalam sepak bola?','Which ball is kicked toward a goal in football?','足球比赛中，哪种球被踢向球门？','أي كرة تركل نحو المرمى في كرة القدم؟'),
 'basketball':T('Bola yang mana dipantulkan dan dilempar ke keranjang dalam bola basket?','Which ball is bounced and thrown into a basket in basketball?','篮球比赛中，哪种球被拍打后投向篮筐？','أي كرة تنطط ثم ترمى في السلة في كرة السلة؟'),
 'badminton-racket':T('Raket yang mana digunakan untuk memukul kok dalam bulu tangkis?','Which racket is used to hit a shuttlecock in badminton?','哪种球拍用来打羽毛球？','أي مضرب يستخدم لضرب الريشة في تنس الريشة؟'),
 'tennis-racket':T('Raket yang mana digunakan untuk memukul bola tenis?','Which racket is used to hit a tennis ball?','哪种球拍用来打网球？','أي مضرب يستخدم لضرب كرة التنس؟'),
 'kite':T('Aku terbang tertiup angin dan dipegang dengan tali. Mainan apakah aku?','I fly in the wind while someone holds my string. Which toy am I?','风吹时我会飞起来，有人握着我的线。我是什么玩具？','أطير مع الريح بينما يمسك أحد بخيطي. أي لعبة أنا؟'),
 'building-blocks':T('Mainan mana dapat ditumpuk untuk membangun menara?','Which toys can be stacked to build a tower?','哪种玩具可以叠起来搭高塔？','أي ألعاب يمكن تكديسها لبناء برج؟'),
 'skateboard':T('Aku adalah papan dengan roda kecil di bawahnya. Apakah aku?','I am a board with small wheels underneath. What am I?','我是一块下面有小轮子的板。我是什么？','أنا لوح تحته عجلات صغيرة. ما أنا؟'),
 'tent':T('Aku memiliki pintu kain dan menjadi tempat bermain kemah. Apakah aku?','I have a fabric doorway for pretend camping. What am I?','我有布门，可以用来玩露营游戏。我是什么？','لدي باب من القماش للعب التخييم. ما أنا؟'),
}
toyrounds=[]
for n in range(24):
 target=toys[n%len(toys)];others=R.sample([a for a in toys if a!=target],2)
 toyrounds.append(choose([target,*others],[target],toy_clues[target],'clue'))
toyworks=worksheets('games-toys',[
 ('clue',toyrounds),('match',[match(x) for x in sets(toys,24,2,31)]),
 ('memory',[memory(x) for x in sets(toys,24,3,32)]),
 ('pattern',[pattern(x,i) for i,x in enumerate(sets(toys,24,3,33))]),
])

# The pictures themselves show the actions. Prompts never infer invisible intentions.
scenes=['habit-sharing','habit-waiting','habit-tidying','habit-helping','habit-greeting','habit-thanking','habit-asking-help','habit-gentle','habit-apologizing']
stories={
 'habit-sharing':T('Nara ingin berbagi balok dengan teman. Pilih gambar berbagi balok.','Nara wants to share blocks with a friend. Choose the sharing picture.','娜拉想和朋友分享积木。请选择分享积木的图片。','تريد نارا مشاركة المكعبات مع صديق. اختر صورة مشاركة المكعبات.'),
 'habit-waiting':T('Teman sedang memakai mobil mainan. Pilih gambar menunggu giliran.','A friend is using the toy car. Choose the picture of waiting for a turn.','朋友正在玩小汽车。请选择等待轮到自己的图片。','يلعب صديق بالسيارة. اختر صورة انتظار الدور.'),
 'habit-tidying':T('Waktu bermain sudah selesai. Pilih gambar menyimpan mainan.','Playtime has finished. Choose the picture of putting toys away.','游戏时间结束了。请选择收好玩具的图片。','انتهى وقت اللعب. اختر صورة ترتيب الألعاب.'),
 'habit-helping':T('Setelah bermain rumah-rumahan, kita membantu membawa bantal. Mana gambarnya?','After pretend house play, we help carry a cushion. Which picture shows this?','玩过家家后，我们帮忙搬靠垫。是哪一张图片？','بعد لعب البيت نساعد في حمل وسادة. أي صورة توضح ذلك؟'),
 'habit-greeting':T('Teman datang untuk bermain. Pilih gambar menyapa dengan ramah.','A friend arrives to play. Choose the friendly greeting picture.','朋友来一起玩。请选择友好打招呼的图片。','يأتي صديق للعب. اختر صورة إلقاء التحية بلطف.'),
 'habit-thanking':T('Seseorang memberikan buku untuk bermain cerita. Pilih gambar mengucapkan terima kasih.','Someone gives us a book for story play. Choose the picture of saying thank you.','有人递来讲故事的书。请选择说谢谢的图片。','يعطينا أحد كتابا للعب القصص. اختر صورة قول شكرا.'),
 'habit-asking-help':T('Kita boleh meminta bantuan saat bermain. Mana gambar anak meminta bantuan pendamping?','We can ask for help during play. Which picture shows asking a grown-up?','玩的时候可以求助。哪张图是向大人求助？','يمكننا طلب المساعدة أثناء اللعب. أي صورة تظهر طلب المساعدة من شخص بالغ؟'),
 'habit-gentle':T('Kita bermain bersama anak yang lebih kecil. Pilih gambar bermain dengan lembut.','We are playing with a younger child. Choose the picture of gentle play.','我们陪更小的孩子玩。请选择温柔玩耍的图片。','نلعب مع طفل أصغر. اختر صورة اللعب برفق.'),
 'habit-apologizing':T('Saat bermain, kita tidak sengaja menyenggol teman. Pilih gambar mengucapkan maaf.','During play, we accidentally bump a friend. Choose the picture of saying sorry.','玩耍时不小心碰到了朋友。请选择说对不起的图片。','أثناء اللعب نصطدم بصديق دون قصد. اختر صورة قول آسف.'),
}
onerounds=[]
for n in range(24):
 target=scenes[n%len(scenes)]
 other=R.sample([a for a in scenes if a!=target],2)
 onerounds.append(choose([target,*other],[target],stories[target]))
MANY=T('Pilih kedua gambar ini: {a} dan {b}.','Choose both of these pictures: {a} and {b}.','请选择这两种行为的图片：{a}和{b}。','اختر هاتين الصورتين: {a} و{b}.')
manyrounds=[]
for a,b in sets(scenes,24,2,41):
 distractors=R.sample([x for x in scenes if x not in (a,b)],2)
 manyrounds.append(choose([a,b,*distractors],[a,b],fmt(MANY,a=L[a],b=L[b]),'choose-many'))
rules=worksheets('games-rules',[
 ('choose-one',onerounds),('choose-many',manyrounds),
 ('match',[match(x) for x in sets(scenes,24,2,42)]),
 ('memory',[memory(x) for x in sets(scenes,24,3,43)]),
])

records={'world-countries':world,'world-flags':flags,'games-toys':toyworks,'games-rules':rules}
info={
 'world-countries':('earth',T('Peta dan Negara','Maps and Countries','地图与国家','الخرائط والبلدان'),T('Jelajahi penanda negara, cocokkan bendera, ingat gambar, dan lanjutkan pola.','Explore country markers, match flags, remember pictures and continue patterns.','探索国家标记、配对国旗、记忆图片和继续规律。','استكشف علامات البلدان وطابق الأعلام وتذكر الصور وأكمل الأنماط.')),
 'world-flags':('earth',T('Bendera Dunia','Flags of the World','世界国旗','أعلام العالم'),T('Amati warna dan bentuk 24 bendera melalui petunjuk, pasangan, ingatan, dan pola.','Explore colors and shapes of 24 flags through clues, matching, memory and patterns.','通过线索、配对、记忆和规律，观察24面国旗的颜色与形状。','استكشف ألوان وأشكال 24 علما عبر الأدلة والمطابقة والذاكرة والأنماط.')),
 'games-toys':('game-top',T('Permainan dan Mainan','Games and Toys','游戏与玩具','الألعاب والدمى'),T('Kenali gasing, congklak, engklek, puzzle, dan mainan untuk berbagai cara bermain.','Meet spinning tops, congklak, hopscotch, puzzles and toys for different kinds of play.','认识陀螺、康克拉棋、跳房子、拼图和不同玩法的玩具。','تعرف إلى البلبل وكونغكلاك والحجلة والأحاجي وألعاب متنوعة.')),
 'games-rules':('habit-sharing',T('Bermain Bersama dengan Baik','Playing Kindly Together','友好地一起玩','نلعب معا بلطف'),T('Kenali berbagi, giliran, meminta bantuan, dan merapikan melalui cerita bergambar.','Explore sharing, taking turns, asking for help and tidying through picture stories.','通过图片故事认识分享、轮流、求助和整理。','تعرف إلى المشاركة وتبادل الأدوار وطلب المساعدة والترتيب عبر قصص مصورة.')),
}
categories=[]
for cat,works in records.items():
 asset,title,description=info[cat]
 categories.append(dict(id=cat,group='world' if cat.startswith('world-') else 'games',asset=asset,title=title,description=description,engine=works[0]['engine'],age=3,ageRange=[3,6],worksheetCount=24,activityKinds=list(dict.fromkeys(w['activityKind'] for w in works))))
 (OUT/'bundles'/f'{cat}.json').write_text(json.dumps(works,ensure_ascii=False,separators=(',',':')))
(OUT/'categories.json').write_text(json.dumps(categories,ensure_ascii=False,indent=2))
(OUT/'labels.json').write_text(json.dumps(L,ensure_ascii=False,indent=2))
artlabels={f'flag-{code}':fmt(T('Bendera {name}','Flag of {name}','{name}国旗','علم {name}'),name=C[code]['name']) for code in codes}
artlabels.update({a:L[a] for a in ['game-top','game-congklak','game-hopscotch','game-puzzle']})
(OUT/'art-labels.json').write_text(json.dumps(artlabels,ensure_ascii=False,indent=2))

# Semantic signatures ignore card order and internal IDs. Every worksheet has four
# distinct tasks; each full taskset differs within its category.
def signature(r):
 byid={o['id']:o['asset'] for o in r['options']}
 return json.dumps(dict(engine=r['engine'],kind=r['activityKind'],instruction=r['instruction'],assets=sorted(byid.values()),targets=sorted(byid[x] for x in r['answer']),pattern=[x and x['asset'] for x in r.get('patternItems',[])],map=r.get('map')),ensure_ascii=False,sort_keys=True)
def check_text(v):
 if isinstance(v,dict):
  if 'id' in v and 'en' in v:
   assert all(isinstance(v.get(l),str) and v[l].strip() for l in LANGS),v
  for a in v.values():check_text(a)
 elif isinstance(v,list):
  for a in v:check_text(a)
audit={}
for cat,works in records.items():
 assert len(works)==24
 kindset={w['activityKind'] for w in works};engines={w['engine'] for w in works}
 assert len(kindset)>=4 and len(engines)>=3
 tasksets=[]
 for w in works:
  assert len(w['rounds'])==4
  sigs=[signature(r) for r in w['rounds']];assert len(set(sigs))==4,w['id']
  tasksets.append(tuple(sorted(sigs)))
  check_text(w)
  for r in w['rounds']:
   ids={p['id'] for p in r['options']};assert len(ids)==len(r['options'])
   assert all(a in ids for a in r['answer'])
   for p in r['options']:assert p['asset'] in L
   if r['engine']=='pair':
    right={p['id']:p['asset'] for p in r['rightOptions']}
    left={p['id']:p['asset'] for p in r['options']}
    assert len(r['pairs'])==len(ids)
    assert all(left[p['left']]==right[p['right']] for p in r['pairs'])
   if r['engine']=='pattern':assert sum(p is None for p in r['patternItems'])==1
   if r['engine']=='map':
    places=r['map']['places'];assert {p['option'] for p in places}==ids
    assert len(r['answer'])==1
    assert all(min(distance(a['country'],b['country']) for a,b in itertools.combinations(places,2))>=.22 for _ in [0])
    assert all(abs(p['lat'])<=90 and abs(p['lng'])<=180 for p in places)
 assert len(set(tasksets))==24,cat
 audit[cat]=dict(worksheets=24,rounds=96,activityKinds=sorted(kindset),engines=sorted(engines),distinctTasksets=24)
actual_min_distance=min(distance(a['country'],b['country']) for r in maprounds for a,b in itertools.combinations(r['map']['places'],2))
audit['total']=dict(worksheets=96,rounds=384,mapRounds=32,countries=24,fourLanguageText=True,minimumMapMarkerDistance=.22,actualMinimumMapMarkerDistance=actual_min_distance,mapDistanceNormalization='Both axes normalized by map width; longitude/360 and latitude/360 for a 2:1 map',minimumMarkerDistanceAt244px=actual_min_distance*244,valid=True)
audit['sources']=[{'title':'Verified geography and flag assets','path':str(GEO),'flagSource':'https://github.com/lipis/flag-icons','mapSource':'https://www.naturalearthdata.com/'}]
(OUT/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2))
print(json.dumps(audit,ensure_ascii=False,indent=2))
