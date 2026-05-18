# Evidence Ref 校验 - 场景 03 - 批量爆款深拆

- 场景：03 - 批量爆款深拆
- 项目：Evidence Ref 校验
- 交付物类型：拆解报告
- 生成时间：2026-05-17T20:43:57
- 状态：已导入
- 场景文件：`scenarios/03-batch-viral-search-plus-deep-teardown.md`

## 任务上下文

真实 TikTok 采集包导入自 validation/captures/scene01-strong-inputs-pass，当前用于未分类赛道，市场 美国。当前看板规模：3 条已排序 / 3 条达标，最低点赞阈值 1000.
来源账号：https://www.tiktok.com/@validation.orangecat; 会话质量：TikMatrix 主页帖子导出; 查询词：未提供; 主题：未提供.
头部候选：https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | always sing your heart out | 2610 点赞，28400 播放，62 分享.
达标对照：https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | cartoon orange cat sing-along packaging | 2610 点赞，28400 播放，62 分享.
采集根目录：validation/captures/scene01-strong-inputs-pass

### 输入材料

- 账号： https://www.tiktok.com/@validation.orangecat
- 排序视频数：3
- 达标视频数：3
- 采集根目录：validation/captures/scene01-strong-inputs-pass
- 地区：美国

### 最低证据要求

- 1 个关键词 or topic
- A candidate pool to rank
- summary.json 或 汇总文件（aggregate_summary.json）
- 账号汇总文件（profile_summary.json） 或 summary.json
- ranked_videos.json 或 排序视频文件（aggregate_ranked_videos.json）

### 理想证据补充

- 10+ candidate videos
- Links plus screenshots or transcript notes
- Target product or niche
- Explicit top-sample rule
- 达标视频文件（aggregate_qualified_videos.json） 或 qualified_video_links.txt
- 聚合报告（aggregate_report.md）
- 视频明细（video_details.json）

### 约束条件

- Shortlist before tearing down.
- Conclusions must be grounded in evidence from the chosen top videos.
- 当前为真实 TikTok 匿名会话采集包；本包暂不含评论采样。
- 结论必须只绑定到排序指标、标题/钩子文本和采集包摘要，不要外推。

### 目标交付

- Shortlist
- Per-video teardown
- Shared pattern summary
- Creation rules
- TikTok 原生排序模式结论
- 基于 采集包 的可复用改编规则

### 开跑前检查

- Shortlist criteria are clear
- Top 3-5 videos have enough evidence for teardown
- 市场 is not mixed
- Per-video and common-pattern deliverables are both expected
- 已明确标出高排名视频。
- 已将可迁移模式与账号自身品牌势能区分。

## 执行摘要

- 核心结论：The strongest TikTok posts in this pack win by pairing a clear first-line 钩子 with recognizable authority, cultural framing, or a featured-person premise that viewers understand immediately.
- 为什么重要：This pack is useful for studying which short caption, topic cue, and authority signal are actually portable into a new teardown and adaptation workflow.
- 下一步动作：Take the top-ranked shortlist into deeper teardown now, assign each winner to one teardown lane, and replace the original account authority with owned proof or owned talent.
- 置信度：中

## 操作检查清单

- Shortlist first, then deep-teardown only the top set.
- Use an explicit top-sample rule before teardown begins.
- Use the same lens across all chosen videos so patterns are comparable.
- End with creation rules, not only observations.

## 常见失败模式

- Deep-analyzing weak candidates that should have been filtered out earlier.
- Skipping script or time-axis extraction and therefore flattening the teardown.
- Using different teardown criteria across videos.
- Summarizing patterns without enough per-video evidence.

## 直接执行模板

- 推荐请求：`Run scene 03 to shortlist the strongest viral candidates for one topic, then deeply tear down only the top set using an explicit top-sample rule. End with three stable deliverables: per-video teardown, common-pattern summary, and creation guidance that can be used immediately for new scripts.`
- 推荐请求（中文）：`按场景 03 执行：先对同一主题的候选热视频做 shortlist，再只深拆前几条强样本，最后沉淀共用爆点规律和可直接改写成新脚本的创作规则。`
- 运行参数：
  - `python scripts/run_operator_workflow.py --mode scene --scene 03 --project "<project-name>" --output-root ".\tmp\batch-search-teardown"`
  - `python scripts/generate_scene_report.py --scene 03 --project "<project-name>" --output ".\tmp\batch-search-teardown.json" --format json`

### 可变输入

