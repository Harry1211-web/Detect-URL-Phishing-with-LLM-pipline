# Ghi chú cải tiến

Ghi chú này gồm các thay đổi đã làm để tối ưu hệ thống, các phương pháp đã đo rồi bỏ, số liệu
benchmark và các đóng góp mà những số liệu đó chứng minh. Mọi con số đều lấy từ
`notebooks/pipeline_experiment.ipynb` hoặc từ các file báo cáo mà notebook dẫn tới. Mọi lựa chọn
đều được đưa ra trên dữ liệu validation / dev, và mỗi tập test chỉ được chấm một lần cho mỗi cấu
hình đã chọn (lựa chọn thiết kế bỏ tra cứu mạng được ghi rõ ở mục 1).

## 1. Các phương pháp đã áp dụng

| Phương pháp | Nội dung | Bằng chứng |
|---|---|---|
| **Bộ lọc dùng mẫu động** | `html_sanitize.PatternLoader` gộp mỗi ngôn ngữ một file JSON (`data/injection_patterns/<lang>.json`, 16 ngôn ngữ). Mỗi file chứa: regex prompt injection, các cơ quan được trích dẫn và tên miền riêng của họ, từ kết luận, từ phủ định, từ mồi nhử. Bộ lọc và bộ đọc kết luận không còn mẫu riêng của ngôn ngữ nào. | Phát hiện giống hệt trước (bộ test không đổi). Thêm ngôn ngữ chỉ cần thêm file. Red team khó: tối đa 1 trang bị lật thành *safe* trên 324 trang thật bị tấn công (`reports/llm/redteam_injection/`). |
| **VirusTotal làm công cụ kiểm chứng** | Không nằm trong pipeline. Chỉ tra báo cáo URL để làm nhãn tham chiếu khi kiểm chứng pipeline: ≥ 2 engine báo độc hại → phishing. Có cache, không bao giờ gửi URL lên. | Trên một mẫu cố định của tập tiếng Việt (95 phishing từ Chống Lừa Đảo + 95 sạch): các feed công khai bắt được 1,1 % phishing, VirusTotal bắt 66,3 % (precision 0,984, gắn cờ nhầm 1 trang sạch). |
| **Chống Lừa Đảo làm nhãn chuẩn tiếng Việt** | Nhãn phishing tiếng Việt lấy từ blacklist Chống Lừa Đảo (một bản mirror công khai cố định, chỉ giữ host còn sống và đăng ký trước thời điểm chụp). Chống Lừa Đảo *không* phải feed của Lớp A, nên đánh giá Lớp A trên tập này không bị vòng lặp. | 2.681 URL phishing sau kiểm định nhãn. |
| **Tập test tiếng Việt không rò rỉ** | Chuyển sang `data/test_sets/vi/`, tách khỏi dữ liệu huấn luyện. Đã kiểm tra trùng tên miền đăng ký với mọi file huấn luyện, mọi file đánh giá và các trang DOM. | 0 tên miền trùng với file huấn luyện và trang DOM. Có 2 tên miền phishing trùng với các tập trang của Lớp D, nhưng đó là tập đánh giá, chưa từng dùng để huấn luyện. |
| **Một ngôn ngữ prompt, ngôn ngữ đầu ra động** | Prompt viết bằng tiếng Anh. Tham số `lang` (mặc định `vi`) chọn ngôn ngữ giải thích. Từ khóa VERDICT vẫn giữ tiếng Anh. | Dev, 651 trang: giải thích bằng tiếng Việt 100 % (gpt) / 99,7 % (Haiku). Kết luận khớp với lần chạy chỉ ra kết luận: 97,2 % / 95,9 %. Phishing → safe: 15,7 → 15,4 % (gpt, McNemar p = 1,0) và 16,5 → 14,8 % (Haiku, p = 0,07). Giữ lại vì không có thay đổi đáng kể. |
| **Kiểm định nhãn mọi tập** | `src/data_collection/audit_labels.py`: luật độc lập với Lớp C (domain PhiUSIIL đăng ký sau khi thu thập → loại; trang chủ Tranco không trong feed hiện tại và VirusTotal không báo độc → sạch) cộng 234 URL gán tay (`reports/relabel/hand_review.csv`). Áp dụng cho dataset, tập tiếng Việt và PhreshPhish, rồi train và đo lại toàn bộ. | Dataset: 2.951 dòng (2.703 loại, 246 → sạch, 2 loại); tiếng Việt: 33; PhreshPhish: 11 (`dataset/urls/label_fixes.csv`). Gán tay: 24 / 24 trang chủ phổ biến bị gắn phishing thực ra sạch. |
| **Chọn lại Lớp C** | 5 mô hình DL cho URL, cross-fit như bản production. Sau đó RF / XGBoost / LightGBM dùng điểm của mô hình DL thắng + đặc trưng URL + thứ hạng Tranco (như production). Cả hai bước đều chọn theo quy tắc "ít bỏ sót nhất trên val khi nhận ra ≥ 50 % sạch trên val" (hòa: PR-AUC val cao hơn). | BiLSTM thắng với 414 bỏ sót trên val (CNN/BiLSTM 427, char-CNN 461, URLNet 594, Transformer 1.095). **XGBoost thắng**: XGBoost 19, LightGBM 19 (PR-AUC 0,98925 / 0,98920), RF 31. Có tra mạng: XGBoost 16, LightGBM 20, RF 28. |
| **Lớp C không tra cứu mạng** | Đặc trưng host chỉ còn thứ hạng Tranco (file cục bộ): `train.py --host-lookups none`. Trang con của nền tảng chia sẻ (blogspot, sites.google…) không thừa hưởng thứ hạng của nền tảng; trang chủ của chính nền tảng (google.com/) thì có. Luật đặt trước khi train: chấp nhận nếu số bỏ sót trên val tăng không quá 30 %. | Val: 13 bỏ sót, nhận ra 52,0 % sạch (bản có DNS / TLS / RDAP: 15, 54,1 %). Độ trễ Lớp C 32 ms cho mọi URL (trước: 1,4 s p50 / 2,5 s p95 với host mới). Không còn kết nối tới server của trang đang kiểm tra (`reports/layer_c_selection/host_lookups.json`). |
| **Nhãn VirusTotal cho tập gán nhãn lại** | 297 trang (300 trừ 3 trang bị loại khi kiểm định nhãn) gán nhãn bằng VirusTotal: ≥ 2 engine → phishing, 0 → sạch, còn lại → không chắc. | 148 trang có nhãn: 4,1 % nhãn đã kiểm định của dataset không khớp [KTC 95 %: 1,9–8,6 %]. |

