// Native fetch is available globally in Node 24

async function testEndpoint(url) {
  const res = await fetch(url);
  const text = await res.text();
  console.log(`[OK] ${url} -> Status ${res.status}, Length: ${text.length}`);
  return { status: res.status, text };
}

async function run() {
  console.log('=== VERIFYING SENTINELTRACE PROTOTYPE ENDPOINTS ===');
  
  // 1. Health endpoint
  const health = await testEndpoint('http://127.0.0.1:8000/api/health');
  const healthJson = JSON.parse(health.text);
  if (healthJson.status !== 'ok') throw new Error('Health status not ok');

  // 2. Actors endpoint
  const actors = await testEndpoint('http://127.0.0.1:8000/api/actors');
  const actorsList = JSON.parse(actors.text);
  console.log(`Found ${actorsList.length} actors:`, actorsList.map(a => a.name));
  if (actorsList.length < 3) throw new Error('Expected at least 3 actors');

  // 3. Search endpoint
  const search = await testEndpoint('http://127.0.0.1:8000/api/actors?q=Cinder');
  const searchList = JSON.parse(search.text);
  if (searchList.length !== 1 || searchList[0].name !== 'CinderFox') {
    throw new Error('Search filtering failed');
  }

  // 4. Actor details
  for (const actor of actorsList) {
    const detail = await testEndpoint(`http://127.0.0.1:8000/api/actors/${actor.id}`);
    const dJson = JSON.parse(detail.text);
    if (!dJson.actor || !dJson.entities || !dJson.evidence) {
      throw new Error(`Actor details invalid for ${actor.id}`);
    }

    const graph = await testEndpoint(`http://127.0.0.1:8000/api/graph?actor_id=${actor.id}`);
    const gJson = JSON.parse(graph.text);
    if (!gJson.nodes || !gJson.links) {
      throw new Error(`Graph data invalid for ${actor.id}`);
    }

    const cti = await testEndpoint(`http://127.0.0.1:8000/api/actors/${actor.id}/cti.json`);
    const ctiJson = JSON.parse(cti.text);
    if (ctiJson.schema !== 'sentineltrace-cti-demo-v1') {
      throw new Error(`CTI export invalid for ${actor.id}`);
    }

    const csv = await testEndpoint(`http://127.0.0.1:8000/api/actors/${actor.id}/export.csv`);
    if (!csv.text.includes('signal_type')) {
      throw new Error(`CSV export invalid for ${actor.id}`);
    }
  }

  // 5. Check Vite Dev Server on 5173
  const viteDev = await testEndpoint('http://127.0.0.1:5173');
  if (!viteDev.text.includes('SentinelTrace')) {
    throw new Error('Vite dev server page missing SentinelTrace title');
  }

  // 6. Check Production Static Server on 8000
  const prodStatic = await testEndpoint('http://127.0.0.1:8000/');
  if (!prodStatic.text.includes('SentinelTrace') && !prodStatic.text.includes('root')) {
    throw new Error('Production static page missing root');
  }

  console.log('\n✅ ALL VERIFICATION CHECKS PASSED PERFECTLY!');
}

run().catch(err => {
  console.error('\n❌ VERIFICATION FAILED:', err);
  process.exit(1);
});
