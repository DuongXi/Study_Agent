# Hệ thống trợ lý ảo AI cố vấn học tập

Trợ lý ảo sử dụng mô hình ngôn ngữ lớn và kiến trúc ReAct agent, nhằm giải quyết một số vấn đề trong học tập giải đáp các thắc mắc về quy định, quy chế, thông tin đại học, thêm thời gian biểu, tìm biểu mẫu, kiểm tra thông tin, tìm thông tin trong thời khoá biểu kỳ sau.

Các thành phần chính của trợ lý ảo bao gồm:
- Thành phần định tuyến phân tích yêu cầu người dùng.
- LLM được gắn tools cải thiện khả năng khi sử dụng các công cụ bên ngoài.
- Tools: Tập hợp các nguồn dữ liệu và dịch vụ LLM có thể truy cập để tìm kiếm thông tin hoặc thực hiện các hành động.
- Bộ nhớ ngắn hạn: sử dụng bộ nhớ ngắn hạn có sẵn trong LangGraph để duy trì ngữ cảnh trong cuộc đối thoại. Khi nếu cuộc trò chuyện trở nên dài hơn, nó có thể đi qua bước tóm tắt các cuộc trò chuyện dài, giúp duy trì tính mạch lạc và ngắn gọn cho đầu ra.
