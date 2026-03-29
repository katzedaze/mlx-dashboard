const Charts = {
  _instances: {},

  destroy(id) {
    if (this._instances[id]) {
      this._instances[id].destroy();
      delete this._instances[id];
    }
  },

  bar(canvasId, labels, datasets, options = {}) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');
    this._instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#eee' } } },
        scales: {
          x: { ticks: { color: '#aaa' }, grid: { color: '#2a2a4a' } },
          y: { ticks: { color: '#aaa' }, grid: { color: '#2a2a4a' }, ...options.yAxis },
        },
        ...options,
      },
    });
    return this._instances[canvasId];
  },

  horizontalBar(canvasId, labels, data, colors) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');
    this._instances[canvasId] = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{ data, backgroundColor: colors, borderRadius: 6 }],
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: '#aaa' }, grid: { color: '#2a2a4a' }, min: 0, max: 5 },
          y: { ticks: { color: '#eee', font: { size: 13 } }, grid: { display: false } },
        },
      },
    });
    return this._instances[canvasId];
  },

  radar(canvasId, labels, datasets) {
    this.destroy(canvasId);
    const ctx = document.getElementById(canvasId).getContext('2d');
    this._instances[canvasId] = new Chart(ctx, {
      type: 'radar',
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#eee' } } },
        scales: {
          r: {
            beginAtZero: true,
            max: 5,
            ticks: { color: '#aaa', backdropColor: 'transparent' },
            grid: { color: '#2a2a4a' },
            pointLabels: { color: '#eee', font: { size: 12 } },
          },
        },
      },
    });
    return this._instances[canvasId];
  },
};
