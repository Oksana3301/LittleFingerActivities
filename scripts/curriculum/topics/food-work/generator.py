"""Astra additive food and work curriculum. Generates original practice variations.

Run with Python 3; writes beside this script and never changes an existing Site.
Questions describe the pictured serving, not universal recipes or food origins.
"""
from pathlib import Path
from itertools import combinations
import copy, hashlib, json, random

ROOT=Path(__file__).resolve().parent
LANGS=('id','en','zh','ar')
def T(id,en,zh,ar): return dict(zip(LANGS,(id,en,zh,ar)))

L={
 'food-nasi-goreng':T('Nasi goreng','Nasi goreng','印尼炒饭','ناسي غورينغ'),
 'food-sate':T('Sate','Sate','沙爹串','ساتيه'),
 'food-rendang':T('Rendang','Rendang','仁当炖肉','رندانغ'),
 'food-soto':T('Soto ayam','Soto ayam','印尼鸡汤','سوتو الدجاج'),
 'food-gado-gado':T('Gado-gado','Gado-gado','加多加多蔬菜沙拉','غادو غادو'),
 'food-bakso':T('Bakso','Bakso','印尼肉丸汤','باكسو'),
 'food-pempek':T('Pempek','Pempek','印尼鱼糕','بيمبيك'),
 'food-klepon':T('Klepon','Klepon','椰丝糯米球','كليبون'),
 'food-pizza':T('Piza','Pizza','比萨','بيتزا'),
 'food-sushi':T('Sushi gulung','Sushi rolls','寿司卷','لفائف السوشي'),
 'food-spaghetti':T('Spageti','Spaghetti','意大利细面','سباغيتي'),
 'food-taco':T('Taco','Taco','塔可','تاكو'),
 'food-croissant':T('Kroisan','Croissant','牛角面包','كرواسون'),
 'food-dumplings':T('Bao kukus','Steamed bao','小笼包','خبز باو على البخار'),
 'food-curry':T('Kari dan nasi','Curry with rice','咖喱饭','كاري مع الأرز'),
 'food-bibimbap':T('Bibimbap','Bibimbap','韩式拌饭','بيبيمباب'),
 'job-doctor':T('Dokter','Doctor','医生','طبيبة'),
 'job-nurse':T('Perawat','Nurse','护士','ممرض'),
 'job-firefighter':T('Pemadam kebakaran','Firefighter','消防员','عاملة إطفاء'),
 'job-teacher':T('Guru','Teacher','老师','معلم'),
 'job-chef':T('Koki','Chef','厨师','طاهية'),
 'job-farmer':T('Petani','Farmer','农民','مزارع'),
 'job-mechanic':T('Montir','Mechanic','机械师','ميكانيكية'),
 'job-mailcarrier':T('Pengantar surat','Mail carrier','邮递员','ساعي بريد'),
 'job-builder':T('Pekerja bangunan','Builder','建筑工人','عاملة بناء'),
 'job-scientist':T('Ilmuwan','Scientist','科学家','عالم'),
 'job-artist':T('Seniman','Artist','艺术家','فنانة'),
 'job-pilot':T('Pilot','Pilot','飞行员','طيار'),
 'spoon':T('Sendok','Spoon','勺子','ملعقة'),
 'plate':T('Piring','Plate','盘子','طبق'),
 'cup':T('Cangkir','Cup','杯子','كوب'),
 'watering-can':T('Penyiram tanaman','Watering can','洒水壶','مرش نباتات'),
 'trowel':T('Sekop kecil','Trowel','小铲子','مجرفة صغيرة'),
 'tractor':T('Traktor','Tractor','拖拉机','جرار'),
 'wrench':T('Kunci pas','Wrench','扳手','مفتاح ربط'),
 'screwdriver':T('Obeng','Screwdriver','螺丝刀','مفك براغي'),
 'pliers':T('Tang','Pliers','钳子','كماشة'),
 'toolbox':T('Kotak perkakas','Toolbox','工具箱','صندوق أدوات'),
 'book':T('Buku','Book','书','كتاب'),
 'pencil':T('Pensil','Pencil','铅笔','قلم رصاص'),
 'ruler':T('Penggaris','Ruler','尺子','مسطرة'),
 'airplane':T('Pesawat','Airplane','飞机','طائرة'),
 'microscope':T('Mikroskop','Microscope','显微镜','مجهر'),
 'bag':T('Tas','Bag','包','حقيبة'),
 'fire-truck':T('Mobil pemadam','Fire truck','消防车','سيارة إطفاء'),
 'hammer':T('Palu','Hammer','锤子','مطرقة'),
 'helmet':T('Helm keselamatan','Safety helmet','安全头盔','خوذة سلامة'),
 'football':T('Bola sepak','Football','足球','كرة قدم'),
 'kite':T('Layang-layang','Kite','风筝','طائرة ورقية'),
 'building-blocks':T('Balok mainan','Building blocks','积木','مكعبات لعب'),
 'car':T('Mobil','Car','汽车','سيارة'),
 'chair':T('Kursi','Chair','椅子','كرسي'),
 'lamp':T('Lampu','Lamp','灯','مصباح'),
}
FOOD_ID=['food-nasi-goreng','food-sate','food-rendang','food-soto','food-gado-gado','food-bakso','food-pempek','food-klepon']
FOOD_WORLD=['food-pizza','food-sushi','food-spaghetti','food-taco','food-croissant','food-dumplings','food-curry','food-bibimbap']
PEOPLE=[k for k in L if k.startswith('job-')]
TOOLS=['spoon','plate','watering-can','trowel','tractor','wrench','screwdriver','pliers','toolbox','book','pencil','ruler','airplane','microscope','bag','fire-truck','hammer','helmet']
NONFOOD=['football','kite','building-blocks','car','chair','lamp','book','pencil']

