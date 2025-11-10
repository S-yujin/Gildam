let map, markers = [], polyline = null;
let itineraryData = null;

/* =======================
   1. 초기 진입 & 데이터 검증
======================= */
document.addEventListener('DOMContentLoaded', async () => {
  console.log('🚀 itinerary.js 실행됨');

  const tripData = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
  const required = ['start', 'end', 'days', 'purpose', 'emotions', 'themes'];
  const missing = required.filter(k => !(k in tripData) || !tripData[k] || (Array.isArray(tripData[k]) && !tripData[k].length));

  if (missing.length) {
    alert('여행 정보가 부족합니다. 다시 입력해주세요. (누락: ' + missing.join(', ') + ')');
    window.location.href = '/';
    return;
  }

  await generateItinerary(tripData);
});

/* =======================
   2. 일정 생성 API 호출
======================= */
async function generateItinerary(tripData) {
  const loading = document.getElementById('loading');
  const content = document.getElementById('content');

  try {
    const response = await fetch('/api/generate-itinerary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tripData)
    });

    // ★ 서버 에러 메시지 노출 강화
    if (!response.ok) {
      const text = await response.text().catch(() => '');
      throw new Error(`일정 생성 실패: ${response.status} ${text}`);
    }

    itineraryData = await response.json();

    loading.style.display = 'none';
    content.style.display = 'grid';

    initMap();
    renderTabs();
    renderSchedule('all');
    initButtons();

  } catch (e) {
    console.error('❌ API 오류:', e);
    alert('일정 생성 중 문제가 발생했습니다.\n\n' + (e?.message || ''));
    window.location.href = '/theme';
  }
}

/* =======================
   3. 지도 초기화
======================= */
function initMap() {
  map = L.map('map').setView([35.1796, 129.0756], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);
}

/* =======================
   4. 탭 렌더링
======================= */
function renderTabs() {
  const tabsContainer = document.getElementById('tabs');
  const days = itineraryData.itinerary.length;

  const allTab = document.querySelector('.tab[data-day="all"]');
  if (allTab) {
    allTab.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      allTab.classList.add('active');
      renderSchedule('all');
    });
  }

  for (let i = 1; i <= days; i++) {
    const btn = document.createElement('button');
    btn.className = 'tab';
    btn.dataset.day = i;
    btn.textContent = `${i}일차`;
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      btn.classList.add('active');
      renderSchedule(i);
    });
    tabsContainer.appendChild(btn);
  }
}

/* =======================
   5. 일정 렌더링
======================= */
function renderSchedule(day) {
  const scheduleContainer = document.getElementById('schedule');
  scheduleContainer.innerHTML = '';
  clearMap();

  const daysToShow = day === 'all' ? itineraryData.itinerary : [itineraryData.itinerary[day - 1]];

  daysToShow.forEach(dayPlan => {
    const section = document.createElement('div');
    section.className = 'day-section';
    const header = document.createElement('div');
    header.className = 'day-header';
    header.innerHTML = `
      ${dayPlan.day}일차 <span class="day-date">${dayPlan.date}</span>
    `;
    section.appendChild(header);

    dayPlan.places.forEach((place, idx) => {
      const item = createPlaceItem(place, idx, dayPlan.day);
      section.appendChild(item);
    });

    scheduleContainer.appendChild(section);
  });

  // 마커 표시
  displayMarkersOnMap(daysToShow);

  // ★ 폴리라인 & 자동 줌 복귀
  const allPlaces = daysToShow.flatMap(p => p.places || []);
  if (allPlaces.length > 1) {
    const latlngs = allPlaces.map(p => [p.latitude, p.longitude]);
    polyline = L.polyline(latlngs, { color: '#111', weight: 3, opacity: 0.7, smoothFactor: 1 }).addTo(map);
    map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
  } else if (allPlaces.length === 1) {
    map.setView([allPlaces[0].latitude, allPlaces[0].longitude], 13);
  }
}

