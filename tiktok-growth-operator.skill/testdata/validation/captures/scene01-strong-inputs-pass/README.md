# Scene 01 强约束正向夹具

这个夹具用于验证 Scene 01 在“强约束输入已补齐”时，会进入“允许交接 Scene 03”的正向状态。

## 目的

- 覆盖与缺字段 smoke 包相反的状态
- 验证以下字段同时存在时，Scene 01 不再报“暂不建议交接”
  - `publish_window`
  - `market`
  - `sort_by`
  - `shop_only`
  - `shortlist_count`

## 来源

- 基于 `captures/tiktok-analysis-pack-smoke-20260423f/` 最小复制
- 只补强运行时强约束输入，不伪造新的视频内容

## 预期

- Scene 01 报告中应出现：
  - `可以直接交接 Scene 03`
- 不应再出现：
  - `暂不建议直接全量交接 Scene 03`
