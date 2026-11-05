<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue';

// =====================================================================
//  R Chat: floating assistant for the home page (FRONTEND ONLY for now)
//
//  When the backend is ready, only `askBot()` below has to change.
//  Everything else (UI, animations, history) stays the same.
// =====================================================================

const isOpen = ref(false);
const input = ref('');
const isTyping = ref(false);
const listRef = ref(null);
const inputRef = ref(null);
const props = defineProps({ eventId: { type: Number, default: null } });

let nextId = 1;
const makeMsg = (from, text) => ({ id: nextId++, from, text });

const messages = ref([
  makeMsg('bot', "Hey! I'm Rolly 👋 Ask me anything about Ready2Roll: events, subscriptions, your profile..."),
]);

const suggestions = [
  'How do I find events?',
  'How do I subscribe?',
  'Who are you?',
  'What kind of night is it?',
  'Who is playing?',
  'Where is it?',
  'How much does it cost?',
];

// ---------------------------------------------------------------------
//  Bot brain (temporary, local answers)
// ---------------------------------------------------------------------
const rules = [
  { re: /\b(hi|hello|hey|yo|salam|salut|slm|bonjour)\b/i,
    reply: "Hey! 👋 What can I help you with? Events, subscriptions, profile..." },
  { re: /(who|what)\s+(are|is)\s+(you|r chat)|your name|chkon nta/i,
    reply: "I'm Rolly, the Ready2Roll assistant. Right now I run locally in your browser, soon I'll be connected to the real brain 🧠" },
  { re: /thank|thx|merci|chokran|shukran|choukran/i,
    reply: "Anytime! Keep rolling 🚀" },
  { re: /subscri|follow/i,
    reply: "Open an event on the feed and hit the Subscribe button next to the owner's name. All your subscriptions are in the \"Subscription\" tab of the menu." },
  { re: /creat|publish|owner|upload|post/i,
    reply: "Events are published by owners. If you're an owner, you can create one from your account, then it shows up in everybody's feed." },
  { re: /profile|account|avatar|settings/i,
    reply: "Your profile is behind the little person icon at the top right of the navbar." },
  { re: /message|dm|chat|inbox/i,
    reply: "Your private messages are behind the paper-plane icon in the navbar." },
  { re: /event|video|feed|discover|scroll/i,
    reply: "The feed is right here on the home page: scroll to jump from one event to the next, click a video to play or pause it. The \"Discover\" tab in the menu shows more." },
  { re: /comment|like/i,
    reply: "Select an event on the feed, then use the right panel to like it or write a comment. You can reply to other people's comments too." },
];
const fallbacks = [
  "Hmm, I'm still learning that one 🤔 Try asking about events, subscriptions or your profile.",
  "Not sure about that yet! I'm in demo mode for now, but I know the basics of Ready2Roll.",
];
let fallbackIdx = 0;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/**
 * The only place to touch when connecting to the backend.
 * Must resolve with the bot's answer as a string.
 *
 * Example (later):
 *   const res = await fetch('/api/chatbot/', {
 *     method: 'POST',
 *     headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
 *     body: JSON.stringify({ message: text, history }),
 *   });
 *   const data = await res.json();
 *   return data.reply;
 */
const askLocal = async (text) => {
  await sleep(700 + Math.random() * 700);   // fake "thinking" time
  const hit = rules.find((r) => r.re.test(text));
  if (hit) return hit.reply;
  return fallbacks[fallbackIdx++ % fallbacks.length];
};

const getToken = () =>
  localStorage.getItem('token') || localStorage.getItem('access') || localStorage.getItem('access_token');

const askBot = async (text, history = []) => {
  if (!props.eventId) return askLocal(text);          // nessun video attivo
  try {
    const res = await fetch(`/api/events/${props.eventId}/ask/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${getToken()}` },
      // send() ha già aggiunto la domanda corrente allo storico: la tolgo, il backend la aggiunge da solo
      body: JSON.stringify({ question: text, history: history.slice(0, -1) }),
    });
    const data = await res.json().catch(() => ({}));
    if (res.ok && data.answer) return data.answer;
    if (res.status === 429) return data.error || 'I need a minute, try again soon 🙏';
  } catch (e) {
    // rete o server non disponibili: uso le risposte locali
  }
  return askLocal(text);
};


