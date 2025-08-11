
// Tiny helper utilities
function $(sel, root=document){ return root.querySelector(sel); }
function $all(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

async function fetchJSON(url){
  const res = await fetch(url, {headers: {"Accept": "application/json"}});
  if(!res.ok){
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  return res.json();
}

// Resize-aware canvas scaling for crisp lines
function prepCanvas(canvas){
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = Math.max(300, Math.floor(rect.width * dpr));
  canvas.height = Math.max(200, Math.floor(rect.height * dpr));
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return ctx;
}

// Simple number formatting
function fmt(x, digits=4){
  if (Number.isInteger(x)) return x.toString();
  return Number(x).toLocaleString(undefined, {maximumFractionDigits: digits});
}
