# Evidence Ref 校验 - 场景 08 - 评论挖掘与人群画像

- 场景：08 - 评论挖掘与人群画像
- 项目：Evidence Ref 校验
- 交付物类型：洞察报告
- 生成时间：2026-05-17T22:40:56
- 状态：已导入
- 场景文件：`scenarios/08-multi-product-comment-mining-and-persona-report.md`

## 任务上下文

真实 TikTok 采集包导入自 validation/captures/scene08-multi-product-home-goods-comments，当前用于未分类赛道。当前看板规模：0 条已排序 / 0 条达标.
来源账号：待补; 会话质量：待补; 查询词：未提供; 主题：未提供.
采集根目录：validation/captures/scene08-multi-product-home-goods-comments

### 输入材料

- 账号：
- 排序视频数：0
- 达标视频数：0
- 采集根目录：validation/captures/scene08-multi-product-home-goods-comments

### 最低证据要求

- 至少 2 个商品的评论
- summary.json 或 汇总文件（aggregate_summary.json）
- 账号汇总文件（profile_summary.json） 或 summary.json
- ranked_videos.json 或 排序视频文件（aggregate_ranked_videos.json）

### 理想证据补充

- 每个商品 20-40 条评论
- 市场上下文
- 定位目标
- 价格带上下文
- 购买型评论语言样本
- 达标视频文件（aggregate_qualified_videos.json） 或 qualified_video_links.txt
- 聚合报告（aggregate_report.md）
- 视频明细（video_details.json）

### 约束条件

- 如果评论量偏少，应把结论标记为暂定判断。
- 结论必须只绑定到排序指标、标题/钩子文本和采集包摘要，不要外推。

### 目标交付

- 购买因素提炼
- 好评关键词提炼
- 差评痛点提炼
- 价格带差异视图
- 人群画像总结
- 选品与内容启发
- TikTok 原生排序模式结论
- 基于 采集包 的可复用改编规则

### 开跑前检查

- 评论应按商品维度分组保留。
- 可以直接引用重复出现的原话。
- 样本量不足的前提已明确写出。
- 合并后仍保留来源商品标记。
- 基础价值与改进机会可以分开
- 已明确标出高排名视频。
- 已将可迁移模式与账号自身品牌势能区分。

## 执行摘要

- 核心结论：这份 TikTok 评论包里最强的重复用户语言，已经能更清楚地归到购买因素、信任信号和差评痛点三类，并且能用回复链压力把浅层热闹和真实异议处理区分开。
- 为什么重要：这很重要，因为操作者拿到的不再是一堆平铺评论，而是更干净的买家语言聚类、来源商品标签、去重后的高频原话和回复链线索。
- 下一步动作：在下一轮测试前，先用这些已清洗的差评痛点和信任信号去写评论回复、FAQ 文案和定位话术。
- 置信度：中

## 操作检查清单

- 合并品类信号前，先按商品维度保留评论分组。
- 来源商品标签要一路保留到洞察层。
- 优先引用重复出现的用户原话，而不只是分析师转述。
- 把痛点与欲望翻译成产品决策和脚本启发。
- 优先突出物流、包装、真假、退货、before-after、尺码 / 色号适配这类购买型语言。

## 常见失败模式

- 把一次性抱怨和真正重复出现的痛点混为一谈。
- 只做情绪总结，没有具体用户原话。
- 过早抹平来源商品差异，丢掉价格带洞察。
- 忽略欲望、抱怨和信任信号之间的区别。

## 直接执行模板

- 推荐请求：`按场景 08 执行：把多个商品的评论做成品类级人群洞察。先按来源商品分组，再提炼购买因素、好评关键词、差评痛点、价位差异，并保留重复用户原话与来源商品标签，最后回到人群画像、定位与脚本话术建议。`
- 推荐请求（中文）：`按场景 08 执行：把多个产品的评论做合并挖掘，分开提炼痛点、欲望和信任信号，并保留原话，最后转成人群和话术启发。`
- 运行参数：
  - `python scripts/run_operator_workflow.py --mode scene --scene 08 --project "<project-name>" --output-root ".\tmp\comment-mining-persona"`
  - `python scripts/generate_scene_report.py --scene 08 --project "<project-name>" --output ".\tmp\comment-mining-persona.json" --format json`

