
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("benfordForm");
  const canvas = document.getElementById("bdChart");
  const stats = document.getElementById("bdStats");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const gen = document.getElementById("bdGen").value;
    const n = document.getElementById("bdN").value;

    try{
      const data = await fetchJSON(`/api/benford?generator=${encodeURIComponent(gen)}&n=${encodeURIComponent(n)}`);
      const labels = Array.from({length:9}, (_,i)=> (i+1).toString());
      const observed = labels.map(d => data.counts[d] || 0);
      const expected = labels.map(d => (data.expected[d] || 0) * data.n);

      stats.innerHTML = `
        <li><strong>Samples used:</strong> ${data.n}</li>
        <li><strong>Chi-square vs. Benford:</strong> ${data.chi_square.toFixed(2)}</li>
      `;

      drawBarChart(canvas, labels, [
        { name: "Observed", values: observed, color: "#6366f1" },
        { name: "Expected", values: expected, color: "#10b981" }
      ]);
    }catch(err){
      alert("Error: " + err.message);
    }
  });

  form.dispatchEvent(new Event("submit"));
});
