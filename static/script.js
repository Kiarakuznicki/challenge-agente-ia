const chatContainer = document.getElementById('chatContainer');
const chat = document.getElementById('chat');
const emptyState = document.getElementById('emptyState');
const form = document.getElementById('chatForm');
const input = document.getElementById('pregunta');
const sendBtn = document.getElementById('sendBtn');

function agregarMensaje(texto, tipo, fuentes) {
  emptyState.style.display = 'none';
  const msg = document.createElement('div');
  msg.className = `msg ${tipo}`;
  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = texto;
  msg.appendChild(bubble);
  if (fuentes && fuentes.length) {
    const src = document.createElement('div');
    src.className = 'sources';
    src.textContent = 'Fuente: ' + fuentes.join(', ');
    msg.appendChild(src);
  }
  chat.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function mostrarEscribiendo() {
  const msg = document.createElement('div');
  msg.className = 'msg bot';
  msg.id = 'typingIndicator';
  msg.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
  chat.appendChild(msg);
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

function quitarEscribiendo() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

async function enviarPregunta(pregunta) {
  agregarMensaje(pregunta, 'user');
  mostrarEscribiendo();
  sendBtn.disabled = true;
  try {
    const res = await fetch('/api/preguntar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pregunta }),
    });
    const data = await res.json();
    quitarEscribiendo();
    if (!res.ok) {
      agregarMensaje(data.error || 'Ocurrió un error al procesar la pregunta.', 'bot');
    } else {
      agregarMensaje(data.respuesta, 'bot', data.fuentes);
    }
  } catch (err) {
    quitarEscribiendo();
    agregarMensaje('No se pudo conectar con el servidor. Intentá de nuevo.', 'bot');
  } finally {
    sendBtn.disabled = false;
  }
}

form.addEventListener('submit', (e) => {
  e.preventDefault();
  const pregunta = input.value.trim();
  if (!pregunta) return;
  input.value = '';
  enviarPregunta(pregunta);
});

document.querySelectorAll('.suggestion-chip').forEach((chip) => {
  chip.addEventListener('click', () => enviarPregunta(chip.dataset.q));
});