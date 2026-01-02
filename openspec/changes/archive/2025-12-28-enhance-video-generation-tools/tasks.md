# 任务列表

## 后端实现

1. **实现 vidu 视频生成 API 函数**
   - 在 `server/utils/video_api.py` 中添加 `vidu_reference_to_video` 函数
   - 支持多图片输入（最多7张）
   - 支持 aspect_ratio、resolution、duration 参数
   - 实现图片上传到 OSS 或直接使用 base64
   - 实现轮询机制获取生成结果

2. **实现 sora 视频生成 API 函数**
   - 在 `server/utils/video_api.py` 中添加 `sora_2_image_to_video` 函数
   - 支持单图片输入
   - 支持 duration 参数（4、8、12秒）
   - 实现图片上传到 OSS 或直接使用 base64
   - 实现轮询机制获取生成结果

3. **实现 wan 视频生成 API 函数**
   - 在 `server/utils/video_api.py` 中添加 `wan_2_5_image_to_video` 和 `wan_2_6_image_to_video` 函数
   - 支持单图片输入
   - 支持 resolution、duration、enable_prompt_expansion 等参数
   - 实现图片上传到 OSS 或直接使用 base64
   - 实现轮询机制获取生成结果

4. **更新工具执行逻辑**
   - 在 `server/api/tools.py` 中实现 `vidu_ref_image_to_video` 工具类型
   - 在 `server/api/tools.py` 中实现 `sora_image_to_video` 工具类型
   - 在 `server/api/tools.py` 中将 `text_to_video` 改为 `wan_image_to_video` 并实现
   - 更新 `ToolType` 枚举，添加新工具类型
   - 更新 `create_tool_task` 函数，处理新工具的参数
   - 更新 `execute_task` 函数，调用相应的视频生成 API

5. **更新历史记录输出**
   - 确保视频路径正确保存到历史记录
   - 确保视频 URL 可以正确访问

## 前端实现

6. **更新工具定义**
   - 在 `apps/web/js/tools.js` 中更新 `TOOLS` 数组：
     - 将 `ref_image_to_video` 改为 `vidu_ref_image_to_video`，名称改为"vidu参考生视频"
     - 添加 `sora_image_to_video`，名称为"sora生视频"
     - 将 `text_to_video` 改为 `wan_image_to_video`，名称改为"wan图生视频"
   - 调整工具顺序，确保 sora 在 vidu 下面

7. **更新工具表单字段**
   - 在 `apps/web/js/tools.js` 中更新 `TOOL_FIELDS`：
     - `vidu_ref_image_to_video`：images（多图，最多7张）、prompt、aspect_ratio、resolution、duration
     - `sora_image_to_video`：image（单图）、prompt、duration（4/8/12）
     - `wan_image_to_video`：image（单图）、prompt、model（2.5/2.6）、resolution、duration、enable_audio

8. **实现多图片管理（vidu 工具）**
   - 复用现有的 `initImageListUpload` 功能
   - 限制最多7张图片
   - 支持拖拽排序和删除

9. **实现单图片输入（sora 和 wan 工具）**
   - 使用现有的 `initImageUpload` 功能
   - 集成素材选择功能

10. **更新历史记录显示**
    - 在 `apps/web/js/tools.js` 的 `renderHistory` 函数中，检测视频输出并显示预览
    - 支持视频播放控件

11. **更新做同款功能**
    - 在 `apps/web/js/tools.js` 的 `reuseHistory` 函数中，确保视频生成工具的图片能正确填充

12. **更新任务详情显示**
    - 确保视频生成任务在"正在处理"时也能查看详情

## 测试

13. **测试 vidu 参考生视频工具**
    - 测试多图片上传（1-7张）
    - 测试图片排序
    - 测试不同分辨率和时长组合
    - 测试素材选择功能

14. **测试 sora 生视频工具**
    - 测试单图片上传
    - 测试不同时长选择
    - 测试素材选择功能

15. **测试 wan 图生视频工具**
    - 测试单图片上传
    - 测试模型版本切换（2.5/2.6）
    - 测试不同分辨率和时长组合
    - 测试音频生成选项
    - 测试素材选择功能

16. **测试历史记录功能**
    - 测试视频预览显示
    - 测试做同款时图片填充
    - 测试生成过程中查看详情

