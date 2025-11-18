"""解析ICD-10疾病编码Excel文件"""

import pandas as pd
from typing import List, Dict


def parse_icd_excel(file_path: str) -> List[Dict]:
    """
    解析ICD-10疾病编码Excel文件
    
    Args:
        file_path: Excel文件路径
        
    Returns:
        疾病实体列表
    """
    df = pd.read_excel(file_path)
    
    diseases = []
    for _, row in df.iterrows():
        disease_name = str(row.get("疾病诊断名称", "")).strip()
        disease_code = str(row.get("疾病诊断编码", "")).strip()
        
        if not disease_name or disease_name == "nan":
            continue
        
        # 构建实体
        entity = {
            "standard_name": disease_name,
            "type": "Disease",
            "aliases": [],
            "icd_10_codes": [disease_code] if disease_code and disease_code != "nan" else [],
            "source": "ICD-10 国家临床版 2.0",
            "category": "disease"
        }
        
        diseases.append(entity)
    
    return diseases

