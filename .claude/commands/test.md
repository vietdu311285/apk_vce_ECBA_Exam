# /test — Tạo Unit Tests Tự động

## Kích hoạt
Gõ: `/test @[tên_file_hoặc_function]`

## Quy trình Claude sẽ thực hiện
1. Đọc code implementation
2. Xác định các cases cần test:
   - ✅ Happy path: input hợp lệ, kết quả đúng
   - ⚠️ Edge cases: input rỗng, None, số âm, chuỗi dài
   - ❌ Error cases: input sai kiểu, ngoài phạm vi

## Framework sử dụng
- **Python**: pytest
- **JavaScript/TypeScript**: Vitest hoặc Jest
- **React**: React Testing Library

## Output — Python example
```python
# tests/test_[module].py
import pytest
from src.[module] import [function]

class Test[FunctionName]:
    
    def test_happy_path(self):
        """Test with valid input"""
        result = [function](valid_input)
        assert result == expected_output
    
    def test_empty_input(self):
        """Test with empty input"""
        with pytest.raises(ValueError):
            [function]("")
    
    def test_none_input(self):
        """Test with None"""
        with pytest.raises(TypeError):
            [function](None)
```

## Chạy tests
```bash
# Python
pytest tests/ -v
pytest tests/test_[module].py -v --tb=short

# JavaScript
npm test
npx vitest run
```
