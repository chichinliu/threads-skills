#!/usr/bin/env python3
"""Threads 官方 Graph API poster 範例(自建 poster,Tier 1)。

重要:本檔的端點、參數名稱與限制,是依作者對 Meta Threads API 的理解撰寫,
**尚未對照官方文件逐項驗證**(撰寫時文件網域無法連線)。第一次實際發文前,
請先讀官方文件並核對下方「API 常數」區塊的每一項:
https://developers.facebook.com/docs/threads/

用法(由 skill 呼叫,不需要手動執行):

    export THREADS_SKILLS_CUSTOM_POSTER="python /path/to/examples/threads_graph_poster.py"
    export THREADS_ACCESS_TOKEN="..."      # 長效 token,需要發文權限

介面約定(見 lib/backend_selector.py):
    argv:   <kind> <target_url>          kind 為 post 或 thread
    stdin:  JSON {"kind", "draft_text", "target_url", ...額外參數}
    stdout: JSON 結果(status、post_ids 或錯誤)
    exit:   0 成功或 dry-run;1 API 或網路失敗;2 輸入不合法(尚未發出任何東西)

行為:
- 沒有 THREADS_ACCESS_TOKEN,或設定 THREADS_POSTER_DRY_RUN=1:只驗證並印出計畫,
  不呼叫網路。
- 串文以單獨一行的 `---` 分段,每段一則,依序用 reply_to_id 串成連續貼文。
  不會自作主張替你切段:kind=thread 卻沒有 `---` 又超過 500 字元,會拒絕。
- 部分失敗:已發出的貼文會留在線上,stdout 回報 status=partially_published
  與已發佈的 id,不會重試,也不會刪除。
- 不支援:排程(scheduled_time)、多圖輪播。收到時直接拒絕,不會悄悄立刻發出。
- reply / quote 永遠不會被 skill 交給 poster;若收到,拒絕。

選用環境變數:THREADS_REPLY_CONTROL(everyone / accounts_you_follow / mentioned_only)。

安全:token 只從環境變數讀取,絕不印出;所有請求 allow_redirects=False。
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from typing import Any, Optional

import requests

# ── API 常數:第一次實際發文前,請逐項對照官方文件 ─────────────────────────
GRAPH_BASE = "https://graph.threads.net/v1.0"
USER_ID = "me"                 # 也可改成數字 user id
MAX_CHARS = 500                # 單則貼文字元上限(以 App 內計數為準)
MAX_HASHTAGS = 1               # Threads 每則只允許 1 個主題標籤
VALID_REPLY_CONTROL = {"everyone", "accounts_you_follow", "mentioned_only"}
CONTAINER_POLL_SECONDS = 2
CONTAINER_POLL_TIMEOUT = 60
# ───────────────────────────────────────────────────────────────────────────

SEPARATOR = re.compile(r"(?m)^[ \t]*---[ \t]*$")
HASHTAG = re.compile(r"(?<!\S)#\S+")


class InputError(Exception):
    """輸入不合法,尚未發出任何東西。"""


class ApiError(Exception):
    """Graph API 或網路錯誤。訊息不得包含 token。"""


def split_posts(kind: str, text: str) -> list[str]:
    parts = [p.strip() for p in SEPARATOR.split(text)]
    parts = [p for p in parts if p]
    if not parts:
        raise InputError("草稿是空的")
    if kind == "post" and len(parts) > 1:
        raise InputError("kind=post 但草稿含有 `---` 分段;請改用 thread")
    return parts


def validate(posts: list[str]) -> None:
    for i, text in enumerate(posts, 1):
        if len(text) > MAX_CHARS:
            raise InputError(
                f"第 {i} 則有 {len(text)} 字元,超過 {MAX_CHARS}。請縮短,或用 `---` 自行分段")
        tags = HASHTAG.findall(text)
        if len(tags) > MAX_HASHTAGS:
            raise InputError(f"第 {i} 則有 {len(tags)} 個主題標籤,Threads 每則只允許 {MAX_HASHTAGS} 個")


def check_extras(payload: dict) -> Optional[str]:
    """回傳單張圖片網址(若有);遇到不支援的參數就拒絕。"""
    if payload.get("scheduled_time"):
        raise InputError("Threads API 沒有排程功能,本 poster 不支援 scheduled_time;"
                         "請拿掉它,或在你自己的排程器於時間到時才呼叫")
    media = payload.get("media_urls") or []
    if len(media) > 1:
        raise InputError("本範例只支援 1 張圖片(附在第 1 則);輪播請自行擴充")
    if media:
        if not str(media[0]).startswith("https://"):
            raise InputError("media_urls 必須是公開可存取的 https 網址")
        return str(media[0])
    return None


def _request(method: str, path: str, token: str, fields: dict[str, Any]) -> dict:
    url = f"{GRAPH_BASE}/{path}"
    try:
        if method == "GET":
            resp = requests.get(url, params={**fields, "access_token": token},
                                timeout=30, allow_redirects=False)
        else:
            resp = requests.post(url, data={**fields, "access_token": token},
                                 timeout=30, allow_redirects=False)
    except requests.RequestException as exc:
        raise ApiError(f"網路錯誤:{type(exc).__name__}") from None
    try:
        body = resp.json()
    except ValueError:
        body = {}
    if resp.status_code >= 300 or "error" in body:
        err = body.get("error", {}) if isinstance(body, dict) else {}
        msg = err.get("message") or f"HTTP {resp.status_code}"
        raise ApiError(f"{msg} (code={err.get('code')}, http={resp.status_code})")
    return body


def create_container(token: str, text: str, reply_to: Optional[str],
                     image_url: Optional[str], reply_control: Optional[str]) -> str:
    fields: dict[str, Any] = {"media_type": "IMAGE" if image_url else "TEXT", "text": text}
    if image_url:
        fields["image_url"] = image_url
    if reply_to:
        fields["reply_to_id"] = reply_to
    if reply_control and not reply_to:       # 回覆權限只設在串文第 1 則
        fields["reply_control"] = reply_control
    body = _request("POST", f"{USER_ID}/threads", token, fields)
    if "id" not in body:
        raise ApiError("建立 container 的回應沒有 id")
    return str(body["id"])


def wait_until_ready(token: str, container_id: str) -> None:
    deadline = time.monotonic() + CONTAINER_POLL_TIMEOUT
    while time.monotonic() < deadline:
        body = _request("GET", container_id, token, {"fields": "status,error_message"})
        status = body.get("status")
        if status == "FINISHED":
            return
        if status in ("ERROR", "EXPIRED"):
            raise ApiError(f"container 狀態 {status}:{body.get('error_message', '')}")
        time.sleep(CONTAINER_POLL_SECONDS)
    raise ApiError("等待 container 處理逾時")


def publish_container(token: str, container_id: str) -> str:
    body = _request("POST", f"{USER_ID}/threads_publish", token, {"creation_id": container_id})
    if "id" not in body:
        raise ApiError("發佈的回應沒有 id")
    return str(body["id"])


def permalink(token: str, post_id: str) -> Optional[str]:
    try:
        return _request("GET", post_id, token, {"fields": "permalink"}).get("permalink")
    except ApiError:
        return None


def run(kind: str, payload: dict, token: Optional[str], dry_run: bool) -> tuple[int, dict]:
    if kind not in ("post", "thread"):
        return 2, {"status": "rejected", "error": f"不支援 kind={kind!r};回覆與引用請手動貼上"}
    try:
        posts = split_posts(kind, str(payload.get("draft_text", "")))
        validate(posts)
        image_url = check_extras(payload)
        reply_control = os.getenv("THREADS_REPLY_CONTROL") or None
        if reply_control and reply_control not in VALID_REPLY_CONTROL:
            raise InputError(f"THREADS_REPLY_CONTROL 必須是 {sorted(VALID_REPLY_CONTROL)}")
    except InputError as exc:
        return 2, {"status": "rejected", "error": str(exc)}

    if dry_run or not token:
        return 0, {
            "status": "dry_run",
            "reason": "THREADS_POSTER_DRY_RUN=1" if dry_run else "沒有設定 THREADS_ACCESS_TOKEN",
            "posts": [{"index": i, "chars": len(t), "text": t} for i, t in enumerate(posts, 1)],
            "image_url": image_url,
            "reply_control": reply_control,
        }

    published: list[str] = []
    prev: Optional[str] = None
    try:
        for i, text in enumerate(posts):
            image = image_url if i == 0 else None
            container = create_container(token, text, prev, image, reply_control)
            if image:
                wait_until_ready(token, container)
            prev = publish_container(token, container)
            published.append(prev)
    except ApiError as exc:
        status = "partially_published" if published else "failed"
        return 1, {"status": status, "error": str(exc), "failed_index": len(published) + 1,
                   "post_ids": published}
    return 0, {"status": "published", "post_ids": published,
               "permalink": permalink(token, published[0])}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(json.dumps({"status": "rejected", "error": "用法:<kind> <target_url>,草稿由 stdin 的 JSON 提供"},
                         ensure_ascii=False))
        return 2
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        print(json.dumps({"status": "rejected", "error": "stdin 不是合法的 JSON"}, ensure_ascii=False))
        return 2
    code, result = run(argv[1], payload, os.getenv("THREADS_ACCESS_TOKEN"),
                       os.getenv("THREADS_POSTER_DRY_RUN") == "1")
    print(json.dumps(result, ensure_ascii=False))
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
