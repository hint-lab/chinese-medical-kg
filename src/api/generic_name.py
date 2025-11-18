#!/usr/bin/env python3
"""
通用名查询API端点
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ontology.db_loader import MedicalKnowledgeGraphDB

router = APIRouter(prefix="/api/generic", tags=["Generic Names"])


def get_db():
    """获取数据库连接"""
    from src.api.main import get_db as _get_db
    return _get_db()


@router.get("/search")
async def search_by_generic_name(
    generic_name: str = Query(..., description="药品通用名"),
    include_products: bool = Query(True, description="是否包含相关制剂列表")
):
    """
    按通用名搜索药物
    
    - **generic_name**: 药品通用名（如"阿司匹林"）
    - **include_products**: 是否返回相关制剂列表
    
    返回该通用名的所有制剂信息
    """
    try:
        db = get_db()
        result = db.search_by_generic_name(generic_name, return_products=include_products)
        
        if not result['generic_entity'] and not result['products']:
            raise HTTPException(status_code=404, detail=f"未找到通用名: {generic_name}")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
async def get_products_by_generic(
    generic_name: str = Query(..., description="药品通用名")
):
    """
    获取通用名的所有制剂
    
    - **generic_name**: 药品通用名
    """
    try:
        db = get_db()
        result = db.search_by_generic_name(generic_name, return_products=True)
        
        if not result['products']:
            raise HTTPException(status_code=404, detail=f"未找到通用名 '{generic_name}' 的制剂")
        
        return {
            "generic_name": generic_name,
            "products": [
                {
                    "name": p['name'],
                    "standard_name": p['standard_name'],
                    "dosage_form": p.get('dosage_form'),
                    "source": p.get('source')
                }
                for p in result['products']
            ],
            "count": len(result['products'])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