## 2. Các phương pháp đã bỏ và lý do

| Phương pháp | Trạng thái | Lý do |
|---|---|---|
| Regex viết cứng trong Python | Dùng đến commit f82f78b (regex tiếng Việt + tiếng Anh trong `html_sanitize.py`). Chuyển sang dữ liệu ở d733ab8. Các danh sách cuối cùng (tên miền cơ quan, từ kết luận, từ phủ định) chuyển trong đợt này. | Thêm ngôn ngữ phải sửa code. Một lần "dịch toàn bộ" trước đây đã dịch luôn mẫu phát hiện tiếng Việt, và lẽ ra sẽ làm hỏng khả năng phát hiện trên trang tiếng Việt. |
| System prompt hai ngôn ngữ | **Chưa bao giờ triển khai.** Dự án từng dùng prompt chỉ tiếng Việt (f82f78b), sau đó là một prompt tiếng Anh. | Hai prompt sẽ nhân đôi công tinh chỉnh và đánh giá. Ngôn ngữ đầu ra động đã cho giải thích tiếng Việt từ một prompt mà kết luận không thay đổi đáng kể (bảng trên). |
| URL phishing tổng hợp / tự tạo làm nhãn | **Không bao giờ dùng để huấn luyện hay kiểm thử.** Trang tổng hợp chỉ có trong red team và các kịch bản thương hiệu Việt, và được báo cáo rõ là tổng hợp. | URL tự tạo đo bộ sinh chứ không đo kẻ tấn công thật. Dự án dùng feed thật thay thế (PhishTank, OpenPhish, Chống Lừa Đảo). |
| Dữ liệu gộp chung, không tách biệt | Tập tiếng Việt từng nằm ở `dataset/urls/vi/` cạnh dữ liệu huấn luyện (dù đã tách theo tên miền). Nay nằm ở `data/test_sets/vi/`, có kiểm tra trùng lặp trong notebook và trong test. | Tách vật lý và có kiểm tra thì rò rỉ sẽ lộ ra. |
| Cho mô hình DOM xóa cờ của URL (luật "and") | **Bị loại.** | Trang do kẻ tấn công kiểm soát: một trang cloaking trông sạch sẽ biến URL đã bị gắn cờ thành "sạch". |
| Mô hình DOM chỉ thêm nghi ngờ (luật "or") | Được phép, nhưng không đạt ≥ 50 % sạch trên val. **Không bật.** | Lớp C production vẫn chỉ dùng URL. Mô hình DOM (PR-AUC val 0,973) được giữ lại và đo đạc. |
| Số engine VirusTotal làm đặc trưng ML | Không xây dựng | Số engine gắn cờ một URL gần như chính là nhãn của nó (rò rỉ). Quota miễn phí (500 / ngày) không đủ cho tập huấn luyện. |
| Đặc trưng DNS / TLS / RDAP (tra mạng khi chạy) | Đã đo, **bỏ khỏi production** | Ablation 3 seed trên bản có tra mạng: bỏ cả ba chỉ tăng bỏ sót trên val 17 → 24 (bỏ riêng Tranco: 17 → 71), nhưng tốn 1–2,5 s cho mỗi host mới và phải kết nối tới server của kẻ tấn công. Code giữ lại cho thí nghiệm. |
| Các ứng viên Lớp C khác | Đã đo, thua trên val | CNN/BiLSTM, char-CNN, URLNet, Transformer; random forest (mục 3). |
| Các vòng trước | Đã đo, bỏ | RAG cho Lớp D (kết luận không tốt hơn, `reports/llm/rag_pipeline/`). Các biến thể tên miền ghép của Lớp B (báo động nhầm nhiều hơn mà bỏ sót của pipeline không giảm). |

