// Handles the QR check-in page: camera scanning via html5-qrcode,
// manual lookup, rendering the participant card, and submitting the
// check-in action.

let html5QrCode = null;
let isScanning = false;

const resultCard = document.getElementById('result-card');
const statusMessage = document.getElementById('status-message');

function renderParticipant(p) {
  resultCard.classList.remove('hidden');

  const statusHtml = p.checked_in
    ? `<span class="text-green-400">Checked In${p.check_in_time ? ' at ' + p.check_in_time : ''}</span>`
    : `<span class="text-gray-500">Not Checked In</span>`;

  resultCard.innerHTML = `
    <div class="flex justify-between items-start mb-4">
      <div>
        <p class="text-xs text-gray-500">Registration ID</p>
        <p class="font-display text-xl font-bold gold-text">${p.reg_id}</p>
      </div>
      <div class="text-right text-sm">${statusHtml}</div>
    </div>
    <div class="grid grid-cols-2 gap-3 text-sm text-gray-300 mb-5">
      <p><span class="text-gray-500">Name:</span> ${p.name}</p>
      <p><span class="text-gray-500">Age:</span> ${p.age}</p>
      <p><span class="text-gray-500">Weight:</span> ${p.weight} kg</p>
      <p><span class="text-gray-500">City:</span> ${p.city}</p>
      <p><span class="text-gray-500">Phone:</span> ${p.phone}</p>
      <p><span class="text-gray-500">Email:</span> ${p.email}</p>
    </div>
    <button id="checkin-btn" ${p.checked_in ? 'disabled' : ''}
      class="w-full gold-gradient text-black font-bold py-3 rounded-lg transition ${p.checked_in ? 'opacity-40 cursor-not-allowed' : 'hover:scale-[1.02]'}">
      ${p.checked_in ? 'Already Checked In' : 'Check In'}
    </button>
  `;

  if (!p.checked_in) {
    document.getElementById('checkin-btn').addEventListener('click', () => performCheckin(p.reg_id));
  }
}

async function lookupParticipant(regId) {
  statusMessage.textContent = '';
  try {
    const res = await fetch(`/api/participant/${encodeURIComponent(regId)}`);
    const data = await res.json();
    if (data.success) {
      renderParticipant(data.participant);
    } else {
      resultCard.classList.add('hidden');
      statusMessage.innerHTML = `<span class="text-red-400">${data.message}</span>`;
    }
  } catch (err) {
    statusMessage.innerHTML = `<span class="text-red-400">Lookup failed. Please try again.</span>`;
  }
}

async function performCheckin(regId) {
  try {
    const res = await fetch(`/api/checkin/${encodeURIComponent(regId)}`, { method: 'POST' });
    const data = await res.json();

    if (data.success) {
      statusMessage.innerHTML = `<span class="text-green-400">${data.message}</span>`;
    } else {
      statusMessage.innerHTML = `<span class="text-yellow-400">${data.message}</span>`;
    }
    // Refresh the card so the button + status reflect the new state.
    lookupParticipant(regId);
  } catch (err) {
    statusMessage.innerHTML = `<span class="text-red-400">Check-in failed. Please try again.</span>`;
  }
}

function onScanSuccess(decodedText) {
  let regId = decodedText;
  try {
    const parsed = JSON.parse(decodedText);
    if (parsed && parsed.reg_id) {
      regId = parsed.reg_id;
    }
  } catch (err) {
    // Not JSON -- treat the raw scanned text as the reg_id.
  }
  lookupParticipant(regId);
  stopScanning();
}

function startScanning() {
  html5QrCode = new Html5Qrcode('qr-reader');
  html5QrCode
    .start({ facingMode: 'environment' }, { fps: 10, qrbox: 250 }, onScanSuccess)
    .then(() => {
      isScanning = true;
      document.getElementById('start-scan').disabled = true;
      document.getElementById('stop-scan').disabled = false;
    })
    .catch((err) => {
      statusMessage.innerHTML = `<span class="text-red-400">Camera error: ${err}</span>`;
    });
}

function stopScanning() {
  if (html5QrCode && isScanning) {
    html5QrCode.stop().then(() => {
      isScanning = false;
      document.getElementById('start-scan').disabled = false;
      document.getElementById('stop-scan').disabled = true;
    });
  }
}

document.getElementById('start-scan').addEventListener('click', startScanning);
document.getElementById('stop-scan').addEventListener('click', stopScanning);

document.getElementById('manual-lookup').addEventListener('click', () => {
  const regId = document.getElementById('manual-reg-id').value.trim();
  if (regId) lookupParticipant(regId);
});

document.getElementById('manual-reg-id').addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    document.getElementById('manual-lookup').click();
  }
});
