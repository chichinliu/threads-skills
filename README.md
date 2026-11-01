<p align="center">
  <img src="assets/hero.png" alt="Threads 行銷 skills(繁體中文台灣版),適用 Claude Code 與 Codex,MIT 開源" width="900" />
</p>

# Threads 行銷 Skills・繁體中文台灣版

<p align="center">
  <img src="https://img.shields.io/github/v/release/chichinliu/threads-skills?color=111827&label=release" alt="Latest release">
  <img src="https://img.shields.io/badge/Claude_Code-Compatible-D97757?logo=anthropic&logoColor=white" alt="Claude Code Compatible">
  <img src="https://img.shields.io/badge/Codex-Compatible-111827" alt="Codex Compatible">
  <img src="https://img.shields.io/badge/Claude-Skills-8A63D2" alt="Claude Skills">
  <img src="https://img.shields.io/badge/License-MIT-22C55E.svg" alt="MIT License">
  <img src="https://img.shields.io/github/stars/chichinliu/threads-skills?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/badge/PRs-welcome-F59E0B.svg" alt="PRs Welcome">
</p>

> **由 [chichinliu](https://chichinliu.com) 維護。** 本專案改寫自開源的 threads-skills(MIT,原作者 Sergey Bulaev),調整為繁體中文與台灣市場,並把發佈層改為中立設計。更多 AI 與策略資源:[chichinliu.com](https://chichinliu.com)。

**8 個 skill,把 Claude Code 與 Codex 變成你的 Threads 內容團隊。** 用你的口吻寫貼文與串文、用經過驗證的鉤子公式起頭、草擬回覆、用真實資料讀懂你的利基領域,並規劃一週內容。每份草稿都會先去掉 AI 味,等你核准後才發佈。不需要寫程式。

安裝後,直接對 Claude Code 或 Codex 說:

- 「幫我寫一則 Threads 貼文,主題是 [主題]」
- 「把這些筆記整理成一串文」
- 「我的利基領域最近什麼內容有效?(用 Apify 讀真實資料)」
- 「把這篇改得像真人寫的」

對的 skill 會自動啟動。然後由你檢視、核准。

## 這個版本和原版的差異

| 面向 | 原版 | 這個版本 |
|---|---|---|
| 語言 | 英文 | 繁體中文、台灣用語 |
| 語氣規則 | 英文 AI 詞彙、破折號密度、小寫句首 | 中文 AI 腔詞表、全形標點、中英間距、語氣詞、台灣用語 |
| 發佈層 | 以單一第三方服務為預設推薦 | **不綁定任何服務**:預設手動貼上,進階使用者可接自建 poster |
| 在地情境 | 無 | 台灣時段、節慶節點、常見搬運來源(標示為待驗證假設) |

> 凡標示「假設」的時段、字數、節慶效果,都是起點,不是平台保證。請用自己帳號的洞察數據校正。

## 安裝

選一種你平常使用 Claude Code 或 Codex 的方式:

### Codex CLI

```bash
codex plugin marketplace add chichinliu/threads-skills
codex plugin add threads-skills@threads-skills
```

### claude.ai(網頁)

1. 開啟 https://claude.ai/code
2. 側邊欄進入 **Skills**
3. 點 **Add from GitHub**
4. 貼上:`chichinliu/threads-skills`
5. 完成。問到 Threads 時,skill 會自動啟動。

### Claude Desktop(Mac / Windows)

1. 開啟 Claude Desktop,進入 **Settings**
2. 進入 **Skills**,點 **Add from GitHub**
3. 貼上:`chichinliu/threads-skills`
4. 開新對話,請 Claude 寫一則 Threads 貼文。

### Claude Code(CLI / VS Code / JetBrains)

```
/plugin marketplace add chichinliu/threads-skills
/plugin install threads-skills@threads-skills
```

或直接 clone 後把資料夾當作工作目錄:

```bash
git clone https://github.com/chichinliu/threads-skills.git
cd threads-skills
```

### 其他 agent(skills CLI)

```bash
npx skills add chichinliu/threads-skills
```

> **覺得有用嗎?** 歡迎到 [GitHub](https://github.com/chichinliu/threads-skills) 給顆星,也歡迎來 [chichinliu.com](https://chichinliu.com) 看更多 AI 與策略資源。不需要註冊,也不用留 email。

## 你可以做什麼

安裝後,直接請 Claude Code 或 Codex 協助處理 Threads,對的 skill 會自動啟動。

**寫一則貼文:**
> 「幫我寫一則 Threads 貼文,講為什麼多數 AI agent 壞在重試而不是推理。語氣溫暖一點。」

**把想法變成串文:**
> 「把我的筆記整理成 Threads 串文:我們怎麼把 agent 延遲從 9 秒降到 2.1 秒。」

**發佈前檢查:**
> 「幫我審這則 Threads 貼文有沒有 AI 腔、有沒有超過 500 字元:[貼上文字]」

**拆解爆文:**
> 「這則用了什麼鉤子?https://www.threads.com/@someone/post/abc(文字我貼給你)」

**回覆創作者:**
> 「幫我草擬回覆,我想加值而不是嗆:https://www.threads.com/@someone/post/abc」

**規劃一週:**
> 「幫我規劃一週的 Threads 內容。我在公開打造一個給獨立開發者的 AI agent。」

每個 skill 都會先給你看草稿,等你同意。沒有你的核准,什麼都不會發出去。

## 8 個 skill

| Skill | 功能 |
|---|---|
| **Post Writer(`threads-post-writer`)** | 依目標(回覆、轉發、按讚、引用)挑選 2026 年的 Threads 鉤子公式,起草單則貼文或多則串文。遵守 500 字元上限(長文附件 10,000)與單一主題標籤規則 |
| **Humanizer(`threads-humanizer`)** | 去除讀者會察覺的 AI 腔:依密度計分的中文 AI 腔詞彙、否定式對仗、揭曉橋段、堆疊三段式、表演式真誠、簡繁與大陸用語混入、標點與中英間距。不承諾能騙過偵測器。內含 `--mode audit` 發佈前檢查(字元數、鉤子、主題標籤、連結位置、語氣溫度) |
| **Hook Extractor(`threads-hook-extractor`)** | 從任何一則爆文或串文拆解鉤子,對應到 13 種 Threads 公式之一,並給你一份可填的空白範本 |
| **Reply Drafter(`threads-reply-drafter`)** | 為任一 Threads 貼文網址草擬回覆或加值的引用貼文,並判斷該回覆還是引用。回覆他人是另一則獨立貼文,所以草稿以複製貼上區塊交付 |
| **Repurposer(`threads-repurposer`)** | 把其他平台的內容(Facebook、Instagram、LinkedIn、部落格、Podcast 逐字稿、YouTube 腳本、電子報)改成 Threads 原生貼文或串文:調暖語氣、去公文腔與行銷腔、縮到合適長度、重建鉤子、清掉原平台的痕跡,再跑去 AI 味 |
| **Content Planner(`threads-content-planner`)** | 產出一週計畫:單則與串文的比例、每日鉤子、發文時段、每日回覆目標,以及目標組合的平衡檢查 |
| **Profile Optimizer(`threads-profile-optimizer`)** | 端到端審查並重寫 Threads 個人檔案:大頭貼、帶搜尋關鍵字的名稱、@帳號、簡介(150 字元)、連結、置頂貼文,以及連動 Instagram 帶來的探索。回傳評分表、優先修正與前後對照 |
| **Audience Insights(`threads-audience-insights`)** | 用真實資料(經 Apify,免登入)讀懂受眾與利基領域:掃描某個查詢或標籤當下的熱門貼文與互動數,或抓取帳號(你的或競品)的追蹤者數、簡介與近期貼文。Threads 不公開按讚者名單,所以這是探索與帳號統計,不是互動者名單 |

## Threads 上的串文怎麼運作

Threads 每則貼文上限 **500 字元**(附上長文附件可到 10,000)。更長的內容就要做成多則串連的串文。

在官方 Threads API 上做串文,要先為第 1 則建立容器並發佈,再為後續每一則帶上 `reply_to_id` 指向前一則,並處理部分失敗。這個 bundle 把「發佈」這一步抽象成**中立的發佈層**:你寫成一整塊(或用 `---` 手動分段),核准後交給你選擇的發佈方式。與 X 不同,Threads 預設不加 `(1/N)` 編號。

## 發佈層:手動為預設,自建 poster 為選項

Skill 只呼叫 `lib.publish(...)`,不綁定任何第三方服務。你可以:

1. **維持手動(預設,零設定)。** 核准後得到可複製貼上的區塊,你自己貼到 Threads。不需要任何帳號、金鑰或安裝。
2. **自建 poster(進階)。** 請 Claude Code 或 Codex 用 [Threads 官方 Graph API](https://developers.facebook.com/docs/threads/) 寫一個,並在**啟動環境**設定:

```bash
export THREADS_SKILLS_CUSTOM_POSTER="python /path/to/my-poster.py"
```

核准時,skill 會把草稿以 JSON 從 stdin 交給你的指令,並以 `kind` 與目標網址當參數。串文拆分、重試、配額與部分失敗處理,都由你的 poster 負責。

**範例:** [`examples/threads_graph_poster.py`](examples/threads_graph_poster.py) 是一個用官方 Graph API 發單則貼文與串文的可用起點(以 `---` 分段、用 `reply_to_id` 串連、可附 1 張圖、沒有 token 時只做 dry-run)。**它尚未對照官方文件逐項驗證,也沒有對真實帳號發過文**,第一次請先用 `THREADS_POSTER_DRY_RUN=1`,再核對檔頭「API 常數」區塊。需要的環境變數:`THREADS_ACCESS_TOKEN`(可放 `.env`)與 `THREADS_SKILLS_CUSTOM_POSTER`(必須在啟動環境)。這個變數刻意不能寫在 `.env`:`.env` 只允許憑證,避免 clone 下來的檔案夾帶可執行指令。

> **關於回覆:** 回覆與引用他人貼文必須指定對方的貼文,不適合無人看管地自動送出,所以不論哪種發佈層,Reply Drafter 一律以複製貼上區塊交付。

## 選用:用 Pixfaro 產生配圖

一張圖能提升貼文觸及。Post Writer 可以為你的鉤子產生配圖或引言卡,並在發佈時自動附上。沒有金鑰時,它會草擬圖片提示詞,請你自行產圖,所以不會出錯。

[Pixfaro](https://pixfaro.com) 是整合多個模型的圖片 API,可在圖上疊加你的帳號、品牌色或標誌(像素等級精準疊字),便宜的底模型也能有清晰的引言卡文字。品牌欄位來自你的[語氣與品牌檔案](references/voice-profile.md)(第 6 節)。

設定:把 `PIXFARO_TOKEN=pf_live_...` 放進 `.env`。`lib.illustrate(prompt, kind="square")` 與 `lib.refine(image_id, instruction)` 會回傳可直接給 `lib.publish(..., media_urls=[url])` 的託管網址。`refine` 以圖片 id 修改既有圖片(比重畫便宜);結果附 `cost`、`balance_after` 與 `premium` 旗標,避免默默花錢在昂貴模型上。

## 選用:用 Apify 讀取真實 Threads 資料

`threads-audience-insights` 會掃描某個查詢或標籤當下流傳的貼文(內容、讚、回覆、轉發、引用),並抓取帳號的追蹤者數、簡介與最新貼文。沒有讀取憑證時,它會請你貼上看得到的內容,所以不會出錯。

**有 shell 的環境**,在 `.env` 放入免費 token:

```
APIFY_TOKEN=apify_api_...
```

**在 claude.ai 上**(skill 沒有環境可存 token),改用 Apify 的 MCP 伺服器當自訂連接器:

```
https://mcp.apify.com?actors=igview-owner/threads-search-scraper,apify/threads-profile-api-scraper
```

第一次使用時以 OAuth 登入,金鑰不落地。**請保留 `?actors=` 過濾器**:裸的 `https://mcp.apify.com` 還會給 agent `search-actors` 與 `call-actor`,可執行 Apify Store 裡任何東西並依該 actor 收費。

兩件事請注意:搜尋 actor 每次最低計 20 則貼文,要 5 則也收 20 則;Threads 完全不公開按讚名單,所以這是探索加帳號統計,不是互動者名單。細節與欄位對照見 [`references/mcp-read-layer.md`](references/mcp-read-layer.md)。

> 中文內容的抓取結果可能受語言與地區影響,這部分尚未驗證,請先小量測試。

## 語氣規則

每個 skill 都會自動遵守(完整版見 [`references/voice-rules.md`](references/voice-rules.md)):

1. 繁體中文、台灣用語;不混簡體,不用大陸慣用詞。
2. 全形標點;中英數字之間加半形空格;品牌名維持官方寫法。
3. 破折號每則最多 1 個;軟停頓用「⋯⋯」或換行。
4. 避開 AI 腔詞彙群:出現 1 個正常,3 個以上整則重寫。
5. 具體數字勝過形容詞;一則一個想法;第一行承擔全部重量。
6. 每則 500 字元上限;主題標籤 0 到 1 個(Threads 只允許 1 個),emoji 0 到 2 個。
7. 溫暖口語,不是移植過來的 X 式嗆聲。

## 疑難排解

| 問題 | 處理 |
|---|---|
| 問到 Threads 時 skill 沒有啟動 | 確認已透過 Skills 面板、`/plugin install` 或 `codex plugin add` 安裝,並開新對話再試。 |
| 第二個主題標籤不見了 | Threads 每則只允許一個主題標籤,多的會被平台丟掉。只用一個,放在最後。 |
| 串文沒有串連發出 | Meta 處理 Threads App 重新連線時,多則串連可能暫時無法使用。先發第 1 則,其餘手動以回覆補上。 |
| 回覆沒有自動發出 | 回覆他人是獨立貼文,一律由 Reply Drafter 給複製貼上區塊,請自己貼。 |
| 500 字元的邊界跟預期不同 | 中文、英文、標點與 emoji 的計法以 Threads App 為準,請在 App 內實測一次。 |
| `pip install` 失敗 | 用虛擬環境:`python -m venv venv && source venv/bin/activate && pip install -r requirements.txt` |

## 共用參考文件

- [`references/hook-formulas.md`](references/hook-formulas.md):13 種 Threads 鉤子公式,含骨架與目標標記
- [`references/algorithm-heuristics.md`](references/algorithm-heuristics.md):2026 年 Threads 排序訊號、時機與限制
- [`references/voice-rules.md`](references/voice-rules.md):每個 skill 繼承的標準語氣規則與術語表

---

<details>
<summary><b>給開發者:執行環境相容性、網址解析與內部設計</b></summary>

## 執行環境相容性

```
threads-skills/
  skills/             SKILL.md frontmatter;Claude Code 與 Codex 原生支援,其他以 markdown 讀取
  .codex-marketplace/ 產生的巢狀 Codex 套件(執行 scripts/sync_codex_marketplace.py)
  lib/                純 Python,任何 agent 執行環境皆可
  references/         純 markdown,隨處可用
  scripts/            純 Python CLI,隨處可用
```

| 執行環境 | 自動探索 skill? | 設定 |
|---|---|---|
| **Claude Code**(CLI、Desktop、Web、IDE) | 是 | 以 plugin 安裝或 clone,符合的提示會自動啟動 skill。 |
| **Codex CLI** | 是 | `codex plugin marketplace add chichinliu/threads-skills` 與 `codex plugin add threads-skills@threads-skills`。 |
| **Anthropic Managed Agents**(`/v1/agents`) | 是 | 把 skill 檔放進 agent context。 |
| **Cursor / Cline / Aider** | 手動 | 把 `SKILL.md` 當提示脈絡讀入;以 Python 匯入 `lib/`。 |
| **LangChain / AutoGen** | 否 | 把 `lib/` 當套件用;把 `references/` 餵進提示脈絡。 |

## 通用 Python agent 快速範例

```python
import sys; sys.path.insert(0, "path/to/threads-skills")
from lib import parse_threads_url, publish

parsed = parse_threads_url("https://www.threads.net/@zuck/post/C8H9abcDEf_")
print(parsed["handle"], parsed["post_id"])  # zuck C8H9abcDEf_

# 高階包裝:依已設定的發佈層路由(手動 / 自建 poster)
publish("thread", draft_text="第一則\n\n---\n\n第二則\n\n---\n\n第三則",
        target_url="https://www.threads.com/")
```

沒有設定任何發佈層時,`publish` 回傳 `{"mode": "manual", "message": ...}`,內含可複製貼上的區塊。

## 網址處理

`lib/url_parser.py` 解析兩種網域的 Threads 貼文與帳號網址:

| 網址片段 | 解析結果 |
|---|---|
| `threads.net/@HANDLE/post/CODE` | `{handle, post_id, url_type: "post"}` |
| `threads.com/@HANDLE/post/CODE` | 同上(正規化為 threads.com) |
| `threads.com/@HANDLE` | `{handle, url_type: "profile"}` |

```bash
python lib/url_parser.py "https://www.threads.net/@zuck/post/C8H9abcDEf_"
```

## 為什麼回覆是獨立貼文

LinkedIn 把回覆串壓成 2 層,且需要頂層留言的 URN 當父節點。Threads 不是:回覆自然巢狀,沒有要解析的父留言 URN。所以 Reply Drafter 只負責起草文字;回覆必須指定他人貼文,因此刻意設計成複製貼上。

</details>

## 參考資料

- [Threads API(Meta for Developers)](https://developers.facebook.com/docs/threads/):2026 年啟發式所依據的官方 Threads Graph API

## 授權

MIT。由 [chichinliu.com](https://chichinliu.com) 維護;原專案版權歸原作者 Sergey Bulaev(見 [LICENSE](LICENSE))。

## 更多資源

- [chichinliu.com](https://chichinliu.com):AI 策略、導入與訓練資源
- [Anthropic Skills repo](https://github.com/anthropics/skills) 與 `awesome-claude-skills` 目錄
