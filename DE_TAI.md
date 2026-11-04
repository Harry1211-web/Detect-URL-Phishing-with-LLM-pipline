## Tên đề tài

**Tên ngắn:** Hệ thống phát hiện website lừa đảo sử dụng học máy và học sâu kết hợp mô hình ngôn ngữ lớn (Phishing Website Detection System Using Machine Learning and Deep Learning Combined with Large Language Models)

## Mô tả đề tài

### Mục tiêu

Website lừa đảo chỉ tồn tại vài giờ đến vài ngày, nên các danh sách đen công khai luôn đi sau kẻ tấn công. Ngược lại, dùng mô hình ngôn ngữ lớn (LLM) đọc mọi trang thì chậm, tốn kém và dễ bị chính trang độc thao túng qua prompt injection. Ngoài ra, các giải pháp hiện có chủ yếu được đánh giá trên dữ liệu quốc tế, chưa kiểm chứng trên dữ liệu lừa đảo tiếng Việt.

Đề tài xây dựng hệ thống cảnh báo khi người dùng bấm vào một URL, với bốn mục tiêu:

* **Không bỏ sót**: không để URL lừa đảo nào bị kết luận là sạch, kể cả URL mới chưa có trong danh sách đen.
* **Nhanh và rẻ**: phần lớn URL sạch được xác nhận trong vài chục mili giây, không cần gọi LLM.
* **Bền trước tấn công**: kẻ tấn công không thể chèn chỉ thị ẩn vào trang để LLM kết luận an toàn.
* **Dùng được ở Việt Nam**: được đánh giá trên dữ liệu lừa đảo tiếng Việt thực tế, không chỉ trên tập quốc tế.

### Phương pháp

Mỗi URL đi qua bốn lớp từ rẻ đến đắt. Một lớp chỉ chuyển URL lên lớp sau khi chưa đủ chắc chắn.

|Lớp|Vai trò|Thời gian|
|-|-|-|
|**A**: Blocklist |Chặn tức thì URL đã biết là lừa đảo (OpenPhish, PhishTank, Phishing.Database, cập nhật mỗi giờ)|< 1 ms|
|**B**: Typosquatting|Phát hiện mạo danh thương hiệu bằng Damerau-Levenshtein và Jaro-Winkler trên toàn bộ URL, gồm subdomain, path và URL chuyển hướng ẩn|\~0,5 ms|
|**C**: BiLSTM + XGBoost|Cổng ưu tiên recall: điểm học sâu của URL kết hợp đặc trưng URL và thứ hạng Tranco của tên miền (file cục bộ, không tra cứu mạng). Xác nhận ngay khoảng một nửa số URL sạch, phần còn lại chuyển lên lớp D|\~32 ms|
|**D**: LLM|Đọc nội dung trang đã lọc chỉ thị ẩn, kết luận phishing, suspicious hoặc safe|\~2 s|

Nguyên tắc thiết kế: không để URL lừa đảo nào bị gắn nhãn sạch. Khi một lớp gặp lỗi, hết thời gian hoặc thiếu bằng chứng, hệ thống nghiêng về cảnh báo thay vì bỏ qua.

Đóng gói và triển khai:

* Hệ thống chạy dưới dạng HTTP API trên Docker, có xác thực bằng khóa và giới hạn tần suất, để giao diện web hoặc tiện ích trình duyệt gọi trực tiếp.
* Hệ thống được gia cố trước các kỹ thuật né tránh thực tế: URL rút gọn, chuyển hướng lồng nhau, host mã hóa hoặc dùng ký tự full-width, cloaking và đầu độc cache.

Đánh giá và thí nghiệm:

* Mô hình và ngưỡng chỉ được chọn trên tập val. Tập test, tập tiếng Việt và tập ngoài PhreshPhish mỗi tập chỉ đo một lần.
* Dữ liệu chia theo tên miền để không có rò rỉ giữa các tập.
* Kết quả được so với 8 baseline, có ablation từng nhóm đặc trưng, kiểm định thống kê (Wilson, McNemar) và red team prompt injection.

### Kết quả dự kiến

* **Hệ thống chạy được**: HTTP API kèm backend-for-frontend, đóng gói Docker, có notebook tái lập toàn bộ thí nghiệm.
* **Hiệu năng lớp A + B + C**: bỏ sót dưới 0,1% URL phishing trên tập test, đồng thời tự xác nhận khoảng 50% URL sạch mà không cần LLM (độ trễ khoảng 32 ms, không phụ thuộc mạng).
* **Bộ benchmark lừa đảo tiếng Việt**: không trùng tên miền với dữ liệu huấn luyện, cho thấy khoảng cách giữa các blocklist toàn cầu và dữ liệu Việt Nam.
* **Lớp LLM chống prompt injection**: số trang bị tấn công lật thành safe gần bằng 0, dùng chung một prompt cho hai họ LLM.
* **Kiểm định nhãn**: sửa nhãn sai của các nguồn công khai bằng bằng chứng độc lập với mô hình (luật + gán tay), train và đo lại toàn bộ trên nhãn đã kiểm định.

