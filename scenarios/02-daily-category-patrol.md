# Scene 2: Daily Category Patrol

## Use When

- the user wants a repeatable daily patrol workflow for one category or watchlist
- the real goal is to stop re-searching manually and only escalate new or abnormal signals

## Minimum Inputs

- one category
- one primary market

## Ideal Inputs

- 3-10 patrol keywords
- patrol cadence
- fixed patrol time
- append strategy
- whether to append into one long-lived sheet
- whether each row must carry patrol date
- alert conditions
- multi-category or multi-keyword watchlist

## Workflow

1. define the watchlist and cadence
2. fix one stable patrol table schema and row-level required fields
3. define append-to-same-sheet, capture-date, and historical retention rules
4. separate new, rising, weak, and abnormal signals instead of repeating old winners
5. write a daily summary template that highlights only net-new or changed signals
6. define which rows auto-escalate into Scene 03 and which stay as patrol history

## Output Contract

- patrol SOP
- stable patrol main-board schema
- append and capture-date rules
- alert logic
- daily summary template
- Scene 03 escalation path
- weak-signal archive path

## Direct Prompt

```text
按场景 02 执行：设计一个 TikTok 品类日常巡检体系。
这次要像产品一样固定下来，不要只给研究建议。

必须明确：
1. 巡检频率和时间
2. 是否追加到同一份表格
3. 每行是否记录采集日期
4. 多关键词 / 多品类 watchlist 怎么组织
5. 哪些信号算新增、上升、异常、弱信号
6. 高价值结果何时自动进入 Scene 03

输出要包括：
- 稳定表头
- 巡检 SOP
- 日报模板
- 哪些结果自动进入 Scene 03
- 哪些结果只沉淀到 patrol 历史库

日报不要重复抄昨天内容，要优先突出：
- 今天新增的强信号
- 今天明显上升的内容
- 今天出现的异常变化
- 仍需观察但不值得立刻深拆的弱信号
```

## Fallback

If the user has no automation source yet, convert the workflow into a manual but durable patrol SOP instead of pretending the collection is already automated.
