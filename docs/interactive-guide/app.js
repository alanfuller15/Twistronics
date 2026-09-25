'use strict';
(() => {
const D = window.TWISTRONICS_DATA;
const $ = id => document.getElementById(id);
const NS = 'http://www.w3.org/2000/svg';
const colors = ['#77e3ed','#ffd18b','#c1a6ff','#f198b5','#92d7a7','#e8e1a1'];
let active = 'layers', timer = null, selected = D.points.reduce((a,b)=>a.upper<b.upper?a:b);
const el = (name, attrs={}, text) => { const n=document.createElementNS(NS,name); for(const [k,v] of Object.entries(attrs)) n.setAttribute(k,v); if(text!==undefined)n.textContent=text; return n; };
function add(svg,name,attrs,text){const n=el(name,attrs,text);svg.appendChild(n);return n;}
function stop(){clearInterval(timer);timer=null;$('play-nodes').textContent='Play saved states';}
function chapter(id,focus=false){
  if(!['layers','momentum','nodes','evidence'].includes(id))id='layers';
  stop();active=id;document.querySelectorAll('.lesson').forEach(x=>x.hidden=x.id!==id);
  document.querySelectorAll('[data-tab]').forEach(x=>{if(x.dataset.tab===id)x.setAttribute('aria-current','page');else x.removeAttribute('aria-current');});
  history.replaceState(null,'','#'+id);
  if(id==='layers')drawMoire();if(id==='momentum')drawMap();if(id==='nodes')drawNodes();
  if(focus)$('lesson').focus({preventScroll:true});
}
document.querySelectorAll('[data-tab]').forEach(b=>b.addEventListener('click',()=>chapter(b.dataset.tab,true)));
document.querySelectorAll('[data-next]').forEach(b=>b.addEventListener('click',()=>{chapter(b.dataset.next,true);$('lesson').scrollIntoView({behavior:'auto',block:'start'});}));
window.addEventListener('hashchange',()=>chapter(location.hash.slice(1)));
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop();});

