#!/usr/bin/env python3
"""
为数据库添加通用名字段
"""

import sqlite3
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extract_generic_names import extract_generic_name_and_dosage


def add_generic_name_column(db_path='ontology/data/medical_kg.db'):
    """为数据库添加通用名字段"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("=" * 70)
    print("  为数据库添加通用名字段")
    print("=" * 70)
    
    # 检查列是否存在
    cursor.execute("PRAGMA table_info(entities)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'generic_name' not in columns:
        print("\n[1/3] 添加通用名字段...")
        cursor.execute('ALTER TABLE entities ADD COLUMN generic_name TEXT')
        cursor.execute('ALTER TABLE entities ADD COLUMN dosage_form TEXT')
        cursor.execute('ALTER TABLE entities ADD COLUMN is_generic INTEGER DEFAULT 0')
        conn.commit()
        print("✅ 字段添加完成")
    else:
        print("\n[1/3] 字段已存在，跳过...")
    
    # 更新数据
    print("\n[2/3] 更新药物数据...")
    cursor.execute('SELECT id, name, type FROM entities WHERE type = ?', ('Drug',))
    drugs = cursor.fetchall()
    
    updated = 0
    for drug_id, drug_name, drug_type in drugs:
        generic_name, dosage_form, is_generic = extract_generic_name_and_dosage(drug_name)
        
        cursor.execute('''
            UPDATE entities 
            SET generic_name = ?, dosage_form = ?, is_generic = ?
            WHERE id = ?
        ''', (generic_name, dosage_form, 1 if is_generic else 0, drug_id))
        
        updated += 1
        if updated % 1000 == 0:
            conn.commit()
            print(f"  已更新: {updated:,} 条...")
    
    conn.commit()
    print(f"✅ 已更新 {updated:,} 条药物数据")
    
    # 创建索引
    print("\n[3/3] 创建索引...")
    try:
        cursor.execute('CREATE INDEX idx_entities_generic_name ON entities(generic_name)')
        cursor.execute('CREATE INDEX idx_entities_is_generic ON entities(is_generic)')
        conn.commit()
        print("✅ 索引创建完成")
    except sqlite3.OperationalError as e:
        if "already exists" in str(e):
            print("✅ 索引已存在")
        else:
            raise
    
    # 统计
    cursor.execute('SELECT COUNT(*) FROM entities WHERE type = ? AND is_generic = 1', ('Drug',))
    generic_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM entities WHERE type = ? AND is_generic = 0', ('Drug',))
    product_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(DISTINCT generic_name) FROM entities WHERE type = ? AND generic_name IS NOT NULL', ('Drug',))
    unique_generic = cursor.fetchone()[0]
    
    print("\n" + "=" * 70)
    print("  更新完成！")
    print("=" * 70)
    print(f"\n📊 统计信息:")
    print(f"  通用名（无剂型）: {generic_count:,}")
    print(f"  制剂（有剂型）: {product_count:,}")
    print(f"  唯一通用名: {unique_generic:,}")
    
    conn.close()


if __name__ == '__main__':
    add_generic_name_column()