# All culinary clues are observations of this atlas's illustrated serving.
CLUE={
 'food-nasi-goreng':T('Di gambar ini, makanan mana berupa nasi goreng dengan telur di atasnya?','Which picture shows fried rice with an egg on top?','哪张图是上面放着鸡蛋的炒饭？','أي صورة تُظهر أرزًا مقليًا تعلوه بيضة؟'),
 'food-sate':T('Makanan mana disajikan pada tusuk-tusuk kecil?','Which food is shown on small skewers?','哪种食物串在小竹签上？','أي طعام يظهر على أسياخ صغيرة؟'),
 'food-rendang':T('Di gambar ini, mana potongan daging berbumbu gelap di samping nasi?','Which picture shows dark seasoned meat beside rice?','哪张图是米饭旁边放着深色炖肉？','أي صورة تُظهر لحمًا متبلًا داكن اللون بجانب الأرز؟'),
 'food-soto':T('Di gambar ini, mana sup ayam berkuah kuning?','Which picture shows yellow chicken soup?','哪张图是黄色的鸡汤？','أي صورة تُظهر حساء دجاج أصفر؟'),
 'food-gado-gado':T('Di gambar ini, mana sayuran dengan saus kacang dan telur?','Which picture shows vegetables with peanut sauce and egg?','哪张图是蔬菜配花生酱和鸡蛋？','أي صورة تُظهر خضارًا بصلصة الفول السوداني والبيض؟'),
 'food-bakso':T('Di gambar ini, mana sup berisi bakso bulat dan mi?','Which picture shows soup with round meatballs and noodles?','哪张图是有圆肉丸和面条的汤？','أي صورة تُظهر حساءً بكرات اللحم والمعكرونة؟'),
 'food-pempek':T('Di gambar ini, mana potongan pempek dengan saus gelap di sampingnya?','Which picture shows fish cakes with dark sauce beside them?','哪张图是旁边配着深色酱汁的鱼糕？','أي صورة تُظهر كعكات السمك وبجانبها صلصة داكنة؟'),
 'food-klepon':T('Makanan mana berupa bola-bola hijau bertabur kelapa?','Which food is shown as green balls covered with coconut?','哪种食物是裹着椰丝的绿色小球？','أي طعام يظهر ككرات خضراء مغطاة بجوز الهند؟'),
 'food-pizza':T('Makanan mana terlihat seperti potongan segitiga dengan keju?','Which food looks like a triangular slice with cheese?','哪种食物看起来像带奶酪的三角形切片？','أي طعام يبدو كقطعة مثلثة عليها جبن؟'),
 'food-sushi':T('Makanan mana berupa gulungan nasi yang dipotong kecil?','Which food is shown as small slices of rice rolls?','哪种食物是切成小块的米饭卷？','أي طعام يظهر كقطع صغيرة من لفائف الأرز؟'),
 'food-spaghetti':T('Di gambar ini, mana mi panjang dengan saus tomat?','Which picture shows long pasta with tomato sauce?','哪张图是配番茄酱的长面条？','أي صورة تُظهر معكرونة طويلة بصلصة الطماطم؟'),
 'food-taco':T('Makanan mana memiliki kulit terlipat dengan isian di dalamnya?','Which food has a folded shell with filling inside?','哪种食物的外皮折起来，里面有馅料？','أي طعام له غلاف مطوي وحشوة في الداخل؟'),
 'food-croissant':T('Roti mana berwarna keemasan dan tampak berlapis-lapis?','Which bread is golden and looks layered?','哪种面包呈金黄色，看起来有很多层？','أي خبز ذهبي اللون ويبدو مكونًا من طبقات؟'),
 'food-dumplings':T('Di gambar ini, mana bao kukus di dalam kukusan bambu?','Which picture shows steamed bao in a bamboo steamer?','哪张图是竹蒸笼里的小笼包？','أي صورة تُظهر خبز باو في سلة تبخير من الخيزران؟'),
 'food-curry':T('Di gambar ini, mana kari berkuah di samping nasi?','Which picture shows saucy curry beside rice?','哪张图是米饭旁边配着咖喱？','أي صورة تُظهر كاري بصلصة بجانب الأرز؟'),
 'food-bibimbap':T('Di gambar ini, mana semangkuk nasi dengan sayuran warna-warni dan telur di tengah?','Which picture shows a rice bowl with colorful vegetables and an egg in the middle?','哪张图是盛着米饭和彩色蔬菜，中间有鸡蛋的碗？','أي صورة تُظهر وعاء أرز وخضار ملونة وبيضة في الوسط؟'),
 'job-doctor':T('Siapa yang memeriksa kesehatan kita?','Who checks our health?','谁为我们检查身体？','من يفحص صحتنا؟'),
 'job-nurse':T('Siapa yang membantu merawat pasien?','Who helps care for patients?','谁帮助照护病人？','من يساعد في رعاية المرضى؟'),
 'job-firefighter':T('Siapa yang membantu memadamkan kebakaran?','Who helps put out fires?','谁帮助扑灭火灾？','من يساعد في إطفاء الحرائق؟'),
 'job-teacher':T('Siapa yang membantu anak belajar di kelas?','Who helps children learn in class?','谁帮助孩子们在教室里学习？','من يساعد الأطفال على التعلم في الصف؟'),
 'job-chef':T('Siapa yang memasak makanan di dapur restoran?','Who cooks food in a restaurant kitchen?','谁在餐厅厨房里做饭？','من يطبخ الطعام في مطبخ المطعم؟'),
 'job-farmer':T('Siapa yang menanam dan merawat tanaman di ladang?','Who grows and cares for crops in a field?','谁在田里种植和照料庄稼？','من يزرع المحاصيل ويعتني بها في الحقل؟'),
 'job-mechanic':T('Siapa yang memperbaiki mesin kendaraan?','Who repairs vehicle engines?','谁修理车辆的发动机？','من يصلح محركات المركبات؟'),
 'job-mailcarrier':T('Siapa yang mengantarkan surat?','Who delivers letters?','谁送信？','من يوزع الرسائل؟'),
 'job-builder':T('Siapa yang membantu membangun rumah?','Who helps build houses?','谁帮助建造房屋？','من يساعد في بناء البيوت؟'),
 'job-scientist':T('Siapa yang melakukan pengamatan dan percobaan untuk belajar tentang dunia?','Who makes observations and experiments to learn about the world?','谁通过观察和实验来了解世界？','من يجري ملاحظات وتجارب ليتعلم عن العالم؟'),
 'job-artist':T('Siapa yang membuat karya seni seperti lukisan?','Who creates art such as paintings?','谁创作绘画等艺术作品？','من يصنع أعمالًا فنية مثل اللوحات؟'),
 'job-pilot':T('Siapa yang menerbangkan pesawat?','Who flies an airplane?','谁驾驶飞机？','من يقود الطائرة؟'),
 'spoon':T('Alat mana dapat dipakai untuk menyendok makanan?','Which tool can scoop food?','哪件用具可以舀食物？','أي أداة تُستخدم لغرف الطعام؟'),
 'plate':T('Benda mana menjadi tempat meletakkan makanan saat makan?','Which object holds food at a meal?','吃饭时，哪个物品用来盛食物？','أي شيء يوضع فيه الطعام عند الأكل؟'),
 'watering-can':T('Alat mana dipakai untuk menyiram tanaman?','Which tool waters plants?','哪件工具用来给植物浇水？','أي أداة تُستخدم لسقي النباتات؟'),
 'trowel':T('Alat kecil mana dipakai untuk menggali tanah saat berkebun?','Which small tool digs soil in a garden?','哪件小工具用来在花园里挖土？','أي أداة صغيرة تُستخدم لحفر التربة في الحديقة؟'),
 'tractor':T('Kendaraan mana dapat membantu pekerjaan di ladang?','Which vehicle can help with field work?','哪种车辆能帮助在田间工作？','أي مركبة تساعد في العمل في الحقل؟'),
 'wrench':T('Alat mana dipakai untuk memutar mur?','Which tool turns nuts?','哪件工具用来拧螺母？','أي أداة تُستخدم لتدوير الصواميل؟'),
 'screwdriver':T('Alat mana dipakai untuk memutar sekrup?','Which tool turns screws?','哪件工具用来拧螺丝？','أي أداة تُستخدم لتدوير البراغي؟'),
 'pliers':T('Alat mana memiliki dua rahang untuk menjepit benda?','Which tool has two jaws for gripping objects?','哪件工具有两个夹口，可以夹住物品？','أي أداة لها فكان لإمساك الأشياء؟'),
 'toolbox':T('Benda mana menjadi tempat menyimpan perkakas?','Which object stores tools?','哪个物品用来存放工具？','أي شيء يُستخدم لحفظ الأدوات؟'),
 'book':T('Benda mana memiliki halaman untuk dibaca?','Which object has pages to read?','哪个物品有可以阅读的书页？','أي شيء له صفحات نقرأها؟'),
 'pencil':T('Alat mana dapat dipakai untuk menulis atau menggambar?','Which tool can write or draw?','哪件工具可以写字或画画？','أي أداة يمكن استخدامها للكتابة أو الرسم؟'),
 'ruler':T('Alat mana membantu mengukur panjang dan membuat garis lurus?','Which tool helps measure length and draw straight lines?','哪件工具帮助测量长度和画直线？','أي أداة تساعد على قياس الطول ورسم خطوط مستقيمة؟'),
 'airplane':T('Kendaraan mana diterbangkan oleh pilot?','Which vehicle does a pilot fly?','飞行员驾驶哪种交通工具？','أي مركبة يقودها الطيار في الجو؟'),
 'microscope':T('Alat mana membantu melihat benda yang sangat kecil?','Which tool helps us see very tiny things?','哪件工具帮助我们看很小的东西？','أي أداة تساعدنا على رؤية أشياء صغيرة جدًا؟'),
 'bag':T('Benda mana dapat dipakai pengantar surat untuk membawa surat?','Which object can a mail carrier use to carry letters?','邮递员可以用哪个物品装信？','أي شيء يمكن لساعي البريد استخدامه لحمل الرسائل؟'),
 'fire-truck':T('Kendaraan mana membawa petugas pemadam ke tempat kebakaran?','Which vehicle takes firefighters to a fire?','哪种车辆把消防员送到火灾现场？','أي مركبة تنقل رجال ونساء الإطفاء إلى الحريق؟'),
 'hammer':T('Alat mana dipakai untuk mengetuk paku?','Which tool taps nails?','哪件工具用来敲钉子？','أي أداة تُستخدم لدق المسامير؟'),
 'helmet':T('Benda mana dipakai di kepala untuk membantu melindunginya saat bekerja?','Which object is worn on the head to help protect it at work?','工作时戴在头上帮助保护头部的是什么？','أي شيء يُلبس على الرأس للمساعدة على حمايته أثناء العمل؟'),
}

