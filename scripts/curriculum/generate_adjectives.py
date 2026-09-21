#!/usr/bin/env python3
"""Deterministic four-language adjective expansion. Writes only --out.

288 worksheets, four rounds each. Each worksheet uses one renderer engine.
Category engines are representative; use each worksheet's own engine.
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

LANGS = ('en', 'id', 'zh', 'ar')
def T(en, id, zh, ar): return dict(zip(LANGS, (en,id,zh,ar)))
CARDS = {}
def C(key, asset, label, word, clue):
    CARDS[key] = {'asset':asset, 'label':label, 'word':word, 'clue':clue}

C('hot','adj-hot-cup',T('Hot cup','Cangkir panas','热杯子','كوب ساخن'),T('hot','panas','热','ساخن'),T('The cup is labeled as having a high temperature.','Label cangkir menyatakan suhunya tinggi.','杯子的标签说明它的温度高。','توضح بطاقة الكوب أن حرارته مرتفعة.'))
C('cold','adj-cold-cup',T('Cold cup','Cangkir dingin','冷杯子','كوب بارد'),T('cold','dingin','冷','بارد'),T('The cup is labeled as having a low temperature.','Label cangkir menyatakan suhunya rendah.','杯子的标签说明它的温度低。','توضح بطاقة الكوب أن حرارته منخفضة.'))
C('soft','adj-soft-pillow',T('Soft pillow','Bantal empuk','软枕头','وسادة طرية'),T('soft','empuk','软','طري'),T('This pillow is described as easy to press gently.','Bantal ini disebut mudah ditekan perlahan.','这个枕头被描述为轻轻一按就会凹下去。','توصف هذه الوسادة بأنها تنضغط بسهولة برفق.'))
C('hard','adj-hard-rock',T('Hard rock','Batu keras','硬石头','صخرة صلبة'),T('hard','keras','硬','صلب'),T('This rock is described as firm and not easy to press.','Batu ini disebut padat dan tidak mudah ditekan.','这块石头被描述为坚硬、不容易按下去。','توصف هذه الصخرة بأنها متماسكة ولا تنضغط بسهولة.'))
C('smooth','adj-smooth-ball',T('Smooth ball','Bola halus','光滑的球','كرة ملساء'),T('smooth','halus','光滑','أملس'),T('The ball is described as having a surface without bumps.','Bola ini disebut memiliki permukaan tanpa tonjolan.','这个球被描述为表面没有凹凸。','توصف الكرة بأن سطحها خال من النتوءات.'))
C('rough','adj-rough-stone',T('Rough stone','Batu kasar','粗糙的石头','حجر خشن'),T('rough','kasar','粗糙','خشن'),T('The stone is described as having an uneven surface.','Batu ini disebut memiliki permukaan tidak rata.','这块石头被描述为表面凹凸不平。','يوصف الحجر بأن سطحه غير مستو.'))
C('wet','adj-wet-shirt',T('Wet shirt','Baju basah','湿上衣','قميص مبلل'),T('wet','basah','湿','مبلل'),T('Water is still on this shirt.','Masih ada air pada baju ini.','这件上衣上还有水。','ما زال الماء على هذا القميص.'))
C('dry','adj-dry-shirt',T('Dry shirt','Baju kering','干上衣','قميص جاف'),T('dry','kering','干','جاف'),T('This shirt has no water left on it.','Tidak ada air tersisa pada baju ini.','这件上衣上没有水了。','لم يبق ماء على هذا القميص.'))
C('open','adj-open-box',T('Open box','Kotak terbuka','打开的盒子','صندوق مفتوح'),T('open','terbuka','打开','مفتوح'),T('The box has its lid lifted.','Tutup kotak ini terangkat.','盒子的盖子掀开了。','غطاء هذا الصندوق مرفوع.'))
C('closed','adj-closed-box',T('Closed box','Kotak tertutup','合上的盒子','صندوق مغلق'),T('closed','tertutup','合上','مغلق'),T('The box has its lid shut.','Tutup kotak ini menutup.','盒子的盖子合上了。','غطاء هذا الصندوق مغلق.'))
C('full','adj-full-basket',T('Full basket','Keranjang penuh','满篮子','سلة ممتلئة'),T('full','penuh','满','ممتلئ'),T('This basket has things filling it.','Keranjang ini terisi penuh oleh benda.','这个篮子里装满了东西。','تملأ الأشياء هذه السلة.'))
C('empty','adj-empty-basket',T('Empty basket','Keranjang kosong','空篮子','سلة فارغة'),T('empty','kosong','空','فارغ'),T('This basket has nothing inside.','Tidak ada benda di dalam keranjang ini.','这个篮子里没有东西。','لا توجد أشياء داخل هذه السلة.'))
C('heavy','adj-heavy-box',T('Story label: heavy box','Label cerita: kotak berat','故事标签：重箱子','وصف القصة: صندوق ثقيل'),T('heavy','berat','重','ثقيل'),T('The story says this box takes much effort to lift.','Cerita menyebut kotak ini perlu banyak tenaga untuk diangkat.','故事说搬起这个箱子很费力。','تقول القصة إن رفع هذا الصندوق يحتاج إلى جهد كبير.'))
C('light','adj-light-feather',T('Story label: light feather','Label cerita: bulu ringan','故事标签：轻羽毛','وصف القصة: ريشة خفيفة'),T('light','ringan','轻','خفيف'),T('The story says this feather takes little effort to lift.','Cerita menyebut bulu ini perlu sedikit tenaga untuk diangkat.','故事说拿起这根羽毛不费力。','تقول القصة إن رفع هذه الريشة يحتاج إلى جهد قليل.'))
C('bright','adj-bright-lamp',T('Bright lamp','Lampu terang','明亮的灯','مصباح ساطع'),T('bright','terang','明亮','ساطع'),T('The picture shows a lamp giving off much light.','Gambar menunjukkan lampu yang memancarkan banyak cahaya.','图中的灯发出很多光。','تظهر الصورة مصباحا يصدر ضوءا كثيرا.'))
C('dim','adj-dim-lamp',T('Dim lamp','Lampu redup','昏暗的灯','مصباح خافت'),T('dim','redup','昏暗','خافت'),T('The picture shows a lamp giving off little light.','Gambar menunjukkan lampu yang memancarkan sedikit cahaya.','图中的灯只发出一点光。','تظهر الصورة مصباحا يصدر ضوءا قليلا.'))
C('fast','adj-fast-car',T('Story label: fast car','Label cerita: mobil cepat','故事标签：快车','وصف القصة: سيارة سريعة'),T('fast','cepat','快','سريع'),T('In this story, the car covers the same path in less time.','Dalam cerita ini, mobil menempuh jalur yang sama dalam waktu lebih singkat.','在这个故事里，汽车走完同一段路用的时间少。','في هذه القصة تقطع السيارة الطريق نفسه في وقت أقل.'))
C('slow','adj-slow-car',T('Story label: slow car','Label cerita: mobil lambat','故事标签：慢车','وصف القصة: سيارة بطيئة'),T('slow','lambat','慢','بطيء'),T('In this story, the car covers the same path in more time.','Dalam cerita ini, mobil menempuh jalur yang sama dalam waktu lebih lama.','在这个故事里，汽车走完同一段路用的时间多。','في هذه القصة تقطع السيارة الطريق نفسه في وقت أطول.'))
C('loud','adj-loud-drum',T('Drum card: loud in this story','Kartu drum: keras dalam cerita ini','鼓卡：故事里声音大','بطاقة الطبل: صوته عال في هذه القصة'),T('loud','keras','声音大','عال'),T('The story says this drum makes a sound with high volume.','Cerita menyebut drum ini bersuara dengan volume tinggi.','故事说这面鼓发出的声音音量大。','تقول القصة إن هذا الطبل يصدر صوتا مرتفعا.'))
C('quiet','adj-quiet-book',T('Book card: quiet in this story','Kartu buku: pelan dalam cerita ini','书卡：故事里声音小','بطاقة الكتاب: الصوت هادئ في هذه القصة'),T('quiet','pelan','声音小','هادئ'),T('The story says the reading voice by this book has low volume.','Cerita menyebut suara membaca di dekat buku ini bervolume rendah.','故事说读这本书时声音音量小。','تقول القصة إن صوت القراءة عند هذا الكتاب منخفض.'))
C('tidy','adj-tidy-shelf',T('Tidy shelf','Rak rapi','整齐的架子','رف مرتب'),T('tidy','rapi','整齐','مرتب'),T('The shelf has its things arranged in their places.','Benda di rak tersusun pada tempatnya.','架子上的东西摆放整齐。','أشياء الرف مرتبة في أماكنها.'))
C('messy','adj-messy-shelf',T('Messy shelf','Rak berantakan','凌乱的架子','رف غير مرتب'),T('messy','berantakan','凌乱','غير مرتب'),T('The shelf has its things scattered out of place.','Benda di rak berserakan tidak pada tempatnya.','架子上的东西杂乱地摆着。','أشياء الرف مبعثرة خارج أماكنها.'))
C('fresh','adj-fresh-flower',T('Fresh flower','Bunga segar','新鲜的花','زهرة نضرة'),T('fresh','segar','新鲜','نضر'),T('This flower is standing upright with fresh petals.','Bunga ini tegak dengan kelopak yang segar.','这朵花挺立着，花瓣新鲜。','هذه الزهرة قائمة وبتلاتها نضرة.'))
C('wilted','adj-wilted-flower',T('Wilted flower','Bunga layu','枯萎的花','زهرة ذابلة'),T('wilted','layu','枯萎','ذابل'),T('This flower is drooping with wilted petals.','Bunga ini terkulai dengan kelopak layu.','这朵花垂下来了，花瓣枯萎。','هذه الزهرة متدلية وبتلاتها ذابلة.'))
C('open-book','adj-open-book',T('Open book','Buku terbuka','打开的书','كتاب مفتوح'),CARDS['open']['word'],T('The book has its pages spread apart.','Halaman buku ini terbuka.','书页摊开了。','صفحات هذا الكتاب مفتوحة.'))
C('closed-book','adj-closed-book',T('Closed book','Buku tertutup','合上的书','كتاب مغلق'),CARDS['closed']['word'],T('The book has its covers together.','Kedua sampul buku ini menutup.','书的封面合起来了。','غلافا هذا الكتاب مطبقان.'))
C('full-cup','adj-full-cup',T('Full cup','Gelas penuh','满杯子','كوب ممتلئ'),CARDS['full']['word'],T('This cup is filled with a drink.','Gelas ini terisi penuh minuman.','这个杯子装满了饮料。','هذا الكوب مملوء بالشراب.'))
C('empty-cup','adj-empty-cup',T('Empty cup','Gelas kosong','空杯子','كوب فارغ'),CARDS['empty']['word'],T('There is no drink in this cup.','Tidak ada minuman di dalam gelas ini.','这个杯子里没有饮料。','لا يوجد شراب في هذا الكوب.'))
C('clean','adj-clean-shoe',T('Clean shoe','Sepatu bersih','干净的鞋','حذاء نظيف'),T('clean','bersih','干净','نظيف'),T('There is no mud on this shoe.','Tidak ada lumpur pada sepatu ini.','这只鞋上没有泥。','لا يوجد طين على هذا الحذاء.'))
C('muddy','adj-muddy-shoe',T('Muddy shoe','Sepatu berlumpur','沾泥的鞋','حذاء مغطى بالطين'),T('muddy','berlumpur','沾泥','مغطى بالطين'),T('There is mud on this shoe.','Ada lumpur pada sepatu ini.','这只鞋上有泥。','يوجد طين على هذا الحذاء.'))

PAIR_KEYS = [('hot','cold'),('soft','hard'),('smooth','rough'),('wet','dry'),('open','closed'),('full','empty'),('heavy','light'),('bright','dim'),('fast','slow'),('loud','quiet'),('tidy','messy'),('fresh','wilted')]
OPPOSITES = {a:b for pair in PAIR_KEYS for a,b in (pair,tuple(reversed(pair)))}

# These are quotations attached to character/object cards. They never define
# anyone's value or ask the child to decide who is more attractive.
KIND = [
 ('handsome','adj-neat-boy',T('“You look handsome today.”','“Kamu terlihat ganteng hari ini.”','“你今天看起来很英俊。”','«تبدو وسيما اليوم.»'),T('handsome','ganteng','英俊','وسيم')),
 ('beautiful','adj-neat-girl',T('“You look beautiful today.”','“Kamu terlihat cantik hari ini.”','“你今天看起来很漂亮。”','«تبدين جميلة اليوم.»'),T('beautiful','cantik','漂亮','جميل')),
 ('self-look','adj-neat-boy',T('“I like how I look.”','“Aku suka penampilanku.”','“我喜欢自己的样子。”','«يعجبني مظهري.»'),T('liking my own look','suka penampilan sendiri','喜欢自己的样子','الإعجاب بمظهري')),
 ('self-choice','adj-neat-girl',T('“I chose clothes I like.”','“Aku memilih baju yang kusukai.”','“我选了自己喜欢的衣服。”','«اخترت ملابس أحبها.»'),T('my clothing choice','pilihan bajuku','自己的衣服选择','اختيار ملابسي')),
 ('neat-clothes','adj-neat-boy',T('“Your clothes look neat.”','“Bajumu terlihat rapi.”','“你的衣服看起来很整齐。”','«ملابسك تبدو مرتبة.»'),T('neat clothes','baju rapi','衣服整齐','ملابس مرتبة')),
 ('kind-words','adj-neat-girl',T('“Thank you for your kind words.”','“Terima kasih atas kata-katamu yang ramah.”','“谢谢你友善的话。”','«شكرا على كلماتك اللطيفة.»'),T('kind words','kata yang ramah','友善的话','كلمات لطيفة')),
 ('flower-beauty','adj-fresh-flower',T('“This flower is beautiful.”','“Bunga ini cantik.”','“这朵花很漂亮。”','«هذه الزهرة جميلة.»'),T('a beautiful flower','bunga yang cantik','漂亮的花','زهرة جميلة')),
 ('own-comfort','adj-neat-girl',T('“I feel comfortable in these clothes.”','“Aku merasa nyaman dengan baju ini.”','“我穿这些衣服很舒服。”','«أشعر بالراحة في هذه الملابس.»'),T('comfortable clothes','baju yang nyaman','舒服的衣服','ملابس مريحة')),
]
for key,asset,label,word in KIND:
    C(key,asset,label,word,T('Listen to the quoted words.','Dengarkan kata-kata yang dikutip.','听听引号里的话。','استمع إلى الكلمات المقتبسة.'))

SPECS = [
 ('temperature','hot','cold',T('Hot and Cold','Panas dan Dingin','热和冷','ساخن وبارد')),
 ('soft-hard','soft','hard',T('Soft and Hard','Empuk dan Keras','软和硬','طري وصلب')),
 ('smooth-rough','smooth','rough',T('Smooth and Rough','Halus dan Kasar','光滑和粗糙','أملس وخشن')),
 ('wet-dry','wet','dry',T('Wet and Dry','Basah dan Kering','湿和干','مبلل وجاف')),
 ('open-closed','open','closed',T('Open and Closed','Terbuka dan Tertutup','打开和合上','مفتوح ومغلق')),
 ('full-empty','full','empty',T('Full and Empty','Penuh dan Kosong','满和空','ممتلئ وفارغ')),
 ('heavy-light','heavy','light',T('Heavy and Light','Berat dan Ringan','重和轻','ثقيل وخفيف')),
 ('bright-dim','bright','dim',T('Bright and Dim','Terang dan Redup','明亮和昏暗','ساطع وخافت')),
 ('fast-slow','fast','slow',T('Fast and Slow','Cepat dan Lambat','快和慢','سريع وبطيء')),
 ('loud-quiet','loud','quiet',T('Loud and Quiet','Keras dan Pelan','声音大和声音小','صوت عال وصوت هادئ')),
 ('tidy-messy','tidy','messy',T('Tidy and Messy','Rapi dan Berantakan','整齐和凌乱','مرتب وغير مرتب')),
 ('kind-descriptions','handsome','beautiful',T('Kind Describing Words','Kata Sifat yang Ramah','友善的描述词','كلمات وصف لطيفة')),
]

GENERAL_NOTE = T('A grown-up can read the words aloud. Picture labels describe these examples. Pair and memory games also review other describing words. Children may point, speak, or choose with help; ages are guidance.',
 'Pendamping boleh membacakan kata-kata. Label gambar menggambarkan contoh ini. Permainan pasangan dan ingatan juga mengulang kata sifat lain. Anak boleh menunjuk, berbicara, atau memilih dengan bantuan; usia hanyalah panduan.',
 '可以请大人读出词语。图片标签描述的是这些例子。配对和记忆游戏也会复习其他描述词。孩子可以指一指、说一说，或在帮助下选择；年龄只是参考。',
 'يمكن للكبير قراءة الكلمات بصوت مسموع. تصف بطاقات الصور هذه الأمثلة. تراجع ألعاب المطابقة والذاكرة كلمات وصف أخرى أيضا. يمكن للطفل الإشارة أو الكلام أو الاختيار بمساعدة، والأعمار إرشادية.')
TEMPERATURE_NOTE = T('Picture play with a grown-up. Read the hot and cold labels; do not touch, taste, heat, or cool real items for this game. Adults handle real temperature checks.',
 'Bermain gambar bersama pendamping. Bacakan label panas dan dingin; jangan menyentuh, mencicipi, memanaskan, atau mendinginkan benda asli untuk permainan ini. Orang dewasa memeriksa suhu benda sungguhan.',
 '和大人一起玩图片游戏。读出热和冷的标签；不要为这个游戏触摸、品尝、加热或冷却真实物品。真实物品的温度由大人检查。',
 'لعبة صور مع شخص كبير. اقرأ وصفي الساخن والبارد، ولا تلمس أشياء حقيقية أو تتذوقها أو تسخنها أو تبردها لهذه اللعبة. يتولى الكبار فحص الحرارة في الواقع.')
STORY_NOTE = T('Use the explicit story labels. A picture, an object type, or its size alone does not tell its weight, speed, or sound volume. No lifting, racing, or loud sounds are needed.',
 'Gunakan label cerita yang jelas. Gambar, jenis benda, atau ukurannya saja tidak menentukan berat, kecepatan, atau volume suara. Tidak perlu mengangkat benda, berlomba, atau membuat suara keras.',
 '请按明确的故事标签作答。只看图片、物品种类或大小，不能确定重量、速度或音量。不需要搬东西、比赛或发出大声音。',
 'استخدم أوصاف القصة الواضحة. لا تحدد الصورة أو نوع الشيء أو حجمه وحده الوزن أو السرعة أو شدة الصوت. لا حاجة إلى حمل الأشياء أو السباق أو إصدار أصوات عالية.')
KIND_NOTE = T('Read these as quoted compliments or self-expression. Find the requested words; never rank people by looks. Handsome and beautiful are optional personal words, not rules about gender, clothing, bodies, or worth. Anyone may prefer a different compliment or none.',
 'Bacakan sebagai kutipan pujian atau ungkapan diri. Cari kata yang diminta; jangan menilai peringkat orang berdasarkan penampilan. Ganteng dan cantik adalah kata pribadi yang boleh dipilih, bukan aturan tentang gender, pakaian, tubuh, atau nilai seseorang. Siapa pun boleh memilih pujian lain atau tidak menginginkannya.',
 '把这些话当作引述的赞美或自我表达来读。寻找指定词语，不按外貌给人排名。“英俊”和“漂亮”是可以选择的个人用语，不是关于性别、衣服、身体或个人价值的规则。任何人都可以喜欢别的赞美，也可以不想被赞美。',
 'اقرأ هذه العبارات بوصفها مجاملات مقتبسة أو تعبيرا عن النفس. ابحث عن الكلمات المطلوبة ولا ترتب الناس بحسب مظهرهم. وسيم وجميل كلمتان شخصيتان اختياريتان، وليستا قواعد للجنس أو الملابس أو الأجسام أو قيمة الإنسان. يمكن لأي شخص تفضيل مجاملة أخرى أو عدم الرغبة في مجاملة.')
OFFSCREEN = T('Put the screen aside and draw two picture cards with a grown-up. Say a describing word for each. You can also make up a short story using only the pictures.',
 'Letakkan layar dan gambar dua kartu bersama pendamping. Ucapkan kata sifat untuk masing-masing. Kamu juga boleh membuat cerita pendek hanya dengan gambar.',
 '放下屏幕，和大人一起画两张图片卡。用一个描述词说说每张卡。也可以只用图片编一个小故事。',
 'ضع الشاشة جانبا وارسم بطاقتي صور مع شخص كبير. قل كلمة تصف كل بطاقة. يمكنك أيضا تأليف قصة قصيرة باستخدام الصور فقط.')
KIND_OFFSCREEN = T('With a grown-up, let two toys offer optional kind words. Each toy may say thank you, choose a different compliment, or ask to talk about something else.',
 'Bersama pendamping, biarkan dua mainan menawarkan kata ramah yang boleh diterima atau tidak. Setiap mainan boleh berterima kasih, memilih pujian lain, atau meminta membahas hal lain.',
 '和大人一起让两个玩具说可以自由接受或拒绝的友善话。每个玩具都可以说谢谢、选择别的赞美，或提出聊别的话题。',
 'مع شخص كبير، دع لعبتين تعرضان كلمات لطيفة اختيارية. يمكن لكل لعبة أن تشكر أو تختار مجاملة أخرى أو تطلب الحديث عن شيء آخر.')

# Short, neutral atlas descriptions for category art and unnamed illustrations.
# Worksheet narration must prefer the authored option label, which contains
# the story's words or quotation when that is part of the task.
ART_LABELS = {c['asset']:copy.deepcopy(c['label']) for k,c in CARDS.items() if k not in {row[0] for row in KIND}}
ART_LABELS.update({
 'adj-heavy-box':T('Heavy box picture','Gambar kotak berat','重箱子的图片','صورة صندوق ثقيل'),
 'adj-light-feather':T('Light feather picture','Gambar bulu ringan','轻羽毛的图片','صورة ريشة خفيفة'),
 'adj-fast-car':T('Fast car picture','Gambar mobil cepat','快车的图片','صورة سيارة سريعة'),
 'adj-slow-car':T('Slow car picture','Gambar mobil lambat','慢车的图片','صورة سيارة بطيئة'),
 'adj-loud-drum':T('Drum picture','Gambar drum','鼓的图片','صورة طبل'),
 'adj-quiet-book':T('Quiet reading book picture','Gambar buku untuk membaca dengan tenang','安静阅读的书图片','صورة كتاب للقراءة بهدوء'),
 'adj-neat-boy':T('Boy in neat clothes','Anak laki-laki berbaju rapi','衣着整齐的男孩','طفل بملابس مرتبة'),
 'adj-neat-girl':T('Girl in neat clothes','Anak perempuan berbaju rapi','衣着整齐的女孩','طفلة بملابس مرتبة'),
})

def pic(key, oid):
    return {'id':oid,'kind':'asset','asset':CARDS[key]['asset'],'label':copy.deepcopy(CARDS[key]['label']),'showLabel':True,'vocabularyKey':key}
def rotate(items, seed):
    values=copy.deepcopy(items)
    if seed%2: values.reverse()
    cut=seed%len(values)
    return values[cut:]+values[:cut]
def four_ids(n, variant):
    # Cyclic selections form different unordered sets, not permutations of one set.
    offsets=(0,1,3,6) if variant<12 else (0,2,5,8)
    return [(variant%n+x)%n for x in offsets]

def identify_bank(cid,a,b):
    bank=[]
    for mode in ('word','clue','opposite-word','same-picture','opposite-picture','story-quote'):
        for target,other in ((a,b),(b,a)):
            c=CARDS[target]; o=CARDS[other]; instruction={}
            for lang in LANGS:
                word=c['word'][lang]; opposite=o['word'][lang]; label=c['label'][lang]; clue=c['clue'][lang]
                templates={
                 'word': {
                  'en':f'Listen to the describing word “{word}”. Choose its picture card.',
                  'id':f'Dengarkan kata sifat “{word}”. Pilih kartu gambarnya.',
                  'zh':f'听听描述词“{word}”。请选择对应的图片卡。',
                  'ar':f'استمع إلى كلمة الوصف «{word}». اختر بطاقة الصورة المناسبة.'},
                 'clue': {
                  'en':f'{clue} Choose the card that fits this clue.',
                  'id':f'{clue} Pilih kartu yang sesuai petunjuk ini.',
                  'zh':f'{clue}请选择符合这条线索的卡片。',
                  'ar':f'{clue} اختر البطاقة التي تناسب هذا الوصف.'},
                 'opposite-word': {
                  'en':f'Which card has the opposite describing word to “{opposite}”? Use the labels.',
                  'id':f'Kartu mana memiliki kata sifat yang berlawanan dengan “{opposite}”? Gunakan labelnya.',
                  'zh':f'哪张卡的描述词与“{opposite}”相反？请按标签作答。',
                  'ar':f'أي بطاقة تحمل كلمة الوصف المضادة لكلمة «{opposite}»؟ استخدم الكلمات المكتوبة.'},
                 'same-picture': {
                  'en':f'The example card says “{label}”. Find the same picture and words.',
                  'id':f'Kartu contoh bertuliskan “{label}”. Cari gambar dan kata yang sama.',
                  'zh':f'示例卡写着“{label}”。请找出图片和文字相同的卡。',
                  'ar':f'تقول بطاقة المثال «{label}». ابحث عن الصورة والكلمات نفسها.'},
                 'opposite-picture': {
                  'en':f'The example word is “{opposite}”. Choose the card with its opposite word.',
                  'id':f'Kata pada contoh adalah “{opposite}”. Pilih kartu dengan kata lawannya.',
                  'zh':f'示例的词语是“{opposite}”。请选择描述词相反的卡。',
                  'ar':f'كلمة المثال هي «{opposite}». اختر البطاقة التي تحمل الكلمة المضادة.'},
                 'story-quote': {
                  'en':f'In our picture story, a grown-up reads: “{label}”. Find the card with those words.',
                  'id':f'Dalam cerita gambar, pendamping membaca: “{label}”. Cari kartu dengan kata-kata itu.',
                  'zh':f'在图片故事里，大人读出：“{label}”。请找出写着这些话的卡。',
                  'ar':f'في قصتنا المصورة يقرأ شخص كبير: «{label}». ابحث عن البطاقة التي تحمل هذه الكلمات.'},
                }
                instruction[lang]=templates[mode][lang]
            r={'instruction':instruction,'options':[pic(a,'o0'),pic(b,'o1')],'answer':['o0' if target==a else 'o1'],'layout':'story-choices','scenarioId':f'{cid}:{mode}:{target}'}
            if mode=='same-picture': r['reference']=pic(target,'reference')
            if mode=='opposite-picture': r['reference']=pic(other,'reference')
            bank.append(r)
    return bank

PAIR_INSTRUCTION=T('Match each describing word with its opposite. Read the story labels together; one pair also reviews another describing word.',
 'Pasangkan setiap kata sifat dengan lawannya. Bacakan label cerita bersama; satu pasangan juga mengulang kata sifat lain.',
 '把每个描述词与它的反义词配对。一起读故事标签，其中一组也会复习别的描述词。',
 'صل كل كلمة وصف بالكلمة المضادة لها. اقرأ أوصاف القصة معا، فهناك زوج يراجع كلمة وصف أخرى أيضا.')
MEMORY_INSTRUCTION=T('Find each pair with the same picture. Name its describing word together. One picture reviews another word.',
 'Temukan setiap pasangan dengan gambar yang sama. Sebutkan kata sifatnya bersama. Satu gambar mengulang kata lain.',
 '找出图片相同的每一对，一起说说它的描述词。有一张图片用来复习另一个词。',
 'اعثر على كل زوج من الصور المتطابقة. قل كلمة الوصف مع الكبير. تراجع صورة واحدة كلمة أخرى.')

def pair_bank(a,b):
    support=[p for p in PAIR_KEYS if a not in p and b not in p]
    bank=[]
    for side in range(2):
        for sa,sb in support:
            keys=[(a,b)[side],(sa,sb)[side]]
            bank.append({'instruction':copy.deepcopy(PAIR_INSTRUCTION),'options':[pic(k,f'l{i}') for i,k in enumerate(keys)],
                         'rightOptions':[pic(OPPOSITES[k],f'r{i}') for i,k in enumerate(keys)],
                         'pairs':[{'left':f'l{i}','right':f'r{i}'} for i in range(2)],'answer':[],'layout':'story-choices'})
    return bank

def memory_bank(a,b):
    support=[k for pair in PAIR_KEYS for k in pair if k not in (a,b)]
    return [{'instruction':copy.deepcopy(MEMORY_INSTRUCTION),'options':[pic(k,f'p{i}') for i,k in enumerate([a,b,review])],'answer':[]} for review in support]

def sort_bank(cid,a,b):
    extra=('open-book','closed-book') if cid=='open-closed' else ('full-cup','empty-cup')
    groups={a:[a,extra[0]],b:[b,extra[1]]}; bank=[]
    subsets=lambda values: [[values[0]],[values[1]],values]
    for left in subsets(groups[a]):
        for right in subsets(groups[b]):
            keys=left+right; prompt={}
            for lang in LANGS:
                names=f'{CARDS[a]["word"][lang]} / {CARDS[b]["word"][lang]}'
                prompt[lang]={'en':f'Sort the picture cards by their describing words: {names}. Choose a card, then its group.',
                              'id':f'Kelompokkan kartu gambar menurut kata sifatnya: {names}. Pilih kartu, lalu kelompoknya.',
                              'zh':f'按描述词给图片卡分类：{names}。先选一张卡，再选它的分组。',
                              'ar':f'صنف بطاقات الصور بحسب كلمات الوصف: {names}. اختر بطاقة ثم مجموعتها.'}[lang]
            bank.append({'instruction':prompt,'options':[pic(k,f'o{i}') for i,k in enumerate(keys)],
                         'bins':[{'id':k,'label':copy.deepcopy(CARDS[k]['word']),'asset':CARDS[k]['asset']} for k in (a,b)],
                         'pairs':[{'left':f'o{i}','right':a if k in groups[a] else b} for i,k in enumerate(keys)],'answer':[]})
    return bank

def pattern_bank(a,b):
    bank=[]
    for unit in [(a,b),(b,a),(a,a,b),(b,b,a),(a,b,b),(b,a,a),(a,a,b,b),(b,b,a,a)]:
        # The named unit removes any ambiguity about the intended rule.
        for missing in (5,6):
            length=7; keys=[unit[i%len(unit)] for i in range(length)]; prompt={}
            for lang in LANGS:
                names=(' ثم ' if lang=='ar' else ' → ').join(CARDS[k]['word'][lang] for k in unit)
                prompt[lang]={'en':f'Repeat this word pattern: {names}. Fill the one missing picture.',
                              'id':f'Ulangi pola kata ini: {names}. Isi satu gambar yang hilang.',
                              'zh':f'重复这个词语规律：{names}。填上唯一缺少的图片。',
                              'ar':f'كرر نمط الكلمات هذا: {names}. أكمل الصورة الوحيدة الناقصة.'}[lang]
            bank.append({'instruction':prompt,'patternItems':[None if i==missing else pic(k,f's{i}') for i,k in enumerate(keys)],
                         'options':[pic(a,'o0'),pic(b,'o1')],'answer':['o0' if keys[missing]==a else 'o1'],
                         'patternUnit':list(unit),'missingIndex':missing,'layout':'story-choices'})
    return bank

def kind_identify_bank():
    bank=[]
    for i,(key,asset,label,word) in enumerate(KIND):
        for mode in ('meaning','quote'):
            keys=[key,KIND[(i+1)%8][0],KIND[(i+3)%8][0]]; prompt={}
            for lang in LANGS:
                target=word[lang] if mode=='meaning' else label[lang]
                prompt[lang]=({'en':f'Listen for “{target}” in the quoted words. Choose the matching quotation.',
                              'id':f'Dengarkan “{target}” dalam kata-kata kutipan. Pilih kutipan yang cocok.',
                              'zh':f'听听哪句引述的话表达“{target}”。请选择对应的句子。',
                              'ar':f'استمع إلى معنى «{target}» في الكلمات المقتبسة. اختر العبارة المناسبة.'} if mode=='meaning' else
                             {'en':f'A character reads these exact words: {target} Find the same quotation.',
                              'id':f'Seorang tokoh membaca kata-kata ini: {target} Cari kutipan yang sama.',
                              'zh':f'一个角色读出这句话：{target}请选择相同的引述句子。',
                              'ar':f'تقرأ شخصية هذه الكلمات بالضبط: {target} ابحث عن العبارة نفسها.'})[lang]
            bank.append({'instruction':prompt,'options':[pic(k,f'o{j}') for j,k in enumerate(keys)],'answer':['o0'],
                         'layout':'story-choices','scenarioId':f'kind-descriptions:{mode}:{key}'})
    return bank

def kind_pair_bank():
    prompt=T('Match cards with exactly the same quoted words. These are kind words or personal choices, not a comparison of people.',
             'Pasangkan kartu dengan kata-kata kutipan yang persis sama. Ini kata ramah atau pilihan pribadi, bukan perbandingan orang.',
             '把引述文字完全相同的卡片配对。这些是友善的话或个人选择，不是在比较人。',
             'صل البطاقات التي تحمل الكلمات المقتبسة نفسها تماما. هذه كلمات لطيفة أو اختيارات شخصية وليست مقارنة بين الناس.')
    bank=[]
    for keys in itertools.combinations([row[0] for row in KIND],3):
        bank.append({'instruction':copy.deepcopy(prompt),'options':[pic(k,f'l{i}') for i,k in enumerate(keys)],
                     'rightOptions':[pic(k,f'r{i}') for i,k in enumerate(keys)],'pairs':[{'left':f'l{i}','right':f'r{i}'} for i in range(3)],
                     'answer':[],'layout':'story-choices'})
    return bank

def build():
    categories=[]; worksheets=[]
    for cid,a,b,title in SPECS:
        desc=T(f'Explore {title["en"].lower()} with picture words, matching, and short games.',
               f'Kenali {title["id"].lower()} melalui kata bergambar, pasangan, dan permainan singkat.',
               f'通过图片词语、配对和简短游戏认识{title["zh"]}。',
               f'تعرف إلى كلمات «{title["ar"]}» بالصور والمطابقة والألعاب القصيرة.')
        categories.append({'id':cid,'group':'adjectives','engine':'identify','age':2,'ageRange':[2,6],
                           'asset':CARDS[a]['asset'],'title':title,'description':desc,'worksheetCount':24})
        if cid=='kind-descriptions':
            banks={'identify':kind_identify_bank(),'pair':kind_pair_bank()}
            schedule=[('identify',v) for v in range(12)]+[('pair',v) for v in range(12)]
            note=KIND_NOTE
        else:
            banks={'identify':identify_bank(cid,a,b),'pair':pair_bank(a,b),'memory':memory_bank(a,b),'pattern':pattern_bank(a,b)}
            if cid in ('open-closed','full-empty'): banks['sort']=sort_bank(cid,a,b)
            mid='sort' if cid in ('open-closed','full-empty') else 'memory'
            schedule=[('identify',v) for v in range(8)]+[('pair',v) for v in range(8)]+[(mid,v) for v in range(4)]+[('pattern',v) for v in range(4)]
            note=T(*[' '.join([GENERAL_NOTE[l],TEMPERATURE_NOTE[l],STORY_NOTE[l]]) for l in LANGS])
        for v,(engine,variation) in enumerate(schedule):
            bank=banks[engine]
            # Pick different subsets for adjacent worksheets. A worksheet never
            # receives repeated tasks, even after ignoring every option position.
            selected=four_ids(len(bank),variation)
            rounds=[]
            for r,idx in enumerate(selected):
                activity=copy.deepcopy(bank[idx]); activity['options']=rotate(activity['options'],v*3+r)
                if 'rightOptions' in activity: activity['rightOptions']=rotate(activity['rightOptions'],v+r+1)
                if 'bins' in activity: activity['bins']=rotate(activity['bins'],v+r)
                rounds.append(activity)
            age={'identify':2,'pair':3,'sort':3,'memory':3,'pattern':4}[engine]
            w={'id':f'{cid}-{v+1:02d}','category':cid,'engine':engine,'variant':v+1,'difficulty':1 if engine=='identify' else 3 if engine=='pattern' else 2,
               'age':age,'ageRange':[age,6],'title':copy.deepcopy(title),'note':copy.deepcopy(note),
               'offscreen':copy.deepcopy(KIND_OFFSCREEN if cid=='kind-descriptions' else OFFSCREEN),'rounds':rounds}
            w.update(copy.deepcopy(rounds[0])); worksheets.append(w)
    return categories,worksheets

def write(path,data):
    payload=json.dumps(data,ensure_ascii=False,separators=(',',':'))+'\n'; path.write_text(payload,encoding='utf8')
    return hashlib.sha256(payload.encode()).hexdigest()
def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent); p.add_argument('--skip-audit',action='store_true'); args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=True); categories,worksheets=build()
    hashes={name:write(args.out/name,data) for name,data in [('expansion-categories.json',categories),('expansion-worksheets.json',worksheets),('art-labels-new.json',ART_LABELS)]}
    manifest={'schema':'Normalized Worksheet; root mirrors round 1. Mixed worksheet engines per category; sort bins use exact pairs; memory uses unique canonical cards duplicated by renderer.',
              'categoryCount':12,'worksheetCount':288,'roundCount':1152,'worksheetsPerCategory':24,'roundsPerWorksheet':4,'languages':list(LANGS),
              'engines':sorted({w['engine'] for w in worksheets}),'groupIds':['adjectives'],
              'requiredAssets':sorted({c['asset'] for c in CARDS.values()}),'sha256':hashes,
              'contentRules':['Adult-supported ages 2–6','Every visible and narrated Text includes English, Indonesian, Chinese, and Modern Standard Arabic',
                              'No comparisons or rankings of human appearance or worth','Handsome and beautiful occur in quoted optional compliments or self-expression',
                              'Weight, speed, and sound volume use explicit story labels','Temperature is picture play only; no real touch or taste experiment',
                              'Pattern units are named explicitly','Four distinct semantic tasks and 24 distinct unordered task sets per category',
                              'Short opposite-word pair games include one review contrast','Memory pictures are visually distinct canonical cards'],
              'limits':['Automated semantic audit cannot verify actual art crop identity or renderer behavior; browser and artwork review are required.','Translations are authored in four languages; no professional language certification is claimed.']}
    write(args.out/'expansion-manifest.json',manifest)
    if not args.skip_audit: subprocess.run([sys.executable,str(Path(__file__).with_name('validate_adjectives.py')),'--out',str(args.out)],check=True)
    print(json.dumps({'categories':len(categories),'worksheets':len(worksheets),'rounds':sum(len(w['rounds']) for w in worksheets),'out':str(args.out)}))
if __name__=='__main__': main()
