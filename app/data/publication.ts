import catalogue from '../../public/specs/catalogue-common.json';
export function publicationEligible(id:string):boolean{
 const a=catalogue.find(a=>a.id===id);if(!a)return false;
 const {delivery:d,review:r,safety:s}=a;
 return d.publication==='published'&&d.implementation==='working'&&d.tests==='passed'&&d.assets==='ready'&&d.rights==='cleared'&&s.reviewStatus==='approved'&&r.editorialStatus==='approved'&&!!r.editorialReviewer&&!!r.editorialReviewedAt&&(a.contentType!=='quran'||(r.religiousStatus==='approved'&&!!r.religiousReviewer&&!!r.religiousReviewedAt));
}
export const releaseCounts={authored:catalogue.length,implemented:catalogue.filter(a=>a.delivery.implementation==='working').length,tested:catalogue.filter(a=>a.delivery.tests==='passed').length,approved:catalogue.filter(a=>a.review.editorialStatus==='approved').length,published:catalogue.filter(a=>publicationEligible(a.id)).length};
