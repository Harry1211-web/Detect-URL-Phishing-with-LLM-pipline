# Hướng dẫn tích hợp cho Front End (FE)

Tài liệu này mô tả cách bất kỳ ứng dụng phía người dùng nào (web, tiện ích trình duyệt, app di động,
app desktop...) gọi hệ thống phát hiện website lừa đảo. Giao tiếp là **HTTP + JSON** thông thường, nên
dùng được với mọi ngôn ngữ và framework: chỉ cần thư viện gửi HTTP request của ngôn ngữ đó.

---

## 1. Tổng quan

```
Ứng dụng FE ──HTTPS──> BFF  https://<domain-bff>/api/...  ──> hệ thống AI (4 lớp A → B → C → D)
```

- FE **chỉ gọi BFF**. Không có API key nào trong code FE: BFF tự gắn key phía server.
- Mọi request và response đều là JSON, mã hoá UTF-8.
- Chỉ cần 3 endpoint (mục 3).

| Môi trường | Base URL |
|---|---|
| Chạy thử trên máy | `http://localhost:8080` |
| Production | `https://<domain-bff>` (đội backend cung cấp) |

### Loại ứng dụng FE và điều kiện gọi được

| Loại FE | Điều kiện |
|---|---|
| **Web chạy trong trình duyệt** (mọi framework) | Domain của trang (kể cả cổng khi dev, ví dụ `http://localhost:5173`) phải được backend thêm vào `FE_ORIGINS`. Trình duyệt tự gửi header `Origin`. |
| **Tiện ích trình duyệt** | Gửi kèm Origin của tiện ích (ví dụ `chrome-extension://<id>`); nhờ backend thêm Origin đó vào `FE_ORIGINS`. |
| **App di động / desktop native** (không chạy trong trình duyệt) | App native không tự gửi `Origin`, nên BFF hiện tại trả **403**. **Báo đội backend trước khi tích hợp**: cần cấu hình riêng cho app native. |

---

## 2. Giao thức HTTP

Mọi request kiểm tra URL có dạng:

```http
POST /api/analyze HTTP/1.1
Host: <domain-bff>
Content-Type: application/json
Origin: https://<domain-fe>            (trình duyệt tự thêm)
X-Turnstile-Token: <token>             (chỉ khi backend bật Turnstile, xem mục 6)

{"url": "http://vietcombamk-xacthuc.com/login", "explain": false, "lang": "vi"}
```

Response thành công:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{"url": "http://vietcombamk-xacthuc.com/login", "verdict": "phishing", "decided_by": "fallback_B",
 "explanation": "Label 'vietcombamkxacthuc' — small misspelling of the brand name: ...", "latency_ms": 242.3}
```

Thử ngay bằng `curl` (công cụ dòng lệnh, không phụ thuộc ngôn ngữ của FE):

```bash
curl -X POST http://localhost:8080/api/analyze \
  -H "Origin: http://localhost:5173" -H "Content-Type: application/json" \
  -d '{"url": "http://vietcombamk-xacthuc.com/login"}'
```
Khi test bằng `curl`, phải tự thêm header `Origin` trùng một domain trong `FE_ORIGINS`.

---

## 3. Các endpoint

### 3.1 `POST /api/analyze` — kiểm tra một URL

**Request (JSON body)**

| Trường | Kiểu | Bắt buộc | Mô tả |
|---|---|---|---|
| `url` | string | có | URL cần kiểm tra, tối đa 4096 ký tự. Chấp nhận `http://`, `https://` hoặc host trần (`example.com`). |
| `explain` | boolean | không (mặc định `false`) | `true`: thêm lời giải thích do AI viết (chậm hơn, tốn chi phí hơn). |
| `lang` | string | không (mặc định `"vi"`) | Ngôn ngữ của lời giải thích AI: `vi en zh ja ko th id fr de es it pt nl ru tr ar`. Mã khác → tiếng Anh. |

Bị từ chối (422): URL rỗng, `javascript:`, `data:`, `file:`, `mailto:`, cổng sai.

**Response 200 (JSON)**