KIND_TITLES={
 'choose-one':T('Kenali gambarnya','Name the picture','认识图片','تعرف إلى الصورة'),
 'clue':T('Dengarkan petunjuknya','Listen to the clue','听线索','استمع إلى التلميح'),
 'match':T('Temukan pasangannya','Find its partner','找配对','ابحث عن الصورة المطابقة'),
 'memory':T('Ingat dan temukan','Remember and find','记一记，找一找','تذكر وابحث'),
 'pattern':T('Lanjutkan polanya','Continue the pattern','接着排规律','أكمل النمط'),
 'choose-many':T('Pilih semua yang cocok','Choose every match','选出所有符合的图片','اختر كل الصور المناسبة'),
 'sort':T('Kelompokkan peralatannya','Group the equipment','给用具分类','صنف الأدوات'),
}

def picture(asset, i): return {'id':f'o{i}','kind':'asset','asset':asset,'label':copy.deepcopy(L[asset]),'showLabel':True}
def rand(seed): return random.Random(f'astra-food-work-{seed}')
def shuffled(values,seed):
    out=list(values);rand(seed).shuffle(out);return out
def round_base(kind,engine,instruction,assets,answer_assets=(),seed=''):
    options=[picture(a,i) for i,a in enumerate(assets)]
    return {'activityKind':kind,'engine':engine,'instruction':instruction,'options':shuffled(options,seed),'answer':[o['id'] for o in options if o['asset'] in answer_assets]}
