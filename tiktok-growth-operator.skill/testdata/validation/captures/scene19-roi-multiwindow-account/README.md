Scene 19 ROI / 多窗口夹具

目的
- 给 Scene 19 提供一套更接近“自家账号复盘”的 durable fixture。
- 不只比较高低表现，还补上：
  - 两个发布时间窗口
  - conversion proxy
  - ROI proxy

这个夹具是什么
- 单账号、两段时间窗口、6 条帖子
- 高表现内容偏：
  - founder-proof
  - proof-object demo
- 低表现内容偏：
  - aesthetic montage
  - slow explainer

额外补充的字段
- `commerce_confidence`
- `content_type`
- `conversion_proxy`
- `roi_proxy`
- `publish_window`

主要验证
- Scene 19 能否在已有多周逻辑上更自然地挂上增长 / ROI 相关性
- 高低表现组是否更像真实的内容模式差异，而不是只看表层点赞
- 下轮测试计划是否更接近“继续放大什么、减少什么、停止什么”

怎么使用
- `python .\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py --scene 19 --capture-root .\\tiktok-growth-operator.skill\\testdata\\validation\\captures\\scene19-roi-multiwindow-account --project \"Scene19 ROI Multiwindow Check\" --output .\\.codex-tmp\\scene19-roi-multiwindow.json`
