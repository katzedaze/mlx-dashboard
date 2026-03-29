const App = {
  models: [],
  metricsInterval: null,

  async init() {
    this.setupTabs();
    await this.loadModels();
    await Evaluate.init();
    this.startMetricsPolling();
  },

  setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', () => {
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById(tab.dataset.tab).classList.add('active');
        if (tab.dataset.tab === 'panel-leaderboard') Scoring.refresh();
      });
    });
  },

  async loadModels() {
    try {
      this.models = await API.getModels();
      this.renderModelCheckboxes('bench-models', this.models);
      this.renderModelCheckboxes('eval-models', this.models);
      this.renderModelStatus();
    } catch (e) {
      console.error('Failed to load models:', e);
    }
  },

  renderModelCheckboxes(containerId, models) {
    const container = document.getElementById(containerId);
    container.innerHTML = models.map(m => `
      <label class="checkbox-label">
        <input type="checkbox" value="${m.id}" ${m.downloaded ? 'checked' : ''}>
        ${m.name}
        ${m.downloaded ? '<span class="status-dot online"></span>' : '<span class="status-dot offline"></span>'}
      </label>
    `).join('');
  },

  renderModelStatus() {
    const container = document.getElementById('model-status');
    if (!container) return;
    container.innerHTML = this.models.map(m => `
      <span style="font-size:0.8rem;">
        <span class="status-dot ${m.downloaded ? 'online' : 'offline'}"></span>
        ${m.name}
      </span>
    `).join(' ');
  },

  startMetricsPolling() {
    const update = async () => {
      try {
        const m = await API.getSystemMetrics();
        document.getElementById('metric-cpu').textContent = m.cpu_percent.toFixed(1) + '%';
        document.getElementById('metric-ram').textContent = m.ram_used_gb + ' / ' + m.ram_total_gb + ' GB';
        document.getElementById('metric-ram-pct').textContent = m.ram_percent.toFixed(1) + '%';
      } catch (e) { /* ignore */ }
    };
    update();
    this.metricsInterval = setInterval(update, 3000);
  },

  toast(msg) {
    const el = document.createElement('div');
    el.className = 'toast';
    el.textContent = msg;
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 3000);
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
