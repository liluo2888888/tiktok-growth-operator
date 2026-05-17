# Scene 7: Category Market Insight

## Use When

- the user wants to know whether a category, keyword cluster, or product theme is worth entering
- the result should be a decision surface, not a vague trend note

## Minimum Inputs

- one category or product theme

## Ideal Inputs

- top videos
- keyword set
- title and hashtag clues
- competitor products
- target market

## Workflow

1. extract category keywords from titles and hashtags
2. assess content heat separately from product-side proof
3. identify saturated versus still-open angles
4. write keyword-level decisions
5. end with do / do not do / priority do guidance

## Output Contract

- category judgment
- keyword decision table
- hot angle map
- saturation notes
- decision surface

## Direct Prompt

```text
按场景 07 执行：判断这个品类或主题值不值得做。
不要只给一个总判断，要先做关键词级拆分。

至少输出：
1. 从标题和标签提炼出来的热词
2. 每个关键词的内容热度
3. 每个关键词的商品侧表现或商业严肃度
4. 每个关键词该做 / 不该做 / 优先做
5. 理由

最后再汇总成：
- 哪些角度已经卷
- 哪些空位还值得切
- 最终怎么决策
```

## Fallback

If live data is missing, ask for category video samples, search screenshots, or product examples before making a hard recommendation.
