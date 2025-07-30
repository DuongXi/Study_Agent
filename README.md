# Hướng dẫn sử dụng

### Cài trợ lý ảo sử dụng mô hình Gemini, Llama
- Cài đặt docker
- Di chuyển vào file main chứa docker-compose
- Thực hiện lệnh trong terminal
``` 
docker-compose build -d
```

### Cài đặt trợ lý ảo sử dụng Claude AI
- Cài đặt Claude desktop
- Thay đổi file claude_desktop_config.json như sau
```
{
        "mcpServers": {
            "assistant": {
                "command": "python",
                "args": [
                    "...path/tools/claude_toolkit.py"
            ]
        }
    }
}
```
- Khởi động lại Claude desktop và chờ kết nối