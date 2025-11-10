// 간단 fetch 래퍼
export async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const txt = await res.text().catch(()=> "");
    throw new Error(`API ${res.status}: ${txt}`);
  }
  return await res.json();
}
