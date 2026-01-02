#!/usr/bin/env python3
"""
测试 text2image_generate 核心接口的脚本

直接测试核心的图片生成功能，不依赖配置文件。

使用方法：
python test_text2image.py --api-key YOUR_API_KEY --prompt "your prompt here"
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入核心接口
from univa.utils.wavespeed_api import text_to_image_generate
from univa.utils.image_process import download_image


def test_core_api(api_key: str, prompt: str, output_dir: str = "results/image"):
    """
    直接测试核心接口：text_to_image_generate + download_image
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 图片生成提示词
        output_dir: 输出目录
    """
    print("=" * 60)
    print("测试核心接口: text_to_image_generate")
    print("=" * 60)
    print(f"\n📝 提示词: {prompt}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '****'}")
    print(f"📁 输出目录: {output_dir}")
    
    try:
        # 步骤1: 调用核心接口生成图片 URL
        print("\n" + "-" * 60)
        print("步骤 1: 调用 text_to_image_generate 生成图片...")
        print("-" * 60)
        
        image_url = text_to_image_generate(
            api_key=api_key,
            prompt=prompt,
            model="flux-kontext-pro",
            provider="wavespeed-ai",
            aspect_ratio="16:9",
            guidance_scale=3.5,
            safety_tolerance="5",
            num_images=1
        )
        
        if image_url is None:
            print("❌ 图片生成失败，返回 None")
            return False
        
        if isinstance(image_url, dict) and not image_url.get('success', True):
            print(f"❌ 图片生成失败: {image_url.get('error', 'Unknown error')}")
            return False
        
        print(f"✅ 图片生成成功!")
        print(f"📷 图片 URL: {image_url}")
        
        # 步骤2: 下载图片到本地
        print("\n" + "-" * 60)
        print("步骤 2: 下载图片到本地...")
        print("-" * 60)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成保存路径
        timestamp = datetime.now().strftime("%m%d%H%M%S")
        safe_prompt = prompt[:30].replace(' ', '_').replace('/', '_')
        image_save_path = os.path.join(output_dir, f"{timestamp}_{safe_prompt}.jpg")
        
        print(f"💾 保存路径: {image_save_path}")
        
        download_image(image_url, save_path=image_save_path)
        
        print(f"✅ 图片下载成功!")
        print(f"📁 完整路径: {os.path.abspath(image_save_path)}")
        
        # 验证文件是否存在
        if os.path.exists(image_save_path):
            file_size = os.path.getsize(image_save_path)
            print(f"📊 文件大小: {file_size / 1024:.2f} KB")
            print("\n" + "=" * 60)
            print("✅ 测试完成！图片已成功生成并保存")
            print("=" * 60)
            return True
        else:
            print("❌ 文件保存失败，文件不存在")
            return False
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='测试 text2image_generate 核心接口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认提示词和 API Key（需要设置环境变量）
  python test_text2image.py --api-key YOUR_API_KEY

  # 自定义提示词
  python test_text2image.py --api-key YOUR_API_KEY --prompt "一只可爱的小猫"

  # 指定输出目录
  python test_text2image.py --api-key YOUR_API_KEY --prompt "sunset" --output-dir "./my_images"
        """
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        required=True,
        help='Wavespeed API 密钥（必需）'
    )
    
    parser.add_argument(
        '--prompt',
        type=str,
        default='A beautiful sunset over the ocean with vibrant colors',
        help='图片生成的提示词（默认: A beautiful sunset over the ocean with vibrant colors）'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results/image',
        help='图片保存目录（默认: results/image）'
    )
    
    args = parser.parse_args()
    
    # 运行测试
    success = test_core_api(
        api_key=args.api_key,
        prompt=args.prompt,
        output_dir=args.output_dir
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

