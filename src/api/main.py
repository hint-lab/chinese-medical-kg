#!/usr/bin/env python3
"""
中文医学知识图谱 - FastAPI RESTful API
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi import Path as PathParam
from pydantic import BaseModel
from typing import Optional, List
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ontology.db_loader import MedicalKnowledgeGraphDB

# 创建FastAPI应用
app = FastAPI(
    title="中文医学知识图谱 API",
    description="提供药物、疾病、基因/靶点的查询和关系查询服务",
    version="1.0.0"
)

# 全局数据库连接
_db = None


def get_db():
    """获取数据库连接（单例模式）"""
    global _db
    if _db is None:
        db_path = Path(__file__).parent.parent.parent / 'ontology' / 'data' / 'medical_kg.db'
        if not db_path.exists():
            raise RuntimeError(
                f"数据库不存在: {db_path}\n"
                f"请先运行: python scripts/migrate_to_sqlite.py"
            )
        _db = MedicalKnowledgeGraphDB(str(db_path))
    return _db


# Pydantic模型
class EntityResponse(BaseModel):
    """实体响应模型"""
    id: Optional[int] = None
    name: str
    standard_name: str
    type: str
    source: str
    aliases: List[str] = []


class RelationResponse(BaseModel):
    """关系响应模型"""
    source_name: str
    target_name: str
    relation_type: str
    properties: dict = {}


class StatisticsResponse(BaseModel):
    """统计信息响应模型"""
    total_entities: int
    drugs: int
    diseases: int
    genes: int
    total_relations: int
    total_aliases: int
    data_sources: str
    version: str


# API路由
@app.get("/", tags=["Root"])
async def root():
    """API根路径"""
    return {
        "name": "中文医学知识图谱 API",
        "version": "1.0.0",
        "description": "提供药物、疾病、基因/靶点的查询和关系查询服务",
        "endpoints": {
            "search": "/api/entities/search",
            "fuzzy": "/api/entities/fuzzy",
            "drug_targets": "/api/drugs/{drug_name}/targets",
            "target_drugs": "/api/targets/{target_name}/drugs",
            "statistics": "/api/statistics"
        }
    }


@app.get("/api/entities/search", response_model=EntityResponse, tags=["Entities"])
async def search_entity(
    name: str = Query(..., description="实体名称"),
    entity_type: Optional[str] = Query(None, description="实体类型: Drug, Disease, Gene")
):
    """
    搜索实体（支持精确匹配、别名匹配和部分匹配）
    
    - **name**: 实体名称（支持部分匹配，如"替利珠单抗"可匹配"替利珠单抗注射液"）
    - **entity_type**: 实体类型（可选）
    
    搜索优先级：
    1. 精确匹配（名称或标准名称）
    2. 别名精确匹配
    3. 部分匹配（名称包含关键词）
    4. 别名部分匹配
    """
    try:
        db = get_db()
        result = db.search_entity(name, entity_type)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"未找到实体: {name}")
        
        # 获取别名
        aliases = db.get_aliases(result['name'])
        
        return EntityResponse(
            id=result.get('id'),
            name=result['name'],
            standard_name=result['standard_name'],
            type=result['type'],
            source=result['source'],
            aliases=aliases
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/entities/fuzzy", response_model=List[EntityResponse], tags=["Entities"])
async def fuzzy_search(
    keyword: str = Query(..., description="搜索关键词"),
    entity_type: Optional[str] = Query(None, description="实体类型: Drug, Disease, Gene"),
    limit: int = Query(10, ge=1, le=100, description="返回结果数量限制")
):
    """
    模糊搜索实体
    
    - **keyword**: 搜索关键词
    - **entity_type**: 实体类型（可选）
    - **limit**: 返回结果数量限制（1-100）
    """
    try:
        db = get_db()
        results = db.fuzzy_search(keyword, entity_type, limit)
        
        response = []
        for r in results:
            aliases = db.get_aliases(r['name'])
            response.append(EntityResponse(
                id=r.get('id'),
                name=r['name'],
                standard_name=r['standard_name'],
                type=r['type'],
                source=r['source'],
                aliases=aliases
            ))
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/drugs/{drug_name}/targets", response_model=List[RelationResponse], tags=["Relations"])
async def get_drug_targets(
    drug_name: str = PathParam(..., description="药物名称")
):
    """
    查询药物的靶点
    
    - **drug_name**: 药物名称
    """
    try:
        db = get_db()
        targets = db.get_drug_targets(drug_name)
        
        if not targets:
            raise HTTPException(status_code=404, detail=f"未找到药物 '{drug_name}' 的靶点信息")
        
        response = []
        for t in targets:
            # 提取properties
            properties = {k: v for k, v in t.items() 
                         if k not in ['target_name', 'target_standard_name', 'target_type']}
            
            response.append(RelationResponse(
                source_name=drug_name,
                target_name=t['target_name'],
                relation_type='targets',
                properties=properties
            ))
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/targets/{target_name}/drugs", response_model=List[RelationResponse], tags=["Relations"])
async def get_target_drugs(
    target_name: str = PathParam(..., description="靶点名称")
):
    """
    查询靶点的药物
    
    - **target_name**: 靶点名称
    """
    try:
        db = get_db()
        drugs = db.get_target_drugs(target_name)
        
        if not drugs:
            raise HTTPException(status_code=404, detail=f"未找到针对靶点 '{target_name}' 的药物")
        
        response = []
        for d in drugs:
            # 提取properties
            properties = {k: v for k, v in d.items() 
                         if k not in ['drug_name', 'drug_standard_name', 'drug_type']}
            
            response.append(RelationResponse(
                source_name=target_name,
                target_name=d['drug_name'],
                relation_type='targets',
                properties=properties
            ))
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/statistics", response_model=StatisticsResponse, tags=["Statistics"])
async def get_statistics():
    """
    获取知识图谱统计信息
    """
    try:
        db = get_db()
        stats = db.get_statistics()
        
        return StatisticsResponse(
            total_entities=stats['total_entities'],
            drugs=stats.get('drugs', 0),
            diseases=stats.get('diseases', 0),
            genes=stats.get('genes', 0),
            total_relations=stats['total_relations'],
            total_aliases=stats.get('total_aliases', 0),
            data_sources=stats.get('data_sources', 'Unknown'),
            version=stats.get('version', '1.0.0')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("shutdown")
async def shutdown_event():
    """关闭时清理数据库连接"""
    global _db
    if _db:
        _db.close()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
