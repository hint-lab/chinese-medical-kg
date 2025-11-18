#!/usr/bin/env python3
"""
将JSON数据迁移到SQLite数据库，提升性能
"""

import sqlite3
import json
from pathlib import Path
import time
import sys

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.extract_generic_names import extract_generic_name_and_dosage


class JSONToSQLiteMigrator:
    """JSON到SQLite的迁移工具"""
    
    def __init__(self, db_path='ontology/data/medical_kg.db'):
        self.db_path = Path(db_path)
        self.conn = None
        self.data_dir = Path('ontology/data')
        
    def create_database(self):
        """创建数据库和表结构"""
        print("📦 创建数据库结构...")
        
        # 删除旧数据库
        if self.db_path.exists():
            print(f"⚠️  删除旧数据库: {self.db_path}")
            self.db_path.unlink()
        
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # 创建表
        cursor.executescript('''
            -- 实体表
            CREATE TABLE entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                standard_name TEXT NOT NULL,
                type TEXT NOT NULL,  -- Drug, Disease, Gene
                source TEXT,         -- NMPA, ICD-10, TTD
                generic_name TEXT,   -- 通用名（用于药物）
                dosage_form TEXT,    -- 剂型（用于药物）
                is_generic INTEGER DEFAULT 0,  -- 是否为通用名（0=制剂，1=通用名）
                data TEXT            -- JSON格式存储其他属性
            );
            
            CREATE INDEX idx_entities_name ON entities(name);
            CREATE INDEX idx_entities_standard_name ON entities(standard_name);
            CREATE INDEX idx_entities_type ON entities(type);
            CREATE INDEX idx_entities_source ON entities(source);
            CREATE INDEX idx_entities_generic_name ON entities(generic_name);
            CREATE INDEX idx_entities_is_generic ON entities(is_generic);
            
            -- 别名表（用于快速别名查询）
            CREATE TABLE aliases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_id INTEGER NOT NULL,
                alias TEXT NOT NULL,
                FOREIGN KEY (entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );
            
            CREATE INDEX idx_aliases_alias ON aliases(alias);
            CREATE INDEX idx_aliases_entity_id ON aliases(entity_id);
            
            -- 关系表
            CREATE TABLE relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_entity_id INTEGER,
                target_entity_id INTEGER,
                relation_type TEXT NOT NULL,  -- targets, treats, causes, etc.
                source_name TEXT,  -- 冗余存储，加快查询
                target_name TEXT,  -- 冗余存储，加快查询
                properties TEXT,   -- JSON格式存储关系属性
                FOREIGN KEY (source_entity_id) REFERENCES entities(id) ON DELETE CASCADE,
                FOREIGN KEY (target_entity_id) REFERENCES entities(id) ON DELETE CASCADE
            );
            
            CREATE INDEX idx_relations_source ON relations(source_entity_id);
            CREATE INDEX idx_relations_target ON relations(target_entity_id);
            CREATE INDEX idx_relations_type ON relations(relation_type);
            CREATE INDEX idx_relations_source_name ON relations(source_name);
            CREATE INDEX idx_relations_target_name ON relations(target_name);
            
            -- 元数据表
            CREATE TABLE metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            );
        ''')
        
        self.conn.commit()
        print("✅ 数据库结构创建完成")
    
    def migrate_entities_from_unified(self):
        """从unified_ontology.json迁移实体数据"""
        unified_file = self.data_dir / 'unified_ontology.json'
        
        if not unified_file.exists():
            print(f"⚠️  文件不存在: {unified_file}")
            return {'drugs': 0, 'diseases': 0, 'genes': 0}
        
        print(f"\n📥 从统一本体迁移: {unified_file}")
        
        with open(unified_file, 'r', encoding='utf-8') as f:
            ontology = json.load(f)
        
        entities = ontology.get('entities', {})
        cursor = self.conn.cursor()
        stats = {'drugs': 0, 'diseases': 0, 'genes': 0}
        
        # 迁移药物
        if 'drugs' in entities:
            print(f"\n  处理药物数据...")
            for name, info in entities['drugs'].items():
                standard_name = info.get('standard_name', name)
                sources = info.get('data_sources', ['Unknown'])
                source = ','.join(sources) if isinstance(sources, list) else sources
                
                data_to_store = {k: v for k, v in info.items() 
                               if k not in ['aliases', 'data_sources', 'standard_name', 'generic_name', 'dosage_form', 'is_generic']}
                
                # 提取通用名和剂型
                generic_name = info.get('generic_name')
                dosage_form = info.get('dosage_form')
                is_generic = info.get('is_generic', 0)
                
                # 如果没有通用名字段，尝试从名称中提取
                if not generic_name:
                    generic_name, dosage_form, is_generic_flag = extract_generic_name_and_dosage(name)
                    is_generic = 1 if is_generic_flag else 0
                
                cursor.execute('''
                    INSERT INTO entities (name, standard_name, type, source, generic_name, dosage_form, is_generic, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, standard_name, 'Drug', source, generic_name, dosage_form, is_generic,
                      json.dumps(data_to_store, ensure_ascii=False)))
                
                entity_id = cursor.lastrowid
                stats['drugs'] += 1
                
                # 插入别名
                for alias in info.get('aliases', []):
                    if alias and alias != name:
                        cursor.execute('''
                            INSERT INTO aliases (entity_id, alias) VALUES (?, ?)
                        ''', (entity_id, alias))
                
                if stats['drugs'] % 1000 == 0:
                    self.conn.commit()
                    print(f"    已处理: {stats['drugs']:,} 条...")
            
            self.conn.commit()
            print(f"  ✅ 药物: {stats['drugs']:,} 条")
        
        # 迁移疾病
        if 'diseases' in entities:
            print(f"\n  处理疾病数据...")
            for name, info in entities['diseases'].items():
                standard_name = info.get('standard_name', name)
                sources = info.get('data_sources', ['Unknown'])
                source = ','.join(sources) if isinstance(sources, list) else sources
                
                data_to_store = {k: v for k, v in info.items() 
                               if k not in ['aliases', 'data_sources', 'standard_name']}
                
                cursor.execute('''
                    INSERT INTO entities (name, standard_name, type, source, generic_name, dosage_form, is_generic, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, standard_name, 'Disease', source, None, None, 0,
                      json.dumps(data_to_store, ensure_ascii=False)))
                
                entity_id = cursor.lastrowid
                stats['diseases'] += 1
                
                # 插入别名
                for alias in info.get('aliases', []):
                    if alias and alias != name:
                        cursor.execute('''
                            INSERT INTO aliases (entity_id, alias) VALUES (?, ?)
                        ''', (entity_id, alias))
                
                if stats['diseases'] % 1000 == 0:
                    self.conn.commit()
                    print(f"    已处理: {stats['diseases']:,} 条...")
            
            self.conn.commit()
            print(f"  ✅ 疾病: {stats['diseases']:,} 条")
        
        # 迁移基因
        if 'genes' in entities:
            print(f"\n  处理基因/靶点数据...")
            for name, info in entities['genes'].items():
                standard_name = info.get('standard_name', name)
                sources = info.get('data_sources', ['Unknown'])
                source = ','.join(sources) if isinstance(sources, list) else sources
                
                data_to_store = {k: v for k, v in info.items() 
                               if k not in ['aliases', 'data_sources', 'standard_name']}
                
                cursor.execute('''
                    INSERT INTO entities (name, standard_name, type, source, generic_name, dosage_form, is_generic, data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (name, standard_name, 'Gene', source, None, None, 0,
                      json.dumps(data_to_store, ensure_ascii=False)))
                
                entity_id = cursor.lastrowid
                stats['genes'] += 1
                
                if stats['genes'] % 1000 == 0:
                    self.conn.commit()
                    print(f"    已处理: {stats['genes']:,} 条...")
            
            self.conn.commit()
            print(f"  ✅ 基因: {stats['genes']:,} 条")
        
        return stats
    
    def migrate_relations(self):
        """迁移关系数据"""
        relations_file = self.data_dir / 'enhanced_relations.json'
        
        if not relations_file.exists():
            print(f"⚠️  文件不存在: {relations_file}")
            return 0
        
        print(f"\n🔗 迁移关系数据: {relations_file}")
        
        with open(relations_file, 'r', encoding='utf-8') as f:
            relations = json.load(f)
        
        cursor = self.conn.cursor()
        
        # 创建名称到ID的映射
        print("  构建实体名称索引...")
        cursor.execute('SELECT id, name, standard_name FROM entities')
        name_to_id = {}
        for row in cursor.fetchall():
            entity_id, name, standard_name = row
            name_to_id[name] = entity_id
            if standard_name != name:
                name_to_id[standard_name] = entity_id
        
        total_count = 0
        
        # 迁移各类关系
        relation_types = {
            'target_drug': 'targets',
            'drug_disease': 'treats',
            'target_disease': 'associated_with'
        }
        
        for rel_key, rel_type in relation_types.items():
            if rel_key not in relations:
                continue
            
            print(f"\n  处理 {rel_type} 关系...")
            count = 0
            
            for rel in relations[rel_key]:
                # 获取源实体和目标实体名称
                if rel_key == 'target_drug':
                    source_name = rel.get('target_name')
                    target_name = rel.get('drug_name')
                elif rel_key == 'drug_disease':
                    source_name = rel.get('drug_name')
                    target_name = rel.get('disease_id')
                elif rel_key == 'target_disease':
                    source_name = rel.get('target_name')
                    target_name = rel.get('disease_id')
                else:
                    continue
                
                if not source_name or not target_name:
                    continue
                
                # 查找实体ID
                source_id = name_to_id.get(source_name)
                target_id = name_to_id.get(target_name)
                
                # 删除已存储的名称字段
                properties = {k: v for k, v in rel.items() 
                            if k not in ['target_name', 'drug_name', 'disease_id']}
                
                cursor.execute('''
                    INSERT INTO relations 
                    (source_entity_id, target_entity_id, relation_type, 
                     source_name, target_name, properties)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (source_id, target_id, rel_type, 
                      source_name, target_name, 
                      json.dumps(properties, ensure_ascii=False)))
                
                count += 1
                total_count += 1
                
                if count % 1000 == 0:
                    self.conn.commit()
                    print(f"    已处理: {count:,} 条...")
            
            self.conn.commit()
            print(f"  ✅ {rel_type}: {count:,} 条")
        
        return total_count
    
    def save_metadata(self, stats):
        """保存元数据"""
        print("\n💾 保存元数据...")
        
        cursor = self.conn.cursor()
        metadata = {
            'version': '1.0.0',
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_entities': str(stats['total_entities']),
            'total_relations': str(stats['total_relations']),
            'data_sources': 'NMPA,ICD-10,TTD'
        }
        
        for key, value in metadata.items():
            cursor.execute('''
                INSERT INTO metadata (key, value) VALUES (?, ?)
            ''', (key, value))
        
        self.conn.commit()
        print("✅ 元数据保存完成")
    
    def optimize_database(self):
        """优化数据库"""
        print("\n⚡ 优化数据库...")
        
        cursor = self.conn.cursor()
        
        # 分析表和索引
        cursor.execute('ANALYZE')
        
        # 清理和压缩
        cursor.execute('VACUUM')
        
        self.conn.commit()
        print("✅ 数据库优化完成")
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()


