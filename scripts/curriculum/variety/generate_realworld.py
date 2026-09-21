#!/usr/bin/env python3
"""Deterministic authored variety overlay. Reads Site, writes only --out (outside Site).
Every changed sheet contains four distinct targets/sets. The final semantic audit
recomputes answers from clue facts, membership sets and visible matching assets.
"""
import argparse, copy, itertools, json, pathlib
LANGS=('id','en','zh','ar')
def T(s):
    a=s.split('|'); assert len(a)==4,s
    return dict(zip(LANGS,a))
# A clue names a property/use, never the answer's name. Each fact has one target.
CLUES={}
def clues(raw):
    for row in raw.strip().splitlines():
        asset,phrase=row.split('^',1); CLUES[asset]=T(phrase)
clues('''
habit-toothbrush^Alat ini memiliki bulu kecil untuk membersihkan gigi bersama pendamping. Apa itu?|This tool has little bristles for cleaning teeth with a grown-up. What is it?|这种工具有小刷毛，可以和大人一起用它清洁牙齿。它是什么？|لهذه الأداة شعيرات صغيرة لتنظيف الأسنان مع شخص بالغ. ما هي؟
habit-toothpaste^Pendamping menaruh sedikit bahan dari tabung ini pada sikat gigi. Pilih tabungnya.|A grown-up puts a little of this from a tube onto a toothbrush. Choose the tube.|大人把管里的东西挤一点到牙刷上。选出这个管子。|يضع شخص بالغ قليلا من هذا الأنبوب على فرشاة الأسنان. اختر الأنبوب.
habit-towel^Benda lembut ini menyerap air setelah kita mencuci tangan. Apa itu?|This soft object absorbs water after we wash our hands. What is it?|这个柔软的物品能吸干洗手后的水。它是什么？|يمتص هذا الشيء الناعم الماء بعد غسل اليدين. ما هو؟
habit-soap^Kita memakai benda ini dengan air untuk membersihkan tangan. Apa itu?|We use this with water to clean our hands. What is it?|我们用它和水一起清洁双手。它是什么？|نستخدم هذا مع الماء لتنظيف أيدينا. ما هو؟
habit-clean-shirt^Setelah mandi dan mengeringkan badan, benda ini dapat dipakai di badan. Pilih gambarnya.|After bathing and drying, this can be worn on the body. Choose it.|洗澡并擦干后，可以把它穿在身上。选出来。|بعد الاستحمام والتجفيف يمكن ارتداء هذا على الجسم. اختره.
habit-tissue^Kertas lembut ini bisa digunakan untuk menyeka hidung dengan bantuan. Apa itu?|This soft paper can wipe a nose with help. What is it?|这种柔软的纸可以在帮助下用来擦鼻子。它是什么？|يمكن استخدام هذا الورق الناعم لمسح الأنف بمساعدة. ما هو؟
habit-toilet^Kita duduk di sini untuk buang air, dengan bantuan bila perlu. Pilih bendanya.|We sit here to use the bathroom, with help if needed. Choose it.|我们坐在这里如厕，需要时请人帮助。选出这个物品。|نجلس هنا لقضاء الحاجة، مع المساعدة عند الحاجة. اختره.
habit-plate^Makanan diletakkan di atas benda datar ini saat makan. Apa itu?|Food rests on this flat dish at mealtime. What is it?|用餐时，食物放在这个扁平的餐具上。它是什么？|يوضع الطعام على هذا الإناء المسطح عند الأكل. ما هو؟
habit-cup^Benda ini menampung air yang akan kita minum. Apa itu?|This holds water for us to drink. What is it?|它盛着我们要喝的水。它是什么？|يحمل هذا الماء الذي نشربه. ما هو؟
habit-bed^Kita dapat beristirahat dan tidur di atas perabot ini. Apa itu?|We can rest and sleep on this piece of furniture. What is it?|我们可以躺在这件家具上休息和睡觉。它是什么？|يمكننا الراحة والنوم على قطعة الأثاث هذه. ما هي؟
book^Buka halamannya untuk membaca cerita. Apa bendanya?|Open its pages to read a story. What is it?|翻开它的书页就能读故事。它是什么？|افتح صفحاته لتقرأ قصة. ما هو؟
spoon^Alat makan ini memiliki ujung cekung untuk menyendok makanan. Apa itu?|This utensil has a little bowl at one end for scooping food. What is it?|这种餐具有一个小凹槽，可以用来舀食物。它是什么？|لهذه الأداة تجويف صغير في طرفها لغرف الطعام. ما هي؟
chair^Perabot ini memiliki tempat duduk dan sandaran. Apa itu?|This piece of furniture has a seat and a back. What is it?|这件家具有座位和靠背。它是什么？|لقطعة الأثاث هذه مقعد ومسند للظهر. ما هي؟
table^Perabot ini memiliki permukaan rata untuk meletakkan buku saat menggambar. Apa itu?|This furniture has a flat top to hold a book while drawing. What is it?|这件家具的平面可以在画画时放书。它是什么？|لهذا الأثاث سطح مستو لوضع كتاب أثناء الرسم. ما هو؟
bed^Perabot ini digunakan untuk tidur dan beristirahat. Apa itu?|This furniture is used for sleeping and resting. What is it?|这件家具用来睡觉和休息。它是什么？|يستخدم هذا الأثاث للنوم والراحة. ما هو؟
lamp^Benda ini dinyalakan untuk memberi cahaya di ruangan. Apa itu?|We switch this on to add light to a room. What is it?|打开它可以照亮房间。它是什么？|نشغل هذا ليضيء الغرفة. ما هو؟
clock^Jarumnya menunjukkan waktu. Pilih bendanya.|Its hands show the time. Choose it.|它的指针显示时间。选出这个物品。|تشير عقارب هذا الشيء إلى الوقت. اختره.
pencil^Kita memegang alat ini untuk menggambar garis di kertas. Apa itu?|We hold this tool to draw lines on paper. What is it?|我们握着它在纸上画线。它是什么？|نمسك بهذه الأداة لرسم خطوط على الورق. ما هي؟
bag^Benda ini membawa buku saat kita pergi belajar. Apa itu?|This carries books when we go to learn. What is it?|去学习时，我们用它装书。它是什么？|يحمل هذا الكتب عندما نذهب للتعلم. ما هو؟
ruler^Alat lurus dengan tanda ukuran ini membantu mengukur panjang. Apa itu?|This straight tool with measurement marks helps measure length. What is it?|这个有刻度的直工具可以测量长度。它是什么？|تساعد هذه الأداة المستقيمة ذات العلامات على قياس الطول. ما هي؟
scissors^Dua bilah alat ini memotong kertas dengan bantuan pendamping. Apa itu?|Its two blades cut paper with a grown-up's help. What is it?|在大人帮助下，它的两片刀刃可以剪纸。它是什么？|تقص شفرتا هذه الأداة الورق بمساعدة شخص بالغ. ما هي؟
umbrella^Kita membuka benda ini di atas kepala agar terlindung dari hujan. Apa itu?|We open this above our heads to keep rain off. What is it?|我们把它撑在头顶上挡雨。它是什么？|نفتح هذا فوق رؤوسنا لنتقي المطر. ما هو؟
watering-can^Benda ini memiliki cerat untuk menyiram tanaman. Apa itu?|This has a spout for watering plants. What is it?|它有一个壶嘴，可以用来给植物浇水。它是什么？|لهذا الشيء فوهة لسقي النباتات. ما هو؟
trowel^Alat kebun kecil ini membantu memindahkan tanah dengan pendamping. Apa itu?|This small garden tool helps move soil with a grown-up. What is it?|在大人陪伴下，这个小园艺工具可以用来移土。它是什么？|تساعد أداة الحديقة الصغيرة هذه على نقل التراب مع شخص بالغ. ما هي؟
water-glass^Setelah bermain, kita haus. Pilih air yang siap diminum.|After playing, we are thirsty. Choose the water ready to drink.|玩过之后口渴了。选出可以喝的水。|نشعر بالعطش بعد اللعب. اختر الماء الجاهز للشرب.
car^Kendaraan jalan ini kecil dan memiliki empat roda. Pilih gambarnya.|This small road vehicle has four wheels. Choose it.|这种小型道路车辆有四个轮子。选出来。|لهذه المركبة الصغيرة على الطريق أربع عجلات. اخترها.
bus^Banyak penumpang dapat duduk bersama dalam kendaraan jalan besar ini. Apa itu?|Many passengers can sit together in this large road vehicle. What is it?|很多乘客可以一起坐在这辆大型道路车辆里。它是什么？|يمكن لركاب كثيرين الجلوس معا في هذه المركبة الكبيرة على الطريق. ما هي؟
bicycle^Kendaraan dua roda ini digerakkan dengan pedal. Apa itu?|This two-wheeled vehicle is moved by pedals. What is it?|这种两轮交通工具靠踩踏板前进。它是什么？|تتحرك هذه المركبة ذات العجلتين بالدواسات. ما هي؟
fire-truck^Kendaraan ini membawa petugas dan peralatan untuk memadamkan api. Apa itu?|This vehicle carries firefighters and equipment to put out fires. What is it?|这种车运送消防员和灭火设备。它是什么？|تنقل هذه المركبة رجال الإطفاء ومعدات إخماد الحرائق. ما هي؟
train^Gerbong kendaraan ini berjalan di atas rel. Apa itu?|This vehicle's carriages travel on tracks. What is it?|这种交通工具的车厢在轨道上行驶。它是什么？|تسير عربات هذه المركبة على قضبان. ما هي؟
airplane^Kendaraan bersayap ini terbang membawa penumpang. Apa itu?|This winged vehicle flies with passengers. What is it?|这种有翅膀的交通工具在空中运送乘客。它是什么？|تطير هذه المركبة ذات الأجنحة حاملة الركاب. ما هي؟
helicopter^Baling-baling di atas kendaraan ini berputar saat terbang. Apa itu?|The rotor on top of this vehicle spins as it flies. What is it?|这种交通工具飞行时，顶部的旋翼会旋转。它是什么？|تدور المروحة أعلى هذه المركبة أثناء طيرانها. ما هي؟
sailboat^Kendaraan air ini memakai layar untuk menangkap angin. Apa itu?|This water vehicle uses a sail to catch the wind. What is it?|这种水上交通工具用帆借助风力。它是什么？|تستخدم هذه المركبة المائية شراعا لالتقاط الرياح. ما هي؟
submarine^Kendaraan ini dapat menyelam di bawah permukaan air. Apa itu?|This vehicle can travel under the water's surface. What is it?|这种交通工具可以在水面以下航行。它是什么？|يمكن لهذه المركبة السير تحت سطح الماء. ما هي؟
excavator^Mesin ini memakai lengan dan ember besar untuk menggali tanah. Apa itu?|This machine uses an arm and a big bucket to dig soil. What is it?|这种机器用长臂和大铲斗挖土。它是什么？|تستخدم هذه الآلة ذراعا ودلوا كبيرا لحفر التراب. ما هي؟
bulldozer^Mesin ini mendorong tanah dengan bilah lebar di depan. Apa itu?|This machine pushes soil with a wide blade at the front. What is it?|这种机器用前面的宽铲刀推土。它是什么？|تدفع هذه الآلة التراب بشفرة عريضة في مقدمتها. ما هي؟
crane^Mesin tinggi ini mengangkat beban dengan kait. Apa itu?|This tall machine lifts loads with a hook. What is it?|这种高大的机器用吊钩提升重物。它是什么？|ترفع هذه الآلة الطويلة الأحمال بخطاف. ما هي؟
dump-truck^Bak kendaraan ini dapat dimiringkan untuk menurunkan muatan. Apa itu?|This vehicle tips its bed to unload its load. What is it?|这种车能倾斜车斗，把货物倒出来。它是什么？|تميل هذه المركبة صندوقها لتفريغ الحمولة. ما هي؟
hammer^Pendamping memakai kepala alat ini untuk mengetuk paku. Pilih gambarnya.|A grown-up uses this tool's head to tap nails. Choose its picture.|大人用这种工具的头敲钉子。选出它的图片。|يستخدم شخص بالغ رأس هذه الأداة لدق المسامير. اختر صورتها.
wrench^Alat ini mencengkeram mur untuk memutarnya. Pilih gambarnya.|This tool grips a nut to turn it. Choose its picture.|这种工具夹住螺母并转动它。选出它的图片。|تمسك هذه الأداة بالصامولة لتديرها. اختر صورتها.
screwdriver^Ujung alat ini masuk ke kepala sekrup untuk memutarnya. Apa itu?|This tool's tip fits a screw head to turn it. What is it?|这种工具的尖端插入螺丝头来转动螺丝。它是什么？|يدخل طرف هذه الأداة في رأس البرغي لتدويره. ما هي؟
saw^Pendamping memakai deretan gigi tajam alat ini untuk memotong kayu. Pilih gambarnya.|A grown-up uses this tool's row of teeth to cut wood. Choose its picture.|大人用这种工具的一排锯齿切割木头。选出它的图片。|يستخدم شخص بالغ صف أسنان هذه الأداة لقطع الخشب. اختر صورتها.
wheel^Bagian bulat ini berputar ketika kendaraan bergerak. Apa itu?|This round part turns when a vehicle moves. What is it?|车辆移动时，这个圆形部件会转动。它是什么？|يدور هذا الجزء المستدير عندما تتحرك المركبة. ما هو؟
gear^Bagian bundar ini memiliki gigi yang bertemu dengan gigi bagian lain. Apa itu?|This round part has teeth that meet another part's teeth. What is it?|这个圆形部件的齿会与另一个部件的齿咬合。它是什么？|لهذا الجزء المستدير أسنان تتشابك مع أسنان جزء آخر. ما هو؟
spring^Bagian logam melingkar ini dapat ditekan lalu kembali memanjang. Apa itu?|This coiled metal part can compress and then stretch back. What is it?|这个卷起来的金属部件可以被压缩，然后恢复伸展。它是什么？|يمكن ضغط هذا الجزء المعدني الملفوف ثم يعود للتمدد. ما هو؟
pulley^Bagian ini adalah roda dengan tali yang membantu mengangkat benda. Apa itu?|This part is a wheel with a rope that helps lift things. What is it?|这个带绳子的轮子能帮助提升物品。它是什么？|هذا الجزء عجلة بحبل تساعد على رفع الأشياء. ما هو؟
football^Bola ini biasa ditendang ke arah gawang. Pilih gambarnya.|This ball is commonly kicked toward a goal. Choose its picture.|这种球通常被踢向球门。选出它的图片。|تركل هذه الكرة عادة نحو المرمى. اختر صورتها.
basketball^Bola ini dipantulkan lalu dilempar ke keranjang tinggi. Apa itu?|This ball is bounced and thrown toward a high hoop. What is it?|这种球会被拍到地上，再投向高处的篮筐。它是什么？|تنطط هذه الكرة ثم ترمى نحو سلة مرتفعة. ما هي؟
helmet^Kita memakai benda keras ini di kepala saat bersepeda. Apa itu?|We wear this hard item on the head when cycling. What is it?|骑车时，我们把这个坚硬的物品戴在头上。它是什么？|نرتدي هذا الشيء الصلب على الرأس عند ركوب الدراجة. ما هو؟
kite^Angin mengangkat mainan bertali ini ke udara. Apa itu?|The wind lifts this toy into the air while we hold its string. What is it?|我们握着线时，风能把这个玩具吹上天空。它是什么？|ترفع الرياح هذه اللعبة في الهواء بينما نمسك بخيطها. ما هي؟
tent^Tempat berlindung dari kain ini didirikan saat berkemah. Apa itu?|This fabric shelter is put up when camping. What is it?|露营时搭起的这种布制住所是什么？|ينصب هذا المأوى القماشي عند التخييم. ما هو؟
compass^Jarum alat ini menunjukkan arah utara. Apa itu?|This tool's needle points north. What is it?|这个工具的指针指向北方。它是什么？|تشير إبرة هذه الأداة إلى الشمال. ما هي؟
flashlight^Lampu kecil ini dapat dibawa di tangan untuk menerangi jalan. Apa itu?|This small light can be held in a hand to light a path. What is it?|这种小灯可以拿在手里照路。它是什么？|يمكن حمل هذا المصباح الصغير في اليد لإضاءة الطريق. ما هو؟
binoculars^Kita melihat melalui dua lensa alat ini untuk melihat burung yang jauh. Apa itu?|We look through this tool's two lenses to see distant birds. What is it?|我们透过这个工具的两个镜片观察远处的鸟。它是什么？|ننظر عبر عدستي هذه الأداة لرؤية الطيور البعيدة. ما هي؟
t-rex^Dinosaurus ini berjalan dengan dua kaki dan memiliki lengan pendek. Pilih gambarnya.|This dinosaur walked on two legs and had short arms. Choose its picture.|这种恐龙用两条腿行走，手臂很短。选出它的图片。|سار هذا الديناصور على ساقين وكانت له ذراعان قصيرتان. اختر صورته.
triceratops^Dinosaurus ini memiliki tiga tanduk dan kerah besar di belakang kepala. Apa itu?|This dinosaur had three horns and a large frill behind its head. What is it?|这种恐龙有三只角，头后有一圈大骨盾。它是什么？|كان لهذا الديناصور ثلاثة قرون وطوق عظمي كبير خلف رأسه. ما هو؟
stegosaurus^Dinosaurus ini memiliki deretan lempeng di punggung. Apa itu?|This dinosaur had a row of plates along its back. What is it?|这种恐龙的背上长着一排骨板。它是什么？|كان لهذا الديناصور صف من الصفائح على ظهره. ما هو؟
fossil^Jejak atau sisa makhluk hidup purba tersimpan dalam batu. Pilih gambarnya.|A trace or remains of ancient life is preserved in rock. Choose it.|古代生物的痕迹或遗体保存在岩石中。选出它。|أثر أو بقايا كائن قديم محفوظة في الصخر. اخترها.
''')
clues('''
earth^Kita tinggal di planet ini. Daratan dan lautan menutupi permukaannya. Apa itu?|We live on this planet. Land and oceans cover its surface. What is it?|我们住在这颗星球上，它的表面有陆地和海洋。它是什么？|نعيش على هذا الكوكب وتغطي سطحه اليابسة والمحيطات. ما هو؟
mars^Planet ini dikenal sebagai Planet Merah. Apa namanya?|This planet is known as the Red Planet. What is its name?|这颗行星被称为红色星球。它叫什么？|يعرف هذا الكوكب باسم الكوكب الأحمر. ما اسمه؟
saturn^Planet ini terkenal dengan cincin lebar yang tampak pada gambar. Pilih planetnya.|This planet is famous for the broad rings shown in the picture. Choose it.|这颗行星以图片中宽大的环闻名。选出它。|يشتهر هذا الكوكب بحلقاته العريضة الظاهرة في الصورة. اختره.
jupiter^Ini planet terbesar dalam tata surya kita. Pilih planetnya.|This is the largest planet in our solar system. Choose it.|这是太阳系中最大的行星。选出它。|هذا أكبر كواكب مجموعتنا الشمسية. اختره.
rocket^Mesin ini meluncur ke angkasa dengan gas yang keluar dari belakang. Apa itu?|This machine launches into space with gas flowing out behind it. What is it?|这种机器靠向后喷气飞入太空。它是什么？|تنطلق هذه الآلة إلى الفضاء بالغاز المندفع من خلفها. ما هي؟
telescope^Alat panjang ini membantu kita melihat benda jauh di langit. Apa itu?|This long tool helps us see distant objects in the sky. What is it?|这个长长的工具帮助我们观察天空中遥远的天体。它是什么？|تساعدنا هذه الأداة الطويلة على رؤية الأجسام البعيدة في السماء. ما هي؟
moon^Benda langit ini mengelilingi Bumi dan memantulkan cahaya Matahari. Apa itu?|This object goes around Earth and reflects sunlight. What is it?|这个天体围绕地球运行，并反射阳光。它是什么？|يدور هذا الجرم حول الأرض ويعكس ضوء الشمس. ما هو؟
sun^Bintang terdekat kita memberi cahaya dan kehangatan pada Bumi. Apa itu?|Our nearest star gives Earth light and warmth. What is it?|离我们最近的恒星给地球带来光和温暖。它是什么？|يمنح أقرب نجم إلينا الأرض الضوء والدفء. ما هو؟
cloud^Kumpulan tetes air kecil ini tampak melayang di langit. Apa itu?|This collection of tiny water drops appears to float in the sky. What is it?|许多小水滴聚在一起，看起来飘在天空中。它是什么？|يبدو هذا التجمع من قطرات الماء الصغيرة طافيا في السماء. ما هو؟
raindrop^Tetes air ini jatuh dari awan saat hujan. Pilih gambarnya.|This drop of water falls from clouds when it rains. Choose it.|下雨时，这种水滴从云里落下来。选出它。|تسقط قطرة الماء هذه من السحب عند المطر. اخترها.
eye^Bagian tubuh ini membantu kita melihat warna bunga. Apa itu?|This body part helps us see a flower's color. What is it?|这个身体部位帮助我们看见花的颜色。它是什么？|يساعدنا هذا الجزء من الجسم على رؤية لون الزهرة. ما هو؟
ear^Bagian tubuh ini membantu kita mendengar suara burung. Apa itu?|This body part helps us hear birdsong. What is it?|这个身体部位帮助我们听见鸟叫。它是什么？|يساعدنا هذا الجزء من الجسم على سماع تغريد الطيور. ما هو؟
nose^Bagian tubuh ini membantu kita mencium aroma bunga. Apa itu?|This body part helps us smell a flower's scent. What is it?|这个身体部位帮助我们闻到花香。它是什么？|يساعدنا هذا الجزء من الجسم على شم رائحة الزهرة. ما هو؟
mouth^Lidah untuk mengecap rasa berada di dalam bagian tubuh ini. Apa itu?|The tongue for tasting is inside this body part. What is it?|用来尝味道的舌头在这个身体部位里面。它是什么？|يوجد اللسان الذي يتذوق الطعام داخل هذا الجزء من الجسم. ما هو؟
mother^Dalam kosakata keluarga, ini sebutan untuk orang tua perempuan. Pilih kartunya.|In family vocabulary, this is the term for a female parent. Choose the card.|在家庭词汇中，这是对女性家长的称呼。选出卡片。|في مفردات العائلة هذا هو اسم الوالدة. اختر البطاقة.
father^Dalam kosakata keluarga, ini sebutan untuk orang tua laki-laki. Pilih kartunya.|In family vocabulary, this is the term for a male parent. Choose the card.|在家庭词汇中，这是对男性家长的称呼。选出卡片。|في مفردات العائلة هذا هو اسم الوالد. اختر البطاقة.
grandmother^Dalam kosakata keluarga, apa sebutan ibu dari orang tuamu?|In family vocabulary, what is a parent's mother called?|在家庭词汇中，父母的母亲叫什么？|في مفردات العائلة ماذا نسمي أم أحد الوالدين؟
grandfather^Dalam kosakata keluarga, apa sebutan ayah dari orang tuamu?|In family vocabulary, what is a parent's father called?|在家庭词汇中，父母的父亲叫什么？|في مفردات العائلة ماذا نسمي أبا أحد الوالدين؟
habit-thanking^Seseorang membantu menemukan mainanmu. Kata apa menunjukkan rasa terima kasih?|Someone helps find your toy. Which words express thanks?|有人帮你找到玩具。哪些话表达感谢？|ساعدك شخص في العثور على لعبتك. أي كلمات تعبر عن الشكر؟
habit-greeting^Kamu bertemu teman di pintu. Kata apa dapat membuka percakapan?|You meet a friend at the door. Which words can begin your conversation?|你在门口遇见朋友。哪些话可以开始交谈？|تقابل صديقا عند الباب. أي كلمات يمكن أن تبدأ بها الحديث؟
habit-apologizing^Kamu tidak sengaja menyenggol teman. Kata apa mengakui kecelakaan itu?|You accidentally bump a friend. Which words acknowledge the accident?|你不小心碰到朋友。哪些话能承认这次意外？|اصطدمت بصديق دون قصد. أي كلمات تعترف بما حدث؟
habit-asking-help^Ada tugas yang sulit dikerjakan sendiri. Kata apa dapat meminta bantuan?|A task is hard to do alone. Which words ask for help?|有件事很难独自完成。哪些话可以请求帮助？|يصعب القيام بمهمة وحدك. أي كلمات تطلب بها المساعدة؟
habit-sharing^Teman ingin mencoba mainan bersama. Tindakan apa memberi kesempatan bergiliran?|A friend wants to try a shared toy. Which action offers a turn?|朋友想试试共用的玩具。哪个做法可以让对方轮流玩？|يريد صديق تجربة لعبة مشتركة. أي فعل يتيح له دورا؟
habit-waiting^Teman belum selesai memakai mainan bersama. Tindakan apa memberi mereka waktu?|A friend has not finished using a shared toy. Which action gives them time?|朋友还没用完共用的玩具。哪个做法能给对方时间？|لم ينته صديق من استخدام لعبة مشتركة. أي فعل يمنحه الوقت؟
habit-gentle^Ada anak yang beristirahat di dekatmu. Tindakan apa menjaga suasana tenang?|A child is resting nearby. Which action keeps the space quiet?|有个孩子正在附近休息。哪个做法能保持安静？|يستريح طفل بالقرب منك. أي فعل يحافظ على هدوء المكان؟
habit-helping^Menara balok teman roboh. Tindakan apa menawarkan bantuan membangun lagi?|A friend's block tower falls. Which action offers to help rebuild?|朋友的积木塔倒了。哪个做法是主动帮忙重搭？|انهار برج مكعبات صديق. أي فعل يعرض المساعدة في بنائه مجددا؟
cat^Hewan ini mengeong dan memiliki kumis. Apa itu?|This animal meows and has whiskers. What is it?|这种动物会喵喵叫，还有胡须。它是什么？|يموء هذا الحيوان وله شوارب. ما هو؟
dog^Hewan ini menggonggong dan mengibaskan ekor. Apa itu?|This animal barks and wags its tail. What is it?|这种动物会汪汪叫，还会摇尾巴。它是什么？|ينبح هذا الحيوان ويحرك ذيله. ما هو؟
bee^Serangga ini berdengung dan mengunjungi bunga untuk mencari nektar. Apa itu?|This insect buzzes and visits flowers for nectar. What is it?|这种昆虫嗡嗡飞，去花朵上采花蜜。它是什么？|تطن هذه الحشرة وتزور الأزهار بحثا عن الرحيق. ما هي؟
snail^Hewan kecil ini membawa cangkang di punggung dan bergerak perlahan. Apa itu?|This little animal carries a shell on its back and moves slowly. What is it?|这种小动物背着壳，移动缓慢。它是什么？|يحمل هذا الحيوان الصغير صدفة على ظهره ويتحرك ببطء. ما هو؟
carrot^Bagian sayuran jingga ini tumbuh sebagai akar di dalam tanah. Apa itu?|This orange vegetable part grows as a root in the soil. What is it?|这种橙色蔬菜的食用部分是长在土里的根。它是什么？|ينمو هذا الجزء البرتقالي من الخضار كجذر داخل التراب. ما هو؟
banana^Buah kuning ini memiliki kulit yang dapat dikupas dan bentuk melengkung. Apa itu?|This yellow fruit has a peel and a curved shape. What is it?|这种黄色水果有可剥的皮，形状弯弯的。它是什么？|لهذه الفاكهة الصفراء قشرة وشكل منحن. ما هي؟
apple^Buah bulat ini digambar berwarna merah dengan tangkai kecil di atasnya. Apa itu?|This round fruit is pictured red with a small stalk on top. What is it?|图片中，这种圆水果是红色的，顶部有小果梗。它是什么？|تظهر هذه الفاكهة المستديرة حمراء ولها ساق صغيرة في أعلاها. ما هي؟
cucumber^Sayuran hijau panjang ini sering diiris untuk salad. Apa itu?|This long green vegetable is often sliced for salads. What is it?|这种长长的绿色蔬菜常被切片做沙拉。它是什么？|تقطع هذه الخضرة الطويلة الخضراء غالبا إلى شرائح للسلطة. ما هي؟
tree^Tumbuhan besar ini memiliki batang berkayu dan cabang. Apa itu?|This large plant has a woody trunk and branches. What is it?|这种大植物有木质的树干和树枝。它是什么？|لهذا النبات الكبير جذع خشبي وأغصان. ما هو؟
flower^Bagian tumbuhan ini memiliki kelopak yang menarik perhatian. Apa itu?|This plant part has eye-catching petals. What is it?|这个植物部位有引人注目的花瓣。它是什么？|لهذا الجزء من النبات بتلات تلفت النظر. ما هو؟
seed^Benda kecil ini dapat tumbuh menjadi tanaman baru. Apa itu?|This small thing can grow into a new plant. What is it?|这个小东西可以长成新植物。它是什么？|يمكن لهذا الشيء الصغير أن ينمو إلى نبات جديد. ما هو؟
leaf^Bagian hijau ini membantu tumbuhan membuat makanan dengan cahaya. Apa itu?|This green part helps a plant make food using light. What is it?|这个绿色部位帮助植物利用光制造养分。它是什么？|يساعد هذا الجزء الأخضر النبات على صنع غذائه بالضوء. ما هو؟
''')
# Use the appropriate isolated object vocabulary for the duplicate care atlas.
for old,new in [('habit-toothbrush','toothbrush'),('habit-soap','soap'),('habit-towel','towel'),('habit-plate','plate'),('habit-cup','cup')]: CLUES[new]=CLUES[old]
# Catalogue-specific pools: first four have independently authored use/fact clues.
POOLS={}
def pool(cats,assets):
 for cat in cats.split(): POOLS[cat]=assets.split()