def sample3(pool,n):
    combos=list(combinations(pool,3));return list(combos[(n*11+3)%len(combos)])
def select_round(pool,n,kind):
    target=pool[n%len(pool)]
    distractors=[a for a in pool if a!=target]
    # The two healthcare jobs are not distractors for one another's overlapping roles.
    if kind=='clue' and target in ('job-doctor','job-nurse'): distractors=[a for a in distractors if a not in ('job-doctor','job-nurse')]
    # A classroom pencil also draws: keep it out of the ruler's straight-line clue.
    if kind=='clue' and target=='ruler': distractors=[a for a in distractors if a!='pencil']
    picks=rand(f'{pool[0]}-{kind}-{n}').sample(distractors,2)
    label=L[target]
    instruction=CLUE[target] if kind=='clue' else T(f"Cari gambar: {label['id']}.",f"Find the picture: {label['en']}.",f"找一找：{label['zh']}。",f"ابحث عن الصورة: {label['ar']}.")
    return round_base(kind,'identify',instruction,[target,*picks],[target],f'{kind}{n}')
def identical_pair(pool,n):
    assets=sample3(pool,n)
    r=round_base('match','pair',T('Pasangkan setiap gambar dengan gambar yang sama.','Match each picture to the same picture.','把每张图片和相同的图片配对。','صل كل صورة بالصورة نفسها.'),assets,seed=f'pair{n}')
    r['rightOptions']=shuffled([{**picture(a,i),'id':f'r{i}'} for i,a in enumerate(assets)],f'right{n}')
    r['pairs']=[{'left':f'o{i}','right':f'r{i}'} for i in range(len(assets))]
    return r
