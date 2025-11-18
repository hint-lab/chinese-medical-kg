#!/bin/bash
# 中文医学本体 - 一键开始脚本（自动完成所有数据构建）

echo "=========================================="
echo "   中文医学本体（Ontology）快速开始"
echo "=========================================="

# 检查Python版本
echo ""
echo "1️⃣  检查环境..."
python3 --version

# 安装依赖
echo ""
echo "2️⃣  安装依赖..."

# 检查是否使用 uv（更快的包管理器）
if command -v uv &> /dev/null; then
    echo "✅ 检测到 uv，使用 uv 安装依赖（更快）..."
    uv pip install -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装成功（使用 uv）"
    else
        echo "⚠️  uv 安装失败，尝试使用 pip..."
        pip install -q -r requirements.txt
        if [ $? -eq 0 ]; then
            echo "✅ 依赖安装成功（使用 pip）"
        else
            echo "❌ 依赖安装失败"
            exit 1
        fi
    fi
else
    echo "ℹ️  使用 pip 安装依赖（建议安装 uv 以获得更快速度: curl -LsSf https://astral.sh/uv/install.sh | sh）"
    pip install -q -r requirements.txt
    if [ $? -eq 0 ]; then
        echo "✅ 依赖安装成功"
    else
        echo "❌ 依赖安装失败"
        exit 1
    fi
fi

# 检查并构建数据
echo ""
echo "3️⃣  检查并构建数据..."

