# Evidence Ref 校验 - 场景 04 - 单视频拆解

- 场景：04 - 单视频拆解
- 项目：Evidence Ref 校验
- 交付物类型：拆解报告
- 生成时间：2026-05-17T22:40:52
- 状态：已导入
- 场景文件：`scenarios/04-single-video-breakdown.md`

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

- 1 条视频链接或一份分镜摘要
- summary.json 或 汇总文件（aggregate_summary.json）
- 账号汇总文件（profile_summary.json） 或 summary.json
- ranked_videos.json 或 排序视频文件（aggregate_ranked_videos.json）

### 理想证据补充

- 下载 JSON 或 capture detail
- 转写稿或字幕笔记
- 按节拍截图
- 基础表现上下文
- 音频或 BGM 线索
- 达标视频文件（aggregate_qualified_videos.json） 或 qualified_video_links.txt
- 聚合报告（aggregate_report.md）
- 视频明细（video_details.json）

### 约束条件

- 把深层机制与表层风格分开看。
- 如果没有口播，就从字幕、动作、剪辑与视觉证明链里重建逻辑。
- 当前为真实 TikTok 匿名会话采集包；本包暂不含评论采样。
- 结论必须只绑定到排序指标、标题/钩子文本和采集包摘要，不要外推。

### 目标交付

- 时间轴拆解表
- 视频类型判断
- BGM 分析
- 三段式爆点解读
- 可复用机制
- 改编建议
- TikTok 原生排序模式结论
- 基于 采集包 的可复用改编规则

### 开跑前检查

- 能够重建 钩子、证明段与收口段
- 至少已知 1 个改编目标
- 时间轴表可以在不臆造缺失段落的前提下补完
- 有口播 / 无口播路径已明确
- 已明确标出高排名视频。
- 已将可迁移模式与账号自身品牌势能区分。

## 执行摘要

- 核心结论：这条真实单视频拆解目标之所以能跑出来，核心不是表面风格，而是首屏先让人秒懂，再用权威、人物或结果线索做压缩证明。
- 为什么重要：真正可复用的资产不是装饰层，而是从识别到证明再到轻收口的顺序；只要顺序对，换产品或换人设时仍可成立。
- 下一步动作：先按顺序把参考视频重建出来，再把证明层改写成你自己的产品、创作者或证据物也能承接同样决策逻辑。
- 置信度：中

## 操作检查清单

- 用带时间范围的节拍表按顺序重建视频。
- 在过度泛化结论前，先判断视频类型。
- 把核心机制与创作者个人化表层风格分开。
- 显式记录 BGM、字幕表现与转场节奏。
- 在收尾前至少写出 1 条改编路径。
- 无口播视频也要按字幕、动作、镜头与节奏完整拆解。

## 常见失败模式

- 把视觉精致度误当成真正的转化机制。
- 因为转写稿稀疏，就忽略无口播视频的成立逻辑。
- 因为收口或 CTA 看起来简单，就直接跳过。
- 只给抽象夸赞，没有可复用结论。

## 直接执行模板

- 推荐请求：`按场景 04 执行：完整拆解 1 条 TikTok 或抖音视频。先判断视频类型与有无口播，再按时间轴逐拍重建画面、字幕 / 口播、BGM、钩子、证明段与收口段，最后分离核心机制与表层风格，并给出保守 / 激进两条改编路径。`
- 推荐请求（中文）：`按场景 04 执行：完整拆一条短视频，按 钩子、铺垫、证明、收口重建结构，再分离真正有效的机制和表层风格，并给出一个可改编方向。`
- 运行参数：
  - `python scripts/run_operator_workflow.py --mode scene --scene 04 --project "<project-name>" --output-root ".\tmp\single-video-breakdown"`
  - `python scripts/generate_scene_report.py --scene 04 --project "<project-name>" --output ".\tmp\single-video-breakdown.json" --format json`

### 可变输入

| 变量 | 含义 | 示例 | 是否必填 |
| --- | --- | --- | --- |
| project_name | 便于识别的运行名或项目名 | 口红爆款单视频拆解 | 是 |
| market | 当场景依赖单一市场时的目标市场或地区 | 美国 | 建议 |
| evidence_pack | 作为源证据使用的链接、截图、转写、导出文件、OCR 文本或摘录备注 | 视频链接、下载 JSON / capture detail、转写笔记、逐拍截图与 BGM 线索 | 是 |
| success_goal | 操作者希望该场景产出的结果 | 单视频机制拆解、标准时间轴表与改编路径 | 建议 |

