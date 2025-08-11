
document.addEventListener("DOMContentLoaded", () => {
  console.log("DOM loaded, setting up birthday form");
  
  const form = document.getElementById("birthdayForm");
  const stats = document.getElementById("bStats");
  const canvas = document.getElementById("bChart");
  
  console.log("Form element:", form);
  console.log("Stats element:", stats);
  console.log("Canvas element:", canvas);
  
  if (!form || !stats || !canvas) {
    console.error("Required elements not found!");
    return;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log("Form submitted");
    
    const n = document.getElementById("bGroup").value;
    const trials = document.getElementById("bTrials").value;
    
    console.log("Group size:", n, "Trials:", trials);

    const url = `/api/birthday?group_size=${encodeURIComponent(n)}&trials=${encodeURIComponent(trials)}`;
    console.log("Fetching URL:", url);
    
    try{
      const data = await fetchJSON(url);
      console.log("Received data:", data);
      
      stats.innerHTML = `
        <li><strong>Group size:</strong> ${data.group_size}</li>
        <li><strong>Theoretical:</strong> ${(data.theoretical*100).toFixed(2)}%</li>
        <li><strong>Simulated:</strong> ${(data.simulated*100).toFixed(2)}% over ${data.trials} trials</li>
      `;
      
      try {
        drawBarChart(canvas, ["Theoretical", "Simulated"], [
          { name: "Probability", values: [data.theoretical*100, data.simulated*100] }
        ]);
        console.log("Chart drawn successfully");
      } catch (chartErr) {
        console.error("Chart drawing error:", chartErr);
        alert("Chart drawing error: " + chartErr.message);
      }
    }catch(err){
      console.error("Error occurred:", err);
      alert("Error: " + err.message);
    }
  });

  // Trigger initial calculation
  console.log("Triggering initial form submission");
  setTimeout(() => {
    form.dispatchEvent(new Event("submit"));
  }, 100);
});
