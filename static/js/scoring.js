const Scoring = {
  async refresh() {
    try {
      const leaderboard = await API.getLeaderboard();
      const criteria = await API.getCriteria();
      this.render(leaderboard, criteria);
    } catch (e) {
      console.error('Leaderboard error:', e);
    }
  },

  render(leaderboard, criteria) {
    if (leaderboard.length === 0) {
      document.getElementById('leaderboard-empty').style.display = 'block';
      document.getElementById('leaderboard-content').style.display = 'none';
      return;
    }
    document.getElementById('leaderboard-empty').style.display = 'none';
    document.getElementById('leaderboard-content').style.display = 'block';

    const rankClasses = ['gold', 'silver', 'bronze'];
    const colors = ['#e94560', '#00d2ff', '#f5a623', '#4caf50', '#9c27b0', '#ff6b81'];
    const criteriaKeys = Object.keys(criteria);

    // Radar chart
    const radarDatasets = leaderboard.slice(0, 6).map((entry, i) => ({
      label: entry.model_name,
      data: criteriaKeys.map(k => entry.criteria_scores[k] || 0),
      borderColor: colors[i],
      backgroundColor: colors[i] + '33',
      pointBackgroundColor: colors[i],
    }));
    Charts.radar('chart-radar', criteriaKeys.map(k => criteria[k].name), radarDatasets);

    // Horizontal bar chart
    Charts.horizontalBar(
      'chart-overall',
      leaderboard.map(e => e.model_name),
      leaderboard.map(e => e.overall_score),
      leaderboard.map((_, i) => colors[i % colors.length]),
    );

    // Table
    const tbody = document.getElementById('leaderboard-table-body');
    tbody.innerHTML = leaderboard.map((entry, i) => `
      <tr>
        <td><span class="rank ${rankClasses[i] || ''}">#${i + 1}</span></td>
        <td><strong>${entry.model_name}</strong></td>
        <td><strong>${entry.overall_score}</strong></td>
        ${criteriaKeys.map(k => `<td>${(entry.criteria_scores[k] || 0).toFixed(1)}</td>`).join('')}
        <td>${entry.eval_count}</td>
      </tr>
    `).join('');
  },
};