Ba đóng góp chính và số liệu cụ thể được trình bày ở mục tiếp theo.

---

## Ba đóng góp chính

### 1. Kiến trúc phân tầng ưu tiên recall: gần như không bỏ sót, nhưng chỉ cần LLM cho một nửa lưu lượng

- Trên tập test 81.225 URL (nhãn đã kiểm định), **Lớp A + B + C chỉ bỏ sót 4 trên 38.800 URL phishing
  (0,010 %)**; không có Lớp A (phishing chưa vào feed nào) bỏ sót 12 (0,031 %).
- Đồng thời hệ thống **xác nhận sạch 52,5 % URL sạch trong khoảng 33 ms (p95 36 ms), không gọi LLM và
  không tra cứu mạng**. LLM chỉ xử lý nửa "khó" của lưu lượng.
- Cặp mô hình được **chọn bằng thực nghiệm** theo một quy tắc trên tập val (ít bỏ sót nhất khi nhận ra
  ≥ 50 % URL sạch, hòa thì PR-AUC val cao hơn), từ 5 kiến trúc DL × 3 bộ phân loại: **BiLSTM + XGBoost**
  thắng (XGBoost và LightGBM cùng bỏ sót 19 trên val, XGBoost có PR-AUC cao hơn). So với 8 baseline: mô
  hình chỉ dùng URL bỏ sót **1,0–5,1 %** phishing test, Lớp C bỏ sót 0,03 %.
- **Bỏ tra cứu mạng (DNS, TLS, RDAP)** là lựa chọn thiết kế: tốn 1,4 s (p50) đến 2,5 s cho mỗi host mới.
  Luật đặt trước khi train: bỏ nếu số bỏ sót trên val tăng không quá 30 %. Kết quả: bỏ sót trên val **13**
  (có tra mạng: 15), độ trễ Lớp C từ 1,4 s xuống 32 ms.
- Ablation 3 seed trên Lớp C đang dùng: **thứ hạng Tranco là đặc trưng quyết định** (bỏ nó: bỏ sót trên
  val 18 → 393); bỏ điểm BiLSTM: 18 → 29; bỏ toàn bộ đặc trưng thủ công: 18 → 27. Trên bản có tra mạng, bỏ
  cả DNS + TLS + RDAP chỉ tăng 17 → 24 (PR-AUC giảm nhẹ trên cả 4 tập).

### 2. Bộ benchmark lừa đảo tiếng Việt thực tế, không rò rỉ dữ liệu, cho thấy giới hạn của các giải pháp toàn cầu

- **4.265 URL** (2.681 phishing, 1.584 sạch): phishing lấy từ Chống Lừa Đảo; URL sạch lấy từ tên miền `.vn`
  trong Tranco và các tên miền thương hiệu đã xác minh. Đã kiểm tra **không trùng tên miền** với dữ liệu
  huấn luyện; trang cờ bạc / đầu tư bất hợp pháp nhưng không phải phishing đã được loại sau khi gán nhãn tay.
- **Các feed blocklist toàn cầu chỉ bắt được 0,5 % số phishing tiếng Việt**; để so sánh, VirusTotal (công cụ
  kiểm chứng, không nằm trong pipeline) bắt được 66,3 % (trên mẫu 190 URL).
- Lớp A + B + C **khái quát được sang dữ liệu chưa từng thấy**: bỏ sót **0,56 %** (15 URL), nhận ra 58,3 %
  URL sạch. Các mô hình chỉ dùng URL bỏ sót 12–50 % ở cùng quy tắc.
- Toàn pipeline chạy trên trang thật, đang hoạt động (300 + 300 URL), cảnh báo **91–93 %** trang phishing,
  **warn-F1 0,90–0,91**; 89–90 % trang sạch được kết luận *safe*.

### 3. Lớp LLM chống prompt injection, không phụ thuộc mô hình, có kiểm chứng đối kháng

- **Bộ lọc dựa trên dữ liệu (16 ngôn ngữ)** gỡ văn bản ẩn, trùng màu nền, đẩy ra ngoài màn hình, ký tự vô
  hình và "ASCII smuggling". Nội dung trang được đóng khung là DATA, với marker có nonce ngẫu nhiên mà trang
  không thể giả mạo.
- **Red team** với các tấn công ẩn, đa bước và đa ngôn ngữ: lật tối đa **1 trên 324 trang thật** thành *safe*.
- **Kết hợp chéo giữa các lớp:** LLM nói *safe* nhưng Lớp C chắc chắn ≥ 0,99 thì hạ xuống *suspicious*.
  Nhờ đó tỉ lệ phishing bị kết luận *safe* trên 2.004 trang giữ riêng giảm từ **7,6 % xuống 5,1 %** (gpt-6-luna).
