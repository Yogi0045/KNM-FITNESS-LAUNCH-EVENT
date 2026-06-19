// Handles the "Pick Winner" button: calls the backend, displays the
// winner, and prepends them to the winner history table.

document.getElementById('pick-winner-btn').addEventListener('click', async () => {
  const messageEl = document.getElementById('draw-message');
  const winnerDisplay = document.getElementById('winner-display');
  messageEl.textContent = '';

  try {
    const res = await fetch('/lucky-draw/pick', { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      const w = data.winner;
      document.getElementById('winner-name').textContent = w.name;
      document.getElementById('winner-reg-id').textContent = w.reg_id;
      document.getElementById('winner-city').textContent = w.city;
      winnerDisplay.classList.remove('hidden');

      const tbody = document.querySelector('#winners-table tbody');
      const emptyRow = tbody.querySelector('td[colspan]');
      if (emptyRow) emptyRow.closest('tr').remove();

      const row = document.createElement('tr');
      row.className = 'border-b border-white/5';
      row.innerHTML = `
        <td class="px-5 py-3 font-mono text-gold-400">${w.reg_id}</td>
        <td class="px-5 py-3">${w.name}</td>
        <td class="px-5 py-3">${w.city}</td>
      `;
      tbody.prepend(row);
    } else {
      winnerDisplay.classList.add('hidden');
      messageEl.innerHTML = `<span class="text-yellow-400">${data.message}</span>`;
    }
  } catch (err) {
    messageEl.innerHTML = `<span class="text-red-400">Draw failed. Please try again.</span>`;
  }
});
