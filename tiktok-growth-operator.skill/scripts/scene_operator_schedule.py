from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from text_normalization import normalize_text, write_json_file


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def _next_weekday_iso(weekday: int) -> str:
    today = datetime.now().date()
    delta = (weekday - today.weekday()) % 7
    if delta == 0:
        delta = 7
    return (today + timedelta(days=delta)).isoformat()


def schedule_dispatch_rows(schedule: dict) -> list[list[str]]:
    rows: list[list[str]] = []
    for item in schedule.get("dispatch") or []:
        if not isinstance(item, dict):
            continue
        rows.append(
            [
                normalize_text(item.get("when")) or "today",
                normalize_text(item.get("action")) or "",
                normalize_text(item.get("owner")) or "operator",
                normalize_text(item.get("channel")) or "local",
            ]
        )
    return rows


def build_operator_schedule(scene_id: str, **context: Any) -> dict[str, Any]:
    scene = normalize_text(scene_id).lstrip("0") or scene_id
    capture_root = context.get("capture_root")
    append_scope = normalize_text(context.get("append_scope")) or _today()
    category = normalize_text(context.get("category")) or "category"
    market = normalize_text(context.get("market")) or "US"
    cadence = normalize_text(context.get("cadence")) or "daily"
    verdict = normalize_text(context.get("verdict"))
    compare_mode = normalize_text(context.get("compare_mode"))
    latest_week = normalize_text(context.get("latest_week"))
    alert_count = int(context.get("alert_count") or 0)
    shortlist_count = int(context.get("shortlist_count") or 0)
    board_rows = int(context.get("board_row_count") or 0)

    feishu_table_key = {
        "1": "scene01_collection_board",
        "2": "scene02_patrol_board",
        "7": "scene07_category_entry",
        "6": "scene06_competitor_product_board",
        "8": "scene08_comment_persona",
        "17": "scene17_creator_formula",
        "18": "scene18_competitor_weekly",
        "19": "scene19_account_retro",
    }.get(scene, f"scene{scene}_report")

    delivery = {
        "local_bundle": True,
        "feishu": {
            "status": "planned",
            "table_key": feishu_table_key,
            "append_mode": "append_by_run_date",
            "run_date_field": "采集日期",
            "append_scope_field": "追加批次",
            "append_scope": append_scope,
        },
        "channels": ["local", "feishu"],
        "notify_when_done": True,
    }

    dispatch: list[dict[str, str]] = []
    next_runs: list[dict[str, str]] = []

    if scene == "1":
        dispatch = [
            {"when": "today", "action": "把 collection_board.xlsx 追加进飞书主表，并标记 Top3 交接 Scene 03", "owner": "operator", "channel": "feishu"},
            {"when": "today", "action": f"对 P1–P3 候选各跑一条 Scene 03 深拆（共 {min(shortlist_count, 3) or 3} 条）", "owner": "analyst", "channel": "local"},
            {"when": "tomorrow", "action": "用同一搜索配置复采，比较 shortlist 是否漂移", "owner": "collector", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "daily", "suggested_cron": "0 9 * * *", "run_command": "python scripts/run_operator_workflow.py --mode capture-pack --scene 01 --push-feishu"},
        ]
    elif scene == "2":
        dispatch = [
            {"when": "today", "action": f"发送日报摘要（新增/上升/异常；告警 {alert_count} 条）", "owner": "operator", "channel": "feishu"},
            {"when": "today", "action": "仅把 scene03_candidates 前 3 条送进 Scene 03，不全量重拆", "owner": "analyst", "channel": "local"},
            {"when": "tomorrow", "action": f"同表追加巡检：{category} / {market} / {cadence}", "owner": "collector", "channel": "feishu"},
        ]
        next_runs = [
            {
                "cadence": cadence,
                "suggested_cron": "0 9 * * *",
                "run_command": "python scripts/run_scene0203.py --source patrol-loop",
            },
        ]
    elif scene == "3":
        dispatch = [
            {"when": "today", "action": "完成 TOP 深拆后，把共性规律表交给 Scene 09 或 11", "owner": "creative", "channel": "local"},
            {"when": "this_week", "action": "用 creation_matrix 做 1 轮脚本试写，不直接全量生成", "owner": "creative", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "on_demand", "suggested_cron": "", "run_command": "python scripts/run_scene0203.py --also-run-scene03"},
        ]
    elif scene == "4":
        dispatch = [
            {"when": "today", "action": "按分镜表补关键帧或下载源，再交给 Scene 05 反推", "owner": "editor", "channel": "local"},
            {"when": "this_week", "action": "用 production_spec_handoff.json 试一条 Sora/Veo 分支草稿", "owner": "creative", "channel": "local"},
        ]
        next_runs = [{"cadence": "on_demand", "suggested_cron": "", "run_command": "python scripts/start_capture_pack_run.py --scene 04"}]
    elif scene == "5":
        dispatch = [
            {"when": "today", "action": "选定 generator 分支（Sora / Veo / i2v）并填 adapt 字段", "owner": "creative", "channel": "local"},
            {"when": "this_week", "action": "提交 1 条生成任务并记录 job_id（需 GENERATION_RENDERER_URL）", "owner": "producer", "channel": "local"},
        ]
        next_runs = [{"cadence": "on_demand", "suggested_cron": "", "run_command": "python scripts/start_capture_pack_run.py --scene 05"}]
    elif scene == "6":
        dispatch = [
            {"when": "today", "action": "把 competitor_product_board 异动行追加进主表并标红待补字段", "owner": "operator", "channel": "feishu"},
            {"when": "today", "action": "对降价/评分下滑 SKU 各拉 1 份评论样本解释原因", "owner": "analyst", "channel": "local"},
            {"when": "this_week", "action": "锁定 3–10 个核心竞品 SKU 做下一轮同字段复采", "owner": "collector", "channel": "local"},
        ]
        next_runs = [
            {
                "cadence": "weekly",
                "suggested_cron": "0 10 * * 2",
                "run_command": "python scripts/start_capture_pack_run.py --scene 06",
            },
        ]
    elif scene == "7":
        dispatch = [
            {"when": "today", "action": f"类目进入判断：{verdict or '见报告'} — 同步给选品/内容负责人", "owner": "lead", "channel": "feishu"},
            {"when": "this_week", "action": "若判为「有空间」，开 3 条小流量验证；若「热但拥挤」只测差异化 proof", "owner": "operator", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "weekly", "suggested_cron": "0 10 * * 1", "run_command": "python scripts/start_capture_pack_run.py --scene 07"},
        ]
    elif scene == "8":
        dispatch = [
            {"when": "today", "action": "把四块评论洞察写入 FAQ / 卖点 / 差评回应话术", "owner": "copy", "channel": "feishu"},
            {"when": "this_week", "action": "补采评论不足的 SKU，并保留 source_product 标签", "owner": "collector", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "biweekly", "suggested_cron": "0 11 * * 3", "run_command": "python scripts/start_capture_pack_run.py --scene 08"},
        ]
    elif scene == "17":
        dispatch = [
            {"when": "today", "action": "从公式库挑 1 条钩子模板写新脚本草案", "owner": "creative", "channel": "local"},
            {"when": "this_week", "action": "对同一创作者再采 1 周帖子，验证公式是否稳定", "owner": "collector", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "monthly", "suggested_cron": "0 10 1 * *", "run_command": "python scripts/start_capture_pack_run.py --scene 17"},
        ]
    elif scene == "18":
        week_note = f"{latest_week} vs 上周" if compare_mode == "compare" else f"基线周 {latest_week or '当前'}"
        dispatch = [
            {"when": "today", "action": f"发送竞品周报调度单（{week_note}）", "owner": "operator", "channel": "feishu"},
            {"when": "this_week", "action": "对「继续追 / 借鉴 / 忽略」各执行 1 个动作", "owner": "content", "channel": "local"},
            {"when": _next_weekday_iso(0), "action": "同字段复采 3–5 个竞品账号", "owner": "collector", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "weekly", "suggested_cron": "0 9 * * 1", "run_command": "python scripts/run_scene1819.py --preset multiweek --scene18-only"},
        ]
    elif scene == "19":
        dispatch = [
            {"when": "today", "action": "按「多做/少做/停止」表调整下周排期", "owner": "operator", "channel": "feishu"},
            {"when": "this_week", "action": "执行 Open Questions 里的 2 条 A/B 测试", "owner": "content", "channel": "local"},
            {"when": _next_weekday_iso(0), "action": "同字段复采自有账号并跑 Scene 19 周对比", "owner": "collector", "channel": "local"},
        ]
        next_runs = [
            {"cadence": "weekly", "suggested_cron": "0 10 * * 1", "run_command": "python scripts/run_scene1819.py --preset multiweek"},
        ]

    schedule = {
        "schema_version": "operator-schedule-v1",
        "scene": scene,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "append_scope": append_scope,
        "delivery": delivery,
        "dispatch": dispatch,
        "next_runs": next_runs,
        "context": {key: value for key, value in context.items() if key != "capture_root" and value not in (None, "")},
    }
    if board_rows:
        schedule["board_row_count"] = board_rows
    return schedule


