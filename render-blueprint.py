#!/usr/bin/env python3
"""
Render avonomics-blueprint.json to Markdown documentation.
Usage: python render-blueprint.py [--output FILE]
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


def load_blueprint(path: str = "avonomics-blueprint.json") -> dict:
    with open(path, "r") as f:
        return json.load(f)


def render_metadata(metadata: dict) -> str:
    lines = [
        f"# {metadata['title']}",
        "",
        f"**Version:** {metadata['version']}  ",
        f"**Status:** {metadata['status'].capitalize()}  ",
        f"**Last Updated:** {metadata['last_updated']}",
        "",
    ]

    if metadata.get("changelog"):
        lines.append("### Changelog")
        lines.append("")
        lines.append("| Version | Date | Description |")
        lines.append("|---------|------|-------------|")
        for entry in metadata["changelog"]:
            lines.append(f"| {entry['version']} | {entry['date']} | {entry['description']} |")
        lines.append("")

    return "\n".join(lines)


def render_executive_summary(summary: dict) -> str:
    lines = [
        f"## {summary['section_number']}. {summary['title']}",
        "",
        summary["content"]["overview"],
        "",
        summary["content"]["solana_context"],
        "",
        summary["content"]["avo_positioning"],
        "",
        summary["content"]["economic_challenge"],
        "",
        summary["content"]["solution_overview"],
        "",
        "### Strategic Pillars",
        "",
    ]

    for pillar in summary["strategic_pillars"]:
        lines.append(f"**{pillar['number']}. {pillar['name']}:** {pillar['description']}")
        lines.append("")

    return "\n".join(lines)


def render_table(table: dict) -> str:
    lines = [
        f"**Table {table['table_id']}: {table['title']}**",
        "",
    ]

    # Handle different table formats
    if table["table_id"] == "3.1":
        lines.append("| Scenario | User Pays | Deployer Earns | Avo Net Revenue |")
        lines.append("|----------|-----------|----------------|-----------------|")
        for row in table["rows"]:
            user = f"${row['user_pays']['amount']:,}" if isinstance(row['user_pays']['amount'], int) else f"${row['user_pays']['amount']}"
            if 'percentage' in row['user_pays']:
                user += f" ({row['user_pays']['percentage']}%)"
            elif 'note' in row['user_pays']:
                user += f" ({row['user_pays']['note']})"

            deployer = f"${row['deployer_earns']['amount']:,}" if row['deployer_earns']['amount'] >= 0 else f"${row['deployer_earns']['amount']}"
            if 'percentage' in row['deployer_earns']:
                deployer += f" ({row['deployer_earns']['percentage']}%)"
            elif 'note' in row['deployer_earns']:
                deployer += f" ({row['deployer_earns']['note']})"

            avo = f"${row['avo_net_revenue']['amount']:,}" if row['avo_net_revenue']['amount'] >= 0 else f"${row['avo_net_revenue']['amount']}"
            if 'percentage' in row['avo_net_revenue']:
                avo += f" ({row['avo_net_revenue']['percentage']}%)"
            elif 'note' in row['avo_net_revenue']:
                avo += f" ({row['avo_net_revenue']['note']})"

            lines.append(f"| {row['scenario']} | {user} | {deployer} | {avo} |")

    elif table["table_id"] == "4.1":
        lines.append("| Lock Duration | Multiplier | Tier Name | Strategic Rationale |")
        lines.append("|---------------|------------|-----------|---------------------|")
        for row in table["rows"]:
            days = row["lock_duration_days"]
            if days >= 365:
                duration = f"{days // 365} Year{'s' if days >= 730 else ''}" if days % 365 == 0 else f"{days} Days"
            else:
                duration = f"{days} Days"
            lines.append(f"| {duration} | {row['multiplier']}x | {row['tier_name']} | {row['strategic_rationale'][:80]}... |")

    lines.append("")
    return "\n".join(lines)


def render_subsection(subsection: dict, level: int = 3) -> str:
    prefix = "#" * level
    lines = [
        f"{prefix} {subsection.get('subsection_number', '')} {subsection['title']}".strip(),
        "",
    ]

    if "content" in subsection:
        lines.append(subsection["content"])
        lines.append("")

    # Handle various subsection-specific content
    if "solana_advantages" in subsection:
        for adv in subsection["solana_advantages"]:
            lines.append(f"- **{adv['feature']}:** {adv['description']}")
        lines.append("")

    if "market_context" in subsection:
        lines.append(subsection["market_context"])
        lines.append("")

    if "risk" in subsection:
        lines.append(f"**The Risk:** {subsection['risk']}")
        lines.append("")

    if "opportunity" in subsection:
        lines.append(f"**The Opportunity:** {subsection['opportunity']}")
        lines.append("")

    if "sub_subsections" in subsection:
        for sub in subsection["sub_subsections"]:
            lines.append(f"#### {sub['number']} {sub['title']}")
            lines.append("")
            if "content" in sub:
                lines.append(sub["content"])
                lines.append("")
            if "value_propositions" in sub:
                for vp in sub["value_propositions"]:
                    lines.append(f"- **{vp['name']}:** {vp['description']}")
                lines.append("")
            if "conclusion" in sub:
                lines.append(sub["conclusion"])
                lines.append("")
            if "comparison" in sub:
                for k, v in sub["comparison"].items():
                    lines.append(f"- **{k.replace('_', ' ').title()}:** {v}")
                lines.append("")
            if "user_protection_mechanisms" in sub:
                for mech in sub["user_protection_mechanisms"]:
                    lines.append(f"- **{mech['name']}:** {mech['description']}")
                    lines.append(f"  - *Purpose:* {mech['purpose']}")
                    lines.append(f"  - *Example:* \"{mech['example']}\"")
                lines.append("")

    if "scenarios" in subsection:
        for key, scenario in subsection["scenarios"].items():
            lines.append(f"#### {scenario['name']}")
            lines.append("")
            lines.append(scenario["description"])
            lines.append("")
            fs = scenario["fee_structure"]
            lines.append(f"- **Total Fee:** {fs.get('total_fee_percentage', fs.get('effective_fee_percentage'))}%")
            lines.append(f"- **Avo Share:** {fs['avo_share_percentage']}% ({fs['avo_share_of_volume']}% of volume)")
            lines.append(f"- **Deployer Share:** {fs['deployer_share_percentage']}% ({fs['deployer_share_of_volume']}% of volume)")
            if "user_discount_percentage" in fs:
                lines.append(f"- **User Discount:** {fs['user_discount_percentage']}%")
            lines.append("")
            if "analysis" in scenario:
                lines.append(f"*Analysis:* {scenario['analysis']}")
                lines.append("")

    if "implications" in subsection:
        for imp in subsection["implications"]:
            lines.append(f"**{imp['name']}:** {imp['description']}")
            if "breakdown" in imp:
                for k, v in imp["breakdown"].items():
                    lines.append(f"  - {k.replace('_', ' ').title()}: {v} bps")
            lines.append("")

    if "strategic_insight" in subsection:
        lines.append(f"*Strategic Insight:* {subsection['strategic_insight']}")
        lines.append("")

    if "rationale" in subsection:
        for r in subsection["rationale"]:
            lines.append(f"- **{r['reason']}:** {r['explanation']}")
        lines.append("")

    if "scenario_simulation" in subsection:
        sim = subsection["scenario_simulation"]
        lines.append("#### Scenario Simulation")
        lines.append("")
        lines.append("**Assumptions:**")
        lines.append(f"- Daily Volume: ${sim['assumptions']['daily_volume_usd']:,}")
        lines.append(f"- Traffic Mix: {sim['assumptions']['traffic_mix']['organic_percentage']}% Organic / {sim['assumptions']['traffic_mix']['referred_percentage']}% Referred")
        lines.append(f"- Total Daily Revenue: ${sim['assumptions']['net_daily_revenue']['total_daily_usd']:,}")
        lines.append(f"- Seeder Pool (30%): ${sim['assumptions']['seeder_pool']['daily_usd']:,}/day")
        lines.append("")

        for phase in sim["phases"]:
            lines.append(f"**Phase {phase['phase']}: {phase['name']}**")
            lines.append(f"- Total AVO Locked: {phase['total_avo_locked']:,}")
            lines.append(f"- Average Multiplier: {phase['average_multiplier']}x")
            lines.append(f"- APR: {phase['apr_percentage']}%")
            lines.append(f"- *Result:* {phase['result']}")
            lines.append("")

    if "cost_categories" in subsection:
        for cat in subsection["cost_categories"]:
            lines.append(f"- **{cat['category']}:** {cat['description']}")
        lines.append("")

    if "surplus_allocation" in subsection:
        sa = subsection["surplus_allocation"]
        lines.append(f"**Surplus Allocation:** {sa['percentage']}% to {sa['destination']}")
        lines.append(f"**Target:** {sa['target']}")
        lines.append("")

    if "strategic_importance" in subsection:
        for si in subsection["strategic_importance"]:
            lines.append(f"- **{si['benefit']}:** {si['description']}")
        lines.append("")

    if "execution_strategy" in subsection:
        es = subsection["execution_strategy"]
        lines.append(f"**Execution Strategy ({es['name']}):** {es['description']}")
        lines.append("")

    if "mechanism" in subsection:
        mech = subsection["mechanism"]
        lines.append(f"**Mechanism:** {mech['action']}")
        lines.append(f"**Trigger:** {mech['trigger']}")
        lines.append("")

    if "economic_impact" in subsection:
        lines.append(f"**Economic Impact:** {subsection['economic_impact']}")
        lines.append("")

    if "implementation" in subsection:
        impl = subsection["implementation"]
        if "framework" in impl:
            lines.append(f"**Framework:** {impl['framework']} + {impl['governance']}")
            lines.append("")
            lines.append("**Configuration:**")
            lines.append(f"- `min_lockup`: {impl['configuration']['min_lockup_days']} days")
            lines.append(f"- `max_lockup`: {impl['configuration']['max_lockup_days']} days")
            lines.append(f"- `voting_power_multiplier`: {impl['configuration']['voting_power_multiplier']['range']['min']}x to {impl['configuration']['voting_power_multiplier']['range']['max']}x ({impl['configuration']['voting_power_multiplier']['type']})")
            lines.append("")
            lines.append("**Reward Distribution:**")
            lines.append(f"- Method: {impl['reward_distribution']['method']}")
            lines.append(f"- Snapshot Frequency: {impl['reward_distribution']['snapshot_frequency']}")
            lines.append(f"- {impl['reward_distribution']['description']}")
            lines.append(f"- *Status: {impl['reward_distribution']['status']}*")
            lines.append("")

    return "\n".join(lines)


def render_section(section: dict) -> str:
    lines = [
        f"## {section['section_number']}. {section['title']}",
        "",
    ]

    if "overview" in section:
        lines.append(section["overview"])
        lines.append("")

    if "content" in section:
        lines.append(section["content"])
        lines.append("")

    if "treasury_wallet" in section:
        lines.append(f"**Treasury Wallet:** `{section['treasury_wallet']}`")
        lines.append("")

    if "subsections" in section:
        for subsection in section["subsections"]:
            lines.append(render_subsection(subsection))

    if "tables" in section:
        for table in section["tables"]:
            lines.append(render_table(table))

    if "value_propositions" in section:
        vp = section["value_propositions"]
        lines.append("### Value Propositions")
        lines.append("")
        lines.append(f"- **For Deployers:** {vp['for_deployers']['benefit']} - {vp['for_deployers']['outcome']}")
        lines.append(f"- **For Users:** {vp['for_users']['benefit']}")
        lines.append(f"- **For Holders:** {vp['for_holders']['benefit']}")
        lines.append("")

    if "final_statement" in section:
        lines.append(f"*{section['final_statement']}*")
        lines.append("")

    return "\n".join(lines)


def render_parameters(params: dict) -> str:
    lines = [
        "## Appendix: Key Parameters",
        "",
        "### Fee Structure",
        "",
        f"| Parameter | Value |",
        f"|-----------|-------|",
        f"| Base Swap Fee | {params['fee_structure']['base_swap_fee_percentage']}% |",
        f"| Referral Discount | {params['fee_structure']['referral_discount_percentage']}% |",
        f"| Effective Referred Fee | {params['fee_structure']['effective_referred_fee_percentage']}% |",
        "",
        "### Revenue Split",
        "",
        "| Scenario | Avo Share | Deployer Share |",
        "|----------|-----------|----------------|",
        f"| Organic | {params['revenue_split']['organic']['avo_share_percentage']}% | {params['revenue_split']['organic']['deployer_share_percentage']}% |",
        f"| Referred | {params['revenue_split']['referred']['avo_share_percentage']}% | {params['revenue_split']['referred']['deployer_share_percentage']}% |",
        "",
        "### Treasury Allocation",
        "",
        f"- Seeder Pool: {params['treasury_allocation']['seeder_pool_percentage']}%",
        f"- Operations: {params['treasury_allocation']['operations_percentage']}%",
        "",
        "### Seeder Multipliers",
        "",
        "| Lock Duration | Multiplier |",
        "|---------------|------------|",
    ]

    for m in params["seeder_multipliers"]:
        days = m["days"]
        if days >= 365:
            duration = f"{days} days ({days // 365} year{'s' if days >= 730 else ''})"
        else:
            duration = f"{days} days"
        lines.append(f"| {duration} | {m['multiplier']}x |")

    lines.append("")
    lines.append("### Recapture Strategy")
    lines.append("")
    lines.append(f"- Target Supply: {params['recapture_strategy']['target_supply_percentage']}%")
    lines.append(f"- Post-Target Action: {params['recapture_strategy']['post_target_action'].capitalize()}")
    lines.append("")

    return "\n".join(lines)


def render_references(refs: dict) -> str:
    lines = [
        "## References",
        "",
        "### Works Cited",
        "",
    ]

    for cite in refs["works_cited"]:
        lines.append(f"{cite['number']}. [{cite['title']}]({cite['url']}) - Accessed {cite['accessed']}")

    lines.append("")
    return "\n".join(lines)


def render_blueprint(blueprint: dict) -> str:
    parts = [
        render_metadata(blueprint["metadata"]),
        "---",
        "",
        render_executive_summary(blueprint["executive_summary"]),
    ]

    for section in blueprint["sections"]:
        parts.append(render_section(section))

    parts.append(render_parameters(blueprint["parameters"]))
    parts.append(render_references(blueprint["references"]))

    # Footer
    parts.append("---")
    parts.append(f"*Generated from `avonomics-blueprint.json` on {datetime.now().strftime('%Y-%m-%d %H:%M')}*")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="Render Avonomics blueprint JSON to Markdown")
    parser.add_argument("--input", "-i", default="avonomics-blueprint.json", help="Input JSON file")
    parser.add_argument("--output", "-o", default="AVONOMICS.md", help="Output Markdown file")
    args = parser.parse_args()

    blueprint = load_blueprint(args.input)
    markdown = render_blueprint(blueprint)

    with open(args.output, "w") as f:
        f.write(markdown)

    print(f"Rendered {args.input} -> {args.output}")


if __name__ == "__main__":
    main()
