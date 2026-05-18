# Evidence Ref 校验 - 场景 18 - 竞品账号周报

- 场景：18 - 竞品账号周报
- 项目：Evidence Ref 校验
- 交付物类型：采集看板
- 生成时间：2026-05-17T22:40:59
- 状态：已导入
- 场景文件：`scenarios/18-competitor-account-weekly-report.md`

## 任务上下文

真实 TikTok 采集包导入自 validation/captures/scene18-19-multi-week-account，当前用于未分类赛道。当前看板规模：6 条已排序 / 3 条达标.
来源账号：https://www.tiktok.com/@mustsharebeauty; 会话质量：fixture_multi_week_account; 查询词：未提供; 主题：未提供.
头部候选：https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 | Shade match story with decent trust but slow first frame. Comments ask for daylight proof and wear test. | 6100 点赞，236000 播放，81 分享，188 评论.
采集根目录：validation/captures/scene18-19-multi-week-account

### 输入材料

- 账号： https://www.tiktok.com/@mustsharebeauty
- 排序视频数：6
- 达标视频数：3
- 采集根目录：validation/captures/scene18-19-multi-week-account

### 最低证据要求

- 2 个以上竞品账号
- 1 周帖子批次
- summary.json 或 汇总文件（aggregate_summary.json）
- 账号汇总文件（profile_summary.json） 或 summary.json
- ranked_videos.json 或 排序视频文件（aggregate_ranked_videos.json）

### 理想证据补充

- 上周备注
- 逐帖表现上下文
- 目标市场
- 1 个矩阵里包含 3-5 个账号
- 2 周以上周度快照
- 达标视频文件（aggregate_qualified_videos.json） 或 qualified_video_links.txt
- 聚合报告（aggregate_report.md）
- 视频明细（video_details.json）

### 约束条件

- 如果目前只有 1 周数据，应标记为基线周，而不是趋势判断。
- 结论必须只绑定到排序指标、标题/钩子文本和采集包摘要，不要外推。

### 目标交付

- 分账号周度总结
- 跨账号横向对比
- 关键变化
- 策略变化视角
- 对用户的影响
- TikTok 原生排序模式结论
- 基于 采集包 的可复用改编规则

### 开跑前检查

- 帖子已按账号与周维度分组
- 可以明确写出相对上周的变化
- 可以给每周响应动作排优先级
- 可以进行跨账号横向对比
- baseline week 与多周趋势可以区分
- 已明确标出高排名视频。
- 已将可迁移模式与账号自身品牌势能区分。

## 执行摘要

- 核心结论：这份竞品账号周报现在已经能对比最近两周，所以不再只是看单周榜单，而是能判断策略是否真的发生了变化。
- 为什么重要：有了两周切片后，可以把稳定连胜的包装方式和短期噪音分开，也更容易识别竞对本周到底改了什么。
- 下一步动作：直接按下方周环比变化去做本周动作分发：哪些线继续追，哪些线可以借鉴，哪些异常峰值先忽略。
- 置信度：中

## 操作检查清单

- 开始比较前，先按账号和周维度整理帖子。
- 重点标出周度变化，而不是只列周度总量。
- 横向比较账号，而不是拆成互不相干的小报告。
- 最后必须落到本周用户该采取的动作。
- 如果只有单周数据，就标成 baseline week，不要假装长期趋势。

## 常见失败模式

- 只列活动量，没有解释模式变化。
- 只有 1 个基线周却直接下趋势判断。
- 报告太像库存清单，导致漏掉策略变化检测。
- 没有真正做跨账号横向比较。

## 直接执行模板

- 推荐请求：`按场景 18 执行：输出竞品账号周报。把 3-5 个账号视为同一个矩阵，按账号与周维度比较发帖、爆点内容、爆款归因与策略变化；如果只有 1 周数据，要明确标成 baseline week，最后写清本周该跟进什么动作。`
- 推荐请求（中文）：`按场景 18 执行：输出竞品账号周报，要按账号和周维度比较内容变化，不只看总量，并明确本周该跟进的动作。`
- 运行参数：
  - `python scripts/run_operator_workflow.py --mode scene --scene 18 --project "<project-name>" --output-root ".\tmp\competitor-account-weekly-report"`
  - `python scripts/generate_scene_report.py --scene 18 --project "<project-name>" --output ".\tmp\competitor-account-weekly-report.json" --format json`