// Ideal geometry only: triangular Bravais reference sites, two atoms per site.
function drawMoire(){
  const canvas=$('moire-canvas'), box=canvas.getBoundingClientRect();if(!box.width)return;
  const dpr=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(box.width*dpr);canvas.height=Math.round(box.height*dpr);
  const c=canvas.getContext('2d');c.scale(dpr,dpr);const w=box.width,h=box.height;
  const theta=+$('angle').value,rad=theta*Math.PI/180,a=.246,L=a/(2*Math.sin(rad/2));
  const field=+$('real-zoom').value,scale=w/field;
  $('angle-value').textContent=theta.toFixed(2)+'°';
  $('moire-length').innerHTML=L.toFixed(2)+' <small>nm</small>';
  $('moire-ratio').textContent=(L/a).toFixed(1)+' × the atomic lattice spacing';
  $('scale-analogy').textContent=`If a were drawn as 1 mm, one moiré repeat would be ${(L/a).toFixed(1)} mm. A smaller twist makes L larger.`;
  $('real-scale').textContent=field+' nm across · equal x/y length scale';
  document.querySelectorAll('[data-angle]').forEach(b=>b.classList.toggle('active',+b.dataset.angle===theta));
  c.fillStyle='#08141d';c.fillRect(0,0,w,h);
  const extent=Math.hypot(w,h)/scale/2+a, n=Math.ceil(extent/(a*Math.sqrt(3)/2));
  for(const [angle,color] of [[-rad/2,'#77e3ed'],[rad/2,'#ffd18b']]){
    const cs=Math.cos(angle),sn=Math.sin(angle);c.fillStyle=color;c.globalAlpha=field===3?.9:.7;
    for(let j=-n;j<=n;j++){
      const y=j*a*Math.sqrt(3)/2;
      const imin=Math.floor(-extent/a-j/2),imax=Math.ceil(extent/a-j/2);
      for(let i=imin;i<=imax;i++){
        const x=a*(i+j/2),px=w/2+scale*(cs*x-sn*y),py=h/2-scale*(sn*x+cs*y);
        if(px<0||px>w||py<0||py>h)continue;
        const radius=field===3?2.4:field===12?1.25:.8;
        c.beginPath();c.arc(px,py,radius,0,Math.PI*2);c.fill();
      }
    }
  }
  c.globalAlpha=1;
  if($('show-cell').checked){
    // Real-space cell dual to the difference of symmetrically rotated reciprocal bases.
    const v1=[0,L],v2=[-Math.sqrt(3)*L/2,L/2],o=[-(v1[0]+v2[0])/2,-(v1[1]+v2[1])/2];
    const pts=[o,[o[0]+v1[0],o[1]+v1[1]],[o[0]+v1[0]+v2[0],o[1]+v1[1]+v2[1]],[o[0]+v2[0],o[1]+v2[1]]];
    c.beginPath();pts.forEach((p,i)=>c[i?'lineTo':'moveTo'](w/2+p[0]*scale,h/2-p[1]*scale));c.closePath();c.fillStyle='#77e3ed0b';c.fill();c.strokeStyle='#d3f8fc';c.lineWidth=1.7;c.stroke();
    c.fillStyle='#e7f6f9';c.font='13px ui-monospace, monospace';c.fillText(1.5*L*scale<h-30?'One moiré cell · edges L':'Moiré cell extends beyond this view',22,27);
  }
  // Fixed units, responsive pixel conversion. Both spatial axes share one scale.
  const bar=field===40?5:field===12?2:.5,x=26,y=h-30;
  c.fillStyle='#08141de8';c.fillRect(14,y-28,Math.max(bar*scale+30,132),46);
  c.strokeStyle='#edf5f8';c.lineWidth=2;c.beginPath();c.moveTo(x,y);c.lineTo(x+bar*scale,y);c.moveTo(x,y-4);c.lineTo(x,y+4);c.moveTo(x+bar*scale,y-4);c.lineTo(x+bar*scale,y+4);c.stroke();
  c.fillStyle='#edf5f8';c.font='13px ui-monospace, monospace';c.fillText(bar+' nm',x,y-11);
}
['angle','real-zoom','show-cell'].forEach(id=>$(id).addEventListener('input',drawMoire));
document.querySelectorAll('[data-angle]').forEach(b=>b.addEventListener('click',()=>{$('angle').value=b.dataset.angle;drawMoire();}));
$('layer-reset').addEventListener('click',()=>{$('angle').value='1.05';$('real-zoom').value='40';$('show-cell').checked=true;drawMoire();});
new ResizeObserver(()=>{if(active==='layers')drawMoire();}).observe($('moire-canvas'));

