'use client';
import {Art,pictureDescription} from './artwork';
import type {Worksheet,WorksheetState} from '../data/workbook';
import {textOf,type Lang,type Text} from '../data/types';

export default function WorldMapGame({a,state,onSelect,l,listen,translation,print=false}:{a:Worksheet;state:WorksheetState;onSelect:(id:string)=>void;l:Lang;listen?:(value:Text,key:string)=>React.ReactNode;translation?:{text:(value:Text)=>string;lang:string;dir:"ltr"|"rtl"};print?:boolean}){
 const places=a.map?.places||[],selected=state.selected||[];
 const t=(id:string,en:string)=>l==='id'?id:en;
 return <div className={'world-game '+(print?'world-print':'')}>
  <p className="world-map-hint">{t('Ketuk nomor di peta atau pilih benderanya.','Tap a number on the map or choose its flag.')}</p>
  <div className="world-map" dir="ltr" role="group" aria-label={t('Peta dunia dengan penanda negara','World map with country markers')}>
   <img src="/assets/geography/world.svg" alt="" draggable={false}/>
   {places.map((place,i)=>{const option=a.options.find(o=>o.id===place.option);if(!option)return null;return <button key={place.option} className={'world-pin '+(selected.includes(place.option)?'selected':'')} style={{left:`${(place.lng+180)/360*100}%`,top:`${(90-place.lat)/180*100}%`}} aria-label={`${i+1}. ${textOf(option.label,l)}`} aria-pressed={selected.includes(place.option)} disabled={print||state.complete} onClick={()=>onSelect(place.option)}>{i+1}</button>})}
  </div>
  <div className="world-country-choices">{places.map((place,i)=>{const option=a.options.find(o=>o.id===place.option);if(!option)return null;return <div className="world-country" key={place.option}><button className={'world-country-button '+(selected.includes(place.option)?'selected':'')} aria-label={textOf(option.label,l)} aria-pressed={selected.includes(place.option)} disabled={print||state.complete} onClick={()=>onSelect(place.option)}><span className="world-country-number">{i+1}</span><Art name={option.asset!}/><span>{textOf(option.label,l)}</span>{translation&&<span className="world-country-translation" lang={translation.lang} dir={translation.dir}>{translation.text(pictureDescription(option))}</span>}</button>{!print&&listen?.(pictureDescription(option),'country-'+place.option)}</div>})}</div>
  <p className="world-map-note">{t('Penanda menunjukkan perkiraan lokasi negara.','Markers show approximate country locations.')}</p>
 </div>;
}
