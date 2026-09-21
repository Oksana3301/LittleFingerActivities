import type {CSSProperties} from 'react';
import type {Text} from '../data/types';
import atlases from '../data/art-atlases.json';
import externalArt from '../data/external-art.json';

export const animalAssets=['hen','duck','turtle','cat','rabbit','goat','squirrel','bird','lion','butterfly','snail','ladybug','bee','cow','horse','dog'];
export const objectAssets=['carrot','cucumber','tomato','apple','banana','leaf','flower','tree','seed','sprout','sun','moon','cloud','raindrop','star','rocket','planet','astronaut','bicycle','umbrella','train','boat','car','watering-can','trowel'];
export function Art({name,className='',style={}}:{name:string;className?:string;style?:CSSProperties}){
 const external=(externalArt as Record<string,{src:string}>)[name];
 if(external)return <span aria-hidden="true" data-art={name} className={'storybook-art external-art '+className} style={{backgroundImage:`url(${external.src})`,...style}}/>;
 const atlas=atlases.find(a=>a.assets.includes(name));
 if(!atlas)return <span className={'art-fallback '+className} aria-hidden="true">{name==='heart'?'♥':name==='fish'?'♧':name.slice(0,1).toUpperCase()}</span>;
 const n=atlas.size,index=atlas.assets.indexOf(name);
 // Saturn’s wide rings extend beyond its regular sprite cell.
 const crop:CSSProperties=name==='food-dumplings'?{backgroundSize:'400% 375%',backgroundPosition:'33.3333% 100%'}:name==='saturn'?{backgroundSize:'358.2857% 400%',backgroundPosition:'33.7389% 33.3333%'}:name==='uranus'?{clipPath:'inset(0 0 0 5%)'}:name==='robot'?{backgroundPosition:'0% 98.4%'}:name==='bolt'?{clipPath:'inset(0 0 3% 0)'}:name==='hand'?{backgroundPosition:'0% 98.4%'}:name==='head'?{backgroundPosition:'66.6667% 98.4%'}:['eye','nose'].includes(name)?{clipPath:'inset(0 0 3% 0)'}:{};
 return <span aria-hidden="true" data-art={name} className={'storybook-art '+className+(atlas.file.startsWith('adjective-')?' alpha-art':'')} style={{backgroundImage:`url(/assets/workbook/${atlas.file}.webp)`,backgroundSize:`${n*100}% ${n*100}%`,backgroundPosition:`${index%n/(n-1)*100}% ${Math.floor(index/n)/(n-1)*100}%`,...crop,...style}}/>;
}

