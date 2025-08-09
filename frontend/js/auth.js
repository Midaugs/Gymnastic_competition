import { api, setToken } from "./api.js";

// LOGIN
const loginForm = document.getElementById("login-form");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    // OAuth2PasswordRequestForm expects x-www-form-urlencoded
    const body = new URLSearchParams();
    body.append("username", formData.get("username"));
    body.append("password", formData.get("password"));

    const res = await fetch("http://127.0.0.1:8000/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) return alert("Invalid credentials");
    const data = await res.json();
    setToken(data.access_token);
    window.location.href = "dashboard.html";
  });
}

// REGISTER
const regForm = document.getElementById("register-form");
if (regForm) {
  regForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const payload = {
      username: regForm.username.value,
      name: regForm.name.value,
      surname: regForm.surname.value,
      birthday: regForm.birthday.value,
      level: regForm.level.value,
      password: regForm.password.value,
    };
    try {
      await api("/register/", { method: "POST", body: payload, auth: false });
      alert("Registered! You can log in now.");
      window.location.href = "login.html";
    } catch (err) {
      alert("Registration failed: " + err.message);
    }
  });
}
