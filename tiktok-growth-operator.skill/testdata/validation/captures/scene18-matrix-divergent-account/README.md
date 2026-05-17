Scene 18 分化型矩阵夹具

目的
- 验证 Scene 18 不只是能看“多个账号一起变强”。
- 还要能看出：
  - 哪个账号本周明显增强
  - 哪个账号本周明显回落
  - 哪个账号只是轻波动 / 事件噪音

这个夹具是什么
- `proofboostlab`
  - Week 17 明显增强
  - proof-first 和 fast recognition 明显拉升
- `slowstoryroom`
  - Week 17 明显回落
  - 叙事拖长、结果变慢、证明不足
- `eventspikelab`
  - Week 17 只有轻波动
  - 仍然更像事件壳 / 情绪壳，不像稳定可迁移增长线

这个夹具主要验证
- Scene 18 的矩阵模式能否不把所有账号写成同一种趋势
- `Objects To Track` 是否会保留每个账号自己的周变化标签
- `Why They Matter` 是否能区分：
  - 明显增强
  - 明显回落
  - 轻波动 / 相对持平
- `Next Action` 是否会把“减少跟进”真正指向回落账号，而不是误伤轻波动账号

怎么使用
- `python .\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py --scene 18 --capture-root .\\tiktok-growth-operator.skill\\testdata\\validation\\captures\\scene18-matrix-divergent-account --project \"Scene18 Divergent Matrix Check\" --output .\\.codex-tmp\\scene18-divergent-matrix.json`
