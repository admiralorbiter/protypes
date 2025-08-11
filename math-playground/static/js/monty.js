
document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("montyForm");
  const stats = document.getElementById("mStats");
  const canvas = document.getElementById("mChart");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const trials = document.getElementById("mTrials").value;

    const url = `/api/monty?strategy=both&trials=${encodeURIComponent(trials)}`;
    try{
      const data = await fetchJSON(url);
      stats.innerHTML = `
        <li><strong>Stay:</strong> ${(data.stay*100).toFixed(2)}%</li>
        <li><strong>Switch:</strong> ${(data.switch*100).toFixed(2)}%</li>
        <li><strong>Trials:</strong> ${data.trials}</li>
      `;
      drawBarChart(canvas, ["Stay", "Switch"], [
        { name: "Win rate (%)", values: [data.stay*100, data.switch*100] }
      ]);
    }catch(err){
      alert("Error: " + err.message);
    }
  });

  form.dispatchEvent(new Event("submit"));
});