### 可变输入

| 变量 | 含义 | 示例 | 是否必填 |
| --- | --- | --- | --- |
| project_name | 便于识别的运行名或项目名 | 竞品账号周报 | 是 |
| market | 当场景依赖单一市场时的目标市场或地区 | 美国 | 建议 |
| evidence_pack | 作为源证据使用的链接、截图、转写、导出文件、OCR 文本或摘录备注 | 2-5 个竞品账号的周度帖子批次、上周备注与多周快照 | 是 |
| success_goal | 操作者希望该场景产出的结果 | 竞品周报、爆款归因、策略变化判断与动作看板 | 建议 |

### Codex 提示词骨架

- 以场景 18 作为本次工作的主流程。
- 分析前先把现有证据归整为以下输入：2 个以上竞品账号, 最近帖子或周度帖子清单, 如有则附上上周备注, 目标市场, 周度监控窗口。
- 如果证据不足，先明确缺口再继续。最低开工证据：2 个以上竞品账号, 1 周帖子批次。
- 最终必须产出以下可直接给运营使用的结果：分账号周度总结, 跨账号横向对比, 关键变化, 策略变化视角, 对用户的影响。
- 重点突出跨账号的周度模式变化，而不是只列活动量。
- 把观察到的变化翻译成本周可执行动作。
- 解释为什么会爆，而不是只点名哪条爆了。
- 只有单周数据时，不要假装有长期趋势判断。
- 优先填入可复用结论、表格、排序逻辑和下一步动作，不要停留在泛泛点评。

### 中文提示词骨架

- 按场景 18 执行：输出竞品账号周报，要按账号和周维度比较内容变化，不只看总量，并明确本周该跟进的动作。
- 先把我提供的材料整理成这组输入：2 个以上竞品账号, 最近帖子或周度帖子清单, 如有则附上上周备注, 目标市场, 周度监控窗口。
- 如果证据不足，先明确缺口再继续。最低开工证据：2 个以上竞品账号, 1 周帖子批次。
- 最终必须产出：分账号周度总结, 跨账号横向对比, 关键变化, 策略变化视角, 对用户的影响。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

### 执行步骤

1. 开始比较前，先按账号和周维度整理帖子。
2. 重点标出周度变化，而不是只列周度总量。
3. 横向比较账号，而不是拆成互不相干的小报告。
4. 最后必须落到本周用户该采取的动作。
5. 如果只有单周数据，就标成 baseline week，不要假装长期趋势。

### 交付检查清单

- 帖子已经按账号与周维度整理。
- 报告解释了变化，而不是只罗列原始活动量。
- 跨账号策略差异已经说清楚。
- 已经区分 baseline week 与多周趋势判断。
- 本周响应动作已经排优先级。

## 证据总表

| 标签 | 详情 | 来源 |
| --- | --- | --- |
| 汇总 | 已排序=6; 达标=3; 最低点赞= | summary.json |
| 账号汇总 | 账号=https://www.tiktok.com/@mustsharebeauty; 会话=fixture_multi_week_account; 已排序=6 | 账号汇总文件（账号汇总文件（profile_summary.json）） |
| 排序视频 7616000000000000002 | Shade match story with decent trust but slow first frame. Comments ask for daylight proof and wear test. | https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 |
| 排序视频 7617000000000000001 | Before-after reveal in the first two seconds. Fast recognition, direct proof, and immediate save-worthy shade context. | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001 |
| 排序视频 7617000000000000002 | 钩子 opens on the problem face, then switches straight into proof. Less talking, clearer payoff, stronger 评论. | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000002 |
| Content graph clusters | creator=1; sound=0; hashtag=0; videos=6 | content_graph.json |

## 执行结论

_总结本周被监控竞品账号到底发生了哪些变化。_

这份竞品账号周报现在已经能对比最近两周，所以不再只是看单周榜单，而是能判断策略是否真的发生了变化。

账号基线：https://www.tiktok.com/@mustsharebeauty

证据等级：可直接周对比（1 个账号 / 2 个自然周 / 6 条帖子 / 12 条评论样本 / 2 条下载成功）

比较窗口：2026-W17 vs 2026-W16