def apply_operator_schedule(
    payload: dict,
    scene_id: str,
    *,
    section_heading: str = "Next Action",
    capture_root: Path | None = None,
    **context: Any,
) -> dict[str, Any]:
    schedule = build_operator_schedule(scene_id, capture_root=capture_root, **context)
    payload["operator_schedule"] = schedule

    sections = {sec.get("heading"): sec for sec in payload.get("sections", []) if isinstance(sec, dict)}
    section = sections.get(section_heading) or sections.get("Recommended Action") or {}
    dispatch_rows = schedule_dispatch_rows(schedule)
    if dispatch_rows:
        existing = (section.get("table") or {}).get("rows") or []
        section.setdefault("table", {})
        section["table"]["title"] = normalize_text(section["table"].get("title")) or "运营调度 / 推送计划"
        headers = section["table"].get("headers")
        if not headers or len(headers) < 4:
            section["table"]["headers"] = ["时间", "动作", "负责人", "渠道"]
        section["table"]["rows"] = dispatch_rows + list(existing)

    bullets = list(section.get("bullets") or [])
    for run in schedule.get("next_runs") or []:
        cmd = normalize_text(run.get("run_command"))
        if cmd:
            bullets.append(f"建议定时：{normalize_text(run.get('cadence'))} | {cmd}")
    feishu = (schedule.get("delivery") or {}).get("feishu") or {}
    if feishu.get("status") == "planned":
        bullets.append(
            f"飞书追加：表 `{feishu.get('table_key')}` | 批次 `{feishu.get('append_scope')}` | 模式 `{feishu.get('append_mode')}`"
        )
    section["bullets"] = list(dict.fromkeys(bullets))

    if capture_root is not None:
        path = Path(capture_root) / f"operator_schedule_scene_{normalize_text(scene_id).lstrip('0') or scene_id}.json"
        write_json_file(path, schedule)
        assets = payload.setdefault("assets", [])
        assets.append(
            {
                "label": f"Scene {scene_id} operator schedule",
                "path": str(path),
                "note": "推送/定时调度真源，可对接 deliver_operator_run --adapter feishu",
            }
        )
    return schedule


