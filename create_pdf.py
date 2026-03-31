import img2pdf
import os

screenshots = [
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_01_homepage_1774920870568.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_02_about_1774921068941.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_03_vision_mission_1774921086751.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_04_org_structure_1774921124327.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_05_gad_committee_1774921141942.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_06_contact_1774921163350.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_02_knowledge_products_1774920898788.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_03_brochures_1774920922603.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_04_livelihood_program_feeds_1774920952069.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_05_news_archive_1774920982016.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_06_calendar_1774921004622.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_07_projects_1774921181716.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_08_projects_archive_1774921200917.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_09_reports_1774921221740.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_10_lbp_forms_1774921242827.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\screenshot_11_estado_ni_juana_1774921267020.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\privacy_policy_screenshot_1774921334210.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\terms_and_conditions_screenshot_1774921357691.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\developers_team_screenshot_1774921387366.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_dashboard_1774921768042.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_features_1774921784281.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_policies_1774921795231.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_events_full_1774921863308.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_projects_1774921887633.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_knowledge_1774921906459.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_brochures_1774921942867.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_livelihood_feeds_1774921970950.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_org_structure_1774921989669.png",
    r"C:\Users\Administrator\.gemini\antigravity\brain\f5098058-9fc0-4796-9455-ea85e2bab3a8\admin_committee_1774922011748.png"
]

# Verify files exist
valid_screenshots = [s for s in screenshots if os.path.exists(s)]
print(f"Found {len(valid_screenshots)} out of {len(screenshots)} screenshots.")

output_pdf = "GAD_Website_Screenshots.pdf"
with open(output_pdf, "wb") as f:
    f.write(img2pdf.convert(valid_screenshots))

print(f"PDF created successfully: {output_pdf}")
