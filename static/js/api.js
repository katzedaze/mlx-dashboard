const API = {
  async get(path) {
    const res = await fetch(`/api${path}`);
    if (!res.ok) throw new Error(`GET ${path}: ${res.status}`);
    return res.json();
  },
  async post(path, body) {
    const res = await fetch(`/api${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(`POST ${path}: ${res.status}`);
    return res.json();
  },

  getModels: () => API.get('/models'),
  getSystemMetrics: () => API.get('/system/metrics'),
  getHealth: () => API.get('/system/health'),

  runBenchmark: (modelIds, numRuns) => API.post('/benchmark/run', { model_ids: modelIds, num_runs: numRuns }),
  getBenchmarkResults: () => API.get('/benchmark/results'),

  getCategories: () => API.get('/evaluate/categories'),
  runEvaluation: (prompt, modelIds, category, autoScore) => API.post('/evaluate/run', { prompt, model_ids: modelIds, category, auto_score: autoScore }),
  getHistory: () => API.get('/evaluate/history'),

  rateResponse: (evalId, modelId, scores) => API.post('/scoring/rate', { eval_id: evalId, model_id: modelId, scores }),
  getLeaderboard: () => API.get('/scoring/leaderboard'),
  getCriteria: () => API.get('/scoring/criteria'),
};
