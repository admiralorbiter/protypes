
/**
 * Minimal chart helpers (no external libs).
 * Draws bar charts, histograms, and line charts on a canvas.
 */

function drawAxes(ctx, x, y, w, h){
  ctx.strokeStyle = "#e5e7eb";
  ctx.lineWidth = 1;
  // x-axis
  ctx.beginPath();
  ctx.moveTo(x, y+h);
  ctx.lineTo(x+w, y+h);
  ctx.stroke();
  // y-axis
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x, y+h);
  ctx.stroke();
}

function drawBarChart(canvas, labels, datasets, opts={}){
  const ctx = prepCanvas(canvas);
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const padding = {left: 46, right: 16, top: 16, bottom: 40};
  const w = canvas.clientWidth - padding.left - padding.right;
  const h = canvas.clientHeight - padding.top - padding.bottom;
  const x0 = padding.left, y0 = padding.top;

  // compute max
  let maxVal = 0;
  for(const ds of datasets){
    for(const v of ds.values){ if(v>maxVal) maxVal = v; }
  }
  maxVal = maxVal || 1;

  drawAxes(ctx, x0, y0, w, h);

  const groupCount = labels.length;
  const groupWidth = w / groupCount;
  const barWidth = Math.min(28, groupWidth * 0.35);

  const colors = ["#6366f1", "#10b981", "#ef4444", "#f59e0b"];
  ctx.save();
  ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto, Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";

  for(let i=0; i<groupCount; i++){
    const gx = x0 + i * groupWidth + groupWidth/2;
    // x labels
    ctx.fillStyle = "#6b7280";
    ctx.fillText(labels[i], gx, y0 + h + 8);

    // bars
    const totalBars = datasets.length;
    const start = gx - (totalBars * barWidth + (totalBars-1)*6)/2 + barWidth/2;
    for(let j=0; j<datasets.length; j++){
      const ds = datasets[j];
      const v = ds.values[i] || 0;
      const bh = (v / maxVal) * (h - 6);
      const bx = start + j * (barWidth + 6);
      const by = y0 + h - bh;
      ctx.fillStyle = ds.color || colors[j % colors.length];
      roundRect(ctx, bx - barWidth/2, by, barWidth, bh, 6, true, false);
    }
  }

  // y ticks (5)
  ctx.fillStyle = "#6b7280";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for(let i=0; i<=5; i++){
    const v = (maxVal * i / 5);
    const py = y0 + h - (i/5)*(h-6);
    ctx.fillText(v.toFixed(2), x0 - 8, py);
    ctx.strokeStyle = "rgba(0,0,0,0.04)";
    ctx.beginPath();
    ctx.moveTo(x0, py);
    ctx.lineTo(x0+w, py);
    ctx.stroke();
  }

  ctx.restore();
}

function drawHistogramWithCurve(canvas, buckets, curvePoints, opts={}){
  const ctx = prepCanvas(canvas);
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const padding = {left: 56, right: 16, top: 16, bottom: 40};
  const w = canvas.clientWidth - padding.left - padding.right;
  const h = canvas.clientHeight - padding.top - padding.bottom;
  const x0 = padding.left, y0 = padding.top;

  // scales
  const xMin = buckets[0].x0;
  const xMax = buckets[buckets.length-1].x1;
  let yMax = 0;
  for(const b of buckets){ if(b.count > yMax) yMax = b.count; }
  for(const p of curvePoints){ if(p.y > yMax) yMax = p.y; }
  yMax = yMax || 1;

  // axes
  drawAxes(ctx, x0, y0, w, h);

  // helper to map x,y to canvas
  const X = x => x0 + (x - xMin) / (xMax - xMin) * (w-2);
  const Y = y => y0 + h - (y / yMax) * (h - 6);

  // bars
  ctx.fillStyle = "#6366f1";
  for(const b of buckets){
    const bx0 = X(b.x0), bx1 = X(b.x1);
    const barW = Math.max(1, bx1 - bx0 - 2);
    const by = Y(b.count);
    roundRect(ctx, bx0+1, by, barW, (y0 + h - by), 4, true, false);
  }

  // curve
  ctx.strokeStyle = "#10b981";
  ctx.lineWidth = 2;
  ctx.beginPath();
  let first = true;
  for(const p of curvePoints){
    const xx = X(p.x), yy = Y(p.y);
    if(first){ ctx.moveTo(xx, yy); first=false; } else { ctx.lineTo(xx, yy); }
  }
  ctx.stroke();

  // x ticks (5)
  ctx.fillStyle = "#6b7280";
  ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto, Arial";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for(let i=0; i<=5; i++){
    const xv = xMin + (xMax - xMin) * i/5;
    const px = X(xv);
    ctx.fillText(xv.toFixed(2), px, y0 + h + 8);
  }
  // y ticks (5)
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for(let i=0; i<=5; i++){
    const yv = yMax * i/5;
    const py = Y(yv);
    ctx.fillText(yv.toFixed(0), x0 - 8, py);
    ctx.strokeStyle = "rgba(0,0,0,0.04)";
    ctx.beginPath();
    ctx.moveTo(x0, py);
    ctx.lineTo(x0+w, py);
    ctx.stroke();
  }
}

