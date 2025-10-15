"""批量运行所有测试"""
import sys
import subprocess
from pathlib import Path

# 获取tests目录
tests_dir = Path(__file__).parent

# 获取所有测试文件
test_files = sorted(tests_dir.glob("test_*.py"))

print("=" * 60)
print("批量运行所有测试")
print("=" * 60)

print(f"\n找到 {len(test_files)} 个测试文件:")
for i, test_file in enumerate(test_files, 1):
    print(f"  {i}. {test_file.name}")

print("\n" + "=" * 60)

# 运行每个测试
results = []
for i, test_file in enumerate(test_files, 1):
    print(f"\n[{i}/{len(test_files)}] 运行: {test_file.name}")
    print("-" * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=False,
            text=True,
            timeout=120  # 2分钟超时
        )
        
        success = result.returncode == 0
        results.append((test_file.name, success))
        
        if success:
            print(f"✓ {test_file.name} 通过")
        else:
            print(f"✗ {test_file.name} 失败")
            
    except subprocess.TimeoutExpired:
        print(f"✗ {test_file.name} 超时")
        results.append((test_file.name, False))
    except Exception as e:
        print(f"✗ {test_file.name} 错误: {e}")
        results.append((test_file.name, False))

# 汇总结果
print("\n" + "=" * 60)
print("测试结果汇总")
print("=" * 60)

passed = sum(1 for _, success in results if success)
failed = len(results) - passed

for test_name, success in results:
    status = "✓ 通过" if success else "✗ 失败"
    print(f"{status} - {test_name}")

print("\n" + "-" * 60)
print(f"总计: {len(results)} 个测试")
print(f"通过: {passed} 个")
print(f"失败: {failed} 个")
print(f"成功率: {passed/len(results)*100:.1f}%")

if failed == 0:
    print("\n🎉 所有测试通过！")
    sys.exit(0)
else:
    print(f"\n⚠️  有 {failed} 个测试失败")
    sys.exit(1)