pool('brush-teeth','habit-toothbrush habit-toothpaste habit-towel habit-soap habit-clean-tooth habit-brushing')
pool('bath-routine wash-hands','habit-soap habit-towel habit-clean-shirt habit-toothbrush habit-bathing habit-drying')
pool('toilet-care','habit-toilet habit-tissue habit-soap habit-towel habit-clean-shirt habit-handwash')
pool('mealtime-habits','habit-plate habit-cup spoon habit-towel habit-eating habit-drinking')
pool('bedtime-routine','habit-bed book habit-toothbrush habit-clean-shirt habit-sleeping habit-brushing')
pool('tidy-toys','book pencil habit-plate habit-towel building-blocks football')
pool('helping-family','book habit-towel habit-plate watering-can habit-clean-shirt spoon')
pool('daily-routine','habit-bed habit-soap habit-plate book habit-eating habit-tidying')
pool('polite-words kind-words','habit-thanking habit-greeting habit-apologizing habit-asking-help habit-sharing habit-waiting')
pool('gentle-with-younger friendly-choices taking-turns','habit-sharing habit-waiting habit-gentle habit-helping habit-greeting habit-asking-help')
pool('road-vehicles','bus bicycle fire-truck car ambulance motorcycle')
pool('air-water-vehicles','airplane helicopter sailboat submarine boat ship')
pool('construction-vehicles','excavator bulldozer crane dump-truck tractor')
pool('garage-tools','hammer wrench screwdriver saw toolbox pliers')
pool('machine-parts build-a-vehicle','wheel gear spring pulley bolt nut')
pool('workshop-sort','hammer wrench screwdriver saw wheel gear spring pulley')
pool('sports-kit hobby-patterns','football basketball helmet kite bicycle skateboard')
pool('camping-kit adventure-sort','tent compass flashlight binoculars backpack umbrella')
pool('dinosaur-names','t-rex triceratops stegosaurus fossil')
pool('planet-names planet-facts','earth mars saturn jupiter mercury venus uranus neptune')
pool('space-pairs','rocket telescope moon earth astronaut satellite sun comet')
pool('body-parts five-senses','eye ear nose mouth hand foot head shoulder')
pool('body-care','soap toothbrush towel water-glass bed habit-clean-shirt')
pool('family-members family-pairs','mother father grandmother grandfather older-sibling younger-sibling baby family')
pool('room-objects','chair table bed lamp clock plate cup spoon')
pool('school-objects','book pencil ruler scissors bag chair')
pool('object-functions','chair lamp clock book pencil bag ruler umbrella')
pool('living-nonliving animal-names','cat dog bee snail tree rabbit rock chair')
pool('plant-needs garden-names','watering-can sun seed leaf tree flower trowel sprout')
pool('weather-choices','umbrella water-glass cloud sun raindrop towel')
pool('produce-names','carrot banana apple cucumber tomato')
pool('vehicle-names','bicycle bus airplane train car boat rocket')
pool('sky-names','sun moon cloud raindrop star planet rocket astronaut')
pool('home-names','umbrella watering-can trowel book chair lamp')
# Explicit membership boundaries for multi-selection and odd-one-out. No assumed
# family roles, diet or habitat rules. The membership sets are independent of the
# positions and IDs assigned to answer cards.
RULES={}
def rule(name,positive,negative,text):RULES[name]=(positive.split(),negative.split(),T(text))
rule('care','habit-toothbrush habit-toothpaste habit-towel habit-soap','book pencil football clock','Pilih semua benda untuk membersihkan atau mengeringkan tubuh.|Choose every object used to clean or dry the body.|选出所有用来清洁或擦干身体的物品。|اختر كل الأشياء المستخدمة لتنظيف الجسم أو تجفيفه.')
rule('road','car bus bicycle motorcycle fire-truck ambulance','boat ship sailboat submarine','Pilih semua kendaraan yang berjalan di jalan darat.|Choose every vehicle that travels on roads.|选出所有在道路上行驶的车辆。|اختر كل المركبات التي تسير على الطرق.')
rule('water','boat ship sailboat submarine','car bus bicycle motorcycle','Pilih semua kendaraan yang bergerak di air.|Choose every vehicle that travels in water.|选出所有在水中航行的交通工具。|اختر كل المركبات التي تسير في الماء.')
rule('tools','hammer wrench screwdriver saw pliers drill','wheel gear spring pulley','Pilih semua perkakas, bukan bagian mesin.|Choose every tool rather than a machine part.|选出所有工具，不选机器零件。|اختر كل الأدوات، دون أجزاء الآلات.')
rule('parts','wheel gear spring pulley bolt nut','hammer saw wrench screwdriver','Pilih semua bagian mesin, bukan perkakas.|Choose every machine part rather than a tool.|选出所有机器零件，不选工具。|اختر كل أجزاء الآلات، دون الأدوات.')
rule('planets','earth mars saturn jupiter mercury venus neptune uranus','moon sun comet rocket','Pilih semua planet dalam tata surya kita.|Choose every planet in our solar system.|选出所有太阳系中的行星。|اختر كل الكواكب في مجموعتنا الشمسية.')
rule('body','eye ear nose mouth hand foot head shoulder','soap towel chair cup','Pilih semua bagian tubuh.|Choose every body part.|选出所有身体部位。|اختر كل أجزاء الجسم.')
rule('living','cat dog bee snail tree rabbit sprout cow','rock chair spoon pencil','Pilih semua makhluk hidup.|Choose every living thing.|选出所有生物。|اختر كل الكائنات الحية.')
rule('produce','carrot banana apple cucumber tomato','watering-can trowel umbrella pencil','Pilih semua buah dan sayuran.|Choose every fruit and vegetable.|选出所有水果和蔬菜。|اختر كل الفواكه والخضروات.')
rule('plants','tree flower sprout seed leaf','watering-can trowel chair pencil','Pilih semua tumbuhan atau bagian tumbuhan.|Choose every plant or plant part.|选出所有植物或植物的部分。|اختر كل النباتات أو أجزاء النباتات.')
rule('furniture','chair table bed','lamp clock spoon book','Pilih semua perabot untuk duduk, berbaring, atau menaruh barang di atasnya.|Choose every piece of furniture for sitting, lying down, or putting things on.|选出所有可以坐、躺或放东西的家具。|اختر كل قطع الأثاث للجلوس أو الاستلقاء أو وضع الأشياء عليها.')
RULE_FOR={c:'care' for c in 'brush-teeth bath-routine wash-hands toilet-care body-care'.split()}
for cats,key in [('road-vehicles vehicle-names','road'),('air-water-vehicles','water'),('garage-tools workshop-sort','tools'),('machine-parts build-a-vehicle','parts'),('planet-names planet-facts space-pairs','planets'),('body-parts five-senses','body'),('animal-names living-nonliving','living'),('produce-names','produce'),('plant-needs garden-names','plants')]:
 for c in cats.split(): RULE_FOR[c]=key