# 检查统一本体是否已存在且完整
NEED_BUILD=false
if [ -f "ontology/data/unified_ontology.json" ]; then
    stats=$(python3 -c "
import json
try:
    data = json.load(open('ontology/data/unified_ontology.json'))
    stats = data.get('metadata', {}).get('statistics', {})
    print(f\"{stats.get('drugs', 0)},{stats.get('diseases', 0)},{stats.get('genes', 0)},{stats.get('total_entities', 0)}\")
except:
    print('0,0,0,0')
" 2>/dev/null || echo "0,0,0,0")
    
    IFS=',' read -r drug_count disease_count gene_count total_count <<< "$stats"
    
    if [ "$total_count" -gt 0 ] && [ "$gene_count" -gt 0 ]; then
        echo "✅ 统一本体数据已就绪:"
        echo "   - 药物: $drug_count 条"
        echo "   - 疾病: $disease_count 条"
        echo "   - 基因/靶点: $gene_count 条"
        echo "   - 总计: $total_count 条实体"
        NEED_BUILD=false
    else
        echo "⚠️  统一本体数据不完整，需要重新构建"
        NEED_BUILD=true
    fi
else
    echo "⚠️  统一本体数据不存在，开始构建..."
    NEED_BUILD=true
fi

# 如果需要构建，执行完整的数据构建流程
if [ "$NEED_BUILD" = true ]; then
    echo ""
    echo "📦 开始数据构建流程..."
    
    # 步骤1: 解析官方 Excel 数据（如果存在）
    echo ""
    echo "[步骤 1/4] 解析官方 Excel 数据..."
    if [ -f "data/国家临床版2.0疾病诊断编码（ICD-10）.xlsx" ] || \
       [ -f "data_sources/国家临床版2.0疾病诊断编码（ICD-10）.xlsx" ]; then
        python scripts/parse_official_medical_excel.py
        if [ $? -eq 0 ]; then
            echo "✅ Excel 数据解析完成"
        else
            echo "⚠️  Excel 数据解析失败，继续其他步骤"
        fi
    else
        echo "ℹ️  未找到 Excel 文件，跳过此步骤"
        echo "   提示: 将 Excel 文件放到 data/ 或 data_sources/ 目录"
    fi
    
    # 步骤2: 检查并下载/解析 TTD 数据
    echo ""
    echo "[步骤 2/4] 处理 TTD 数据（包含基因/靶点）..."
    
    # 检查 TTD 数据目录
    TTD_DIR="data/ttd"
    if [ ! -d "$TTD_DIR" ]; then
        TTD_DIR="data_sources/ttd"
    fi
    
    # 检查 TTD 数据文件是否存在
    if [ -f "$TTD_DIR/P1-01-TTD_target_download.txt" ] && \
       [ -f "$TTD_DIR/P1-02-TTD_drug_download.txt" ]; then
        echo "✅ 发现 TTD 数据文件，开始解析..."
        python scripts/parse_ttd_data.py
        if [ $? -eq 0 ]; then
            echo "✅ TTD 数据解析完成"
        else
            echo "⚠️  TTD 数据解析失败"
        fi
    else
        echo "⚠️  TTD 数据文件不存在"
        echo "   提示: 运行 './scripts/download_ttd_data.sh' 下载 TTD 数据"
        echo "   或访问: https://ttd.idrblab.cn/full-data-download"
        echo ""
        read -p "是否现在下载 TTD 数据？[y/N] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./scripts/download_ttd_data.sh
            if [ $? -eq 0 ]; then
                echo "✅ TTD 数据下载完成，开始解析..."
                python scripts/parse_ttd_data.py
            fi
        else
            echo "⚠️  跳过 TTD 数据，将只使用基础数据（无基因/靶点）"
        fi
    fi
    
    # 步骤3: 合并所有数据源
    echo ""
    echo "[步骤 3/4] 合并所有数据源到统一本体..."
    python scripts/merge_ontology.py
    if [ $? -eq 0 ]; then
        echo "✅ 数据合并完成"
        
        # 显示统计信息
        if [ -f "ontology/data/unified_ontology.json" ]; then
            stats=$(python3 -c "
import json
try:
    data = json.load(open('ontology/data/unified_ontology.json'))
    stats = data.get('metadata', {}).get('statistics', {})
    print(f\"{stats.get('drugs', 0)},{stats.get('diseases', 0)},{stats.get('genes', 0)},{stats.get('total_entities', 0)}\")
except:
    print('0,0,0,0')
" 2>/dev/null || echo "0,0,0,0")
            
            IFS=',' read -r drug_count disease_count gene_count total_count <<< "$stats"
            echo ""
            echo "📊 数据统计:"
            echo "   - 药物: $drug_count 条"
            echo "   - 疾病: $disease_count 条"
            echo "   - 基因/靶点: $gene_count 条"
            echo "   - 总计: $total_count 条实体"
        fi
    else
        echo "❌ 数据合并失败"
        exit 1
    fi
    
    # 步骤4: 迁移到 SQLite 数据库
    echo ""
    echo "[步骤 4/5] 迁移到 SQLite 数据库（提升性能）..."
    python scripts/migrate_to_sqlite.py
    if [ $? -eq 0 ]; then
        echo "✅ SQLite 数据库创建完成"
        
        # 显示数据库统计
        if [ -f "ontology/data/medical_kg.db" ]; then
            db_size=$(du -h ontology/data/medical_kg.db | cut -f1)
            echo "   - 数据库文件: ontology/data/medical_kg.db ($db_size)"
        fi
    else
        echo "⚠️  SQLite 数据库迁移失败（可选步骤）"
    fi
    
    # 步骤5: 检查并添加通用名字段（如果数据库已存在但缺少字段）
    echo ""
    echo "[步骤 5/5] 检查数据库字段完整性..."
    if [ -f "ontology/data/medical_kg.db" ]; then
        # 检查是否需要添加 generic_name 字段
        has_generic=$(python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('ontology/data/medical_kg.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(entities)')
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    print('1' if 'generic_name' in columns else '0')
except:
    print('0')
" 2>/dev/null || echo "0")
        
        if [ "$has_generic" = "0" ]; then
            echo "⚠️  数据库缺少 generic_name 字段，正在添加..."
            python scripts/add_generic_name_to_db.py
            if [ $? -eq 0 ]; then
                echo "✅ 通用名字段添加完成"
            else
                echo "⚠️  通用名字段添加失败"
            fi
        else
            echo "✅ 数据库字段完整"
        fi
    fi
fi

# 检查 SQLite 数据库
echo ""
echo "4️⃣  检查 SQLite 数据库..."
if [ -f "ontology/data/medical_kg.db" ]; then
    echo "✅ SQLite 数据库已就绪"
    db_size=$(du -h ontology/data/medical_kg.db | cut -f1)
    echo "   - 文件大小: $db_size"
    
    # 检查数据库字段完整性
    has_generic=$(python3 -c "
import sqlite3
try:
    conn = sqlite3.connect('ontology/data/medical_kg.db')
    cursor = conn.cursor()
    cursor.execute('PRAGMA table_info(entities)')
    columns = [col[1] for col in cursor.fetchall()]
    conn.close()
    print('1' if 'generic_name' in columns else '0')
except:
    print('0')
" 2>/dev/null || echo "0")
    
    if [ "$has_generic" = "0" ]; then
        echo "⚠️  数据库缺少 generic_name 字段"
        echo "   提示: 运行 'python scripts/add_generic_name_to_db.py' 添加字段"
        echo ""
        read -p "是否现在添加 generic_name 字段？[Y/n] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            python scripts/add_generic_name_to_db.py
        fi
    fi
else
    echo "⚠️  SQLite 数据库不存在"
    echo "   提示: 运行 'python scripts/migrate_to_sqlite.py' 创建数据库"
fi

# 询问是否使用 Docker 部署
echo ""
echo "5️⃣  选择部署方式..."
echo ""
echo "请选择部署方式:"
echo "  1) 本地运行演示脚本（默认）"
echo "  2) Docker 部署 API 服务"
echo "  3) 跳过演示，直接查看使用指南"
echo ""
read -p "请输入选项 [1-3] (默认: 1): " deploy_choice
deploy_choice=${deploy_choice:-1}

case $deploy_choice in
    2)
        echo ""
        echo "🐳 开始 Docker 部署..."
        
        # 检查 Docker 是否安装
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker 未安装，请先安装 Docker"
            echo "   安装指南: https://docs.docker.com/get-docker/"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null; then
            echo "❌ docker-compose 未安装，请先安装 docker-compose"
            echo "   安装指南: https://docs.docker.com/compose/install/"
            exit 1
        fi
        
        echo ""
        echo "选择 Docker 配置:"
        echo "  1) 标准版（docker-compose.yml）"
        echo "  2) 国内加速版（docker-compose.cn.yml，推荐）"
        read -p "请输入选项 [1-2] (默认: 2): " docker_choice
        docker_choice=${docker_choice:-2}
        
        if [ "$docker_choice" = "2" ]; then
            COMPOSE_FILE="docker-compose.cn.yml"
            echo "✅ 使用国内加速版配置"
        else
            COMPOSE_FILE="docker-compose.yml"
            echo "✅ 使用标准配置"
        fi
        
        echo ""
        echo "正在启动 Docker 服务..."
        docker-compose -f $COMPOSE_FILE up -d
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Docker 服务启动成功！"
            echo ""
            echo "📚 访问信息:"
            echo "  - API 文档: http://localhost:8000/docs"
            echo "  - API 根路径: http://localhost:8000/"
            echo ""
            echo "🔧 常用命令:"
            echo "  - 查看日志: docker-compose -f $COMPOSE_FILE logs -f"
            echo "  - 停止服务: docker-compose -f $COMPOSE_FILE down"
            echo "  - 重启服务: docker-compose -f $COMPOSE_FILE restart"
            echo ""
            echo "等待服务启动（约 10-30 秒）..."
            sleep 5
            
            # 检查服务状态
            if curl -f http://localhost:8000/ &> /dev/null; then
                echo "✅ API 服务已就绪！"
            else
                echo "⏳ 服务正在启动中，请稍候访问 http://localhost:8000/docs"
            fi
        else
            echo "❌ Docker 服务启动失败，请检查错误信息"
        fi
        ;;
    3)
        echo ""
        echo "⏭️  跳过演示"
        ;;
    *)
        # 默认运行演示脚本
        echo ""
        echo "6️⃣  运行演示脚本..."
        echo ""
        python3 example_ontology_usage.py
        ;;
esac

echo ""
echo "=========================================="
echo "  完成！"
echo "=========================================="
echo ""

# 显示最终统计和使用指南
if [ -f "ontology/data/unified_ontology.json" ]; then
    stats=$(python3 -c "
import json
try:
    data = json.load(open('ontology/data/unified_ontology.json'))
    stats = data.get('metadata', {}).get('statistics', {})
    print(f\"{stats.get('drugs', 0)},{stats.get('diseases', 0)},{stats.get('genes', 0)},{stats.get('total_entities', 0)}\")
except:
    print('0,0,0,0')
" 2>/dev/null || echo "0,0,0,0")
    
    IFS=',' read -r drug_count disease_count gene_count total_count <<< "$stats"
    
    echo "✅ 数据已准备完成！"
    echo ""
    echo "📊 数据统计:"
    echo "   - 药物: $drug_count 条"
    echo "   - 疾病: $disease_count 条"
    echo "   - 基因/靶点: $gene_count 条"
    echo "   - 总计: $total_count 条实体"
    echo ""
    echo "📚 使用方式:"
    echo ""
    echo "1. CLI 命令行工具:"
    echo "   python scripts/kg_cli.py search 阿司匹林 --type Drug"
    echo "   python scripts/kg_cli.py drug-targets Ibrance"
    echo ""
    echo "2. FastAPI 服务:"
    echo "   python -m src.api.main"
    echo "   访问: http://localhost:8000/docs"
    echo ""
    echo "3. Python API:"
    echo "   from ontology.db_loader import MedicalKnowledgeGraphDB"
    echo "   db = MedicalKnowledgeGraphDB()"
    echo "   result = db.search_entity('阿司匹林')"
    echo ""
    echo "4. Docker 部署（推荐）🐳:"
    echo "   # 标准部署"
    echo "   docker-compose up -d"
    echo ""
    echo "   # 国内用户加速版（推荐）"
    echo "   docker-compose -f docker-compose.cn.yml up -d"
    echo ""
    echo "   # 访问 API 文档"
    echo "   http://localhost:8000/docs"
    echo ""
    echo "   详细部署指南: cat docker_deployment_guide.md"
    echo ""
    if [ -f "ontology/data/medical_kg.db" ]; then
        echo "✅ SQLite 数据库已就绪，查询速度提升 10-50 倍！"
    else
        echo "💡 提示: 运行 'python scripts/migrate_to_sqlite.py' 创建数据库以提升性能"
    fi
else
    echo "⚠️  数据构建未完成，请检查错误信息"
    echo ""
    echo "📋 手动构建步骤:"
    echo "  1. python scripts/parse_official_medical_excel.py  # 解析 Excel"
    echo "  2. python scripts/parse_ttd_data.py                # 解析 TTD"
    echo "  3. python scripts/merge_ontology.py                # 合并数据"
    echo "  4. python scripts/migrate_to_sqlite.py             # 迁移到数据库"
fi

echo ""
