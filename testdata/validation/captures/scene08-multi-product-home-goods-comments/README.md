Scene 08 非美妆购买型评论夹具

目的
- 给 Scene 08 提供第二套不同类目的购买语言回归夹具。
- 降低当前评论挖掘只贴近美妆 / 色号 / before-after 语言的过拟合风险。

这个夹具是什么
- `comments_sampled.json`
  - 3 个非美妆商品来源：
    - `under-sink-organizer`
    - `pet-hair-remover-roller`
    - `compression-packing-cubes`
  - 重点覆盖的购买语言：
    - 物流速度
    - 包装完整度
    - 真假 / dropship 怀疑
    - 退货与退款体验
    - 尺寸 / 适配 / 空间兼容
    - 耐用度 / zipper / handle / load test
    - before-after 是否真实

为什么需要这个夹具
- 现有 Scene 08 强夹具已经能覆盖美妆类购买语言。
- 但如果只盯着色号、肤色、wear-test、before-after，Scene 08 的泛化能力不够稳。
- 这套非美妆夹具主要验证：
  - Scene 08 能不能把“尺寸 / 适配 / 耐用度 / 退货”语言也组织成品类洞察
  - 来源商品标签是否仍能保留
  - reply-chain 里的真实性 / 耐用度 / compatibility objection 能否被正确识别

怎么使用
- `python .\\tiktok-growth-operator.skill\\scripts\\import_tiktok_capture_pack.py --scene 08 --capture-root .\\tiktok-growth-operator.skill\\testdata\\validation\\captures\\scene08-multi-product-home-goods-comments --project \"Scene08 Home Goods Comment Check\" --output .\\.codex-tmp\\scene08-home-goods-comment-check.json`