| Trường | Kiểu | Ý nghĩa |
|---|---|---|
| `url` | string | URL đã gửi (đã bỏ khoảng trắng đầu/cuối). |
| `verdict` | string | Kết luận: `phishing`, `suspicious` hoặc `clean` (xem 3.2). |
| `decided_by` | string | Lớp đưa ra kết luận (xem 3.3). Dùng cho thống kê / debug, không cần hiện cho người dùng. |
| `explanation` | string | Lý do ngắn, có thể rỗng. Xem lưu ý ở 3.4. |
| `latency_ms` | number | Thời gian xử lý phía server (mili giây). |

FE nên **bỏ qua các trường lạ**: server có thể thêm trường mới mà không báo trước.

### 3.2 Ý nghĩa `verdict` và cách hiển thị đề xuất

| `verdict` | Ý nghĩa | Gợi ý giao diện |
|---|---|---|
| `phishing` | Gần như chắc chắn lừa đảo. | **Chặn**: màu đỏ, "Trang này là lừa đảo", không có nút đi tiếp (hoặc nút ẩn kèm cảnh báo mạnh). |
| `suspicious` | Có dấu hiệu nguy hiểm nhưng chưa đủ bằng chứng, hoặc không đọc được nội dung trang. | **Cảnh báo**: màu cam, "Trang này đáng ngờ", cho phép đi tiếp sau khi người dùng xác nhận. |
| `clean` | Không phát hiện dấu hiệu lừa đảo. | **Cho qua**: màu xanh hoặc không hiện gì. |

Hệ thống thiết kế theo hướng **thà cảnh báo nhầm còn hơn bỏ sót**: khi một bước lỗi hoặc quá thời gian,
kết quả là `suspicious`, không bao giờ là `clean`. Nếu nhận được giá trị `verdict` lạ (phiên bản sau),
FE nên xử lý như `suspicious`.

### 3.3 Các giá trị `decided_by`

| Giá trị | Lớp quyết định |
|---|---|
| `A_blocklist` | URL (hoặc nơi nó chuyển hướng tới) nằm trong danh sách lừa đảo công khai |
| `verified_official_domain` | Tên miền chính chủ đã xác minh của thương hiệu |
| `C_classifier` | Mô hình URL đánh giá an toàn |
| `D_llm` | AI đọc nội dung trang và kết luận |
| `D_llm+C_override` | AI nói an toàn nhưng mô hình URL rất chắc là nguy hiểm → cảnh báo |
| `D_llm+evasion` | Link giấu quá nhiều đích chuyển hướng (kỹ thuật né tránh) → cảnh báo |
| `D_llm+listed_official` | Trang trên tên miền chính chủ nhưng bị một danh sách công khai báo cáo → cảnh báo |
| `fallback_B` | Không có kết luận AI; tên miền mạo danh thương hiệu → lừa đảo |
| `fallback_C` | Không có kết luận AI; dựa vào điểm rủi ro của URL |
| `fallback_lookup_failed` | Lớp C không chấm được URL và không đọc được trang → cảnh báo |

Danh sách có thể được bổ sung: FE nên xử lý theo `verdict`, không phụ thuộc vào `decided_by`.

### 3.4 Lưu ý về `explanation`

- Với các lớp kỹ thuật (blocklist, mô hình URL...), `explanation` là **câu tiếng Anh cố định**.
- Chỉ khi `decided_by` bắt đầu bằng `D_llm` **và** gửi `explain: true`, câu giải thích do AI viết theo `lang`.
- **Khuyến nghị:** hiển thị câu chính theo `verdict` bằng tiếng Việt do FE tự soạn; `explanation` chỉ là
  phần "Xem chi tiết".

### 3.5 `POST /api/feedback` — người dùng báo kết quả sai

Dùng cho nút "Báo sai" (ví dụ trang bị chặn nhầm, hoặc trang lừa đảo mà hệ thống cho qua). Server không
lưu URL, chỉ lưu mã băm để thống kê tỉ lệ báo nhầm.

| Trường | Kiểu | Mô tả |
|---|---|---|
| `url` | string | URL người dùng báo |
| `label` | string | `"clean"` = trang an toàn (bị cảnh báo nhầm), `"phishing"` = trang lừa đảo (bị cho qua) |

