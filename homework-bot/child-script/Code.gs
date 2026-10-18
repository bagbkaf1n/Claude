const LOOKBACK_DAYS = 7;    // прострочені за останні 7 днів
const AHEAD_DAYS = 1;       // плюс ті, що треба здати сьогодні-завтра
const HOURS = [13, 21];     // автоматичні перевірки з 13:00 до 21:00
const POLL_HOURS = [7, 23]; // кнопки й команди в Telegram працюють з 7:00 до 23:00

function preview() {
  Logger.log(JSON.stringify(applyExceptions(findPending()), null, 2));
}

function check(force) {
  force = force === true;
  const h = new Date().getHours();
  if (!force && (h < HOURS[0] || h >= HOURS[1])) return;
  const pending = applyExceptions(findPending());
  reportToParent(pending);
  const props = PropertiesService.getScriptProperties();
  props.setProperty('pending', JSON.stringify(pending.map(p => ({id: p.id, course: p.course, title: p.title}))));
  const key = pending.map(p => p.id).sort().join(',');
  if (!force && key === props.getProperty('last')) return;
  props.setProperty('last', key);
  sendStatus(pending);
}

function sendStatus(pending) {
  if (!pending.length) return notify('✅ Усі завдання здано!');
  const text = '📚 Не здано (' + pending.length + '):\n' + pending.map(p =>
    '• ' + esc(p.course) + ': <a href="' + esc(p.link) + '">' + esc(p.title) + '</a> (до ' + p.due + ')').join('\n') +
    '\n\nЯкщо завдання здано в класі, натисни на нього нижче:';
  notify(text, pending.map(p => [{text: '✔️ ' + short(p.title), callback_data: 'ex:' + p.id}]));
}

function reportToParent(pending) {
  const p = PropertiesService.getScriptProperties();
  const url = p.getProperty('PARENT_URL');
  if (!url) return;
  UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    muteHttpExceptions: true,
    payload: JSON.stringify({
      secret: p.getProperty('PARENT_SECRET'),
      done: pending.length === 0,
      pending: pending.map(x => x.course + ': ' + x.title),
    }),
  });
}

function findPending() {
  const from = Date.now() - LOOKBACK_DAYS * 864e5;
  const end = new Date();
  end.setDate(end.getDate() + AHEAD_DAYS);
  end.setHours(23, 59, 59, 999);
  const tz = Session.getScriptTimeZone();
  const result = [];
  listAll(t => Classroom.Courses.list({studentId: 'me', courseStates: ['ACTIVE'], pageToken: t}), 'courses').forEach(c => {
    const subs = listAll(t => Classroom.Courses.CourseWork.StudentSubmissions.list(c.id, '-', {userId: 'me', pageToken: t}), 'studentSubmissions')
      .filter(s => s.state !== 'TURNED_IN' && s.state !== 'RETURNED');
    subs.forEach(s => {
      let w = null;
      try {
        w = Classroom.Courses.CourseWork.get(c.id, s.courseWorkId);
      } catch (e) {
        // the course doesn't let us read the assignment itself: count it only if Classroom marks it late and it is recent
        if (s.late && Date.parse(s.creationTime) >= from) {
          result.push({id: s.id, course: c.name, title: 'завдання (без назви)', due: 'прострочено', link: s.alternateLink});
        }
        Logger.log('Немає доступу до завдання в курсі "' + c.name + '": ' + e.message);
        return;
      }
      if (!w.dueDate) return;
      const d = w.dueDate, tm = w.dueTime;
      const due = Date.UTC(d.year, d.month - 1, d.day, tm ? (tm.hours || 0) : 23, tm ? (tm.minutes || 0) : 59);
      if (due >= from && due <= end.getTime()) {
        result.push({id: s.id, course: c.name, title: w.title, due: Utilities.formatDate(new Date(due), tz, 'dd.MM HH:mm'), link: w.alternateLink});
      }
    });
  });
  return result;
}

// ---------- виключення ----------

function getSheet() {
  const props = PropertiesService.getScriptProperties();
  const id = props.getProperty('SHEET_ID');
  if (id) return SpreadsheetApp.openById(id).getSheets()[0];
  const ss = SpreadsheetApp.create('Домашка — виключення');
  const sh = ss.getSheets()[0];
  sh.appendRow(['Предмет (необов\'язково)', 'Завдання або частина назви', 'ID (заповнює бот)', 'Додано']);
  sh.setFrozenRows(1);
  sh.setColumnWidths(1, 4, 220);
  props.setProperty('SHEET_ID', ss.getId());
  return sh;
}

function applyExceptions(pending) {
  const lc = s => String(s).trim().toLowerCase();
  const rows = getSheet().getDataRange().getValues().slice(1);
  const ids = new Set(rows.map(r => String(r[2]).trim()).filter(Boolean));
  const rules = rows.filter(r => !String(r[2]).trim() && lc(r[1])).map(r => ({course: lc(r[0]), title: lc(r[1])}));
  return pending.filter(p => !ids.has(p.id) &&
    !rules.some(r => (!r.course || lc(p.course).includes(r.course)) && lc(p.title).includes(r.title)));
}