// ---------------------------------------------------------------------
//  UI logic
// ---------------------------------------------------------------------
let alive = true;
onBeforeUnmount(() => { alive = false; });

const scrollToBottom = async () => {
  await nextTick();
  const el = listRef.value;
  if (el) el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
};

const toggle = async () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    await nextTick();
    inputRef.value?.focus();
    scrollToBottom();
  }
};
const close = () => { isOpen.value = false; };

const send = async (preset) => {
  const text = (typeof preset === 'string' ? preset : input.value).trim();
  if (!text || isTyping.value) return;
  input.value = '';
  messages.value.push(makeMsg('user', text));
  isTyping.value = true;
  scrollToBottom();
  try {
    const history = messages.value.map((m) => ({ role: m.from === 'bot' ? 'assistant' : 'user', content: m.text }));
    const answer = await askBot(text, history);
    if (!alive) return;
    messages.value.push(makeMsg('bot', answer));
  } catch (e) {
    if (!alive) return;
    messages.value.push(makeMsg('bot', "Oops, something went wrong on my side. Try again in a sec 🙏"));
  } finally {
    isTyping.value = false;
    scrollToBottom();
    if (alive && isOpen.value) { await nextTick(); inputRef.value?.focus(); }
  }
};

const showSuggestions = () => messages.value.length === 1 && !isTyping.value;
</script>

