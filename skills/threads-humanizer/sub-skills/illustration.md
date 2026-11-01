# 子流程:為 Threads 貼文產生配圖

為草稿加上一張選用的圖片(動態消息配圖、方形美術圖或金句卡),並在發佈時附上。圖像層(Pixfaro)是**可選的**,透過 `lib.illustrate` 呼叫,會回傳一個託管網址,可直接交給發佈層的 `media_urls`。任何 agent(Claude Code、Codex、OpenClaw)都能跑。沒有圖像服務也完全不影響發文。

## 何時執行

- 使用者說「幫我加一張圖」「做一張配圖」「做金句卡」。
- 草稿核准後提供一次,且只在圖片確實能提升觸及時提。

## 後端(與發佈層對稱)

- **pixfaro**:設定了 `PIXFARO_TOKEN`(`pf_live_...`)時,自動產圖並附上。
- **manual**:沒有 token 時,由 skill 草擬圖片提示詞,請使用者自行產生後貼上網址。絕不阻擋草稿。

`lib.image_backend()` 會回報目前使用哪一個。

## 步驟

1. **選尺寸類型。** Threads 預設為 `square`(1:1)。需要時用 `aspect_ratio="w:h"` 覆寫。其他類型:thumbnail 16:9、carousel / quote / portrait 4:5、story / cover 9:16、wide / link 16:9、square 1:1。
2. **撰寫提示詞。** 描述主體、構圖、風格、色調。除非語氣檔案 §6 指定了視覺風格,否則預設乾淨、專業。**不要把貼文的文字畫進圖裡**(用 overlay)。中文字尤其不要交給生圖模型,容易出現錯字。
3. **套用品牌 overlay(若檔案有填)。** 讀 `../../../references/voice-profile.md` §6。若有設定帳號名稱、品牌色或 logo,就傳入 `overlay`,讓文字與 logo 以像素精準的方式疊上去(即使底圖模型很便宜,字也清楚):
   ```python
   from lib import illustrate
   r = illustrate("<場景提示詞>", kind="square",
                  overlay={"text": "@handle", "position": "bottom-right", "color": "#RRGGBB"})
   ```
   做**金句卡**時,把挑出的鉤子句放進 overlay 的 `text`(不要放進提示詞),`kind="quote"`。overlay 的中文字體是否正確顯示,請在核准前確認預覽。
4. **模型選擇。** 預設 `nano-banana-2`,沒傳 model 時 `illustrate` 就用它。文字由 overlay 處理,所以便宜的底圖模型就夠;只有需要高階美術時才用 gemini-pro-image。絕不默默升級等級。
5. **展示並確認。** 呈現回傳的 `url` 與 `cost`。核准後,發佈時用 `media_urls=[r["url"]]` 附上。
6. **手動模式。** 若 `r["backend"] == "manual"`,顯示 `r["message"]` 並請使用者貼上網址。

## 微調,不要重畫

使用者要小改(「天空再暗一點」「換掉標題」「多留白」)時,**不要**從頭重新產生。保留上一次結果的 `id` 去編輯:

```python
from lib import illustrate, refine
first = illustrate("<場景>", kind="wide")     # -> {"id": "img_...", "url": ...}
fixed = refine(first["id"], "背景調暗並提高對比")
```

`refine` 以 `img_...` 的 id 編輯(不是網址);省略 `aspect_ratio` / `resolution` 時會沿用原圖的形狀與計費等級,比重新產生便宜,也更一致。可以連續微調多次。

## 成本防護

- 每個結果都帶有 `cost` 與 `balance_after`;若 `low_balance` 為 True,在繼續產圖前先告訴使用者 Pixfaro 餘額偏低。
- 預設 `nano-banana-2` + 1K。高階模型(`gemini-pro-image`、`gpt-5-image`)的單價高出數倍,只有使用者點名時才用;`illustrate` / `refine` 不會自行升級。結果的 `premium` 旗標為 True 時,代表用了高價模型,請確認那是使用者要的。
- 需要顯示即時價格與延遲時,用 `lib.available_models()`。

## 硬性規則

- 每次請求一張圖(不支援 `n>1`);輪播圖一張一張產。
- 真正要出現的字放進 `overlay`,不要畫進提示詞的美術裡。
- 除非使用者要求高階,否則預設便宜模型 + 1K 解析度。
- 絕不附上使用者沒看過、沒核准的圖片。
- 圖像層是可選項。使用者不想用或沒有 token,就走手動模式,不要催促註冊。
