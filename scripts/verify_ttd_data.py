#!/usr/bin/env python3
"""
验证 TTD 数据文件是否正确下载
"""

from pathlib import Path

def check_file(file_path, expected_keywords):
    """检查文件是否有效"""
    if not file_path.exists():
        return False, "文件不存在"
    
    # 检查文件大小
    size = file_path.stat().st_size
    if size < 1000:  # 小于1KB，可能是错误文件
        return False, f"文件太小 ({size} 字节)，可能是下载失败"
    
    # 检查文件内容
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            first_lines = ''.join([f.readline() for _ in range(10)])
            
            # 检查是否是 HTML
            if '<!doctype html>' in first_lines.lower() or '<html' in first_lines.lower():
                return False, "文件是 HTML 网页，不是数据文件"
            
            # 检查关键词
            has_keyword = any(keyword in first_lines for keyword in expected_keywords)
            if not has_keyword:
                return False, f"文件格式不正确，应包含: {expected_keywords}"
            
            return True, f"✅ 正确 ({size:,} 字节)"
    except Exception as e:
        return False, f"读取错误: {e}"


def main():
    """主函数"""
    print("=" * 60)
    print("  验证 TTD 数据文件")
    print("=" * 60)
    
    data_dir = Path('data/ttd')
    
    if not data_dir.exists():
        print(f"\n❌ 数据目录不存在: {data_dir}")
        print(f"请先创建目录: mkdir -p {data_dir}")
        return
    
    # 需要检查的文件
    files_to_check = [
        ('P1-01-TTD_target_download.txt', ['TARGETID', 'TARGNAME', 'GENENAME']),
        ('P1-02-TTD_drug_download.txt', ['TTDDRUID', 'DRUGNAME']),
        ('P1-04-Drug_synonyms.txt', ['TTDDRUID', 'SYNONYMS']),
        ('P1-05-Drug_disease.txt', ['TTDDRUID', 'ICD']),
        ('P1-06-Target_disease.txt', ['TARGETID', 'INDICATI']),
        # P1-07 是 Excel 文件，需要单独检查
    ]
    
    print(f"\n数据目录: {data_dir.absolute()}")
    print()
    
    all_valid = True
    
    # 检查 Excel 文件
    excel_file = data_dir / 'P1-07-Drug-TargetMapping.xlsx'
    if excel_file.exists() and excel_file.stat().st_size > 1000:
        print(f"✅ P1-07-Drug-TargetMapping.xlsx           ✅ 正确 ({excel_file.stat().st_size:,} 字节)")
    else:
        print(f"❌ P1-07-Drug-TargetMapping.xlsx           文件不存在或太小")
        all_valid = False
    
    for filename, keywords in files_to_check:
        file_path = data_dir / filename
        is_valid, message = check_file(file_path, keywords)
        
        status = "✅" if is_valid else "❌"
        print(f"{status} {filename:40} {message}")
        
        if not is_valid:
            all_valid = False
    
    print("\n" + "=" * 60)
    
    if all_valid:
        print("✅ 所有文件验证通过！")
        print("\n下一步: python scripts/parse_ttd_data.py")
    else:
        print("❌ 部分文件有问题")
        print("\n请访问以下网址手动下载：")
        print("https://ttd.idrblab.cn/full-data-download")
        print("\n点击每个 'Click to download' 按钮下载文件")
        print(f"保存到: {data_dir.absolute()}")
        print("\n详细说明: cat data/ttd/下载说明.txt")
    
    print("=" * 60)


if __name__ == '__main__':
    main()

