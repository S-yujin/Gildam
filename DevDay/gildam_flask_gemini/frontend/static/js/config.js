// /static/js/config.js  (ESM)
window.DATASET_URL = '/static/data/busan_data.csv';

window.LLM_CONFIG = {
  provider: 'gemini',
  model: 'gemini-2.5-flash',
  endpoint: (m) => `https://generativelanguage.googleapis.com/v1beta/models/${m}:generateContent`,
  useProxy: false,
  proxyURL: '/api/generate',
  key: '', // 필요 시 키 입력
  preTopK: 140,
  maxItemsPerDay: 4,
  responseMimeType: 'application/json',

  //itinerary.html에서 쓰고 있으니 경로 지정
  blacklistCsv: '/static/data/blacklist.csv'
};