```http
POST /api/feedback
Content-Type: application/json

{"url": "https://example.com/page", "label": "clean"}
```
Response 200: `{"ok": true}`

Gợi ý: nếu `verdict` là `clean` thì báo `"phishing"`, ngược lại báo `"clean"`.

### 3.6 `GET /api/health`

Response 200: `{"ok": true}` (hoặc `false`). Dùng để kiểm tra dịch vụ còn hoạt động, ví dụ ẩn tính năng
khi `ok` là `false`. Endpoint này không cần body hay header đặc biệt.

---

## 4. Luồng xử lý đề xuất (giả mã)

Viết lại bằng ngôn ngữ của FE:

```
khi người dùng gửi URL:
    url = bỏ khoảng trắng đầu/cuối(URL)
    nếu url rỗng: báo "Hãy nhập đường link" và dừng
    khoá nút gửi, hiện "Đang kiểm tra..."

    gửi POST {BFF}/api/analyze
        header  Content-Type: application/json
        header  X-Turnstile-Token: <token>          # chỉ khi backend bật Turnstile
        body    {"url": url, "explain": true, "lang": "vi"}
        timeout 45 giây

    nếu hết thời gian chờ:     báo "Hết thời gian chờ, hãy thử lại"
    ngược lại theo mã HTTP:
        200 -> đọc JSON, hiển thị theo verdict:
                 "phishing"   -> khung đỏ  "Trang lừa đảo — không nên truy cập"
                 "suspicious" -> khung cam "Trang đáng ngờ — hãy cẩn thận"
                 "clean"      -> khung xanh "Chưa phát hiện dấu hiệu lừa đảo"
                 giá trị khác -> xử lý như "suspicious"
               hiện explanation trong phần "Chi tiết" (dạng TEXT, xem mục 8)
               hiện nút "Báo sai" -> POST {BFF}/api/feedback
        403 -> "Không xác minh được yêu cầu, hãy tải lại trang"
        413 -> "URL quá dài"
        422 -> "URL không hợp lệ"
        429 -> nếu detail bắt đầu bằng "Daily": "Bạn đã dùng hết lượt kiểm tra hôm nay"
               ngược lại: "Bạn gửi quá nhanh, thử lại sau 1 phút"
        504 -> "Phân tích quá lâu, hãy thử lại"
        khác -> "Dịch vụ đang bận, thử lại sau"

    mở khoá nút gửi
```

---

## 5. Lỗi

| HTTP | Khi nào | `detail` |
|---|---|---|
| 403 | Origin không được phép; thiếu / sai mã xác minh Turnstile | `"Origin not allowed."` / `"Missing human verification."` / `"Human verification failed."` |
| 413 | Body quá lớn (> 16 KB) | `"Request body too large."` |
| 422 | URL hoặc dữ liệu không hợp lệ | danh sách lỗi (xem dưới) |
| 429 | Vượt giới hạn mỗi phút / mỗi ngày | `"Too many requests, retry in a minute."` / `"Daily limit reached, try again tomorrow."` |
| 502 | Dịch vụ phân tích lỗi | `"Analysis service unavailable."` / `"Analysis service error."` |
| 503 | Server thiếu cấu hình | `"Server has no ... configured."` |
| 504 | Phân tích quá lâu | `"The analysis took too long, try again."` |

Lỗi có dạng `{"detail": "<chuỗi>"}`, riêng lỗi 422 có dạng danh sách:

```json
{
  "detail": [
    { "type": "value_error", "loc": ["body", "url"],
      "msg": "Value error, url must be an http(s) URL or a host name", "input": "javascript:alert(1)" }
  ]
}
```

FE nên dựa vào **mã HTTP** để chọn thông báo, không hiện nguyên văn `detail` cho người dùng.

Giới hạn mặc định mỗi IP: **10 request/phút, 300 request/ngày** (tính chung cho `/api/analyze` và
`/api/feedback`). Nếu cần nhiều hơn khi test, nhờ backend đổi `BFF_RATE_PER_MIN` / `BFF_RATE_PER_DAY`.