## 3. Tóm tắt benchmark

**Cách đọc.** Phishing là lớp dương. Mọi số liệu tính trên nhãn đã kiểm định (mục 1).

- **Lớp A–C:** một URL bị *gắn cờ* khi bị chặn hoặc bị chuyển tiếp sang Lớp D.
- **Lớp C** là cổng ưu tiên recall. Theo thiết kế, nó chuyển khoảng một nửa số URL sạch sang LLM,
  nên precision và F1 thấp là có chủ đích. Con số quan trọng là tỉ lệ bỏ sót.
- **Lớp D và toàn pipeline:** *strict* = kết luận *phishing*. *warn* = *phishing* hoặc
  *suspicious*, tức người dùng được cảnh báo.

### 3.1 Lớp C và các baseline — cùng một quy tắc cho mọi mô hình

Tập test của dataset (81.225 URL), PhreshPhish (19.994 URL), tập tiếng Việt (4.265 URL).

| Mô hình | % bỏ sót test | Recall | F1 | PhreshPhish: % bỏ sót / % sạch | VN: % bỏ sót / % sạch |
|---|---|---|---|---|---|
| Logistic regression (URL) | 5,14 | 0,949 | 0,760 | 4,46 / 48,2 | 30,7 / 97,2 |
| Random forest (URL) | 3,61 | 0,964 | 0,770 | 3,06 / 49,5 | 50,3 / 92,4 |
| Transformer (URL) | 2,77 | 0,972 | 0,774 | 3,68 / 61,5 | 40,2 / 84,9 |
| LightGBM (URL) | 2,76 | 0,972 | 0,774 | 3,32 / 57,6 | 46,7 / 98,0 |
| URLNet (URL) | 1,49 | 0,985 | 0,782 | 2,23 / 63,0 | 12,5 / 96,9 |
| char-CNN (URL) | 1,03 | 0,990 | 0,784 | 2,22 / 63,3 | 20,4 / 98,1 |
| BiLSTM (URL) | 1,02 | 0,990 | 0,784 | 2,83 / 71,9 | 22,8 / 98,2 |
| LightGBM (URL + host có tra mạng) | 0,026 | 0,9997 | 0,789 | 0,20 / 37,5 | 0,07 / 13,5 |
| **Lớp C: BiLSTM + XGBoost (URL + Tranco)** | **0,021** | **0,9998** | **0,789** | **0,46 / 47,4** | **0,52 / 55,1** |