function palette(v){
  const min=.003089965450713,max=.385512008303379;
  let t=$('color-scale').value==='log'?(Math.log(v)-Math.log(min))/(Math.log(max)-Math.log(min)):(v-min)/(max-min);
  t=Math.max(0,Math.min(1,t));const cs=[[255,209,139],[119,227,237],[143,152,232]],i=t<.5?0:1,f=t<.5?t*2:(t-.5)*2;
  return `rgb(${cs[i].map((a,k)=>Math.round(a+(cs[i+1][k]-a)*f)).join(',')})`;
}
function batchPoints(){return D.points.filter(p=>$('batch').value==='all'||p.batch===$('batch').value);}
function inView(p){const mode=$('map-view').value;return mode!=='refined'||(p.u>=.25&&p.u<=.75&&p.v>=.5&&p.v<=1);}
function visiblePoints(){return batchPoints().filter(inView);}
function choose(p){selected=p;drawMap();}
function plotAxes(svg,bounds,labels){
  const compact=window.innerWidth<=720;
  const [xmin,xmax,ymin,ymax]=bounds, left=94,top=compact?20:30,size=compact?280:458;
  svg.setAttribute('viewBox',compact?'0 0 420 432':'0 0 720 560');
  const X=v=>left+(v-xmin)/(xmax-xmin)*size,Y=v=>top+size-(v-ymin)/(ymax-ymin)*size;
  add(svg,'rect',{x:left,y:top,width:size,height:size,fill:'#0b1b27',stroke:'#344b5a'});
  for(let i=0;i<=4;i++){
    const x=xmin+(xmax-xmin)*i/4,y=ymin+(ymax-ymin)*i/4;
    add(svg,'line',{x1:X(x),x2:X(x),y1:top,y2:top+size,stroke:'#263b48','stroke-width':.8});
    add(svg,'line',{x1:left,x2:left+size,y1:Y(y),y2:Y(y),stroke:'#263b48','stroke-width':.8});
    const fmt=v=>Math.abs(v)<1e-10?'0':v.toFixed(3).replace(/0+$/,'').replace(/\.$/,'');
    add(svg,'text',{x:X(x),y:top+size+24,fill:'#a9bdc9','font-size':compact?17:14,'text-anchor':'middle'},fmt(x));
    add(svg,'text',{x:left-14,y:Y(y)+5,fill:'#a9bdc9','font-size':compact?17:14,'text-anchor':'end'},fmt(y));
  }
  add(svg,'text',{x:left+size/2,y:compact?392:550,fill:'#bcd0da','font-size':compact?18:15,'text-anchor':'middle'},compact?labels[0].replace(' · parent-relative coordinate',' (parent units)').replace(' · fractional coordinate',' (fractional)'):labels[0]);
  add(svg,'text',{x:24,y:top+size/2,fill:'#bcd0da','font-size':compact?18:15,'text-anchor':'middle',transform:`rotate(-90 24 ${top+size/2})`},compact?labels[1].replace(' · parent-relative coordinate',' (parent units)').replace(' · fractional coordinate',' (fractional)').replace(' · unwrapped fractional coordinate',' (unwrapped)'):labels[1]);
  return {X,Y,left,top,size,compact};
}
function drawMap(){
  const svg=$('map-plot');svg.replaceChildren(el('title',{},'Retained point samples: no interpolation or certified area'),el('desc',{},'Use previous and next sample controls or the data table to inspect every point.'));
  const mode=$('map-view').value,domain=mode==='domain',refined=mode==='refined',bounds=domain?[0,1,0,1]:refined?[.25,.75,.5,1]:[0,1,0,1];
  const {X,Y,left,top,size,compact}=plotAxes(svg,bounds,domain?['x · fractional coordinate','y · fractional coordinate']:['u · parent-relative coordinate','v · parent-relative coordinate']);
  const points=visiblePoints();if(!points.includes(selected))selected=points.reduce((a,b)=>a.upper<b.upper?a:b);
  $('map-magnification').textContent=(domain?'1':refined?'1,024':'512')+'× LINEAR ZOOM';
  const defs=add(svg,'defs');const cp=add(defs,'clipPath',{id:'map-clip'});add(cp,'rect',{x:left,y:top,width:size,height:size});
  const g=add(svg,'g',{'clip-path':'url(#map-clip)'});
  if(!domain&&!refined){add(g,'rect',{x:X(.25),y:Y(1),width:size*.5,height:size*.5,fill:'none',stroke:'#7e939f','stroke-dasharray':'5 6'});if(!compact)add(svg,'text',{x:572,y:105,fill:'#a9bdc9','font-size':12},'Dashed box:');if(!compact)add(svg,'text',{x:572,y:124,fill:'#a9bdc9','font-size':12},'1,024× view');}
  for(const p of points){
    const px=X(domain?p.x:p.u),py=Y(domain?p.y:p.v),r=domain?1.5:p.batch==='001'?5.7:5;
    const a={fill:palette(p.upper),stroke:'#07121b','stroke-width':1.4,class:'point','data-id':p.batch+'-'+p.index};
    let n=p.batch==='001'?add(g,'rect',{...a,x:px-r,y:py-r,width:r*2,height:r*2,rx:1}):add(g,'circle',{...a,cx:px,cy:py,r});
    add(n,'title',{},`${p.batch}-${p.index}: ${p.upper.toPrecision(8)} meV; x=${p.center[0]}, y=${p.center[1]}`);n.addEventListener('click',()=>choose(p));
  }
  const px=X(domain?selected.x:selected.u),py=Y(domain?selected.y:selected.v);
  if(domain){
    const sx=X(351/512),sy=Y(369/512);add(svg,'rect',{x:sx,y:sy,width:size/512,height:size/512,fill:'none',stroke:'#ffd18b'});
    add(svg,'circle',{cx:px,cy:py,r:11,fill:'none',stroke:'#ffd18b','stroke-width':1.5});
    if(!compact)add(svg,'line',{x1:px+13,y1:py,x2:570,y2:py,stroke:'#ffd18b','stroke-width':1});
    if(!compact)add(svg,'text',{x:576,y:py-7,fill:'#ffd18b','font-size':13},'Parent patch');if(!compact)add(svg,'text',{x:576,y:py+13,fill:'#a9bdc9','font-size':12},'1/512 wide');
    add(svg,'text',{x:compact?70:110,y:compact?420:465,fill:'#a9bdc9','font-size':compact?14:12},compact?'Locator ring enlarged; not patch area.':'Ring enlarged to locate the patch; it is not its area.');
  }else{
    add(svg,'circle',{cx:px,cy:py,r:11,fill:'none',stroke:'#fff','stroke-width':1.8});
    add(svg,'line',{x1:px-17,y1:py,x2:px-12,y2:py,stroke:'white'});add(svg,'line',{x1:px+12,y1:py,x2:px+17,y2:py,stroke:'white'});
  }
  // Unit-chart locator keeps the parent patch in context on every zoomed view.
  if(!domain&&!compact){
    const lx=578,ly=320,s=105;
    add(svg,'text',{x:lx,y:ly-15,fill:'#a9bdc9','font-size':12},'UNIT CHART');add(svg,'rect',{x:lx,y:ly,width:s,height:s,fill:'#0d202d',stroke:'#405967'});
    add(svg,'circle',{cx:lx+s*selected.x,cy:ly+s*(1-selected.y),r:4,fill:'#ffd18b'});
    add(svg,'text',{x:lx,y:ly+s+22,fill:'#a9bdc9','font-size':12},'Locator enlarged');
  }
  $('sample-label').textContent=(selected.batch==='001'?'COARSE 001':'REFINED 002')+' / POINT '+selected.index;
  $('selected-gap').textContent=selected.upper.toFixed(6)+' meV';
  $('selected-location').textContent=`x = ${selected.center[0]} · y = ${selected.center[1]} (depth ${selected.cell.depth})`;
  $('selected-energy').textContent=`E₉₈ ${(+selected.energies['98']).toFixed(6)} → E₉₉ ${(+selected.energies['99']).toFixed(6)} meV`;
  const isLog=$('color-scale').value==='log';
  $('color-ticks').innerHTML=(isLog?['0.00309','0.0103','0.0345','0.115','0.386']:['0.00309','0.0987','0.194','0.290','0.386']).map(s=>`<span>${s}</span>`).join('');
  $('color-explainer').textContent=isLog?'meV · equal color steps mean equal ratios (~3.34× per tick).':'meV · equal color steps mean equal differences (~0.0956 meV per tick).';
  $('point-table').replaceChildren();
  for(const p of batchPoints()){
    const tr=document.createElement('tr');const td=document.createElement('td');const b=document.createElement('button');b.textContent=p.batch+' / '+p.index;
    b.addEventListener('click',()=>{if(!inView(p))$('map-view').value='parent';choose(p);$('selected-gap').scrollIntoView({behavior:'auto',block:'center'});});td.appendChild(b);tr.appendChild(td);
    [p.center[0],p.center[1],p.upper.toPrecision(10),p.cell.depth].forEach(v=>{const t=document.createElement('td');t.textContent=v;tr.appendChild(t);});$('point-table').appendChild(tr);
  }
}
['map-view','batch','color-scale'].forEach(id=>$(id).addEventListener('change',drawMap));
$('find-min').addEventListener('click',()=>choose(visiblePoints().reduce((a,b)=>a.upper<b.upper?a:b)));
for(const [id,direction] of [['previous-point',-1],['next-point',1]])$(id).addEventListener('click',()=>{const p=visiblePoints(),i=p.indexOf(selected);choose(p[(i+direction+p.length)%p.length]);});

