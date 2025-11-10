import { postJSON } from "/static/js/api.js";

function getMultiSelectValues(sel) {
  return Array.from(sel.selectedOptions).map(o => o.value);
}

async function onAnalyze() {
  const text = document.getElementById("freeText").value.trim();
  if (!text) return alert("감정 분석할 텍스트를 입력해 주세요.");
  const data = await postJSON("/api/emotion", { text });
  const el = document.getElementById("analyzeResult");
  if (data.emotions?.length) {
    el.textContent = "Gemini가 감지한 감정: " + data.emotions.join(", ");
    // 자동 반영
    const sel = document.getElementById("emotions");
    Array.from(sel.options).forEach(opt => {
      opt.selected = data.emotions.includes(opt.value);
    });
  } else {
    el.textContent = "감정을 추출하지 못했습니다.";
  }
}

async function onRecommend() {
  const emotions = getMultiSelectValues(document.getElementById("emotions"));
  const themes = getMultiSelectValues(document.getElementById("themes"));
  const date = document.getElementById("date").value || null;

  const payload = { emotions, themes, date };
  const data = await postJSON("/api/recommend", payload);
  renderResults(data.items || []);
}

function renderResults(items) {
  const root = document.getElementById("resultList");
  root.innerHTML = "";
  if (!items.length) {
    root.innerHTML = "<p>조건에 맞는 결과가 없어요 😿</p>";
    return;
  }
  items.forEach(item => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `
      <h3>${item.name}</h3>
      <div class="meta">${item.category} • ${item.district}</div>
      <div>점수: <span class="score">${item.score.toFixed(3)}</span></div>
      <div class="tags">
        ${(item.tags || []).map(t => `<span class="tag">#${t}</span>`).join(" ")}
      </div>
    `;
    root.appendChild(div);
  });
}

window.addEventListener("DOMContentLoaded", () => {
  document.getElementById("btnAnalyze").addEventListener("click", onAnalyze);
  document.getElementById("btnRecommend").addEventListener("click", onRecommend);
});