| 变量 | 含义 | 示例 | 是否必填 |
| --- | --- | --- | --- |
| project_name | 便于识别的运行名或项目名 | 晨间美妆钩子批量深拆 | 是 |
| market | 当场景依赖单一市场时的目标市场或地区 | 美国 | 建议 |
| evidence_pack | 作为源证据使用的链接、截图、转写、导出文件、OCR 文本或摘录备注 | 10 条候选 TikTok 链接，附截图与转写笔记 | 是 |
| success_goal | 操作者希望该场景产出的结果 | 短名单、逐条深拆与创作规则 | 建议 |

### Codex 提示词骨架

- 以场景 03 作为本次工作的主流程。
- 分析前先把现有证据归整为以下输入：Keyword or topic, 目标市场, Candidate links or search results, Desired sample size, Shortlist rule。
- 如果证据不足，先明确缺口再继续。最低开工证据：1 个关键词 or topic, A candidate pool to rank。
- 最终必须产出以下可直接给运营使用的结果：Shortlist, Per-video teardown, Shared pattern summary, Creation rules。
- Use the same teardown lens across all shortlisted videos so the pattern summary is comparable.
- Do not deep-analyze weak candidates that should have been filtered out earlier.
- Preserve full script, 钩子, proof rhythm, and time-axis conversion notes whenever evidence allows.
- 优先填入可复用结论、表格、排序逻辑和下一步动作，不要停留在泛泛点评。

### 中文提示词骨架

- 按场景 03 执行：先对同一主题的候选热视频做 shortlist，再只深拆前几条强样本，最后沉淀共用爆点规律和可直接改写成新脚本的创作规则。
- 先把我提供的材料整理成这组输入：Keyword or topic, 目标市场, Candidate links or search results, Desired sample size, Shortlist rule。
- 如果证据不足，先明确缺口再继续。最低开工证据：1 个关键词 or topic, A candidate pool to rank。
- 最终必须产出：Shortlist, Per-video teardown, Shared pattern summary, Creation rules。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

### 执行步骤

1. Shortlist first, then deep-teardown only the top set.
2. Use an explicit top-sample rule before teardown begins.
3. Use the same lens across all chosen videos so patterns are comparable.
4. End with creation rules, not only observations.

### 交付检查清单

- The top set is explicitly shortlisted before deep teardown.
- Each chosen video is analyzed with the same fields.
- The output includes both per-video detail and common-pattern synthesis.
- The report ends with reusable creation rules, not only observations.

## 证据总表

| 标签 | 详情 | 来源 |
| --- | --- | --- |
| 汇总 | 已排序=3; 达标=3; 最低点赞=1000 | 汇总文件（汇总文件（aggregate_summary.json）） |
| 账号汇总 | 账号=https://www.tiktok.com/@validation.orangecat; 会话=TikMatrix 主页帖子导出; 已排序=3 | 账号汇总文件（账号汇总文件（profile_summary.json）） |
| 排序视频 7636206423080226070 | always sing your heart out | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 排序视频 7636373657828347158 | SuperCat Papa | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 |
| 排序视频 7636137611576282399 | sad cat | https://www.tiktok.com/@aicatstories44/video/7636137611576282399 |
| Content graph clusters | creator=0; sound=0; hashtag=0; videos=3 | content_graph.json |

## 执行结论

_State the core winning pattern shared by the top videos._

这批 TikTok 爆款深拆现在已经更接近 Clipcat 文档里的平台闭环：先搜候选，再按带货与点赞规则缩成短名单，最后直接进入逐条深拆。

候选池规模：3 | 达标视频数：3

短名单规则：先搜 10 条，当前无强带货候选，按综合分与点赞共同排序取 Top 3 深拆

头部样本主题：cartoon orange cat sing-along packaging

头部样本钩子：always sing your heart out

- 头部样本权威信号：orangecat0088（未认证）
- 头部样本应该拆它的钩子、证明链和权威替代逻辑，而不是照搬字面外壳。

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:03 | always sing your heart out | Executive conclusion: top shortlist 钩子 and authority packaging |

## 结构逻辑

_Show how the top candidates were ranked and selected._

### 短名单

