// /static/js/dates.js

document.addEventListener('DOMContentLoaded', () => {
  const $next = document.getElementById('btnNext');
  const $back = document.getElementById('btnBack');
  const $summary = document.getElementById('summary');

  
  // 오늘 기준으로 과거 비활성화
  const today = new Date();
  today.setHours(0,0,0,0);
  const minDate = today.toISOString().slice(0,10); // YYYY-MM-DD

  // Litepicker 초기화: 한 달력(range), 인라인 렌더링
  const picker = new Litepicker({
    element: document.getElementById('picker'), // 인라인용 element
    inlineMode: true,          // 달력을 페이지에 직접 표시
    singleMode: false,         // 범위 선택
    numberOfMonths: 1,         // 한 달만
    numberOfColumns: 1,
    autoApply: true,           // 두 날짜 선택하면 즉시 확정
    minDate: today,                   // 과거 비활성화
    format: 'YYYY-MM-DD',
    lang: 'ko',
    tooltipText: { one: '일', other: '일' },
    tooltipNumber: (totalDays) => totalDays,
    lockDaysFilter: (day) => day < today, // 드래그 시 과거 금지
    lockDaysFilter: (day) => {
      const d = day.dateInstance; // dayjs → JS Date 변환
      return d < today; // ✅ 오늘 이전 날짜 클릭 불가
    }
  });

  // 저장된 선택 복원
  const saved = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
  if (saved.start && saved.end) {
  // picker 초기화 후 setDateRange로 기존 범위 복원
  picker.setDateRange(saved.start, saved.end);
  
  // summary 표시와 버튼 상태도 같이 갱신
  const nights = daysBetween(saved.start, saved.end);
  const days = nights + 1;
  $summary.textContent = `일정: ${nights}박 ${days}일`;
  $next.disabled = false;
}

  function daysBetween(a, b) {
    const A = new Date(a), B = new Date(b);
    return Math.round((B - A) / (1000*60*60*24));
  }

  // 선택 변경 이벤트
  picker.on('selected', (startDate, endDate) => {
    if (!startDate || !endDate) {
      $summary.textContent = '';
      $next.disabled = true;
      return;
    }
    const s = startDate.format('YYYY-MM-DD');
    const e = endDate.format('YYYY-MM-DD');
    const nights = daysBetween(s, e);
    const days = nights + 1;

    $summary.textContent = `일정: ${nights}박 ${days}일`;
    // 완료되었을 때만 다음 버튼 활성화
    $next.disabled = !(s && e && nights >= 0);
    // 다음 단계에서 쓰도록 저장
    localStorage.setItem('gildam:trip', JSON.stringify({ start: s, end: e, nights, days }));
  });

  // 뒤로가기 → 홈으로 이동
  $back.addEventListener('click', () => {
    localStorage.removeItem('gildam:trip');
    window.location.href = '/';   
    });

    

  // 다음 단계로
  $next.addEventListener('click', () => {
    const data = localStorage.getItem('gildam:trip');
    if (!data) return; // 안전장치
    window.location.href = '/purpose';
  });
});