### 可变输入

| 变量 | 含义 | 示例 | 是否必填 |
| --- | --- | --- | --- |
| project_name | 便于识别的运行名或项目名 | 口红品类评论挖掘与人群画像报告 | 是 |
| market | 当场景依赖单一市场时的目标市场或地区 | 美国 | 建议 |
| evidence_pack | 作为源证据使用的链接、截图、转写、导出文件、OCR 文本或摘录备注 | 来自 3-5 个商品的评论样本，已标出物流、包装、真假、退货、before-after、色号 / 尺码适配等购买型语言 | 是 |
| success_goal | 操作者希望该场景产出的结果 | 买家语言提炼、基础价值 / 改进机会分离与人群画像启发 | 建议 |

### Codex 提示词骨架

- 以场景 08 作为本次工作的主流程。
- 分析前先把现有证据归整为以下输入：来自 2 个以上商品的评论, 市场, 产品定位目标, 可选的价格带备注。
- 如果证据不足，先明确缺口再继续。最低开工证据：至少 2 个商品的评论。
- 最终必须产出以下可直接给运营使用的结果：购买因素提炼, 好评关键词提炼, 差评痛点提炼, 价格带差异视图, 人群画像总结, 选品与内容启发。
- 合并品类信号前，先按商品维度保留评论分组。
- 优先保留重复用户原话，不要只做抽象情绪总结。
- 把品类级基础价值与品类级改进机会明确分开。
- 尽量突出物流、包装、真假、退货、before-after、尺码 / 色号适配等购买型语言。
- 优先填入可复用结论、表格、排序逻辑和下一步动作，不要停留在泛泛点评。

### 中文提示词骨架

- 按场景 08 执行：把多个产品的评论做合并挖掘，分开提炼痛点、欲望和信任信号，并保留原话，最后转成人群和话术启发。
- 先把我提供的材料整理成这组输入：来自 2 个以上商品的评论, 市场, 产品定位目标, 可选的价格带备注。
- 如果证据不足，先明确缺口再继续。最低开工证据：至少 2 个商品的评论。
- 最终必须产出：购买因素提炼, 好评关键词提炼, 差评痛点提炼, 价格带差异视图, 人群画像总结, 选品与内容启发。
- 输出必须可直接给运营、拆解、脚本、测试或交付使用，优先给表格、排序逻辑、复用规则和下一步动作。

### 执行步骤

1. 合并品类信号前，先按商品维度保留评论分组。
2. 来源商品标签要一路保留到洞察层。
3. 优先引用重复出现的用户原话，而不只是分析师转述。
4. 把痛点与欲望翻译成产品决策和脚本启发。
5. 优先突出物流、包装、真假、退货、before-after、尺码 / 色号适配这类购买型语言。

### 交付检查清单

- 已清晰区分重复的痛点、欲望与信任信号。
- 已保留真实用户语言证据。
- 合并分析后仍能看见来源商品。
- 基础价值与改进机会已明确分开。
- 人群画像与话术启发均直接来自评论挖掘。

## 证据总表

| 标签 | 详情 | 来源 |
| --- | --- | --- |
| 汇总 | 已排序=0; 达标=0; 最低点赞= | summary.json |
| 账号汇总 | 账号=; 会话=待补; 已排序=0 | summary.json |
| Content graph clusters | creator=0; sound=0; hashtag=0; videos=0 | content_graph.json |

## 执行结论

_概括这些评论揭示出的品类购买者特征。_

这份 TikTok 评论包里最强的重复用户语言，已经能更清楚地归到购买因素、信任信号和差评痛点三类，并且能用回复链压力把浅层热闹和真实异议处理区分开。

