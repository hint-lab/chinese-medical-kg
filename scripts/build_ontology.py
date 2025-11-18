#!/usr/bin/env python3
"""
构建医学本体数据
从官方Excel文件生成标准化的JSON本体文件
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.parsers.parse_icd import parse_icd_excel
from src.parsers.parse_nmpa import parse_nmpa_excel
from src.parsers.parse_pubchem import fetch_drug_info
from src.parsers.parse_ncbi import fetch_gene_info


def main():
    """主函数"""
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description="构建医学本体数据")
    # 统一使用项目目录下的 data/ 目录（如果不存在则尝试 data_sources/，兼容旧版本）
    root_dir = Path(__file__).resolve().parents[1]
    default_data_dir = root_dir / "data"
    if not default_data_dir.exists():
        default_data_dir = root_dir / "data_sources"
    parser.add_argument("--data-dir", default=str(default_data_dir), help="数据源目录")
    parser.add_argument("--output-dir", default="./ontology/data", help="输出目录")
    parser.add_argument("--skip-api", action="store_true", help="跳过API调用")
    args = parser.parse_args()
    
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("开始构建医学本体数据")
    print("=" * 60)
    
    # 1. 解析ICD-10疾病编码
    print("\n[1/3] 解析ICD-10疾病编码...")
    icd_file = data_dir / "国家临床版2.0疾病诊断编码（ICD-10）.xlsx"
    if icd_file.exists():
        diseases = parse_icd_excel(str(icd_file))
        output_file = output_dir / "diseases.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(diseases, f, ensure_ascii=False, indent=2)
        print(f"✅ 解析完成，共 {len(diseases)} 条疾病，保存到: {output_file}")
    else:
        print(f"⚠️ ICD文件不存在: {icd_file}")
    
    # 2. 解析NMPA药品数据
    print("\n[2/3] 解析NMPA药品数据...")
    domestic_file = data_dir / "国家药品编码本位码信息（国产药品）.xlsx"
    imported_file = data_dir / "国家药品编码本位码信息（进口药品）.xlsx"
    
    drugs = []
    if domestic_file.exists():
        drugs.extend(parse_nmpa_excel(str(domestic_file), drug_type="domestic"))
        print(f"  - 国产药品解析完成")
    else:
        print(f"⚠️ 国产药品文件不存在: {domestic_file}")
    
    if imported_file.exists():
        drugs.extend(parse_nmpa_excel(str(imported_file), drug_type="imported"))
        print(f"  - 进口药品解析完成")
    else:
        print(f"⚠️ 进口药品文件不存在: {imported_file}")
    
    if drugs:
        output_file = output_dir / "drugs.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(drugs, f, ensure_ascii=False, indent=2)
        print(f"✅ 解析完成，共 {len(drugs)} 条药品，保存到: {output_file}")
    
    # 3. 初始化基因数据（空白或示例）
    print("\n[3/3] 初始化基因数据...")
    genes = []
    output_file = output_dir / "genes.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(genes, f, ensure_ascii=False, indent=2)
    print(f"✅ 初始化完成，保存到: {output_file}")
    
    print("\n" + "=" * 60)
    print("本体构建完成！")
    print("=" * 60)
    print(f"输出目录: {output_dir.absolute()}")
    print(f"  - 疾病: {len(diseases) if 'diseases' in locals() else 0} 条")
    print(f"  - 药品: {len(drugs)} 条")
    print(f"  - 基因: {len(genes)} 条")
    print("\n后续步骤：")
    print("  1. 运行测试: pytest tests/")
    print("  2. 启动API: python -m src.api.main")


if __name__ == "__main__":
    main()