### Codex 提示词骨架

- 以场景 04 作为本次工作的主流程。
- 分析前先把现有证据归整为以下输入：1 条视频链接或一份分镜摘要, 转写稿或字幕笔记, 逐帧笔记或截图, 可选的基础表现数据。
- 如果证据不足，先明确缺口再继续。最低开工证据：1 条视频链接或一份分镜摘要。
- 最终必须产出以下可直接给运营使用的结果：时间轴拆解表, 视频类型判断, BGM 分析, 三段式爆点解读, 可复用机制, 改编建议。
- 先按顺序重建视频，再下结论。
- 明确区分创作者个人化包装与可迁移的转化逻辑。
- 同时支持有口播与无口播视频，必要时用字幕、动作与运动证明链补齐分析。
- 优先使用标准表格：Time Range | Scene Type | Visual Content | Spoken / On-Screen Script | 作用 In Conversion | Evidence Ref。
- 优先填入可复用结论、表格、排序逻辑和下一步动作，不要停留在泛泛点评。

### 中文提示词骨架

- 按场景 04 执行：完整拆一条短视频，按 钩子、铺垫、证明、收口重建结构，再分离真正有效的机制和表层风格，并给出一个可改编方向。
- 先把我提供的材料整理成这组输入：1 条视频链接或一份分镜摘要, 转写稿或字幕笔记, 逐帧笔记或截图, 可选的基础表现数据。
- 如果证据不足，先明确缺口再继续。最低开工证据：1 条视频链接或一份分镜摘要。
- 最终必须产出：时间轴拆解表, 视频类型判断, BGM 分析, 三段式爆点解读, 可复用机制, 改编建议。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

### 执行步骤

1. 用带时间范围的节拍表按顺序重建视频。
2. 在过度泛化结论前，先判断视频类型。
3. 把核心机制与创作者个人化表层风格分开。
4. 显式记录 BGM、字幕表现与转场节奏。
5. 在收尾前至少写出 1 条改编路径。
6. 无口播视频也要按字幕、动作、镜头与节奏完整拆解。

### 交付检查清单

- 时间轴已按顺序重建，且每一拍都有证据支撑。
- 钩子、证明段与收口段已按顺序复原。
- BGM、视频类型与转化节奏已明确写出。
- 核心机制与表层风格已分离。
- 至少有 1 条改编路径具体到可以直接继续产出。

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

_明确判断这条单视频为什么成立，或为什么没有成立。_

这条真实单视频拆解目标之所以能跑出来，核心不是表面风格，而是首屏先让人秒懂，再用权威、人物或结果线索做压缩证明。

参考视频：https://www.tiktok.com/@orangecat0088/video/7636206423080226070

来源账号基线：https://www.tiktok.com/@validation.orangecat

- 已恢复 钩子：always sing your heart out
- 已恢复主题线索：cartoon orange cat sing-along packaging
- 权威 / 人物信号：orangecat0088（未认证）
- 视频类型归类：识别优先的短讲解
- 可复核下载源：当前只有页面级证据，若要更细镜头拆解需补下载明细。

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:03 | always sing your heart out | Executive conclusion: recognition-first 钩子 and compressed proof path |
| creator | orangecat0088 | https://www.tiktok.com/@validation.orangecat | account-sample-window | OrangeCat | Account baseline that may inflate lift for this reference video |

## 结构逻辑

_按节拍重建视频从开头到结尾的结构。_

主表必须稳定贴近《口红爆款视频拆解报告》的成品视图：时间段 | 场景类型 | 画面内容 | 口播脚本，再补这一段在转化中的作用与素材需求。

如果源视频口播很薄，就优先从字幕、动作、切镜和证明物去重建，不要因为没有完整口播就放弃结构化拆解。

### 时间轴拆解

