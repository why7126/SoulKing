export const APP_VERSION = "v0.0.6";

/** 写入侧栏品牌区版本角标，并同步 document.title（若尚未包含版本）。 */
export function applyAppVersion() {
  const el = document.getElementById("appBrandVersion");
  if (el) {
    el.textContent = APP_VERSION;
    el.setAttribute("aria-label", `版本 ${APP_VERSION}`);
  }
  if (document.title && !document.title.includes(APP_VERSION)) {
    document.title = document.title.replace(/^SoulKing\b/, `SoulKing ${APP_VERSION}`);
  }
}
