document.getElementById("fetchBtn").addEventListener("click", async () => {
  const battery = parseInt(document.getElementById("battery").value);
  const temp = parseFloat(document.getElementById("temp").value);

  if (isNaN(battery) || isNaN(temp)) {
    alert("Please enter both battery and temperature values.");
    return;
  }

  try {
    const res = await fetch("http://127.0.0.1:9000/forecast");
    const data = await res.json();
    const weather = data.weather || "Clouds"; // fallback
    document.getElementById("weather").textContent = weather;

    let strategy = "";

    if (battery < 30) {
      strategy = "Battery critically low. Charge up to 40% minimum.";
    } else if (weather === "Clear") {
      strategy = "Sunny 🌞 → Limit charging to 30%, rely on solar energy.";
    } else if (weather === "Clouds" || weather === "Mist" || weather === "Fog") {
      strategy = "Cloudy ☁️ → Charge up to 70% for safe GPS operation.";
    } else if (weather === "Rain" || weather === "Drizzle" || weather === "Thunderstorm") {
      strategy = "Rainy 🌧️ → Charge up to 80% using stored power sources.";
    } else {
      strategy = "Unknown weather → Default to 60% charge.";
    }

    document.getElementById("strategy").textContent = strategy;

  } catch (err) {
    console.error(err);
    alert("Failed to fetch weather data from backend.");
  }
});
