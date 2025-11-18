"""
日志工具
"""
import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """
    获取logger实例
    
    Args:
        name: logger名称（通常使用 __name__）
        level: 日志级别（默认INFO）
    
    Returns:
        配置好的logger实例
    """
    if level is None:
        level = logging.INFO
    
    logger = logging.getLogger(name)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 创建控制台handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    
    # 添加handler到logger
    logger.addHandler(handler)
    
    return logger