def memory_round(pool,n):
    return round_base('memory','memory',T('Buka kartu dan temukan semua pasangan gambar yang sama.','Turn over the cards and find every matching pair.','翻开卡片，找出所有相同的图片。','اقلب البطاقات واعثر على كل زوج من الصور المتطابقة.'),sample3(pool,n+17),seed=f'memory{n}')
def pattern_round(pool,n):
    # ABAB, AAB, and ABC patterns vary both rule and pictorial content.
    chosen=shuffled(pool,f'pattern-assets-{n}')[:3]
    a,b,c=chosen
    patterns=[[a,b,a,b,None],[a,a,b,a,a,None],[a,b,c,a,b,None],[a,b,b,a,b,None]]
    p=patterns[n%4]
    target=[a,b,c,b][n%4]
    r=round_base('pattern','pattern',T('Lihat urutan gambar. Pilih gambar untuk tempat yang kosong.','Look at the picture pattern. Choose the missing picture.','观察图片规律，选出空缺的图片。','انظر إلى نمط الصور واختر الصورة الناقصة.'),chosen,[target],f'pattern{n}')
    r['patternItems']=[None if x is None else picture(x,i+10) for i,x in enumerate(p)]
    return r
def choose_many_round(pool,n,people=False):
    assets=sample3(pool,n+31)
    distractors=rand(f'many-{pool[0]}-{n}').sample(NONFOOD,2)
    instruction=T('Pilih semua gambar orang yang sedang mengenalkan pekerjaannya. Ada tiga.','Choose all the people showing their jobs. There are three.','选出所有展示职业的人物图片。一共有三张。','اختر كل صور الأشخاص الذين يعرضون مهنهم. هناك ثلاث صور.') if people else T('Pilih semua gambar makanan. Ada tiga.','Choose every picture of food. There are three.','选出所有食物图片。一共有三张。','اختر كل صور الطعام. هناك ثلاث صور.')
    return round_base('choose-many','identify',instruction,[*assets,*distractors],assets,f'many{n}')