- Precision ≈ 0,65 ở mọi dòng, vì quy tắc chuyển tiếp ≈ 50 % URL sạch. Recall = 1 − tỉ lệ bỏ sót.
- Bảng này dùng một ngưỡng duy nhất (nhận ra 50 % sạch trên val) cho mọi mô hình; Lớp C production
  dùng ngưỡng theo segment (mục 3.2), nên số của nó ở mục 3.2 hơi khác.
- Baseline "LightGBM (URL + host)" bỏ sót ít hơn nhưng gần như không nhận ra URL sạch tiếng Việt
  (13,5 %): ngưỡng val của nó không chuyển được sang dữ liệu mới, và nó cần tra mạng.
- Các ứng viên được chọn trên val (`reports/layer_c_selection/`): DL 414–1.095 bỏ sót; ML trên điểm
  BiLSTM + Tranco: XGBoost 19, LightGBM 19 (XGBoost thắng nhờ PR-AUC), random forest 31.
- Ablation 3 seed trên Lớp C đang dùng (bỏ sót trên val, trung bình): đủ 18; bỏ Tranco 393; bỏ điểm
  BiLSTM 29; bỏ mọi đặc trưng thủ công 27; bỏ nhóm độ dài / cấu trúc URL 21; các nhóm URL khác 17–19.

### 3.2 Các lớp của pipeline — ngưỡng production, không gọi LLM

| Tập | Lớp | Bỏ sót | Nhận ra sạch | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| Test của dataset (38.800 phishing / 42.425 sạch) | A | 9.528 | 100 % | 1,000 | 0,754 | 0,860 |
| | B | 35.747 | 99,7 % | 0,964 | 0,079 | 0,146 |
| | C | 12 | 52,6 % | 0,659 | 0,9997 | 0,794 |
| | **A + B + C** | **4** | **52,5 %** | 0,658 | 0,9999 | 0,794 |
| | B + C (không có A) | 12 | 52,5 % | 0,658 | 0,9997 | 0,794 |
| Tập tiếng Việt (2.681 / 1.584) | A (feed) | 2.668 | 99,9 % | 0,929 | 0,005 | 0,010 |
| | B | 2.623 | 99,9 % | 0,967 | 0,022 | 0,042 |
| | C | 16 (0,60 %) | 56,8 % | 0,796 | 0,994 | 0,884 |
| | **A + B + C** | **15 (0,56 %)** | **58,3 %** | 0,801 | 0,994 | 0,888 |
| PhreshPhish (9.991 / 10.003) | A | 9.956 | 100 % | 0,946 | 0,004 | 0,007 |
| | B | 8.590 | 99,6 % | 0,974 | 0,140 | 0,245 |
| | C | 47 | 44,3 % | 0,641 | 0,995 | 0,780 |
| | **A + B + C** | **43 (0,43 %)** | **44,5 %** | 0,642 | 0,996 | 0,781 |
| Mẫu VN, 95 + 95 | Chỉ blocklist | 94 | 100 % | 1,000 | 0,011 | 0,021 |
| | Blocklist + VirusTotal (tham chiếu, không trong pipeline) | **32** | **99,0 %** | **0,984** | **0,663** | **0,793** |

