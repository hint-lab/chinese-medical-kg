#!/usr/bin/env python3
"""
中文医学知识图谱 - 交互式查询工具（数据库版）
性能：比JSON快10-50倍
"""

from ontology.db_loader import MedicalKnowledgeGraphDB


def print_header():
    print("\n" + "=" * 70)
    print("  中文医学知识图谱 - 交互式查询 (SQLite)")
    print("=" * 70)


def print_menu():
    print("\n请选择查询类型:")
    print("  1. 搜索实体（药物/疾病/基因）")
    print("  2. 模糊搜索")
    print("  3. 查询药物的靶点")
    print("  4. 查询靶点的药物")
    print("  5. 查看统计信息")
    print("  6. 查看实体详情")
    print("  0. 退出")
    print()


def search_entity(db):
    """搜索实体"""
    name = input("请输入实体名称: ").strip()
    if not name:
        print("❌ 名称不能为空")
        return
    
    print("\n选择类型（可选）:")
    print("  1. 药物")
    print("  2. 疾病")
    print("  3. 基因/靶点")
    print("  0. 全部类型")
    
    type_choice = input("选择 (0-3): ").strip()
    type_map = {'1': 'Drug', '2': 'Disease', '3': 'Gene'}
    entity_type = type_map.get(type_choice)
    
    print("\n🔍 搜索中...")
    result = db.search_entity(name, entity_type)
    
    if not result:
        print(f"❌ 未找到 '{name}'")
        return
    
    print(f"\n✅ 找到: {result['name']} ({result['type']})")
    print(f"   标准名称: {result['standard_name']}")
    print(f"   数据来源: {result['source']}")
    
    # 显示别名
    aliases = db.get_aliases(result['name'])
    if aliases:
        print(f"   别名: {', '.join(aliases[:5])}")
        if len(aliases) > 5:
            print(f"         ... 还有 {len(aliases) - 5} 个")


def fuzzy_search(db):
    """模糊搜索"""
    keyword = input("请输入关键词: ").strip()
    if not keyword:
        print("❌ 关键词不能为空")
        return
    
    print("\n🔍 搜索中...")
    results = db.fuzzy_search(keyword, limit=10)
    
    if not results:
        print(f"❌ 未找到包含 '{keyword}' 的实体")
        return
    
    print(f"\n✅ 找到 {len(results)} 个结果:")
    for i, r in enumerate(results, 1):
        print(f"  {i}. {r['name']} ({r['type']})")


def query_drug_targets(db):
    """查询药物的靶点"""
    drug_name = input("请输入药物名称: ").strip()
    if not drug_name:
        print("❌ 名称不能为空")
        return
    
    print(f"\n🔍 查询 '{drug_name}' 的靶点...")
    targets = db.get_drug_targets(drug_name)
    
    if not targets:
        print(f"❌ 未找到 '{drug_name}' 的靶点信息")
        return
    
    print(f"\n✅ 找到 {len(targets)} 个靶点:")
    for i, t in enumerate(targets, 1):
        print(f"  {i}. {t['target_name']}")
        # 显示属性
        for key in ['mode_of_action', 'highest_status']:
            if key in t:
                print(f"     {key}: {t[key]}")


def query_target_drugs(db):
    """查询靶点的药物"""
    target_name = input("请输入靶点名称（如 EGFR, CDK4）: ").strip()
    if not target_name:
        print("❌ 名称不能为空")
        return
    
    print(f"\n🔍 查询针对 '{target_name}' 的药物...")
    drugs = db.get_target_drugs(target_name)
    
    if not drugs:
        print(f"❌ 未找到针对 '{target_name}' 的药物")
        return
    
    print(f"\n✅ 找到 {len(drugs)} 个药物:")
    for i, d in enumerate(drugs, 1):
        print(f"  {i}. {d['drug_name']}")
        for key in ['mode_of_action', 'highest_status']:
            if key in d:
                print(f"     {key}: {d[key]}")


def show_statistics(db):
    """显示统计信息"""
    stats = db.get_statistics()
    
    print("\n" + "=" * 70)
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


def show_entity_detail(db):
    """显示实体详细信息"""
    name = input("请输入实体名称: ").strip()
    if not name:
        print("❌ 名称不能为空")
        return
    
    result = db.search_entity(name)
    
    if not result:
        print(f"❌ 未找到 '{name}'")
        return
    
    print(f"\n{'=' * 70}")
    print(f"  实体详情: {result['name']}")
    print("=" * 70)
    
    # 以格式化方式展示信息
    print(f"\n基本信息:")
    print(f"  名称: {result['name']}")
    print(f"  标准名称: {result['standard_name']}")
    print(f"  类型: {result['type']}")
    print(f"  数据来源: {result['source']}")
    
    # 显示别名
    aliases = db.get_aliases(result['name'])
    if aliases:
        print(f"\n别名 ({len(aliases)} 个):")
        for alias in aliases[:10]:
            print(f"  - {alias}")
        if len(aliases) > 10:
            print(f"  ... 还有 {len(aliases) - 10} 个")
    
    # 如果是药物，查询靶点
    if result['type'] == 'Drug':
        targets = db.get_drug_targets(result['name'])
        if targets:
            print(f"\n作用靶点 ({len(targets)} 个):")
            for t in targets[:5]:
                print(f"  - {t['target_name']}")
                if 'mode_of_action' in t:
                    print(f"    作用方式: {t['mode_of_action']}")
            if len(targets) > 5:
                print(f"  ... 还有 {len(targets) - 5} 个靶点")
    
    # 如果是基因/靶点，查询药物
    elif result['type'] == 'Gene':
        drugs = db.get_target_drugs(result['name'])
        if drugs:
            print(f"\n相关药物 ({len(drugs)} 个):")
            for d in drugs[:5]:
                print(f"  - {d['drug_name']}")
                if 'mode_of_action' in d:
                    print(f"    作用方式: {d['mode_of_action']}")
            if len(drugs) > 5:
                print(f"  ... 还有 {len(drugs) - 5} 个药物")


def main():
    """主函数"""
    print_header()
    
    # 初始化数据库
    print("\n⏳ 连接数据库...")
    try:
        db = MedicalKnowledgeGraphDB()
        print("✅ 数据库连接成功！")
    except Exception as e:
        print(f"❌ 加载失败: {e}")
        print("\n请先运行: python scripts/migrate_to_sqlite.py")
        return
    
    # 主循环
    while True:
        print_menu()
        choice = input("请选择 (0-6): ").strip()
        
        if choice == '0':
            print("\n再见！👋")
            break
        elif choice == '1':
            search_entity(db)
        elif choice == '2':
            fuzzy_search(db)
        elif choice == '3':
            query_drug_targets(db)
        elif choice == '4':
            query_target_drugs(db)
        elif choice == '5':
            show_statistics(db)
        elif choice == '6':
            show_entity_detail(db)
        else:
            print("❌ 无效选择，请重试")
        
        input("\n按回车继续...")
    
    db.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n再见！👋")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()