def main():
    """主函数"""
    print("=" * 70)
    print("  JSON → SQLite 数据迁移")
    print("=" * 70)
    
    start_time = time.time()
    
    # 创建迁移器
    migrator = JSONToSQLiteMigrator()
    
    try:
        # 1. 创建数据库
        migrator.create_database()
        
        # 2. 迁移实体数据
        entity_stats = migrator.migrate_entities_from_unified()
        
        # 3. 迁移关系数据
        relation_count = migrator.migrate_relations()
        
        # 4. 保存元数据
        stats = {
            'total_entities': sum(entity_stats.values()),
            'total_relations': relation_count,
            **entity_stats
        }
        migrator.save_metadata(stats)
        
        # 5. 优化数据库
        migrator.optimize_database()
        
        # 统计信息
        elapsed = time.time() - start_time
        db_size = Path(migrator.db_path).stat().st_size / (1024 * 1024)
        
        print("\n" + "=" * 70)
        print("  迁移完成！")
        print("=" * 70)
        print(f"\n📊 统计信息:")
        print(f"  实体总数: {stats['total_entities']:,}")
        print(f"    - 药物: {stats['drugs']:,}")
        print(f"    - 疾病: {stats['diseases']:,}")
        print(f"    - 基因: {stats['genes']:,}")
        print(f"  关系总数: {stats['total_relations']:,}")
        print(f"\n📦 数据库文件:")
        print(f"  路径: {migrator.db_path}")
        print(f"  大小: {db_size:.1f} MB")
        print(f"\n⏱️  用时: {elapsed:.1f} 秒")
        
        print("\n✅ 迁移成功！现在可以使用数据库查询了")
        print("\n下一步:")
        print("  使用交互式查询: python kg_query_db.py")
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        migrator.close()


if __name__ == '__main__':
    main()

