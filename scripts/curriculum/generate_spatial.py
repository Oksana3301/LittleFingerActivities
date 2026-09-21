#!/usr/bin/env python3
"""Deterministic, multilingual spatial worksheet authoring. Reads existing art only."""
import argparse,copy,itertools,json,math,random
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--site',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
OUT=args.output; (OUT/'bundles').mkdir(parents=True,exist_ok=True)
LABELS=json.loads((args.site/'app/data/art-labels.json').read_text()); ZH=json.loads((args.site/'public/audio/mandarin.json').read_text());AR=json.loads((args.site/'public/audio/arabic.json').read_text())
def T(i,e,z,a):return dict(id=i,en=e,zh=z,ar=a)
def label(asset):
 d=copy.deepcopy(LABELS[asset]);d.setdefault('zh',ZH.get(d['en']));d.setdefault('ar',AR.get(d['en']));assert all(d.get(x) for x in ['id','en','zh','ar']),asset;return d

def pic(asset,id=None,**kw):
 d={'kind':'asset','asset':asset,'label':label(asset),'showLabel':True}
 if id is not None:d['id']=id
 return {**d,**kw}
def shuffle(items,s):
 o=copy.deepcopy(items);random.Random(180926+s).shuffle(o);return o
VEH=['car','bus','bicycle','train','helicopter','airplane','sailboat','boat','submarine','tractor','fire-truck','police-car','ambulance','scooter','motorcycle','dump-truck','excavator','bulldozer','crane','rocket']
POOL=VEH+['cat','dog','rabbit','turtle','hen','cow','lion','goat','horse','squirrel','bird','duck','butterfly','bee','snail','ladybug','apple','banana','carrot','cucumber','tomato','tree','flower','leaf','watering-can','trowel','tent','backpack','flashlight','binoculars','umbrella','book','cup','chair','spoon','pencil','toothbrush','soap','towel','clock','wheel','gear','hammer','wrench']
for a in POOL:label(a)

def group_assets(pool,n,index):
 # Non-overlapping runs before wrapping; start advances by a coprime step.
 return [pool[(index*7+i*3)%len(pool)] for i in range(n)]

def base(kind,engine,instruction,options,answer=None,**kw):return {'activityKind':kind,'engine':engine,'instruction':instruction,'options':options,'answer':answer or [],**kw}
CROP_LABEL=T('Potongan gambar','Picture detail','图片局部','جزء من الصورة')

def cropped(n,pool=POOL):
 a=pool[n%len(pool)];distr=[x for x in group_assets(pool,8,n+5) if x!=a][:3]
 assert len(set(distr))==3
 opts=[pic(x,'o'+str(i)) for i,x in enumerate([a]+distr)]
 return base('picture-detail','identify',T('Lihat potongannya. Gambar utuh yang mana?','Look at the detail. Which is the whole picture?','看图片的局部。完整图片是哪一张？','انظر إلى جزء الصورة. أي صورة كاملة تطابقه؟'),shuffle(opts,n),['o0'],reference=pic(a,'detail',label=CROP_LABEL,showLabel=False,crop={'x':.2,'y':.2,'width':.6,'height':.6}))

