"""
测试实体链接器
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.entity_linker import EntityLinker


def test_entity_linker_basic():
    """测试基本实体链接功能"""
    linker = EntityLinker()
    
    # 加载本体
    ontology_dir = Path(__file__).parent.parent / "ontology" / "data"
    if not ontology_dir.exists():
        print("⚠️ 本体数据不存在，跳过测试")
        return
    
    linker.load_ontology(str(ontology_dir))
    
    # 测试精确匹配
    result = linker.link("帕博利珠单抗", entity_type="drug")
    print(f"精确匹配测试: {result}")
    
    # 测试模糊匹配
    result = linker.link("帕博利单抗", entity_type="drug")
    print(f"模糊匹配测试: {result}")
    
    # 测试疾病
    result = linker.link("非小细胞肺癌", entity_type="disease")
    print(f"疾病匹配测试: {result}")


if __name__ == "__main__":
    test_entity_linker_basic()