| Rank | Video | 钩子 | 证明 | Conversion Signal | 入选溯源 | Commerce Signal | Why It Made Top Set |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P1 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | always sing your heart out | 钩子 / caption / 包装研究 | 点赞=2610 / 评论=0 / 分享=62 \| 商业置信度=55 \| 购物车信号=未检测到 | reuse-value rank #1 | Selected for caption/钩子 completeness, 可迁移格式, commerce intent; 支撑信号： 点赞=2610, 分享=62. | 立即深拆 |
| P2 | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | SuperCat Papa | 钩子 / caption / 包装研究 | 点赞=1194 / 评论=18 / 分享=40 \| 商业置信度=0 \| 购物车信号=未检测到 | reuse-value rank #2 | Selected for caption/钩子 completeness, 可迁移格式, topic spread; 支撑信号： 点赞=1194, 评论=18, 分享=40. | 立即深拆 |
| P3 | https://www.tiktok.com/@aicatstories44/video/7636137611576282399 | sad cat | 钩子 / caption / 包装研究 | 点赞=606 / 评论=12 / 分享=29 \| 商业置信度=0 \| 购物车信号=未检测到 | reuse-value rank #3 | Selected for caption/钩子 completeness, comment density, topic spread; 支撑信号： 点赞=606, 评论=12, 分享=29. | 立即深拆 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:05 | always sing your heart out | Shortlist row P1: 钩子, proof style, and traction metrics |
| video | 7636373657828347158 | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | 00:00-00:05 | SuperCat Papa | Shortlist row P2: 钩子, proof style, and traction metrics |
| video | 7636137611576282399 | https://www.tiktok.com/@aicatstories44/video/7636137611576282399 | 00:00-00:05 | sad cat | Shortlist row P3: 钩子, proof style, and traction metrics |

## 核心机制

_Break down each selected video using the same lens._

逐条深拆必须同时保留 4 块：脚本全文 / 关键句、时间轴节奏、证明装置、最终可执行创作建议。

如果 caption 或脚本证据仍偏薄，这一行就该被标记为弱样本，而不是直接升格成共性规律。

- 时间轴默认按 4 段展开：开头钩子 / 主题铺垫 / 证明段 / 软收口。
- 脚本文本不够时，也要尽量保留当前能恢复出的完整 caption 或主题线索，别只剩一句抽象总结。
- 后续创作建议必须对应到时间轴，而不是只给泛化结论。

### 逐条视频拆解表

| Video | Opening 钩子 | Full Script / Key Lines | Time-Axis Rhythm | 证明 Device | CTA / 收口 | Main Reuse Value |
| --- | --- | --- | --- | --- | --- | --- |
| https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | always sing your heart out | PSA: always sing your heart out, you'll never know who's going to listen. | 00:00-00:03 always sing your heart out \| 00:03-00:08 cartoon orange cat sing-along packaging \| 00:08-00:14 钩子 / caption / 包装研究 \| 00:14-00:20 软收口延续 | orangecat0088（未认证） | 软收口 CTA 或当前未恢复明确 CTA | 保留识别优先的包装逻辑，再用自有素材重写证明层。 |
| https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | SuperCat Papa | SuperCat Papa | 00:00-00:03 SuperCat Papa \| 00:03-00:08 story-led orange cat meme packaging \| 00:08-00:14 钩子 / caption / 包装研究 \| 00:14-00:20 软收口延续 | usatiktoker23（未认证） | 软收口 CTA 或当前未恢复明确 CTA | 保留识别优先的包装逻辑，再用自有素材重写证明层。 |
| https://www.tiktok.com/@aicatstories44/video/7636137611576282399 | sad cat | sad cat | 00:00-00:03 sad cat \| 00:03-00:08 sad orange cat ai story packaging \| 00:08-00:14 钩子 / caption / 包装研究 \| 00:14-00:20 软收口延续 | aicatstories44（未认证） | 软收口 CTA 或当前未恢复明确 CTA | 保留识别优先的包装逻辑，再用自有素材重写证明层。 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | candidate-1 | 待补视频链接 | 00:00-00:03 | 钩子 and first proof beat from the top-ranked video. | Per-video 钩子 breakdown |
| transcript | candidate-1-script | paste-transcript-source | 00:00-00:12 | Recovered caption or subtitle lines supporting the time-axis rhythm. | Full script / key lines |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:14 | always sing your heart out | Per-video teardown: 钩子-to-proof timeline for candidate 1 |
| transcript | 7636206423080226070-script | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:12 | PSA: always sing your heart out, you'll never know who's going to listen. | Recovered caption / script lines for candidate 1 |
| video | 7636373657828347158 | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | 00:00-00:14 | SuperCat Papa | Per-video teardown: 钩子-to-proof timeline for candidate 2 |
| transcript | 7636373657828347158-script | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | 00:00-00:12 | SuperCat Papa | Recovered caption / script lines for candidate 2 |
| video | 7636137611576282399 | https://www.tiktok.com/@aicatstories44/video/7636137611576282399 | 00:00-00:14 | sad cat | Per-video teardown: 钩子-to-proof timeline for candidate 3 |
| transcript | 7636137611576282399-script | https://www.tiktok.com/@aicatstories44/video/7636137611576282399 | 00:00-00:12 | sad cat | Recovered caption / script lines for candidate 3 |

