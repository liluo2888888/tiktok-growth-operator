Scene 18 / 19 多周账号夹具

目的
- 给 Scene 18 竞品账号周报提供可重复的“最近两周对比”夹具。
- 给 Scene 19 自家账号复盘提供可重复的“高低表现 + 多周模式”夹具。

这个夹具是什么
- `ranked_videos.json`
  - 1 个账号、2 个自然周、6 条帖子。
  - Week 16 偏“解释先行、开头偏慢”。
  - Week 17 偏“识别先行、证明更早、信任更明确”。
- `summary.json` / `profile_summary.json`
  - 提供账号 URL、帖子数、评论采样数、下载数等周对比所需基线字段。
- `comments_sampled.json`
  - 提供与两周内容模式对应的评论语言。
  - 重点覆盖：
    - 开头是否够快
    - before-after 是否更早出现
    - daylight / wear-test / trust proof 是否被直接回答
    - 评论压力是“犹豫”还是“信任增强”

为什么需要这个夹具
- 之前 Scene 18 / 19 虽然已经支持多周逻辑，但 durable validation 侧缺一份稳定的两周样本。
- 这会导致周对比能力更多依赖临时运行或历史 `tmp/` 证据。
- 这份夹具的目标不是模拟全平台，而是稳定触发：
  - `compare_latest_two_weeks(...)`
  - `weekly_evidence_grade(...)`
  - Scene 18 的周报 compare 模式
  - Scene 19 的高低表现 + 多做/少做/停止 + 下轮测试计划

怎么使用
- Scene 18:
  - `python .\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py --scene 18 --capture-root .\\tiktok-growth-operator.skill\\testdata\\validation\\captures\\scene18-19-multi-week-account --project \"Scene18 Multi Week Check\" --output .\\.codex-tmp\\scene18-multiweek.json`
- Scene 19:
  - `python .\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py --scene 19 --capture-root .\\tiktok-growth-operator.skill\\testdata\\validation\\captures\\scene18-19-multi-week-account --project \"Scene19 Multi Week Check\" --output .\\.codex-tmp\\scene19-multiweek.json`

预期结果
- Scene 18 应进入“最近两周可比”的周报结论，而不是仅基线周。
- Scene 19 应进入“已有至少两周切片”的复盘结论，并给出高低表现组和下轮测试导向。
