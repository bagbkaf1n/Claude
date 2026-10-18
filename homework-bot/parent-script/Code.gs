// ===== Налаштування =====
const SERVER_NAME = 'Дитина';   // назва сервера дитини в AdGuard DNS (як у кабінеті)
const GAME_SERVICES = [];       // id ігрових сервісів, напр. ['roblox', 'steam'] (список дасть listIds)
const GAME_CATEGORIES = [];     // id категорій сайтів, напр. ['games'] (список дасть listIds)
const GAME_HOURS = [14, 21];    // коли ігри взагалі можна відкривати
const OPEN_MINUTES = 60;        // на скільки відкриває кнопка «Відкрити»
const STATUS_MAX_AGE_MIN = 40;  // якщо від скрипта дитини давно немає статусу, ігри закриті

// ===== Статус від скрипта дитини =====

function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  const p = PropertiesService.getScriptProperties();
  if (data.secret !== p.getProperty('SECRET')) return ContentService.createTextOutput('forbidden');
  p.setProperty('status', JSON.stringify({done: !!data.done, pending: data.pending || [], at: Date.now()}));
  apply();
  return ContentService.createTextOutput('ok');
}

// ===== Логіка =====

function tick() {
  pollTelegram();
  apply();
}

function desired() {
  const p = PropertiesService.getScriptProperties();
  const now = Date.now();
  const override = JSON.parse(p.getProperty('override') || 'null');
  if (override && override.until > now) {
    return {open: override.open, why: (override.open ? 'відкрито вручну до ' : 'закрито вручну до ') + hhmm(override.until)};
  }
  const h = new Date().getHours();
  if (h < GAME_HOURS[0] || h >= GAME_HOURS[1]) return {open: false, why: 'поза ігровим часом'};
  const st = JSON.parse(p.getProperty('status') || 'null');
  if (!st || now - st.at > STATUS_MAX_AGE_MIN * 60000) return {open: false, why: 'немає свіжого статусу домашки'};
  return st.done ? {open: true, why: 'усе здано'} : {open: false, why: 'не здано завдань: ' + st.pending.length};
}

function apply() {
  const lock = LockService.getScriptLock();
  if (!lock.tryLock(20000)) return false;
  try {
    const p = PropertiesService.getScriptProperties();
    const d = desired();
    if (p.getProperty('applied') === String(d.open)) return false;
    try {
      setGames(d.open);
    } catch (e) {
      if (p.getProperty('lastError') !== e.message) notify('⚠️ Не вдалося змінити AdGuard: ' + e.message);
      p.setProperty('lastError', e.message);
      return false;
    }
    p.deleteProperty('lastError');
    p.setProperty('applied', String(d.open));
    notify((d.open ? '🎮 Ігри відкрито' : '⛔ Ігри закрито') + ' (' + d.why + ')', menu());
    return true;
  } finally {
    lock.releaseLock();
  }
}

function statusText() {
  const p = PropertiesService.getScriptProperties();
  const st = JSON.parse(p.getProperty('status') || 'null');
  let t = (p.getProperty('applied') === 'true' ? '🎮 Ігри зараз відкриті' : '⛔ Ігри зараз закриті') + ' (' + desired().why + ')';
  if (st) {
    t += '\n\nДомашка на ' + hhmm(st.at) + ': ' + (st.done ? '✅ все здано' : '📚 не здано:\n• ' + st.pending.join('\n• '));
  }
  return t;
}

// ===== AdGuard DNS =====

function adg(method, path, body) {
  const opts = {
    method: method,
    headers: {Authorization: 'ApiKey ' + PropertiesService.getScriptProperties().getProperty('ADG_KEY')},
    contentType: 'application/json',
    muteHttpExceptions: true,
  };
  if (body) opts.payload = JSON.stringify(body);
  const r = UrlFetchApp.fetch('https://api.adguard-dns.io' + path, opts);
  if (r.getResponseCode() >= 300) throw new Error(method.toUpperCase() + ' ' + path + ': ' + r.getResponseCode() + ' ' + r.getContentText());
  const text = r.getContentText();
  return text ? JSON.parse(text) : null;
}

function findServer() {
  const items = adg('get', '/oapi/v2/dns_servers?limit=100').items || [];
  const s = items.find(x => x.name.trim().toLowerCase() === SERVER_NAME.trim().toLowerCase());
  if (!s) throw new Error('Не знайшов сервер "' + SERVER_NAME + '". Є: ' + items.map(x => x.name).join(', '));
  return s;
}

function setGames(open) {
  if (!GAME_SERVICES.length && !GAME_CATEGORIES.length) throw new Error('Не задано GAME_SERVICES або GAME_CATEGORIES');
  const s = findServer();
  const pc = {};
  if (GAME_SERVICES.length) {
    const map = {};
    (s.settings.parental_control_settings.blocked_services || []).forEach(b => map[b.id] = b.enabled);
    GAME_SERVICES.forEach(id => map[id] = !open);
    pc.blocked_services = Object.keys(map).map(id => ({id: id, enabled: map[id]}));
  }
  if (GAME_CATEGORIES.length) {
    pc.blocked_filtering_categories = GAME_CATEGORIES.map(id => ({id: id, enabled: !open}));
  }
  adg('put', '/oapi/v1/dns_servers/' + s.id + '/settings', {parental_control_settings: pc});
}

