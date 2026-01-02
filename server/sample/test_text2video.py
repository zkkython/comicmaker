#!/usr/bin/env python3
"""
测试 text2video_gen 核心接口的脚本

直接测试核心的视频生成功能，不依赖配置文件。

使用方法：
python test_text2video.py --api-key YOUR_API_KEY --prompt "your prompt here"
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入核心接口
from univa.utils.wavespeed_api import text_to_video_generate


def test_core_api(api_key: str, prompt: str, output_dir: str = "results/video"):
    """
    直接测试核心接口：text_to_video_generate
    
    Args:
        api_key: Wavespeed API 密钥
        prompt: 视频生成提示词
        output_dir: 输出目录
    """
    print("=" * 60)
    print("测试核心接口: text_to_video_generate")
    print("=" * 60)
    print(f"\n📝 提示词: {prompt}")
    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:] if len(api_key) > 14 else '****'}")
    print(f"📁 输出目录: {output_dir}")
    
    try:
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 生成保存路径
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        safe_prompt = prompt[:30].replace(' ', '_').replace('/', '_')
        save_dir = os.path.join(output_dir, f"{timestamp}_{safe_prompt}")
        os.makedirs(save_dir, exist_ok=True)
        
        _time = datetime.now().strftime("%m%d%H%M%S")
        save_path = os.path.join(save_dir, f"{_time}.mp4")
        
        print(f"\n💾 保存路径: {save_path}")
        
        # 步骤1: 调用核心接口生成视频
        print("\n" + "-" * 60)
        print("步骤 1: 调用 text_to_video_generate 生成视频...")
        print("-" * 60)
        print("⏳ 视频生成中，请耐心等待（通常需要几分钟）...")
        
        result = text_to_video_generate(
            api_key=api_key,
            prompt=prompt,
            save_path=save_path,
            model="seedance-v1-pro-t2v-480p",
            provider="bytedance"
        )
        
        # 检查结果
        if not isinstance(result, dict):
            print(f"❌ 返回结果格式错误: {type(result)}")
            print(f"结果内容: {result}")
            return False
        
        if not result.get('success', False):
            error_msg = result.get('error', 'Unknown error')
            print(f"❌ 视频生成失败: {error_msg}")
            return False
        
        print(f"✅ 视频生成成功!")
        
        # 获取输出路径
        output_path = result.get('output_path', save_path)
        message = result.get('message', 'Video generated successfully.')
        
        print(f"💬 消息: {message}")
        print(f"📹 视频路径: {output_path}")
        
        # 验证文件是否存在
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"📊 文件大小: {file_size / (1024 * 1024):.2f} MB")
            print(f"📁 完整路径: {os.path.abspath(output_path)}")
            
            print("\n" + "=" * 60)
            print("✅ 测试完成！视频已成功生成并保存")
            print("=" * 60)
            return True
        else:
            print(f"❌ 文件保存失败，文件不存在: {output_path}")
            return False
            
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    parser = argparse.ArgumentParser(
        description='测试 text2video_gen 核心接口',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认提示词
  python test_text2video.py --api-key YOUR_API_KEY

  # 自定义提示词
  python test_text2video.py --api-key YOUR_API_KEY --prompt "一只可爱的小猫在草地上玩耍"

  # 指定输出目录
  python test_text2video.py --api-key YOUR_API_KEY --prompt "sunset" --output-dir "./my_videos"
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
        default='一个钢铁侠飞行的视频',
        help='视频生成的提示词（默认: A beautiful sunset over the ocean with waves crashing on the shore）'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='results/video',
        help='视频保存目录（默认: results/video）'
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

