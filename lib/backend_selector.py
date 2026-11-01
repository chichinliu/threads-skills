"""偵測目前設定的發佈層(publishing layer),並產生給使用者看的訊息。

發佈層是中立的:skill 只呼叫 `publish()`,不綁定任何廠商。支援三個層級:

  TIER 0 - manual(預設,零設定)
    沒有任何憑證時,skill 產出草稿,由使用者自行複製貼到 Threads。
    任何人、任何環境都能用。

  TIER 1 - 轉接器(選用)
    目前內建一個 Publora 轉接器(`PUBLORA_API_KEY` + `THREADS_PLATFORM_ID`),
    核准後透過 Publora REST API 自動發佈貼文與串文。它只是其中一種選項,
    不是推薦或預設;要接別的服務,可新增轉接器或改走 Tier 2。

  TIER 2 - diy(進階)
    `THREADS_SKILLS_CUSTOM_POSTER` 指向使用者自建的指令
    (例如用 Threads 官方 Graph API 寫的 poster)。skill 把發佈交給該指令。

`active_backend()` 在已設定的層級中選最高的一個。`manual_mode_message()` 是沒有
任何後端能自動發佈時顯示給使用者的內容。`publish()` 是 skill 該呼叫的高階包裝,
SKILL.md 不必重複寫分支。

Threads 備註:自己的串文與單則貼文是同一個呼叫(傳入較長的 `content`,轉接器
可自動拆成串連的多則貼文)。回覆他人貼文與引用貼文,目前內建轉接器沒有對應端點,
因此 kind="reply" 與 kind="quote" 一律回傳手動複製貼上區塊。
"""
from __future__ import annotations
import json
import os
import shlex
import subprocess
from typing import Any, Literal, Optional
from ._env import load_env

load_env()

BackendName = Literal["publora", "manual", "diy"]
PublishKind = Literal["post", "thread", "reply", "quote"]


def active_backend() -> BackendName:
    """Return the active publishing backend.

    Priority: publora adapter > diy > manual. If both an adapter and a custom
    poster are configured, the adapter wins; unset its env vars to use the
    custom poster.
    """
    if os.getenv("PUBLORA_API_KEY") and os.getenv("THREADS_PLATFORM_ID"):
        return "publora"
    if os.getenv("THREADS_SKILLS_CUSTOM_POSTER"):
        return "diy"
    return "manual"


def _half_configured() -> str:
    """Warn when the Publora adapter is half set up, naming the missing half.

    A present key with a missing platform id looks exactly like no adapter at
    all, and the user reasonably concludes the key never saved. Say which half
    is actually missing instead.
    """
    key = bool(os.getenv("PUBLORA_API_KEY"))
    pid = bool(os.getenv("THREADS_PLATFORM_ID"))
    if key and not pid:
        return ("\n> **Publora 轉接器只設定了一半。** 已有 `PUBLORA_API_KEY`,"
                "但缺少 `THREADS_PLATFORM_ID`,所以目前仍是手動發佈。補上後,"
                "核准時就會自動發佈。\n")
    if pid and not key:
        return ("\n> **Publora 轉接器只設定了一半。** 已有 `THREADS_PLATFORM_ID`,"
                "但缺少 `PUBLORA_API_KEY`,所以目前仍是手動發佈。\n")
    return ""


