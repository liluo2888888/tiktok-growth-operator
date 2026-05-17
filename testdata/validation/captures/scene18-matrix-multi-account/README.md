Scene 18 多账号多周矩阵夹具

目的
- 给 Scene 18 提供真正的“竞品矩阵周报”验证面，而不是只验证单账号多周。
- 让 importer 能真实输出：
  - 按账号拆开的周摘要
  - 按账号拆开的周度变化
  - 矩阵级动作分发

这个夹具是什么
- `ranked_videos.json`
  - 3 个账号
  - 2 个自然周
  - 每个账号各 4 条帖子
- `summary.json` / `profile_summary.json`
  - 标明这是 3 个账号的矩阵型 fixture
- `comments_sampled.json`
  - 每个账号都有与其策略变化一致的评论语言

设计意图
- Week 16:
  - 解释偏多
  - 开头偏慢
  - 证明偏晚
- Week 17:
  - 识别更快
  - 证明更早
  - trust / wear-test / clarity 更明确

这个夹具不是为了模拟完整真实市场，而是为了稳定触发：
- Scene 18 的 `matrix_mode`
- 账号级周摘要表
- 账号级周变化表
- 矩阵级 `Next Action` 调度语义

怎么使用
- `python .\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py --scene 18 --capture-root .\\tiktok-growth-operator.skill\\testdata\\validation\\captures\\scene18-matrix-multi-account --project \"Scene18 Matrix Check\" --output .\\.codex-tmp\\scene18-matrix.json`

预期结果
- executive summary 应明确进入“多账号、多周矩阵视角”
- `Objects To Track` 应按账号逐行输出，而不是只给一个账号池
- `Why They Matter` 应按账号输出周度变化
- `Next Action` 应变成矩阵级调度，而不是单账号复盘口吻
