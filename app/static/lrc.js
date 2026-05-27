/** LRC 解析与播放同步工具（前台/后台共用） */

export const LYRIC_PLACEHOLDER = "当前暂无歌词同步显示";

const LRC_TIME_TAG_RE = /\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\]/g;

function timestampToMs(minutes, seconds, frac) {
  let ms = minutes * 60_000 + seconds * 1_000;
  if (frac == null || frac === "") return ms;
  const digits = String(frac).trim();
  if (digits.length === 2) return ms + parseInt(digits, 10) * 10;
  if (digits.length === 3) return ms + parseInt(digits, 10);
  return ms + parseInt(digits.padEnd(2, "0").slice(0, 2), 10) * 10;
}

/** 客户端 fallback：解析 LRC 文本 */
export function parseLrc(text) {
  const entries = [];
  for (const rawLine of String(text || "").split(/\r?\n/)) {
    const line = rawLine.trim();
    if (!line) continue;
    const tags = [...line.matchAll(LRC_TIME_TAG_RE)];
    if (!tags.length) continue;
    const lyricText = line.replace(LRC_TIME_TAG_RE, "").trim();
    for (const m of tags) {
      entries.push({
        time_ms: timestampToMs(parseInt(m[1], 10), parseInt(m[2], 10), m[3]),
        text: lyricText,
      });
    }
  }
  entries.sort((a, b) => a.time_ms - b.time_ms);
  return entries;
}

/** 按播放时间（毫秒）取当前行文本 */
export function findLyricLineAtTime(lines, timeMs) {
  if (!lines?.length) return "";
  const t = Number(timeMs) || 0;
  let current = "";
  for (const line of lines) {
    if (line.time_ms <= t) current = line.text || "";
    else break;
  }
  return current;
}

/** 从 API 加载歌词；无歌词返回 null。requestFn 为 async (path) => data */
export async function loadSongLyricsViaRequest(requestFn, songId) {
  try {
    const data = await requestFn(`/songs/${songId}/lyrics`);
    const lines = Array.isArray(data.lines) && data.lines.length ? data.lines : parseLrc(data.content || "");
    return {
      filename: data.filename || "",
      content: data.content || "",
      lines,
    };
  } catch (err) {
    const msg = String(err?.message || "");
    if (msg.includes("404") || msg.includes("暂无歌词") || msg.includes("not found")) return null;
    return null;
  }
}