def matching(n,pool=POOL,shadow=False):
 assets=group_assets(pool,2+(n//12)%2,n)
 left=[pic(a,'l'+str(i),pairId='r'+str(i)) for i,a in enumerate(assets)]
 right=[pic(a,'r'+str(i),silhouette=True,showLabel=False) if shadow else pic(a,'r'+str(i)) for i,a in enumerate(assets)]
 instruction=T('Pasangkan setiap kendaraan dengan bayangannya.','Match each vehicle with its shadow.','把每辆交通工具与它的影子配对。','صل كل وسيلة نقل بظلها.') if shadow and pool==VEH else T('Pasangkan setiap gambar dengan bayangannya.','Match each picture with its shadow.','把每张图片与它的影子配对。','صل كل صورة بظلها.') if shadow else T('Pasangkan gambar yang sama.','Match the identical pictures.','把相同的图片配成一对。','صل الصور المتطابقة.')
 return base('shadow-match' if shadow else 'match','pair',instruction,left,pairs=[{'left':x['id'],'right':x['pairId']} for x in left],rightOptions=shuffle(right,n+51))

def memory(n,pool=POOL):
 assets=group_assets(pool,2+n//12,n)
 return base('memory','memory',T('Balik kartu. Temukan pasangan gambar yang sama.','Turn over the cards. Find each identical picture pair.','翻开卡片，找出相同的图片对。','اقلب البطاقات واعثر على كل زوج من الصور المتطابقة.'),[pic(a,'m'+str(i)) for i,a in enumerate(assets)])

# Measured from the unchanged atlas cells: fraction of pixels below RGB 220.
# Missing tiles must contain at least 8% visible content.
PUZZLE_INK={'hen': [0.21157, 0.393038, 0.424155, 0.423506], 'duck': [0.18455, 0.175139, 0.369508, 0.503022], 'turtle': [0.291605, 0.158505, 0.362159, 0.567082], 'cat': [0.181468, 0.321473, 0.53844, 0.270883], 'rabbit': [0.21211, 0.306835, 0.477139, 0.479492], 'goat': [0.377178, 0.131145, 0.269108, 0.513895], 'squirrel': [0.423775, 0.40156, 0.458068, 0.619944], 'bird': [0.045035, 0.299567, 0.395107, 0.330237], 'lion': [0.329005, 0.776049, 0.490486, 0.508824], 'butterfly': [0.421844, 0.43112, 0.365099, 0.383707], 'snail': [0.232166, 0.179242, 0.569002, 0.419165], 'ladybug': [0.23375, 0.228197, 0.386547, 0.360988], 'bee': [0.306625, 0.347235, 0.299566, 0.251613], 'cow': [0.441736, 0.58972, 0.375919, 0.275265], 'horse': [0.367508, 0.594791, 0.356035, 0.273642], 'dog': [0.375269, 0.535559, 0.345775, 0.287395], 'carrot': [0.060595, 0.458222, 0.376952, 0.16416], 'cucumber': [0.023117, 0.340698, 0.456063, 0.286272], 'tomato': [0.183619, 0.194159, 0.5008, 0.483584], 'apple': [0.199987, 0.301841, 0.580317, 0.437824], 'banana': [0.0, 0.192889, 0.396635, 0.455232], 'leaf': [0.187705, 0.488952, 0.433206, 0.410624], 'flower': [0.229529, 0.23219, 0.28254, 0.22688], 'tree': [0.511048, 0.488, 0.510336, 0.483648], 'seed': [0.084656, 0.183683, 0.35619, 0.202752], 'sprout': [0.316201, 0.255619, 0.144063, 0.137664], 'sun': [0.272, 0.39424, 0.232317, 0.30144], 'moon': [0.30927, 0.20096, 0.346984, 0.347584], 'cloud': [0.20032, 0.258816, 0.364416, 0.408128], 'raindrop': [0.219746, 0.201088, 0.333079, 0.280512], 'star': [0.392571, 0.329152, 0.361841, 0.314304], 'rocket': [0.281557, 0.436952, 0.318603, 0.158656], 'planet': [0.415029, 0.520444, 0.339429, 0.195264], 'astronaut': [0.336254, 0.448254, 0.284096, 0.21888], 'bicycle': [0.232867, 0.278476, 0.349016, 0.273216], 'umbrella': [0.49326, 0.548571, 0.134603, 0.007744], 'train': [0.445389, 0.266413, 0.381143, 0.415872], 'boat': [0.304611, 0.318413, 0.357968, 0.342016], 'car': [0.484952, 0.485206, 0.27392, 0.274752], 'watering-can': [0.35897, 0.62527, 0.119238, 0.418368], 'trowel': [0.109473, 0.311683, 0.317968, 0.05984], 'mercury': [0.202199, 0.272303, 0.34472, 0.439774], 'venus': [0.280949, 0.285772, 0.465336, 0.456205], 'earth': [0.311, 0.279646, 0.506288, 0.475638], 'mars': [0.339121, 0.231287, 0.540468, 0.380543], 'jupiter': [0.390332, 0.526498, 0.350359, 0.454907], 'saturn': [0.282216, 0.547281, 0.433897, 0.292912], 'uranus': [0.384369, 0.363343, 0.359668, 0.327681], 'neptune': [0.442512, 0.344398, 0.4231, 0.321757], 'comet': [0.083374, 0.313898, 0.28845, 0.12467], 'telescope': [0.253411, 0.225012, 0.112037, 0.123697], 'satellite': [0.347058, 0.184713, 0.117549, 0.332022], 'microscope': [0.113221, 0.199249, 0.254777, 0.246136], 'magnet': [0.37466, 0.441113, 0.154205, 0.15526], 'ice-cube': [0.21064, 0.31624, 0.125102, 0.123859], 'rock': [0.497264, 0.399489, 0.203454, 0.218305], 'water-glass': [0.23717, 0.209623, 0.148606, 0.134083], 'mother': [0.347032, 0.413607, 0.633697, 0.487768], 'father': [0.426711, 0.354659, 0.528826, 0.517587], 'grandmother': [0.302915, 0.365248, 0.52511, 0.518682], 'grandfather': [0.360583, 0.339405, 0.58189, 0.550611], 'older-sibling': [0.405643, 0.351503, 0.362733, 0.371658], 'younger-sibling': [0.248562, 0.23967, 0.449045, 0.456408], 'baby': [0.227852, 0.313123, 0.401846, 0.256765], 'family': [0.465948, 0.430753, 0.876222, 0.728995], 'eye': [0.357627, 0.404989, 0.260335, 0.296604], 'ear': [0.297789, 0.279683, 0.270537, 0.131324], 'nose': [0.227482, 0.142822, 0.319819, 0.229015], 'mouth': [0.180916, 0.162584, 0.176924, 0.138302], 'hand': [0.422289, 0.443507, 0.186661, 0.181995], 'foot': [0.119141, 0.559049, 0.269517, 0.151325], 'head': [0.651846, 0.534991, 0.232852, 0.175707], 'shoulder': [0.507607, 0.662218, 0.424317, 0.34188], 'chair': [0.165321, 0.319648, 0.331454, 0.384721], 'table': [0.268373, 0.289424, 0.259881, 0.302], 'bed': [0.049404, 0.2977, 0.56153, 0.514341], 'lamp': [0.280336, 0.254169, 0.317579, 0.286989], 'clock': [0.34252, 0.443206, 0.37608, 0.488823], 'book': [0.340894, 0.344561, 0.396783, 0.495558], 'pencil': [0.034065, 0.247142, 0.306059, 0.048562], 'bag': [0.357341, 0.356688, 0.578441, 0.494138], 'scissors': [0.057243, 0.356116, 0.23007, 0.148444], 'ruler': [0.07306, 0.364446, 0.29773, 0.029778], 'spoon': [0.037434, 0.342234, 0.202433, 0.0], 'plate': [0.358117, 0.247469, 0.232058, 0.180656], 'cup': [0.512637, 0.533774, 0.226865, 0.16812], 'toothbrush': [0.106157, 0.231125, 0.16585, 0.0], 'soap': [0.457088, 0.431661, 0.170995, 0.161508], 'towel': [0.578076, 0.523956, 0.14954, 0.173841], 'bus': [0.121749, 0.255183, 0.362773, 0.442777], 'fire-truck': [0.144292, 0.25498, 0.450882, 0.402166], 'ambulance': [0.079944, 0.052375, 0.361955, 0.201225], 'police-car': [0.041462, 0.023003, 0.409104, 0.204674], 'tractor': [0.10579, 0.28642, 0.41308, 0.482007], 'excavator': [0.186678, 0.143925, 0.258493, 0.48221], 'bulldozer': [0.040064, 0.163237, 0.423649, 0.440505], 'crane': [0.210722, 0.054344, 0.347032, 0.396527], 'airplane': [0.073983, 0.095092, 0.107063, 0.147227], 'helicopter': [0.160092, 0.250694, 0.206149, 0.103371], 'ship': [0.060158, 0.148375, 0.314307, 0.300053], 'sailboat': [0.079944, 0.064919, 0.213274, 0.207797], 'motorcycle': [0.214491, 0.292507, 0.198466, 0.189622], 'scooter': [0.100849, 0.018175, 0.116977, 0.1097], 'dump-truck': [0.445166, 0.355471, 0.249224, 0.186539], 'submarine': [0.240456, 0.201185, 0.24289, 0.198264], 'hammer': [0.073877, 0.256846, 0.239563, 0.045357], 'wrench': [0.0, 0.188567, 0.207211, 0.095298], 'screwdriver': [0.0, 0.103331, 0.294055, 0.030062], 'pliers': [0.029048, 0.189785, 0.280376, 0.145077], 'saw': [0.005471, 0.232402, 0.233965, 0.265001], 'drill': [0.20895, 0.368365, 0.062919, 0.364315], 'gear': [0.217127, 0.211008, 0.294014, 0.258875], 'wheel': [0.313368, 0.229177, 0.435839, 0.319323], 'bolt': [0.01576, 0.334395, 0.172745, 0.09043], 'nut': [0.127959, 0.174465, 0.135595, 0.177776], 'spring': [0.183679, 0.165197, 0.173649, 0.147876], 'pulley': [0.388658, 0.264168, 0.161264, 0.166538], 'robot': [0.204876, 0.345369, 0.140736, 0.173678], 'traffic-cone': [0.117181, 0.237941, 0.185244, 0.252951], 'helmet': [0.367671, 0.325125, 0.244978, 0.128038], 'toolbox': [0.467078, 0.336119, 0.221672, 0.216723], 'football': [0.068197, 0.104954, 0.138707, 0.206621], 'basketball': [0.193818, 0.199278, 0.27511, 0.266907], 'badminton-racket': [0.038421, 0.14317, 0.088478, 0.112581], 'tennis-racket': [0.089983, 0.131202, 0.142562, 0.137206], 'kite': [0.135228, 0.267475, 0.047182, 0.121831], 'skateboard': [0.059131, 0.261432, 0.25984, 0.078299], 'tent': [0.198019, 0.203618, 0.274089, 0.259605], 'backpack': [0.31398, 0.210191, 0.368129, 0.30768], 'compass': [0.1565, 0.291483, 0.180413, 0.228123], 'binoculars': [0.263437, 0.291483, 0.1427, 0.23433], 'flashlight': [0.175583, 0.256492, 0.193573, 0.01424], 'building-blocks': [0.278377, 0.23326, 0.255142, 0.21725], 't-rex': [0.399732, 0.2678, 0.091079, 0.149905], 'triceratops': [0.481341, 0.272465, 0.16487, 0.232342], 'stegosaurus': [0.370366, 0.397339, 0.186551, 0.162928], 'fossil': [0.499655, 0.376242, 0.229827, 0.183415], 'habit-toothbrush': [0.0, 0.124184, 0.153353, 0.04414], 'habit-toothpaste': [0.098073, 0.203457, 0.088886, 0.164915], 'habit-clean-tooth': [0.023069, 0.033835, 0.041238, 0.055012], 'habit-food-tooth': [0.029819, 0.057933, 0.061017, 0.063248], 'habit-soap': [0.026621, 0.048628, 0.162562, 0.206134], 'habit-shower': [0.092538, 0.268782, 0.089376, 0.054242], 'habit-towel': [0.037722, 0.120978, 0.260575, 0.289991], 'habit-clean-shirt': [0.49359, 0.442675, 0.391375, 0.341718], 'habit-handwash': [0.105626, 0.335701, 0.46651, 0.165605], 'habit-tissue': [0.200074, 0.183488, 0.350808, 0.399408], 'habit-toilet': [0.038338, 0.163278, 0.120488, 0.19871], 'habit-flush': [0.307774, 0.329699, 0.285448, 0.265731], 'habit-plate': [0.334009, 0.586718, 0.213437, 0.266745], 'habit-cup': [0.200351, 0.167512, 0.111832, 0.091728], 'habit-bed': [0.609383, 0.394012, 0.196676, 0.312061], 'habit-toy-basket': [0.596941, 0.570043, 0.385452, 0.357905], 'habit-brushing': [0.301432, 0.683192, 0.642095, 0.680636], 'habit-bathing': [0.247836, 0.231287, 0.465621, 0.460343], 'habit-drying': [0.345011, 0.336363, 0.365058, 0.429105], 'habit-sleeping': [0.237819, 0.461601, 0.823644, 0.657633], 'habit-eating': [0.298791, 0.359301, 0.600957, 0.527202], 'habit-drinking': [0.323841, 0.424057, 0.417524, 0.325003], 'habit-tidying': [0.157668, 0.430385, 0.644537, 0.501805], 'habit-helping': [0.258452, 0.555365, 0.470283, 0.608909], 'habit-sharing': [0.4321, 0.375388, 0.512475, 0.496937], 'habit-waiting': [0.41342, 0.341254, 0.383268, 0.548339], 'habit-greeting': [0.414037, 0.389025, 0.34203, 0.431011], 'habit-thanking': [0.153764, 0.608239, 0.565013, 0.643109], 'habit-apologizing': [0.444197, 0.470851, 0.441762, 0.421518], 'habit-asking-help': [0.277397, 0.613128, 0.475135, 0.676904], 'habit-gentle': [0.557611, 0.233924, 0.559244, 0.500264], 'habit-cover-cough': [0.313765, 0.443953, 0.249178, 0.611343], 'adj-hot-cup': [0.788024, 0.689521, 0.632602, 0.706804], 'adj-cold-cup': [0.889842, 0.85399, 0.532664, 0.669479], 'adj-soft-pillow': [0.590683, 0.618889, 0.543361, 0.656173], 'adj-hard-rock': [0.954684, 0.989939, 0.841211, 0.861779], 'adj-wet-shirt': [0.914789, 0.950923, 0.936022, 0.884742], 'adj-dry-shirt': [0.932528, 0.947901, 0.989833, 0.984097], 'adj-open-box': [0.967291, 0.988404, 0.882941, 0.789038], 'adj-closed-box': [0.979014, 0.968847, 0.752079, 0.754635], 'adj-full-basket': [0.924914, 0.977095, 0.428009, 0.43588], 'adj-empty-basket': [0.985659, 0.986894, 0.60828, 0.715364], 'adj-heavy-box': [0.925542, 0.920505, 0.764903, 0.745304], 'adj-light-feather': [0.578475, 0.513106, 0.53848, 0.633778], 'adj-bright-lamp': [0.428861, 0.430849, 0.441843, 0.460749], 'adj-dim-lamp': [0.51527, 0.94304, 0.647844, 0.804252], 'adj-fresh-flower': [0.912094, 0.96369, 0.807733, 0.836058], 'adj-wilted-flower': [0.936103, 0.988032, 0.83407, 0.849446], 'adj-fast-car': [0.94657, 0.987586, 0.771512, 0.841413], 'adj-slow-car': [0.99657, 0.988884, 0.74163, 0.80129], 'adj-loud-drum': [0.895231, 0.923323, 0.782215, 0.802751], 'adj-quiet-book': [0.983448, 0.980324, 0.814272, 0.836383], 'adj-tidy-shelf': [0.912216, 0.911073, 0.850947, 0.872449], 'adj-messy-shelf': [0.919173, 0.891311, 0.864446, 0.860441], 'adj-smooth-ball': [0.905901, 0.971297, 0.713866, 0.769849], 'adj-rough-stone': [0.951576, 0.974277, 0.815976, 0.63536], 'adj-open-book': [0.727748, 0.553854, 0.787821, 0.661325], 'adj-closed-book': [0.916338, 0.951699, 0.842193, 0.790742], 'adj-full-cup': [0.783284, 0.830679, 0.835579, 0.753093], 'adj-empty-cup': [0.572554, 0.547852, 0.751471, 0.6453], 'adj-clean-shoe': [0.89314, 0.922593, 0.848473, 0.860359], 'adj-muddy-shoe': [0.893639, 0.942229, 0.908215, 0.869285], 'adj-neat-boy': [0.989874, 0.993144, 0.896742, 0.911355], 'adj-neat-girl': [0.995781, 0.998905, 0.89245, 0.921254]}
PUZZLE_USED=set()

def puzzle(n,pool=POOL):
 # First four worksheets (16 tasks) need one tile; then two, then three.
 count=1+min(2,n//16)
 for offset in range(len(pool)):
  asset=pool[(n+offset)%len(pool)]
  good=[tile for tile,ink in enumerate(PUZZLE_INK[asset]) if ink>=.08]
  choices=[tiles for tiles in itertools.combinations(good,count) if (asset,tiles) not in PUZZLE_USED]
  if choices:
   missing=choices[n%len(choices)];PUZZLE_USED.add((asset,missing));break
 else:raise ValueError('No meaningful, distinct puzzle tiles available for '+str(n))
 letters=shuffle(list('ABCD'),n)
 options=[]
 for i,tile in enumerate(missing):
  letter=letters[i]
  options.append(pic(asset,'tile-'+str(tile),label=T('Potongan '+letter,'Piece '+letter,'拼图片 '+letter,'قطعة '+letter),showLabel=False,crop={'x':(tile%2)/2,'y':(tile//2)/2,'width':.5,'height':.5}))
 return base('complete-picture','puzzle',T('Lengkapi gambar. Pilih potongan, lalu sentuh tempat kosong yang cocok.','Complete the picture. Choose a piece, then tap its matching gap.','补全图片。选一块拼图，再点它对应的空位。','أكمل الصورة. اختر قطعة ثم المس الفراغ المناسب لها.'),shuffle(options,n+92),puzzle={'image':pic(asset,'whole'),'columns':2,'rows':2,'missing':list(missing)},pairs=[{'left':'tile-'+str(x),'right':'slot-'+str(x)} for x in missing])

ODD_CONFIG=[
(['helicopter','airplane','bicycle'],'bicycle',T('tidak dapat terbang','cannot fly','不能飞行','لا تستطيع الطيران')),
(['helicopter','airplane','car'],'car',T('tidak dapat terbang','cannot fly','不能飞行','لا تستطيع الطيران')),
(['helicopter','airplane','bus'],'bus',T('tidak dapat terbang','cannot fly','不能飞行','لا تستطيع الطيران')),
(['helicopter','airplane','train'],'train',T('tidak dapat terbang','cannot fly','不能飞行','لا تستطيع الطيران')),
(['boat','sailboat','car'],'car',T('bukan kendaraan air','is not a water vehicle','不是水上交通工具','ليست وسيلة نقل مائية')),
(['submarine','sailboat','bus'],'bus',T('bukan kendaraan air','is not a water vehicle','不是水上交通工具','ليست وسيلة نقل مائية')),
(['submarine','boat','bicycle'],'bicycle',T('bukan kendaraan air','is not a water vehicle','不是水上交通工具','ليست وسيلة نقل مائية')),
(['boat','sailboat','tractor'],'tractor',T('bukan kendaraan air','is not a water vehicle','不是水上交通工具','ليست وسيلة نقل مائية')),
(['car','bus','sailboat'],'sailboat',T('tidak beroda','has no wheels','没有车轮','ليست لها عجلات')),
(['bicycle','motorcycle','boat'],'boat',T('tidak beroda','has no wheels','没有车轮','ليست لها عجلات')),
(['tractor','dump-truck','submarine'],'submarine',T('tidak beroda','has no wheels','没有车轮','ليست لها عجلات')),
(['scooter','car','sailboat'],'sailboat',T('tidak beroda','has no wheels','没有车轮','ليست لها عجلات')),
(['car','bicycle','tree'],'tree',T('bukan kendaraan','is not a vehicle','不是交通工具','ليست وسيلة نقل')),
(['train','airplane','flower'],'flower',T('bukan kendaraan','is not a vehicle','不是交通工具','ليست وسيلة نقل')),
(['bus','boat','apple'],'apple',T('bukan kendaraan','is not a vehicle','不是交通工具','ليست وسيلة نقل')),
(['helicopter','tractor','book'],'book',T('bukan kendaraan','is not a vehicle','不是交通工具','ليست وسيلة نقل'))]

def odd(n):
 assets,target,rule=ODD_CONFIG[n]; options=[pic(a,'o'+str(i)) for i,a in enumerate(assets)]; answer=options[assets.index(target)]['id']
 return base('odd-one-out','identify',T('Pilih satu yang '+rule['id']+'.','Choose the one that '+rule['en']+'.','选出'+rule['zh']+'的那一个。','اختر الصورة التي '+rule['ar']+'.'),shuffle(options,n),[answer])

def many(n):
 wheeled=['car','bus','bicycle','train','tractor','fire-truck','police-car','ambulance','scooter','motorcycle','dump-truck']; triples=list(itertools.combinations(wheeled,3)); assets=list(triples[n*5%len(triples)])+[ ['sailboat','boat','submarine'][n%3] ];opts=[pic(a,'o'+str(i)) for i,a in enumerate(assets)]
 return base('choose-many','identify',T('Pilih semua kendaraan beroda. Ada tiga gambar yang cocok.','Choose every vehicle with wheels. Three pictures match.','选出所有有轮子的交通工具。一共有三张。','اختر كل وسائل النقل ذات العجلات. هناك ثلاث صور مطابقة.'),shuffle(opts,n),['o0','o1','o2'])

ROUTES=[[(14,78),(35,72),(56,52),(80,25)],[(14,78),(15,48),(50,50),(80,25)],[(14,78),(40,82),(68,70),(67,43),(80,19)],[(14,78),(33,55),(30,26),(58,20),(82,27)]]
DEST=['tent','tree','book','flower','backpack','umbrella','chair','watering-can','cup','football','building-blocks','sun']

def route(n,transport=False):
 starts=VEH[:4]+['scooter','tractor','police-car','ambulance'] if transport else ['car','bus','bicycle','train','rabbit','turtle','dog','cat','horse','snail','ladybug','squirrel']
 start=starts[n%len(starts)];end=DEST[(n//len(starts)+n*3)%len(DEST)];s=label(start);e=label(end);geometry=ROUTES[n%4]
 points=[{'x':x,'y':y,'label':T('Langkah '+str(i+1),'Step '+str(i+1),'第'+str(i+1)+'步','الخطوة '+str(i+1))} for i,(x,y) in enumerate(geometry)]
 # One distractor, far from all required points and endpoint illustration anchors.
 candidates=[(18,20),(82,82),(46,22),(82,50),(48,87)]
 decoy=next(q for q in candidates if all(math.dist(q,p)>24 for p in geometry) and math.dist(q,(10,80))>25 and math.dist(q,(90,20))>25)
 return base('follow-route','route',T('Ikuti jalur dari '+s['id'].lower()+' ke '+e['id'].lower()+'. Sentuh titiknya secara berurutan.','Follow the route from '+s['en'].lower()+' to '+e['en'].lower()+'. Tap the points in order.','沿着路线从'+s['zh']+'到'+e['zh']+'。按顺序点圆点。','اتبع المسار من '+s['ar']+' إلى '+e['ar']+'. المس النقاط بالترتيب.'),[],['step-'+str(i) for i in range(len(points))],route={'start':pic(start,'start'),'end':pic(end,'end'),'points':points,'decoys':[{'x':decoy[0],'y':decoy[1],'label':T('Titik di luar jalur','Point outside the route','路线外的圆点','نقطة خارج المسار')} ]})


def cell_labels(cols,rows):
 out=[]
 for r in range(rows):
  for c in range(cols):
   rv=(['atas','bawah'],['top','bottom'],['上','下'],['العلوي','السفلي']) if rows==2 else (['atas','tengah','bawah'],['top','middle','bottom'],['上','中','下'],['العلوي','الأوسط','السفلي'])
   cv=(['kiri','kanan'],['left','right'],['左','右'],['الأيسر','الأيمن']) if cols==2 else (['kiri','tengah','kanan'],['left','middle','right'],['左','中','右'],['الأيسر','الأوسط','الأيمن'])
   out.append(T('Baris '+rv[0][r]+', kolom '+cv[0][c],rv[1][r].title()+' row, '+cv[1][c]+' column',rv[2][r]+'排'+cv[2][c]+'列','الصف '+rv[3][r]+'، العمود '+cv[3][c]))
 return out

def placement(n):
 cols=2 if n<16 else 3;rows=2 if n<32 else 3;count=2+min(2,n//16);assets=group_assets(POOL,count,n);cells=shuffle(list(range(cols*rows)),n)[:count];options=[pic(a,'o'+str(i)) for i,a in enumerate(assets)]
 return base('copy-layout','placement',T('Lihat contoh. Letakkan setiap gambar di posisi yang sama pada kotak kosong.','Look at the example. Place each picture in the same position on the empty grid.','看示范，把每张图片放在空白方格中相同的位置。','انظر إلى المثال. ضع كل صورة في الموضع نفسه على الشبكة الفارغة.'),shuffle(options,n+106),placement={'columns':cols,'rows':rows,'example':[{'option':o['id'],'cell':cells[i]} for i,o in enumerate(options)],'cells':cell_labels(cols,rows)},pairs=[{'left':o['id'],'right':'cell-'+str(cells[i])} for i,o in enumerate(options)])


def sequence(n,pool=POOL):
 assets=group_assets(pool,3,n);words={lang:' → '.join(label(a)[lang] for a in assets) for lang in ['id','en','zh','ar']};opts=[pic(a,'o'+str(i)) for i,a in enumerate(assets)]
 return base('sequence','sequence',T('Susun urutan gambar ini: '+words['id']+'.','Arrange the pictures in this order: '+words['en']+'.','按这个顺序排列图片：'+words['zh']+'。','رتب الصور بهذا التسلسل: '+words['ar']+'.'),shuffle(opts,n),['o0','o1','o2'])


def pattern(n):
 a,b,c=group_assets(POOL,3,n); pattern=[a,b,a,b,a,None] if n%3==0 else [a,a,b,a,a,None] if n%3==1 else [a,b,b,a,b,None]
 opts=[pic(v,'o'+str(i)) for i,v in enumerate([a,b,c])]
 return base('pattern','pattern',T('Lihat gambar dari awal. Pilih gambar yang melengkapi pola.','Look from the start. Choose the picture that completes the pattern.','从头观察，选出补全规律的图片。','انظر من البداية. اختر الصورة التي تكمل النمط.'),shuffle(opts,n),['o1'],patternItems=[pic(v) if v else None for v in pattern])


def trace(n):
 names=[T('lurus','straight','直线','مستقيم'),T('melengkung','curved','曲线','منحن'),T('zig-zag','zigzag','折线','متعرج'),T('berputar','looping','环线','دائري')];d=['M 40 150 L 360 150','M 40 220 C 120 220 115 80 200 80 S 285 220 360 80','M 40 220 L 115 80 L 195 220 L 275 80 L 360 160','M 40 230 C 40 60 240 25 280 130 C 325 240 105 270 120 140 C 145 55 265 50 360 70'][n%4]
 asset=VEH[n%len(VEH)];a=label(asset);name=names[n%4];offset=(n//4)*6
 # Each route has a genuinely different guide position plus a different vehicle.
 if offset:d=d.replace('40 ',str(40+offset)+' ',1)
 return base('trace','trace',T('Ajak '+a['id'].lower()+' mengikuti jalur '+name['id']+'. Telusuri garis dengan jari.','Invite the '+a['en'].lower()+' along the '+name['en']+' route. Trace the line with your finger.','让'+a['zh']+'沿着'+name['zh']+'前进。用手指描线。','ساعد '+a['ar']+' على اتباع المسار '+name['ar']+'. تتبع الخط بإصبعك.'),[],canvas={'viewBox':[0,0,400,300],'guide':[{'kind':'path','d':d,'fill':'none','stroke':'#94A7C5','strokeWidth':7},{'kind':'asset','asset':asset,'x':5,'y':230,'width':50,'height':50}]},completion={'mode':'self-check','goals':[T('Aku sudah mencoba mengikuti jalur.','I tried following the route.','我试着沿路线描线了。','حاولت تتبع المسار.')]})

TITLES={
'shadow-match':T('Pasangkan bayangan','Match the shadows','影子配对','مطابقة الظلال'),
'odd-one-out':T('Mana yang berbeda?','Which is different?','哪一个不同？','أيها مختلف؟'),
'choose-many':T('Pilih semua yang cocok','Choose every match','选出所有符合的图片','اختر كل الصور المطابقة'),
'picture-detail':T('Tebak dari potongan','Guess from a detail','看局部猜图片','خمن من جزء الصورة'),
'complete-picture':T('Lengkapi gambar','Complete the picture','补全图片','أكمل الصورة'),
'follow-route':T('Ikuti jalurnya','Follow the route','沿路线走','اتبع المسار'),
'match':T('Pasangkan gambar','Match the pictures','图片配对','مطابقة الصور'),
'memory':T('Ingat pasangan gambar','Remember the picture pairs','记住图片对子','تذكر أزواج الصور'),
'copy-layout':T('Tiru susunannya','Copy the layout','照样摆放','انسخ ترتيب الصور'),
'sequence':T('Susun urutan gambar','Arrange the picture order','排列图片顺序','رتب الصور'),
'pattern':T('Lanjutkan pola gambar','Continue the picture pattern','继续图片规律','أكمل نمط الصور'),
'trace':T('Telusuri jalur','Trace the path','描绘路线','تتبع الطريق')}
CATEGORIES=[
('transport-play','vehicles','bus',T('Transportasi: Banyak Cara Bermain','Transport: Many Ways to Play','交通工具：多种玩法','المواصلات: طرق لعب متنوعة'),T('Bayangan, pengecualian, pilih semua, potongan gambar, puzzle, dan jalur kendaraan.','Vehicle shadows, exceptions, multiple matches, picture details, puzzles, and routes.','玩交通工具影子配对、找不同、多选、局部猜图、拼图和路线。','ظلال وسائل النقل، والمختلف، والاختيار المتعدد، وأجزاء الصور، والألغاز، والمسارات.')),
('picture-details','visual-spatial','binoculars',T('Detektif Detail Gambar','Picture Detail Detectives','图片细节小侦探','محققو تفاصيل الصور'),T('Kenali gambar dari bagian kecil, bayangan, pasangan, dan permainan ingatan.','Recognize pictures from details, shadows, matching, and memory games.','通过局部、影子、配对和记忆游戏认识图片。','تعرف إلى الصور من التفاصيل والظلال والمطابقة وألعاب الذاكرة.')),
('picture-puzzles','visual-spatial','building-blocks',T('Puzzle Bagian dan Utuh','Parts and Whole Puzzles','部分与整体拼图','ألغاز الأجزاء والصورة الكاملة'),T('Isi bagian yang hilang dan hubungkan potongan dengan gambar utuh.','Fill missing parts and connect picture details with the whole.','填上缺少的部分，把局部与完整图片联系起来。','أكمل الأجزاء الناقصة واربط تفاصيل الصورة بالصورة الكاملة.')),
('spatial-layouts','visual-spatial','compass',T('Posisi dan Susunan','Positions and Layouts','位置与排列','المواضع وترتيب الصور'),T('Tiru posisi pada kotak, pasangkan, urutkan, dan lanjutkan pola.','Copy positions on a grid, match, order, and continue patterns.','模仿方格中的位置，练习配对、排序和规律。','انسخ المواضع على الشبكة وطابق الصور ورتبها وأكمل الأنماط.')),
('route-adventures','visual-spatial','tent',T('Petualangan Jalur','Route Adventures','路线小冒险','مغامرات المسارات'),T('Ikuti titik berurutan, telusuri garis, dan susun gambar perjalanan.','Follow points in order, trace paths, and arrange travel pictures.','按顺序点圆点，描路线，排列旅途图片。','اتبع النقاط بالترتيب وتتبع المسارات ورتب صور الرحلة.'))]

PLANS={
 'transport-play':[(lambda n:matching(n,VEH,True),4),(odd,4),(many,4),(lambda n:cropped(n,['train']+[a for a in VEH if a!='train']),4),(lambda n:puzzle(n,['bus','train','car','tractor','fire-truck','dump-truck','bicycle','helicopter','airplane','police-car','ambulance','scooter','motorcycle','submarine','boat','sailboat']),4),(lambda n:route(n,True),4)],
 'picture-details':[(cropped,6),(lambda n:matching(n+16,POOL,True),6),(lambda n:matching(n+40),6),(memory,6)],
 'picture-puzzles':[(puzzle,12),(lambda n:cropped(n+24),4),(lambda n:matching(n+64,POOL,True),4),(lambda n:matching(n+80),4)],
 'spatial-layouts':[(placement,12),(lambda n:matching(n+96),4),(sequence,4),(pattern,4)],
 'route-adventures':[(route,12),(trace,4),(lambda n:sequence(n+20,VEH),4),(lambda n:matching(n+112),4)]}

categories=[];manifest={'revision':'spatial-1','categoryCount':5,'worksheetCount':120,'roundCount':480,'categories':[],'rules':['All authored text includes id/en/zh/ar.','Transport wheel selection includes bicycles.','Shadow pairing uses identical image asset IDs.','Crop references use generic labels to avoid spoken answer spoilers.','Puzzles use exact normalized tiles from the same image.','Route points are ordered and separated by at least 18 normalized units.']}
allrecords=[]
for cid,group,asset,title,description in CATEGORIES:
 records=[]
 for maker,count in PLANS[cid]:
  for j in range(count):
   rounds=[maker(j*4+r) for r in range(4)];v=len(records)+1
   record={'id':f'{cid}-{v:02}','category':cid,'title':TITLES[rounds[0]['activityKind']],'variant':v,'difficulty':min(3,1+j//4),'age':3,'ageRange':[3,6],'revision':'spatial-1',**copy.deepcopy(rounds[0]),'rounds':rounds}
   records.append(record)
 assert len(records)==24
 kinds=sorted({x['activityKind'] for x in records});engines=sorted({x['engine'] for x in records});assert len(kinds)>=4 and len(engines)>=3
 category={'id':cid,'group':group,'asset':asset,'title':title,'description':description,'engine':records[0]['engine'],'age':3,'ageRange':[3,6],'worksheetCount':24,'activityKinds':kinds}
 categories.append(category);manifest['categories'].append({'id':cid,'worksheets':24,'rounds':96,'activityKinds':kinds,'engines':engines});allrecords+=records
 (OUT/'bundles'/f'{cid}.json').write_text(json.dumps(records,ensure_ascii=False,separators=(',',':'))+'\n')

def texts(node):
 if isinstance(node,dict):
  if 'id' in node and 'en' in node:
   assert all(isinstance(node.get(k),str) and node[k] for k in ['id','en','zh','ar']),node
  for v in node.values():texts(v)
 elif isinstance(node,list):
  for v in node:texts(v)
texts(allrecords);texts(categories)
# Each task has its own actual content; worksheet comparison ignores round order.
def normalize(r):
 d=copy.deepcopy(r)
 # Presentation shuffling is not counted as task variation.
 for key in ['options','rightOptions','pairs']:
  if key in d:d[key]=sorted(d[key],key=lambda x:json.dumps(x,sort_keys=True))
 return json.dumps(d,ensure_ascii=False,sort_keys=True)
seen={};dups=[]
for w in allrecords:
 hashes=[normalize(r) for r in w['rounds']];assert len(set(hashes))==4,w['id'];h=(w['category'],tuple(sorted(hashes)))
 if h in seen:dups.append([seen[h],w['id']])
 seen[h]=w['id']
manifest['duplicateWorksheetTaskSets']=dups;assert not dups,dups
manifest['minimumMissingTileInkFraction']=min(PUZZLE_INK[r['puzzle']['image']['asset']][tile] for w in allrecords for r in w['rounds'] if r['engine']=='puzzle' for tile in r['puzzle']['missing'])
for w in allrecords:
 for r in w['rounds']:
  if r['engine']=='route':
   points=r['route']['points'];assert all(math.dist((a['x'],a['y']),(b['x'],b['y']))>=18 for a,b in itertools.combinations(points,2))
(OUT/'categories.json').write_text(json.dumps(categories,ensure_ascii=False,separators=(',',':'))+'\n');(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps(manifest,ensure_ascii=False,indent=2))
