#!/usr/bin/env python3
"""Generate 12 trilingual habit categories, 288 worksheets and 1,152 rounds.

Only writes to --out. No network, runtime dependencies, random state, or Site reads.
Run: python generate_habits.py --out OUTPUT_DIRECTORY
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


def T(en, id, zh):
    return {'en': en, 'id': id, 'zh': zh}


CARDS = {}


def card(key, asset, en, id, zh):
    CARDS[key] = {'asset': asset, 'label': T(en, id, zh)}
    return key


# Art may illustrate a general action. The read-aloud label specifies this story's task.
for row in [
 ('brush','habit-toothbrush','Toothbrush','Sikat gigi','牙刷'),
 ('paste','habit-toothpaste','Toothpaste','Pasta gigi','牙膏'),
 ('clean-tooth','habit-clean-tooth','Clean tooth','Gigi bersih','干净的牙齿'),
 ('food-tooth','habit-food-tooth','Food on a tooth','Sisa makanan di gigi','牙齿上的食物残渣'),
 ('soap','habit-soap','Soap','Sabun','肥皂'),
 ('shower','habit-shower','Bath water','Air untuk mandi','洗澡水'),
 ('towel','habit-towel','Clean towel','Handuk bersih','干净的毛巾'),
 ('shirt','habit-clean-shirt','Clean shirt','Baju bersih','干净的上衣'),
 ('wash','habit-handwash','Wash hands with soap and water','Cuci tangan dengan sabun dan air','用肥皂和水洗手'),
 ('tissue','habit-tissue','Tissue','Tisu','纸巾'),
 ('toilet','habit-toilet','Toilet','Toilet','马桶'),
 ('flush','habit-flush','Flush with help','Siram toilet dengan bantuan','请大人帮忙冲水'),
 ('plate','habit-plate','Plate','Piring','盘子'),
 ('cup','habit-cup','Drinking cup','Gelas minum','水杯'),
 ('bed','habit-bed','Bed','Tempat tidur','床'),
 ('basket','habit-toy-basket','Toy basket','Keranjang mainan','玩具篮'),
 ('brushing','habit-brushing','Brush with a grown-up','Sikat gigi bersama pendamping','和大人一起刷牙'),
 ('bathing','habit-bathing','Wash the body with a grown-up','Bersihkan badan bersama pendamping','在大人陪伴下洗澡'),
 ('drying','habit-drying','Dry with a clean towel','Keringkan dengan handuk bersih','用干净的毛巾擦干'),
 ('sleeping','habit-sleeping','Rest in bed','Beristirahat di tempat tidur','在床上休息'),
 ('eating','habit-eating','Sit for a meal','Duduk untuk makan','坐下来吃饭'),
 ('drinking','habit-drinking','Drink water','Minum air','喝水'),
 ('tidying','habit-tidying','Put toys away','Simpan mainan','收好玩具'),
 ('helping','habit-helping','Help with a small task','Bantu tugas kecil','帮忙做一件小事'),
 ('sharing','habit-sharing','Offer a turn','Tawarkan giliran','邀请别人轮流玩'),
 ('waiting','habit-waiting','Wait for a turn','Tunggu giliran','等待轮到自己'),
 ('hello','habit-greeting','Hello!','Halo!','你好！'),
 ('thanks','habit-thanking','Thank you!','Terima kasih!','谢谢！'),
 ('sorry','habit-apologizing','Sorry, I bumped you.','Maaf, aku tidak sengaja menyenggolmu.','对不起，我不小心碰到你了。'),
 ('help','habit-asking-help','Please help me.','Tolong bantu aku.','请帮帮我。'),
 ('gentle','habit-gentle','Use gentle hands','Gunakan tangan dengan lembut','动作轻轻的'),
 ('cough','habit-cover-cough','Cover a cough with an elbow','Tutup batuk dengan siku','用手肘遮住咳嗽'),
 ('book','book','Book','Buku','书'),
 ('spoon','spoon','Spoon','Sendok','勺子'),
 ('chair','chair','Chair','Kursi','椅子'),
 ('table','table','Table','Meja','桌子'),
 ('apple','apple','Apple','Apel','苹果'),
 ('banana','banana','Banana','Pisang','香蕉'),
 ('water','water-glass','Drinking water','Air minum','饮用水'),
 ('blocks','building-blocks','Building blocks','Balok mainan','积木'),
 ('car','car','Toy car picture','Gambar mobil mainan','玩具汽车图'),
 ('football','football','Football','Bola sepak','足球'),
 ('basketball','basketball','Basketball','Bola basket','篮球'),
 ('pencil','pencil','Pencil','Pensil','铅笔'),
 ('ruler','ruler','Ruler','Penggaris','尺子'),
 ('bag','bag','Bag','Tas','包'),
 ('family','family','Trusted grown-up','Pendamping tepercaya','信任的大人'),
 ('water-can','watering-can','Small watering can','Penyiram kecil','小洒水壶'),
 ('please','habit-asking-help','May I have a turn, please?','Bolehkah aku mendapat giliran?','请问可以轮到我吗？'),
 ('no-thanks','habit-greeting','No, thank you.','Tidak, terima kasih.','不用了，谢谢。'),
 ('excuse','habit-greeting','Excuse me, may I pass?','Permisi, boleh aku lewat?','不好意思，可以让我过去吗？'),
 ('bye','habit-greeting','Goodbye!','Sampai jumpa!','再见！'),
 ('goodnight','habit-sleeping','Good night!','Selamat tidur!','晚安！'),
 ('stop','habit-gentle','Please stop. I need space.','Tolong berhenti. Aku perlu ruang.','请停下来，我需要一点空间。'),
 ('are-you-ok','habit-gentle','Are you okay?','Kamu baik-baik saja?','你还好吗？'),
 ('welcome','habit-thanking',"You're welcome!",'Sama-sama!','不客气！'),
 ('ask-first','habit-asking-help','Ask before taking','Tanya sebelum mengambil','拿东西前先问一问'),
 ('quiet','habit-gentle','Use a quiet voice','Gunakan suara pelan','轻声说话'),
 ('space','habit-gentle','Give some space','Beri ruang','留出一点空间'),
 ('soft-ball','habit-gentle','Roll a soft ball gently','Gulirkan bola lembut perlahan','轻轻地滚软球'),
 ('show','habit-helping','Show slowly and wait','Tunjukkan perlahan lalu tunggu','慢慢示范，再等一等'),
 ('adult-help','habit-asking-help','Ask a trusted grown-up to help','Minta bantuan pendamping tepercaya','请信任的大人帮忙'),
 ('wave','habit-greeting','Wave if you want to','Lambaikan tangan jika kamu mau','愿意的话可以挥挥手'),
 ('offer','habit-sharing','Offer and listen to the answer','Tawarkan lalu dengarkan jawabannya','先邀请，再听对方的回答'),
 ('listen','habit-gentle','Listen without rushing','Dengarkan tanpa terburu-buru','耐心听对方说'),
 ('invite','habit-sharing','Would you like to play?','Mau bermain bersama?','你想一起玩吗？'),
 ('return','habit-sharing','Return the borrowed toy','Kembalikan mainan pinjaman','归还借来的玩具'),
 ('repair','habit-helping','Offer to help rebuild','Tawarkan bantuan membangun kembali','主动提出一起重新搭好'),
 ('different','habit-gentle','Let them choose differently','Biarkan ia memilih yang berbeda','允许对方选择不同的玩法'),
 ('take-break','habit-sleeping','Take a quiet break','Istirahat sebentar di tempat tenang','安静地休息一会儿'),
 ('own-brush','habit-toothbrush','Use your own toothbrush','Gunakan sikat gigimu sendiri','使用自己的牙刷'),
 ('gentle-brush','habit-brushing','Brush gently with a grown-up','Sikat perlahan bersama pendamping','和大人一起轻轻刷牙'),
 ('tell-discomfort','habit-asking-help','Tell a grown-up it feels uncomfortable','Beri tahu pendamping jika terasa tidak nyaman','不舒服时告诉大人'),
 ('rinse-brush','habit-toothbrush','Rinse the toothbrush with help','Bilas sikat gigi dengan bantuan','在大人帮助下冲洗牙刷'),
 ('put-brush','habit-toothbrush','Put the brush in its holder','Taruh sikat gigi di tempatnya','把牙刷放回架子上'),
 ('wait-paste','habit-toothpaste','Let a grown-up prepare the toothpaste','Biarkan pendamping menyiapkan pasta gigi','请大人准备牙膏'),
 ('hands-back','habit-handwash','Rub the backs of the hands','Gosok punggung tangan','搓洗手背'),
 ('hands-between','habit-handwash','Rub between the fingers','Gosok sela jari','搓洗指缝'),
 ('rinse-hands','habit-handwash','Rinse the soap away','Bilas sabun sampai bersih','把肥皂冲干净'),
 ('wet-hands','habit-handwash','Wet hands with clean running water','Basahi tangan dengan air bersih mengalir','用干净的流动水湿手'),
 ('rub-hands','habit-handwash','Rub soapy hands together','Gosok kedua tangan yang bersabun','双手抹上肥皂后搓一搓'),
 ('dry-hands','habit-towel','Dry hands with a clean towel','Keringkan tangan dengan handuk bersih','用干净的毛巾擦干手'),
]:
    card(*row)


SCENARIOS = {}


def scenario(cid, key, en, id, zh, answer, distractors):
    SCENARIOS.setdefault(cid, []).append({'key': key, 'prompt': T(en, id, zh),
                                         'answer': answer, 'distractors': distractors.split()})


def S(cid, rows):
    for row in rows:
        scenario(cid, *row)


S('brush-teeth', [
 ('tool','It is brushing time. Which tool cleans teeth with a grown-up?','Waktunya menyikat gigi. Alat mana yang membersihkan gigi bersama pendamping?','该刷牙了。和大人一起刷牙要用哪种工具？','brush','soap towel spoon'),
 ('food','A little food is left on a tooth. Which picture shows the food to clean away?','Ada sedikit sisa makanan di gigi. Gambar mana menunjukkan sisa makanan yang akan dibersihkan?','牙齿上留了一点食物。哪张图画着要清理的食物残渣？','food-tooth','clean-tooth cup shirt'),
 ('clean','After brushing, we talk about clean teeth. Choose the clean tooth picture.','Sesudah menyikat gigi, kita membahas gigi bersih. Pilih gambar gigi bersih.','刷牙后，我们说说干净的牙齿。请选择干净牙齿的图片。','clean-tooth','food-tooth soap spoon'),
 ('paste','A grown-up is preparing the brush. Which tube belongs to toothbrushing?','Pendamping menyiapkan sikat gigi. Tabung mana yang dipakai untuk menyikat gigi?','大人正在准备牙刷。刷牙需要哪一管用品？','paste','soap cup towel'),
 ('together','You want help reaching your back teeth. Choose brushing together.','Kamu ingin bantuan menjangkau gigi belakang. Pilih menyikat gigi bersama pendamping.','你想请人帮忙刷后面的牙齿。请选择和大人一起刷牙。','brushing','bathing eating sleeping'),
 ('personal','There are several brushes at home. Which choice uses the brush that belongs to you?','Ada beberapa sikat gigi di rumah. Pilihan mana memakai sikat gigimu sendiri?','家里有几把牙刷。哪个选择表示使用自己的牙刷？','own-brush','put-brush rinse-brush wait-paste'),
 ('gentle','The brush is ready. Choose a gentle way to brush with a grown-up.','Sikat gigi sudah siap. Pilih cara menyikat perlahan bersama pendamping.','牙刷准备好了。请选择和大人轻轻刷牙的做法。','gentle-brush','rinse-brush put-brush waiting'),
 ('comfort','Brushing feels uncomfortable today. What can you tell a grown-up?','Hari ini menyikat gigi terasa tidak nyaman. Apa yang bisa kamu sampaikan kepada pendamping?','今天刷牙时不太舒服。你可以怎样告诉大人？','tell-discomfort','hello thanks goodnight'),
 ('after','Brushing is finished. The brush needs washing. Choose rinsing the brush.','Menyikat gigi sudah selesai. Sikatnya perlu dibersihkan. Pilih membilas sikat gigi.','刷完牙了，牙刷也需要清洗。请选择冲洗牙刷。','rinse-brush','put-brush eating sleeping'),
 ('holder','The toothbrush has been rinsed. Where does its tidy-up card tell you to put it?','Sikat gigi sudah dibilas. Kartu merapikan menyuruhmu menaruhnya di mana?','牙刷冲洗好了。收纳卡上说要把它放在哪里？','put-brush','wash dry-hands eating'),
 ('prepare','Before brushing, who can help prepare the toothpaste? Choose the helpful step.','Sebelum menyikat gigi, siapa yang bisa membantu menyiapkan pasta gigi? Pilih langkahnya.','刷牙前，可以请谁帮忙准备牙膏？请选择这个步骤。','wait-paste','put-brush rinse-brush sleeping'),
 ('evening','Your bedtime story can wait a moment. Choose the tooth-care activity with a grown-up.','Cerita sebelum tidur bisa menunggu sebentar. Pilih kegiatan merawat gigi bersama pendamping.','睡前故事可以等一会儿。请选择和大人一起护理牙齿的活动。','brushing','book tidying drinking'),
])

S('wash-hands', [
 ('meal','Lunch is ready. Choose handwashing before eating.','Makan siang sudah siap. Pilih mencuci tangan sebelum makan.','午饭准备好了。请选择吃饭前洗手。','wash','eating sleeping tidying'),
 ('toilet','You have finished using the toilet. Choose handwashing.','Kamu selesai memakai toilet. Pilih mencuci tangan.','你上完厕所了。请选择洗手。','wash','book eating sleeping'),
 ('soil','There is soil on your hands after gardening. Choose washing with soap and water.','Ada tanah di tangan setelah berkebun. Pilih mencuci dengan sabun dan air.','种完花，手上沾了泥土。请选择用肥皂和水洗手。','wash','tissue shirt cup'),
 ('soap','The clean running water is ready. What do we add to wash our hands?','Air bersih mengalir sudah siap. Apa yang kita gunakan untuk mencuci tangan?','干净的流动水准备好了。洗手还要用什么？','soap','paste spoon book'),
 ('wet','Before adding soap, choose wetting hands with clean running water.','Sebelum memakai sabun, pilih membasahi tangan dengan air bersih mengalir.','用肥皂前，请选择用干净的流动水把手弄湿。','wet-hands','dry-hands rub-hands rinse-hands'),
 ('rub','There is soap on both hands. Choose rubbing soapy hands together.','Kedua tangan sudah bersabun. Pilih menggosok kedua tangan.','两只手都抹好了肥皂。请选择双手搓一搓。','rub-hands','dry-hands wet-hands eating'),
 ('back','We washed our palms. Which card reminds us to rub the backs of our hands too?','Telapak tangan sudah digosok. Kartu mana mengingatkan kita menggosok punggung tangan juga?','手心搓过了。哪张卡提醒我们也要搓洗手背？','hands-back','hands-between dry-hands cup'),
 ('between','Soap can go between our fingers too. Choose that rubbing step.','Sela jari juga digosok dengan sabun. Pilih langkah itu.','指缝也要用肥皂搓洗。请选择这个步骤。','hands-between','hands-back dry-hands book'),
 ('rinse','We finished rubbing our soapy hands. Choose rinsing the soap away.','Kita selesai menggosok tangan bersabun. Pilih membilas sabunnya.','双手搓洗好了。请选择把肥皂冲干净。','rinse-hands','rub-hands soap sleeping'),
 ('dry','Our hands are rinsed and wet. Choose drying them with a clean towel.','Tangan sudah dibilas dan masih basah. Pilih mengeringkan dengan handuk bersih.','双手冲干净了，还湿湿的。请选择用干净的毛巾擦干。','dry-hands','wet-hands rinse-hands book'),
 ('reach','The tap is hard to reach. Who can help you wash your hands?','Keran sulit dijangkau. Siapa yang bisa membantumu mencuci tangan?','水龙头够不到。谁可以帮你洗手？','adult-help','waiting hello goodnight'),
 ('nose','You used a tissue to blow your nose. Choose washing your hands next.','Kamu memakai tisu untuk membuang ingus. Pilih mencuci tangan sesudahnya.','你刚用纸巾擤了鼻涕。接下来请选择洗手。','wash','eating sleeping sharing'),
])

S('polite-words', [
 ('gift','A friend gives you a picture they made. What words show thanks?','Teman memberimu gambar buatannya. Kata apa yang menunjukkan terima kasih?','朋友送给你一幅画。你可以说什么表示感谢？','thanks','hello bye goodnight'),
 ('arrive','You meet a friend at the door. Choose a greeting.','Kamu bertemu teman di pintu. Pilih ucapan sapaan.','你在门口遇见朋友。请选择一句问候。','hello','thanks bye goodnight'),
 ('leave','Playtime is over and you are going home. Choose a farewell.','Waktu bermain selesai dan kamu pulang. Pilih ucapan perpisahan.','玩耍结束了，你要回家了。请选择一句告别的话。','bye','hello please welcome'),
 ('bedtime','Someone is settling into bed. Choose a bedtime wish.','Seseorang bersiap tidur. Pilih ucapan sebelum tidur.','有人准备睡觉了。请选择一句睡前祝福。','goodnight','hello excuse please'),
 ('turn','You would like a turn with the toy. Choose words to ask.','Kamu ingin mendapat giliran bermain. Pilih kata untuk meminta.','你也想玩这个玩具。请选择一句请求轮流玩的话。','please','bye thanks goodnight'),
 ('help','Your bag will not open. Choose words to ask for help.','Tasmu sulit dibuka. Pilih kata untuk meminta bantuan.','你的包打不开。请选择一句求助的话。','help','hello bye welcome'),
 ('decline','You do not want another turn. Choose a polite way to say no.','Kamu tidak ingin giliran lagi. Pilih cara sopan untuk menolak.','你不想再玩一轮了。请选择一句礼貌拒绝的话。','no-thanks','please hello goodnight'),
 ('pass','Someone is in the doorway. You want to pass. What can you say?','Ada orang di pintu. Kamu ingin lewat. Apa yang bisa kamu katakan?','有人站在门口，你想过去。你可以说什么？','excuse','bye thanks goodnight'),
 ('bump','You accidentally bump a friend. Choose words that name what happened.','Kamu tidak sengaja menyenggol teman. Pilih kata yang menyebut kejadian itu.','你不小心碰到了朋友。请选择一句说明发生了什么的话。','sorry','hello bye please'),
 ('boundary','A game feels too rough. Choose words that ask for space.','Permainan terasa terlalu kasar. Pilih kata untuk meminta ruang.','游戏的动作太大，让你不舒服。请选择一句表达需要空间的话。','stop','hello welcome thanks'),
 ('check','A friend trips and gets up. Choose words to check how they feel.','Teman tersandung lalu berdiri. Pilih kata untuk menanyakan keadaannya.','朋友绊了一下又站起来了。请选择一句关心对方的话。','are-you-ok','goodnight bye please'),
 ('reply','Someone says thank you for your help. Choose a friendly reply.','Seseorang berterima kasih atas bantuanmu. Pilih jawaban yang ramah.','有人感谢你的帮助。请选择一句友善的回应。','welcome','bye goodnight excuse'),
])

S('gentle-with-younger', [
 ('sleep','A younger child is sleeping nearby. Choose a voice that lets them rest.','Anak yang lebih kecil sedang tidur di dekatmu. Pilih suara yang membantunya beristirahat.','旁边的小朋友睡着了。请选择让对方休息的说话方式。','quiet','invite hello please'),
 ('no-touch','A younger child says, "No touching." Choose how to respect that.','Anak yang lebih kecil berkata, "Jangan sentuh." Pilih cara menghormatinya.','小朋友说：“不要碰我。”请选择尊重对方的做法。','space','gentle sharing show'),
 ('ball','A younger child wants to play with a soft ball. Choose a gentle ball game.','Anak yang lebih kecil ingin bermain bola lembut. Pilih permainan bola yang lembut.','小朋友想玩软球。请选择动作轻轻的球类玩法。','soft-ball','book waiting sleeping'),
 ('show','A younger child asks how to stack a block. Choose a patient way to show them.','Anak yang lebih kecil bertanya cara menumpuk balok. Pilih cara menunjukkan dengan sabar.','小朋友问怎么搭积木。请选择耐心示范的做法。','show','waiting quiet space'),
 ('cry','A younger child is crying and you do not know why. Who can you ask for help?','Anak yang lebih kecil menangis dan kamu tidak tahu sebabnya. Kepada siapa kamu bisa meminta bantuan?','小朋友哭了，你不知道为什么。你可以请谁帮忙？','adult-help','hello bye please'),
 ('greeting','You want to greet a younger child without touching. Choose a greeting with your hand.','Kamu ingin menyapa anak yang lebih kecil tanpa menyentuh. Pilih sapaan dengan tangan.','你想不碰身体地向小朋友打招呼。请选择用手问候的方式。','wave','gentle show soft-ball'),
 ('offer','You have a toy to offer a younger child. Choose asking and listening.','Kamu ingin menawarkan mainan kepada anak yang lebih kecil. Pilih menawarkan dan mendengarkan.','你想邀请小朋友玩一个玩具。请选择先邀请再听回答的做法。','offer','return quiet sleeping'),
 ('talk','A younger child is trying to tell a story. Choose a patient listening action.','Anak yang lebih kecil mencoba bercerita. Pilih tindakan mendengarkan dengan sabar.','小朋友正在努力讲故事。请选择耐心倾听的做法。','listen','hello invite goodnight'),
 ('touch','A younger child says it is okay to hold hands. Choose a gentle way to do it.','Anak yang lebih kecil setuju bergandengan tangan. Pilih cara yang lembut.','小朋友同意牵手。请选择动作轻轻的做法。','gentle','space waiting show'),
 ('play-choice','A younger child wants to draw while you build. Choose respecting their choice.','Anak yang lebih kecil ingin menggambar saat kamu menyusun balok. Pilih menghormati pilihannya.','你想搭积木，小朋友想画画。请选择尊重对方选择的做法。','different','show return please'),
 ('turn','A younger child is still using a shared toy. Choose waiting for a turn.','Anak yang lebih kecil masih memakai mainan bersama. Pilih menunggu giliran.','小朋友还在玩共用的玩具。请选择等待轮流的做法。','waiting','return invite show'),
 ('heavy','A younger child needs to be lifted. Choose asking a grown-up to help.','Anak yang lebih kecil perlu digendong. Pilih meminta bantuan pendamping.','小朋友需要被抱起来。请选择请大人帮忙。','adult-help','soft-ball gentle sharing'),
])

S('friendly-choices', [
 ('join','A friend is alone and may want to play. Choose an invitation they can accept or decline.','Teman sedang sendiri dan mungkin ingin bermain. Pilih ajakan yang boleh diterima atau ditolak.','朋友独自待着，也许想一起玩。请选择一个可以接受或拒绝的邀请。','invite','return quiet bye'),
 ('borrow','You want to borrow a friend’s toy. Choose what to do before taking it.','Kamu ingin meminjam mainan teman. Pilih tindakan sebelum mengambilnya.','你想借朋友的玩具。拿之前可以先做什么？','ask-first','return repair sleeping'),
 ('return','Your turn with a borrowed toy is finished. Choose returning it.','Giliranmu memakai mainan pinjaman selesai. Pilih mengembalikannya.','借来的玩具玩好了。请选择归还玩具。','return','ask-first waiting invite'),
 ('wait','A friend is using the shared crayons. Choose waiting for your turn.','Teman sedang memakai krayon bersama. Pilih menunggu giliran.','朋友正在用共用的蜡笔。请选择等待轮到自己。','waiting','return quiet sleeping'),
 ('share','You are finished with a shared ball. Choose offering the next turn.','Kamu selesai memakai bola bersama. Pilih menawarkan giliran berikutnya.','你已经玩好共用的球了。请选择邀请别人接着玩。','sharing','ask-first return goodnight'),
 ('tower','You accidentally knock over a friend’s tower. Choose an offer to help fix it.','Kamu tidak sengaja merobohkan menara teman. Pilih tawaran untuk membantu memperbaikinya.','你不小心碰倒了朋友的积木塔。请选择提出帮忙修复。','repair','hello goodnight invite'),
 ('space','A friend asks for space. Choose a way to respect their request.','Teman meminta ruang. Pilih cara menghormati permintaannya.','朋友说想自己待一会儿。请选择尊重这个请求的做法。','space','invite soft-ball sharing'),
 ('different','Your friend chooses a different game. Choose letting them make that choice.','Temanmu memilih permainan lain. Pilih membiarkannya membuat pilihan itu.','朋友选择了不同的游戏。请选择允许对方自己决定。','different','show ask-first repair'),
 ('upset','You feel upset during play and want a pause. Choose a quiet break.','Kamu merasa kesal saat bermain dan ingin berhenti sebentar. Pilih istirahat tenang.','玩耍时你有些难过，想暂停一下。请选择安静休息一会儿。','take-break','invite sharing please'),
 ('problem','Two friends cannot agree on a turn. Choose asking a trusted grown-up for help.','Dua teman belum sepakat tentang giliran. Pilih meminta bantuan pendamping tepercaya.','两个朋友还没商量好谁先玩。请选择请信任的大人帮忙。','adult-help','hello bye sleeping'),
 ('story','A friend is telling you something important. Choose listening patiently.','Teman sedang menceritakan sesuatu yang penting. Pilih mendengarkan dengan sabar.','朋友正在讲一件重要的事。请选择耐心倾听。','listen','invite hello please'),
 ('comfort','You do not want a hug today. Choose a greeting that does not need touch.','Hari ini kamu tidak ingin dipeluk. Pilih sapaan tanpa sentuhan.','今天你不想拥抱。请选择不需要身体接触的问候。','wave','gentle show soft-ball'),
])


for row in [
 ('get-towel','habit-towel','Get a clean towel','Siapkan handuk bersih','准备干净的毛巾'),
 ('get-shirt','habit-clean-shirt','Choose clean clothes','Pilih pakaian bersih','选择干净的衣服'),
 ('wear-shirt','habit-clean-shirt','Put on clean clothes with help','Pakai pakaian bersih dengan bantuan','在帮助下穿好干净的衣服'),
 ('water-check','habit-asking-help','Ask a grown-up to check the water','Minta pendamping memeriksa air','请大人检查水温'),
 ('water-off','habit-shower','Let a grown-up turn off the water','Biarkan pendamping mematikan air','请大人关水'),
 ('rinse-body','habit-bathing','Rinse with a grown-up nearby','Bilas badan dengan pendamping di dekatmu','在大人陪伴下冲洗身体'),
 ('hang-towel','habit-towel','Hang the towel with help','Gantung handuk dengan bantuan','在帮助下挂好毛巾'),
 ('bath-help','habit-asking-help','Ask a grown-up to stay close','Minta pendamping tetap dekat','请大人陪在身边'),
 ('bath-pause','habit-asking-help','Say that you need a pause','Katakan bahwa kamu perlu jeda','说出自己想暂停一下'),
 ('listen-plan','habit-gentle','Listen to the bath plan together','Dengarkan rencana mandi bersama','一起听听洗澡的安排'),
 ('tell-toilet','habit-asking-help','Tell a grown-up you need the toilet','Beri tahu pendamping kamu perlu ke toilet','告诉大人你想上厕所'),
 ('toilet-help','habit-toilet','Use the toilet with support as needed','Gunakan toilet dengan bantuan bila perlu','需要时在帮助下如厕'),
 ('wipe-help','habit-tissue','Ask for help wiping','Minta bantuan membersihkan diri','请大人帮忙擦干净'),
 ('clothes-help','habit-clean-shirt','Adjust clothes with help','Rapikan pakaian dengan bantuan','在帮助下整理衣服'),
 ('privacy','habit-toilet','Ask for comfortable privacy','Minta privasi yang nyaman','请求让自己舒服的隐私空间'),
 ('clothing-change','habit-clean-shirt','Get fresh clothes with help','Ambil pakaian ganti dengan bantuan','在帮助下拿好替换衣服'),
 ('say-accident','habit-asking-help','Tell a grown-up about an accident','Beri tahu pendamping jika terlanjur mengompol','不小心尿湿了就告诉大人'),
 ('read','book','Read a book together','Baca buku bersama','一起读书'),
 ('choose-book','book','Choose a storybook','Pilih buku cerita','选一本故事书'),
 ('put-book','book','Put the book away','Simpan buku','把书放好'),
 ('pajamas','habit-clean-shirt','Put on sleep clothes with help','Pakai baju tidur dengan bantuan','在帮助下穿好睡衣'),
 ('sleep-help','habit-asking-help','Ask for help feeling comfortable','Minta bantuan agar nyaman','请大人帮自己调整得舒服些'),
 ('night-wave','habit-greeting','Wave good night','Lambaikan tangan mengucap selamat tidur','挥挥手说晚安'),
 ('morning','habit-greeting','Greet your family','Sapa keluargamu','向家人问好'),
 ('wake','habit-bed','Wake up and sit comfortably','Bangun dan duduk dengan nyaman','醒来后舒服地坐好'),
 ('put-plate','habit-plate','Put a light plate on the table','Taruh piring ringan di meja','把轻巧的盘子放到桌上'),
 ('put-cup','habit-cup','Set down your cup','Taruh gelasmu','把水杯放好'),
 ('put-spoon','spoon','Put out a spoon','Siapkan sendok','摆好勺子'),
 ('play-blocks','building-blocks','Play with blocks','Bermain balok','玩积木'),
 ('draw','pencil','Draw a picture','Menggambar','画一幅画'),
 ('put-pencil','pencil','Put the pencil away','Simpan pensil','把铅笔放好'),
 ('pack-book','bag','Put a book in your bag','Masukkan buku ke tas','把书放进包里'),
 ('choose-help','habit-helping','Choose a small helping task','Pilih tugas kecil untuk membantu','选择一件小事帮忙'),
 ('full','habit-eating','Say when you feel full','Katakan saat kamu merasa kenyang','吃饱时说出来'),
 ('more-water','habit-asking-help','Ask for more water','Minta tambahan air minum','请求再加一点水'),
 ('wipe-table','habit-helping','Wipe a small spill with a grown-up','Lap tumpahan kecil bersama pendamping','和大人一起擦掉一点洒出的水'),
]:
    card(*row)


STORIES = {}


def stories(cid, rows):
    STORIES[cid] = [{'key': key, 'title': T(en, id, zh), 'steps': steps.split()}
                    for key, en, id, zh, steps in rows]


stories('bath-routine', [
 ('wash-dry-dress','After playing outside','Setelah bermain di luar','户外玩耍后','bathing drying wear-shirt'),
 ('prepare','Getting ready together','Bersiap bersama','一起准备','get-towel water-check bathing'),
 ('finish','Finishing a bath','Menyelesaikan mandi','洗澡快结束了','rinse-body drying wear-shirt'),
 ('clothes','Preparing clean clothes','Menyiapkan pakaian bersih','准备干净的衣服','get-shirt bathing wear-shirt'),
 ('support','A grown-up stays nearby','Pendamping tetap dekat','大人陪在身边','bath-help water-check bathing'),
 ('comfortable','Making a comfortable plan','Membuat rencana yang nyaman','商量舒服的安排','listen-plan water-check bathing'),
 ('rinse','Washing and rinsing','Mencuci dan membilas','清洗和冲洗','bathing rinse-body drying'),
 ('towel','Caring for the towel','Merawat handuk','收好毛巾','drying wear-shirt hang-towel'),
 ('water','The water is finished','Air sudah selesai dipakai','用完洗澡水','rinse-body water-off drying'),
 ('pause','Taking a pause together','Berhenti sebentar bersama','一起暂停一下','bath-pause bath-help drying'),
 ('ready-towel','A towel ready for later','Handuk siap dipakai nanti','先准备好毛巾','get-towel bathing drying'),
 ('after-bath','A calm moment after a bath','Saat tenang setelah mandi','洗澡后的安静时刻','drying wear-shirt read'),
])

stories('toilet-care', [
 ('ask-go','Asking to use the toilet','Meminta ke toilet','告诉大人想上厕所','tell-toilet toilet-help wipe-help'),
 ('finish','Finishing with support','Menyelesaikan dengan bantuan','在帮助下完成','wipe-help clothes-help wash'),
 ('flush','After using the toilet','Setelah memakai toilet','上完厕所后','toilet-help flush wash'),
 ('dry','Hands after the toilet','Tangan setelah dari toilet','如厕后洗手','wash dry-hands tidying'),
 ('private','Comfortable privacy','Privasi yang nyaman','舒服的隐私空间','privacy toilet-help wipe-help'),
 ('clothes','Getting clothes comfortable','Merapikan pakaian agar nyaman','整理好衣服','toilet-help clothes-help wash'),
 ('ask-help','Help with wiping','Bantuan membersihkan diri','请人帮忙擦干净','wipe-help flush wash'),
 ('accident','An accident can be helped','Pendamping bisa membantu saat mengompol','尿湿了可以请大人帮忙','say-accident clothing-change wash'),
 ('support','A supported toilet visit','Ke toilet dengan bantuan','有人帮助的如厕时间','tell-toilet privacy toilet-help'),
 ('fresh','Getting fresh clothes','Mengambil pakaian ganti','拿好替换衣服','clothing-change clothes-help wash'),
 ('wash-next','Washing after getting dressed','Mencuci tangan setelah berpakaian','整理衣服后洗手','clothes-help wash dry-hands'),
 ('back-play','Back to play after washing','Kembali bermain setelah mencuci tangan','洗好手再去玩','wash dry-hands play-blocks'),
])

stories('bedtime-routine', [
 ('story','A story before resting','Cerita sebelum beristirahat','休息前听故事','brushing read sleeping'),
 ('clothes','Getting into sleep clothes','Memakai baju tidur','穿好睡衣','pajamas brushing sleeping'),
 ('choose','Choosing a bedtime book','Memilih buku sebelum tidur','选择睡前读的书','choose-book read put-book'),
 ('toys','Putting toys away','Menyimpan mainan','收好玩具','tidying pajamas sleeping'),
 ('water','A drink before the story','Minum sebelum cerita','听故事前喝点水','drinking brushing read'),
 ('goodnight','Saying good night','Mengucap selamat tidur','道晚安','read night-wave sleeping'),
 ('comfort','Getting comfortable','Mencari rasa nyaman','让自己舒服些','sleep-help read sleeping'),
 ('bath','From bath to a story','Dari mandi ke cerita','洗好澡再听故事','drying pajamas read'),
 ('book-away','Closing story time','Mengakhiri waktu cerita','结束故事时间','read put-book sleeping'),
 ('toilet','A toilet stop before rest','Ke toilet sebelum istirahat','休息前去厕所','toilet-help wash sleeping'),
 ('brush','Preparing for toothbrushing','Menyiapkan kegiatan sikat gigi','准备刷牙','wait-paste brushing put-brush'),
 ('quiet','A quiet end to the day','Akhir hari yang tenang','安静地结束一天','tidying read sleeping'),
])

stories('daily-routine', [
 ('morning','A friendly morning','Pagi yang ramah','友好的早晨','wake morning get-shirt'),
 ('breakfast','Getting breakfast ready','Menyiapkan sarapan','准备早餐','wash put-plate eating'),
 ('meal','From handwashing to a meal','Dari cuci tangan ke makan','洗好手再吃饭','wash dry-hands eating'),
 ('blocks','Blocks and tidy-up','Balok dan merapikan','玩积木和收积木','play-blocks tidying drinking'),
 ('art','Drawing time','Waktu menggambar','画画时间','draw put-pencil wash'),
 ('book','Taking a book along','Membawa buku','带上一本书','choose-book pack-book bye'),
 ('help','Choosing to help','Memilih untuk membantu','选择帮忙','choose-help helping thanks'),
 ('lunch','Setting a place','Menyiapkan tempat makan','摆好餐具','put-plate put-spoon eating'),
 ('spill','A little water spill','Sedikit air tumpah','洒了一点水','put-cup wipe-table wash'),
 ('rest','A quiet rest','Istirahat tenang','安静休息','tidying read sleeping'),
 ('outside','After outdoor play','Setelah bermain di luar','在外面玩耍后','wash dry-hands drinking'),
 ('evening','An evening together','Malam bersama','一起度过傍晚','brushing read night-wave'),
])


# Exact item-to-named-task matches. Several other tasks may also use an item in life;
# the instruction explicitly matches the item NAMED by each task in this game.
HELP_PAIRS = [
 ('towel', 'fold-towel', 'Fold a clean towel', 'Lipat handuk bersih', '折好干净的毛巾'),
 ('book', 'shelf-book', 'Put a book on a low shelf', 'Taruh buku di rak rendah', '把书放到矮书架上'),
 ('spoon', 'set-spoon', 'Set a spoon beside a plate', 'Taruh sendok di samping piring', '把勺子放到盘子旁边'),
 ('plate', 'set-plate', 'Set a light plate on the table', 'Taruh piring ringan di meja', '把轻巧的盘子放到桌上'),
 ('cup', 'set-cup', 'Set an empty unbreakable cup down', 'Taruh gelas kosong yang tidak mudah pecah', '放好不会摔碎的空水杯'),
 ('blocks', 'put-blocks', 'Put large blocks in a basket', 'Masukkan balok besar ke keranjang', '把大积木放进篮子里'),
 ('shirt', 'fold-shirt', 'Fold a clean shirt with help', 'Lipat baju bersih dengan bantuan', '在帮助下折好干净的上衣'),
 ('pencil', 'put-pencils', 'Put pencils in their box', 'Simpan pensil di kotaknya', '把铅笔放进笔盒里'),
 ('bag', 'hang-bag', 'Put a light bag in its place', 'Taruh tas ringan di tempatnya', '把轻巧的包放回原处'),
 ('water-can', 'water-plant', 'Use a small watering can with help', 'Gunakan penyiram kecil dengan bantuan', '在帮助下使用小洒水壶'),
 ('football', 'put-ball', 'Return a football to the basket', 'Kembalikan bola sepak ke keranjang', '把足球放回篮子里'),
 ('tissue', 'bring-tissue', 'Bring a clean tissue when asked', 'Ambil tisu bersih saat diminta', '有人需要时拿一张干净纸巾'),
]
for item, key, en, id, zh in HELP_PAIRS:
    card(key, CARDS[item]['asset'], en, id, zh)


MEMORY_POOL = ['plate','cup','spoon','wash','dry-hands','eating','drinking','thanks','full','more-water','wipe-table','family']
SORT_POOLS = {
    'toys': ['blocks','car','football','basketball'],
    'meal': ['plate','cup','spoon'],
    'washing': ['soap','towel','brush','paste'],
    'drawing': ['pencil','ruler','book'],
}
SORT_LABELS = {
    'toys': T('Toy pictures','Gambar mainan','玩具图片'),
    'meal': T('Tableware pictures','Gambar peralatan makan','餐具图片'),
    'washing': T('Body-care item pictures','Gambar benda perawatan tubuh','身体护理用品图片'),
    'drawing': T('Book and stationery pictures','Gambar buku dan alat tulis','书和文具图片'),
}
SORT_ICONS = {'toys':'habit-toy-basket','meal':'habit-plate','washing':'habit-soap','drawing':'book'}
SORT_GROUPS = [('toys','meal'),('toys','washing'),('toys','drawing'),('meal','washing'),('drawing','meal'),('drawing','washing')]


def rotate(items, seed):
    result = copy.deepcopy(items)
    if seed % 2:
        result.reverse()
    cut = seed % len(result)
    return result[cut:] + result[:cut]


def pic(key, id):
    return {'id': id, 'kind': 'asset', **copy.deepcopy(CARDS[key]), 'showLabel': True}


def select_index(v, r):
    # Two genuinely different sets of four stories per starting story; not option shuffles.
    offsets = [0, 1, 3, 6] if v < 12 else [0, 2, 5, 8]
    return (v % 12 + offsets[r]) % 12


def identify(cid, v, r):
    story = SCENARIOS[cid][select_index(v, r)]
    keys = [story['answer']] + story['distractors'][:2 if v < 8 else 3]
    options = [pic(key, f'o{j}') for j, key in enumerate(keys)]
    return {'instruction': copy.deepcopy(story['prompt']), 'options': rotate(options, v * 5 + r),
            'answer': ['o0'], 'layout':'story-choices', 'scenarioId': f'{cid}:{story["key"]}'}


def sequencing(cid, v, r):
    story = STORIES[cid][select_index(v, r)]
    instruction = {}
    for lang in ('en', 'id', 'zh'):
        steps = ' → '.join(CARDS[key]['label'][lang] for key in story['steps'])
        instruction[lang] = {
            'en': f'{story["title"][lang]}. In this short story: {steps}. Choose the three cards in that order.',
            'id': f'{story["title"][lang]}. Dalam cerita pendek ini: {steps}. Pilih tiga kartu sesuai urutan itu.',
            'zh': f'{story["title"][lang]}。这个小故事的顺序是：{steps}。请按这个顺序选择三张卡。',
        }[lang]
    options = [pic(key, f'o{j}') for j, key in enumerate(story['steps'])]
    # Never show the three cards already in the answer order.
    shuffled = [options[1], options[2], options[0]] if (v + r) % 2 else [options[2], options[0], options[1]]
    return {'instruction': instruction, 'options': shuffled, 'answer': ['o0','o1','o2'],
            'scenarioId': f'{cid}:{story["key"]}'}


def combination(pool, count, seed):
    choices = list(itertools.combinations(pool, count))
    return list(choices[seed % len(choices)])


def matching(v, r):
    n = 2 if v < 8 else 3
    selected = combination(list(range(len(HELP_PAIRS))), n, v * 7 + r * 31 + r * r * 3)
    left = [pic(HELP_PAIRS[i][0], f'l{j}') for j, i in enumerate(selected)]
    right = [pic(HELP_PAIRS[i][1], f'r{j}') for j, i in enumerate(selected)]
    return {'instruction': T('Match each item to the helping task that names it. A grown-up can read the labels.',
                            'Pasangkan setiap benda dengan tugas membantu yang menyebut namanya. Pendamping boleh membacakan label.',
                            '把每件物品与提到它的帮忙任务配对。可以请大人读出标签。'),
            'options': rotate(left, v+r), 'rightOptions': rotate(right, v+r+3),
            'pairs': [{'left': f'l{j}', 'right': f'r{j}'} for j in range(n)], 'answer': []}


def memory(v, r):
    n = 2 if v < 8 else 3
    # 13 is coprime with both 12-choose-2 (66) and 12-choose-3 (220).
    keys = combination(MEMORY_POOL, n, v * 13 + r * 29 + r * r * 7)
    return {'instruction': T('Turn the mealtime cards over. Find each pair with the same picture and words.',
                            'Balik kartu waktu makan. Temukan setiap pasangan dengan gambar dan kata yang sama.',
                            '翻开用餐卡，找出图片和文字都一样的每一对。'),
            'options': rotate([pic(key, f'p{j}') for j, key in enumerate(keys)], v+r), 'answer': []}


def sorting(v, r):
    groups = SORT_GROUPS[(v + r + v // 6) % len(SORT_GROUPS)]
    counts = [1 + (v+r) % 2, 1 + (v+r+1) % 2] if v < 8 else ([2,2] if v < 16 else [3,2])
    bins = [{'id': group, 'label': copy.deepcopy(SORT_LABELS[group]), 'asset': SORT_ICONS[group]} for group in groups]
    options = []; pairs = []
    for group, count in zip(groups, counts):
        for key in combination(SORT_POOLS[group], min(count,len(SORT_POOLS[group])), v * 5 + r * 3):
            oid = f'o{len(options)}'
            options.append(pic(key, oid))
            pairs.append({'left': oid, 'right': group})
    prompt = {}
    for lang in ('en','id','zh'):
        names = ' / '.join(SORT_LABELS[group][lang] for group in groups)
        prompt[lang] = {'en': f'Tidy these picture cards into their named groups: {names}. Choose a card, then its group.',
                        'id': f'Rapikan kartu gambar ke kelompok bernama: {names}. Pilih kartu, lalu kelompoknya.',
                        'zh': f'请按名称整理图片卡：{names}。先选一张卡，再选它的分组。'}[lang]
    return {'instruction': prompt, 'options': rotate(options, v+r), 'bins': rotate(bins,v+r), 'pairs': pairs, 'answer': []}


SPECS = [
 ('brush-teeth','habits','identify',2,'habit-brushing',T('Brush My Teeth','Sikat Gigiku','一起刷牙'),T('Explore gentle tooth care with a grown-up.','Kenali perawatan gigi yang lembut bersama pendamping.','和大人一起认识轻柔的牙齿护理。')),
 ('bath-routine','habits','sequence',3,'habit-bathing',T('Bath-Time Stories','Cerita Waktu Mandi','洗澡小故事'),T('Follow three clearly named steps in supported bath-time stories.','Ikuti tiga langkah yang disebutkan dalam cerita mandi dengan pendamping.','按顺序选择有人陪伴的洗澡故事中的三个步骤。')),
 ('wash-hands','habits','identify',2,'habit-handwash',T('Wash My Hands','Cuci Tanganku','洗洗小手'),T('Choose handwashing tools, steps, and moments for washing.','Pilih alat, langkah, dan waktu untuk mencuci tangan.','认识洗手用品、步骤和需要洗手的时候。')),
 ('toilet-care','habits','sequence',3,'habit-toilet',T('Toilet Care with Help','Ke Toilet dengan Bantuan','有人帮助的如厕护理'),T('Follow short toilet-care stories with help and comfortable privacy.','Ikuti cerita pendek perawatan diri di toilet dengan bantuan dan privasi yang nyaman.','按顺序读懂有帮助、也有舒服隐私空间的如厕小故事。')),
 ('mealtime-habits','habits','memory',3,'habit-eating',T('Mealtime Picture Pairs','Pasangan Gambar Waktu Makan','用餐图片配对'),T('Find picture pairs about eating, drinking, and saying what you need.','Temukan pasangan gambar tentang makan, minum, dan menyampaikan kebutuhan.','寻找吃饭、喝水和表达需求的图片对子。')),
 ('bedtime-routine','habits','sequence',3,'habit-sleeping',T('Bedtime Stories in Order','Urutan Cerita Sebelum Tidur','睡前故事排一排'),T('Put three cards in the order stated for each calm bedtime story.','Susun tiga kartu sesuai urutan cerita tenang sebelum tidur.','按每个安静的睡前故事所说的顺序选择三张卡。')),
 ('tidy-toys','habits','sort',3,'habit-tidying',T('Tidy Our Picture Cards','Rapikan Kartu Gambar','整理图片卡'),T('Sort toys and everyday objects into clearly named picture groups.','Kelompokkan mainan dan benda sehari-hari ke kelompok gambar yang jelas namanya.','把玩具和日常用品图片放入名称明确的分组。')),
 ('polite-words','kindness','identify',2,'habit-thanking',T('Words with Care','Kata yang Ramah','温柔地表达'),T('Practice thanks, greetings, requests, and respectful boundaries.','Latih terima kasih, sapaan, permintaan, dan batasan yang saling menghormati.','练习感谢、问候、请求和表达彼此尊重的界限。')),
 ('helping-family','kindness','pair',3,'habit-helping',T('Small Ways to Help','Bantuan Kecil untuk Keluarga','帮忙做点小事'),T('Match familiar objects to small supported helping tasks.','Pasangkan benda yang dikenal dengan tugas membantu yang kecil dan didampingi.','把熟悉的物品与有人陪伴的小帮忙任务配对。')),
 ('gentle-with-younger','kindness','identify',2,'habit-gentle',T('Gentle with Younger Children','Lembut kepada yang Lebih Kecil','温柔对待小朋友'),T('Explore patient play, listening, space, and asking a grown-up for help.','Kenali bermain sabar, mendengarkan, memberi ruang, dan meminta bantuan pendamping.','认识耐心玩耍、倾听、留出空间和请大人帮忙。')),
 ('friendly-choices','kindness','identify',2,'habit-sharing',T('Friendly Choices','Pilihan yang Ramah','友善的选择'),T('Explore inviting, taking turns, repairing mistakes, and respecting choices.','Kenali mengajak, bergiliran, memperbaiki kesalahan, dan menghormati pilihan.','认识邀请、轮流、弥补小失误和尊重选择。')),
 ('daily-routine','habits','sequence',3,'habit-greeting',T('Little Daily Stories','Cerita Kecil Sehari-hari','日常小故事'),T('Follow the three stated steps in varied everyday stories.','Ikuti tiga langkah yang disebutkan dalam beragam cerita sehari-hari.','按各种日常小故事中说明的三个步骤排序。')),
]

GENERIC = T('Read the prompt and card labels aloud. Children may point, speak, or choose with help. Follow their comfort and interest.',
            'Bacakan petunjuk dan label kartu. Anak boleh menunjuk, berbicara, atau memilih dengan bantuan. Ikuti kenyamanan dan minatnya.',
            '请读出题目和卡片标签。孩子可以指一指、说一说，或在帮助下选择。尊重孩子的舒适感和兴趣。')
STORY_NOTE = T('These are short picture stories, not complete care instructions. Read the exact three-step order aloud. Adapt real routines to the child and provide help.',
               'Ini cerita gambar pendek, bukan petunjuk perawatan lengkap. Bacakan urutan tiga langkah yang tertera. Sesuaikan rutinitas nyata dengan anak dan berikan bantuan.',
               '这些是简短的图片故事，并不是完整的护理步骤。请读出所写的三个步骤。真实生活中要按孩子的需要调整并提供帮助。')
NOTES = {
 'brush-teeth': T('A grown-up helps with gentle brushing and prepares an age-appropriate amount of fluoride toothpaste. Talk about cleaning food and plaque from teeth without fear or shame.',
                  'Pendamping membantu menyikat dengan lembut dan menyiapkan pasta gigi berfluorida dalam jumlah sesuai usia. Bicarakan membersihkan sisa makanan dan plak tanpa menakut-nakuti atau mempermalukan.',
                  '大人帮助孩子轻轻刷牙，并按年龄准备适量含氟牙膏。可以说刷牙清理食物残渣和牙菌斑，不吓唬、不羞辱孩子。'),
 'bath-routine': T('A grown-up stays close and checks the water. Washing removes dirt. These short stories invite naming steps; a missed bath does not make a child bad or guarantee illness.',
                  'Pendamping tetap dekat dan memeriksa air. Mencuci membantu menghilangkan kotoran. Cerita pendek ini mengajak menyebut langkah; melewatkan mandi tidak membuat anak buruk atau pasti sakit.',
                  '大人要陪在身边并检查水温。清洗可以洗去污垢。这些小故事帮助认识步骤；一次没洗澡并不表示孩子不好，也不代表一定会生病。'),
 'wash-hands': T('Support washing with soap and clean running water: wet, lather, scrub for at least 20 seconds, rinse, then dry. Read action labels; the pictures illustrate selected steps.',
                'Bantu anak mencuci dengan sabun dan air bersih mengalir: basahi, beri sabun, gosok setidaknya 20 detik, bilas, lalu keringkan. Bacakan label tindakan; gambar menunjukkan beberapa langkah.',
                '帮助孩子用肥皂和干净的流动水洗手：湿手、抹肥皂、搓洗至少20秒、冲净、擦干。请读出动作标签；图片只展示其中的一些步骤。'),
 'toilet-care': T('Offer help and comfortable privacy. Toilet learning takes time; accidents are met calmly. These short stories are not a complete toilet-training method. Always support handwashing afterward.',
                 'Tawarkan bantuan dan privasi yang nyaman. Belajar ke toilet memerlukan waktu; tanggapi mengompol dengan tenang. Cerita pendek ini bukan metode latihan toilet lengkap. Selalu bantu mencuci tangan sesudahnya.',
                 '提供帮助和让孩子舒服的隐私空间。学习如厕需要时间，尿湿时平静应对。这些小故事不是完整的如厕训练方法。如厕后要帮助孩子洗手。'),
 'mealtime-habits': T('Match the same picture and words. Read the labels together. Let the child say when they are hungry, full, thirsty, or need help; this game does not ask them to finish a plate.',
                     'Pasangkan gambar dan kata yang sama. Bacakan label bersama. Izinkan anak menyampaikan lapar, kenyang, haus, atau perlu bantuan; permainan ini tidak meminta anak menghabiskan makanan.',
                     '寻找图片和文字相同的对子，一起读读标签。允许孩子表达饿了、饱了、渴了或需要帮助；游戏不要求孩子吃光盘里的食物。'),
 'tidy-toys': T('This is a picture classification game. The named groups are toys, tableware, body-care items, and books or stationery. Real tidy-up can be a small shared task with a grown-up.',
               'Ini permainan mengelompokkan gambar. Nama kelompoknya adalah mainan, peralatan makan, benda perawatan tubuh, serta buku atau alat tulis. Merapikan sungguhan bisa menjadi tugas kecil bersama pendamping.',
               '这是图片分类游戏，分组是玩具、餐具、身体护理用品、书和文具。真实的整理活动可以是和大人一起完成的一件小事。'),
 'polite-words': T('Read the words as choices for this story, not a test of being a good child. Children may say no, ask for space, or use gestures. Greetings never require hugs or touch.',
                  'Bacakan kata sebagai pilihan untuk cerita ini, bukan ujian menjadi anak baik. Anak boleh menolak, meminta ruang, atau memakai isyarat. Sapaan tidak harus disertai pelukan atau sentuhan.',
                  '这些话是故事中的表达选择，不是评判孩子好坏的考试。孩子可以拒绝、请求空间或用动作表达。问候不需要拥抱或身体接触。'),
 'helping-family': T('Helping is an invitation. Offer one small task, help as needed, and allow a child to decline or pause. Use large, light, safe objects; adults handle heavy, sharp, hot, or breakable items.',
                    'Membantu adalah ajakan. Tawarkan satu tugas kecil, bantu sesuai kebutuhan, dan izinkan anak menolak atau berhenti sebentar. Gunakan benda besar, ringan, dan aman; benda berat, tajam, panas, atau mudah pecah ditangani orang dewasa.',
                    '帮忙是一种邀请。可以提供一件小任务，按需要协助，并允许孩子拒绝或暂停。使用大件、轻巧、安全的物品；沉重、锋利、滚烫或易碎物品由大人处理。'),
 'gentle-with-younger': T('Being gentle includes listening, giving space, and asking an adult for help. Ask before touch and respect no. Children are not responsible for lifting, supervising, or caring for a baby alone.',
                        'Bersikap lembut termasuk mendengarkan, memberi ruang, dan meminta bantuan orang dewasa. Tanyakan sebelum menyentuh dan hormati penolakan. Anak tidak bertanggung jawab menggendong, mengawasi, atau merawat bayi sendirian.',
                        '温柔也包括倾听、留出空间和请大人帮忙。接触身体前先询问，并尊重拒绝。孩子不负责独自抱起、看护或照顾婴儿。'),
 'friendly-choices': T('Discuss what fits each story. Friendship allows different choices, boundaries, breaks, and asking for help. Sharing does not mean giving away a personal toy or agreeing to unwanted touch.',
                     'Bahas pilihan yang sesuai dengan tiap cerita. Berteman tetap memberi ruang untuk pilihan berbeda, batasan, istirahat, dan meminta bantuan. Berbagi bukan berarti harus menyerahkan mainan pribadi atau menerima sentuhan yang tidak diinginkan.',
                     '一起讨论每个故事中的选择。朋友之间也可以有不同选择、界限、暂停和求助。分享不表示必须交出自己的玩具，也不表示要接受不想要的身体接触。'),
}
OFFSCREEN = {
 'habits': T('Choose one picture together and tell a tiny story about caring for yourself. You can point, pretend with toys, or try one comfortable step with a grown-up.',
             'Pilih satu gambar bersama dan buat cerita singkat tentang merawat diri. Kamu boleh menunjuk, bermain pura-pura dengan mainan, atau mencoba satu langkah yang nyaman bersama pendamping.',
             '一起选一张图片，讲一个照顾自己的小故事。可以指一指、用玩具假装做一做，或和大人尝试一个舒服的小步骤。'),
 'kindness': T('Use two toys to tell a friendly story. Practice asking, listening, saying no kindly, or offering help. Let each character choose whether to join.',
               'Gunakan dua mainan untuk membuat cerita ramah. Latih bertanya, mendengarkan, menolak dengan ramah, atau menawarkan bantuan. Biarkan setiap tokoh memilih untuk ikut atau tidak.',
               '用两个玩具讲一个友善的小故事。练习询问、倾听、温和拒绝或提供帮助。让每个角色自己决定是否参加。'),
}

SOURCES = [
 {'url':'https://www.cdc.gov/clean-hands/about/index.html','supports':['handwashing moments','soap and clean running water','scrub for at least 20 seconds','rinse and dry']},
 {'url':'https://www.mouthhealthy.org/all-topics-a-z/brushing-your-teeth','supports':['gentle brushing','cleaning teeth','fluoride toothpaste']},
 {'url':'https://www.mouthhealthy.org/life-stages/babies-and-kids','supports':['developmentally appropriate early dental care','positive support']},
 {'url':'https://www.mouthhealthy.org/all-topics-a-z/tooth-decay-with-baby-bottles','supports':['grown-up supervision','gentle brushing for young children','age-appropriate fluoride toothpaste amount']},
]


def build():
    categories = []; worksheets = []
    for cid, group, engine, age, asset, title, description in SPECS:
        categories.append({'id':cid,'group':group,'engine':engine,'age':age,'ageRange':[age,6],
                           'asset':asset,'title':title,'description':description,'worksheetCount':24})
        for v in range(24):
            rounds = []
            for r in range(4):
                if engine == 'identify': activity = identify(cid,v,r)
                elif engine == 'sequence': activity = sequencing(cid,v,r)
                elif engine == 'pair': activity = matching(v,r)
                elif engine == 'memory': activity = memory(v,r)
                elif engine == 'sort': activity = sorting(v,r)
                else: raise ValueError(engine)
                rounds.append(activity)
            w = {'id':f'{cid}-{v+1:02d}','category':cid,'engine':engine,'variant':v+1,
                 'difficulty':1+v//8,'age':age,'ageRange':[age,6],'title':copy.deepcopy(title),
                 'rounds':rounds,'note':copy.deepcopy(NOTES.get(cid, STORY_NOTE if engine=='sequence' else GENERIC)),
                 'offscreen':copy.deepcopy(OFFSCREEN[group])}
            w.update(copy.deepcopy(rounds[0]))
            worksheets.append(w)
    return categories, worksheets


def write_json(path, data):
    payload = json.dumps(data, ensure_ascii=False, separators=(',',':')) + '\n'
    path.write_text(payload, encoding='utf-8')
    return hashlib.sha256(payload.encode()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', type=Path, default=Path(__file__).resolve().parent)
    p.add_argument('--skip-audit', action='store_true')
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    categories, worksheets = build()
    hashes = {name:write_json(args.out/name, data) for name,data in [
        ('expansion-categories.json',categories),('expansion-worksheets.json',worksheets)]}
    manifest = {'schema':'normalized Worksheet; root mirrors round 1; sort uses bins and exact pairs; memory uses canonical unique cards',
                'categoryCount':12,'worksheetCount':288,'roundCount':1152,'worksheetsPerCategory':24,'roundsPerWorksheet':4,
                'languages':['en','id','zh'],'engines':sorted({c['engine'] for c in categories}),
                'requiredAssets':sorted({c['asset'] for c in CARDS.values()} | {c['asset'] for c in categories}),
                'groupIds':['habits','kindness'],'sourceNotes':SOURCES,
                'contentRules':['Adult-supported ages 2–6','Three explicit steps per sequence story','No forced touch or obedience',
                                'No food completion pressure','No hygiene fear or shame','Helping is optional and supported',
                                'Story variants change actions and scenarios, not just option positions'],
                'sha256':hashes}
    write_json(args.out/'expansion-manifest.json',manifest)
    if not args.skip_audit:
        subprocess.run([sys.executable,str(Path(__file__).with_name('validate_habits.py')),'--out',str(args.out)],check=True)
    print(json.dumps({'categories':12,'worksheets':288,'rounds':1152,'out':str(args.out)}))


if __name__ == '__main__':
    main()