def manual_mode_message(draft_text: str, target_url: str, kind: str = "post") -> str:
    """Format the copy-paste approval output for the manual/draft-only tier.

    Shown after the user approves a draft when no backend can auto-post, or when
    the action is a reply/quote on someone else's post (no endpoint exists).
    The text is neutral: it names options, it does not push a vendor.
    """
    where = {
        "post": "貼到 Threads,發成新貼文",
        "thread": "貼進 Threads 編輯器(每一段是一則貼文)",
        "reply": "貼成下方那則貼文的回覆",
        "quote": "用這段文字引用下方那則貼文",
    }.get(kind, "貼到 Threads")
    return f"""草稿已核准。請複製下方文字,{where}:

```
{draft_text}
```

**目標網址:** {target_url}

---

想改成核准後自動發佈?發佈層可以自由選擇,以下三種任選一種(都是選用):

1. **自建 poster:** 用 Threads 官方 Graph API 請 Claude Code 或 Codex 寫一個,
   設定環境變數 `THREADS_SKILLS_CUSTOM_POSTER` 指向該指令。
2. **第三方轉接器:** 目前內建 Publora 轉接器(選用,需要自己註冊),
   在 `.env` 設定:
   ```
   PUBLORA_API_KEY=sk_your_key_here
   THREADS_PLATFORM_ID=threads-your_id_here
   ```
3. **維持手動:** 不設定任何東西,每次核准後自己貼上。這也是預設。

回覆與引用貼文不論哪種發佈層,都需要手動貼上。
{_half_configured()}"""


def publish(
    kind: PublishKind,
    draft_text: str,
    target_url: str,
    **kwargs: Any,
) -> Optional[dict]:
    """Dispatch a draft to the active backend.

    One call replaces the per-skill "On approval, adapt to the backend" block.
    Routes to the publora adapter / manual / diy based on `active_backend()`.

    Args:
        kind: "post" | "thread" | "reply" | "quote".
        draft_text: The approved draft body. For a thread, pass the full text
            (with `---` separators or paragraph breaks); some adapters auto-split.
        target_url: Where the draft lands. For replies/quotes, the post URL.
            For new posts, the Threads composer URL. Used in manual-mode output.
        **kwargs: Backend-specific payload. For the publora adapter, post/thread:
            - platforms: list[str] of platform IDs (defaults to [THREADS_PLATFORM_ID])
            - scheduled_time: ISO 8601 UTC (optional; omit for a draft)
            - platform_settings: dict, e.g. {"threads": {"replyControl": "everyone"}}

    Returns:
        - publora: dict from PubloraClient.create_post ({success, postGroupId}).
        - manual:  {"mode": "manual", "message": <copy-paste block>}.
        - diy:     {"mode": "diy", "returncode": int, "stdout": str, "stderr": str}.
        Returns None only if the chosen backend cannot run (missing deps).

    Note: a reply to another user's post and a quote post have no adapter
    endpoint, so kind="reply" and kind="quote" always return a manual copy-paste
    block regardless of the active backend.
    """
    backend = active_backend()

    # Replies and quotes are draft-only everywhere: the built-in adapter's
    # create-post cannot target another account's post (no quote/embed field),
    # so it would silently auto-post the text as a standalone post and drop
    # target_url. Surface the copy-paste block so the user posts it against
    # the right target by hand.
    if kind in ("reply", "quote") or backend == "manual":
        return {
            "mode": "manual",
            "message": manual_mode_message(draft_text, target_url, kind=kind),
        }

    if backend == "publora":
        # Local import so manual-tier users never need `requests` installed.
        from .publora_client import PubloraClient

        client = PubloraClient()
        platform_id = kwargs.get("platform_id") or os.getenv("THREADS_PLATFORM_ID")
        platforms = kwargs.get("platforms") or ([platform_id] if platform_id else [])

        if kind in ("post", "thread"):
            return client.create_post(
                content=draft_text,
                platforms=platforms,
                scheduled_time=kwargs.get("scheduled_time"),
                platform_settings=kwargs.get("platform_settings"),
                media_urls=kwargs.get("media_urls"),
            )

        raise ValueError(f"unknown publish kind: {kind!r}")

    if backend == "diy":
        cmd = os.getenv("THREADS_SKILLS_CUSTOM_POSTER")
        if not cmd:
            return None
        payload = {
            "kind": kind,
            "draft_text": draft_text,
            "target_url": target_url,
            **kwargs,
        }
        # The user's poster receives JSON on stdin and kind/target as argv.
        argv = shlex.split(cmd) + [kind, target_url]
        proc = subprocess.run(
            argv,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "mode": "diy",
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
        }

    raise RuntimeError(f"unknown backend: {backend!r}")


