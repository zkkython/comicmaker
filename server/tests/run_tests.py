#!/usr/bin/env python3
"""
测试脚本入口
支持批量执行测试和结果统计
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(module=None, cleanup=False, verbose=False):
    """运行测试"""
    cmd = ["python", "-m", "pytest"]
    
    if module:
        # 运行指定模块的测试
        cmd.append(f"tests/test_{module}.py")
    else:
        # 运行所有测试
        cmd.append("tests/")
    
    if verbose:
        cmd.append("-v")
    else:
        # 使用 -v 显示每个测试用例名称
        cmd.append("-v")
    
    # 添加测试输出格式
    cmd.extend(["--tb=short", "--color=yes"])
    
    print(f"执行命令: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent.parent)
    
    print("=" * 60)
    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(description="运行 API 测试")
    parser.add_argument(
        "--module",
        choices=["materials", "works", "episodes", "content"],
        help="指定要运行的测试模块"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="测试前后清理测试数据"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="详细输出"
    )
    
    args = parser.parse_args()
    
    success = run_tests(
        module=args.module,
        cleanup=args.cleanup,
        verbose=args.verbose
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