function drawLineChart(canvas, xs, ys, opts={}){
  const ctx = prepCanvas(canvas);
  ctx.clearRect(0,0,canvas.width,canvas.height);
  const padding = {left: 56, right: 16, top: 16, bottom: 40};
  const w = canvas.clientWidth - padding.left - padding.right;
  const h = canvas.clientHeight - padding.top - padding.bottom;
  const x0 = padding.left, y0 = padding.top;

  const xMin = xs[0], xMax = xs[xs.length-1];
  let yMin = Math.min(...ys);
  let yMax = Math.max(...ys);
  if (opts.yMin !== undefined) yMin = Math.min(yMin, opts.yMin);
  if (opts.yMax !== undefined) yMax = Math.max(yMax, opts.yMax);
  if (yMax === yMin){ yMax += 1; yMin -= 1; }

  drawAxes(ctx, x0, y0, w, h);

  // grid
  ctx.strokeStyle = "rgba(0,0,0,0.04)";
  for(let i=0;i<=5;i++){
    const py = y0 + h - (i/5)*(h-6);
    ctx.beginPath(); ctx.moveTo(x0,py); ctx.lineTo(x0+w,py); ctx.stroke();
  }

  const X = x => x0 + (x - xMin) / (xMax - xMin) * (w-2);
  const Y = y => y0 + h - (y - yMin) / (yMax - yMin) * (h - 6);

  // line
  ctx.strokeStyle = "#6366f1";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(X(xs[0]), Y(ys[0]));
  for(let i=1;i<xs.length;i++){
    ctx.lineTo(X(xs[i]), Y(ys[i]));
  }
  ctx.stroke();

  // optional horizontal
  if(opts.hline !== undefined){
    ctx.strokeStyle = "#10b981";
    ctx.setLineDash([6,4]);
    const py = Y(opts.hline);
    ctx.beginPath(); ctx.moveTo(x0, py); ctx.lineTo(x0+w, py); ctx.stroke();
    ctx.setLineDash([]);
  }

  // ticks
  ctx.fillStyle = "#6b7280";
  ctx.font = "12px system-ui, -apple-system, Segoe UI, Roboto, Arial";
  ctx.textAlign = "center"; ctx.textBaseline = "top";
  for(let i=0; i<=5; i++){
    const xv = xMin + (xMax - xMin) * i/5;
    const px = X(xv);
    ctx.fillText(Math.round(xv).toString(), px, y0 + h + 8);
  }
  ctx.textAlign = "right"; ctx.textBaseline = "middle";
  for(let i=0; i<=5; i++){
    const yv = yMin + (yMax - yMin) * i/5;
    const py = Y(yv);
    ctx.fillText(yv.toFixed(2), x0 - 8, py);
  }
}

function roundRect(ctx, x, y, w, h, r, fill, stroke){
  if (w<0) { x += w; w = -w; }
  if (h<0) { y += h; h = -h; }
  r = Math.min(r, Math.abs(w/2), Math.abs(h/2));
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
  if (fill) ctx.fill();
  if (stroke) ctx.stroke();
}
