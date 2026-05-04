# Scene 3: Batch Viral Search Plus Deep Teardown

## Use When

- the user wants “先搜，再拆”
- they care about why a topic is working, not only which videos are hot

## Minimum Inputs

- one keyword or topic

## Ideal Inputs

- candidate links
- market
- desired sample size
- target product or niche

## Workflow

1. collect candidate videos
2. rank them
3. choose top 3-5
4. run structured teardown on each
5. synthesize the shared pattern
6. output a creation guide

## Output Contract

- shortlist
- per-video teardown
- shared pattern summary
- creation rules

## Direct Prompt

```text
我要做“批量爆款搜索 + 深度拆解报告”。

主题：<主题>
地区：<地区>
候选视频：<链接或列表>

请按以下顺序输出：
1. 先排序，挑出最值得研究的 3-5 条
2. 每条视频做结构拆解
3. 总结它们共同的爆款逻辑
4. 提炼成一个我能拿去创作的执行指南
```

## Fallback

If no candidates exist yet, first run Scene 1, then continue here.
