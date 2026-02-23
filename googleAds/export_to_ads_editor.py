#!/usr/bin/env python3
"""
Convert ads_data.json to Google Ads Editor CSV format.
"""

import json
import csv
from datetime import datetime

# All columns in Google Ads Editor export format
COLUMNS = [
    "Campaign", "Labels", "Campaign Type", "Networks", "Budget", "Budget type",
    "Standard conversion goals", "Customer acquisition", "Languages", "Bid Strategy Type",
    "Bid Strategy Name", "Enhanced CPC", "Target CPA", "Ad location", "Target impression share",
    "Maximum CPC bid limit", "Start Date", "End Date", "Broad match keywords", "Ad Schedule",
    "Ad rotation", "Content exclusions", "Targeting method", "Exclusion method", "Audience targeting",
    "Flexible Reach", "Text asset automation", "Final URL expansion", "Image enhancement",
    "Image generation", "Image extraction", "Video enhancement", "Brand guidelines",
    "Brand business name", "Ad Group", "Max CPC", "Max CPM", "Max CPV", "Target CPV",
    "Percent CPC", "Target CPM", "Target ROAS", "Desktop Bid Modifier", "Mobile Bid Modifier",
    "Tablet Bid Modifier", "TV Screen Bid Modifier", "Display Network Custom Bid Type",
    "Optimized targeting", "Strict age and gender targeting", "Ad Group Type", "Audience name",
    "Age demographic", "Gender demographic", "Income demographic", "Parental status demographic",
    "Remarketing audience segments", "Interest categories", "Life events", "Custom audience segments",
    "Detailed demographics", "Remarketing audience exclusions", "Tracking template", "Final URL suffix",
    "Custom parameters", "Asset Group", "Headline 1", "Headline 2", "Headline 3", "Headline 4",
    "Headline 5", "Headline 6", "Headline 7", "Headline 8", "Headline 9", "Headline 10",
    "Headline 11", "Headline 12", "Headline 13", "Headline 14", "Headline 15",
    "Long headline 1", "Long headline 2", "Long headline 3", "Long headline 4", "Long headline 5",
    "Description 1", "Description 2", "Description 3", "Description 4", "Description 5",
    "Call to action", "Business name", "Video ID 1", "Video ID 2", "Video ID 3", "Video ID 4",
    "Video ID 5", "Path 1", "Path 2", "Final URL", "Final mobile URL", "Audience signal", "ID",
    "Audience segment", "Bid Modifier", "Age", "Criterion Type", "Household income", "Location",
    "Reach", "Location groups", "Radius", "Unit", "Account keyword type", "Keyword",
    "First page bid", "Top of page bid", "First position bid", "Quality score",
    "Landing page experience", "Expected CTR", "Ad relevance", "Image Size", "Upgraded extension",
    "Link source", "Search theme", "Ad type", "Headline 1 position", "Headline 2 position",
    "Headline 3 position", "Headline 4 position", "Headline 5 position", "Headline 6 position",
    "Headline 7 position", "Headline 8 position", "Headline 9 position", "Headline 10 position",
    "Headline 11 position", "Headline 12 position", "Headline 13 position", "Headline 14 position",
    "Headline 15 position", "Description 1 position", "Description 2 position",
    "Description 3 position", "Description 4 position", "Shared set name", "Shared set type",
    "Keyword count", "Link Text", "Description Line 1", "Description Line 2", "Source",
    "Phone Number", "Country of Phone", "Conversion Action", "Campaign Status", "Ad Group Status",
    "Asset Group Status", "Status", "Approval Status", "Ad strength", "Comment"
]


def create_empty_row():
    """Create an empty row dict with all columns."""
    return {col: "" for col in COLUMNS}


def create_campaign_row(campaign):
    """Create a campaign-level row."""
    row = create_empty_row()
    row["Campaign"] = campaign["name"]
    row["Campaign Type"] = campaign.get("type", "Search")
    row["Networks"] = campaign.get("networks", "Google search")
    row["Budget"] = campaign.get("budget", "")
    row["Budget type"] = campaign.get("budget_type", "Daily")
    row["Languages"] = campaign.get("languages", "en")

    # Bid strategy
    bid_strategy = campaign.get("bid_strategy", "")
    if bid_strategy == "Target impression share":
        row["Bid Strategy Type"] = "Target impression share"
        row["Target impression share"] = campaign.get("target_impression_share", "")
        row["Maximum CPC bid limit"] = campaign.get("max_cpc_limit", "")
        row["Ad location"] = "Top of results page"
    elif bid_strategy == "Manual CPC":
        row["Bid Strategy Type"] = "Manual CPC"
        row["Enhanced CPC"] = "Disabled"
    elif bid_strategy == "Maximize clicks":
        row["Bid Strategy Type"] = "Maximize clicks"
    else:
        row["Bid Strategy Type"] = bid_strategy

    row["Start Date"] = campaign.get("start_date", "")
    row["Ad rotation"] = "Rotate indefinitely"
    row["Targeting method"] = "Location of presence"
    row["Exclusion method"] = "Location of presence"
    row["Audience targeting"] = "Audience segments"
    row["Flexible Reach"] = "Audience segments"
    row["Text asset automation"] = "Disabled"
    row["Final URL expansion"] = "Disabled"
    row["Image enhancement"] = "Disabled"
    row["Image generation"] = "Disabled"
    row["Image extraction"] = "Disabled"
    row["Video enhancement"] = "Disabled"
    row["Brand guidelines"] = "Disabled"
    row["Campaign Status"] = campaign.get("status", "Enabled")
    row["Comment"] = campaign.get("comment", "")

    return row