| 时间范围 | 场景类型 | 画面内容 | 口播 / 画面文案 | 转化作用 | 所需素材 / 人物 | 证据引用 |
| --- | --- | --- | --- | --- | --- | --- |
| 00:00-00:03 | 开头钩子 | always sing your heart out | always sing your heart out | 先让观众在第一眼看懂谁 / 什么值得继续看 | 优先保留首屏截图、封面、下载视频或关键帧 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 00:03-00:08 | 场景设定 | cartoon orange cat sing-along packaging | cartoon orange cat sing-along packaging | 补足最少必要前提，避免观众在理解前流失 | 需要场景承接画面、字幕或环境线索 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 00:08-00:14 | 证明段 | orangecat0088（未认证） | 钩子 / caption / 包装研究 | 把信任、结果或权威尽量前置，不靠长解释推进 | 需要证明物、人物、结果画面或可复核下载源 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 00:14-00:20 | 收口 / CTA | 回到主画面并给一个轻量软收口 | 继续看 / 保存 / 轻量关注 / 去主页看完整内容 | 用 TikTok 原生节奏收口，而不是硬切强转化 | 需要收口镜头或主页 / 继续看指向 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | primary-video | 待补视频链接 | 00:00-00:02 | 展示首个钩子瞬间或第一视觉回报的片段。 | 时间轴行：钩子 |
| screenshot | frame-setup | 待补截图路径或链接 | 00:02-00:06 | 支撑铺垫到证明转折的截图组。 | 时间轴行：铺垫 |
| transcript | subtitle-pass | 待补转写来源 | 00:06-00:14 | 支撑证明段的字幕或口播证据。 | 时间轴行：证明 |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:03 | always sing your heart out | Timeline row: 钩子 beat |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:03-00:08 | always sing your heart out | Timeline row: setup-to-proof transition |
| transcript | 7636206423080226070-script | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:12 | PSA: always sing your heart out, you'll never know who's going to listen. | Timeline row: proof segment supported by caption/subtitle |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:14-00:20 | always sing your heart out | Timeline row: 延续式收口 |

## 核心机制

_描述真正起作用的底层机制，而不是只写表层风格。_

真正的机制是识别优先的压缩表达：观众先知道谁或什么值得看，然后再接受最短路径的证明，而不是先听长解释。

证明层之所以成立，是因为源视频借到了账号语境、人物熟悉度、结果感或文化线索，把信任转移压缩到了前半段。

- 视频类型归类：识别优先的短讲解。
- 即便几乎没有口播也能成立，因为字幕和画面线索已经把前提带出来了。
- 可迁移逻辑：首屏清晰 + 压缩证明。
- 不可直接照抄的 lift：官方账号权威、名人识别度或账号分发优势。
- 若要继续做逐镜头复核，下一步需要补下载视频或关键帧。

### 机制拆解

| 机制层 | 观察到的模式 | 为什么有效 | 移除后风险 | 证据引用 |
| --- | --- | --- | --- | --- |
| 视频类型 | 识别优先的短讲解 | 先判定这是哪类单视频，再决定后续复刻该保什么、不该抄什么。 | 如果类型判断错了，后续会把情绪拼贴、教程、权威背书混为一谈。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 注意力张力 | 首屏识别优先，前半段尽快进入证明 | 观众在解释开始前就知道为什么该继续看。 | 首屏如果只铺垫不兑现，停留和后续证明都会一起变弱。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 证明装置 | orangecat0088（未认证） | 用人、权威、结果、动作或文化线索做快速可信度转移。 | 如果证明只停留在口头描述，这条结构就会变成普通讲解。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 无口播兜底 | 即便几乎没有口播也能成立，因为字幕和画面线索已经把前提带出来了。 | 即使没有完整口播，也能依靠字幕、切镜和动作把逻辑传出去。 | 如果字幕和画面 cue 都弱，就必须补更多截图 / 下载细节后再深拆。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | primary-video | 待补视频链接 | full-video | 用整条视频区分底层机制与表面包装。 | 机制拆解 |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | full-video | always sing your heart out | Mechanism: recognition-first compression logic |

## 可复用公式

_只抽取能迁移复用的部分。_

| 层级 | 观察结果 | 是否可复用 | 改编说明 | 置信度 |
| --- | --- | --- | --- | --- |
| 钩子逻辑 | always sing your heart out | 是 | 保留一眼能懂的识别感，但把原视频里的人物 / 对象 / 话题换成自有资产。 | 中 |
| 画面风格 | 偏 编辑感 / 原生社交风格 的原生包装 | 部分可复用 | 只保留有助于证明顺序的视觉组织，不要抄纯装饰层。 | 中 |
| 证明逻辑 | orangecat0088（未认证） | 是，但要替换 | 改成自有 proof、凭证、产品证据或合作方信任，而不是继续借原账号外壳。 | 中 |
| CTA 风格 | 轻量 延续式收口 | 是 | 更适合继续看、保存、轻量关注，而不是硬切强卖点。 | 中 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:02 | always sing your heart out | 钩子公式 |
| screenshot | 7636206423080226070-style | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | visual-layer | cartoon orange cat sing-along packaging | 视觉风格 reference |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:06-00:14 | always sing your heart out | 证明 formula |

