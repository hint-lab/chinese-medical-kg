"""
轻量级实体链接器
"""
from typing import Dict, List, Optional, Tuple
from rapidfuzz import fuzz, process
from utils.logger import get_logger

logger = get_logger(__name__)


class TrieNode:
    """前缀树节点"""
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.entity_info = None


class Trie:
    """前缀树，用于快速精确匹配"""
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word: str, entity_info: Dict):
        """插入词条"""
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.entity_info = entity_info
    
    def search(self, word: str) -> Optional[Dict]:
        """精确查找"""
        node = self.root
        for char in word:
            if char not in node.children:
                return None
            node = node.children[char]
        return node.entity_info if node.is_end else None


class EntityLinker:
    """轻量级实体链接器"""
    
    def __init__(self, ontology_dict: Dict[str, Dict]):
        """
        Args:
            ontology_dict: {
                "entity_text": {
                    "standard_name": "标准名称",
                    "type": "实体类型",
                    "aliases": ["别名1", "别名2"],
                    "metadata": {...}
                }
            }
        """
        self.ontology = ontology_dict
        self.trie = Trie()
        self.alias_map = {}  # 别名 -> 标准名映射
        self._build_index()
    
    def _build_index(self):
        """构建索引"""
        logger.info(f"开始构建实体索引: {len(self.ontology)} 条")
        
        for entity_text, entity_info in self.ontology.items():
            # 插入标准名称
            self.trie.insert(entity_text.lower(), entity_info)
            
            # 插入别名
            aliases = entity_info.get("aliases", [])
            for alias in aliases:
                alias_lower = alias.lower()
                self.trie.insert(alias_lower, entity_info)
                self.alias_map[alias_lower] = entity_text
        
        logger.info("实体索引构建完成")
    
    def link(self, entity_text: str, threshold: int = 85) -> Optional[Dict]:
        """
        链接实体到本体
        
        Args:
            entity_text: 待链接的实体文本
            threshold: 模糊匹配阈值 (0-100)
        
        Returns:
            匹配的实体信息，包含 standard_name, type, confidence 等
        """
        if not entity_text:
            return None
        
        # 1. 精确匹配（最快）
        exact_match = self._exact_match(entity_text)
        if exact_match:
            exact_match["confidence"] = 1.0
            exact_match["match_type"] = "exact"
            return exact_match
        
        # 2. 小写匹配
        lower_match = self._exact_match(entity_text.lower())
        if lower_match:
            lower_match["confidence"] = 0.99
            lower_match["match_type"] = "case_insensitive"
            return lower_match
        
        # 3. 部分匹配（搜索词是实体名称的一部分，或实体名称包含搜索词）
        partial_match = self._partial_match(entity_text)
        if partial_match:
            return partial_match
        
        # 4. 模糊匹配（编辑距离）
        fuzzy_match = self._fuzzy_match(entity_text, threshold)
        if fuzzy_match:
            return fuzzy_match
        
        # 未匹配到
        return None
    
    def _exact_match(self, entity_text: str) -> Optional[Dict]:
        """精确匹配"""
        return self.trie.search(entity_text)
    
    def _partial_match(self, entity_text: str) -> Optional[Dict]:
        """部分匹配：搜索词是实体名称的一部分，或实体名称包含搜索词"""
        entity_text_lower = entity_text.lower()
        candidates = []
        
        # 收集所有可能的匹配
        for entity_name, entity_info in self.ontology.items():
            entity_name_lower = entity_name.lower()
            score = 0
            match_type = None
            
            # 如果搜索词是实体名称的一部分
            if entity_text_lower in entity_name_lower:
                # 计算相似度（搜索词长度 / 实体名称长度）
                similarity = len(entity_text) / len(entity_name) if len(entity_name) > 0 else 0
                # 如果相似度足够高（至少30%）
                if similarity >= 0.3:
                    # 优先匹配更短、更简单的名称（如"盐酸二甲双胍"优于"二甲双胍恩格列净片"）
                    # 计算得分：相似度 * (1 - 长度惩罚)
                    length_penalty = min(0.3, (len(entity_name) - len(entity_text)) / 50.0)
                    score = similarity * (1 - length_penalty)
                    match_type = "partial"
            
            # 检查通用名（generic_name）字段
            generic_name = entity_info.get("generic_name", "")
            if generic_name and entity_text_lower in generic_name.lower():
                similarity = len(entity_text) / len(generic_name) if len(generic_name) > 0 else 0
                if similarity >= 0.3:
                    length_penalty = min(0.3, (len(generic_name) - len(entity_text)) / 50.0)
                    generic_score = similarity * (1 - length_penalty) * 0.9  # 通用名匹配稍低优先级
                    if generic_score > score:
                        score = generic_score
                        match_type = "partial_generic"
            
            if score > 0:
                candidates.append((score, entity_name, entity_info, match_type))
        
        # 返回得分最高的匹配
        if candidates:
            candidates.sort(key=lambda x: x[0], reverse=True)
            best_score, best_name, best_info, best_type = candidates[0]
            result = best_info.copy()
            result["confidence"] = min(0.95, best_score)
            result["match_type"] = best_type
            result["matched_text"] = best_name
            return result
        
        return None
    
    def _fuzzy_match(self, entity_text: str, threshold: int) -> Optional[Dict]:
        """模糊匹配"""
        # 使用rapidfuzz进行快速模糊匹配
        all_keys = list(self.ontology.keys()) + list(self.alias_map.keys())
        
        match = process.extractOne(
            entity_text,
            all_keys,
            scorer=fuzz.ratio,
            score_cutoff=threshold
        )
        
        if match:
            matched_text, score, _ = match
            
            # 获取实体信息
            if matched_text in self.ontology:
                entity_info = self.ontology[matched_text].copy()
            elif matched_text.lower() in self.alias_map:
                standard_name = self.alias_map[matched_text.lower()]
                entity_info = self.ontology[standard_name].copy()
            else:
                return None
            
            entity_info["confidence"] = score / 100.0
            entity_info["match_type"] = "fuzzy"
            entity_info["matched_text"] = matched_text
            
            return entity_info
        
        return None
    
    def link_batch(self, entity_texts: List[str], threshold: int = 85) -> List[Optional[Dict]]:
        """批量链接"""
        return [self.link(text, threshold) for text in entity_texts]
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        return {
            "total_entities": len(self.ontology),
            "total_aliases": len(self.alias_map),
            "total_keys": len(self.ontology) + len(self.alias_map),
        }

