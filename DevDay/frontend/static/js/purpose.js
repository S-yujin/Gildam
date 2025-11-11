document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('purposeForm');
  const textarea = document.getElementById('purposeText');
  const charCount = document.getElementById('charCount');
  const backBtn = document.getElementById('btnPurposeBack');
  const nextBtn = document.getElementById('btnPurposeNext');
  const checkboxes = document.querySelectorAll('.emotion-list input[type="checkbox"]');
  const MAX = 300;

  // 기존 데이터 복원
  const saved = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
  if (typeof saved.purpose === 'string') textarea.value = saved.purpose;
  if (Array.isArray(saved.emotions)) {
    checkboxes.forEach(cb => {
      if (saved.emotions.includes(cb.value)) cb.checked = true;
    });
  }

  // ✅ 수정된 상태 동기화 (둘 다 입력해야 활성화)
  const sync = () => {
    if (textarea.value.length > MAX) textarea.value = textarea.value.slice(0, MAX);
    charCount.textContent = textarea.value.length;

    const hasText = textarea.value.trim().length > 0;
    const hasEmotion = Array.from(checkboxes).some(cb => cb.checked);
    const enable = hasText && hasEmotion; // 둘 다 true여야 활성화

    nextBtn.disabled = !enable;
    nextBtn.classList.toggle('active', enable);
  };

  // ✅ 텍스트, 체크박스 모두 이벤트 감시
  textarea.addEventListener('input', sync);
  checkboxes.forEach(cb => cb.addEventListener('change', sync));
  sync();

  // 뒤로가기 → dates 페이지로
  backBtn.addEventListener('click', () => {
    window.location.href = '/dates';
  });

  // ✅ 제출 시 둘 다 없으면 막기
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const text = textarea.value.trim();
    const emotions = Array.from(checkboxes)
      .filter(cb => cb.checked)
      .map(cb => cb.value);

    if (!text || emotions.length === 0) return; // 둘 다 필요

    const trip = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
    trip.purpose = text;
    trip.emotions = emotions;

    localStorage.setItem('gildam:trip', JSON.stringify(trip));
    window.location.href = '/theme';
  });
});
