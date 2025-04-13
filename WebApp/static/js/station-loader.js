// Load and populate all dropdown station selectors on page load
export async function loadStations() {
  const dropdownIds = [
    "quick-start-station",
    "quick-destination-station",
    "plan-start-station",
    "plan-destination-station"
  ];

  try {
    // Fetch station data from backend API
    const stations = await fetch("/api/stations").then(res => res.json());

    // Loop through each dropdown and populate with options
    dropdownIds.forEach(id => {
      const select = document.getElementById(id);
      if (select) {
        select.innerHTML = "";

        // Add default placeholder option
        const placeholder = document.createElement("option");
        placeholder.value = "";
        placeholder.textContent = id.includes("destination") ? "Select Destination" : "Select Start Station";
        placeholder.disabled = true;
        placeholder.selected = true;
        select.appendChild(placeholder);

        // Add actual station options
        stations.forEach(station => {
          const option = document.createElement("option");
          option.value = station.number;
          option.textContent = station.name;
          select.appendChild(option);
        });
      }
    });

  } catch (error) {
    console.error("Failed to load stations:", error);
  }
}

// Automatically load stations once DOM is ready
document.addEventListener("DOMContentLoaded", loadStations);
