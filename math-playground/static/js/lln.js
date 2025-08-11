
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("llnForm");
  const canvas = document.getElementById("lChart");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const p = parseFloat(document.getElementById("lP").value);
    const flips = parseInt(document.getElementById("lN").value, 10);

    try{
      const data = await fetchJSON(`/api/lln?p=${encodeURIComponent(p)}&flips=${encodeURIComponent(flips)}`);
      const ys = data.running_mean;
      const xs = ys.map((_,i)=> i+1);

      drawLineChart(canvas, xs, ys, {hline: data.p, yMin: 0, yMax: 1});
    }catch(err){
      alert("Error: " + err.message);
    }
  });

  form.dispatchEvent(new Event("submit"));
});
