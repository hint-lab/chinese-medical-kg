"""
医学本体加载器
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class OntologyLoader:
    """医学本体数据加载器"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = Path(__file__).parent / "data"
        self.data_dir = Path(data_dir)
        
        self.drugs = {}
        self.diseases = {}
        self.genes = {}
        self.manufacturers = {}
        self.relations = {}
        
        self._load_all()
    
    def _load_all(self):
        """加载所有本体数据"""
        logger.info("开始加载医学本体数据...")
        
        # 加载药物本体
        drug_file = self.data_dir / "drugs.json"
        if drug_file.exists():
            with open(drug_file, 'r', encoding='utf-8') as f:
                self.drugs = json.load(f)
            logger.info(f"加载药物本体: {len(self.drugs)} 条")
        
        # 加载疾病本体
        disease_file = self.data_dir / "diseases.json"
        if disease_file.exists():
            with open(disease_file, 'r', encoding='utf-8') as f:
                self.diseases = json.load(f)
            logger.info(f"加载疾病本体: {len(self.diseases)} 条")
        
        # 加载基因本体
        gene_file = self.data_dir / "genes.json"
        if gene_file.exists():
            with open(gene_file, 'r', encoding='utf-8') as f:
                self.genes = json.load(f)
            logger.info(f"加载基因本体: {len(self.genes)} 条")
        
        # 加载生产商本体
        manufacturer_file = self.data_dir / "manufacturers.json"
        if manufacturer_file.exists():
            with open(manufacturer_file, 'r', encoding='utf-8') as f:
                self.manufacturers = json.load(f)
            logger.info(f"加载生产商本体: {len(self.manufacturers)} 条")
        
        # 加载关系本体
        relation_file = self.data_dir / "relations.json"
        if relation_file.exists():
            with open(relation_file, 'r', encoding='utf-8') as f:
                self.relations = json.load(f)
            logger.info(f"加载关系本体: {len(self.relations)} 条")
        
        logger.info("医学本体数据加载完成")
    
    def get_entity_by_type(self, entity_type: str) -> Dict:
        """根据类型获取实体本体"""
        type_map = {
            "Drug": self.drugs,
            "Disease": self.diseases,
            "Gene_Target": self.genes,
            "Manufacturer": self.manufacturers,
        }
        return type_map.get(entity_type, {})
    
    def get_relation_info(self, relation_type: str) -> Optional[Dict]:
        """获取关系类型信息"""
        return self.relations.get(relation_type)
    
    def validate_relation(self, relation_type: str, source_type: str, target_type: str) -> bool:
        """验证关系类型是否合法"""
        relation_info = self.get_relation_info(relation_type)
        if not relation_info:
            return False
        
        valid_sources = relation_info.get("source_types", [])
        valid_targets = relation_info.get("target_types", [])
        
        return source_type in valid_sources and target_type in valid_targets

