document.getElementById("checkEmailBtn").addEventListener("click", () => {
  const loading = document.getElementById("loading");
  const responseContainer = document.getElementById("responseContainer");
  const responseJson = document.getElementById("responseJson");

  loading.classList.remove("hidden");
  responseContainer.classList.add("hidden");

  fetch("/revisar_correo", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      responseJson.textContent = JSON.stringify(data, null, 2);
      responseContainer.classList.remove("hidden");
    })
    .catch((error) => {
      console.error("Error:", error);
      responseJson.textContent = `Error: ${error.message}`;
      responseContainer.classList.remove("hidden");
    })
    .finally(() => {
      loading.classList.add("hidden");
    });
});