### Thời gian phản hồi

| Trường hợp | Thời gian thường gặp |
|---|---|
| URL đã biết (blocklist, tên miền chính chủ) | < 0,1 giây |
| URL được mô hình URL xác nhận an toàn | ~0,1–3 giây |
| URL phải nhờ AI đọc trang | 2–15 giây |

- Đặt **timeout phía FE khoảng 45 giây**.
- Luôn hiện trạng thái đang tải và **khoá nút gửi** trong lúc chờ (tránh gửi trùng, tốn lượt).
- Server có cache kết quả: kiểm tra lại cùng một URL thường nhanh hơn.

---

## 6. Xác minh người thật (Cloudflare Turnstile) — chỉ khi server bật

Nếu backend bật Turnstile, **mọi request POST phải kèm header `X-Turnstile-Token`**; thiếu header → 403.
Hỏi backend xem đã bật chưa và lấy **site key** (khoá công khai, để trong FE được).

- Mỗi token dùng được **1 lần** và hết hạn sau 5 phút: lấy token mới cho mỗi request.
- Cách lấy token tuỳ nền tảng; xem tài liệu chính thức của Cloudflare Turnstile cho nền tảng của FE
  (web: nhúng widget; app di động: thường hiển thị widget trong WebView).

---

## 7. Phát triển và kiểm thử

1. Backend chạy API và BFF trên máy, với `FE_ORIGINS` là Origin của FE khi dev (ví dụ
   `http://localhost:5173`; phải trùng chính xác giao thức, tên miền và cổng).
2. FE trỏ địa chỉ BFF về `http://localhost:8080` (đặt trong file cấu hình / biến môi trường của FE, không
   viết cứng trong code).
3. Muốn tắt AI để không tốn chi phí khi dev: backend đặt `USE_LLM=0` (URL khó sẽ ra `suspicious`).
4. URL thử nghiệm:

| URL | Kết quả mong đợi |
|---|---|
| `http://vietcombamk-xacthuc.com/login` | `phishing` (mạo danh Vietcombank) |
| `https://www.vietcombank.com.vn/` | `clean` (tên miền chính chủ) |
| `javascript:alert(1)` | lỗi 422 |

---

## 8. Quy tắc bảo mật bắt buộc

1. **Hiển thị mọi trường dạng TEXT thuần**, không bao giờ diễn giải thành HTML hay markup (với web: không
   dùng `innerHTML` hay tương đương; với app: không đưa vào WebView dạng HTML). `explanation` do AI viết sau
   khi đọc trang của kẻ tấn công, nên có thể bị tác động.
2. **Không biến URL đang bị cảnh báo thành link bấm được**, kể cả trong trang kết quả.
3. **Không đưa API key nào vào FE.** FE không cần và không có key; nếu ai đó yêu cầu thêm key vào FE, đó là
   cấu hình sai.
4. Chỉ gửi URL cần kiểm tra; không gửi kèm cookie, token đăng nhập hay dữ liệu người dùng.
5. Luôn dùng **HTTPS** khi gọi BFF ở production.

---

## 9. Xử lý sự cố

| Hiện tượng | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| Trình duyệt báo lỗi **CORS** | Origin của FE chưa có trong `FE_ORIGINS` (phải trùng chính xác giao thức, tên miền, cổng) | Nhờ backend thêm đúng Origin |
| 403 `Origin not allowed.` | Như trên, hoặc FE là app native / công cụ không gửi `Origin` | Thêm Origin; app native → báo backend (mục 1) |
| 403 `Missing human verification.` | Server bật Turnstile nhưng FE chưa gửi token | Làm theo mục 6 |
| 429 liên tục khi test | Hết lượt mỗi phút / mỗi ngày của IP | Đợi, hoặc nhờ backend nâng giới hạn ở môi trường dev |
| Luôn ra `suspicious` | Server đang tắt AI (`USE_LLM=0`) hoặc AI hết ngân sách | Hỏi backend |
| 504 | Trang đích phản hồi quá chậm | Cho người dùng thử lại |