MATCH=T('Pasangkan setiap gambar dengan gambar dan kata yang sama.|Match each picture with the same picture and words.|把每张图片与图片和文字都一样的卡片配对。|صل كل صورة بالبطاقة التي تحمل الصورة والكلمات نفسها.')
MEMORY=T('Balik kartu. Temukan setiap pasangan dengan gambar dan kata yang sama.|Turn the cards over. Find every pair with the same picture and words.|翻开卡片，找出图片和文字都一样的每一对。|اقلب البطاقات واعثر على كل زوج له الصورة والكلمات نفسها.')
PATTERN=T('Perhatikan urutan gambar yang berulang. Pilih gambar untuk tempat kosong.|Look at the repeating picture pattern. Choose the picture for the gap.|观察重复的图片规律，选择空缺处的图片。|انظر إلى نمط الصور المتكرر واختر الصورة المناسبة للفراغ.')
ODD_PREFIX=T('Semua kecuali satu cocok dengan aturan ini: {rule} Pilih satu pengecualian.|All except one follow this rule: {rule} Choose the one exception.|除了一张以外，其余都符合这个规则：{rule} 选出唯一的例外。|تنطبق القاعدة التالية على جميع البطاقات إلا واحدة: {rule} اختر البطاقة المستثناة.')
CLUE_MATCH=T('Dengarkan setiap petunjuk. Pasangkan dengan gambar yang tepat.|Listen to each clue. Match it to the correct picture.|听每条线索，把它与正确的图片配对。|استمع إلى كل دليل وصله بالصورة الصحيحة.')
RULE_NAMES={
'care':T('benda untuk membersihkan atau mengeringkan tubuh|objects used to clean or dry the body|用来清洁或擦干身体的物品|أشياء لتنظيف الجسم أو تجفيفه'),
'road':T('kendaraan jalan darat|road vehicles|道路车辆|مركبات تسير على الطرق'),
'water':T('kendaraan air|water vehicles|水上交通工具|مركبات مائية'),
'parts':T('bagian mesin|machine parts|机器零件|أجزاء آلات'),
 'tools':T('perkakas|tools|工具|أدوات'),
 'planets':T('planet dalam tata surya kita|planets in our solar system|太阳系中的行星|كواكب في مجموعتنا الشمسية'),
 'body':T('bagian tubuh|body parts|身体部位|أجزاء الجسم'),
 'living':T('makhluk hidup|living things|生物|كائنات حية'),
 'produce':T('buah dan sayuran|fruit and vegetables|水果和蔬菜|فواكه وخضروات'),
 'plants':T('tumbuhan atau bagian tumbuhan|plants or plant parts|植物或植物的部分|نباتات أو أجزاء نباتات')}
