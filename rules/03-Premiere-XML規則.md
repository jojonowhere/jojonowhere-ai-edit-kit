# Premiere XML 產生規則

（Premiere Pro 2026, 版本 26.2.0 上實測；這個格式沒有單一可靠的官方規格，網路上找得到的「已驗證可用」範例彼此互相矛盾，任何沒有從「已驗證能匯入成功」的檔案照抄的元素，都算是用猜的。）

## 已驗證正確的做法（照這個做）

1. **單一影像軌＋單一音軌是預設起手式**。就算最終目標是多軌合成（子母畫面、疊加），也要**分開產生多個單軌 XML 檔案**，讓使用者自己在 Premiere 裡手動疊軌（匯入成獨立序列→複製剪輯片段→貼到新軌道），不要冒險把多軌塞進同一份檔案。
2. **音軌一定要指向另外用 ffmpeg 抽出來的獨立音檔，絕對不能跟影像軌共用同一個來源檔案／同一個 `<file>` id**——就算用「同一個file id、`<media>`裡video/audio一起宣告」這種在XML格式上合法的寫法，實測證實 Premiere 還是會匯入失敗（讀取條跑一下就消失）。指令：`ffmpeg -i 來源.mov -vn -acodec aac -b:a 192k 輸出.m4a`。這是最重要的一條規則，優先度高於其他所有XML規則。
3. **同一個來源檔案在同一軌內被大量 clipitem 重複引用是安全的**，已驗證單一音檔切33段、單一影像檔案用44個clipitem（22個剪點）都能正常匯入——**剪點數量本身不是風險**，真正的風險是「一份Sequence裡引用了太多『不同的』來源檔案／`<file>` id」。所以「同一支長素材切很多段」可以放心直接做XML；「很多支不同來源影片混剪在同一個Sequence」風險仍在，優先考慮下面提到的編號小檔案法。
4. **`<file>` 元素子項目固定順序**：`name → pathurl → rate → duration → media`。
5. **`<clipitem>` 子項目固定順序**：`name → duration → rate → start → end → in → out → file`。
6. **`<media><video><samplecharacteristics>` 要包含完整欄位，不能只有width/height**：至少要有 `<rate>`、`<width>`、`<height>`、`<pixelaspectratio>`、`<fielddominance>`、`<colordepth>`。只寫width/height會導致Premiere匯入後sequence settings跑掉、pixel aspect ratio不是square。`pixelaspectratio`／`fielddominance`的值要用 `ffprobe -show_entries stream=sample_aspect_ratio,field_order` 讀來源檔案實測結果去填，不要憑感覺猜。
7. **檔名、序列名稱、所有內部`<name>`欄位只能用純英數字**，不能有中文，排除編碼/檔名解析這個變數。
8. **`<track>`標籤裡不能有`<name>`子標籤**。
9. **不要自己編造`<filter>`特效標籤**（動態、縮放、位置、透明度等），子母畫面的定位/縮放留給使用者匯入後在Premiere的效果控制面板手動調整。
10. **如果來源含macOS螢幕錄影／QuickTime螢幕擷取，生成XML之前要先確認並處理VFR（變動影格率）問題**：這類素材直接引用會讓Premiere預覽/拖曳明顯卡頓，這是素材本身的問題、不是XML語法能修好的。做法：`ffmpeg -i 來源.mov -r 30 -vsync cfr -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k 輸出_CFR.mov`，保留原始解析度只修正影格時間結構，轉完用`ffprobe`確認`r_frame_rate`跟`avg_frame_rate`兩個數字一致才算成功。XML裡的`<file>`要整個指向這支CFR檔案，`<rate><timebase>`也要改成CFR檔案的真實影格率。不要等使用者回報卡頓才處理，來源一旦是螢幕錄影就該預期是VFR。
11. **同時交付「保底版」（編號小檔案，不能延伸剪點）跟「正式版」（XML，引用原始長版素材，可以自由延伸剪點）**，不要只做一種——XML有沒有匯入成功使用者當下才知道，保底版讓使用者不會被卡住。
12. XML格式驗證（例如用`xml.dom.minidom`）只能證明檔案是合法XML，**不能證明Premiere會接受這個序列**，這是兩件不同的事，交付時要講清楚。
13. **每次交付都要明確講清楚**：這次的結構是不是跟上次使用者確認可行的檔案完全一致，還是有任何新的、沒驗證過的改動——不要暗示「這應該可以了」，有新風險就明講。

## 已知會導致匯入失敗或播放異常的做法（不要做）

1. **不要讓音軌跟影像軌共用同一個來源檔案／同一個`<file>` id**，即使技術上用「一個id、media裡video/audio都宣告」的寫法合法，實測依然匯入失敗——這是最容易犯、也最重要的一條。
2. **不要在`<track>`底下加`<name>`子標籤**——Premiere的解析器比一般XML parser嚴格，可能整份檔案直接判讀失敗。
3. **不要自己編造`<filter>`特效區塊**——結構複雜且未經驗證，寫錯風險很高，會拖累整份檔案匯入失敗。
4. **不要用中文檔名／中文內部`<name>`標籤**——已實測會導致Premiere匯入完全沒反應（拖曳或File > Import都一樣）。
5. **不要把多軌（PiP／畫中畫）疊加塞進同一份XML**——已試過三次修正都失敗，原因未定論，改用拆成多份單軌XML分開匯入、使用者手動疊合。
6. **不要假設「規模大＝一定失敗」而直接放棄XML**——同一支素材重複引用即使剪點數達20-40個仍驗證可行；真正該提高警覺的情境是「一份Sequence裡有很多支不同來源檔案」，不是單純剪點數量多。
7. **不要只宣告width/height就當作`<samplecharacteristics>`寫完了**——漏掉pixelaspectratio/fielddominance/colordepth會讓Premiere自己猜、猜錯導致sequence settings跑掉。
8. **不要用來源檔案容器宣告的`r_frame_rate`直接當作XML timebase去解決卡頓問題**——如果來源是VFR，這個數字往往跟實際`avg_frame_rate`落差很大，單純改timebase宣告的數字沒辦法解決VFR本身造成的播放卡頓，必須先把來源轉成真正的CFR檔案。
9. **不要把`xml.dom.minidom`能parse通過當成「保證能匯入Premiere」**——這只排除低級語法錯誤，不是匯入成功的保證，兩者是不同層次的驗證。
10. 如果真的避不開多軌/多素材交叉引用，且XML反覆匯入失敗，考慮改用**CMX3600 EDL**（更古老、更簡單的純文字格式，錯誤面更小，代價是基本只能單軌影像+少數幾軌音訊）作為備案。