- 本周最强包装线：证明 / authority teardown
- 爆点帖子关键信号：Shade match story with decent trust but slow first frame.
- 评论侧信任 / 质疑线索：一般反应 | 回复压力=17 | The first two seconds sold me. I knew exactly why I should keep watching.
- 如果还没有上周对照，就把本次视为基线周报；若账号数不足，也不要包装成完整矩阵级结论。
- 头部样本入选溯源：creator cluster (@mustsharebeauty, 6 posts) → reuse-value rank #2
- 评论回复链信号：一般反应 | 回复压力=17 | The first two seconds sold me. I knew exactly why I should keep watching.
- 周度基线异动：2026-W17 vs 2026-W16: 互动均值抬升

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| account_week | week-2026-W17 | https://www.tiktok.com/@mustsharebeauty | weekly-window | Compared against prior week 2026-W16 | Executive conclusion: latest-week strategy shift |
| video | 7616000000000000002 | https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 | 00:00-00:05 | Shade match story with decent trust but slow first frame. Comments ask for daylight proof and wear test. | Executive conclusion: strongest packaging line this week |

## 监控对象

_按账号记录每周产出表现。_

- 自然周覆盖：2 周；帖子数：6；账号数：1。
- 先看哪一周在重复赢、哪一周只是新冒头，再决定是否判定为策略变化；矩阵模式下还要看这种变化有没有跨账号扩散。

### 分账号周度总结

| 账号 | 发帖量 | 本周胜出帖子 | 主主题 | 爆点信号 | 相对上周变化 | 策略变化 |
| --- | --- | --- | --- | --- | --- | --- |
| https://www.tiktok.com/@mustsharebeauty | 2026-W17 | 3 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001 | Before-after reveal in the first two seconds. | 钩子 / 包装研究 | 18200 点赞，912000 播放，315 分享，420 评论 |
| https://www.tiktok.com/@mustsharebeauty | 2026-W16 | 3 | https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 | Shade match story with decent trust but slow first frame. | 证明 / authority teardown | 6100 点赞，236000 播放，81 分享，188 评论 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| account_week | 7616000000000000002 | https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 | weekly-window | Shade match story with decent trust but slow first frame. Comments ask for daylight proof and wear test. | Tracked account/week object row |
| account_week | 7617000000000000001 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001 | weekly-window | Before-after reveal in the first two seconds. Fast recognition, direct proof, and immediate save-worthy shade context. | Tracked account/week object row |
| account_week | 7617000000000000002 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000002 | weekly-window | 钩子 opens on the problem face, then switches straight into proof. Less talking, clearer payoff, stronger 评论. | Tracked account/week object row |

## 为什么值得关注

_解释这些变化为什么重要，而不是只罗列现象。_

这一块不只是周报报数，而是先解释本周相对上周的基线异动，再解释谁在发力、谁在回落、谁只是事件噪音。

- 优先解释策略变化，再解释单条爆点；不要把偶发爆点误写成全账号升级。
- 横向对比要回答两个问题：是谁变了；这种变化有没有跨账号扩散。

### Change-First Weekly Digest

| 信号 | 发生了什么 | 为什么重要 | 是否升级动作 |
| --- | --- | --- | --- |
| 周度基线 | 2026-W17 vs 2026-W16 | 发帖 3→3；均赞 4600.0→15300.0 | 是 |
| 互动均值抬升 | 平均点赞 4600.0 -> 15300.0 | 继续追本周头部包装线，并检查是否伴随评论侧信任/质疑变化。 | 是 |
| 2026-W17 vs 2026-W16 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001 | 本周：Before-after reveal in the first two seconds. | 上周：Shade match story with decent trust but slow first frame. |
| 2026-W17 vs 2026-W16 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000002 | 本周：钩子 opens on the problem face, then switches straight into proof. | 上周：GRWM but the result reveal comes too late. |
| 2026-W17 vs 2026-W16 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000003 | 本周：Creator shows result under indoor and daylight lighting with a quick... | 上周：Texture demo with calm narration. |
| 2026-W17 周趋势 | 钩子 / 包装研究 | 3 条样本；头部线索：Before-after reveal in the first two seconds. | 当前基线周 |
| 评论语言压力 | 一般反应 | 回复密集的评论簇能帮助区分：这是健康兴趣，还是争议 / 困惑驱动的放大。 | 回复链活跃（12 条回复），已经足够视为真实的购买前确认或异议处理信号。 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| account_week | account-a-week | 待补账号或表格链接 | 周观察窗口 | 展示账号 A 在该周主要内容或策略变化的周总结。 | 周度变化归因 |
| video | breakout-post-1 | 待补视频链接 | 00:00-00:05 | 用于解释账号为什么发生变化的代表性爆点帖子。 | 爆点归因 |
| video | 7616000000000000002 | https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 | 00:00-00:05 | Shade match story with decent trust but slow first frame. Comments ask for daylight proof and wear test. | Weekly shift / breakout interpretation |
| video | 7617000000000000001 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001 | 00:00-00:05 | Before-after reveal in the first two seconds. Fast recognition, direct proof, and immediate save-worthy shade context. | Weekly shift / breakout interpretation |
| comment | mw-c-007 | https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001 | comment-thread | mustsharebeauty-week17-before-after: 回复链活跃（12 条回复），已经足够视为真实的购买前确认或异议处理信号。 | Comment-language pressure behind this week's breakout interpretation |

