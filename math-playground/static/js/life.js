
(function(){
  let cols = 80, rows = 50, speed = 120;
  let grid = [];
  let timer = null;

  const canvas = document.getElementById("lifeCanvas");
  const ctx = canvas.getContext("2d");

  function resetGrid(){
    grid = Array.from({length: rows}, () => Array(cols).fill(0));
  }
  function randomizeGrid(){
    grid = Array.from({length: rows}, () => Array.from({length: cols}, () => Math.random() < 0.2 ? 1 : 0));
  }

  function draw(){
    const w = canvas.clientWidth || canvas.width;
    const h = canvas.clientHeight || canvas.height;
    const cellW = Math.floor(w / cols);
    const cellH = Math.floor(h / rows);
    ctx.clearRect(0,0,canvas.width,canvas.height);

    // crisp scaling
    const dpr = window.devicePixelRatio || 1;
    canvas.width = Math.max(300, Math.floor(w * dpr));
    canvas.height = Math.max(200, Math.floor(h * dpr));
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    // cells
    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        if(grid[r][c]){
          ctx.fillStyle = "#111827";
          ctx.fillRect(c*cellW+1, r*cellH+1, cellW-2, cellH-2);
        }else{
          ctx.fillStyle = "#f3f4f6";
          ctx.fillRect(c*cellW+1, r*cellH+1, cellW-2, cellH-2);
        }
      }
    }
    // grid overlay
    ctx.strokeStyle = "#e5e7eb";
    ctx.lineWidth = 1;
    for(let r=0;r<=rows;r++){
      ctx.beginPath();
      ctx.moveTo(0, r*cellH);
      ctx.lineTo(cols*cellW, r*cellH);
      ctx.stroke();
    }
    for(let c=0;c<=cols;c++){
      ctx.beginPath();
      ctx.moveTo(c*cellW, 0);
      ctx.lineTo(c*cellW, rows*cellH);
      ctx.stroke();
    }
  }

  function neighbors(r, c){
    let sum = 0;
    for(let dr=-1; dr<=1; dr++){
      for(let dc=-1; dc<=1; dc++){
        if(dr===0 && dc===0) continue;
        const rr = r+dr, cc = c+dc;
        if(rr>=0 && rr<rows && cc>=0 && cc<cols){
          sum += grid[rr][cc];
        }
      }
    }
    return sum;
  }

  function step(){
    const next = Array.from({length: rows}, () => Array(cols).fill(0));
    for(let r=0;r<rows;r++){
      for(let c=0;c<cols;c++){
        const n = neighbors(r,c);
        if(grid[r][c] === 1){
          next[r][c] = (n === 2 || n === 3) ? 1 : 0;
        }else{
          next[r][c] = (n === 3) ? 1 : 0;
        }
      }
    }
    grid = next;
    draw();
  }

  // Controls
  document.getElementById("lifeStart").addEventListener("click", () => {
    if(timer) return;
    timer = setInterval(step, speed);
  });
  document.getElementById("lifePause").addEventListener("click", () => {
    if(timer){ clearInterval(timer); timer = null; }
  });
  document.getElementById("lifeStep").addEventListener("click", step);
  document.getElementById("lifeRandom").addEventListener("click", () => { randomizeGrid(); draw(); });
  document.getElementById("lifeClear").addEventListener("click", () => { resetGrid(); draw(); });

  document.getElementById("lifeCols").addEventListener("change", (e) => {
    cols = Math.max(10, Math.min(200, parseInt(e.target.value,10) || 80));
    resetGrid(); draw();
  });
  document.getElementById("lifeRows").addEventListener("change", (e) => {
    rows = Math.max(10, Math.min(200, parseInt(e.target.value,10) || 50));
    resetGrid(); draw();
  });
  document.getElementById("lifeSpeed").addEventListener("change", (e) => {
    speed = Math.max(10, Math.min(1000, parseInt(e.target.value,10) || 120));
    if(timer){ clearInterval(timer); timer = setInterval(step, speed); }
  });

  // Click to toggle
  canvas.addEventListener("click", (e) => {
    const rect = canvas.getBoundingClientRect();
    const w = canvas.clientWidth || canvas.width;
    const h = canvas.clientHeight || canvas.height;
    const cellW = Math.floor(w / cols);
    const cellH = Math.floor(h / rows);
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const c = Math.floor(x / cellW);
    const r = Math.floor(y / cellH);
    if(r>=0 && r<rows && c>=0 && c<cols){
      grid[r][c] = grid[r][c] ? 0 : 1;
      draw();
    }
  });

  // init
  resetGrid();
  draw();
})();