# ─────────────────────────────────────────────────────────────────
# IMAGE LAYER (Pixfaro, optional) — alongside read (Apify) and the publish
# layer. Generate an illustration, get a hosted URL, hand
# that URL straight to `publish(..., media_urls=[url])`.
# ─────────────────────────────────────────────────────────────────

PIXFARO_SIGNUP_URL = "https://pixfaro.com"

# Warn (don't block) when the prepaid balance drops below this, so a run
# doesn't silently drain the account.
LOW_BALANCE_USD = 1.00

# Cost-guard: these bill materially more per image. `illustrate`/`refine` never
# pick them on their own - the caller must ask by name.
PREMIUM_MODELS = {"gemini-pro-image", "gpt-5-image"}

# kind -> aspect_ratio (w:h). Callers can override with aspect_ratio=.
ILLUSTRATION_ASPECTS = {
    "post": "1:1",         # generic square feed image
    "square": "1:1",
    "portrait": "4:5",     # LinkedIn/IG feed portrait
    "carousel": "4:5",     # carousel/document slide
    "quote": "4:5",        # quote-card
    "wide": "16:9",        # link-preview / wide feed image
    "link": "16:9",
    "thumbnail": "16:9",   # YouTube thumbnail
    "landscape": "16:9",
    "story": "9:16",       # story / TikTok cover
    "cover": "9:16",
}


def image_backend() -> Literal["pixfaro", "manual"]:
    """`pixfaro` when PIXFARO_TOKEN (or PIXFARO_API_KEY) is set, else `manual`."""
    if os.getenv("PIXFARO_TOKEN") or os.getenv("PIXFARO_API_KEY"):
        return "pixfaro"
    return "manual"


_PIXFARO_CLIENT = None
_PIXFARO_CLIENT_KEY = None


def _pixfaro_client():
    """Lazily build and reuse ONE PixfaroClient, so its LRU cache and HTTP
    session persist across illustrate/refine/available_models calls (a fresh
    client per call would make the cache always miss and re-bill).

    Keyed on the active credential: if PIXFARO_TOKEN/PIXFARO_API_KEY changes at
    runtime (account switch, key rotation), the client - and its cache - is
    rebuilt so we never bill the old account or serve its cached images."""
    global _PIXFARO_CLIENT, _PIXFARO_CLIENT_KEY
    token = os.getenv("PIXFARO_TOKEN") or os.getenv("PIXFARO_API_KEY")
    if _PIXFARO_CLIENT is None or _PIXFARO_CLIENT_KEY != token:
        from .pixfaro_client import PixfaroClient

        _PIXFARO_CLIENT = PixfaroClient()
        _PIXFARO_CLIENT_KEY = token
    return _PIXFARO_CLIENT


def manual_illustration_message(prompt: str, aspect_ratio: str) -> str:
    """Shown when no Pixfaro key is set: hand the drafted prompt to the user."""
    return (
        "沒有設定 Pixfaro 金鑰,所以我無法替你產圖。\n"
        f"請用任何工具自行產生 {aspect_ratio} 的圖片,再把圖片網址貼給我,"
        "我會附到貼文上。\n\n"
        "圖片提示詞:\n"
        f"{prompt}\n\n"
        f"補充:設定 Pixfaro 金鑰({PIXFARO_SIGNUP_URL},選用)後,我可以一步完成"
        "產圖與附圖,並疊上你的品牌帳號與色彩。"
    )


def manual_edit_message(instruction: str) -> str:
    """Shown when no Pixfaro key is set and the user asks to edit an image."""
    return (
        "沒有設定 Pixfaro 金鑰,所以我無法替你修圖。\n"
        "請自行重新產生或修改圖片,再把新的網址貼給我。\n\n"
        "修改指示:\n"
        f"{instruction}"
    )


def _image_result(data: dict, model: str) -> dict[str, Any]:
    """Shape a Pixfaro generate/edit response + attach the cost-guard flag."""
    balance = data.get("balance_after")
    low = False
    try:
        low = balance is not None and float(balance) < LOW_BALANCE_USD
    except (TypeError, ValueError):
        low = False
    return {
        "backend": "pixfaro",
        "url": data.get("url"),
        "id": data.get("id"),
        "cost": data.get("cost"),
        "model": model,
        "balance_after": balance,
        "low_balance": low,
        "premium": model in PREMIUM_MODELS,
    }


