// estimation.js – gère le formulaire d'estimation et affiche le résultat

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("estimate-form");
  const resultDiv = document.getElementById("estimate-result");

  form.addEventListener("submit", async e => {
    e.preventDefault();
    resultDiv.textContent = "Envoi de votre demande…";

    const data = {
      email: form.email.value.trim(),
      marque: form.marque.value.trim(),
      modele: form.modele.value.trim(),
      annee: parseInt(form.annee.value, 10),
      kilometrage: parseInt(form.kilometrage.value, 10),
      energie: form.energie.value,
    };

    try {
      const res = await Api.estimation.createRequest(data);
      resultDiv.textContent = res.message
        || "Votre demande est prise en compte, vous recevrez votre estimation par mail.";
      form.reset();
    } catch (err) {
      resultDiv.textContent = err.message;
    }
  });
});