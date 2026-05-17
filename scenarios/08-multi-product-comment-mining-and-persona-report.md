# Scene 8: Multi-Product Comment Mining and Persona Report

## Use When

- the user wants category-level user insight from multiple products
- the goal is to drive positioning, messaging, and content, not just summarize comments

## Minimum Inputs

- comments from at least 2 products

## Ideal Inputs

- 3-5 products
- 20-40 comments each
- market
- product positioning goal
- price-band notes
- purchase-oriented comments with shipping, packaging, authenticity, fit, return, or before-after language when possible

## Workflow

1. keep comments grouped by source product
2. extract repeated purchase factors, praise keywords, and complaint pain points
3. compare differences by price band or product layer
4. separate category base value from improvement opportunity
5. preserve repeated user language and source-product labels into the insight layer
6. output persona, positioning, and messaging implications

## Output Contract

- source-product summary
- purchase factor synthesis
- praise keyword synthesis
- complaint pain-point synthesis
- price-band differences
- category base value vs improvement opportunity
- repeated user-language evidence
- persona and messaging implications

## Direct Prompt

```text
按场景 08 执行：把多个商品的评论做成品类级人群洞察。
这次不要只做情绪总结，要按 4 块来输出：
1. 购买因素
2. 好评关键词
3. 差评痛点
4. 价位差异

要求：
- 评论先按来源商品分开
- 合并分析时不能丢掉来源商品标签
- 分清哪些是品类基础价值，哪些是改进机会
- 尽量突出物流、包装、真假、退货、before-after、尺码 / 色号适配这类购买型语言
- 最后回到选品定位、营销卖点、脚本话术建议
```

## Fallback

If comment volume is low, state clearly that the result is provisional and list what more evidence should be collected.
