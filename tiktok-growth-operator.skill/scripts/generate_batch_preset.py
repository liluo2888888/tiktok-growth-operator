from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from feishu_naming import build_task_title, normalize_scene_id, scene_label_zh
from text_normalization import read_json_file, write_json_file, write_utf8_text


PRESETS = {
    "topic-to-publish": {
        "label": "Topic To Publish",
        "description": "Generate one goal-mode queue for topic selection through publish handoff.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["product", "category"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want a Douyin workflow for {product} in {category} from topic selection to creative testing to publish handoff",
                "name_suffix": "{product_slug}-topic-to-publish",
                "project_suffix": "{product} - Topic To Publish Workflow",
                "path_suffix": "goal-topic-to-publish",
            }
        ],
    },
    "viral-to-testing": {
        "label": "Viral To Testing",
        "description": "Generate one goal-mode queue from viral teardown into a reusable testing workflow.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["product", "category"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want to turn viral teardown for {product} in {category} into a reusable creative testing workflow",
                "name_suffix": "{product_slug}-viral-to-testing",
                "project_suffix": "{product} - Viral To Testing Workflow",
                "path_suffix": "goal-viral-to-testing",
            }
        ],
    },
    "category-to-localized-launch": {
        "label": "Category To Localized Launch",
        "description": "Generate one goal-mode queue for category research, localization, and publish handoff.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["product", "category", "market"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want a multi-market workflow for {product} in {category} from category research to localized launch in {market}",
                "name_suffix": "{product_slug}-category-to-localized-launch",
                "project_suffix": "{product} - Category To Localized Launch Workflow",
                "path_suffix": "goal-category-to-localized-launch",
            }
        ],
    },
    "competitor-weekly-and-breakdown": {
        "label": "Competitor Weekly And Breakdown",
        "description": "Generate one goal-mode queue for weekly competitor monitoring and creator breakdown.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["category", "account_name"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want competitor weekly monitoring and creator breakdown for {account_name} in {category}",
                "name_suffix": "{account_slug}-competitor-weekly-and-breakdown",
                "project_suffix": "{account_name} - Competitor Weekly And Breakdown",
                "path_suffix": "goal-competitor-weekly-and-breakdown",
            }
        ],
    },
    "competitor-to-publish": {
        "label": "Competitor To Publish",
        "description": "Generate one goal-mode queue that turns competitor monitoring into publish-ready assets.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["product", "category"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want to monitor competitors for {product} in {category} and turn the findings into publish-ready test assets",
                "name_suffix": "{product_slug}-competitor-to-publish",
                "project_suffix": "{product} - Competitor To Publish Workflow",
                "path_suffix": "goal-competitor-to-publish",
            }
        ],
    },
    "audience-to-live": {
        "label": "Audience To Live",
        "description": "Generate one goal-mode queue from audience language mining into live-support prep.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["product", "audience"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want a workflow for {product} from comment mining to live-session moderator prompts for {audience}",
                "name_suffix": "{product_slug}-audience-to-live",
                "project_suffix": "{product} - Audience To Live Workflow",
                "path_suffix": "goal-audience-to-live",
            }
        ],
    },
    "weekly-monitor-to-next-test": {
        "label": "Weekly Monitor To Next Test",
        "description": "Generate one goal-mode queue from weekly monitoring into the next test cycle.",
        "platform": "Douyin",
        "market": "China",
        "variables": ["account_name", "category"],
        "tasks": [
            {
                "mode": "goal",
                "query": "I want to use weekly competitor review and account retro for {account_name} in {category} to define the next test cycle",
                "name_suffix": "{account_slug}-weekly-monitor-to-next-test",
                "project_suffix": "{account_name} - Weekly Monitor To Next Test Workflow",
                "path_suffix": "goal-weekly-monitor-to-next-test",
            }
        ],
    },
    "tiktok-ranked-breakdown-capture": {
        "label": "TikTok Ranked Breakdown Capture",
        "description": "Generate one capture-pack queue for ranked-video teardown plus creator distillation.",
        "platform": "TikTok",
        "market": "US",
        "requires": ["capture_root"],
        "variables": ["account_name", "category"],
        "tasks": [
            {
                "mode": "capture-pack",
                "scene": "03",
                "capture_root_ref": "capture_root",
                "name_suffix": "{account_slug}-ranked-breakdown",
                "project_suffix": "{account_name} - Ranked Breakdown",
                "path_suffix": "capture-scene-03-ranked-breakdown",
            },
            {
                "mode": "capture-pack",
                "scene": "17",
                "capture_root_ref": "capture_root",
                "name_suffix": "{account_slug}-creator-distillation",
                "project_suffix": "{account_name} - Creator Distillation",
                "path_suffix": "capture-scene-17-creator-distillation",
            },
        ],
    },
    "tiktok-comment-live-capture": {
        "label": "TikTok Comment Live Capture",
        "description": "Generate one capture-pack queue for comment mining into live-assist prep.",
        "platform": "TikTok",
        "market": "US",
        "requires": ["capture_root"],
        "variables": ["product", "audience"],
        "tasks": [
            {
                "mode": "capture-pack",
                "scene": "08",
                "capture_root_ref": "capture_root",
                "name_suffix": "{product_slug}-comment-live",
                "project_suffix": "{product} - Comment Signal To Live Assist",
                "path_suffix": "capture-scene-08-comment-live",
            }
        ],
    },
    "tiktok-account-watch-capture": {
        "label": "TikTok Account Watch Capture",
        "description": "Generate one capture-pack queue for account weekly review plus self-account retro.",
        "platform": "TikTok",
        "market": "US",
        "requires": ["capture_root"],
        "variables": ["account_name", "category"],
        "tasks": [
            {
                "mode": "capture-pack",
                "scene": "18",
                "capture_root_ref": "capture_root",
                "name_suffix": "{account_slug}-account-weekly",
                "project_suffix": "{account_name} - Competitor Account Weekly Review",
                "path_suffix": "capture-scene-18-account-weekly",
            },
            {
                "mode": "capture-pack",
                "scene": "19",
                "capture_root_ref": "capture_root",
                "name_suffix": "{account_slug}-account-retro",
                "project_suffix": "{account_name} - Self Account Retro",
                "path_suffix": "capture-scene-19-account-retro",
            },
        ],
    },
}