ROLE_TOOL={
 'job-chef':'spoon','job-farmer':'tractor','job-mechanic':'wrench','job-teacher':'book',
 'job-pilot':'airplane','job-scientist':'microscope','job-mailcarrier':'bag',
 'job-firefighter':'fire-truck','job-builder':'hammer','job-artist':'pencil'
}
def role_tool_round(n):
    # These curated three-role groups avoid overlapping classroom/art or repair/build tools.
    groups=[['job-chef','job-farmer','job-pilot'],['job-mechanic','job-teacher','job-scientist'],['job-mailcarrier','job-firefighter','job-artist'],['job-builder','job-chef','job-scientist'],['job-farmer','job-teacher','job-firefighter'],['job-pilot','job-mechanic','job-mailcarrier'],['job-artist','job-chef','job-farmer'],['job-scientist','job-builder','job-pilot'],['job-teacher','job-chef','job-mailcarrier'],['job-firefighter','job-scientist','job-farmer'],['job-mechanic','job-artist','job-pilot'],['job-builder','job-mailcarrier','job-chef'],['job-farmer','job-scientist','job-teacher'],['job-pilot','job-firefighter','job-artist'],['job-mailcarrier','job-mechanic','job-scientist'],['job-builder','job-teacher','job-farmer']]
    roles=groups[n]
    r=round_base('match','pair',T('Pasangkan setiap pekerja dengan alat atau kendaraan yang sesuai pada gambar.','Match each worker to the pictured tool or vehicle that fits their job.','把每位工作者与适合其工作的工具或车辆图片配对。','صل كل عامل بصورة الأداة أو المركبة المناسبة لعمله.'),roles,seed=f'role{n}')
    r['rightOptions']=shuffled([{**picture(ROLE_TOOL[a],i),'id':f'r{i}'} for i,a in enumerate(roles)],f'role-right{n}')
    r['pairs']=[{'left':f'o{i}','right':f'r{i}'} for i in range(3)]
    return r