Các feed blocklist cũng là nguồn nhãn phishing của dataset, nên kết quả của Lớp A trên tập test
của dataset bị lạc quan. Riêng "B + C (không có A)" bỏ sót 12.

### 3.3 Lớp D và toàn pipeline

| Thiết lập | Mô hình | Phishing → safe | Sạch → phishing | Strict P / R / F1 | Warn P / R / F1 | p50 / p95 |
|---|---|---|---|---|---|---|
| Lớp D, test giữ riêng (2.004 trang), có override của C | gpt-6-luna | 5,08 % | 2,90 % | 0,959 / 0,678 / 0,795 | 0,937 / 0,949 / 0,943 | 2,0 / 4,8 s |
| | claude-haiku-5-5 | 4,38 % | 4,80 % | 0,940 / 0,745 / 0,831 | 0,892 / 0,956 / 0,923 | 1,5 / 3,2 s |
| Toàn pipeline, VN live (300 + 300) | gpt-6-luna | 9,33 % | 2,00 % | 0,928 / 0,257 / 0,402 | 0,901 / 0,907 / **0,904** | 0,2 / 7,7 s |
| | claude-haiku-5-5 | 7,33 % | 2,00 % | 0,935 / 0,287 / 0,439 | 0,897 / 0,927 / **0,911** | 0,1 / 7,9 s |
| Toàn pipeline, trang sâu của top site (400 trang sạch) | gpt-6-luna | — | 0,75 % | — | 93,0 % kết luận *safe* | 0,1 / 6,0 s |

**Chạy lại lần hai trên cùng các trang:**
- Kết luận khớp 95,4–97,4 %.
- Phishing → safe: gpt (test) 7,57 / 7,67 %; Haiku (test) 5,98 / 5,58 %.
- Không có McNemar p nào < 0,12.

**Chi phí mỗi trang:** gpt $0,000129, Haiku $0,000224.

**Các lần chạy VN live:** khoảng một nửa trang phishing tiếng Việt trong blacklist đã offline, nên
kết luận của chúng lấy từ luật dự phòng (*suspicious*). Vì vậy recall strict thấp còn recall warn cao.

### 3.4 Độ trễ (một URL, không LLM; `reports/pipeline/metrics.json`)

| Giai đoạn | p50 | p95 |
|---|---|---|
| A blocklist | 0,12 ms | 0,16 ms |
| B typosquatting | 0,52 ms | 1,2 ms |
| C (URL + Tranco, không tra mạng) | 32,1 ms | 35,0 ms |
| A + B + C | 32,9 ms | 35,6 ms |
| D (LLM) | 1,5–2,0 s | 3,2–4,8 s |

Bản Lớp C có tra DNS / TLS / RDAP mất 1,4 s (p50) / 2,5 s (p95) cho host chưa có trong cache.

## 4. Đóng góp cho bài báo nghiên cứu

Mỗi luận điểm đều kèm bằng chứng. Luận điểm nào chưa đủ bằng chứng được ghi ở phần giới hạn.

1. **Chuỗi lớp ưu tiên recall, chỉ dùng LLM cho nửa khó.**
   - Lớp A + B + C bỏ sót 4 trên 38.800 URL phishing test (0,010 %); không có A: 12 (0,031 %).
   - Đồng thời xác nhận sạch 52,5 % URL sạch trong khoảng 33 ms, không gọi LLM, không tra cứu mạng.
   - Trên các trang giữ riêng có đi tới LLM, override của C giảm phishing → safe còn 5,1 % (gpt)
     / 4,4 % (Haiku).
