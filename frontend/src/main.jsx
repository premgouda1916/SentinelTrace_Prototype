import React, {useEffect, useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import * as d3 from 'd3';
import './styles.css';

const API = import.meta.env.VITE_API_URL || '';

function Graph({data, selected}) {
  const ref = React.useRef(null);
  useEffect(()=>{
    const el=ref.current; if(!el || !data.nodes.length) return;
    el.innerHTML=''; const width=el.clientWidth||650, height=390;
    const svg=d3.select(el).append('svg').attr('width','100%').attr('height',height).attr('viewBox',`0 0 ${width} ${height}`);
    const g=svg.append('g'); svg.call(d3.zoom().scaleExtent([.5,3]).on('zoom',e=>g.attr('transform',e.transform)));
    const sim=d3.forceSimulation(data.nodes).force('link',d3.forceLink(data.links).id(d=>d.id).distance(85)).force('charge',d3.forceManyBody().strength(-260)).force('center',d3.forceCenter(width/2,height/2));
    const link=g.append('g').selectAll('line').data(data.links).join('line').attr('stroke','#6b7280').attr('stroke-width',d=>1+d.confidence*2).attr('opacity',.65);
    const node=g.append('g').selectAll('g').data(data.nodes).join('g').call(d3.drag().on('start',(e,d)=>{if(!e.active)sim.alphaTarget(.3).restart();d.fx=d.x;d.fy=d.y}).on('drag',(e,d)=>{d.fx=e.x;d.fy=e.y}).on('end',(e,d)=>{if(!e.active)sim.alphaTarget(0);d.fx=null;d.fy=null}));
    node.append('circle').attr('r',d=>d.type==='actor'?18:10).attr('fill',d=>d.type==='actor'?'#0f766e':'#334155').attr('stroke',d=>d.id===selected?'#f59e0b':'#e2e8f0').attr('stroke-width',d=>d.id===selected?4:1.5);
    node.append('text').text(d=>d.label).attr('x',13).attr('y',4).attr('font-size','11px').attr('fill','#0f172a');
    sim.on('tick',()=>{link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);node.attr('transform',d=>`translate(${d.x},${d.y})`)});
    return ()=>sim.stop();
  },[data,selected]);
  return <div className="graph" ref={ref}/>;
}

function App(){
  const [actors,setActors]=useState([]),[selected,setSelected]=useState(null),[detail,setDetail]=useState(null),[graph,setGraph]=useState({nodes:[],links:[]}),[q,setQ]=useState(''),[health,setHealth]=useState(null);
  const load=async()=>{const r=await fetch(`${API}/api/actors${q?`?q=${encodeURIComponent(q)}`:''}`);const x=await r.json();setActors(x); if(!selected&&x[0]) select(x[0].id);};
  const select=async id=>{setSelected(id);const [a,g]=await Promise.all([fetch(`${API}/api/actors/${id}`).then(r=>r.json()),fetch(`${API}/api/graph?actor_id=${id}`).then(r=>r.json())]);setDetail(a);setGraph(g)};
  useEffect(()=>{load();fetch(`${API}/api/health`).then(r=>r.json()).then(setHealth)},[]);
  const score=useMemo(()=>detail?Math.round(detail.actor.confidence*100):0,[detail]);
  return <div className="app">
    <header><div><div className="brand">SENTINELTRACE</div><div className="sub">Threat Actor Intelligence & Attribution Support</div></div><div className="health">● {health?.status==='ok'?'Demo online':'Connecting'}</div></header>
    <main>
      <section className="toolbar"><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search actor or category..."/><button onClick={load}>Search</button><span className="demo">Synthetic data · authorized workflow demonstration</span></section>
      <div className="grid">
        <aside><h3>Actor profiles</h3>{actors.map(a=><button className={`actor ${selected===a.id?'active':''}`} key={a.id} onClick={()=>select(a.id)}><span>{a.name}</span><b>{Math.round(a.confidence*100)}%</b><small>{a.category} · {a.status}</small></button>)}</aside>
        <section className="panel"><div className="panelhead"><div><h2>Relationship graph</h2><p>Evidence-linked identifiers and infrastructure</p></div>{detail&&<div className="score"><strong>{score}%</strong><span>attribution confidence</span></div>}</div><Graph data={graph} selected={selected}/><div className="legend"><span><i className="actorDot"/>Actor</span><span><i className="entityDot"/>Identifier / signal</span><span>Edge width = relationship confidence</span></div></section>
        <section className="panel evidence"><div className="panelhead"><div><h2>Case evidence</h2><p>Provenance · reliability · analyst review</p></div>{detail&&<div className="actions"><a href={`${API}/api/actors/${selected}/export.csv`}>CSV</a><a href={`${API}/api/actors/${selected}/export.json`}>JSON</a><a href={`${API}/api/actors/${selected}/cti.json`}>CTI</a></div>}</div>
          {detail?<><div className="case"><h3>{detail.actor.name}</h3><span>{detail.actor.category}</span><p>{detail.actor.summary}</p></div><div className="timeline">{detail.evidence.map(e=><article key={e.id}><div className="line"><b>{e.signal_type}</b><time>{e.observed_at.slice(0,10)}</time></div><p>{e.description}</p><small>{e.source} · reliability {Math.round(e.reliability*100)}% · signal confidence {Math.round(e.confidence*100)}%</small></article>)}</div></>:<p>Select an actor.</p>}
        </section>
      </div>
    </main>
    <footer>SentinelTrace · SIH26151 · Attribution hypotheses only — analyst review required.</footer>
  </div>
}
createRoot(document.getElementById('root')).render(<App/>);