这次共从 3 条 TikTok 视频中采到了评论样本。

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| comment | hg-019 | https://www.tiktok.com/@travelpackessentials/video/7633000000000000003 | comment-thread | compression-packing-cubes: I need to know if the zipper breaks after two trips because that always happens with cheap sets. | Executive conclusion: strongest purchase-factor language |

## 高层判断

_写出最强的需求侧判断。_

核心教训是：一旦把低信号表情噪音、病毒式重复留言和浅层互动诱饵清理掉，真正重复出现的买家语言就会更可执行。

- 原始评论=24 | 清洗后=24 | 过滤噪音=0
- 最强购买因素：价格 / 性价比顾虑
- 最强差评痛点簇：物流 / 包装顾虑
- 最有价值的回复链簇：一般反应 | 回复压力=56 | Can someone show this with Costco-size bottles because that is the only thing stopping me f…
- 价格带信号：未恢复出强价格带分层
- 回复链合成条数：6

### 来源商品概览

| 来源商品 | 价格带 | 数量 | 主要购买触发因素 | 主要抱怨 |
| --- | --- | --- | --- | --- |
| pet-hair-remover-roller | 价格敏感 | 8 | 购买意向 \| I need to know if this is one of those dropship rollers because I saw t… | 真假 / 正品顾虑 \| I ordered it because the before and after on the couch looked real and… |
| under-sink-organizer | 偏高端 | 8 | 购买意向 \| Need a side-by-side before after with all the products loaded because e… | 物流 / 包装顾虑 \| Mine arrived fast but one tray corner was cracked. Seller refunded me w… |
| compression-packing-cubes | 价格敏感 | 8 | 价格 / 性价比顾虑 \| I need to know if the zipper breaks after two trips because that always… | 退货 / 退款顾虑 \| Returned because the large cube was too tall for my carry-on, not becau… |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| comment | hg-002 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: 回复链活跃（24 条回复），已经足够视为真实的购买前确认或异议处理信号。 | High-level judgment: synthesized reply-chain anchor comment |
| comment | hg-019 | https://www.tiktok.com/@travelpackessentials/video/7633000000000000003 | comment-thread | compression-packing-cubes: I need to know if the zipper breaks after two trips because that always happens with cheap sets. | High-level judgment: purchase-factor cluster |
| comment | hg-003 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: Mine arrived fast but one tray corner was cracked. Seller refunded me without making me ship it back. | High-level judgment: complaint / objection cluster |
| comment | hg-002 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: Please tell me if the measurements are real because half of these organizers never fit around the pipe. | High-level judgment: reply-chain pressure cluster |

## 证据聚类

_跨商品聚类重复出现的用户语言。_

主报告优先贴近四段式：购买因素、好评关键词、差评痛点、价位差异。

每个聚类都尽量保留来源商品、重复原话、回复链压力和价格带线索，方便直接翻译成 FAQ、评论回复和卖点脚本。

- 回复链综合（顶层评论 + 追问回复已分开清洗）：
- 一般反应 | 回复压力=56 | 来源=under-sink-organizer | 回复链活跃（24 条回复），已经足够视为真实的购买前确认或异议处理信号。
- 一般反应 | 回复压力=55 | 来源=compression-packing-cubes | 回复链活跃（19 条回复），已经足够视为真实的购买前确认或异议处理信号。
- 购买意向 | 回复压力=36 | 来源=pet-hair-remover-roller | Authenticity / dropship suspicion shows up in the reply chain.
- 价格 / 性价比顾虑 | 回复压力=33 | 来源=pet-hair-remover-roller | Durability proof is the biggest missing trust layer.

### 评论信号聚类

