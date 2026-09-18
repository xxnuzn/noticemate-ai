const noticeText = document.querySelector('#noticeText');
const analyzeBtn = document.querySelector('#analyzeBtn');
const sampleBtn = document.querySelector('#sampleBtn');
const clearBtn = document.querySelector('#clearBtn');
const resultEl = document.querySelector('#result');
const modeTag = document.querySelector('#modeTag');
const historyEl = document.querySelector('#history');

const sample = `2026 SCNU OSS·AI 해커톤 최종 제출 안내
9.27(일) 오후 10시까지 통합 갤러리에 프로젝트를 등록하고, 실행 URL, GitHub 공개 저장소, README, 발표자료(PPT/PDF)를 제출해야 합니다. 9.30(수) 13:00~17:00 본 행사에서 팀별 발표와 시연이 진행됩니다. GitHub에는 전체 소스코드, README, 오픈소스 라이선스를 포함해주세요.`;

function escapeHtml(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

function list(items, mapper) {
  if (!items || items.length === 0) return '<p class="empty">추출된 항목이 없습니다.</p>';
  return `<ul>${items.map(mapper).join('')}</ul>`;
}

function render(data) {
  modeTag.textContent = data.mode === 'ai' ? 'AI 분석' : '기본 분석';
  resultEl.innerHTML = `
    <div class="result-block">
      <h3>핵심 요약</h3>
      ${list(data.summary, item => `<li>${escapeHtml(item)}</li>`)}
    </div>
    <div class="result-block">
      <h3>마감일/일정</h3>
      ${list(data.deadlines, item => `<li><b>${escapeHtml(item.date)}</b> - ${escapeHtml(item.title)}<br><small>${escapeHtml(item.detail)}</small></li>`)}
    </div>
    <div class="result-block">
      <h3>해야 할 일</h3>
      ${list(data.todos, item => `<li>${escapeHtml(item.task)} <span class="priority">${escapeHtml(item.priority)}</span></li>`)}
    </div>
    <div class="result-block">
      <h3>준비물</h3>
      ${list(data.materials, item => `<li>${escapeHtml(item)}</li>`)}
    </div>
    <div class="result-block">
      <h3>주의할 점</h3>
      ${list(data.risks, item => `<li>${escapeHtml(item)}</li>`)}
    </div>
    <div class="result-block">
      <h3>캘린더 복사용</h3>
      <p>${escapeHtml(data.calendar_text)}</p>
    </div>
  `;
}

function saveHistory(text, data) {
  const history = JSON.parse(localStorage.getItem('noticemate-history') || '[]');
  history.unshift({
    text: text.slice(0, 80),
    summary: data.summary?.[0] || '',
    created_at: data.created_at || new Date().toLocaleString()
  });
  localStorage.setItem('noticemate-history', JSON.stringify(history.slice(0, 5)));
  renderHistory();
}

function renderHistory() {
  const history = JSON.parse(localStorage.getItem('noticemate-history') || '[]');
  if (history.length === 0) {
    historyEl.innerHTML = '<li class="empty">저장된 분석 기록이 없습니다.</li>';
    return;
  }
  historyEl.innerHTML = history.map(item => `
    <li class="history-item">
      <b>${escapeHtml(item.created_at)}</b><br>
      ${escapeHtml(item.summary)}<br>
      <small>원문: ${escapeHtml(item.text)}...</small>
    </li>
  `).join('');
}

sampleBtn.addEventListener('click', () => { noticeText.value = sample; });
clearBtn.addEventListener('click', () => { localStorage.removeItem('noticemate-history'); renderHistory(); });

analyzeBtn.addEventListener('click', async () => {
  const text = noticeText.value.trim();
  if (text.length < 10) {
    alert('공지 내용을 10자 이상 입력해주세요.');
    return;
  }
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = '분석 중...';
  resultEl.innerHTML = '<p class="empty">AI가 내용을 정리하고 있습니다.</p>';
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || '분석 실패');
    render(data);
    saveHistory(text, data);
  } catch (error) {
    resultEl.innerHTML = `<p class="empty">오류: ${escapeHtml(error.message)}</p>`;
  } finally {
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'AI로 분석하기';
  }
});

renderHistory();
