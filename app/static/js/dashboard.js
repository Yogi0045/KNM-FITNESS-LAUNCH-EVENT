// Polls /api/stats every 5 seconds and updates the dashboard cards in
// place, so the numbers stay live without a full page refresh.

async function refreshStats() {
  try {
    const res = await fetch('/api/stats');
    if (!res.ok) return;
    const data = await res.json();
    if (data.success) {
      document.getElementById('stat-total').textContent = data.total;
      document.getElementById('stat-checked-in').textContent = data.checked_in;
      document.getElementById('stat-pending').textContent = data.pending;
    }
  } catch (err) {
    console.error('Failed to refresh dashboard stats', err);
  }
}

setInterval(refreshStats, 5000);