TEMPLATE_BUNDLES = {
    "topic-to-publish-board": {
        "label": "Topic To Publish Board",
        "description": "Combined planning board from topic selection through publish handoff plus live-session language support.",
        "presets": ["topic-to-publish", "audience-to-live"],
        "ordering": "mode",
    },
    "viral-testing-board": {
        "label": "Viral Testing Board",
        "description": "Combined board for viral teardown, ranked-capture evidence, and reusable testing follow-through.",
        "presets": ["viral-to-testing", "tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
    },
    "competitor-to-publish-board": {
        "label": "Competitor To Publish Board",
        "description": "Combined board for competitor-driven publish planning plus account-watch capture evidence.",
        "presets": ["competitor-to-publish", "tiktok-account-watch-capture"],
        "ordering": "mode",
    },
    "beauty-ops-board": {
        "label": "Beauty Ops Board",
        "description": "Combined operating board for competitor publish prep, audience live prep, and account-watch capture evidence.",
        "presets": ["competitor-to-publish", "audience-to-live", "tiktok-account-watch-capture"],
        "ordering": "mode",
    },
    "localized-launch-board": {
        "label": "Localized Launch Board",
        "description": "Combined board for localized launch planning plus ranked-breakdown capture evidence.",
        "presets": ["category-to-localized-launch", "tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
    },
    "weekly-monitor-to-next-test-board": {
        "label": "Weekly Monitor To Next Test Board",
        "description": "Combined board for weekly competitor review, next-test planning, and account-watch capture evidence.",
        "presets": ["competitor-weekly-and-breakdown", "weekly-monitor-to-next-test", "tiktok-account-watch-capture"],
        "ordering": "mode",
    },
}

VERTICAL_STARTERS = {
    "beauty-us-ops-starter": {
        "label": "Beauty US Ops Starter",
        "description": "Business-ready TikTok beauty operator board seeded for competitor-to-publish, audience-to-live, and account-watch capture work.",
        "presets": ["competitor-to-publish", "audience-to-live", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "beauty-us-ops-starter",
            "project": "Beauty US Ops Starter",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "beauty-comment-live-starter": {
        "label": "Beauty Comment Live Starter",
        "description": "Seeded TikTok beauty starter for comment-signal mining into live-room operator prep.",
        "presets": ["audience-to-live", "tiktok-comment-live-capture"],
        "ordering": "mode",
        "seed": {
            "name": "beauty-comment-live-starter",
            "project": "Beauty Comment Live Starter",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-download-validated-20260423",
        },
    },
    "douyin-beauty-launch-starter": {
        "label": "Douyin Beauty Launch Starter",
        "description": "Seeded Douyin beauty starter for topic selection, testing, and localized launch planning.",
        "presets": ["topic-to-publish", "category-to-localized-launch"],
        "ordering": "stage",
        "seed": {
            "name": "douyin-beauty-launch-starter",
            "project": "Douyin Beauty Launch Starter",
            "platform": "Douyin",
            "market": "China",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
        },
    },
    "tiktok-ranked-creator-starter": {
        "label": "TikTok Ranked Creator Starter",
        "description": "Seeded TikTok starter for ranked teardown and creator distillation from a real local capture pack.",
        "presets": ["tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
        "seed": {
            "name": "tiktok-ranked-creator-starter",
            "project": "TikTok Ranked Creator Starter",
            "platform": "TikTok",
            "market": "US",
            "account_name": "GlowOfficial",
            "category": "Beauty",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "douyin-competitor-weekly-starter": {
        "label": "Douyin Competitor Weekly Starter",
        "description": "Seeded Douyin starter for weekly competitor review and next-test planning.",
        "presets": ["competitor-weekly-and-breakdown", "weekly-monitor-to-next-test"],
        "ordering": "mode",
        "seed": {
            "name": "douyin-competitor-weekly-starter",
            "project": "Douyin Competitor Weekly Starter",
            "platform": "Douyin",
            "market": "China",
            "account_name": "Anxiansheng Official",
            "category": "Health",
        },
    },
}

LAUNCH_BOARDS = {
    "publish-week-board": {
        "label": "Publish Week Board",
        "description": "Objective-first board for one publish week: competitor insight, publish prep direction, and live-language follow-through.",
        "presets": ["competitor-to-publish", "audience-to-live", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "publish-week-board",
            "project": "Publish Week Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "comment-to-live-board": {
        "label": "Comment To Live Board",
        "description": "Objective-first board for turning comment evidence into live-room prompts, escalation logic, and response themes.",
        "presets": ["audience-to-live", "tiktok-comment-live-capture"],
        "ordering": "mode",
        "seed": {
            "name": "comment-to-live-board",
            "project": "Comment To Live Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-download-validated-20260423",
        },
    },
    "competitor-review-board": {
        "label": "Competitor Review Board",
        "description": "Objective-first board for weekly competitor review, creator breakdown, and next-test planning.",
        "presets": ["competitor-weekly-and-breakdown", "weekly-monitor-to-next-test", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "competitor-review-board",
            "project": "Competitor Review Board",
            "platform": "TikTok",
            "market": "US",
            "account_name": "GlowOfficial",
            "category": "Beauty",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "localization-sprint-board": {
        "label": "Localization Sprint Board",
        "description": "Objective-first board for category entry, ranked evidence review, and localized launch planning.",
        "presets": ["category-to-localized-launch", "tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
        "seed": {
            "name": "localization-sprint-board",
            "project": "Localization Sprint Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "viral-testing-sprint-board": {
        "label": "Viral Testing Sprint Board",
        "description": "Objective-first board for ranked teardown, viral testing translation, and immediate experiment setup.",
        "presets": ["viral-to-testing", "tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
        "seed": {
            "name": "viral-testing-sprint-board",
            "project": "Viral Testing Sprint Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
}

MANAGER_BOARDS = {
    "content-operator-board": {
        "label": "Content Operator Board",
        "description": "Role-first board for content operators who need publish direction, ranked references, and rapid testing setup.",
        "presets": ["competitor-to-publish", "viral-to-testing", "tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
        "seed": {
            "name": "content-operator-board",
            "project": "Content Operator Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "live-operator-board": {
        "label": "Live Operator Board",
        "description": "Role-first board for live operators who need comment mining, moderator prompts, and account-watch context.",
        "presets": ["audience-to-live", "tiktok-comment-live-capture", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "live-operator-board",
            "project": "Live Operator Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-download-validated-20260423",
        },
    },
    "strategy-operator-board": {
        "label": "Strategy Operator Board",
        "description": "Role-first board for strategy operators who need weekly review, creator distillation, and next-test planning.",
        "presets": ["competitor-weekly-and-breakdown", "weekly-monitor-to-next-test", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "strategy-operator-board",
            "project": "Strategy Operator Board",
            "platform": "TikTok",
            "market": "US",
            "account_name": "GlowOfficial",
            "category": "Beauty",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "growth-operator-board": {
        "label": "Growth Operator Board",
        "description": "Role-first board for end-to-end growth operators combining publish planning, live-language mining, and retrospective review.",
        "presets": ["competitor-to-publish", "audience-to-live", "weekly-monitor-to-next-test", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "growth-operator-board",
            "project": "Growth Operator Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
}

CADENCE_BOARDS = {
    "daily-ops-board": {
        "label": "Daily Ops Board",
        "description": "Cadence-first board for daily operator loops covering publish direction, audience signal intake, and ranked reference tracking.",
        "presets": ["competitor-to-publish", "audience-to-live", "tiktok-ranked-breakdown-capture"],
        "ordering": "mode",
        "seed": {
            "name": "daily-ops-board",
            "project": "Daily Ops Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "weekly-ops-board": {
        "label": "Weekly Ops Board",
        "description": "Cadence-first board for weekly review, creator distillation, account retro, and next-test planning.",
        "presets": ["competitor-weekly-and-breakdown", "weekly-monitor-to-next-test", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "weekly-ops-board",
            "project": "Weekly Ops Board",
            "platform": "TikTok",
            "market": "US",
            "account_name": "GlowOfficial",
            "category": "Beauty",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "launch-sprint-board": {
        "label": "Launch Sprint Board",
        "description": "Cadence-first board for a short launch sprint combining localized launch planning and publish-week execution context.",
        "presets": ["category-to-localized-launch", "competitor-to-publish", "tiktok-ranked-breakdown-capture"],
        "ordering": "stage",
        "seed": {
            "name": "launch-sprint-board",
            "project": "Launch Sprint Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-analysis-pack-smoke-20260423f",
        },
    },
    "live-shift-board": {
        "label": "Live Shift Board",
        "description": "Cadence-first board for one live-session shift covering comment evidence, moderator prompts, and escalation support.",
        "presets": ["audience-to-live", "tiktok-comment-live-capture", "tiktok-account-watch-capture"],
        "ordering": "mode",
        "seed": {
            "name": "live-shift-board",
            "project": "Live Shift Board",
            "platform": "TikTok",
            "market": "US",
            "product": "Velvet Lip Glaze",
            "category": "Beauty",
            "audience": "Skincare Deal Seekers",
            "account_name": "GlowOfficial",
            "capture_root": "D:\\我的文档\\Documents\\Playground 4\\captures\\tiktok-download-validated-20260423",
        },
    },
}

MODE_ORDER = {
    "goal": 1,
    "scene": 2,
    "pack": 3,
    "capture-pack": 4,
}

STAGE_ORDER = {
    "goal": 1,
    "scene": 2,
    "pack": 3,
    "capture-pack": 4,
}

FEISHU_WEEKLY_SCENES = {"18", "19"}
FEISHU_DATE_SCENES = {"01", "02", "03"}


def slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_json_file(path, payload)


def write_markdown(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_utf8_text(path, content)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_utf8_text(path, content)


def build_feishu_period(scene_id: str) -> str:
    now = datetime.now()
    if scene_id in FEISHU_WEEKLY_SCENES:
        iso_year, iso_week, _ = now.isocalendar()
        return f"{iso_year}-W{iso_week:02d}"
    return now.strftime("%Y-%m-%d")


def build_feishu_title_from_task(task: dict) -> str:
    return build_task_title(task)


def build_feishu_handoff(tasks: list[dict], helper_scripts: dict[str, str], batch_result_path: Path) -> dict:
    task_templates: list[dict[str, str]] = []
    for index, task in enumerate(tasks, start=1):
        scene_id = normalize_scene_id(task.get("scene"))
        if not scene_id:
            continue
        title = build_feishu_title_from_task(task)
        task_templates.append(
            {
                "index": str(index),
                "scene": scene_id,
                "scene_label": scene_label_zh(scene_id),
                "project": str(task.get("project", "")).strip(),
                "market": str(task.get("market", "")).strip(),
                "recommended_title": title,
                "recommended_base_name": title,
            }
        )
    return {
        "recommended_batch_result": str(batch_result_path),
        "helper_script": helper_scripts.get("push_feishu_ps1", ""),
        "helper_wrapper": helper_scripts.get("push_feishu_cmd", ""),
        "requires_env": ["FEISHU_APP_ID", "FEISHU_APP_SECRET"],
        "task_templates": task_templates,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate reusable batch JSON presets for TikTok Growth Operator.")
    parser.add_argument("--config", default="", help="Optional JSON config file for preset generation inputs.")
    parser.add_argument("--preset", default="", help="Preset slug to generate.")
    parser.add_argument("--list", action="store_true", help="List available preset slugs and descriptions.")
    parser.add_argument(
        "--template-output",
        default="",
        help="Optional JSON file path where a starter config template will be written instead of generating a queue.",
    )
    parser.add_argument(
        "--template-bundle-root",
        default="",
        help="Optional directory where a starter-template bundle will be written instead of generating a queue.",
    )
    parser.add_argument("--name", default="", help="Run slug prefix. Defaults to the preset slug.")
    parser.add_argument("--project", default="", help="Project title prefix. Defaults to the preset label.")
    parser.add_argument("--product", default="", help="Optional product or offer name for parameterized presets.")
    parser.add_argument("--category", default="", help="Optional category or niche name for parameterized presets.")
    parser.add_argument("--audience", default="", help="Optional audience segment for parameterized presets.")
    parser.add_argument("--account-name", default="", help="Optional account or creator name for parameterized presets.")
    parser.add_argument("--platform", default="", help="Override preset platform.")
    parser.add_argument("--market", default="", help="Override preset market.")
    parser.add_argument("--formats", default="", help="Formats field for generated tasks.")
    parser.add_argument("--capture-root", default="", help="Capture root used by capture-pack presets.")
    parser.add_argument("--task-root", default="", help="Root directory used for generated task output paths.")
    parser.add_argument(
        "--ordering",
        default="",
        choices=["input", "mode", "stage"],
        help="Task ordering strategy for combined preset output.",
    )
    parser.add_argument("--output", default="", help="Output JSON file path for the generated batch tasks.")
    return parser.parse_args()


def read_json(path: Path) -> dict | list:
    return read_json_file(path)


def get_config_value(config: dict, *keys: str) -> object:
    for key in keys:
        if key in config:
            return config[key]
    return ""


def read_text_value(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def normalize_preset_value(value: object) -> str:
    if isinstance(value, list):
        return ",".join(str(item).strip() for item in value if str(item).strip())
    return read_text_value(value)


def resolve_args(raw_args: argparse.Namespace) -> tuple[argparse.Namespace, dict, str]:
    config_path = Path(raw_args.config).expanduser().resolve() if raw_args.config.strip() else None
    config_payload: dict = {}
    if config_path:
        loaded = read_json(config_path)
        if not isinstance(loaded, dict):
            raise SystemExit("Preset config file must contain one JSON object.")
        config_payload = loaded

    resolved = argparse.Namespace(**vars(raw_args))
    resolved.config = str(config_path) if config_path else ""
    resolved.preset = raw_args.preset.strip() or normalize_preset_value(get_config_value(config_payload, "preset", "presets"))
    resolved.name = raw_args.name.strip() or read_text_value(get_config_value(config_payload, "name"))
    resolved.project = raw_args.project.strip() or read_text_value(get_config_value(config_payload, "project"))
    resolved.product = raw_args.product.strip() or read_text_value(get_config_value(config_payload, "product"))
    resolved.category = raw_args.category.strip() or read_text_value(get_config_value(config_payload, "category"))
    resolved.audience = raw_args.audience.strip() or read_text_value(get_config_value(config_payload, "audience"))
    resolved.account_name = raw_args.account_name.strip() or read_text_value(
        get_config_value(config_payload, "account_name", "account-name")
    )
    resolved.platform = raw_args.platform.strip() or read_text_value(get_config_value(config_payload, "platform"))
    resolved.market = raw_args.market.strip() or read_text_value(get_config_value(config_payload, "market"))
    resolved.formats = raw_args.formats.strip() or read_text_value(get_config_value(config_payload, "formats")) or "md"
    resolved.capture_root = raw_args.capture_root.strip() or read_text_value(
        get_config_value(config_payload, "capture_root", "capture-root")
    )
    resolved.task_root = raw_args.task_root.strip() or read_text_value(
        get_config_value(config_payload, "task_root", "task-root")
    )
    resolved.ordering = raw_args.ordering.strip() or read_text_value(get_config_value(config_payload, "ordering")) or "input"
    resolved.output = raw_args.output.strip() or read_text_value(get_config_value(config_payload, "output"))
    if resolved.ordering not in {"input", "mode", "stage"}:
        raise SystemExit(f"Unsupported ordering strategy: {resolved.ordering}")
    return resolved, config_payload, str(config_path) if config_path else ""


def collect_required_variables(preset_slugs: list[str]) -> list[str]:
    values: list[str] = []
    for preset_slug in preset_slugs:
        for variable in PRESETS[preset_slug].get("variables", []):
            if variable not in values:
                values.append(variable)
    return values


def collect_requirements(preset_slugs: list[str]) -> list[str]:
    values: list[str] = []
    for preset_slug in preset_slugs:
        for requirement in PRESETS[preset_slug].get("requires", []):
            if requirement not in values:
                values.append(requirement)
    return values


def parse_preset_slugs(raw: str) -> list[str]:
    values = [item.strip() for item in raw.split(",") if item.strip()]
    deduped: list[str] = []
    for value in values:
        if value not in deduped:
            deduped.append(value)
    return deduped


def build_default_task_root(preset_slug: str, name: str) -> Path:
    skill_root = Path(__file__).resolve().parents[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = slugify(name or preset_slug) or preset_slug
    return skill_root / "tmp" / f"{timestamp}-batch-preset-{preset_slug}-{suffix}"


def require_args(args: argparse.Namespace, preset_slugs: list[str]) -> None:
    if not preset_slugs:
        raise SystemExit("Preset generation requires --preset.")
    for preset_slug in preset_slugs:
        if preset_slug not in PRESETS:
            raise SystemExit(f"Unknown preset: {preset_slug}")
    if not args.output.strip():
        raise SystemExit("Preset generation requires --output.")
    for preset_slug in preset_slugs:
        for variable in PRESETS[preset_slug].get("variables", []):
            if variable == "product" and not args.product.strip():
                raise SystemExit(f"Preset {preset_slug} requires --product.")
            if variable == "category" and not args.category.strip():
                raise SystemExit(f"Preset {preset_slug} requires --category.")
            if variable == "audience" and not args.audience.strip():
                raise SystemExit(f"Preset {preset_slug} requires --audience.")
            if variable == "account_name" and not args.account_name.strip():
                raise SystemExit(f"Preset {preset_slug} requires --account-name.")
        for requirement in PRESETS[preset_slug].get("requires", []):
            if requirement == "capture_root" and not args.capture_root.strip():
                raise SystemExit(f"Preset {preset_slug} requires --capture-root.")


def render_list() -> list[dict]:
    payload = []
    for slug, preset in PRESETS.items():
        payload.append(
            {
                "slug": slug,
                "label": preset["label"],
                "description": preset["description"],
                "platform": preset["platform"],
                "market": preset["market"],
                "task_count": len(preset["tasks"]),
                "requires": preset.get("requires", []),
                "variables": preset.get("variables", []),
            }
        )
    return payload


def build_template_output_path(args: argparse.Namespace) -> Path:
    candidate = args.template_output.strip() or args.output.strip()
    if not candidate:
        raise SystemExit("Template generation requires --template-output or --output.")
    return Path(candidate).expanduser().resolve()


def build_template_bundle_root(args: argparse.Namespace) -> Path:
    candidate = args.template_bundle_root.strip()
    if not candidate:
        raise SystemExit("Template bundle generation requires --template-bundle-root.")
    return Path(candidate).expanduser().resolve()


def build_starter_config_template(args: argparse.Namespace, preset_slugs: list[str], config_source: str) -> dict:
    primary_preset = PRESETS[preset_slugs[0]]
    required_variables = collect_required_variables(preset_slugs)
    requirements = collect_requirements(preset_slugs)
    template: dict[str, object] = {
        "preset": preset_slugs if len(preset_slugs) > 1 else preset_slugs[0],
        "name": args.name or "replace-with-run-name",
        "project": args.project or "Replace With Project Name",
        "platform": args.platform or "",
        "market": args.market or "",
        "formats": args.formats or "md",
        "ordering": args.ordering or "input",
        "output": str(build_template_output_path(args)),
        "_notes": {
            "description": "Starter config template for scripts/generate_batch_preset.py --config",
            "selected_presets": preset_slugs,
            "preset_labels": [PRESETS[slug]["label"] for slug in preset_slugs],
            "required_variables": required_variables,
            "requirements": requirements,
            "default_platform": primary_preset["platform"],
            "default_market": primary_preset["market"],
            "config_source": config_source,
        },
    }
    if "product" in required_variables:
        template["product"] = args.product or "Replace With Product"
    if "category" in required_variables:
        template["category"] = args.category or "Replace With Category"
    if "audience" in required_variables:
        template["audience"] = args.audience or "Replace With Audience"
    if "account_name" in required_variables:
        template["account_name"] = args.account_name or "Replace With Account Name"
    if "capture_root" in requirements:
        template["capture_root"] = args.capture_root or "D:\\path\\to\\real-capture-pack"
    if args.task_root.strip():
        template["task_root"] = args.task_root
    return template


def apply_template_seed(template: dict, seed: dict[str, str]) -> dict:
    seeded = dict(template)
    notes = dict(template.get("_notes", {}))
    for key, value in seed.items():
        if str(value).strip():
            seeded[key] = value
    if seed:
        notes["seeded_defaults"] = seed
    seeded["_notes"] = notes
    return seeded


def build_named_bundle_template_path(bundle_root: Path, slug: str) -> Path:
    return bundle_root / f"{slug}.template.json"


def build_bundle_item(
    bundle_root: Path,
    slug: str,
    preset_slugs: list[str],
    config_source: str,
    args: argparse.Namespace,
    *,
    item_type: str,
    label: str,
    description: str,
    ordering: str = "",
    seed: dict[str, str] | None = None,
) -> dict:
    template_path = build_named_bundle_template_path(bundle_root, slug)
    queue_output_path = bundle_root / f"{slug}.json"
    bundle_args = argparse.Namespace(**vars(args))
    bundle_args.output = str(queue_output_path)
    if ordering:
        bundle_args.ordering = ordering
    template_payload = build_starter_config_template(bundle_args, preset_slugs, config_source)
    if seed:
        template_payload = apply_template_seed(template_payload, seed)
    write_json(template_path, template_payload)
    return {
        "slug": slug,
        "type": item_type,
        "presets": preset_slugs,
        "label": label,
        "description": description,
        "variables": collect_required_variables(preset_slugs),
        "requires": collect_requirements(preset_slugs),
        "ordering": template_payload.get("ordering", ordering or args.ordering or "input"),
        "suggested_output_file": str(queue_output_path),
        "seeded_defaults": seed or {},
        "template_file": str(template_path),
    }


def build_bundle_items(bundle_root: Path, preset_slugs: list[str], config_source: str, args: argparse.Namespace) -> list[dict]:
    if preset_slugs:
        single_slugs = preset_slugs
        allowed = set(preset_slugs)
    else:
        single_slugs = list(PRESETS)
        allowed = set(PRESETS)

    items: list[dict] = []
    for slug in single_slugs:
        preset = PRESETS[slug]
        items.append(
            build_bundle_item(
                bundle_root,
                slug,
                [slug],
                config_source,
                args,
                item_type="single",
                label=preset["label"],
                description=preset["description"],
            )
        )

    for combo_slug, combo in TEMPLATE_BUNDLES.items():
        combo_presets = list(combo["presets"])
        if any(preset_slug not in allowed for preset_slug in combo_presets):
            continue
        items.append(
            build_bundle_item(
                bundle_root,
                combo_slug,
                combo_presets,
                config_source,
                args,
                item_type="combo",
                label=combo["label"],
                description=combo["description"],
                ordering=combo.get("ordering", ""),
            )
        )
    for vertical_slug, vertical in VERTICAL_STARTERS.items():
        vertical_presets = list(vertical["presets"])
        if any(preset_slug not in allowed for preset_slug in vertical_presets):
            continue
        items.append(
            build_bundle_item(
                bundle_root,
                vertical_slug,
                vertical_presets,
                config_source,
                args,
                item_type="vertical",
                label=vertical["label"],
                description=vertical["description"],
                ordering=vertical.get("ordering", ""),
                seed=vertical.get("seed", {}),
            )
        )
    for board_slug, board in LAUNCH_BOARDS.items():
        board_presets = list(board["presets"])
        if any(preset_slug not in allowed for preset_slug in board_presets):
            continue
        items.append(
            build_bundle_item(
                bundle_root,
                board_slug,
                board_presets,
                config_source,
                args,
                item_type="launch-board",
                label=board["label"],
                description=board["description"],
                ordering=board.get("ordering", ""),
                seed=board.get("seed", {}),
            )
        )
    for board_slug, board in MANAGER_BOARDS.items():
        board_presets = list(board["presets"])
        if any(preset_slug not in allowed for preset_slug in board_presets):
            continue
        items.append(
            build_bundle_item(
                bundle_root,
                board_slug,
                board_presets,
                config_source,
                args,
                item_type="manager-board",
                label=board["label"],
                description=board["description"],
                ordering=board.get("ordering", ""),
                seed=board.get("seed", {}),
            )
        )
    for board_slug, board in CADENCE_BOARDS.items():
        board_presets = list(board["presets"])
        if any(preset_slug not in allowed for preset_slug in board_presets):
            continue
        items.append(
            build_bundle_item(
                bundle_root,
                board_slug,
                board_presets,
                config_source,
                args,
                item_type="cadence-board",
                label=board["label"],
                description=board["description"],
                ordering=board.get("ordering", ""),
                seed=board.get("seed", {}),
            )
        )
    return items


def render_bundle_report(bundle_root: Path, items: list[dict]) -> str:
    single_count = sum(1 for item in items if item["type"] == "single")
    combo_count = sum(1 for item in items if item["type"] == "combo")
    vertical_count = sum(1 for item in items if item["type"] == "vertical")
    launch_board_count = sum(1 for item in items if item["type"] == "launch-board")
    manager_board_count = sum(1 for item in items if item["type"] == "manager-board")
    cadence_board_count = sum(1 for item in items if item["type"] == "cadence-board")
    lines = [
        "# Preset Template Bundle",
        "",
        "## Overview",
        "",
        f"- bundle root: `{bundle_root}`",
        f"- template count: `{len(items)}`",
        f"- single templates: `{single_count}`",
        f"- combo templates: `{combo_count}`",
        f"- vertical starters: `{vertical_count}`",
        f"- launch boards: `{launch_board_count}`",
        f"- manager boards: `{manager_board_count}`",
        f"- cadence boards: `{cadence_board_count}`",
        "",
        "## How To Use",
        "",
        "- fill one `*.template.json` file with your variables and real output path",
        "- run `python scripts/generate_batch_preset.py --config <filled-template.json>` to create the real queue",
        "- use single templates when one preset is enough",
        "- use combo templates when you want a reusable multi-preset board without hand-assembling the preset list",
        "- use vertical starters when you want a seeded business board with default platform, market, naming, and capture fixture values",
        "- use launch boards when you think in weekly outcomes such as publish, review, localization, or testing instead of vertical ownership",
        "- use manager boards when the entrypoint should match who is operating the workflow, such as content, live, strategy, or growth",
        "- use cadence boards when the entrypoint should match the operating rhythm, such as daily, weekly, launch sprint, or live shift",
        f"- vertical suites live under `{build_vertical_suite_root(bundle_root)}` and include generate/dry-run/run helpers",
        "",
        "## Templates",
        "",
    ]
    for item in items:
        lines.append(f"### {item['label']}")
        lines.append("")
        lines.append(f"- type: `{item['type']}`")
        lines.append(f"- slug: `{item['slug']}`")
        lines.append(f"- presets: `{', '.join(item['presets'])}`")
        lines.append(f"- ordering: `{item['ordering']}`")
        lines.append(f"- template file: `{item['template_file']}`")
        lines.append(f"- suggested output file: `{item['suggested_output_file']}`")
        if item["variables"]:
            lines.append(f"- variables: `{', '.join(item['variables'])}`")
        else:
            lines.append("- variables: none")
        if item["requires"]:
            lines.append(f"- requirements: `{', '.join(item['requires'])}`")
        else:
            lines.append("- requirements: none")
        if item["seeded_defaults"]:
            lines.append("- seeded defaults:")
            for key, value in item["seeded_defaults"].items():
                lines.append(f"- seeded `{key}`: `{value}`")
        if item.get("suite_root"):
            lines.append(f"- suite root: `{item['suite_root']}`")
            lines.append(f"- suite generate script: `{item['suite_generate_ps1']}`")
            lines.append(f"- suite dry-run script: `{item['suite_dry_run_ps1']}`")
            lines.append(f"- suite run script: `{item['suite_run_ps1']}`")
        lines.append(f"- description: {item['description']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def resolve_capture_root(args: argparse.Namespace, template: dict) -> str:
    if template.get("capture_root_ref") == "capture_root":
        return str(Path(args.capture_root).expanduser().resolve())
    return ""


def build_task_output_path(task_root: Path, template: dict) -> str:
    return str((task_root / template["path_suffix"]).resolve())


def build_template_context(args: argparse.Namespace, preset_slug: str, preset: dict) -> dict:
    product = args.product.strip()
    category = args.category.strip()
    audience = args.audience.strip()
    account_name = args.account_name.strip()
    market = args.market.strip() or preset["market"]
    name = args.name.strip() or preset_slug
    project = args.project.strip() or preset["label"]
    return {
        "product": product,
        "product_slug": slugify(product) or "product",
        "category": category,
        "category_slug": slugify(category) or "category",
        "audience": audience,
        "audience_slug": slugify(audience) or "audience",
        "account_name": account_name,
        "account_slug": slugify(account_name) or "account",
        "market": market,
        "market_slug": slugify(market) or "market",
        "name": name,
        "project": project,
        "preset": preset_slug,
    }


def render_template(value: str, context: dict) -> str:
    return value.format(**context)


def build_task(args: argparse.Namespace, preset_slug: str, preset: dict, template: dict, task_root: Path) -> dict:
    base_name = slugify(args.name or preset_slug) or preset_slug
    project_base = args.project.strip() or preset["label"]
    platform = args.platform.strip() or preset["platform"]
    market = args.market.strip() or preset["market"]
    context = build_template_context(args, preset_slug, preset)
    task = {
        "mode": template["mode"],
        "name": render_template(f"{base_name}-{template['name_suffix']}", context),
        "project": render_template(f"{project_base} - {template['project_suffix']}", context),
        "formats": args.formats,
        "platform": platform,
        "market": market,
        "_preset": preset_slug,
    }
    if template["mode"] == "goal":
        task["query"] = render_template(template["query"], context)
        task["output_root"] = build_task_output_path(task_root, template)
    elif template["mode"] == "capture-pack":
        task["scene"] = template["scene"]
        task["capture_root"] = resolve_capture_root(args, template)
        task["output_root"] = build_task_output_path(task_root, template)
    elif template["mode"] == "pack":
        task["type"] = template["type"]
        task["output_dir"] = build_task_output_path(task_root, template)
    else:
        task["scene"] = template["scene"]
        task["output_root"] = build_task_output_path(task_root, template)
    return task


def task_sort_key(task: dict, ordering: str, index: int) -> tuple:
    if ordering == "input":
        return (index,)
    if ordering == "mode":
        return (MODE_ORDER.get(task["mode"], 99), index)
    if ordering == "stage":
        return (STAGE_ORDER.get(task["mode"], 99), task.get("scene", ""), task.get("name", ""), index)
    return (index,)


def order_tasks(tasks: list[dict], ordering: str) -> list[dict]:
    indexed = list(enumerate(tasks))
    indexed.sort(key=lambda item: task_sort_key(item[1], ordering, item[0]))
    return [task for _, task in indexed]


def strip_internal_fields(tasks: list[dict]) -> list[dict]:
    cleaned = []
    for task in tasks:
        cleaned.append({key: value for key, value in task.items() if not key.startswith("_")})
    return cleaned


def build_mode_counts(tasks: list[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for task in tasks:
        mode = str(task.get("mode", "")).strip() or "unknown"
        counts[mode] = counts.get(mode, 0) + 1
    return counts


def build_recommended_batch_root(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}-batch-run")


def build_recommended_output_file(output_path: Path) -> Path:
    return output_path.with_name(f"{output_path.stem}.result.json")


def build_helper_script_paths(output_path: Path) -> dict[str, Path]:
    stem = output_path.stem
    parent = output_path.parent
    return {
        "dry_run_ps1": parent / f"{stem}.dry-run.ps1",
        "run_ps1": parent / f"{stem}.run.ps1",
        "rerun_ps1": parent / f"{stem}.rerun.ps1",
        "dry_run_cmd": parent / f"{stem}.dry-run.cmd",
        "run_cmd": parent / f"{stem}.run.cmd",
        "rerun_cmd": parent / f"{stem}.rerun.cmd",
        "input_json": parent / f"{stem}.input.json",
        "generate_ps1": parent / f"{stem}.generate.ps1",
        "generate_cmd": parent / f"{stem}.generate.cmd",
        "push_feishu_ps1": parent / f"{stem}.push-feishu.ps1",
        "push_feishu_cmd": parent / f"{stem}.push-feishu.cmd",
    }


def shell_quote(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def format_command(command: str, args: list[str]) -> str:
    lines = [command + " `"]
    for index, arg in enumerate(args):
        suffix = " `" if index < len(args) - 1 else ""
        lines.append(f"  {arg}{suffix}")
    return "\n".join(lines)


def format_powershell_command(command: str, args: list[str]) -> str:
    parts = [shell_quote(command), *[shell_quote(arg) for arg in args]]
    return "& " + " ".join(parts)


def render_helper_ps1(
    title: str,
    command: str,
    args: list[str],
    skill_root: Path,
) -> str:
    return "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            f"$Host.UI.RawUI.WindowTitle = {shell_quote(title)}",
            f"Set-Location -LiteralPath {shell_quote(str(skill_root))}",
            "",
            format_powershell_command(command, args),
            "",
        ]
    )


def render_helper_cmd(ps1_path: Path) -> str:
    return "\n".join(
        [
            "@echo off",
            "setlocal",
            f'powershell -ExecutionPolicy Bypass -File "{ps1_path}"',
            "set EXIT_CODE=%ERRORLEVEL%",
            "if not \"%EXIT_CODE%\"==\"0\" pause",
            "exit /b %EXIT_CODE%",
            "",
        ]
    )


def render_push_feishu_ps1(
    title: str,
    batch_result_path: Path,
    skill_root: Path,
    push_script_path: Path,
) -> str:
    return "\n".join(
        [
            "$ErrorActionPreference = 'Stop'",
            f"$Host.UI.RawUI.WindowTitle = {shell_quote(title)}",
            f"Set-Location -LiteralPath {shell_quote(str(skill_root))}",
            "",
            "if (-not $env:FEISHU_APP_ID) {",
            "  throw 'Set FEISHU_APP_ID before running this helper.'",
            "}",
            "if (-not $env:FEISHU_APP_SECRET) {",
            "  throw 'Set FEISHU_APP_SECRET before running this helper.'",
            "}",
            f"$BatchResult = {shell_quote(str(batch_result_path))}",
            "if (-not (Test-Path -LiteralPath $BatchResult)) {",
            "  throw \"Expected batch result file not found: $BatchResult\"",
            "}",
            "",
            format_powershell_command(
                "python",
                [
                    str(push_script_path),
                    "--batch-result",
                    str(batch_result_path),
                ],
            ),
            "",
        ]
    )


def build_vertical_suite_root(bundle_root: Path) -> Path:
    return bundle_root / "vertical-suites"


def build_vertical_suite_paths(bundle_root: Path, slug: str) -> dict[str, Path]:
    suite_root = build_vertical_suite_root(bundle_root) / slug
    return {
        "suite_root": suite_root,
        "config_json": suite_root / f"{slug}.config.json",
        "queue_json": suite_root / f"{slug}.json",
        "generate_ps1": suite_root / "generate.ps1",
        "generate_cmd": suite_root / "generate.cmd",
        "dry_run_ps1": suite_root / "dry-run.ps1",
        "dry_run_cmd": suite_root / "dry-run.cmd",
        "run_ps1": suite_root / "run.ps1",
        "run_cmd": suite_root / "run.cmd",
        "readme_md": suite_root / "README.md",
    }


def render_vertical_suite_readme(item: dict, suite_paths: dict[str, Path], batch_root: Path, result_file: Path) -> str:
    lines = [
        f"# {item['label']}",
        "",
        f"- type: `{item['type']}`",
        f"- slug: `{item['slug']}`",
        f"- presets: `{', '.join(item['presets'])}`",
        f"- ordering: `{item['ordering']}`",
        f"- config file: `{suite_paths['config_json']}`",
        f"- queue file: `{suite_paths['queue_json']}`",
        f"- recommended batch root: `{batch_root}`",
        f"- recommended result file: `{result_file}`",
        "",
        "## Helper Scripts",
        "",
        f"- generate: `{suite_paths['generate_ps1']}`",
        f"- dry-run: `{suite_paths['dry_run_ps1']}`",
        f"- execute: `{suite_paths['run_ps1']}`",
        "",
        "## Seeded Defaults",
        "",
    ]
    if item["seeded_defaults"]:
        for key, value in item["seeded_defaults"].items():
            lines.append(f"- `{key}`: `{value}`")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Manual Commands",
            "",
            "### Generate Queue",
            "",
            "```powershell",
            format_command(
                "python scripts/generate_batch_preset.py",
                [f"--config {shell_quote(str(suite_paths['config_json']))}"],
            ),
            "```",
            "",
            "### Dry Run",
            "",
            "```powershell",
            format_command(
                "python scripts/batch_run_operator_workflows.py",
                [
                    f"--batch-file {shell_quote(str(suite_paths['queue_json']))}",
                    "--dry-run",
                    f"--batch-root {shell_quote(str(batch_root))}",
                ],
            ),
            "```",
            "",
            "### Execute",
            "",
            "```powershell",
            format_command(
                "python scripts/batch_run_operator_workflows.py",
                [
                    f"--batch-file {shell_quote(str(suite_paths['queue_json']))}",
                    f"--batch-root {shell_quote(str(batch_root))}",
                    f"--output-file {shell_quote(str(result_file))}",
                ],
            ),
            "```",
            "",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def export_vertical_suite(bundle_root: Path, item: dict, skill_root: Path) -> dict[str, str]:
    suite_paths = build_vertical_suite_paths(bundle_root, item["slug"])
    batch_root = suite_paths["suite_root"] / "batch-run"
    result_file = suite_paths["suite_root"] / f"{item['slug']}.result.json"

    config_payload = read_json(Path(item["template_file"]))
    if isinstance(config_payload, dict):
        config_payload["output"] = str(suite_paths["queue_json"])
        notes = config_payload.get("_notes")
        if isinstance(notes, dict):
            notes["suite_root"] = str(suite_paths["suite_root"])
            notes["suite_queue_output"] = str(suite_paths["queue_json"])
    write_json(suite_paths["config_json"], config_payload)

    generate_args = [
        str(Path(__file__).resolve()),
        "--config",
        str(suite_paths["config_json"]),
    ]
    dry_run_args = [
        str(Path(__file__).resolve().parent / "batch_run_operator_workflows.py"),
        "--batch-file",
        str(suite_paths["queue_json"]),
        "--dry-run",
        "--batch-root",
        str(batch_root),
    ]
    run_args = [
        str(Path(__file__).resolve().parent / "batch_run_operator_workflows.py"),
        "--batch-file",
        str(suite_paths["queue_json"]),
        "--batch-root",
        str(batch_root),
        "--output-file",
        str(result_file),
    ]

    write_text(
        suite_paths["generate_ps1"],
        render_helper_ps1("TikTok Growth Operator Vertical Generate", "python", generate_args, skill_root),
    )
    write_text(
        suite_paths["dry_run_ps1"],
        render_helper_ps1("TikTok Growth Operator Vertical Dry Run", "python", dry_run_args, skill_root),
    )
    write_text(
        suite_paths["run_ps1"],
        render_helper_ps1("TikTok Growth Operator Vertical Run", "python", run_args, skill_root),
    )
    write_text(suite_paths["generate_cmd"], render_helper_cmd(suite_paths["generate_ps1"]))
    write_text(suite_paths["dry_run_cmd"], render_helper_cmd(suite_paths["dry_run_ps1"]))
    write_text(suite_paths["run_cmd"], render_helper_cmd(suite_paths["run_ps1"]))
    write_markdown(
        suite_paths["readme_md"],
        render_vertical_suite_readme(item, suite_paths, batch_root, result_file),
    )
    return {key: str(value) for key, value in suite_paths.items()}


def build_manifest(
    args: argparse.Namespace,
    config_source: str,
    preset_slugs: list[str],
    presets: list[dict],
    task_root: Path,
    output_path: Path,
    report_path: Path,
    helper_scripts: dict[str, str],
    input_payload: dict,
    tasks: list[dict],
) -> dict:
    combined_requires: list[str] = []
    combined_variables: list[str] = []
    for preset in presets:
        for item in preset.get("requires", []):
            if item not in combined_requires:
                combined_requires.append(item)
        for item in preset.get("variables", []):
            if item not in combined_variables:
                combined_variables.append(item)
    feishu_handoff = build_feishu_handoff(tasks, helper_scripts, build_recommended_output_file(output_path))
    return {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "preset": preset_slugs[0] if len(preset_slugs) == 1 else "",
        "presets": preset_slugs,
        "labels": [preset["label"] for preset in presets],
        "descriptions": [preset["description"] for preset in presets],
        "platform": args.platform.strip() or presets[0]["platform"],
        "market": args.market.strip() or presets[0]["market"],
        "ordering_strategy": args.ordering,
        "config_source": config_source,
        "requires": combined_requires,
        "variables": combined_variables,
        "variable_values": {
            "product": args.product.strip(),
            "category": args.category.strip(),
            "audience": args.audience.strip(),
            "account_name": args.account_name.strip(),
        },
        "task_root": str(task_root),
        "output_file": str(output_path),
        "report_file": str(report_path),
        "helper_scripts": helper_scripts,
        "feishu_handoff": feishu_handoff,
        "input_payload": input_payload,
        "task_count": len(tasks),
        "task_modes": [task["mode"] for task in tasks],
        "task_mode_counts": build_mode_counts(tasks),
        "tasks": tasks,
    }


def render_preset_report(
    args: argparse.Namespace,
    preset_slugs: list[str],
    presets: list[dict],
    output_path: Path,
    manifest_path: Path,
    report_path: Path,
    manifest: dict,
) -> str:
    mode_counts = manifest["task_mode_counts"]
    variable_values = manifest["variable_values"]
    batch_root = build_recommended_batch_root(output_path)
    batch_output_file = build_recommended_output_file(output_path)
    helper_scripts = manifest["helper_scripts"]
    feishu_handoff = manifest.get("feishu_handoff", {})
    dry_run_command = format_command(
        "python scripts/batch_run_operator_workflows.py",
        [
            f"--batch-file {shell_quote(str(output_path))}",
            "--dry-run",
            f"--batch-root {shell_quote(str(batch_root))}",
        ],
    )
    run_command = format_command(
        "python scripts/batch_run_operator_workflows.py",
        [
            f"--batch-file {shell_quote(str(output_path))}",
            f"--batch-root {shell_quote(str(batch_root))}",
            f"--output-file {shell_quote(str(batch_output_file))}",
        ],
    )
    rerun_command = format_command(
        "python scripts/batch_run_operator_workflows.py",
        [
            f"--rerun-failed-from {shell_quote(str(batch_root))}",
            f"--batch-root {shell_quote(str(batch_root.with_name(batch_root.name + '-rerun')))}",
        ],
    )
    lines = [
        "# Batch Preset Report",
        "",
        "## Overview",
        "",
        f"- presets: `{', '.join(preset_slugs)}`",
        f"- labels: `{', '.join(manifest['labels'])}`",
        f"- ordering: `{manifest['ordering_strategy']}`",
        f"- platform: `{manifest['platform']}`",
        f"- market: `{manifest['market']}`",
        f"- task count: `{manifest['task_count']}`",
        f"- task root: `{manifest['task_root']}`",
        f"- output file: `{output_path}`",
        f"- manifest file: `{manifest_path}`",
        f"- report file: `{report_path}`",
        "",
        "## Preset Details",
        "",
    ]
    for slug, preset in zip(preset_slugs, presets):
        lines.append(f"### {preset['label']} (`{slug}`)")
        lines.append("")
        lines.append(f"- description: {preset['description']}")
        lines.append(f"- default platform: `{preset['platform']}`")
        lines.append(f"- default market: `{preset['market']}`")
        if preset.get("variables"):
            lines.append(f"- variables: `{', '.join(preset['variables'])}`")
        else:
            lines.append("- variables: none")
        if preset.get("requires"):
            lines.append(f"- requirements: `{', '.join(preset['requires'])}`")
        else:
            lines.append("- requirements: none")
        lines.append(f"- generated tasks: `{len(preset['tasks'])}`")
        lines.append("")

    lines.extend(
        [
            "## Variable Values",
            "",
        ]
    )
    for key, value in variable_values.items():
        display = value if value else "(not set)"
        lines.append(f"- `{key}`: {display}")
    if args.capture_root.strip():
        lines.append(f"- `capture_root`: `{Path(args.capture_root).expanduser().resolve()}`")
    else:
        lines.append("- `capture_root`: (not set)")
    lines.extend(
        [
            "",
            "## Mode Summary",
            "",
        ]
    )
    for mode, count in sorted(mode_counts.items()):
        lines.append(f"- `{mode}`: `{count}`")
    lines.extend(
        [
            "",
            "## Execution Handoff",
            "",
            f"- recommended batch root: `{batch_root}`",
            f"- recommended result file: `{batch_output_file}`",
            f"- reusable input file: `{helper_scripts['input_json']}`",
            f"- dry-run script: `{helper_scripts['dry_run_ps1']}`",
            f"- run script: `{helper_scripts['run_ps1']}`",
            f"- rerun script: `{helper_scripts['rerun_ps1']}`",
            "- run dry-run first when you want to inspect routing and artifact paths before execution",
            "- use rerun-failed-from against the batch root if some tasks fail or are blocked",
            "",
            "### Regenerate Preset",
            "",
            f"- input file: `{helper_scripts['input_json']}`",
            f"- PowerShell regenerate: `{helper_scripts['generate_ps1']}`",
            f"- PowerShell push Feishu: `{helper_scripts['push_feishu_ps1']}`",
            f"- CMD regenerate wrapper: `{helper_scripts['generate_cmd']}`",
            f"- CMD push Feishu wrapper: `{helper_scripts['push_feishu_cmd']}`",
            "",
            "### Helper Scripts",
            "",
            f"- PowerShell dry-run: `{helper_scripts['dry_run_ps1']}`",
            f"- PowerShell run: `{helper_scripts['run_ps1']}`",
            f"- PowerShell rerun: `{helper_scripts['rerun_ps1']}`",
            f"- PowerShell regenerate: `{helper_scripts['generate_ps1']}`",
            f"- PowerShell push Feishu: `{helper_scripts['push_feishu_ps1']}`",
            f"- CMD dry-run wrapper: `{helper_scripts['dry_run_cmd']}`",
            f"- CMD run wrapper: `{helper_scripts['run_cmd']}`",
            f"- CMD rerun wrapper: `{helper_scripts['rerun_cmd']}`",
            f"- CMD regenerate wrapper: `{helper_scripts['generate_cmd']}`",
            f"- CMD push Feishu wrapper: `{helper_scripts['push_feishu_cmd']}`",
            "",
            "### Dry Run",
            "",
            "```powershell",
            dry_run_command,
            "```",
            "",
            "### Execute",
            "",
            "```powershell",
            run_command,
            "```",
            "",
            "### Rerun Failed Or Invalid",
            "",
            "```powershell",
            rerun_command,
            "```",
            "",
            "### Regenerate From Saved Input",
            "",
            "```powershell",
            format_command(
                "python scripts/generate_batch_preset.py",
                [f"--config {shell_quote(helper_scripts['input_json'])}"],
            ),
            "```",
            "",
            "## 飞书推送跟进",
            "",
            f"- 预期批量结果文件：`{feishu_handoff.get('recommended_batch_result', '')}`",
            f"- PowerShell 推送助手：`{helper_scripts['push_feishu_ps1']}`",
            f"- CMD 推送助手：`{helper_scripts['push_feishu_cmd']}`",
            "- 必需环境变量：`FEISHU_APP_ID`、`FEISHU_APP_SECRET`",
            "",
            "### 设置凭证",
            "",
            "```powershell",
            '$env:FEISHU_APP_ID="cli_xxx"',
            '$env:FEISHU_APP_SECRET="xxx"',
            "```",
            "",
            "### 推送本批次里所有成功的 Scene 报告",
            "",
            "```powershell",
            format_command(
                "python scripts/push_batch_results_to_feishu.py",
                [f"--batch-result {shell_quote(str(batch_output_file))}"],
            ),
            "```",
            "",
            "### 用生成好的助手脚本直接推送",
            "",
            "```powershell",
            f'& {shell_quote(helper_scripts["push_feishu_ps1"])}',
            "```",
            "",
            "### 推荐飞书命名",
            "",
        ]
    )
    for template in feishu_handoff.get("task_templates", []):
        lines.append(
            f"- 任务 `{template['index']}` 场景 `{template['scene']}`（{template['scene_label']}） -> `{template['recommended_title']}`"
        )
    lines.extend(
        [
            "",
            "## Tasks",
            "",
        ]
    )
    for index, task in enumerate(manifest["tasks"], start=1):
        title = task.get("project") or task.get("name") or f"Task {index}"
        lines.append(f"### {index:03d} {title}")
        lines.append("")
        lines.append(f"- mode: `{task['mode']}`")
        if task.get("scene"):
            lines.append(f"- scene: `{task['scene']}`")
        if task.get("type"):
            lines.append(f"- pack type: `{task['type']}`")
        if task.get("query"):
            lines.append(f"- query: `{task['query']}`")
        if task.get("capture_root"):
            lines.append(f"- capture root: `{task['capture_root']}`")
        if task.get("output_root"):
            lines.append(f"- output root: `{task['output_root']}`")
        if task.get("output_dir"):
            lines.append(f"- output dir: `{task['output_dir']}`")
        lines.append(f"- name: `{task.get('name', '')}`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    raw_args = parse_args()
    if raw_args.list:
        print(json.dumps(render_list(), ensure_ascii=False, indent=2))
        return
    args, config_payload, config_source = resolve_args(raw_args)

    preset_slugs = parse_preset_slugs(args.preset)
    if raw_args.template_bundle_root.strip():
        bundle_root = build_template_bundle_root(args)
        bundle_root.mkdir(parents=True, exist_ok=True)
        index_items = build_bundle_items(bundle_root, preset_slugs, config_source, args)
        skill_root = Path(__file__).resolve().parents[1]
        for item in index_items:
            if item["type"] not in {"vertical", "launch-board", "manager-board", "cadence-board"}:
                continue
            suite_paths = export_vertical_suite(bundle_root, item, skill_root)
            item["suite_root"] = suite_paths["suite_root"]
            item["suite_config_json"] = suite_paths["config_json"]
            item["suite_queue_json"] = suite_paths["queue_json"]
            item["suite_generate_ps1"] = suite_paths["generate_ps1"]
            item["suite_dry_run_ps1"] = suite_paths["dry_run_ps1"]
            item["suite_run_ps1"] = suite_paths["run_ps1"]
        index_path = bundle_root / "template-index.json"
        report_path = bundle_root / "README.md"
        write_json(
            index_path,
            {
                "bundle_root": str(bundle_root),
                "single_template_count": sum(1 for item in index_items if item["type"] == "single"),
                "combo_template_count": sum(1 for item in index_items if item["type"] == "combo"),
                "vertical_template_count": sum(1 for item in index_items if item["type"] == "vertical"),
                "launch_board_count": sum(1 for item in index_items if item["type"] == "launch-board"),
                "manager_board_count": sum(1 for item in index_items if item["type"] == "manager-board"),
                "cadence_board_count": sum(1 for item in index_items if item["type"] == "cadence-board"),
                "vertical_suite_root": str(build_vertical_suite_root(bundle_root)),
                "items": index_items,
            },
        )
        write_markdown(report_path, render_bundle_report(bundle_root, index_items))
        print(
            json.dumps(
                {
                    "mode": "template-bundle",
                    "bundle_root": str(bundle_root),
                    "template_count": len(index_items),
                    "single_template_count": sum(1 for item in index_items if item["type"] == "single"),
                    "combo_template_count": sum(1 for item in index_items if item["type"] == "combo"),
                    "vertical_template_count": sum(1 for item in index_items if item["type"] == "vertical"),
                    "launch_board_count": sum(1 for item in index_items if item["type"] == "launch-board"),
                    "manager_board_count": sum(1 for item in index_items if item["type"] == "manager-board"),
                    "cadence_board_count": sum(1 for item in index_items if item["type"] == "cadence-board"),
                    "vertical_suite_root": str(build_vertical_suite_root(bundle_root)),
                    "index_file": str(index_path),
                    "report_file": str(report_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if raw_args.template_output.strip():
        if not preset_slugs:
            raise SystemExit("Template generation requires --preset.")
        for preset_slug in preset_slugs:
            if preset_slug not in PRESETS:
                raise SystemExit(f"Unknown preset: {preset_slug}")
        template_output_path = build_template_output_path(args)
        template_payload = build_starter_config_template(args, preset_slugs, config_source)
        write_json(template_output_path, template_payload)
        print(
            json.dumps(
                {
                    "mode": "template",
                    "presets": preset_slugs,
                    "template_output": str(template_output_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    require_args(args, preset_slugs)
    presets = [PRESETS[preset_slug] for preset_slug in preset_slugs]
    preset_slug = "-".join(preset_slugs)

    task_root = (
        Path(args.task_root).expanduser().resolve() if args.task_root.strip() else build_default_task_root(preset_slug, args.name)
    )
    output_path = Path(args.output).expanduser().resolve()

    tasks = []
    for current_slug, preset in zip(preset_slugs, presets):
        tasks.extend(build_task(args, current_slug, preset, template, task_root) for template in preset["tasks"])
    ordered_tasks = order_tasks(tasks, args.ordering)
    public_tasks = strip_internal_fields(ordered_tasks)
    manifest_path = output_path.with_name(f"{output_path.stem}.manifest.json")
    report_path = output_path.with_name(f"{output_path.stem}.report.md")
    helper_script_paths = build_helper_script_paths(output_path)
    batch_runner_path = Path(__file__).resolve().parent / "batch_run_operator_workflows.py"
    push_batch_feishu_path = Path(__file__).resolve().parent / "push_batch_results_to_feishu.py"
    skill_root = Path(__file__).resolve().parents[1]
    dry_run_args = [
        str(batch_runner_path),
        "--batch-file",
        str(output_path),
        "--dry-run",
        "--batch-root",
        str(build_recommended_batch_root(output_path)),
    ]
    run_args = [
        str(batch_runner_path),
        "--batch-file",
        str(output_path),
        "--batch-root",
        str(build_recommended_batch_root(output_path)),
        "--output-file",
        str(build_recommended_output_file(output_path)),
    ]
    rerun_args = [
        str(batch_runner_path),
        "--rerun-failed-from",
        str(build_recommended_batch_root(output_path)),
        "--batch-root",
        str(build_recommended_batch_root(output_path).with_name(build_recommended_batch_root(output_path).name + "-rerun")),
    ]
    input_payload = {
        "preset": preset_slugs if len(preset_slugs) > 1 else preset_slugs[0],
        "name": args.name,
        "project": args.project,
        "product": args.product,
        "category": args.category,
        "audience": args.audience,
        "account_name": args.account_name,
        "platform": args.platform,
        "market": args.market,
        "formats": args.formats,
        "capture_root": args.capture_root,
        "task_root": args.task_root,
        "ordering": args.ordering,
        "output": str(output_path),
    }
    if config_source:
        input_payload["source_config_file"] = config_source
    helper_scripts = {key: str(value) for key, value in helper_script_paths.items()}
    manifest = build_manifest(
        args,
        config_source,
        preset_slugs,
        presets,
        task_root,
        output_path,
        report_path,
        helper_scripts,
        input_payload,
        public_tasks,
    )
    report = render_preset_report(args, preset_slugs, presets, output_path, manifest_path, report_path, manifest)

    write_json(output_path, public_tasks)
    write_json(manifest_path, manifest)
    write_markdown(report_path, report)
    write_json(helper_script_paths["input_json"], input_payload)
    write_text(
        helper_script_paths["dry_run_ps1"],
        render_helper_ps1("TikTok Growth Operator Dry Run", "python", dry_run_args, skill_root),
    )
    write_text(
        helper_script_paths["run_ps1"],
        render_helper_ps1("TikTok Growth Operator Run", "python", run_args, skill_root),
    )
    write_text(
        helper_script_paths["rerun_ps1"],
        render_helper_ps1("TikTok Growth Operator Rerun", "python", rerun_args, skill_root),
    )
    write_text(
        helper_script_paths["generate_ps1"],
        render_helper_ps1(
            "TikTok Growth Operator Preset Generate",
            "python",
            [str(Path(__file__).resolve()), "--config", str(helper_script_paths["input_json"])],
            skill_root,
        ),
    )
    write_text(
        helper_script_paths["push_feishu_ps1"],
        render_push_feishu_ps1(
            "TikTok Growth Operator Push Batch Results To Feishu",
            build_recommended_output_file(output_path),
            skill_root,
            push_batch_feishu_path,
        ),
    )
    write_text(helper_script_paths["dry_run_cmd"], render_helper_cmd(helper_script_paths["dry_run_ps1"]))
    write_text(helper_script_paths["run_cmd"], render_helper_cmd(helper_script_paths["run_ps1"]))
    write_text(helper_script_paths["rerun_cmd"], render_helper_cmd(helper_script_paths["rerun_ps1"]))
    write_text(helper_script_paths["generate_cmd"], render_helper_cmd(helper_script_paths["generate_ps1"]))
    write_text(helper_script_paths["push_feishu_cmd"], render_helper_cmd(helper_script_paths["push_feishu_ps1"]))

    print(
        json.dumps(
            {
                "preset": preset_slugs[0] if len(preset_slugs) == 1 else "",
                "presets": preset_slugs,
                "config_source": config_source,
                "output_file": str(output_path),
                "manifest_file": str(manifest_path),
                "report_file": str(report_path),
                "helper_scripts": helper_scripts,
                "task_root": str(task_root),
                "task_count": len(tasks),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