ODD=T('Gambar mana yang tidak termasuk kelompok ini: {group}? Pilih satu.|Which picture is NOT in this group: {group}? Choose one.|哪张图片不属于这个类别：{group}？只选一张。|أي صورة لا تنتمي إلى هذه المجموعة: {group}؟ اختر واحدة.')
OVERRIDES={
'habit-shower':T('Air untuk mandi|Bath water|洗澡水|ماء الاستحمام'),
'habit-bed':T('Tempat tidur|Bed|床|سرير'),
'habit-toilet':T('Toilet|Toilet|马桶|مرحاض'),
'habit-toy-basket':T('Keranjang mainan|Toy basket|玩具篮|سلة ألعاب'),
'habit-asking-help':T('Tolong bantu aku.|Please help me.|请帮帮我。|ساعدني من فضلك.'),
'habit-sharing':T('Tawarkan giliran|Offer a turn|邀请别人轮流玩|اعرض على غيرك أن يأخذ دوره'),
'habit-gentle':T('Gunakan suara pelan|Use a quiet voice|轻声说话|تحدث بصوت هادئ'),
'habit-helping':T('Tawarkan bantuan membangun kembali|Offer to help rebuild|主动提出一起重新搭好|اعرض المساعدة في البناء من جديد')}
POOLS['animal-names']='cat dog bee snail rabbit cow hen horse'.split()
# Ensure the drawing clue identifies the marking tool rather than the straightedge.
CLUES['pencil']=T('Ujung grafit alat ini meninggalkan garis saat digerakkan di kertas. Apa itu?|This tool has a graphite tip that leaves lines as it moves over paper. What is it?|这种工具的石墨尖在纸上移动时会留下线条。它是什么？|لهذه الأداة طرف من الجرافيت يترك خطوطا عند تحريكه على الورق. ما هي؟')

