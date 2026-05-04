# Scene 6: Competitor Product Dashboard

## Use When

- the user wants a repeatable way to watch competitor products

## Minimum Inputs

- 3-10 competitor product links, IDs, screenshots, or names

## Ideal Inputs

- current price
- sales indicators
- rating signals
- update cadence

## Workflow

1. define the product list
2. define fields to track
3. normalize competitor records
4. identify what changes matter commercially
5. output a dashboard schema and interpretation rules

## Output Contract

- competitor board schema
- daily/weekly review checklist
- anomaly interpretation guide

## Direct Prompt

```text
帮我把这些竞品做成一个“持续追踪看板”。

请输出：
1. 必追踪字段
2. 哪些变化最值得警惕
3. 如何判断降价、销量变化、评分变化的含义
4. 一份可重复填写的追踪模板
```

## Fallback

If no structured data exists, build the schema first and tell the user exactly what to capture next time.