## 可复用公式

_Turn the shared pattern into direct creation guidance._

共性规律不是单条视频摘要，而是把多个 shortlisted 视频里反复出现的开头、证明和收口组织方式抽出来。

最终写法要能直接指导新脚本，不是只适合做研究备忘录。

### 创作规则

| 元素 | 观察到的模式 | How To Reuse It | What Not To Copy Blindly | 证据引用 |
| --- | --- | --- | --- | --- |
| 开头钩子 | 沿用让人一眼看懂的首句识别信号 | 保留首句承诺，但把原视频的人 / 物 / 主题替换成自有版本 | 不要用泛化铺垫开场 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 证明段 | 用权威、出镜人或可识别社会线索承接证明 | 把借来的账号势能换成自有证明物、创作者或使用场景 | 证明太弱，整套结构就会塌 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 包装方式 | 文案保持短、原生、主题一眼可懂 | 保留压缩后的主题 cue，减少解释性废话 | 解释过多会把结构拉平 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 软收口 / CTA | 优先用延续式收口或下一次点击引导 | 更适合引导继续看、收藏、去主页，而不是硬卖 | 强转化 CTA 可能破坏原生适配 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | candidate-1 | 待补视频链接 | 00:00-00:02 | Opening reveal pattern reused across the strongest shortlisted videos. | 钩子公式 |
| video | candidate-2 | 待补视频链接 | 00:03-00:08 | 证明-beat structure that repeats without relying on the same product. | 证明 formula |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:02 | always sing your heart out | Shared 钩子 formula distilled from the strongest shortlisted video |
| video | 7636373657828347158 | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | 00:03-00:08 | SuperCat Papa | 证明-beat pattern that repeats without relying on the same product shell |

## 风险与适配说明

_Explain where false copying would fail._

- 认证账号或大号势能可能抬高表现，必须和可迁移的包装逻辑拆开看。
- 这份采集包缺评论样本，所以人群语言相关结论只能弱持有。
- 如果某条候选缺 caption 文本，这一行就应视为深拆证据更弱的样本。

| Risk Area | Why It Can Mislead | What To Check Before Reuse |
| --- | --- | --- |
| Authority inflation | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | Check whether the format still works after removing verified-account or featured-person lift. |
| Thin caption recovery | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | If the 钩子 text is thin, require screenshot, subtitle, or downloaded metadata before overlearning structure. |
| Topic overfit | Shortlist-level pattern | Preserve the packaging move, but rewrite the topic and proof lane before calling the format reusable. |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | full-video | always sing your heart out | Risk note: borrowed authority or thin-caption candidates must stay flagged |

## 下一步动作

_Leave a concrete next production move._

下一步不是重新搜更多视频，而是把当前 shortlist 的脚本全文、时间轴与证明段先拆完整，再进入改写与生产。

1. 先把 https://www.tiktok.com/@orangecat0088/video/7636206423080226070 做成主控深拆样本，完整补齐脚本、时间轴和证明链。
2. 第二条作为备选 钩子 / 主题对照线，避免团队只围着单一赢家过拟合。
3. 第三条保留为反例或低权威对照样本，验证这套包装离开账号势能后是否仍成立。

| Output Block | What Must Be Delivered | Who Uses It Next |
| --- | --- | --- |
| 优先深拆 1 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 钩子 / caption / 包装研究 |
| 优先深拆 2 | https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | 钩子 / caption / 包装研究 |
| 优先深拆 3 | https://www.tiktok.com/@aicatstories44/video/7636137611576282399 | 钩子 / caption / 包装研究 |

## 备注

- Primary teardown control: https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | always sing your heart out | 2610 点赞，28400 播放，62 分享.
- Contrast reference: https://www.tiktok.com/@usatiktoker23/video/7636373657828347158 | 钩子 / caption / 包装研究 | 1194 点赞，16200 播放，40 分享，18 评论.
- Adaptation rule: preserve the recognition-first 钩子, then swap borrowed authority for owned proof, owned talent, or owned product context.

## 来源

- 汇总文件（汇总文件（aggregate_summary.json））
- 排序视频文件（排序视频文件（aggregate_ranked_videos.json））
- https://www.tiktok.com/@validation.orangecat