| 聚类类型 | 重复短语 / 主题 | 来源商品 | 说明了什么 | 产品 / 内容启发 |
| --- | --- | --- | --- | --- |
| 好评关键词 | Bought this because my cleaning bottles were a mess and the pull-out shelf actually fits under a narrow sink. | under-sink-organizer, pet-hair-remover-roller, compression-packing-cubes | 一般反应 \| 重复提及=8 \| 回复压力=134 \| 价位=不明确 \| 信号=high | 除非它持续重复出现且更具体，否则先视为弱信号。 回复链：回复链活跃（18 条回复），已经足够视为真实的购买前确认或异议处理信号。 |
| 购买因素 | I need to know if the zipper breaks after two trips because that always happens with cheap sets. | compression-packing-cubes, pet-hair-remover-roller, under-sink-organizer | 价格 / 性价比顾虑 \| 重复提及=5 \| 回复压力=65 \| 价位=价格敏感, 偏高端 \| 信号=high | 需要更强的价格框架、价值证明或预期管理。 回复链：Durability concern centers on zipper failure and seam strength. |
| 差评痛点 | Mine arrived fast but one tray corner was cracked. Seller refunded me without making me ship it back. | under-sink-organizer, compression-packing-cubes, pet-hair-remover-roller | 物流 / 包装顾虑 \| 重复提及=4 \| 回复压力=42 \| 价位=不明确 \| 信号=high | 把这句重复出现的话翻译成可执行的运营或信息规则。 回复链：回复链活跃（21 条回复），已经足够视为真实的购买前确认或异议处理信号。 |
| 购买因素 | I need to know if this is one of those dropship rollers because I saw the same thing on three different ads. | pet-hair-remover-roller, under-sink-organizer | 购买意向 \| 重复提及=3 \| 回复压力=47 \| 价位=不明确 \| 信号=high | 适合反哺 offer、FAQ 和转化角度设计。 回复链：Authenticity / dropship suspicion shows up in the reply chain. |
| 差评痛点 | Returned mine because the bin kept popping open, but customer service was quick. | pet-hair-remover-roller, under-sink-organizer, compression-packing-cubes | 退货 / 退款顾虑 \| 重复提及=3 \| 回复压力=32 \| 价位=不明确 \| 信号=high | 把这句重复出现的话翻译成可执行的运营或信息规则。 回复链：回复链活跃（12 条回复），已经足够视为真实的购买前确认或异议处理信号。 |
| 差评痛点 | I ordered it because the before and after on the couch looked real and not like a fake edit. | pet-hair-remover-roller | 真假 / 正品顾虑 \| 重复提及=1 \| 回复压力=17 \| 价位=不明确 \| 信号=high | 把这句重复出现的话翻译成可执行的运营或信息规则。 回复链：回复链活跃（17 条回复），已经足够视为真实的购买前确认或异议处理信号。 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| comment | product-a-thread-1 | paste-comment-source | comment-thread | Repeated buyer phrase from one product's comment thread. | Purchase-factor cluster |
| comment | product-b-thread-2 | paste-comment-source | comment-thread | Negative or complaint phrasing repeated across multiple 评论. | Complaint cluster |
| comment | product-c-reply-1 | paste-comment-source | reply-chain | Reply-chain pattern revealing trust or objection handling. | Trust-signal cluster |
| comment | hg-009 | https://www.tiktok.com/@petdailyfinds/video/7633000000000000002 | comment-thread | pet-hair-remover-roller: I ordered it because the before and after on the couch looked real and not like a fake edit. | Evidence cluster row: cleaned buyer-language theme |
| comment | hg-001 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: Bought this because my cleaning bottles were a mess and the pull-out shelf actually fits under a narrow sink. | Evidence cluster row: cleaned buyer-language theme |
| comment | hg-010 | https://www.tiktok.com/@petdailyfinds/video/7633000000000000002 | comment-thread | pet-hair-remover-roller: Does it work on cat hair and human hair or just the fluffy dog kind? | Evidence cluster row: cleaned buyer-language theme |
| comment | hg-002 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: Please tell me if the measurements are real because half of these organizers never fit around the pipe. | Evidence cluster row: cleaned buyer-language theme |

## 建议动作

