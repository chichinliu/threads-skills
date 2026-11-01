"""Approval gate helpers.

每個會發佈到 Threads 的 skill,都必須先把草稿給使用者看,等到明確核准,
才能呼叫發佈層(`lib.publish`)。這個檔案只是格式慣例,不是執行期強制。 Skills call `render_approval_card` to format
the draft consistently and then stop until the user says go.
"""
from __future__ import annotations
from typing import Optional


def render_approval_card(
    *,
    kind: str,  # "post" | "thread" | "reply" | "quote"
    preview_text: str,
    target_url: Optional[str] = None,
    char_count: Optional[int] = None,
    post_count: Optional[int] = None,
    extra_context: Optional[dict] = None,
) -> str:
    """Format a standardized approval card for the user to review.

    The card MUST contain:
    - What the action is (post / thread / reply / quote)
    - The full preview text
    - Char count, and post count for multi-post threads
    - Target URL if applicable (the post being replied to / quoted)
    - A clear prompt: "回覆 發佈 / yes,或提出修改"
    """
    lines = [f"## 草稿待核准 - {kind}", ""]
    if target_url:
        lines.append(f"**目標:** {target_url}")
    if char_count is None:
        char_count = len(preview_text)
    lines.append(f"**字元數:** {char_count}")
    if post_count is not None:
        lines.append(f"**則數:** {post_count}")
    lines.append("")
    lines.append("**預覽:**")
    lines.append("")
    for pl in preview_text.splitlines() or [""]:
        lines.append(f"> {pl}")
    lines.append("")
    if extra_context:
        lines.append("**背景:**")
        for k, v in extra_context.items():
            lines.append(f"- **{k}**: {v}")
        lines.append("")
    lines.append("回覆 **發佈** 或 **yes** 即可進行,或告訴我要修改的地方。")
    return "\n".join(lines)
