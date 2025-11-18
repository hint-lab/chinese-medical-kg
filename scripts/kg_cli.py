#!/usr/bin/env python3
"""
中文医学知识图谱 - 命令行工具 (CLI)
"""

import argparse
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from ontology.db_loader import MedicalKnowledgeGraphDB


def search_entity(db, name, entity_type=None, output_format='text'):
    """搜索实体"""
    result = db.search_entity(name, entity_type)
    
    if not result:
        print(f"❌ 未找到: {name}", file=sys.stderr)
        return None
    
    if output_format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"✅ 找到: {result['name']} ({result['type']})")
        print(f"   标准名称: {result['standard_name']}")
        print(f"   数据来源: {result['source']}")
        
        aliases = db.get_aliases(result['name'])
        if aliases and aliases != ['nan']:
            # 过滤掉nan值
            aliases = [a for a in aliases if a and str(a).lower() != 'nan']
            if aliases:
                print(f"   别名: {', '.join(aliases[:5])}")
                if len(aliases) > 5:
                    print(f"         ... 还有 {len(aliases) - 5} 个")
    
    return result


def fuzzy_search(db, keyword, entity_type=None, limit=10, output_format='text'):
    """模糊搜索"""
    results = db.fuzzy_search(keyword, entity_type, limit)
    
    if not results:
        print(f"❌ 未找到包含 '{keyword}' 的实体", file=sys.stderr)
        return []
    
    if output_format == 'json':
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"✅ 找到 {len(results)} 个结果:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['name']} ({r['type']})")
    
    return results


def get_drug_targets(db, drug_name, output_format='text'):
    """查询药物的靶点"""
    targets = db.get_drug_targets(drug_name)
    
    if not targets:
        print(f"❌ 未找到 '{drug_name}' 的靶点信息", file=sys.stderr)
        return []
    
    if output_format == 'json':
        print(json.dumps(targets, ensure_ascii=False, indent=2))
    else:
        print(f"✅ {drug_name} 的靶点 ({len(targets)} 个):")
        for i, t in enumerate(targets, 1):
            print(f"  {i}. {t['target_name']}")
            for key in ['mode_of_action', 'highest_status']:
                if key in t:
                    print(f"     {key}: {t[key]}")
    
    return targets


def get_target_drugs(db, target_name, output_format='text'):
    """查询靶点的药物"""
    drugs = db.get_target_drugs(target_name)
    
    if not drugs:
        print(f"❌ 未找到针对 '{target_name}' 的药物", file=sys.stderr)
        return []
    
    if output_format == 'json':
        print(json.dumps(drugs, ensure_ascii=False, indent=2))
    else:
        print(f"✅ 针对 {target_name} 的药物 ({len(drugs)} 个):")
        for i, d in enumerate(drugs, 1):
            print(f"  {i}. {d['drug_name']}")
            for key in ['mode_of_action', 'highest_status']:
                if key in d:
                    print(f"     {key}: {d[key]}")
    
    return drugs


def show_statistics(db, output_format='text'):
    """显示统计信息"""
    stats = db.get_statistics()
    
    if output_format == 'json':
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print("=" * 70)
        print("  知识图谱统计")
        print("=" * 70)
        print(f"\n实体总数: {stats.get('total_entities', 0):,}")
        print(f"  💊 药物:     {stats.get('drugs', 0):,}")
        print(f"  🏥 疾病:     {stats.get('diseases', 0):,}")
        print(f"  🧬 基因/靶点: {stats.get('genes', 0):,}")
        print(f"\n关系总数: {stats.get('total_relations', 0):,}")
        print(f"别名总数: {stats.get('total_aliases', 0):,}")
        print(f"\n数据来源: {stats.get('data_sources', 'Unknown')}")
        print(f"版本: {stats.get('version', 'Unknown')}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description='中文医学知识图谱命令行工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 搜索药物
  %(prog)s search 阿司匹林 --type Drug
  
  # 模糊搜索
  %(prog)s fuzzy 糖尿 --limit 5
  
  # 查询药物的靶点
  %(prog)s drug-targets Ibrance
  
  # 查询靶点的药物
  %(prog)s target-drugs CDK4
  
  # 查看统计信息
  %(prog)s stats
  
  # JSON格式输出
  %(prog)s search 阿司匹林 --json
        """
    )
    
    parser.add_argument(
        '--db',
        default=None,
        help='数据库路径 (默认: 项目目录下的 ontology/data/medical_kg.db)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='以JSON格式输出'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # search 命令
    search_parser = subparsers.add_parser('search', help='搜索实体')
    search_parser.add_argument('name', help='实体名称')
    search_parser.add_argument('--type', choices=['Drug', 'Disease', 'Gene'], 
                              help='实体类型')
    
    # fuzzy 命令
    fuzzy_parser = subparsers.add_parser('fuzzy', help='模糊搜索')
    fuzzy_parser.add_argument('keyword', help='搜索关键词')
    fuzzy_parser.add_argument('--type', choices=['Drug', 'Disease', 'Gene'],
                             help='实体类型')
    fuzzy_parser.add_argument('--limit', type=int, default=10,
                             help='返回结果数量限制 (默认: 10)')
    
    # drug-targets 命令
    drug_targets_parser = subparsers.add_parser('drug-targets', 
                                                help='查询药物的靶点')
    drug_targets_parser.add_argument('drug_name', help='药物名称')
    
    # target-drugs 命令
    target_drugs_parser = subparsers.add_parser('target-drugs',
                                                help='查询靶点的药物')
    target_drugs_parser.add_argument('target_name', help='靶点名称')
    
    # stats 命令
    subparsers.add_parser('stats', help='显示统计信息')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # 初始化数据库
    try:
        if args.db is None:
            # 使用默认路径
            db_path = project_root / 'ontology' / 'data' / 'medical_kg.db'
        else:
            db_path = Path(args.db)
        
        db = MedicalKnowledgeGraphDB(str(db_path))
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        print("\n请先运行: python scripts/migrate_to_sqlite.py", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    output_format = 'json' if args.json else 'text'
    
    try:
        # 执行命令
        if args.command == 'search':
            search_entity(db, args.name, args.type, output_format)
        
        elif args.command == 'fuzzy':
            fuzzy_search(db, args.keyword, args.type, args.limit, output_format)
        
        elif args.command == 'drug-targets':
            get_drug_targets(db, args.drug_name, output_format)
        
        elif args.command == 'target-drugs':
            get_target_drugs(db, args.target_name, output_format)
        
        elif args.command == 'stats':
            show_statistics(db, output_format)
    
    except Exception as e:
        print(f"❌ 执行失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == '__main__':
    main()