def default_kind(w):
 e=w['engine']
 return {'pair':'match','identify':'choose-many' if len(w.get('answer',[]))>1 else 'choose-one','compare':'choose-one'}.get(e,e)

def run(site,out):
 site=site.resolve();out=out.resolve()
 assert site not in out.parents and site!=out,'Output must be outside Site checkout'
 cats=json.loads((site/'app/data/worksheet-categories.json').read_text())
 gs={'habits','kindness','vehicles','mechanics','hobbies','space','body','family','everyday','science','social','recognition'}
 owned={c['id'] for c in cats if c['group'] in gs}-{'vehicle-count','vehicle-paths','robot-drawing','build-blocks'}
 assert owned==set(POOLS),(owned-set(POOLS),set(POOLS)-owned)
 labels=json.loads((site/'app/data/art-labels.json').read_text())
 tr={l:json.loads((site/f'public/audio/{f}.json').read_text()) for l,f in [('zh','mandarin'),('ar','arabic')]}
 atlas={x for a in json.loads((site/'app/data/art-atlases.json').read_text()) for x in a['assets']}
 for asset,label in labels.items():
  for l in ['zh','ar']:
   if not label.get(l): label[l]=tr[l].get(label['en'],'')
 labels.update(OVERRIDES)
 def pic(asset,i):
  assert asset in atlas,asset
  assert all(labels[asset].get(l) for l in LANGS),(asset,labels[asset])
  return {'id':i,'kind':'asset','asset':asset,'label':copy.deepcopy(labels[asset]),'showLabel':True}
 def rotate(a,n):return a[n%len(a):]+a[:n%len(a)]
 def rbase(kind,engine,instruction,options,**fields):
  return dict(activityKind=kind,engine=engine,instruction=copy.deepcopy(instruction),options=options,answer=[],**fields)
 def clue_round(pool,r):
  target=pool[r]
  options=[pic(a,'o'+str(i)) for i,a in enumerate(pool[:4])]
  rd=rbase('clue','identify',CLUES[target],rotate(options,r+1));rd['answer']=['o'+str(r)]
  return rd
 def match_round(pool,r,functions=False):
  # Four genuinely different picture sets. Function pairs use the four clue facts.
  choices=list(itertools.combinations(pool[:4] if functions else pool,2 if functions else 3))
  group=choices[r]
  left=[({'id':'l'+str(i),'kind':'glyph','symbol':'?','label':copy.deepcopy(CLUES[a]),'showLabel':True} if functions else pic(a,'l'+str(i))) for i,a in enumerate(group)]
  right=[pic(a,'r'+str(i)) for i,a in enumerate(group)]
  return rbase('match','pair',CLUE_MATCH if functions else MATCH,left,rightOptions=rotate(right,r+1),pairs=[{'left':'l'+str(i),'right':'r'+str(i)} for i in range(len(group))])
 def memory_round(pool,r,advanced=False):
  combos=list(itertools.combinations(pool,3 if advanced else 2));group=combos[r]
  return rbase('memory','memory',MEMORY,[pic(a,'m'+str(i)) for i,a in enumerate(group)])
 def pattern_round(pool,r,style):
  a,b,c=rotate(pool,r)[:3]
  unit={'ab':[a,b],'aab':[a,a,b],'abc':[a,b,c]}[style]
  # At least two complete units make the intended repeat visible.
  strip=unit*2+[None]
  rd=rbase('pattern','pattern',PATTERN,[pic(x,'o'+str(i)) for i,x in enumerate(rotate([a,b,c],r))],patternItems=[pic(x,'p'+str(i)) if x else None for i,x in enumerate(strip)])
  rd['answer']=[o['id'] for o in rd['options'] if o['asset']==unit[0]]
  return rd
 def rule_round(rulekey,r,odd=False):
  pos,neg,inst=RULES[rulekey]
  combos=list(itertools.combinations(pos,3));group=list(combos[r%len(combos)])+[neg[r%len(neg)]]
  if odd: inst={l:ODD[l].format(group=RULE_NAMES[rulekey][l]) for l in LANGS}
  rd=rbase('odd-one-out' if odd else 'choose-many','identify',inst,rotate([pic(a,'o'+str(i)) for i,a in enumerate(group)],r+1))
  rd['answer']=[o['id'] for o in rd['options'] if (o['asset'] not in pos if odd else o['asset'] in pos)]
  return rd
 manifest=[];checks=0;total_changed=0
 bundle=out/'bundles';bundle.mkdir(parents=True,exist_ok=True)
 for cat in sorted(POOLS):
  pool=POOLS[cat];assert all(a in CLUES for a in pool[:4]),cat
  originals=json.loads((site/f'content/worksheets/{cat}.json').read_text());records=copy.deepcopy(originals)
  assert len(records)==24
  for slot in range(8):
   if slot==0: rounds=[clue_round(pool,r) for r in range(4)]
   elif slot in [1,4]:rounds=[match_round(pool,r,slot==4) for r in range(4)]
   elif slot in [2,5]:rounds=[memory_round(pool,r,slot==5) for r in range(4)]
   elif slot in [3,6] and cat in RULE_FOR:rounds=[rule_round(RULE_FOR[cat],r,slot==6) for r in range(4)]
   else:rounds=[pattern_round(pool,r,{3:'ab',6:'aab',7:'abc'}[slot]) for r in range(4)]
   old=originals[16+slot]
   new={k:copy.deepcopy(v) for k,v in old.items() if k in {'id','category','title','variant','difficulty','age','ageRange','offscreen','note'}}
   # Text completeness applies to all new visible title/instruction/picture fields.
   new['title']=T({0:'Tebak dari petunjuk|Guess from a clue|根据线索猜一猜|خمن من الدليل',1:'Pasangan gambar|Picture pairs|图片配对|أزواج الصور',2:'Temukan dua pasangan|Find two pairs|找出两对|اعثر على زوجين',3:'Pilih tiga gambar|Choose three pictures|选出三张图片|اختر ثلاث صور' if cat in RULE_FOR else 'Gambar yang berulang|Repeating pictures|重复的图片|صور متكررة',4:'Pasangkan petunjuk|Match the clues|线索配对|طابق الأدلة',5:'Temukan tiga pasangan|Find three pairs|找出三对|اعثر على ثلاثة أزواج',6:'Temukan pengecualian|Find the exception|找出例外|اعثر على الاستثناء' if cat in RULE_FOR else 'Dua sama, lalu satu|Two alike, then one|两个相同，再一个|اثنان متشابهان ثم واحد',7:'Pola tiga gambar|Three-picture patterns|三张图片的规律|أنماط من ثلاث صور'}[slot])
   for l in ['zh','ar']:new['title'][l]=new['title'].get(l) or tr[l].get(new['title']['en'],'')
   assert all(new['title'].get(l) for l in LANGS),(cat,'title')
   new.update(copy.deepcopy(rounds[0]));new['rounds']=rounds;new['revision']='variety-1'
   new['age']=max(new.get('age',2),4 if slot in [4,7] else 3)
   new['ageRange']=[new['age'],6]
   records[16+slot]=new
  extra_indices=[]
  if cat=='mealtime-habits':
   # Repair four retained memory sheets whose two different labels hid identical
   # visible artwork. Preserve the safety text and the other authored rounds.
   extra_indices=[8,9,10,15]
   arabic_additions={
    'Mealtime Picture Pairs':'أزواج صور وقت الطعام',
    'Match the same picture and words. Read the labels together. Let the child say when they are hungry, full, thirsty, or need help; this game does not ask them to finish a plate.':'طابق الصور والكلمات المتشابهة واقرؤوا التسميات معا. دع الطفل يعبّر عن جوعه أو شبعه أو عطشه أو حاجته للمساعدة؛ لا تطلب هذه اللعبة منه إنهاء طبقه.',
    'Choose one picture together and tell a tiny story about caring for yourself. You can point, pretend with toys, or try one comfortable step with a grown-up.':'اختاروا صورة معا واحكوا قصة قصيرة عن العناية بالنفس. يمكن الإشارة أو التمثيل بالألعاب أو تجربة خطوة مريحة مع شخص بالغ.'}
   def hydrate(v):
    if isinstance(v,dict):
     if 'en' in v and 'id' in v:
      for l in ['zh','ar']:
       v[l]=v.get(l) or tr[l].get(v['en']) or (arabic_additions.get(v['en']) if l=='ar' else None)
       assert v[l],(v['en'],l)
     for x in list(v.values()):hydrate(x)
    elif isinstance(v,list):
     for x in v:hydrate(x)
   for ix in extra_indices:
    w=records[ix];w['revision']='variety-1';w['activityKind']='memory'
    for rd in w['rounds']:
     rd['engine']='memory';rd['activityKind']='memory';seen=set()
     for j,o in enumerate(rd['options']):
      if o['asset'] in seen:
       used={x['asset'] for x in rd['options']};replacement=next(a for a in ['habit-plate','habit-cup','spoon','habit-towel'] if a not in used)
       rd['options'][j]=pic(replacement,o['id'])
      seen.add(rd['options'][j]['asset'])
     assert len(seen)==len(rd['options'])
    w.update(copy.deepcopy(w['rounds'][0]));hydrate(w)
  # Independent checks inspect exported round values, not generator answer IDs.
  for w in records[16:]:
   assert len(w['rounds'])==4
   sigs=[]
   for rd in w['rounds']:
    checks+=1
    for k in rd: assert w[k]==w['rounds'][0][k],(w['id'],'root mismatch',k)
    assert rd['engine']==w['engine'] and rd['activityKind']==w['activityKind']
    options=rd['options'];assets=[o.get('asset') for o in options]
    assert len({o['id'] for o in options})==len(options)
    assert all(all(t.get(l) for l in LANGS) for t in [rd['instruction']]+[o['label'] for o in options+rd.get('rightOptions',[])])
    kind=rd['activityKind']
    if kind=='clue':
     facts=[a for a in pool[:4] if CLUES[a]==rd['instruction']];assert len(facts)==1
     expected=[o['id'] for o in options if o['asset']==facts[0]];assert expected==rd['answer']
     sigs.append(('clue',facts[0]))
    elif kind in ['choose-many','odd-one-out']:
     positive=set(RULES[RULE_FOR[cat]][0]);expected={o['id'] for o in options if (o['asset'] not in positive if kind=='odd-one-out' else o['asset'] in positive)}
     assert expected==set(rd['answer'])
     assert len(expected)==(1 if kind=='odd-one-out' else 3) and len(options)==4
     sigs.append((kind,tuple(sorted(assets))))
    elif kind=='match':
     rs={o['id']:o for o in rd['rightOptions']};links=rd['pairs']
     assert len(links)==len(options)==len(rs)
     assert len({p['left'] for p in links})==len(links)==len({p['right'] for p in links})
     for o in options:
      right=rs[next(p['right'] for p in links if p['left']==o['id'])]
      assert (o.get('asset')==right['asset'] if o.get('asset') else o['label']==CLUES[right['asset']])
     sigs.append((kind,tuple(sorted(o['asset'] for o in rs.values()))))
    elif kind=='memory':
     assert 2<=len(options)<=4 and len(set(assets))==len(options)
     sigs.append((kind,tuple(sorted(assets))))
    elif kind=='pattern':
     strip=[x.get('asset') if x else None for x in rd['patternItems']]
     periods=[p for p in range(1,4) if all(a is None or b is None or a==b for a,b in zip(strip,strip[p:]))]
     assert periods
     period=min(periods);gap=strip.index(None);want=strip[gap%period]
     expected=[o['id'] for o in options if o['asset']==want];assert expected==rd['answer'] and len(expected)==1
     sigs.append((kind,tuple(strip)))
   assert len(set(sigs))==4,(w['id'],'repeated tasks',sigs)
  assert all(records[i]==originals[i] for i in range(16) if i not in extra_indices)
  assert [w['id'] for w in records]==[w['id'] for w in originals]
  kinds=sorted({w.get('activityKind') or default_kind(w) for w in records});engines=sorted({w['engine'] for w in records})
  assert len(kinds)>=4 and len(engines)>=3,(cat,kinds,engines)
  (bundle/f'{cat}.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':'))+'\n')
  changed=[w for w in records if w.get('revision')=='variety-1'];total_changed+=len(changed)
  manifest.append(dict(category=cat,worksheets=24,unchanged=24-len(changed),revised=len(changed),rounds=96,activityKinds=kinds,engines=engines,changedIds=[w['id'] for w in changed]))
 (out/'manifest.json').write_text(json.dumps({'revision':'variety-1','categories':len(manifest),'revisedWorksheets':total_changed,'checkedNewRounds':checks,'checkedRepairedMemoryRounds':16,'items':manifest},ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'categories':len(manifest),'revisedWorksheets':total_changed,'checkedNewRounds':checks,'bundles':str(bundle)},indent=2))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--site',type=pathlib.Path,required=True);p.add_argument('--out',type=pathlib.Path,required=True);a=p.parse_args();run(a.site,a.out)
