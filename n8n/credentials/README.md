# Credentials & Secrets

Ghi chú credential cần tạo thủ công trên n8n hoặc lưu ở file `.env`. Không commit secret lên git.

## 1. PayOS Credentials
Để tích hợp thanh toán PayOS, bạn cần tạo một kênh thanh toán trên Portal của PayOS và chuẩn bị 3 thông tin bảo mật:
- **Client ID**
- **API Key**
- **Checksum Key** (Dùng để mã hóa/tạo và xác thực chữ ký)

Trong các workflow n8n (Onboarding và IPN), hãy mở các **Code Node** ("Build PayOS Params & Sign" và "Verify HMAC-SHA256") và cập nhật trực tiếp `Client ID`, `API Key`, `Checksum Key` vào biến tương ứng, hoặc truyền vào từ biến môi trường của n8n. **KHÔNG** để lộ `API Key` và `Checksum Key` cho bất kỳ ai.

## 2. Discord Bot Token
Hệ thống sử dụng các Node Discord của n8n để gán Role, gửi DM, Kick User. Bạn cần tạo credential trên n8n:
- **Tên**: Discord Bot API
- **Token**: Nhập `Bot YOUR_DISCORD_BOT_TOKEN_HERE`

## 3. Google Sheets OAuth
Hệ thống lưu trữ log tại Google Sheets. Bạn cần kết nối Google Drive API thông qua OAuth2 trong n8n:
- Đi tới **Credentials** > Add new > Search "Google Sheets OAuth2 API".
- Setup Client ID bằng biến `Drive_TOKEN` (ví dụ: `1087011655032-...apps.googleusercontent.com`) mà bạn đã lưu trong file `.env`, cùng với Client Secret tương ứng của tài khoản Google của bạn.
- Nhấn Connect để kết nối tài khoản.
- Sau khi kết nối thành công, vào lại các workflow và chọn lại credential vừa tạo cho tất cả các Node Google Sheets.
