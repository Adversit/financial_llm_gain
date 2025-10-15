"""修复tests目录下测试文件的路径设置"""
from pathlib import Path

tests_dir = Path("tests")
test_files = list(tests_dir.glob("test_*.py"))

print(f"找到 {len(test_files)} 个测试文件")

for test_file in test_files:
    print(f"修复: {test_file.name}")
    
    # 读取文件
    with open(test_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 替换路径设置
    old_path = 'sys.path.insert(0, str(Path(__file__).parent))'
    new_path = 'sys.path.insert(0, str(Path(__file__).parent.parent))'
    
    if old_path in content:
        content = content.replace(old_path, new_path)
        
        # 写回文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  ✓ 已修复")
    else:
        print(f"  - 无需修复")

print("\n完成！")