## 下次补采字段

_列出为了更强周对比还缺哪些字段。_

- 继续补同账号第二周、第三周切片；如果是竞品矩阵，还要保证每个账号都按同字段持续复采。
- 每条帖子补评论采样可用性和出镜人 / 权威标签。
- 如果账号改了封面、首帧或标题包装，要保留证据，不要只留 caption。

### 下轮补采升级

| 待补字段 | 为什么重要 | 优先级 |
| --- | --- | --- |
| 第二周快照 | 没有第二周，就无法把长期有效包装和单周噪音分开。 | P1 |
| 多账号并排采样 | 没有 3-5 个账号并排，就很难判断这是不是矩阵级变化。 | P2 |
| 评论采样标记 | 帮助判断高表现是在积累信任，还是在放大质疑 / 困惑。 | P1 |
| 出镜人 / 权威标签 | 把包装胜利和名人、官方身份加成拆开。 | P1 |
| 封面 / 首帧证据 | 让下一轮比较不只看 caption，还能看点击包装有没有变。 | P2 |

## 下一步动作

_明确本周运营应该做什么响应动作。_

本周响应动作必须更像运营调度单：继续追谁、借鉴谁、忽略谁，都要回到策略变化而不是只回到热度高低。

### 本周运营响应

| 动作领域 | 建议 | 紧急度 | 策略变化点 |
| --- | --- | --- | --- |
| 本周继续追 | 2026-W17 的头部包装线 | 钩子 / 包装研究 \| Before-after reveal in the first two seconds. | 延续识别优先的包装，只做轻量形式变化。 |
| 本周值得借鉴 | 2026-W17 对比 2026-W16 | 本周 钩子 / 包装研究；上周 证明 / authority teardown | 只复制可迁移的开头信号、证明方式和镜头节奏，不复制账号权威壳。 |
| 本周应忽略 | 疑似一次性分发放大 | 一般反应 | 若优势只来自账号体量、官方身份或单次事件流量，不要直接当成可复制公式；先等下一周复采确认。 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7616000000000000002 | https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002 | 00:00-00:03 | Shade match story with decent trust but slow first frame. Comments ask for daylight proof and wear test. | Dispatch action: continue / borrow / ignore decision for this week |

## 资产清单

- [library] 来源账号：file `https://www.tiktok.com/@mustsharebeauty` | Account baseline
- [library] 排序视频 1 reference_video: file `https://www.tiktok.com/@mustsharebeauty/video/7616000000000000002` | ranked reference
- [library] 排序视频 2 reference_video: file `https://www.tiktok.com/@mustsharebeauty/video/7617000000000000001` | ranked reference
- [library] 排序视频 3 reference_video: file `https://www.tiktok.com/@mustsharebeauty/video/7617000000000000002` | ranked reference
- [library] 排序视频 4 reference_video: file `https://www.tiktok.com/@mustsharebeauty/video/7616000000000000001` | ranked reference
- [library] 排序视频 5 reference_video: file `https://www.tiktok.com/@mustsharebeauty/video/7617000000000000003` | ranked reference
- [library] 排序视频 6 reference_video: file `https://www.tiktok.com/@mustsharebeauty/video/7616000000000000003` | ranked reference
- [library] content_graph.json: file `captures/scene18-19-multi-week-account/content_graph.json` | Reusable 采集包 artifact

## 来源

- summary.json
- ranked_videos.json
- https://www.tiktok.com/@mustsharebeauty
