
function toggleBernoulliP(){
  const dist = document.getElementById("cDist").value;
  document.getElementById("cPLabel").style.display = dist === "bernoulli" ? "" : "none";
}

document.addEventListener("DOMContentLoaded", () => {
  toggleBernoulliP();
  const form = document.getElementById("cltForm");
  const canvas = document.getElementById("cChart");
  const stats = document.getElementById("cStats");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const dist = document.getElementById("cDist").value;
    const p = document.getElementById("cP").value;
    const n = document.getElementById("cN").value;
    const num = document.getElementById("cNum").value;
    const bins = document.getElementById("cBins").value;

    const params = new URLSearchParams({dist, sample_size:n, num_samples:num, bins});
    if(dist === "bernoulli") params.set("p", p);

    try{
      const data = await fetchJSON(`/api/clt?${params.toString()}`);

      stats.innerHTML = `
        <li><strong>Empirical mean:</strong> ${data.summary.empirical_mean.toFixed(4)}</li>
        <li><strong>Empirical std (of means):</strong> ${data.summary.empirical_std.toFixed(4)}</li>
        <li><strong>Theoretical mean:</strong> ${data.summary.theoretical_mean.toFixed(4)}</li>
        <li><strong>Theoretical std (of means):</strong> ${data.summary.theoretical_std_of_mean.toFixed(4)}</li>
        <li><strong>Samples:</strong> ${data.num_samples} × <strong>n</strong>=${data.sample_size}</li>
      `;

      drawHistogramWithCurve(canvas, data.buckets, data.normal_curve);
    }catch(err){
      alert("Error: " + err.message);
    }
  });

  form.dispatchEvent(new Event("submit"));
});
