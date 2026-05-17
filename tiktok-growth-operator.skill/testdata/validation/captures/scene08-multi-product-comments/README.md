Scene 08 多商品购买型评论夹具

目的
- 给 Scene 08 提供更强的“购买语言”回归夹具。
- 让品类级评论综合更接近真实购物决策，而不是偏公告或平台反应。

这个夹具是什么
- `comments_sampled.json`
  - 一个 durable validation fixture，把 3 个来源商品合并成一份 capture 风格文件。
  - 语言刻意偏购买决策，重点覆盖：
    - 物流速度
    - 价格 / 性价比判断
    - 复购意愿
    - 退款 / 破损 / 质量担忧
    - before-after 证明
    - 色号 / 尺码 / 使用场景问题
    - 围绕物流、真假、退款、证明展开的 reply-chain 跟进语言

来源说明
- 这是一个用于导出和综合回归的“电商语言重放夹具”。
- 它不宣称自己是某一次单独实时 TikTok 运行的新鲜原始 dump。
- 主要用来验证：
  - 来源商品标注是否保留
  - 重复购买触发语是否能正确聚类
  - 抱怨 / 信任 / 控制感是否能被分开
  - 价格带差异是否能正确输出
  - Scene 08 的 DOCX/XLSX 是否适合做品类级评论报告

为什么需要这个夹具
- 早期的 Scene 08 多商品夹具偏公告 / 平台反应。
- 那不足以判断 Scene 08 是否真的像“产品评论挖掘工作流”。
- 这份夹具更贴近目标任务：
  - 找出用户为什么买
  - 找出用户为什么犹豫
  - 找出哪些重复语言应该变成营销话术或产品指引
  - 区分顶层购买语言和 reply-chain 里的异议处理 / 同行安抚

怎么使用
- 可以直接这样导入：
  - `python .\tiktok-growth-operator.skill\scripts\import_tiktok_capture_pack.py --scene 08 --capture-root .\tiktok-growth-operator.skill\testdata\validation\captures\scene08-multi-product-comments --project "Scene08 Commerce Comment Check" --output .\.codex-tmp\scene08-commerce-comment-check.json`