<template>
  <div class="rc-root" @keydown.esc="close">
    <!-- ============ Chat window ============ -->
    <transition name="rc-panel">
      <section v-if="isOpen" class="rc-panel" role="dialog" aria-label="Rolly">
        <header class="rc-header">
          <div class="rc-avatar" :class="{ busy: isTyping }">
            <span class="rc-avatar-ring"></span>
            <img src="../assets/logo_temp.png" alt="" class="rc-avatar-img">
          </div>
          <div class="rc-title-block">
            <h3 class="rc-title">Rolly</h3>
            <p class="rc-status"><span class="rc-dot"></span>{{ isTyping ? 'typing...' : 'online' }}</p>
          </div>
          <button class="rc-close" @click="close" aria-label="Close Rolly">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" class="rc-close-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </header>

        <div class="rc-messages" ref="listRef">
          <transition-group name="rc-msg" tag="div" class="rc-messages-inner">
            <div
              v-for="m in messages"
              :key="m.id"
              class="rc-row"
              :class="m.from === 'user' ? 'rc-row-user' : 'rc-row-bot'"
            >
              <img v-if="m.from === 'bot'" src="../assets/logo_temp.png" alt="" class="rc-mini">
              <div class="rc-bubble" :class="m.from === 'user' ? 'rc-bubble-user' : 'rc-bubble-bot'">{{ m.text }}</div>
            </div>

            <div v-if="isTyping" key="typing" class="rc-row rc-row-bot">
              <img src="../assets/logo_temp.png" alt="" class="rc-mini rc-mini-busy">
              <div class="rc-bubble rc-bubble-bot rc-typing" aria-label="Rolly is typing">
                <i></i><i></i><i></i>
              </div>
            </div>
          </transition-group>

          <div v-if="showSuggestions()" class="rc-suggestions">
            <button v-for="s in suggestions" :key="s" class="rc-chip" @click="send(s)">{{ s }}</button>
          </div>
        </div>

        <form class="rc-input-bar" @submit.prevent="send()">
          <input
            ref="inputRef"
            v-model="input"
            type="text"
            class="rc-input"
            placeholder="Ask Rolly..."
            maxlength="500"
            autocomplete="off"
          >
          <button type="submit" class="rc-send" :disabled="!input.trim() || isTyping" aria-label="Send">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.8" stroke="currentColor" class="rc-send-icon">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </button>
        </form>
      </section>
    </transition>

    <!-- ============ Floating R button ============ -->
    <div class="rc-launcher-wrap">
      <span v-if="!isOpen" class="rc-label">Rolly</span>
      <button class="rc-launcher" :class="{ open: isOpen }" @click="toggle" :aria-label="isOpen ? 'Close Rolly' : 'Open Rolly'" :aria-expanded="isOpen">
        <span class="rc-glow"></span>
        <span class="rc-ring rc-ring-1"></span>
        <span class="rc-ring rc-ring-2"></span>
        <span class="rc-orbit"><i></i></span>
        <span class="rc-pop">
          <span class="rc-float">
            <img src="../assets/logo_temp.png" alt="" class="rc-logo">
            <span class="rc-shine"></span>
          </span>
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.rc-root { position: fixed; left: 24px; bottom: 24px; z-index: 50; display: flex; flex-direction: column; align-items: flex-start; gap: 14px; font-family: sans-serif; color: #fff; }

/* ---------------- Launcher ---------------- */
.rc-launcher-wrap { display: flex; flex-direction: row-reverse; align-items: center; gap: 10px; }
.rc-label {
  padding: 6px 14px; border-radius: 17px; font-family: "Bruno Ace", sans-serif; font-size: 0.8rem; letter-spacing: 1px;
  background: rgba(20, 10, 40, 0.55); border: 1px solid rgba(255, 255, 255, 0.18); backdrop-filter: blur(10px);
  animation: rc-rise 0.8s ease 1.4s both;
}
.rc-launcher {
  position: relative; width: 76px; height: 76px; padding: 0; border: none; border-radius: 50%; cursor: pointer;
  background: rgba(20, 10, 40, 0.45); backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.25s ease;
}
.rc-launcher:hover { transform: scale(1.1); }
.rc-launcher:active { transform: scale(0.95); }
.rc-launcher:focus-visible { outline: 2px solid #00f2fe; outline-offset: 4px; }
.rc-pop, .rc-float { position: relative; display: block; width: 46px; height: 46px; }
.rc-pop { animation: rc-intro 1.4s cubic-bezier(.2, 1.3, .35, 1) 0.3s both; }
.rc-float { animation: rc-float 4.5s ease-in-out 1.7s infinite; }
.rc-logo { width: 100%; height: 100%; object-fit: contain; display: block; filter: drop-shadow(0 4px 10px rgba(255, 51, 187, 0.6)); }
.rc-shine {
  position: absolute; inset: 0; pointer-events: none;
  background: linear-gradient(115deg, transparent 38%, rgba(255, 255, 255, 0.9) 50%, transparent 62%);
  background-size: 300% 100%; background-repeat: no-repeat;
  -webkit-mask: url('../assets/logo_temp.png') center / contain no-repeat;
  mask: url('../assets/logo_temp.png') center / contain no-repeat;
  mix-blend-mode: soft-light;
  animation: rc-shine 3.6s ease-in-out 2.2s infinite;
}
.rc-glow {
  position: absolute; width: 110px; height: 110px; border-radius: 50%; pointer-events: none;
  background: radial-gradient(circle, rgba(255, 51, 187, 0.55) 0%, rgba(147, 51, 255, 0.35) 45%, transparent 70%);
  filter: blur(10px);
  animation: rc-glow 3.2s ease-in-out infinite;
}
.rc-ring { position: absolute; border-radius: 50%; border: 2px solid transparent; pointer-events: none; }
.rc-ring-1 { inset: 4px; border-top-color: rgba(0, 242, 254, 0.9); border-right-color: rgba(0, 242, 254, 0.25); animation: rc-spin 4s linear infinite, rc-fade-in 1s ease 0.8s both; }
.rc-ring-2 { inset: -4px; border-bottom-color: rgba(255, 51, 187, 0.9); border-left-color: rgba(255, 51, 187, 0.2); animation: rc-spin 6.5s linear infinite reverse, rc-fade-in 1s ease 1s both; }
.rc-orbit { position: absolute; inset: -4px; pointer-events: none; animation: rc-spin 7s linear infinite; }
.rc-orbit i { position: absolute; top: 0; left: 50%; width: 7px; height: 7px; margin-left: -3.5px; border-radius: 50%; background: #fff; box-shadow: 0 0 8px 2px rgba(0, 242, 254, 0.9), 0 0 18px 5px rgba(255, 51, 187, 0.6); animation: rc-twinkle 1.8s ease-in-out infinite; }
.rc-launcher.open .rc-glow { animation-duration: 1.6s; }

/* ---------------- Panel ---------------- */
.rc-panel {
  width: min(360px, calc(100vw - 32px)); height: min(520px, calc(100vh - 150px));
  display: flex; flex-direction: column; overflow: hidden;
  background: rgba(20, 10, 40, 0.6); border: 1px solid rgba(255, 255, 255, 0.18); border-radius: 15px;
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.45), 0 0 40px rgba(147, 51, 255, 0.25);
  transform-origin: bottom left;
}
.rc-panel-enter-active { transition: opacity 0.35s ease, transform 0.45s cubic-bezier(.2, 1.25, .4, 1); }
.rc-panel-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.rc-panel-enter-from, .rc-panel-leave-to { opacity: 0; transform: translateY(24px) scale(0.8); }

.rc-header { display: flex; align-items: center; gap: 12px; padding: 12px 14px; flex-shrink: 0; background: linear-gradient(90deg, rgba(255, 51, 187, 0.25), rgba(147, 51, 255, 0.25)); border-bottom: 1px solid rgba(255, 255, 255, 0.12); }
.rc-avatar { position: relative; width: 42px; height: 42px; flex-shrink: 0; display: flex; align-items: center; justify-content: center; }
.rc-avatar-img { width: 26px; height: 26px; object-fit: contain; filter: drop-shadow(0 2px 6px rgba(255, 51, 187, 0.7)); }
.rc-avatar-ring { position: absolute; inset: 0; border-radius: 50%; border: 2px solid transparent; border-top-color: #00f2fe; border-bottom-color: #ff33bb; animation: rc-spin 4s linear infinite; }
.rc-avatar.busy .rc-avatar-ring { animation-duration: 0.8s; }
.rc-avatar.busy .rc-avatar-img { animation: rc-pulse 0.8s ease-in-out infinite; }
.rc-title-block { flex: 1; min-width: 0; }
.rc-title { margin: 0; font-family: "Bruno Ace", sans-serif; font-size: 1.05rem; letter-spacing: 1px; }
.rc-status { margin: 2px 0 0; font-size: 12px; color: rgba(255, 255, 255, 0.75); display: flex; align-items: center; gap: 6px; }
.rc-dot { width: 7px; height: 7px; border-radius: 50%; background: #3dffa0; box-shadow: 0 0 8px #3dffa0; animation: rc-twinkle 2s ease-in-out infinite; }
.rc-close { background: rgba(255, 255, 255, 0.1); border: none; color: #fff; width: 32px; height: 32px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s ease; }
.rc-close:hover { background: rgba(0, 242, 254, 0.35); transform: rotate(90deg); }
.rc-close-icon { width: 16px; height: 16px; }

.rc-messages { flex: 1; overflow-y: auto; padding: 14px 12px; scrollbar-width: thin; scrollbar-color: rgba(255, 255, 255, 0.25) transparent; }
.rc-messages-inner { display: flex; flex-direction: column; gap: 10px; }
.rc-row { display: flex; align-items: flex-end; gap: 8px; }
.rc-row-user { justify-content: flex-end; }
.rc-mini { width: 22px; height: 22px; object-fit: contain; flex-shrink: 0; filter: drop-shadow(0 2px 4px rgba(255, 51, 187, 0.6)); }
.rc-mini-busy { animation: rc-pulse 0.8s ease-in-out infinite; }
.rc-bubble { max-width: 78%; padding: 9px 13px; border-radius: 15px; font-size: 14px; line-height: 1.4; white-space: pre-wrap; word-break: break-word; }
.rc-bubble-bot { background: rgba(255, 255, 255, 0.12); border: 1px solid rgba(255, 255, 255, 0.12); border-bottom-left-radius: 4px; }
.rc-bubble-user { background: linear-gradient(135deg, #ff33bb, #9333ff); border-bottom-right-radius: 4px; box-shadow: 0 4px 14px rgba(255, 51, 187, 0.3); }

.rc-msg-enter-active { transition: opacity 0.35s ease, transform 0.4s cubic-bezier(.2, 1.3, .4, 1); }
.rc-msg-enter-from { opacity: 0; transform: translateY(14px) scale(0.9); }
.rc-msg-leave-active { transition: opacity 0.15s ease; }
.rc-msg-leave-to { opacity: 0; }

.rc-typing { display: flex; align-items: center; gap: 5px; padding: 12px 14px; }
.rc-typing i { width: 7px; height: 7px; border-radius: 50%; background: #fff; display: block; animation: rc-bounce 1.1s ease-in-out infinite; }
.rc-typing i:nth-child(2) { animation-delay: 0.15s; background: #00f2fe; }
.rc-typing i:nth-child(3) { animation-delay: 0.3s; background: #ff33bb; }

.rc-suggestions { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; padding-left: 30px; }
.rc-chip { background: rgba(255, 255, 255, 0.08); border: 1px solid rgba(0, 242, 254, 0.55); color: #fff; border-radius: 17px; padding: 7px 13px; font-size: 13px; cursor: pointer; transition: all 0.2s ease; animation: rc-rise 0.6s ease both; }
.rc-chip:nth-child(2) { animation-delay: 0.1s; }
.rc-chip:nth-child(3) { animation-delay: 0.2s; }
.rc-chip:hover { background: rgba(0, 242, 254, 0.25); transform: translateY(-2px); }

.rc-input-bar { display: flex; align-items: center; gap: 8px; padding: 10px 12px; flex-shrink: 0; border-top: 1px solid rgba(255, 255, 255, 0.12); }
.rc-input { flex: 1; min-width: 0; background: rgba(255, 255, 255, 0.1); border: 1px solid transparent; border-radius: 17px; padding: 10px 16px; color: #fff; font-size: 14px; outline: none; transition: border-color 0.2s ease, background 0.2s ease; }
.rc-input::placeholder { color: rgba(255, 255, 255, 0.5); }
.rc-input:focus { border-color: rgba(0, 242, 254, 0.7); background: rgba(255, 255, 255, 0.14); }
.rc-send { width: 40px; height: 40px; flex-shrink: 0; border: none; border-radius: 50%; cursor: pointer; color: #fff; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #ff33bb, #9333ff); transition: all 0.2s ease; }
.rc-send:hover:not(:disabled) { transform: scale(1.1) rotate(-8deg); box-shadow: 0 0 16px rgba(255, 51, 187, 0.6); }
.rc-send:disabled { opacity: 0.4; cursor: not-allowed; }
.rc-send-icon { width: 20px; height: 20px; }

/* ---------------- Keyframes ---------------- */
@keyframes rc-intro {
  0%   { transform: scale(0) rotate(-540deg); opacity: 0; filter: blur(8px); }
  60%  { opacity: 1; filter: blur(0); }
  100% { transform: scale(1) rotate(0deg); opacity: 1; }
}
@keyframes rc-float {
  0%, 100% { transform: translateY(0) rotateY(0deg) rotateZ(-2deg); }
  25%      { transform: translateY(-4px) rotateY(18deg) rotateZ(0deg); }
  50%      { transform: translateY(0) rotateY(0deg) rotateZ(2deg); }
  75%      { transform: translateY(-3px) rotateY(-18deg) rotateZ(0deg); }
}
@keyframes rc-shine { 0% { background-position: 130% 0; } 55%, 100% { background-position: -30% 0; } }
@keyframes rc-glow { 0%, 100% { transform: scale(0.9); opacity: 0.7; } 50% { transform: scale(1.15); opacity: 1; } }
@keyframes rc-spin { to { transform: rotate(360deg); } }
@keyframes rc-fade-in { from { opacity: 0; } to { opacity: 1; } }
@keyframes rc-twinkle { 0%, 100% { opacity: 0.35; transform: scale(0.7); } 50% { opacity: 1; transform: scale(1.2); } }
@keyframes rc-rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes rc-pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.25); } }
@keyframes rc-bounce { 0%, 60%, 100% { transform: translateY(0); opacity: 0.6; } 30% { transform: translateY(-6px); opacity: 1; } }

@media (prefers-reduced-motion: reduce) {
  .rc-label, .rc-pop, .rc-float, .rc-shine, .rc-glow, .rc-ring, .rc-orbit, .rc-orbit i, .rc-avatar-ring, .rc-avatar-img,
  .rc-mini-busy, .rc-dot, .rc-typing i, .rc-chip { animation: none !important; }
  .rc-panel-enter-active, .rc-panel-leave-active, .rc-msg-enter-active { transition: none !important; }
}
</style>