function drawNodes(){
  const svg=$('nodes-plot');svg.replaceChildren(el('title',{},'Saved v062 nodes in an unwrapped fractional chart'));
  const states=D.engines[$('engine').value],step=+$('node-step').value,s=states[step];
  $('ratio-value').textContent=s.ratio.toFixed(5);$('state-counter').textContent=`STATE ${step+1} / ${states.length}`;
  const {X,Y,compact}=plotAxes(svg,[.20,.67,.59,1.06],['f₁ · fractional coordinate','f₂ · unwrapped fractional coordinate']);
  add(svg,'line',{x1:X(.2),x2:X(.67),y1:Y(1),y2:Y(1),stroke:'#e4edf0','stroke-dasharray':'5 6'});
  if(!compact)add(svg,'text',{x:569,y:Y(1)+5,fill:'#a9bdc9','font-size':12},'f₂ = 1');
  const names=['U1','U2','X1','X2','X3','X4'];
  names.forEach((name,i)=>{
    if($('show-trails').checked){const path=states.map((st,j)=>`${j?'L':'M'}${X(st.nodes[name][0])},${Y(st.nodes[name][1])}`).join(' ');add(svg,'path',{d:path,fill:'none',stroke:colors[i],'stroke-width':1.5,opacity:.55});for(const st of states)add(svg,'circle',{cx:X(st.nodes[name][0]),cy:Y(st.nodes[name][1]),r:2,fill:colors[i],opacity:.7});}
    const [x,y]=s.nodes[name],cx=X(x),cy=Y(y);add(svg,'circle',{cx,cy,r:7,fill:colors[i],stroke:'#08141d','stroke-width':2});
    const offsets={U1:[12,15],U2:[12,-10],X1:[12,-10],X2:[-32,-10],X3:[12,-10],X4:[12,17]};
    add(svg,'text',{x:cx+offsets[name][0],y:cy+offsets[name][1],fill:colors[i],'font-size':compact?18:15},name);
    if(!compact)add(svg,'circle',{cx:584,cy:315+i*27,r:3,fill:colors[i]});if(!compact)add(svg,'text',{x:597,y:320+i*27,fill:'#bcd0da','font-size':13},name);
  });
  $('node-table').replaceChildren();for(const name of names){const row=document.createElement('tr');[name,...s.nodes[name].map(v=>v.toFixed(9))].forEach(t=>{const cell=document.createElement('td');cell.textContent=t;row.appendChild(cell);});$('node-table').appendChild(row);}
}
['engine','node-step','show-trails'].forEach(id=>$(id).addEventListener('input',()=>{stop();drawNodes();}));
$('play-nodes').addEventListener('click',()=>{
  if(timer){stop();return;}
  if(+$('node-step').value===10)$('node-step').value='0';
  drawNodes();$('play-nodes').textContent='Pause playback';
  timer=setInterval(()=>{const n=+$('node-step').value+1;if(n>10){stop();return;}$('node-step').value=n;drawNodes();if(n===10)stop();},900);
});
const base='https://github.com/alanfuller15/Twistronics/blob/';
const mapping=base+D.mapping_commit+'/research/benchmarks/momentum_mapping_summary_001/OUTPUT/REPORT.md';
$('mapping-source').href=mapping;$('evidence-source').href=mapping;
$('nodes-source').href=base+D.nodes_commit+'/docs/visual-guide/README.md';
window.addEventListener('resize',()=>{if(active==='momentum')drawMap();if(active==='nodes')drawNodes();});
chapter(location.hash.slice(1)||'layers');
})();