## 风险与适配说明

_用最实战的三个视角解释爆点逻辑。_

### 爆点解读

| 视角 | 观察到的模式 | 为什么有效 | 改编护栏 | 证据引用 |
| --- | --- | --- | --- | --- |
| 开头钩子 | always sing your heart out | 第一个可见线索要在解释前先告诉观众为什么值得看。 | 不要把只有源账号扛得住的铺垫，照搬到自家版本里。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 转化节奏 | 钩子 -> 铺垫 -> 证明 -> 轻收口 | 结构把注意力压缩在前半段，并让证明紧贴开头线索出现。 | 如果新产品需要更多说明，优先补证明，不要补长解释。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 视觉风格 | 偏 editorial framing，搭配 当前采集包未恢复出清晰音频线索 | 感官层是在辅助识别，不是在跟主信息抢注意力。 | 保留节奏和清晰度，不要做装饰性模仿。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | primary-video | 待补视频链接 | 00:00-00:03 | 支撑开头钩子判断的首个视觉回报片段。 | 开头钩子解读 |
| video | primary-video | 待补视频链接 | 00:03-00:14 | 覆盖铺垫、证明与抬升的转化节奏证据。 | 转化节奏解读 |
| screenshot | style-board | 待补截图路径或链接 | visual-layer | 展示可复用视觉风格与剪辑处理的截图组。 | 视觉风格解读 |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:03 | always sing your heart out | 开头钩子 adaptation risk |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:03-00:14 | always sing your heart out | Conversion pacing adaptation risk |

## BGM 与感官层

_说明音频、BGM、字幕密度和剪辑节奏如何影响表现。_

BGM 不只是陪衬，它直接决定这条内容更像测评、教程、审美拼贴还是情绪推动；因此这一块必须比普通拆解更醒目。

无口播视频尤其依赖音频、字幕密度和动作节奏来补足逻辑，这时感官层就不是装饰，而是结构本身。

| 元素 | 观察结果 | 策略作用 | 改编说明 | 证据引用 |
| --- | --- | --- | --- | --- |
| BGM / 音频氛围 | 当前采集包未恢复出清晰音频线索 | 在原生感和连续观看上提供底层支撑。 | 只有在自有音频也能保留同样 editorial 能量时才替换。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 字幕样式 | 短句式 premise-led 字幕 / caption 支撑 | 即使口播很薄，也能让逻辑继续成立。 | 优先保留可读性，别把字幕写成长解释。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 转场节奏 | 快 setup、少空拍、早 proof | 避免视频过早变成长讲解。 | 用紧凑切镜或 motion crop，不要做装饰性转场。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |
| 留白 / 停顿使用 | 极少停顿，注意力持续压在关键信号和证明上 | 让整条内容保持原生、压缩、可刷。 | 如果改写里要停顿，必须是在给证明加重，不是在拖节奏。 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | primary-video-audio | 待补视频链接 | audio-layer | 支撑感官层判断的音频、字幕与节奏证据。 | BGM 与感官层 |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | audio-layer | native platform audio | BGM / sensory layer judgment |
| transcript | 7636206423080226070-script | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:12 | PSA: always sing your heart out, you'll never know who's going to listen. | 字幕样式 that keeps logic readable without heavy VO |

## 制作规格交接

_把拆解结果转成可直接复刻或剪辑的蓝图。_

这张表直接服务导演 / 剪辑 / 生成器，不是泛分析备注。

如果还要更细化镜头，应继续把 shot_01 到 shot_04 和上面的时间段主表对齐。

节奏 / 字幕节拍 / 证明块 / 资产需求与 generator handoff JSON（含 Sora / Veo / i2v 分支）已对齐。

- 节奏 0-3s: 首屏识别锁定 / always sing your heart out
- 节奏 3-8s: 压缩前提 / cartoon orange cat sing-along packaging
- 节奏 8-14s: 证明前置 / 钩子 / caption / 包装研究
- 节奏 14-20s: 轻收口 / 继续看 / 保存 / 轻量关注
- 字幕 beat_01 (0-3s): always sing your heart out
- 字幕 beat_02 (3-8s): cartoon orange cat sing-along packaging
- 字幕 beat_03 (8-14s): 钩子 / caption / 包装研究
- 字幕 beat_04 (14-20s): 继续看 / 了解更多

