from __future__ import annotations

import re
from datetime import datetime

from text_normalization import normalize_text

MARKET_LABELS_ZH = {
    "US": "美国",
    "UK": "英国",
    "SG": "新加坡",
    "MY": "马来西亚",
    "ID": "印度尼西亚",
    "PH": "菲律宾",
    "TH": "泰国",
    "VN": "越南",
    "JP": "日本",
    "KR": "韩国",
    "DE": "德国",
    "FR": "法国",
    "IT": "意大利",
    "ES": "西班牙",
    "BR": "巴西",
    "MX": "墨西哥",
    "CA": "加拿大",
    "AU": "澳大利亚",
}


SCENE_FEISHU_LABELS_ZH = {
    "01": "爆款视频采集",
    "02": "日常巡检",
    "03": "批量爆款深拆",
    "04": "单视频拆解",
    "05": "反推提示词与制作简报",
    "06": "TikTok Shop 机会评估",
    "07": "类目市场判断",
    "08": "评论挖掘与人群画像",
    "09": "对标视频复刻制作简报",
    "10": "产品图转视频制作简报",
    "11": "热点视频复制流水线",
    "12": "单品多风格测试矩阵",
    "13": "多市场本地化包",
    "14": "上新素材家族蓝图",
    "15": "图片文案翻译与本地化蓝图",
    "16": "主图竞品基准蓝图",
    "17": "创作者公式提炼",
    "18": "竞品账号周报",
    "19": "自家账号复盘优化",
}

WEEKLY_SCENES = {"18", "19"}

MODE_LABELS_ZH = {
    "summary": "摘要",
    "section_overview": "章节概览",
    "evidence": "证据",
    "assets": "资产",
}

FIELD_LABELS_ZH = {
    "Scene": "场景",
    "Scene Title": "场景标题",
    "Project": "项目",
    "Deliverable Type": "交付物类型",
    "Generated At": "生成时间",
    "Status": "状态",
    "Conclusion": "核心结论",
    "Why It Matters": "为什么重要",
    "Next Action": "下一步动作",
    "Confidence": "置信度",
    "Working Context": "工作上下文",
    "Section Count": "章节数",
    "Evidence Count": "证据数",
    "Asset Count": "资产数",
    "Source Count": "来源数",
    "Order": "序号",
    "Section": "章节",
    "Instruction": "填写说明",
    "Paragraph Count": "段落数",
    "Bullet Count": "要点数",
    "Step Count": "步骤数",
    "Table Title": "表格标题",
    "Table Columns": "表格列",
    "Label": "标签",
    "Detail": "详情",
    "Source": "来源",
    "Path": "路径",
    "Note": "备注",
}

PROJECT_TEXT_REPLACEMENTS = [
    ("Scene04 Single Video Breakdown", "场景 04 单视频拆解"),
    ("Scene05 Validation Capture", "场景 05 校验样例"),
    ("Scene08 Commerce Comment Check", "场景 08 商品评论成品质检"),
    ("Scene18 Weekly Competitor Review", "场景 18 竞品账号周报"),
    ("Scene19 Account Retro Review", "场景 19 自家账号复盘"),
    ("Scene 01 Spot Check", "场景 01 成品质检"),
    ("TikTok Validation", "TikTok 校验"),
    ("Feishu Batch Smoke", "飞书批量冒烟"),
    ("Competitor Account Weekly Review", "竞品账号周报"),
    ("Self Account Retro And Optimization", "自家账号复盘优化"),
    ("Self Account Retro", "自家账号复盘"),
    ("Single Video Teardown", "单视频拆解"),
    ("Single Video", "单视频"),
    ("Capture Rich", "富导出采集"),
    ("Rich", "富导出"),
    ("Capture", "采集"),
    ("Spotcheck", "质检"),
    ("Validation", "校验"),
]

SPOTCHECK_PROJECT_RE = re.compile(r"^(?:Spotcheck Scene|Scene) (\d{2}) Spot Check(?:\s+V(\d+))?\b", re.IGNORECASE)
VALIDATION_PROJECT_RE = re.compile(r"^(?:TikTok )?Validation Scene (\d{2})\b", re.IGNORECASE)
FEISHU_BATCH_SMOKE_RE = re.compile(r"^Feishu Batch Smoke - ([^-]+?) - (.+)$")
SCENE_REPORT_PREFIX_RE = re.compile(r"^Scene (\d{2}) Report - (.+)$", re.IGNORECASE)


def normalize_scene_id(value: object) -> str:
    text = normalize_text(value)
    if not text:
        return ""
    digits = "".join(ch for ch in text if ch.isdigit())
    if digits:
        return digits.zfill(2)
    return text