def create_ad_group_row(campaign, ad_group):
    """Create an ad group-level row."""
    row = create_empty_row()
    row["Campaign"] = campaign["name"]
    row["Languages"] = "All"
    row["Ad Group"] = ad_group["name"]
    row["Max CPC"] = ad_group.get("max_cpc", "0.01")
    row["Max CPM"] = "0.01"
    row["Max CPV"] = ""
    row["Target CPV"] = "0.01"
    row["Percent CPC"] = ""
    row["Target CPM"] = "0.01"
    row["Optimized targeting"] = "Disabled"
    row["Strict age and gender targeting"] = "Disabled"
    row["Ad Group Type"] = "Standard"
    row["Audience targeting"] = "Audience segments"
    row["Flexible Reach"] = "Audience segments;Genders;Ages;Parental status;Household incomes"
    row["Display Network Custom Bid Type"] = "None"
    row["Ad rotation"] = "Optimize"
    row["Campaign Status"] = campaign.get("status", "Enabled")
    row["Ad Group Status"] = ad_group.get("status", "Enabled")

    return row


def create_keyword_row(campaign, ad_group, keyword):
    """Create a keyword row."""
    row = create_empty_row()
    row["Campaign"] = campaign["name"]
    row["Ad Group"] = ad_group["name"]

    # Handle match type
    match_type = keyword.get("match_type", "Phrase")
    if match_type.startswith("Negative"):
        row["Criterion Type"] = match_type
    else:
        row["Criterion Type"] = match_type

    row["Keyword"] = keyword.get("keyword", "")
    row["First page bid"] = "0.00"
    row["Top of page bid"] = "0.00"
    row["First position bid"] = "0.00"
    row["Campaign Status"] = campaign.get("status", "Enabled")
    row["Ad Group Status"] = ad_group.get("status", "Enabled")
    row["Status"] = keyword.get("status", "Enabled")

    return row


def create_ad_row(campaign, ad_group, ad):
    """Create a responsive search ad row."""
    row = create_empty_row()
    row["Campaign"] = campaign["name"]
    row["Ad Group"] = ad_group["name"]

    # Headlines (up to 15)
    headlines = ad.get("headlines", [])
    for i, headline in enumerate(headlines[:15], 1):
        text = headline.get("text", "") if isinstance(headline, dict) else headline
        row[f"Headline {i}"] = text

        # Position
        position = headline.get("position", "") if isinstance(headline, dict) else ""
        if position:
            row[f"Headline {i} position"] = position
        else:
            row[f"Headline {i} position"] = " -"

    # Fill remaining headline positions with " -"
    for i in range(len(headlines) + 1, 16):
        row[f"Headline {i} position"] = ""

    # Descriptions (up to 4)
    descriptions = ad.get("descriptions", [])
    for i, desc in enumerate(descriptions[:4], 1):
        text = desc.get("text", "") if isinstance(desc, dict) else desc
        row[f"Description {i}"] = text

        position = desc.get("position", "") if isinstance(desc, dict) else ""
        if position:
            row[f"Description {i} position"] = position
        else:
            row[f"Description {i} position"] = " -"

    row["Final URL"] = ad.get("final_url", "")
    row["Path 1"] = ad.get("path1", "")
    row["Path 2"] = ad.get("path2", "")
    row["Ad type"] = "Responsive search ad"
    row["Campaign Status"] = campaign.get("status", "Enabled")
    row["Ad Group Status"] = ad_group.get("status", "Enabled")
    row["Status"] = ad.get("status", "Enabled")

    return row


def create_location_row(campaign, location):
    """Create a location targeting row."""
    row = create_empty_row()
    row["Campaign"] = campaign["name"]
    row["Location"] = location
    row["Campaign Status"] = campaign.get("status", "Enabled")
    row["Status"] = "Enabled"

    return row


def convert_to_csv(json_path, output_path):
    """Convert ads_data.json to Google Ads Editor CSV format."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    rows = []

    for campaign in data.get("campaigns", []):
        # Campaign row
        rows.append(create_campaign_row(campaign))

        # Location rows
        for location in campaign.get("locations", []):
            rows.append(create_location_row(campaign, location))

        # Ad groups
        for ad_group in campaign.get("ad_groups", []):
            # Ad group row
            rows.append(create_ad_group_row(campaign, ad_group))

            # Keywords
            for keyword in ad_group.get("keywords", []):
                rows.append(create_keyword_row(campaign, ad_group, keyword))

            # Negative keywords
            for neg_keyword in ad_group.get("negative_keywords", []):
                rows.append(create_keyword_row(campaign, ad_group, neg_keyword))

            # Ads
            for ad in ad_group.get("ads", []):
                rows.append(create_ad_row(campaign, ad_group, ad))

    # Write CSV with UTF-16 encoding (Google Ads Editor format)
    with open(output_path, 'w', newline='', encoding='utf-16') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} rows to {output_path}")

    # Also create a UTF-8 version for easier viewing
    utf8_path = output_path.replace('.csv', '_utf8.csv')
    with open(utf8_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, delimiter='\t')
        writer.writeheader()
        writer.writerows(rows)

    print(f"Also created UTF-8 version at {utf8_path}")

    return len(rows)


if __name__ == "__main__":
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"Fowler_Homes_Ads_Export_{timestamp}.csv"

    convert_to_csv("ads_data.json", output_file)