_把用户语言转成下一步决策。_

| 决策领域 | 建议 | 原因 | 基础价值 / 改进机会 |
| --- | --- | --- | --- |
| 购买因素 | 先围绕最强购买触发点写卖点与证明，不要先写品牌自夸。 | 价格 / 性价比顾虑: I need to know if the zipper breaks after two trips because that always happens with ch… | 品类基础价值 |
| 好评关键词 | 把重复出现的正向原话翻成标题、口播和评论区 FAQ 的基础词库。 | 一般反应: Please tell me if the measurements are real because half of these organizers never fit… | 品类基础价值 |
| 差评痛点 | 把物流、包装、真假、退货、尺寸或 before-after 证据不足单独前置，不要藏到后面。 | 物流 / 包装顾虑: Mine arrived fast but one tray corner was cracked. Seller refunded me without making me… | 改进机会 |
| 价位差异 | 不同价位段需要不同的价值证明和风险安抚，不要用一套脚本打全部价格带。 | 当前价格带分层仍偏弱，需要继续补样本。 | 改进机会 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| comment | hg-019 | https://www.tiktok.com/@travelpackessentials/video/7633000000000000003 | comment-thread | compression-packing-cubes: I need to know if the zipper breaks after two trips because that always happens with cheap sets. | Recommended action: purchase-factor copy and proof |
| comment | hg-003 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: Mine arrived fast but one tray corner was cracked. Seller refunded me without making me ship it back. | Recommended action: complaint preemption |
| comment | hg-002 | https://www.tiktok.com/@homeorganizerlab/video/7633000000000000001 | comment-thread | under-sink-organizer: Please tell me if the measurements are real because half of these organizers never fit around the pipe. | Recommended action: reply-chain handling |

## 待确认问题

_列出缺失证据或薄弱结论。_

- 当前采样评论只覆盖了部分来源视频，所以这些结论更适合作为方向判断，而不是完整品类定论。
- 回复链结论目前主要来自导出的回复数量与摘要，不是完整的原始 threaded reply 全量抓取。
- 当前最值得追加全量抓取的回复链主题：一般反应。

### 价格带差异

| 价格带 | 重复驱动因素 | 重复抱怨 | 启发 |
| --- | --- | --- | --- |
| 价格敏感 | 价格 / 性价比顾虑 | 未恢复出明确的重复抱怨 | 需要更轻的承诺语言、更强的价值证明或更简单的预期管理。 |
| 偏高端 | 价格 / 性价比顾虑 | 未恢复出明确的重复抱怨 | 需要更强的信任转移、差异化收益或高端证明语言。 |
| 不明确 | 购买意向 | 物流 / 包装顾虑 | 当前样本更偏一般反应，价格分层还不够清晰。 |

### 证据总表

| 来源类型 | 来源标识 | 来源链接 | 时间范围 | 摘录 | 支撑结论 |
| --- | --- | --- | --- | --- | --- |
| comment | hg-009 | https://www.tiktok.com/@petdailyfinds/video/7633000000000000002 | comment-thread | pet-hair-remover-roller: Cleaned comment count in current pack: 24 | Open question: sampling coverage still partial across source videos |

## 资产清单

- [library] content_graph.json: file `captures/scene08-multi-product-home-goods-comments/content_graph.json` | Reusable 采集包 artifact

## 备注

- I ordered it because the before and after on the couch looked real and not like a fake edit.
- Bought this because my cleaning bottles were a mess and the pull-out shelf actually fits under a narrow sink.
- Does it work on cat hair and human hair or just the fluffy dog kind?
- Please tell me if the measurements are real because half of these organizers never fit around the pipe.
- Bought these because I only travel carry-on and the zip compression looked easier than vacuum bags.
- I need to know if this is one of those dropship rollers because I saw the same thing on three different ads.
- 一般反应 | 回复压力=134 | Please tell me if the measurements are real because half of these organizers never fit arou…

## 来源

- summary.json
- ranked_videos.json
