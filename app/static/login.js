function getApiUrl(path) {
  const base = window.location.origin;
  return `${base}${path.startsWith("/") ? path : `/${path}`}`;
}

function safeNextPath() {
  const params = new URLSearchParams(window.location.search);
  const next = params.get("next") || "/";
  if (!next.startsWith("/") || next.startsWith("//")) return "/";
  if (next.startsWith("/login")) return "/";
  return next;
}

function initPasswordToggles(container) {
  if (!container) return;
  container.querySelectorAll(".password-input").forEach((wrap) => {
    const input = wrap.querySelector("input");
    const btn = wrap.querySelector(".password-toggle");
    if (!input || !btn || btn.dataset.bound === "1") return;
    btn.dataset.bound = "1";
    btn.addEventListener("click", () => {
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      btn.setAttribute("aria-pressed", show ? "true" : "false");
      btn.setAttribute("aria-label", show ? "隐藏密码" : "显示密码");
      btn.classList.toggle("password-toggle--visible", show);
    });
  });
}

document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const errEl = document.getElementById("loginError");
  const btn = e.target.querySelector(".login-submit");
  const username = document.getElementById("loginUsername")?.value?.trim();
  const password = document.getElementById("loginPassword")?.value || "";
  if (!username || !password) return;
  errEl?.classList.add("hidden");
  if (btn) btn.disabled = true;
  try {
    const res = await fetch(getApiUrl("/auth/login"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password }),
    });
    if (!res.ok) {
      let msg = "用户名或密码错误";
      try {
        const data = await res.json();
        if (data.detail) msg = typeof data.detail === "string" ? data.detail : msg;
      } catch {
        /* ignore */
      }
      if (errEl) {
        errEl.textContent = msg;
        errEl.classList.remove("hidden");
      }
      return;
    }
    window.location.href = safeNextPath();
  } catch {
    if (errEl) {
      errEl.textContent = "无法连接服务器";
      errEl.classList.remove("hidden");
    }
  } finally {
    if (btn) btn.disabled = false;
  }
});

initPasswordToggles(document.getElementById("loginForm"));
