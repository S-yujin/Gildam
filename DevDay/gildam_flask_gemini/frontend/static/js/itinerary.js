let map, markers = [], polyline = null;
let itineraryData = null;

document.addEventListener('DOMContentLoaded', async () => {
  console.log('='.repeat(60));
  console.log('🚀 itinerary.js 로드됨');
  console.log('='.repeat(60));
  
  const tripData = JSON.parse(localStorage.getItem('gildam:trip') || '{}');
  console.log('📦 localStorage에서 불러온 데이터:', tripData);

  const required = ['start','end','days','purpose','emotions','themes'];
  const missing = required.filter(k => !(k in tripData) || !tripData[k] || (Array.isArray(tripData[k]) && !tripData[k].length));
  
  if (missing.length) {
    console.error('❌ 필수 데이터 누락:', missing);
    alert('여행 정보가 부족합니다. 다시 입력해주세요. (누락: ' + missing.join(', ') + ')');
    window.location.href = '/';
    return;
  }

  console.log('✅ 데이터 검증 완료, API 호출 시작...');
  await generateItinerary(tripData);
});

async function generateItinerary(tripData) {
  console.log('='.repeat(60));
  console.log('🌐 API 호출 시작');
  console.log('   URL: /api/generate-itinerary');
  console.log('   데이터:', tripData);
  console.log('='.repeat(60));
  
  const loading = document.getElementById('loading');
  const content = document.getElementById('content');

  try {
    const response = await fetch('/api/generate-itinerary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(tripData)
    });

    console.log('📡 응답 받음:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ API 오류:', errorText);
      throw new Error(`일정 생성 실패: ${response.status} ${errorText}`);
    }

    itineraryData = await response.json();
    console.log('✅ 일정 데이터 받음:', itineraryData);

    // 로딩 숨기고 컨텐츠 표시
    loading.style.display = 'none';
    content.style.display = 'grid';

    // UI 렌더링
    console.log('🎨 UI 렌더링 시작...');
    initMap();
    renderTabs();
    renderSchedule('all');
    initButtons();
    console.log('✅ UI 렌더링 완료');

  } catch (error) {
    console.error('='.repeat(60));
    console.error('❌ 치명적 오류:');
    console.error('   타입:', error.name);
    console.error('   메시지:', error.message);
    console.error('   스택:', error.stack);
    console.error('='.repeat(60));
    
    alert('일정 생성 중 오류가 발생했습니다.\n\n' + error.message + '\n\n콘솔을 확인해주세요.');
    
    // 오류 발생 시 theme 페이지로 돌아가기
    setTimeout(() => {
      window.location.href = '/theme';
    }, 3000);
  }
}

function initMap() {
  console.log('🗺️ 지도 초기화...');
  map = L.map('map').setView([35.1796, 129.0756], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);
  
  console.log('✅ 지도 초기화 완료');
}

function renderTabs() {
  console.log('🏷️ 탭 렌더링...');
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
  
  console.log(`✅ ${days}개 탭 생성 완료`);
}

function renderSchedule(day) {
  console.log(`📅 일정 렌더링: ${day}`);
  const scheduleContainer = document.getElementById('schedule');
  scheduleContainer.innerHTML = '';

  clearMap();

  let daysToShow = [];
  if (day === 'all') {
    daysToShow = itineraryData.itinerary;
  } else {
    daysToShow = [itineraryData.itinerary[day - 1]];
  }

  daysToShow.forEach((dayPlan) => {
    const section = document.createElement('div');
    section.className = 'day-section';

    const header = document.createElement('div');
    header.className = 'day-header';
    header.innerHTML = `
      ${dayPlan.day}일차
      <span class="day-date">${dayPlan.date}</span>
    `;
    section.appendChild(header);

    dayPlan.places.forEach((place, idx) => {
      const item = createPlaceItem(place, idx, dayPlan.day);
      section.appendChild(item);
    });

    scheduleContainer.appendChild(section);
  });

  displayMarkersOnMap(daysToShow);
  console.log('✅ 일정 렌더링 완료');
}

function createPlaceItem(place, index, day) {
  const div = document.createElement('div');
  div.className = 'place-item';
  div.dataset.lat = place.latitude;
  div.dataset.lng = place.longitude;
  div.dataset.index = index;

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
    ${place.travel_to_next ? `
      <div class="travel-info">
        다음 장소까지 약 ${place.travel_to_next}분 소요 (${place.travel_distance}km)
      </div>
    ` : ''}
  `;

  div.addEventListener('click', () => {
    document.querySelectorAll('.place-item').forEach(el => el.classList.remove('active'));
    div.classList.add('active');
    
    map.setView([place.latitude, place.longitude], 15);
  });

  return div;
}

function displayMarkersOnMap(daysToShow) {
  console.log('📍 마커 표시 중...');
  const colors = {
    '식당': '#FF6B6B',
    '카페': '#4ECDC4',
    '관광지': '#45B7D1',
    '체험': '#FFA07A',
    '쇼핑': '#98D8C8',
    '기타': '#939393'
  };

  let allPlaces = [];
  daysToShow.forEach(dayPlan => {
    allPlaces = allPlaces.concat(dayPlan.places);
  });

  allPlaces.forEach((place, idx) => {
    const markerColor = colors[place.category] || '#111';
    
    const icon = L.divIcon({
      className: 'custom-div-icon',
      html: `
        <div class="custom-marker marker-${place.category}">
          <span>${idx + 1}</span>
        </div>
      `,
      iconSize: [40, 40],
      iconAnchor: [20, 50],
      popupAnchor: [0, -45]
    });

    const marker = L.marker([place.latitude, place.longitude], { icon })
      .addTo(map)
      .bindPopup(`
        <div style="min-width:200px;">
          <strong style="font-size:16px;">${place.name}</strong><br>
          <span style="color:#666; font-size:13px;">${place.category}</span><br>
          <span style="font-size:12px;">${place.start_time} - ${place.end_time}</span><br>
          <p style="margin:8px 0 0 0; font-size:13px;">${place.reason}</p>
        </div>
      `);

    markers.push(marker);
  });

  if (allPlaces.length > 1) {
    const latlngs = allPlaces.map(p => [p.latitude, p.longitude]);
    polyline = L.polyline(latlngs, {
      color: '#111',
      weight: 3,
      opacity: 0.7,
      smoothFactor: 1
    }).addTo(map);

    map.fitBounds(polyline.getBounds(), { padding: [50, 50] });
  } else if (allPlaces.length === 1) {
    map.setView([allPlaces[0].latitude, allPlaces[0].longitude], 13);
  }
  
  console.log(`${allPlaces.length}개 마커 표시 완료`);
}

function clearMap() {
  markers.forEach(m => map.removeLayer(m));
  markers = [];

  if (polyline) {
    map.removeLayer(polyline);
    polyline = null;
  }
}

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
  const mapCard  = document.querySelector('.map-card');
  const mapEl    = document.querySelector('#map');
  if (!leftCard || !mapCard || !mapEl) return;

  const apply = () => {
    const h = mapCard.offsetHeight;
    if (h > 0) {
      leftCard.style.height = h + 'px';
    }
  };

  apply();

  const ro = new ResizeObserver(apply);
  ro.observe(mapCard);

  window.addEventListener('resize', apply);

  if (window.gildamMap && typeof window.gildamMap.on === 'function') {
    window.gildamMap.on('load', apply);
    window.gildamMap.on('resize', apply);
    window.gildamMap.on('moveend', apply);
  } else {
    setTimeout(apply, 300);
    setTimeout(apply, 800);
  }
}

document.addEventListener('DOMContentLoaded', syncLeftHeightToMap);