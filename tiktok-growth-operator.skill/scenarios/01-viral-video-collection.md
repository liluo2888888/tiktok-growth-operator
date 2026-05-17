# Scene 1: Viral Video Collection

## Use When

- the user wants to collect viral TikTok videos around one keyword or category
- the goal is not just discovery, but deciding which videos deserve deeper teardown next

## Minimum Inputs

- one keyword or product phrase

## Ideal Inputs

- keyword set
- target market
- publish-time window
- sort rule
- whether to keep only TikTok Shop cart videos
- target audience

## Workflow

1. lock keyword, market, freshness window, sort rule, and commerce scope
2. collect candidate videos from exports, links, screenshots, or browser search
3. rank by reuse value, not only popularity
4. label each shortlisted video by reuse purpose and commerce signal
5. hand the best shortlist directly into Scene 03

## Output Contract

- structured collection board
- ranked shortlist
- why-worth-studying notes
- commerce signal layer
- Scene 03 handoff shortlist

## Direct Prompt

```text
按场景 01 执行：围绕一个关键词或品类采集 TikTok 爆款视频。
这次不要只给我一个列表，要先锁清楚：
1. 发布时间窗口
2. 地区
3. sort_by
4. 是否只看带 TikTok Shop 购物车视频

然后输出一张结构化候选表，至少包含：
- 排名
- 视频链接
- 核心主题
- 表现信号
- 带货 / 购物车信号
- commerce confidence
- 适合复用在哪一层：hook / proof / structure / style
- 为什么值得研究
- 适合什么品类复用

最后再给我一份可以直接进入 Scene 03 的 shortlist，不要搜完就结束。
```

## Fallback

If live results are unavailable, ask for TikTok search screenshots, copied titles plus links, or an exported candidate list, then still keep the same ranking and handoff structure.