/* =======================
   6. 일정 카드 생성
======================= */
function createPlaceItem(place, index, day) {
  const div = document.createElement('div');
  div.className = 'place-item';
  div.dataset.lat = place.latitude;
  div.dataset.lng = place.longitude;

  div.innerHTML = `
    <div class="place-header">
      <div>
        <div class="place-name">${index + 1}. ${place.name}</div>
        <div class="place-time">${place.start_time} - ${place.end_time} (${place.duration}분)</div>
      </div>
    </div>
    <div class="place-category category-${place.category}">${place.category}</div>
    <div class="place-address">📍 ${place.address}</div>
    <div class="place-reason">${place.reason}</div>
    <!-- ★ 다음 장소까지 안내 복귀 -->
    ${place?.travel_to_next != null && place?.travel_distance != null ? `
      <div class="travel-info">
        다음 장소까지 약 ${place.travel_to_next}분 소요 (${place.travel_distance}km)
      </div>
    ` : ''}
  `;

  div.addEventListener('click', () => {
    console.log('[click] list', place.name);
    document.querySelectorAll('.place-item').forEach(el => el.classList.remove('active'));
    div.classList.add('active');
    map.setView([place.latitude, place.longitude], 15);
    openOverlay(place);
  });

  return div;
}

/* =======================
   7. 마커 표시
======================= */
function displayMarkersOnMap(daysToShow) {
  const colors = {
    '식당': '#FF6B6B',
    '카페': '#4ECDC4',
    '관광지': '#45B7D1',
    '체험': '#FFA07A',
    '쇼핑': '#98D8C8',
    '기타': '#939393'
  };

  let allPlaces = [];
  daysToShow.forEach(dayPlan => allPlaces = allPlaces.concat(dayPlan.places || []));

  allPlaces.forEach((place, idx) => {
    const icon = L.divIcon({
      className: 'custom-div-icon',
      html: `<div class="custom-marker marker-${place.category}"><span>${idx + 1}</span></div>`,
      iconSize: [40, 40],
      iconAnchor: [20, 50]
    });

    const marker = L.marker([place.latitude, place.longitude], { icon }).addTo(map);
    marker.on('click', () => {
      console.log('[click] marker', place.name);
      openOverlay(place);
    });

    markers.push(marker);
  });
}

/* =======================
   8. 지도/마커 초기화
======================= */
function clearMap() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];
  if (polyline) {
    map.removeLayer(polyline);
    polyline = null;
  }
}

/* =======================
   9. 오버레이 열기/닫기
======================= */
function openOverlay(place) {
  const overlay = document.getElementById('detailOverlay');
  const title = document.getElementById('overlayTitle');
  const body = document.getElementById('overlayBody');
  if (!overlay || !title || !body) return;

  title.textContent = place.name || '상세 정보';
  body.innerHTML = `
    <div class="place-category category-${place.category}" style="margin-bottom:12px;">${place.category || ''}</div>
    ${place.address ? `<div style="color:#6b7280; font-size:13px; margin-bottom:8px;">📍 ${place.address}</div>` : ''}
    ${place.start_time ? `<div style="font-size:13px; margin-bottom:8px;">🕒 ${place.start_time} - ${place.end_time} (${place.duration}분)</div>` : ''}
    ${place.reason ? `<p style="font-size:14px; margin-top:8px;">${place.reason}</p>` : ''}
  `;

  overlay.classList.remove('is-open');
  overlay.setAttribute('aria-hidden', 'true');
  setTimeout(() => {
    overlay.classList.add('is-open');
    overlay.setAttribute('aria-hidden', 'false');
  }, 30);
}

function closeOverlay() {
  const overlay = document.getElementById('detailOverlay');
  if (!overlay) return;
  overlay.classList.remove('is-open');
  overlay.setAttribute('aria-hidden', 'true');
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('overlayClose')?.addEventListener('click', closeOverlay);
});

/* =======================
   10. 버튼 / 높이 동기화
======================= */
function initButtons() {
  document.getElementById('btnBack').addEventListener('click', () => {
    if (confirm('일정을 다시 만드시겠습니까?')) {
      window.location.href = '/dates';
    }
  });

  document.getElementById('btnSave').addEventListener('click', () => {
    const dataStr = JSON.stringify(itineraryData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `gildam_itinerary_${new Date().getTime()}.json`;
    link.click();
    alert('일정이 저장되었습니다!');
  });
}

function syncLeftHeightToMap() {
  const leftCard = document.querySelector('.itinerary-left .card');
  const mapCard = document.querySelector('.map-card');
  if (!leftCard || !mapCard) return;
  const apply = () => {
    const h = mapCard.offsetHeight;
    if (h > 0) leftCard.style.height = h + 'px';
  };
  apply();
  const ro = new ResizeObserver(apply);
  ro.observe(mapCard);
  window.addEventListener('resize', apply);
}

document.addEventListener('DOMContentLoaded', syncLeftHeightToMap);