def scene_label_zh(scene_id: object) -> str:
    normalized = normalize_scene_id(scene_id)
    if not normalized:
        return "TikTok 增长运营报告"
    return SCENE_FEISHU_LABELS_ZH.get(normalized, f"场景 {normalized}")


def build_period(scene_id: object) -> str:
    normalized = normalize_scene_id(scene_id)
    now = datetime.now()
    if normalized in WEEKLY_SCENES:
        iso_year, iso_week, _ = now.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return now.strftime("%Y-%m-%d")


def localize_project_text(project: object) -> str:
    raw_text = normalize_text(project)
    if not raw_text:
        return ""
    scene_report_match = SCENE_REPORT_PREFIX_RE.match(raw_text)
    if scene_report_match:
        scene_id = scene_report_match.group(1)
        remainder = normalize_text(scene_report_match.group(2))
        localized_remainder = localize_project_text(remainder) if remainder else ""
        if localized_remainder and localized_remainder != remainder:
            return localized_remainder
        if remainder:
            return f"场景 {scene_id} 报告 - {localized_remainder or remainder}"
        return f"场景 {scene_id} 报告"
    spotcheck_match = SPOTCHECK_PROJECT_RE.match(raw_text)
    if spotcheck_match:
        scene_id = spotcheck_match.group(1)
        version = normalize_text(spotcheck_match.group(2))
        if version:
            return f"场景 {scene_id} 成品质检 V{version}"
        return f"场景 {scene_id} 成品质检"
    validation_match = VALIDATION_PROJECT_RE.match(raw_text)
    if validation_match:
        return f"场景 {validation_match.group(1)} 校验样例"
    smoke_match = FEISHU_BATCH_SMOKE_RE.match(raw_text)
    if smoke_match:
        account = normalize_text(smoke_match.group(1))
        lane = normalize_text(smoke_match.group(2))
        if "Competitor Account Weekly Review" in lane:
            return f"{account} 竞品账号周报冒烟"
        if "Self Account Retro" in lane:
            return f"{account} 自家账号复盘冒烟"
        return f"{account} 批量冒烟" if account else "批量冒烟"
    text = raw_text
    for source, target in PROJECT_TEXT_REPLACEMENTS:
        text = text.replace(source, target)
    text = re.sub(r"\bScene (\d{2})\b", r"场景 \1", text)
    text = re.sub(r"\bScene (\d)\b", lambda match: f"场景 {int(match.group(1)):02d}", text)
    text = re.sub(r"\s+-\s+", " - ", text)
    return text


def should_skip_scene_text(project_text: str, scene_text: str, scene_id: str) -> bool:
    if not project_text or not scene_text:
        return False
    if scene_text in project_text:
        return True
    if scene_id == "19" and "自家账号复盘" in project_text:
        return True
    if scene_id == "18" and "竞品账号周报" in project_text:
        return True
    if "场景" in project_text and "成品质检" in project_text:
        return True
    if "场景" in project_text and "校验样例" in project_text:
        return True
    return False


def build_report_title(project: object, scene_id: object, scene_title: object) -> str:
    project_text = localize_project_text(project)
    normalized_scene = normalize_scene_id(scene_id)
    del scene_title
    scene_text = scene_label_zh(normalized_scene)
    scene_part = f"场景 {normalized_scene}" if normalized_scene else ""
    if project_text and scene_part and scene_part in project_text:
        scene_part = ""
    if project_text and "冒烟" in project_text:
        scene_part = ""
    if should_skip_scene_text(project_text, scene_text, normalized_scene):
        scene_text = ""
    parts = [part for part in [project_text, scene_part, scene_text] if part]
    return " - ".join(parts)[:120] or "TikTok 增长运营报告"


def build_task_title(task: dict) -> str:
    scene_id = normalize_scene_id(task.get("scene"))
    label = scene_label_zh(scene_id)
    project = localize_project_text(task.get("project"))
    market_raw = normalize_text(task.get("market"))
    market = MARKET_LABELS_ZH.get(market_raw.upper(), market_raw)
    period = build_period(scene_id)
    parts = [label]
    if project:
        parts.append(project)
    if market:
        parts.append(market)
    parts.append(period)
    return " | ".join(part for part in parts if part)


def mode_label_zh(mode: object) -> str:
    normalized = normalize_text(mode)
    return MODE_LABELS_ZH.get(normalized, normalized or "摘要")


def translate_field_name(name: object) -> str:
    normalized = normalize_text(name)
    return FIELD_LABELS_ZH.get(normalized, normalized)


def build_table_name(scene_id: object, scene_title: object, mode: object) -> str:
    normalized_scene = normalize_scene_id(scene_id)
    title = scene_label_zh(normalized_scene) if normalized_scene else normalize_text(scene_title)
    title = title or "场景报告"
    return f"{title} - {mode_label_zh(mode)}"
