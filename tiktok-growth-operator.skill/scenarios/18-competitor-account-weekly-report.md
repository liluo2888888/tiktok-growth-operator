# Scene 18: Competitor Account Weekly Report

## Use When

- the user wants a weekly view of what competitor accounts changed
- the real goal is to react to strategy shifts, not just list posts

## Minimum Inputs

- 2 or more competitor accounts

## Ideal Inputs

- 3-5 competitor accounts
- account links
- latest posts
- prior-week notes
- 2 or more weekly snapshots when available
- target market

## Workflow

1. group posts by account and week
2. summarize weekly output per account
3. compare accounts horizontally
4. identify breakout causes and strategy changes
5. separate baseline observations from real multi-week trend claims
6. end with operator actions for this week

## Output Contract

- per-account weekly summary
- cross-account comparison
- notable shifts
- breakout-cause view
- strategy-shift view
- weekly operator response

## Direct Prompt

```text
按场景 18 执行：做一份竞品账号周报。
不要把它写成几个单账号小结，而要把 3-5 个账号当成一个矩阵。

必须回答：
1. 上周每个账号发了什么
2. 哪些内容跑出来了
3. 为什么跑出来
4. 每个账号策略上变了什么
5. 账号之间最大的差异是什么
6. 我本周该跟进什么动作

如果只有 1 周数据，不要装作有趋势判断，要明确标成 baseline week。
```

## Fallback

If only one week of data exists, mark it as a baseline week instead of pretending long-term trend certainty.