function addException(id) {
  const list = JSON.parse(PropertiesService.getScriptProperties().getProperty('pending') || '[]');
  const p = list.find(x => x.id === id);
  getSheet().appendRow([p ? p.course : '', p ? p.title : '', id, new Date()]);
  return p;
}

// ---------- Telegram ----------

function pollTelegram() {
  const h = new Date().getHours();
  if (h < POLL_HOURS[0] || h >= POLL_HOURS[1]) return;
  const props = PropertiesService.getScriptProperties();
  const chatId = props.getProperty('TG_CHAT_ID');
  const res = tg('getUpdates', {offset: props.getProperty('TG_OFFSET') || '0', timeout: '0'});
  let changed = false;
  (res.result || []).forEach(u => {
    props.setProperty('TG_OFFSET', String(u.update_id + 1));
    const cb = u.callback_query;
    if (cb && cb.message && String(cb.message.chat.id) === chatId && String(cb.data).startsWith('ex:')) {
      const p = addException(cb.data.slice(3));
      tg('answerCallbackQuery', {callback_query_id: cb.id, text: 'Зараховано: ' + (p ? short(p.title) : 'завдання')});
      changed = true;
    }
    const m = u.message;
    if (m && String(m.chat.id) === chatId && /^\/(status|статус)/i.test(m.text || '')) changed = true;
  });
  if (changed) check(true);
}

function tg(method, params) {
  const token = PropertiesService.getScriptProperties().getProperty('TG_TOKEN');
  const res = UrlFetchApp.fetch('https://api.telegram.org/bot' + token + '/' + method,
    {method: 'post', payload: params, muteHttpExceptions: true});
  return JSON.parse(res.getContentText());
}

function notify(text, buttons) {
  const params = {
    chat_id: PropertiesService.getScriptProperties().getProperty('TG_CHAT_ID'),
    text: text, parse_mode: 'HTML', disable_web_page_preview: 'true',
  };
  if (buttons) params.reply_markup = JSON.stringify({inline_keyboard: buttons});
  tg('sendMessage', params);
}

// ---------- допоміжне ----------

function listAll(fetchPage, field) {
  const out = [];
  let token;
  do {
    const r = fetchPage(token);
    out.push(...(r[field] || []));
    token = r.nextPageToken;
  } while (token);
  return out;
}

function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function short(s) {
  s = String(s);
  return s.length > 40 ? s.slice(0, 39) + '…' : s;
}

// ---------- налаштування ----------

function saveSettings() {
  const TOKEN = 'ВСТАВ_СЮДИ_ТОКЕН';
  if (TOKEN.startsWith('ВСТАВ')) {
    Logger.log('Токен уже збережено раніше. Цю функцію запускати не треба.');
    return;
  }
  const props = PropertiesService.getScriptProperties();
  props.setProperty('TG_TOKEN', TOKEN);
  const res = JSON.parse(UrlFetchApp.fetch('https://api.telegram.org/bot' + TOKEN + '/getUpdates').getContentText());
  const msg = (res.result || []).map(u => u.message).filter(Boolean).pop();
  if (!msg) {
    Logger.log('Не знайшов повідомлень. Напиши своєму боту "привіт" у Telegram і запусти ще раз.');
    return;
  }
  props.setProperty('TG_CHAT_ID', String(msg.chat.id));
  Logger.log('Готово! TG_CHAT_ID = ' + msg.chat.id);
  notify('👋 Бот підключено! Сюди приходитимуть звіти про домашку.');
}

function connectParent() {
  const URL = 'ВСТАВ_URL_ВЕБЗАСТОСУНКУ';
  const SECRET = 'ВСТАВ_SECRET';
  if (URL.startsWith('ВСТАВ') || SECRET.startsWith('ВСТАВ')) {
    Logger.log('Встав URL вебзастосунку і SECRET зі скрипта 2 у дві верхні строчки цієї функції.');
    return;
  }
  const props = PropertiesService.getScriptProperties();
  props.setProperty('PARENT_URL', URL);
  props.setProperty('PARENT_SECRET', SECRET);
  reportToParent(applyExceptions(findPending()));
  Logger.log('Підключено, статус надіслано у скрипт 2.');
}

function setup() {
  ScriptApp.getProjectTriggers().forEach(t => ScriptApp.deleteTrigger(t));
  ScriptApp.newTrigger('check').timeBased().everyMinutes(15).create();
  ScriptApp.newTrigger('pollTelegram').timeBased().everyMinutes(1).create();
  const url = getSheet().getParent().getUrl();
  Logger.log('Таблиця виключень: ' + url);
  notify('📋 Таблиця виключень: ' + url);
}