def scene17_series_cluster_rows(videos: list[dict]) -> list[list[str]]:
    from collections import Counter

    from import_tiktok_capture_pack import teardown_lane_label

    lanes = Counter(teardown_lane_label(video) for video in videos if isinstance(video, dict))
    rows: list[list[str]] = []
    for lane, count in lanes.most_common(4):
        sample = next((video for video in videos if teardown_lane_label(video) == lane), {})
        from pack_video_text import hook_text as _hook_text

        rows.append(
            [
                lane or "未分类",
                str(count),
                _hook_text(sample)[:72] if sample else "—",
                "优先蒸馏" if count >= 2 else "观察",
            ]
        )
    return rows or [["未分类", "0", "样本不足", "先补创作者样本"]]


def scene08_positioning_bridge_rows(comment_snapshot: dict) -> list[list[str]]:
    purchase = comment_snapshot.get("top_purchase_cluster") if isinstance(comment_snapshot, dict) else {}
    complaint = comment_snapshot.get("top_complaint_cluster") if isinstance(comment_snapshot, dict) else {}
    trust = comment_snapshot.get("top_trust_cluster") if isinstance(comment_snapshot, dict) else {}
    rows = [
        [
            "定位话术",
            normalize_text((purchase or {}).get("theme")) or "购买因素待补",
            "卖点 / 首屏承诺",
            normalize_text(((purchase or {}).get("top_entry") or {}).get("quote_text"))[:80],
        ],
        [
            "异议处理",
            normalize_text((complaint or {}).get("theme")) or "差评痛点待补",
            "FAQ / 客服 / 评论区",
            normalize_text(((complaint or {}).get("top_entry") or {}).get("quote_text"))[:80],
        ],
        [
            "信任背书",
            normalize_text((trust or {}).get("theme")) or "好评关键词待补",
            "证明段 / 对比镜头",
            normalize_text(((trust or {}).get("top_entry") or {}).get("quote_text"))[:80],
        ],
    ]
    return rows


def scene03_downstream_handoff_rows(top_videos: list[dict]) -> list[list[str]]:
    rows: list[list[str]] = []
    if not top_videos:
        return [["Scene 09", "无 shortlist", "先完成 Scene 01/02 采集", "blocked"]]
    winner = top_videos[0]
    rows.append(
        [
            "Scene 09",
            "参考视频复刻简报",
            normalize_text(winner.get("video_url")) or "top-1",
            "用 shortlist 第 1 条做 replication brief",
        ]
    )
    if len(top_videos) > 1:
        rows.append(
            [
                "Scene 11",
                "爆款复刻流水线",
                normalize_text(top_videos[1].get("video_url")) or "top-2",
                "用第 2 条做对照变体，避免只押一条",
            ]
        )
    rows.append(
        [
            "Scene 04/05",
            "单条拆解 / 反推",
            normalize_text(winner.get("video_url")) or "top-1",
            "深拆后再反推 generator schema",
        ]
    )
    return rows


def scene05_generator_branch_rows(generator_pack: dict) -> list[list[str]]:
    branches = (generator_pack or {}).get("generator_branches") or {}
    rows: list[list[str]] = []
    for name in ("sora", "veo", "i2v"):
        branch = branches.get(name) or {}
        rows.append(
            [
                name,
                normalize_text(branch.get("use_when")) or f"适合 {name} 工作流",
                normalize_text(branch.get("prompt_focus")) or "见 production_spec_handoff.json",
                "ready" if branch else "需补 handoff JSON",
            ]
        )
    return rows