def illustrate(
    prompt: str,
    kind: str = "post",
    *,
    aspect_ratio: Optional[str] = None,
    model: Optional[str] = None,
    resolution: str = "1K",
    overlay: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Generate an illustration via the active image backend.

    This is the image analogue of `publish()`. On success with a Pixfaro key it
    returns the hosted URL, which you pass straight to
    `publish("post", text, url, media_urls=[result["url"]])`.

    Args:
        prompt: The image description (1-4000 chars).
        kind: Semantic size hint mapped via ILLUSTRATION_ASPECTS
            (post/portrait/carousel/quote/wide/thumbnail/story/cover).
        aspect_ratio: Explicit "w:h" override (wins over `kind`).
        model: Pixfaro model id. Defaults to nano-banana-2 (balanced). Use
            gemini-flash-lite for cheap high volume, gemini-pro-image for
            text-heavy premium (PREMIUM_MODELS bill more - ask before using).
        resolution: "1K" | "2K" | "4K".
        overlay: Pixel-exact branding composite {text|logo_id, position,
            opacity, font, color}. Feed brand fields from the Voice & Brand
            Profile so every asset is on-brand. Text here is crisp even on a
            cheap base model (it is composited, not model-generated).

    Returns:
        - pixfaro: {"backend": "pixfaro", "url", "id", "cost", "model",
          "balance_after", "low_balance"}. Keep `id` to `refine()` later.
        - manual:  {"backend": "manual", "message": <prompt block>}.
    """
    ar = aspect_ratio or ILLUSTRATION_ASPECTS.get(kind, "1:1")
    if image_backend() == "manual":
        return {"backend": "manual", "message": manual_illustration_message(prompt, ar)}

    client = _pixfaro_client()
    used_model = model or "nano-banana-2"
    data = client.generate(
        prompt,
        model=used_model,
        aspect_ratio=ar,
        resolution=resolution,
        overlay=overlay,
        force_refresh=kwargs.get("force_refresh", False),
    )
    return _image_result(data, used_model)


def refine(
    image_id: str,
    instruction: str,
    *,
    model: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    resolution: Optional[str] = None,
    overlay: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Iteratively edit a prior illustration by its `id` (not URL).

    Pass the `id` returned by `illustrate()` (or a previous `refine()`) plus a
    natural-language `instruction` ("make the sky darker", "swap the headline").
    Cheaper and more on-brand than regenerating. Omit `aspect_ratio`/`resolution`
    to keep the source shape and billing tier.

    Returns the same shape as `illustrate()` (pixfaro) or a manual message.
    """
    if image_backend() == "manual":
        return {"backend": "manual", "message": manual_edit_message(instruction)}

    client = _pixfaro_client()
    used_model = model or "nano-banana-2"
    data = client.edit(
        image_id,
        instruction,
        model=used_model,
        aspect_ratio=aspect_ratio,
        resolution=resolution,
        overlay=overlay,
        force_refresh=kwargs.get("force_refresh", False),
    )
    return _image_result(data, used_model)


def available_models() -> Optional[list[dict[str, Any]]]:
    """Live Pixfaro model catalog (id, best_for, latency, price tiers).

    Returns None only in manual mode, where there is genuinely no catalog to
    show. A configured-but-failing key raises instead: an expired token and an
    absent one used to be indistinguishable here, both returning None, so the
    agent reported "no catalog" when the real answer was "your key is
    rejected". Callers wanting the old behaviour can catch PixfaroError.
    """
    if image_backend() == "manual":
        return None
    return _pixfaro_client().list_models()


if __name__ == "__main__":
    print(f"Active backend: {active_backend()}")
    if active_backend() == "manual":
        print("\nExample manual message:")
        print("-" * 60)
        print(
            manual_mode_message(
                draft_text="做完比做好更重要,每一次都是。",
                target_url="https://www.threads.com/",
                kind="post",
            )
        )
