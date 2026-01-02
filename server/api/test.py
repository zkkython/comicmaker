#!/usr/bin/env python3
"""
测试 API 路由
提供测试用例管理和执行接口
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import subprocess
import json
import sys
import os
from pathlib import Path
import asyncio

router = APIRouter()

# 测试用例元数据
TEST_CASES = [
    # 素材管理测试
    {"id": "materials_list_characters", "name": "列出人物角色", "module": "materials", "test": "test_list_materials_characters"},
    {"id": "materials_list_scenes", "name": "列出场景", "module": "materials", "test": "test_list_materials_scenes"},
    {"id": "materials_list_props", "name": "列出道具", "module": "materials", "test": "test_list_materials_props"},
    {"id": "materials_create_character", "name": "创建人物角色", "module": "materials", "test": "test_create_character"},
    {"id": "materials_get_character", "name": "获取人物角色", "module": "materials", "test": "test_get_character"},
    {"id": "materials_update_character", "name": "更新人物角色", "module": "materials", "test": "test_update_character"},
    {"id": "materials_delete_character", "name": "删除人物角色", "module": "materials", "test": "test_delete_character"},
    {"id": "materials_invalid_type", "name": "无效素材类型", "module": "materials", "test": "test_invalid_material_type"},
    
    # 作品管理测试
    {"id": "works_list", "name": "列出作品", "module": "works", "test": "test_list_works"},
    {"id": "works_create", "name": "创建作品", "module": "works", "test": "test_create_work"},
    {"id": "works_get", "name": "获取作品详情", "module": "works", "test": "test_get_work"},
    {"id": "works_update", "name": "更新作品", "module": "works", "test": "test_update_work"},
    {"id": "works_delete", "name": "删除作品", "module": "works", "test": "test_delete_work"},
    {"id": "works_invalid_aspect_ratio", "name": "无效宽高比", "module": "works", "test": "test_update_work_invalid_aspect_ratio"},
    
    # 剧集管理测试
    {"id": "episodes_list", "name": "列出剧集", "module": "episodes", "test": "test_list_episodes"},
    {"id": "episodes_create", "name": "创建剧集", "module": "episodes", "test": "test_create_episode"},
    {"id": "episodes_get", "name": "获取剧集详情", "module": "episodes", "test": "test_get_episode"},
    {"id": "episodes_update", "name": "更新剧集", "module": "episodes", "test": "test_update_episode"},
    {"id": "episodes_delete", "name": "删除剧集", "module": "episodes", "test": "test_delete_episode"},
    {"id": "episodes_save_script", "name": "保存脚本", "module": "episodes", "test": "test_save_script"},
    {"id": "episodes_get_script", "name": "获取脚本", "module": "episodes", "test": "test_get_script"},
    {"id": "episodes_get_storyboard", "name": "获取分镜脚本", "module": "episodes", "test": "test_get_storyboard"},
    
    # 内容生成测试
    {"id": "content_generate_storyboard", "name": "生成分镜脚本", "module": "content", "test": "test_generate_storyboard"},
    {"id": "content_generate_images", "name": "生成图片", "module": "content", "test": "test_generate_images"},
    {"id": "content_select_image", "name": "选择图片", "module": "content", "test": "test_select_image"},
    {"id": "content_generate_video", "name": "生成视频", "module": "content", "test": "test_generate_video"},
    {"id": "content_generate_audio", "name": "生成音频", "module": "content", "test": "test_generate_audio"},
    {"id": "content_get_shot", "name": "获取分镜详情", "module": "content", "test": "test_get_shot"},
    {"id": "content_update_prompts", "name": "更新提示词", "module": "content", "test": "test_update_prompts"},
]


@router.get("/test-cases")
async def list_test_cases(module: Optional[str] = None):
    """获取测试用例列表"""
    cases = TEST_CASES
    if module:
        cases = [c for c in cases if c["module"] == module]
    return {"test_cases": cases, "total": len(cases)}


@router.post("/test-cases/{test_case_id}/run")
async def run_test_case(test_case_id: str):
    """执行单个测试用例"""
    test_case = next((tc for tc in TEST_CASES if tc["id"] == test_case_id), None)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    # 运行指定的测试
    # 确保工作目录是 server 目录
    server_dir = Path(__file__).parent.parent
    test_file = server_dir / f"tests/test_{test_case['module']}.py"
    test_func = test_case['test']
    
    # 使用绝对路径，pytest 格式：文件路径::函数名（没有空格）
    test_path = f"{test_file}::{test_func}"
    cmd = ["python", "-m", "pytest", test_path, "-v", "--tb=short", "--color=no"]
    
    # 设置环境变量
    env = os.environ.copy()
    env["PYTHONPATH"] = str(server_dir)
    
    try:
        # 在线程池中执行，避免阻塞事件循环
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                cmd,
                cwd=str(server_dir),
                capture_output=True,
                text=True,
                timeout=60,
                env=env
            )
        )
        
        # 解析结果
        passed = result.returncode == 0
        # 合并输出，优先显示错误信息
        output = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
        if result.stdout.strip() and result.stderr.strip():
            output = result.stderr.strip() + "\n\n" + result.stdout.strip()
        
        return {
            "test_case_id": test_case_id,
            "name": test_case["name"],
            "passed": passed,
            "output": output,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "test_case_id": test_case_id,
            "name": test_case["name"],
            "passed": False,
            "output": "测试超时（超过60秒）。可能原因：\n1. 后端服务未启动或响应慢\n2. 测试用例执行时间过长\n3. 网络连接问题\n\n请检查后端服务是否正常运行。",
            "return_code": -1
        }
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        return {
            "test_case_id": test_case_id,
            "name": test_case["name"],
            "passed": False,
            "output": f"执行测试时发生异常：\n{str(e)}\n\n详细错误信息：\n{error_detail}",
            "return_code": -1
        }


@router.post("/test-cases/run-all")
async def run_all_tests(module: Optional[str] = None):
    """批量执行所有测试用例"""
    cases = TEST_CASES
    if module:
        cases = [c for c in cases if c["module"] == module]
    
    results = []
    for test_case in cases:
        result = await run_test_case(test_case["id"])
        results.append(result)
    
    passed_count = sum(1 for r in results if r["passed"])
    total_count = len(results)
    
    return {
        "results": results,
        "summary": {
            "total": total_count,
            "passed": passed_count,
            "failed": total_count - passed_count
        }
    }


@router.get("/test-cases/{test_case_id}")
async def get_test_case_detail(test_case_id: str):
    """获取测试用例详情"""
    test_case = next((tc for tc in TEST_CASES if tc["id"] == test_case_id), None)
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    return {
        "test_case": test_case,
        "description": f"测试 {test_case['name']}"
    }