function listIds() {
  Logger.log('Сервери: ' + (adg('get', '/oapi/v2/dns_servers?limit=100').items || []).map(s => '"' + s.name + '"').join(', '));
  Logger.log('Категорії: ' + adg('get', '/oapi/v1/parental_control_categories').map(c => c.id).join(', '));
  Logger.log('Сервіси:\n' + adg('get', '/oapi/v1/web_services').map(w => w.id + ' — ' + w.name).join('\n'));
}

function testClose() {
  setGames(false);
  PropertiesService.getScriptProperties().deleteProperty('applied');
  Logger.log('Ігри закрито. Перевір на пристрої дитини.');
}

function testOpen() {
  setGames(true);
  PropertiesService.getScriptProperties().deleteProperty('applied');
  Logger.log('Ігри відкрито. Перевір на пристрої дитини.');
}

// ===== Telegram =====

function menu() {
  return [
    [{text: '🎮 Відкрити на ' + OPEN_MINUTES + ' хв', callback_data: 'open'}, {text: '⛔ Закрити до кінця дня', callback_data: 'close'}],
    [{text: '🔄 Автоматично', callback_data: 'auto'}, {text: 'ℹ️ Статус', callback_data: 'status'}],
  ];
}

function pollTelegram() {
  const p = PropertiesService.getScriptProperties();
  const chatId = p.getProperty('TG_CHAT_ID');
  if (!chatId) return;
  const res = tg('getUpdates', {offset: p.getProperty('TG_OFFSET') || '0', timeout: '0'});
  (res.result || []).forEach(u => {
    p.setProperty('TG_OFFSET', String(u.update_id + 1));
    let cmd = null;
    if (u.callback_query && u.callback_query.message && String(u.callback_query.message.chat.id) === chatId) {
      cmd = u.callback_query.data;
      tg('answerCallbackQuery', {callback_query_id: u.callback_query.id});
    } else if (u.message && String(u.message.chat.id) === chatId && /^\/?(start|menu|status|меню|статус)/i.test(u.message.text || '')) {
      cmd = 'status';
    }
    if (!cmd) return;
    if (cmd === 'open') p.setProperty('override', JSON.stringify({open: true, until: Date.now() + OPEN_MINUTES * 60000}));
    if (cmd === 'close') {
      const end = new Date();
      end.setHours(23, 59, 59, 999);
      p.setProperty('override', JSON.stringify({open: false, until: end.getTime()}));
    }
    if (cmd === 'auto') p.deleteProperty('override');
    if (!apply()) notify(statusText(), menu());
  });
}

function tg(method, params) {
  const token = PropertiesService.getScriptProperties().getProperty('TG_TOKEN');
  const r = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/' + method, {method: 'post', payload: params, muteHttpExceptions: true});
  return JSON.parse(r.getContentText());
}

function notify(text, buttons) {
  const params = {chat_id: PropertiesService.getScriptProperties().getProperty('TG_CHAT_ID'), text: text};
  if (buttons) params.reply_markup = JSON.stringify({inline_keyboard: buttons});
  tg('sendMessage', params);
}

function hhmm(ms) {
  return Utilities.formatDate(new Date(ms), Session.getScriptTimeZone(), 'HH:mm');
}

// ===== Налаштування =====

function saveSettings() {
  const ADG_KEY = 'ВСТАВ_КЛЮЧ_ADGUARD';
  const TG_TOKEN = 'ВСТАВ_ТОКЕН_ДРУГОГО_БОТА';
  if (ADG_KEY.startsWith('ВСТАВ') || TG_TOKEN.startsWith('ВСТАВ')) {
    Logger.log('Встав ключ AdGuard і токен бота у дві верхні строчки цієї функції.');
    return;
  }
  const p = PropertiesService.getScriptProperties();
  p.setProperty('ADG_KEY', ADG_KEY);
  p.setProperty('TG_TOKEN', TG_TOKEN);
  if (!p.getProperty('SECRET')) p.setProperty('SECRET', Utilities.getUuid());
  const msg = (tg('getUpdates', {}).result || []).map(u => u.message).filter(Boolean).pop();
  if (!msg) {
    Logger.log('Напиши новому боту "привіт" у Telegram і запусти ще раз.');
    return;
  }
  p.setProperty('TG_CHAT_ID', String(msg.chat.id));
  Logger.log('Готово! Сервер AdGuard: "' + findServer().name + '"');
  Logger.log('SECRET для скрипта дитини: ' + p.getProperty('SECRET'));
  notify('👋 Бот керування іграми підключено!', menu());
}

function setup() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('tick').timeBased().everyMinutes(1).create();
  Logger.log('Запущено. Тепер розгорни вебзастосунок.');
}
