document.addEventListener("DOMContentLoaded", () => {
  // chips 기능 (필요 없다면 제거 가능)
  const selectedThemes = new Set();
  document.querySelectorAll(".chip").forEach(ch => {
    ch.addEventListener("click", () => {
      const v = ch.dataset.theme;
      if (selectedThemes.has(v)) {
        selectedThemes.delete(v);
        ch.classList.remove("on");
      } else {
        selectedThemes.add(v);
        ch.classList.add("on");
      }
    });
  });

  //시작하기 버튼 -> /dates 이동
  const form = document.getElementById("heroSearch");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      console.log("[home.js] /dates로 이동 중...");
      window.location.href = "/dates";
    });
  }
});

// 홈 페이지 진입 시 여행 관련 로컬 저장 데이터 초기화
document.addEventListener('DOMContentLoaded', () => {
  Object.keys(localStorage).forEach(key => {
    if (key.startsWith('gildam:')) {
      localStorage.removeItem(key);
    }
  });
});

