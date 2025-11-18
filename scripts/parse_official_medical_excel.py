#!/usr/bin/env python3
"""
将官方 Excel（ICD-10 + 国家药品编码）解析成本体 JSON

输入文件（默认）：
- data/国家临床版2.0疾病诊断编码（ICD-10）.xlsx
- data/国家药品编码本位码信息（国产药品）.xlsx
- data/国家药品编码本位码信息（进口药品）.xlsx

如果 data/ 不存在，会自动尝试 data_sources/ 目录（兼容旧版本）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]
# 统一使用项目目录下的 data/ 目录（如果不存在则尝试 data_sources/，兼容旧版本）
DATA_DIR = ROOT_DIR / "data"
if not DATA_DIR.exists():
    DATA_DIR = ROOT_DIR / "data_sources"
ONTOLOGY_DIR = ROOT_DIR / "ontology" / "data"

ICD_FILE = DATA_DIR / "国家临床版2.0疾病诊断编码（ICD-10）.xlsx"
DRUG_DOMESTIC_FILE = DATA_DIR / "国家药品编码本位码信息（国产药品）.xlsx"
DRUG_IMPORT_FILE = DATA_DIR / "国家药品编码本位码信息（进口药品）.xlsx"


def normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def load_json_if_exists(path: Path) -> Dict[str, dict]:
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_json(path: Path, data: Dict[str, dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_icd() -> Dict[str, dict]:
    if not ICD_FILE.exists():
        print(f"[WARN] 找不到 ICD Excel：{ICD_FILE}")
        return {}

    df = pd.read_excel(ICD_FILE)
    df = df.dropna(subset=["疾病诊断编码", "疾病诊断名称"])

    diseases: Dict[str, dict] = {}

    for _, row in df.iterrows():
        code = normalize_text(row.get("疾病诊断编码"))
        name = normalize_text(row.get("疾病诊断名称"))
        if not code or not name:
            continue

        entry = diseases.setdefault(
            name,
            {
                "standard_name": name,
                "type": "Disease",
                "icd_10_codes": set(),
                "aliases": set(),
                "source": "NHCPRC ICD-10 2.0",
            },
        )
        entry["icd_10_codes"].add(code)

        # 如果名称包含别称（如“霍乱，由于……”），拆出主名称
        base_name = name.replace("，", ",").split(",")[0]
        base_name = base_name.replace("（", "(").split("(")[0].strip()
        if base_name and base_name != name:
            entry["aliases"].add(base_name)

    # 转成普通 list
    for name, entry in diseases.items():
        entry["icd_10_codes"] = sorted(entry["icd_10_codes"])
        entry["aliases"] = sorted(entry["aliases"])

    print(f"[ICD] 疾病实体：{len(diseases)} 条")
    return diseases


def parse_drug_excel(file_path: Path, source_label: str) -> Dict[str, dict]:
    if not file_path.exists():
        print(f"[WARN] 找不到药品 Excel：{file_path}")
        return {}

    df = pd.read_excel(file_path, header=1)
    df = df.dropna(subset=["产品名称"])

    records: Dict[str, dict] = {}

    for _, row in df.iterrows():
        name = normalize_text(row.get("产品名称"))
        if not name:
            continue

        entry = records.setdefault(
            name,
            {
                "standard_name": name,
                "type": "Drug",
                "aliases": set(),
                "dosage_forms": set(),
                "specifications": set(),
                "approval_numbers": set(),
                "drug_codes": set(),
                "marketing_holders": set(),
                "manufacturers": set(),
                "sources": set(),
            },
        )

        entry["sources"].add(source_label)

        dosage = normalize_text(row.get("剂型"))
        spec = normalize_text(row.get("规格"))
        holder = normalize_text(row.get("上市许可持有人")) or normalize_text(
            row.get("上市许可持有人中文")
        )
        holder_en = normalize_text(row.get("上市许可持有人英文"))
        manufacturer = normalize_text(row.get("生产单位")) or normalize_text(
            row.get("公司名称中文")
        )
        manufacturer_en = normalize_text(row.get("公司名称英文"))
        approval = (
            normalize_text(row.get("批准文号"))
            or normalize_text(row.get("注册证号"))
            or normalize_text(row.get("审批证号"))
        )
        drug_code = normalize_text(row.get("药品编码"))
        alias = normalize_text(row.get("药品编码备注"))

        if dosage:
            entry["dosage_forms"].add(dosage)
        if spec:
            entry["specifications"].add(spec)
        if holder:
            entry["marketing_holders"].add(holder)
        if holder_en:
            entry["marketing_holders"].add(holder_en)
        if manufacturer:
            entry["manufacturers"].add(manufacturer)
        if manufacturer_en:
            entry["manufacturers"].add(manufacturer_en)
        if approval:
            entry["approval_numbers"].add(approval)
        if drug_code:
            entry["drug_codes"].add(drug_code)
        if alias and alias != name:
            entry["aliases"].add(alias)

    print(f"[NMPA:{source_label}] 原始药品记录：{len(df)} 行，合并后 {len(records)} 条")
    return records


def merge_drug_sources(*sources: Dict[str, dict]) -> Dict[str, dict]:
    merged: Dict[str, dict] = {}
    for source in sources:
        for name, data in source.items():
            entry = merged.setdefault(
                name,
                {
                    "standard_name": name,
                    "type": "Drug",
                    "aliases": set(),
                    "dosage_forms": set(),
                    "specifications": set(),
                    "approval_numbers": set(),
                    "drug_codes": set(),
                    "marketing_holders": set(),
                    "manufacturers": set(),
                    "sources": set(),
                },
            )
            for key in [
                "aliases",
                "dosage_forms",
                "specifications",
                "approval_numbers",
                "drug_codes",
                "marketing_holders",
                "manufacturers",
                "sources",
            ]:
                entry[key].update(data.get(key, []))
    return merged


def extract_generic_name_and_dosage(drug_name: str) -> tuple:
    """
    从药品名称中提取通用名和剂型
    
    Args:
        drug_name: 药品名称，如"阿司匹林注射液"
    
    Returns:
        (generic_name, dosage_form, is_generic)
        - generic_name: 通用名，如"阿司匹林"
        - dosage_form: 剂型，如"注射液"
        - is_generic: 是否为通用名（无剂型后缀）
    """
    if not drug_name:
        return drug_name, None, True
    
    # 常见剂型列表（按长度降序，优先匹配长剂型）
    DOSAGE_FORMS = [
        '注射液', '注射剂', '针剂',
        '肠溶片', '肠溶胶囊',
        '缓释片', '缓释胶囊',
        '控释片', '控释胶囊',
        '分散片', '咀嚼片', '泡腾片', '口含片', '舌下片',
        '薄膜衣片', '糖衣片',
        '片', '片剂',
        '胶囊', '胶囊剂',
        '颗粒', '颗粒剂',
        '散', '散剂',
        '丸', '丸剂',
        '栓', '栓剂',
        '软膏', '软膏剂',
        '乳膏', '乳膏剂',
        '凝胶', '凝胶剂',
        '贴', '贴剂',
        '喷雾', '喷雾剂',
        '吸入', '吸入剂',
        '滴眼', '滴眼液',
        '滴耳', '滴耳液',
        '滴鼻', '滴鼻液',
        '溶液', '溶液剂',
        '混悬液', '混悬剂',
        '乳剂',
        '糖浆', '糖浆剂',
        '口服液',
        '合剂',
    ]
    
    # 按长度排序，优先匹配长剂型
    sorted_forms = sorted(DOSAGE_FORMS, key=len, reverse=True)
    
    # 尝试匹配剂型
    for form in sorted_forms:
        if drug_name.endswith(form):
            generic_name = drug_name[:-len(form)]
            if generic_name:  # 确保提取到通用名
                return generic_name, form, False
    
    # 如果没有匹配到剂型，可能是通用名
    return drug_name, None, True


def finalize_sets(records: Dict[str, dict]) -> Dict[str, dict]:
    """最终化记录，清理集合并提取通用名"""
    for entry in records.values():
        # 清理集合字段
        for key in [
            "aliases",
            "dosage_forms",
            "specifications",
            "approval_numbers",
            "drug_codes",
            "marketing_holders",
            "manufacturers",
            "sources",
        ]:
            entry[key] = sorted(v for v in entry[key] if v)
        
        # 提取通用名和剂型
        drug_name = entry.get("standard_name", "")
        generic_name, dosage_form, is_generic = extract_generic_name_and_dosage(drug_name)
        
        entry["generic_name"] = generic_name
        entry["is_generic"] = is_generic
        if dosage_form:
            entry["dosage_form"] = dosage_form
    
    return records


def main() -> int:
    print("=== 官方医学本体构建 ===")
    print(f"ICD Excel: {ICD_FILE}")
    print(f"国产药品 Excel: {DRUG_DOMESTIC_FILE}")
    print(f"进口药品 Excel: {DRUG_IMPORT_FILE}")
    print()

    existing_diseases = load_json_if_exists(ONTOLOGY_DIR / "diseases.json")
    existing_drugs = load_json_if_exists(ONTOLOGY_DIR / "drugs.json")

    # 疾病
    icd_diseases = parse_icd()
    diseases = existing_diseases
    diseases.update(icd_diseases)
    save_json(ONTOLOGY_DIR / "diseases.json", diseases)
    print(f"[SAVE] 疾病总计：{len(diseases)} 条")

    # 药品
    domestic = parse_drug_excel(DRUG_DOMESTIC_FILE, "NMPA-国内")
    import_ = parse_drug_excel(DRUG_IMPORT_FILE, "NMPA-进口")
    merged_drugs = merge_drug_sources(domestic, import_)
    merged_drugs = finalize_sets(merged_drugs)
    # 把旧的人工数据也合并进去（如果旧条目不在新数据中）
    for name, data in existing_drugs.items():
        if name not in merged_drugs:
            merged_drugs[name] = data
    save_json(ONTOLOGY_DIR / "drugs.json", merged_drugs)
    print(f"[SAVE] 药物总计：{len(merged_drugs)} 条")

    print("\n完成！")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

