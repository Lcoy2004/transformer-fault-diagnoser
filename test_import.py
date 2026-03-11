import sys
import pandas as pd
import tempfile
import os
from utils.data_importer import DataImporter

# 创建测试数据
data = {
    'H2': [10, 20, 30],
    'CH4': [5, 15, 25],
    'C2H6': [2, 12, 22],
    'C2H4': [3, 13, 23],
    'C2H2': [1, 11, 21],
    '故障类别': ['过热', '放电', '过热'],
    '故障位置': ['绕组', '绝缘', '绕组']
}

df = pd.DataFrame(data)

# 创建临时Excel文件
with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
    temp_file_path = temp_file.name

df.to_excel(temp_file_path, index=False)
print(f"创建测试文件: {temp_file_path}")

# 测试数据导入
data_importer = DataImporter()
table_name = 'oil_chromatography'

try:
    imported_count = data_importer.import_to_table(temp_file_path, table_name)
    print(f"测试导入结果: 成功导入 {imported_count} 条记录")
except Exception as e:
    print(f"测试导入失败: {e}")
finally:
    # 清理临时文件
    os.unlink(temp_file_path)
    print("临时文件已清理")