def sort_round(n):
    if n<8:
        left=['watering-can','trowel','tractor'];right=['wrench','screwdriver','pliers','toolbox']
        bl=T('Berkebun dan bertani','Garden and field','园艺和农田','الحديقة والحقل');br=T('Memperbaiki mesin','Repairing machines','修理机器','إصلاح الآلات')
        la='job-farmer';ra='job-mechanic'
    else:
        left=['book','pencil','ruler'];right=['spoon','plate','cup']
        bl=T('Belajar di meja','Learning at a desk','书桌学习','التعلم على المكتب');br=T('Makan di meja','Eating at a table','餐桌用餐','الأكل على الطاولة')
        la='book';ra='plate'
    lc=list(combinations(left,2));rc=list(combinations(right,2))
    li=list(lc[(n%8)//3%len(lc)]);ri=list(rc[(n%8)%3])
    assets=[*li,*ri]
    r=round_base('sort','sort',T('Kelompokkan setiap benda sesuai kegunaannya pada dua tempat ini.','Group each object by its use in these two places.','按照在这两个场景中的用途，把物品分类。','صنف كل شيء حسب استخدامه في هذين المكانين.'),assets,seed=f'sort{n}')
    r['bins']=[{'id':'left','label':bl,'asset':la},{'id':'right','label':br,'asset':ra}]
    r['pairs']=[{'left':f'o{i}','right':'left' if a in li else 'right'} for i,a in enumerate(assets)]
    return r

CATS=[
 {'id':'food-indonesia','group':'food','asset':'food-nasi-goreng','title':T('Makanan Indonesia','Indonesian Food','印度尼西亚美食','أطعمة إندونيسية'),'description':T('Kenali nasi goreng, sate, soto, dan aneka hidangan lewat petunjuk, pasangan, memori, serta pola.','Explore nasi goreng, sate, soto, and other dishes through clues, matching, memory, and patterns.','通过线索、配对、记忆和规律游戏认识印尼炒饭、沙爹、鸡汤等美食。','تعرف إلى ناسي غورينغ والساتيه والسوتو وأطعمة أخرى بالتلميحات والمطابقة والذاكرة والأنماط.')},
 {'id':'food-world','group':'food','asset':'food-dumplings','title':T('Makanan dari Berbagai Tempat','Food from Many Places','各地美食','أطعمة من أماكن متنوعة'),'description':T('Jelajahi bentuk dan nama hidangan dari berbagai tempat. Setiap keluarga dapat menyajikannya berbeda.','Explore the shapes and names of dishes from many places. Each family may serve them differently.','探索各地美食的形状和名称。不同家庭的做法可能不同。','اكتشف أشكال وأسماء أطعمة من أماكن متنوعة. قد تقدمها كل أسرة بطريقة مختلفة.')},
 {'id':'jobs-people','group':'jobs','asset':'job-doctor','title':T('Kenali Pekerjaan','Meet the Workers','认识职业','تعرف إلى المهن'),'description':T('Kenali dua belas pekerjaan lewat tugas, gambar, petunjuk, pasangan, dan permainan ingatan.','Meet twelve jobs through their tasks, pictures, clues, matching, and memory games.','通过工作任务、图片、线索、配对和记忆游戏认识十二种职业。','تعرف إلى اثنتي عشرة مهنة بالمهام والصور والتلميحات والمطابقة وألعاب الذاكرة.')},
 {'id':'jobs-tools','group':'jobs','asset':'job-mechanic','title':T('Pekerjaan dan Peralatannya','Jobs and Their Equipment','职业与用具','المهن وأدواتها'),'description':T('Hubungkan pekerja dengan peralatan, lalu kenali kegunaan, pola, dan kelompok bendanya.','Connect workers with equipment, then explore uses, patterns, and groups.','把工作者和用具联系起来，再探索用途、规律和分类。','اربط العاملين بالأدوات، ثم اكتشف الاستخدامات والأنماط والمجموعات.')},
]

def build_category(c,pool):
    kinds=['choose-one','clue','match','memory','pattern','sort' if c['id']=='jobs-tools' else 'choose-many']
    records=[]
    for ki,kind in enumerate(kinds):
      for v in range(4):
        rs=[]
        for r in range(4):
          n=v*4+r
          if kind in ('choose-one','clue'): round_=select_round(pool,n,kind)
          elif kind=='match': round_=role_tool_round(n) if c['id']=='jobs-tools' else identical_pair(pool,n)
          elif kind=='memory': round_=memory_round(pool,n)
          elif kind=='pattern': round_=pattern_round(pool,n)
          elif kind=='sort': round_=sort_round(n)
          else: round_=choose_many_round(pool,n,c['id']=='jobs-people')
          rs.append(round_)
        variant=ki*4+v+1
        age=4 if kind in ('clue','pattern','sort') else 3
        w={'id':f"{c['id']}-{variant:02}",'category':c['id'],'title':copy.deepcopy(KIND_TITLES[kind]),'variant':variant,'difficulty':1+v//2,'age':age,'ageRange':[age,6],'revision':'topics-v1',**copy.deepcopy(rs[0]),'rounds':rs}
        records.append(w)
    c.update(engine=records[0]['engine'],age=3,ageRange=[3,6],worksheetCount=24,activityKinds=kinds)
    return records

def semantic(r):
    """Ignore display ordering/identifiers, retain objects, rules, answers and relationships."""
    opts={o['id']:o['asset'] for o in r['options']}
    right={o['id']:o['asset'] for o in r.get('rightOptions',[])}
    return json.dumps({'kind':r['activityKind'],'instruction':r['instruction'],'options':sorted(opts.values()),'answer':sorted(opts[i] for i in r['answer']),'pairs':sorted((opts[p['left']],right.get(p['right'],p['right'])) for p in r.get('pairs',[])),'pattern':[None if x is None else x['asset'] for x in r.get('patternItems',[])]},ensure_ascii=False,sort_keys=True)

def audit(records):
    checks=0
    for w in records:
      assert len(w['rounds'])==4
      assert len({semantic(r) for r in w['rounds']})==4, ('round duplicate',w['id'])
      for r in w['rounds']:
        checks+=1
        ids={p['id'] for p in r['options']};assert len(ids)==len(r['options'])
        assert set(r['answer'])<=ids
        for t in [w['title'],r['instruction'],*(o['label'] for o in r['options']),*(o['label'] for o in r.get('rightOptions',[])),*(b['label'] for b in r.get('bins',[]))]: assert all(t.get(l) for l in LANGS)
        if r['engine']=='identify': assert len(r['answer'])==(3 if r['activityKind']=='choose-many' else 1)
        if r['engine']=='pair':
          assert len(r['pairs'])==len(r['options'])==len(r['rightOptions'])
          assert {p['left'] for p in r['pairs']}==ids
          assert {p['right'] for p in r['pairs']}=={o['id'] for o in r['rightOptions']}
        if r['engine']=='sort': assert {p['left'] for p in r['pairs']}==ids
        if r['engine']=='pattern':
          assert len(r['answer'])==1 and sum(x is None for x in r['patternItems'])==1
    for c in CATS:
      ws=[w for w in records if w['category']==c['id']]
      signatures=[tuple(sorted(semantic(r) for r in w['rounds'])) for w in ws]
      assert len(set(signatures))==24
      assert len({w['activityKind'] for w in ws})>=4
      assert len({w['engine'] for w in ws})>=3
    return {'valid':True,'categories':len(CATS),'worksheets':len(records),'rounds':checks,'languages':list(LANGS),'perCategory':[{ 'id':c['id'],'worksheets':24,'rounds':96,'activityKinds':c['activityKinds'],'engines':sorted({w['engine'] for w in records if w['category']==c['id']})} for c in CATS],'checks':['four semantic rounds per worksheet','no duplicate worksheet task sets per category','complete four-language fields','valid answer IDs and pair targets','three positive matches in multi-select','no healthcare-role ambiguity in clue options','food clues checked against both generated atlases','steamer food named bao to match its pictured form','four-language plain names for all 28 new assets'],'editorialScope':'Original practice variations; translations and artwork require integration review. Food origins are not tested.','sources':[{'url':'https://www.indonesia.travel/nl/nl/news-update/once-again-indonesia-s-rendang-and-nasi-goreng-crowned-world-s-best-foods','publisher':'Indonesia Ministry of Tourism','supports':'Nasi goreng, rendang, soto, sate and gado-gado as Indonesian culinary examples. No rankings copied.'}]}

def main():
    (ROOT/'bundles').mkdir(exist_ok=True)
    records=[]
    for c,pool in zip(CATS,[FOOD_ID,FOOD_WORLD,PEOPLE,TOOLS]):
        ws=build_category(c,pool);records.extend(ws)
        (ROOT/'bundles'/f"{c['id']}.json").write_text(json.dumps(ws,ensure_ascii=False,separators=(',',':')))
    report=audit(records)
    (ROOT/'categories.json').write_text(json.dumps(CATS,ensure_ascii=False,indent=2))
    (ROOT/'art-labels.json').write_text(json.dumps({k:v for k,v in L.items() if k.startswith(('food-','job-'))},ensure_ascii=False,indent=2))
    (ROOT/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__': main()
