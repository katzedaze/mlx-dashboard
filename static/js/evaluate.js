const Evaluate = {
  categories: {},
  criteria: {},
  currentEvalId: null,
  currentResponses: [],
  judgeModel: '',

  async init() {
    this.categories = await API.getCategories();
    this.criteria = await API.getCriteria();
    try {
      const info = await API.get('/evaluate/judge');
      this.judgeModel = info.judge_model || '';
      const el = document.getElementById('eval-judge-model');
      if (el) el.textContent = this.judgeModel || '--';
    } catch (_) { /* ignore */ }
    this.renderCategories();
  },

  renderCategories() {
    const sel = document.getElementById('eval-category');
    sel.innerHTML = '<option value="">-- カテゴリを選択 --</option>';
    for (const [key, cat] of Object.entries(this.categories)) {
      sel.innerHTML += `<option value="${key}">${cat.name}</option>`;
    }
    sel.addEventListener('change', () => this.onCategoryChange());
  },

  onCategoryChange() {
    const key = document.getElementById('eval-category').value;
    const promptSel = document.getElementById('eval-prompt');
    promptSel.innerHTML = '<option value="">-- プロンプトを選択 --</option>';
    if (key && this.categories[key]) {
      this.categories[key].prompts.forEach((p, i) => {
        const short = p.length > 60 ? p.slice(0, 60) + '...' : p;
        promptSel.innerHTML += `<option value="${i}">${short}</option>`;
      });
    }
  },

  getSelectedPrompt() {
    const custom = document.getElementById('eval-custom').value.trim();
    if (custom) return custom;
    const catKey = document.getElementById('eval-category').value;
    const promptIdx = document.getElementById('eval-prompt').value;
    if (catKey && promptIdx !== '') {
      return this.categories[catKey].prompts[parseInt(promptIdx)];
    }
    return null;
  },

  async run() {
    const prompt = this.getSelectedPrompt();
    if (!prompt) { App.toast('プロンプトを選択または入力してください'); return; }

    const checked = [...document.querySelectorAll('#eval-models input:checked')].map(c => c.value);
    if (checked.length === 0) { App.toast('モデルを選択してください'); return; }

    const btn = document.getElementById('eval-run-btn');
    btn.disabled = true;
    document.getElementById('eval-loading').style.display = 'flex';
    document.getElementById('eval-loading-text').textContent = '各モデルで生成中...';
    document.getElementById('eval-responses').innerHTML = '';

    try {
      const category = document.getElementById('eval-category').value || null;
      const autoScore = document.getElementById('eval-auto-score').checked;
      btn.textContent = autoScore ? '生成+採点中...' : '生成中...';
      if (autoScore) {
        document.getElementById('eval-loading-text').textContent = `各モデルで生成後、${this.judgeModel} で自動採点します...`;
      } else {
        document.getElementById('eval-loading-text').textContent = '各モデルで生成中...';
      }
      const data = await API.runEvaluation(prompt, checked, category, autoScore);
      this.currentEvalId = data.eval_id;
      this.currentResponses = data.responses;
      this.renderResponses(prompt);
    } catch (e) {
      App.toast('評価エラー: ' + e.message);
    } finally {
      btn.disabled = false;
      btn.textContent = '評価実行';
      document.getElementById('eval-loading').style.display = 'none';
    }
  },

  renderResponses(prompt) {
    const container = document.getElementById('eval-responses');
    document.getElementById('eval-prompt-display').textContent = prompt;
    document.getElementById('eval-prompt-section').style.display = 'block';

    container.innerHTML = this.currentResponses.map(r => {
      const hasAuto = r.auto_scores && !r.judge_failed;
      const autoLabel = hasAuto
        ? `<span class="badge" style="background:rgba(76,175,80,0.2);color:#4caf50;">AI採点済</span>`
        : r.judge_failed
          ? `<span class="badge" style="background:rgba(244,67,54,0.2);color:#f44336;">採点失敗</span>`
          : '';

      return `
      <div class="response-card" data-model="${r.model_id}">
        <div class="model-header">
          <span class="model-name">${r.model_name}</span>
          <div>
            ${autoLabel}
            <span class="badge badge-tps">${r.tokens_per_second} t/s</span>
            <span class="badge badge-time">${r.response_time_ms} ms</span>
          </div>
        </div>
        <div class="response-text">${this.escapeHtml(r.response_text)}</div>
        <div class="scoring-section">
          <div style="font-size:0.75rem;color:var(--text-muted);margin-bottom:6px;">
            ${this.judgeModel ? `審判モデル: ${this.judgeModel}` : ''}
            ${hasAuto ? ' | 星をクリックで手動上書き可能' : ''}
          </div>
          ${Object.entries(this.criteria).map(([key, c]) => {
            const autoVal = r.auto_scores ? r.auto_scores[key] : 0;
            return `
            <div class="scoring-row">
              <span class="criterion-name">${c.name}</span>
              <div class="star-rating" data-criterion="${key}" data-model="${r.model_id}">
                ${[1,2,3,4,5].map(n => `<span class="star ${n <= autoVal ? 'active' : ''}" data-value="${n}" onclick="Evaluate.setScore('${r.model_id}','${key}',${n})">★</span>`).join('')}
              </div>
              <span class="auto-score-value" style="font-size:0.8rem;color:var(--text-muted);width:20px;">${autoVal || '-'}</span>
            </div>`;
          }).join('')}
          <button class="btn btn-secondary" onclick="Evaluate.submitScore('${r.model_id}')" style="margin-top:8px;">手動スコアで上書き</button>
        </div>
      </div>`;
    }).join('');

    // Initialize pending scores with auto scores
    this._pendingScores = {};
    for (const r of this.currentResponses) {
      if (r.auto_scores) {
        this._pendingScores[r.model_id] = { ...r.auto_scores };
      }
    }
  },

  _pendingScores: {},

  setScore(modelId, criterion, value) {
    if (!this._pendingScores[modelId]) this._pendingScores[modelId] = {};
    this._pendingScores[modelId][criterion] = value;
    const stars = document.querySelectorAll(`.star-rating[data-criterion="${criterion}"][data-model="${modelId}"] .star`);
    stars.forEach(s => {
      s.classList.toggle('active', parseInt(s.dataset.value) <= value);
    });
    // Update value display
    const row = stars[0]?.closest('.scoring-row');
    if (row) {
      const valEl = row.querySelector('.auto-score-value');
      if (valEl) valEl.textContent = value;
    }
  },

  async submitScore(modelId) {
    const scores = this._pendingScores[modelId];
    if (!scores || Object.keys(scores).length === 0) {
      App.toast('スコアを入力してください');
      return;
    }
    try {
      await API.rateResponse(this.currentEvalId, modelId, scores);
      App.toast('手動スコアを保存しました');
    } catch (e) {
      App.toast('保存エラー: ' + e.message);
    }
  },

  escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },
};