export type Picture={crop?:{x:number;y:number;width:number;height:number};id:string;label:Text;asset?:string;shape?:string;color?:string;colorName?:Text;symbol?:string;value?:number;scale?:number;rotation?:number;silhouette?:boolean;dots?:number;width?:number;height?:number;position?:string;pairSymbol?:string;pairLabel?:Text;kind?:string;groupAsset?:string;measure?:string;direction?:string;showLabel?:boolean;ariaLabel?:Text};
export function pictureLabel(item:Picture,lang:'id'|'en',index=0){
 if(item.ariaLabel?.[lang])return item.ariaLabel[lang];
 const positions:Record<string,[string,string]>={'top-left':['kiri atas','top left'],'top-center':['tengah atas','top center'],'top-right':['kanan atas','top right'],'middle-left':['kiri tengah','middle left'],center:['tengah','center'],'middle-right':['kanan tengah','middle right'],'bottom-left':['kiri bawah','bottom left'],'bottom-center':['tengah bawah','bottom center'],'bottom-right':['kanan bawah','bottom right'],up:['atas','up'],down:['bawah','down'],left:['kiri','left'],right:['kanan','right'],'up-left':['kiri atas','up and left'],'up-right':['kanan atas','up and right'],'down-left':['kiri bawah','down and left'],'down-right':['kanan bawah','down and right']};
 if(item.kind==='quantity')return lang==='id'?`Kelompok berisi ${item.value||0} gambar`:`Group of ${item.value||0} pictures`;
 const color=item.colorName?.[lang];let label=item.label[lang];
 if(color)label=lang==='id'?`${label} ${color.toLowerCase()}`:`${color} ${label.toLowerCase()}`;
 const location=positions[item.position||item.direction||''];
 if(location)label+=' '+location[lang==='id'?0:1];
 if(item.kind==='measurement')label+=lang==='id'?` nomor ${index+1}`:` number ${index+1}`;
 return label;
}
export function pictureDescription(item:Picture,index=0):Text{return {id:pictureLabel(item,'id',index),en:pictureLabel(item,'en',index),zh:item.ariaLabel?.zh||(!item.colorName&&!item.position&&!item.direction&&!['quantity','measurement'].includes(item.kind||'')?item.label.zh:undefined),ar:item.ariaLabel?.ar||(!item.colorName&&!item.position&&!item.direction&&!['quantity','measurement'].includes(item.kind||'')?item.label.ar:undefined)}}
export function PictureArt({item,small=false}:{item:Picture;small?:boolean}){
 if(item.crop){const {x,y,width,height}=item.crop;return <span className={'picture-crop '+(small?'small':'')} style={{aspectRatio:`${width}/${height}`}}><span style={{position:'absolute',left:`${-x/width*100}%`,top:`${-y/height*100}%`,width:`${100/width}%`,height:`${100/height}%`}}><PictureArt item={{...item,crop:undefined}}/></span></span>}
 const pictureColor=item.silhouette?'#4d5948':item.color;
 const style={transform:`scale(${item.scale||1}) rotate(${item.rotation||0}deg)`};
 if(item.asset)return <Art name={item.asset} className={(small?'small ':'')+(item.silhouette?'silhouette':'')} style={style}/>;
 if(item.kind==='quantity')return <span className="picture-quantity" aria-hidden="true">{Array.from({length:item.value||0},(_,i)=>item.groupAsset?<Art key={i} name={item.groupAsset}/>:<i key={i}/> )}{item.value===0&&<span className="empty-quantity">∅</span>}</span>;
 if(item.kind==='measurement'&&item.measure!=='scale')return <svg className={'shape-art '+(small?'small':'')} viewBox="0 0 120 120" aria-hidden="true"><rect x={item.measure==='height'?48:8} y={item.measure==='height'?110-(item.value||.5)*88:item.measure==='strokeWidth'?60-(item.value||.5)*18:54} width={item.measure==='width'?(item.value||.5)*94:item.measure==='strokeWidth'?94:24} height={item.measure==='height'?(item.value||.5)*88:item.measure==='strokeWidth'?(item.value||.5)*36:12} fill={pictureColor||'#73955c'} rx="2"/></svg>;
 if(item.dots!==undefined)return <span className="dot-quantity" aria-hidden="true">{Array.from({length:item.dots},(_,i)=><i key={i} style={{background:pictureColor||'#789667'}}/>)}</span>;
 if(item.shape)return <svg className={'shape-art '+(small?'small':'')} viewBox="0 0 120 120" aria-hidden="true" style={style}><g fill={pictureColor||'#db9677'} stroke={pictureColor||'#db9677'} strokeWidth="2" strokeLinejoin="round">{item.shape==='hexagon'?<path d="M35 16H85L110 60 85 104H35L10 60Z"/>:item.shape==='pentagon'?<path d="M60 10 110 47 91 105H29L10 47Z"/>:item.shape==='arrow'?<path d="M60 10 104 55H76V108H44V55H16Z"/>:item.shape==='circle'?<circle cx="60" cy="60" r="40"/>:item.shape==='triangle'?<path d="M60 16 107 100H13Z"/>:item.shape==='star'?<path d="m60 9 14 32 35 3-27 24 8 35-30-18-30 18 8-35L11 44l35-3Z"/>:item.shape==='heart'?<path d="M60 103 20 65C-8 33 34 5 60 37 86 5 128 33 100 65Z"/>:item.shape==='oval'?<ellipse cx="60" cy="60" rx="46" ry="28"/>:item.shape==='diamond'?<path d="M60 9 108 60 60 111 12 60Z"/>:item.shape==='rectangle'?<rect x="12" y="32" width="96" height="56" rx="3"/>:item.shape==='line'?<path d="M14 60H106" strokeWidth="12"/>:<rect x="22" y="22" width="76" height="76" rx="3"/>}</g></svg>;
 const symbol=String(item.symbol??item.value??'?');
 return <span className={'letter-art '+(small?'small':'')+(symbol.length>1?' multi-symbol':'')} style={{color:pictureColor||'#647f52',...(symbol.length>1?{fontSize:Math.max(16,Math.min(small?32:54,(small?75:110)/symbol.length)),minWidth:0}:{}),...style}} aria-hidden="true">{item.symbol??item.value??'?'}</span>;
}