2. **Điểm URL từ DL cộng thứ hạng Tranco, chọn theo một quy tắc ưu tiên bỏ sót.**
   - So với 5 mô hình DL × 3 bộ phân loại và 8 baseline: mô hình chỉ dùng URL bỏ sót 1,0–5,1 %
     phishing test, Lớp C 0,031 %.
   - Ablation 3 seed: Tranco là đặc trưng quyết định (bỏ nó: 18 → 393 bỏ sót trên val); các đặc
     trưng tra mạng (DNS, TLS, RDAP) chỉ thêm ít (17 → 24) nên bị bỏ để Lớp C chạy 32 ms.
   - Ngưỡng val chuyển được sang dữ liệu chưa từng thấy: tiếng Việt bỏ sót 0,56 % ở 58,3 % sạch;
     baseline LightGBM có tra mạng chỉ nhận ra 13,5 % sạch tiếng Việt.
3. **Benchmark tiếng Việt thực tế, không rò rỉ, cho thấy các feed bỏ sót rất nhiều.**
   - 4.265 URL: phishing từ Chống Lừa Đảo; sạch từ Tranco `.vn` và các tên miền thương hiệu đã
     xác minh. Đã kiểm tra tách biệt tên miền và gán tay các URL nghi ngờ.
   - Feed toàn cầu bắt được 0,5 % số phishing này; VirusTotal (chỉ để so sánh) bắt 66,3 % (trên mẫu).
   - Cổng A + B + C bỏ sót 0,56 %; toàn pipeline live cảnh báo 91–93 % phishing, warn-F1 0,90–0,91.
4. **Lớp LLM không phụ thuộc mô hình, chống prompt injection, có đo độ ổn định.**
   - Một bộ lọc (dựa trên dữ liệu, 16 ngôn ngữ) và một prompt tiếng Anh dùng được cho hai họ LLM.
   - Tấn công prompt injection khó lật tối đa 1 trên 324 trang thật thành *safe*.
   - Hai lần chạy giống hệt nhau khớp 95–97 % kết luận, không có khác biệt đáng kể.
   - Đổi mô hình là đánh đổi giữa bỏ sót và báo động nhầm: Haiku bỏ sót ít hơn (p = 0,004)
     nhưng chặn nhầm trang sạch nhiều hơn (p = 0,005).
5. **Dùng cấu trúc trang có ràng buộc bảo mật.**
   - Mô hình DOM huấn luyện trên trang PhreshPhish tách rời mọi tập đánh giá (PR-AUC val 0,973).
   - Cho nó xóa cờ URL bị loại, vì trang do kẻ tấn công kiểm soát (cloaking).
   - Theo luật "chỉ thêm nghi ngờ", nó không đạt mục tiêu về lưu lượng sạch.
   - Đây là kết quả âm, ủng hộ việc dùng bằng chứng URL làm cổng.
6. **Kiểm định nhãn độc lập với mô hình.**
   - Luật dựa trên bằng chứng ngoài Lớp C (ngày đăng ký tên miền, Tranco, feed hiện tại, VirusTotal)
     và gán tay 234 URL; toàn bộ thí nghiệm chạy lại trên nhãn đã kiểm định.

**Giới hạn.**
- Nhãn của các feed công khai vẫn còn nhiễu: lệch 4,1 % so với VirusTotal trên tập gán nhãn lại;
  190 trang chủ phổ biến chưa tra được VirusTotal nên giữ nhãn phishing.
- Phép đo VirusTotal chỉ trên mẫu 190 URL.
- Bỏ tra mạng là lựa chọn thiết kế (theo luật đặt trước): PhreshPhish bỏ sót 32 → 43, nhận ra sạch
  38 % → 44 %.
- Lớp D vẫn để 4–5 % trang phishing nó xem lọt thành *safe* (trang thật tiếng Việt: 7–9 %).
- Mỗi mô hình DL chỉ huấn luyện một lần (một seed), nên chênh lệch BiLSTM / CNN-BiLSTM trên val
  (414 so với 427 bỏ sót) nằm trong mức nhiễu.