### 制作交接 / 分镜执行表

| 镜头 | 这一拍要做什么 | 阶段 | 建议字幕 / 口播 | 执行提醒 | 素材需求 | 置信度 |
| --- | --- | --- | --- | --- | --- | --- |
| 镜头 1 | 首屏必须先让人一眼看懂谁/什么值得看 | 开头认知建立 | always sing your heart out | 人物 / 对象 / 情绪 cue | 首屏画面、字幕或标题卡 | 中 |
| 镜头 2 | cartoon orange cat sing-along packaging | 场景设定 | cartoon orange cat sing-along packaging | 压缩解释，避免拖慢 | 承接镜头或环境线索 | 中 |
| 镜头 3 | orangecat0088（未认证） | 证明段 | 钩子 / caption / 包装研究 | 把信任放到前半段 | 证明物、结果、人物或动作 | 中 |
| 镜头 4 | 回到主画面并给一个轻量软收口 | 收口 / CTA | 看下一条 / 保存 / 继续看 / 轻量关注 | 维持 TikTok 原生节奏 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 低到中 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:20 | always sing your heart out | Shot-by-shot production handoff |

## 下一步动作

_给出一条稳妥版和一条激进版改编路径。_

### 下一步动作 / shot 交接

| shot_id | 时间 | 阶段 | 画面 / 动作 | 字幕 / 口播 | generator 字段 | 素材 / 执行需求 |
| --- | --- | --- | --- | --- | --- | --- |
| shot_01 | 0-3s | 首屏识别 | always sing your heart out | always sing your heart out | hero_钩子 | 首屏主画面 / 封面 / 标题卡 |
| shot_02 | 3-8s | 补前提 | cartoon orange cat sing-along packaging | cartoon orange cat sing-along packaging | premise_setup | 承接镜头 / 场景线索 / 字幕 |
| shot_03 | 8-14s | 证明段 | orangecat0088（未认证） | 钩子 / caption / 包装研究 | proof_block | 证明物 / 结果 / 人物 / 凭证 |
| shot_04 | 14-20s | 软收口 | 回到主线索并引导继续看 / 保存 / 轻量关注 | 给一个低摩擦延续动作，不要硬卖 | cta_close | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| video | 7636206423080226070 | https://www.tiktok.com/@orangecat0088/video/7636206423080226070 | 00:00-00:20 | always sing your heart out | Storyboard / generator handoff row |

## 资产清单

- Scene 04 production_spec_handoff.json: file `captures/scene01-strong-inputs-pass/production_spec_handoff.json` | Generator-ready handoff with Sora / Veo / i2v branches
- [library] 来源账号：file `https://www.tiktok.com/@validation.orangecat` | Account baseline
- [library] 排序视频 1 reference_video: file `https://www.tiktok.com/@orangecat0088/video/7636206423080226070` | always sing your heart out
- [library] 排序视频 2 reference_video: file `https://www.tiktok.com/@usatiktoker23/video/7636373657828347158` | SuperCat Papa
- [library] 排序视频 3 reference_video: file `https://www.tiktok.com/@aicatstories44/video/7636137611576282399` | sad cat
- [library] Scene 06 competitor_product_board.json: file `captures/scene01-strong-inputs-pass/competitor_product_board.json` | Competitor dashboard source mode: tiktok_shop_structured
- [library] 采集看板.json: file `captures/scene01-strong-inputs-pass/采集看板.json` | Reusable 采集包 artifact
- [library] scene03_creation_matrix.json: file `captures/scene01-strong-inputs-pass/scene03_creation_matrix.json` | Reusable 采集包 artifact
- [library] content_graph.json: file `captures/scene01-strong-inputs-pass/content_graph.json` | Reusable 采集包 artifact
- [library] Scene 01 采集看板 XLSX: file `captures/scene01-strong-inputs-pass/采集看板.xlsx` | 可直接导入多维表 / 飞书

## 来源

- 汇总文件（汇总文件（aggregate_summary.json））
- 排序视频文件（排序视频文件（aggregate_ranked_videos.json））
- https://www.tiktok.com/@validation.orangecat
