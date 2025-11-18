#!/usr/bin/env python3
"""
SQLite数据库查询接口
性能：比JSON快10-50倍
"""

import sqlite3
import json
from pathlib import Path
from typing import Dict, List, Optional


class MedicalKnowledgeGraphDB:
    """医学知识图谱数据库接口"""
    
    def __init__(self, db_path='ontology/data/medical_kg.db'):
        self.db_path = Path(db_path)
        
        if not self.db_path.exists():
            raise FileNotFoundError(
                f"数据库不存在: {self.db_path}\n"
                f"请先运行: python scripts/migrate_to_sqlite.py"
            )
        
        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 返回字典式结果
    
    def _row_to_dict(self, row) -> Dict:
        """将SQLite Row转换为字典"""
        if row is None:
            return None
        
        result = dict(row)
        
        # 解析JSON字段
        if 'data' in result and result['data']:
            try:
                data = json.loads(result['data'])
                result.update(data)
                del result['data']
            except:
                pass
        
        if 'properties' in result and result['properties']:
            try:
                props = json.loads(result['properties'])
                result.update(props)
                del result['properties']
            except:
                pass
        
        return result
    
    def search_entity(self, name: str, entity_type: Optional[str] = None, 
                     fuzzy_fallback: bool = True, normalize_to_generic: bool = False) -> Optional[Dict]:
        """
        搜索实体（支持精确匹配、别名匹配和模糊匹配）
        
        Args:
            name: 实体名称
            entity_type: 实体类型 (Drug/Disease/Gene)，可选
            fuzzy_fallback: 如果精确匹配失败，是否尝试模糊匹配（默认True）
            normalize_to_generic: 对于药物，是否标准化到通用名（默认False）
        
        Returns:
            实体信息字典，未找到返回None
            如果normalize_to_generic=True且是药物，返回包含通用名信息的字典
        """
        cursor = self.conn.cursor()
        
        # 1. 先尝试精确匹配（名称和标准名称）
        query = 'SELECT * FROM entities WHERE name = ? OR standard_name = ?'
        params = [name, name]
        
        if entity_type:
            query += ' AND type = ?'
            params.append(entity_type)
        
        result = cursor.execute(query, params).fetchone()
        
        if result:
            entity = self._row_to_dict(result)
            
            # 如果启用通用名标准化且是药物
            if normalize_to_generic and entity_type == 'Drug' and entity.get('is_generic') == 0:
                generic_name = entity.get('generic_name')
                if generic_name:
                    # 返回通用名信息
                    generic_info = self.search_by_generic_name(generic_name, return_products=True)
                    return {
                        'matched_product': entity,
                        'generic_name': generic_name,
                        'generic_entity': generic_info['generic_entity'],
                        'related_products': generic_info['products'],
                        'normalized': True
                    }
            
            return entity
        
        # 2. 尝试别名精确匹配
        query = '''
            SELECT e.* FROM entities e
            JOIN aliases a ON e.id = a.entity_id
            WHERE a.alias = ?
        '''
        params = [name]
        
        if entity_type:
            query += ' AND e.type = ?'
            params.append(entity_type)
        
        result = cursor.execute(query, params).fetchone()
        
        if result:
            entity = self._row_to_dict(result)
            
            # 如果启用通用名标准化且是药物
            if normalize_to_generic and entity_type == 'Drug' and entity.get('is_generic') == 0:
                generic_name = entity.get('generic_name')
                if generic_name:
                    generic_info = self.search_by_generic_name(generic_name, return_products=True)
                    return {
                        'matched_product': entity,
                        'generic_name': generic_name,
                        'generic_entity': generic_info['generic_entity'],
                        'related_products': generic_info['products'],
                        'normalized': True
                    }
            
            return entity
        
        # 3. 如果启用模糊回退，尝试包含匹配（部分匹配）
        if fuzzy_fallback:
            # 搜索名称包含输入关键词的实体
            query = '''
                SELECT * FROM entities 
                WHERE (name LIKE ? OR standard_name LIKE ?)
            '''
            params = [f'%{name}%', f'%{name}%']
            
            if entity_type:
                query += ' AND type = ?'
                params.append(entity_type)
            
            query += ' ORDER BY CASE WHEN name = ? THEN 1 WHEN standard_name = ? THEN 2 ELSE 3 END LIMIT 1'
            params.extend([name, name])
            
            result = cursor.execute(query, params).fetchone()
            
            if result:
                return self._row_to_dict(result)
            
            # 也尝试别名包含匹配
            query = '''
                SELECT e.* FROM entities e
                JOIN aliases a ON e.id = a.entity_id
                WHERE a.alias LIKE ?
            '''
            params = [f'%{name}%']
            
            if entity_type:
                query += ' AND e.type = ?'
                params.append(entity_type)
            
            query += ' LIMIT 1'
            result = cursor.execute(query, params).fetchone()
            
            if result:
                return self._row_to_dict(result)
        
        return None
    
    def fuzzy_search(self, name: str, entity_type: Optional[str] = None, 
                    limit: int = 10) -> List[Dict]:
        """
        模糊搜索实体
        
        Args:
            name: 搜索关键词
            entity_type: 实体类型，可选
            limit: 返回结果数量限制
        
        Returns:
            实体列表
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT DISTINCT e.* FROM entities e
            LEFT JOIN aliases a ON e.id = a.entity_id
            WHERE e.name LIKE ? OR e.standard_name LIKE ? OR a.alias LIKE ?
        '''
        params = [f'%{name}%', f'%{name}%', f'%{name}%']
        
        if entity_type:
            query += ' AND e.type = ?'
            params.append(entity_type)
        
        query += f' LIMIT {limit}'
        
        results = cursor.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in results]
    
    def get_entity_by_id(self, entity_id: int) -> Optional[Dict]:
        """根据ID获取实体"""
        cursor = self.conn.cursor()
        result = cursor.execute(
            'SELECT * FROM entities WHERE id = ?', 
            (entity_id,)
        ).fetchone()
        return self._row_to_dict(result) if result else None
    
    def get_aliases(self, entity_name: str) -> List[str]:
        """获取实体的所有别名"""
        entity = self.search_entity(entity_name)
        if not entity:
            return []
        
        cursor = self.conn.cursor()
        results = cursor.execute(
            'SELECT alias FROM aliases WHERE entity_id = ?',
            (entity['id'],)
        ).fetchall()
        
        return [row['alias'] for row in results]
    
    def get_drug_targets(self, drug_name: str) -> List[Dict]:
        """
        查询药物的靶点
        
        Args:
            drug_name: 药物名称
        
        Returns:
            靶点列表，包含关系属性
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT 
                e2.name as target_name,
                e2.standard_name as target_standard_name,
                e2.type as target_type,
                r.properties
            FROM entities e1
            JOIN relations r ON e1.id = r.source_entity_id OR e1.id = r.target_entity_id
            JOIN entities e2 ON (
                CASE 
                    WHEN e1.id = r.source_entity_id THEN e2.id = r.target_entity_id
                    ELSE e2.id = r.source_entity_id
                END
            )
            WHERE (e1.name = ? OR e1.standard_name = ?)
                AND e1.type = 'Drug'
                AND e2.type = 'Gene'
                AND r.relation_type = 'targets'
        '''
        
        results = cursor.execute(query, (drug_name, drug_name)).fetchall()
        return [self._row_to_dict(row) for row in results]
    
    def search_by_generic_name(self, generic_name: str, return_products: bool = True) -> Dict:
        """
        按通用名搜索药物
        
        Args:
            generic_name: 药品通用名（如"阿司匹林"）
            return_products: 是否返回相关制剂列表
        
        Returns:
            包含通用名信息和相关制剂的字典
        """
        cursor = self.conn.cursor()
        
        # 查找通用名实体
        cursor.execute('''
            SELECT * FROM entities 
            WHERE generic_name = ? AND type = 'Drug' AND is_generic = 1
            LIMIT 1
        ''', (generic_name,))
        
        generic_entity = cursor.fetchone()
        
        result = {
            'generic_name': generic_name,
            'generic_entity': self._row_to_dict(generic_entity) if generic_entity else None,
            'products': []
        }
        
        if return_products:
            # 查找所有相关制剂
            cursor.execute('''
                SELECT * FROM entities 
                WHERE generic_name = ? AND type = 'Drug' AND is_generic = 0
                ORDER BY name
            ''', (generic_name,))
            
            products = cursor.fetchall()
            result['products'] = [self._row_to_dict(row) for row in products]
            result['product_count'] = len(products)
        
        return result
    
    def get_target_drugs(self, target_name: str) -> List[Dict]:
        """
        查询靶点的药物
        
        Args:
            target_name: 靶点名称
        
        Returns:
            药物列表，包含关系属性
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT 
                e2.name as drug_name,
                e2.standard_name as drug_standard_name,
                e2.type as drug_type,
                r.properties
            FROM entities e1
            JOIN relations r ON e1.id = r.source_entity_id OR e1.id = r.target_entity_id
            JOIN entities e2 ON (
                CASE 
                    WHEN e1.id = r.source_entity_id THEN e2.id = r.target_entity_id
                    ELSE e2.id = r.source_entity_id
                END
            )
            WHERE (e1.name = ? OR e1.standard_name = ?)
                AND e1.type = 'Gene'
                AND e2.type = 'Drug'
                AND r.relation_type = 'targets'
        '''
        
        results = cursor.execute(query, (target_name, target_name)).fetchall()
        return [self._row_to_dict(row) for row in results]
    
    def get_statistics(self) -> Dict:
        """获取数据库统计信息"""
        cursor = self.conn.cursor()
        
        stats = {}
        
        # 实体统计
        cursor.execute('SELECT type, COUNT(*) as count FROM entities GROUP BY type')
        for row in cursor.fetchall():
            stats[row['type'].lower() + 's'] = int(row['count'])
        
        cursor.execute('SELECT COUNT(*) as total FROM entities')
        stats['total_entities'] = int(cursor.fetchone()['total'])
        
        # 关系统计
        cursor.execute('SELECT COUNT(*) as total FROM relations')
        stats['total_relations'] = int(cursor.fetchone()['total'])
        
        # 别名统计
        cursor.execute('SELECT COUNT(*) as total FROM aliases')
        stats['total_aliases'] = int(cursor.fetchone()['total'])
        
        # 元数据（字符串值）
        cursor.execute('SELECT key, value FROM metadata')
        for row in cursor.fetchall():
            key = row['key']
            value = row['value']
            # 跳过已经计算的数值字段，保留字符串字段
            if key not in ['total_entities', 'total_relations']:
                stats[key] = value
        
        return stats
    
    def execute_sql(self, query: str, params: tuple = ()) -> List[Dict]:
        """执行自定义SQL查询"""
        cursor = self.conn.cursor()
        results = cursor.execute(query, params).fetchall()
        return [self._row_to_dict(row) for row in results]
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """析构函数"""
        self.close()