- **Cùng một prompt dùng được cho hai họ LLM.** Kiểm định McNemar cho thấy đổi mô hình là đánh đổi giữa bỏ
  sót và báo nhầm: Haiku bỏ sót ít hơn (p = 0,004) nhưng chặn nhầm nhiều hơn (p = 0,005). Hai lần chạy lặp
  lại khớp 95–97 % kết luận.

---

## Kiểm định nhãn dữ liệu

Nhãn của các nguồn công khai có nhiễu. Đề tài sửa nhãn bằng bằng chứng **độc lập với Lớp C** (để việc đánh
giá Lớp C trên nhãn đã sửa không bị vòng lặp), rồi train lại và đo lại toàn bộ. Luật và từng dòng thay đổi
nằm ở `src/data_collection/audit_labels.py` và `dataset/urls/label_fixes.csv`.

| Luật | Tập | Thay đổi | Số dòng |
|---|---|---|---|
| Domain PhiUSIIL đăng ký sau khi dataset được thu thập (chủ mới, đặc trưng hạ tầng mô tả site khác) | dataset | loại | 2.703 |
| Trang chủ của tên miền xếp hạng Tranco, không nằm trong feed hiện tại, VirusTotal không báo độc (gán tay 24 / 24 trang như vậy là sạch) | dataset | phishing → sạch | 188 |
| Gán nhãn tay 234 URL nghi ngờ (`reports/relabel/hand_review.csv`) | dataset | phishing → sạch / loại | 58 / 2 |
| | tiếng Việt | sạch → phishing / phishing → sạch / loại (cờ bạc, đầu tư bất hợp pháp) | 2 / 6 / 25 |
| | PhreshPhish | phishing → sạch / loại | 5 / 6 |

Nhiễu còn lại, ghi ở phần hạn chế:

| File | Nhiễu còn lại | Nguyên nhân |
|---|---|---|
| `dataset/urls/urls_labeled.csv` (534.908 URL) | 1.762 dòng train nghi sai nhãn (loại khỏi train bằng cross-validation, val/test vẫn còn nhiễu cùng loại); 190 trang chủ phổ biến chưa tra được VirusTotal (giữ nhãn phishing) | Nhãn sạch lấy tại một thời điểm, sau đó site bị hack hoặc đổi chủ; Phishing.Database không xác minh từng URL |
| `data/test_sets/vi/phishing.csv` (2.681 URL) | Một phần host còn mang dáng cờ bạc (chỉ trang chủ được gán tay); toàn bộ được liệt kê từ 5/2024 | Chống Lừa Đảo định nghĩa "lừa đảo" rộng hơn phishing; nhiều tên miền đã chết hoặc đổi chủ |
| `dataset/external/phreshphish_urls.csv` và các tập con | Khoảng 6,7 % lệch so với VirusTotal (trước khi gán tay) | Nhãn gán tự động khi thu thập: trang chủ nền tảng bị gắn theo trang lừa đảo của một tenant |
| `reports/relabel/relabel_subset.csv` (297 trang) | Nhãn dataset lệch 6 trên 148 trang VirusTotal kết luận được: **4,1 %** (khoảng tin cậy 95 %: 1,9–8,6 %) | Bản thân VirusTotal cũng nhiễu: "0 engine báo độc" không có nghĩa là sạch |

---

## Lưu ý khi viết báo cáo

- Kết quả Lớp A trên tập test của dataset bị **lạc quan**, vì feed vừa là nguồn nhãn vừa là bộ chặn. Nên
  nhấn mạnh con số "B + C, không có A" (bỏ sót 12) và kết quả trên tập tiếng Việt / PhreshPhish.
- Trên PhreshPhish, bỏ tra cứu mạng làm số bỏ sót của A + B + C tăng từ 32 lên 43 (0,43 %) nhưng nhận ra
  sạch tăng từ 38 % lên 44 %; bỏ tra mạng phải được trình bày đúng là lựa chọn thiết kế (đánh đổi độ trễ),
  theo luật đã đặt trước khi train.
- VirusTotal chỉ dùng để kiểm chứng (không nằm trong pipeline) và chỉ đo trên mẫu 190 URL; Lớp D vẫn để lọt 4–5 % phishing thành *safe* (trên trang thật tiếng Việt: 7–9 %). Hai điểm này nên
  ghi ở mục **hạn chế**, cùng với nhiễu nhãn ở mục trên.
- Phần gia cố bảo mật (né tránh bằng chuyển hướng, host mã hoá, đầu độc cache, cloaking) **chưa có số đo
  định lượng**. Có thể nêu như đóng góp về kỹ thuật hệ thống, không nên xếp vào nhóm đóng góp khoa học có
  số liệu.

Nguồn số liệu: `IMPROVEMENTS_NOTE.md`, `reports/`.
