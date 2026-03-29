const Benchmark = {
  results: [],

  async run() {
    const checked = [...document.querySelectorAll('#bench-models input:checked')].map(c => c.value);
    if (checked.length === 0) { App.toast('モデルを選択してください'); return; }

    const numRuns = parseInt(document.getElementById('bench-runs').value) || 3;
    const btn = document.getElementById('bench-run-btn');
    btn.disabled = true;
    btn.textContent = '実行中...';
    document.getElementById('bench-loading').style.display = 'flex';
    document.getElementById('bench-results').style.display = 'none';

    try {
      this.results = await API.runBenchmark(checked, numRuns);
      this.render();
    } catch (e) {
      App.toast('ベンチマークエラー: ' + e.message);
    } finally {
      btn.disabled = false;
      btn.textContent = 'ベンチマーク実行';
      document.getElementById('bench-loading').style.display = 'none';
    }
  },

  render() {
    if (this.results.length === 0) return;
    document.getElementById('bench-results').style.display = 'block';

    const labels = this.results.map(r => r.model_name);
    const colors = ['#e94560', '#00d2ff', '#f5a623', '#4caf50', '#9c27b0', '#ff6b81'];

    Charts.bar('chart-tps', labels, [{
      label: 'Tokens/sec',
      data: this.results.map(r => r.tokens_per_second),
      backgroundColor: colors.slice(0, this.results.length),
      borderRadius: 6,
    }]);

    Charts.bar('chart-time', labels, [{
      label: '応答時間 (ms)',
      data: this.results.map(r => r.avg_response_time_ms),
      backgroundColor: colors.slice(0, this.results.length),
      borderRadius: 6,
    }]);

    const tbody = document.getElementById('bench-table-body');
    tbody.innerHTML = this.results.map(r => `
      <tr>
        <td><strong>${r.model_name}</strong></td>
        <td><span class="badge badge-tps">${r.tokens_per_second} t/s</span></td>
        <td><span class="badge badge-time">${r.avg_response_time_ms} ms</span></td>
        <td>${r.prompt_eval_time_ms} ms</td>
        <td>${r.total_tokens}</td>
      </tr>
    `).join('');
  },
};
