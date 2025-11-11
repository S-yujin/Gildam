// /static/js/theme.js
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('themeForm');
  const backBtn = document.getElementById('btnThemeBack');
  const nextBtn = document.getElementById('btnThemeNext');
  const checks = [...document.querySelectorAll('.theme-list input[type="checkbox"]')];
  const LIMIT = 3;

  // 저장된 선택 복원
  const saved = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
  if (Array.isArray(saved.themes)) {
    checks.forEach(cb => { cb.checked = saved.themes.includes(cb.value); });
  }

  // 버튼 활성화 동기화
  function sync() {
    const selected = checks.filter(cb => cb.checked);
    // 1~3개 사이면 활성화
    const enable = selected.length >= 1 && selected.length <= LIMIT;
    nextBtn.disabled = !enable;
    nextBtn.classList.toggle('active', enable);
  }

  // 선택 제한
  checks.forEach(cb => {
    cb.addEventListener('change', () => {
      const selected = checks.filter(x => x.checked);
      if (selected.length > LIMIT) {
        cb.checked = false;
        alert(`최대 ${LIMIT}개까지 선택할 수 있어요.`);
      }
      sync();
    });
  });
  sync();

  // 뒤로가기 (직전 페이지로)
  backBtn.addEventListener('click', () => history.back());

  // 제출 → 로컬 저장 후 다음 단계로
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const themes = checks.filter(cb => cb.checked).map(cb => cb.value);
    if (themes.length === 0 || themes.length > LIMIT) return;

    const trip = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
    trip.themes = themes; // ex) ["바다","카페","포토스팟"]
    localStorage.setItem('gildam:trip', JSON.stringify(trip));

    // 다음 페이지(원하면 경로 바꾸기)
    window.location.href = '/itinerary';
  });
});

