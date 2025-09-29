import os, json, re, time
from tqdm import tqdm
from readability import Document
from bs4 import BeautifulSoup
from textwrap import wrap
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
import random

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from bs4.element import Tag
# ---------- Config ----------
URLS = [ "https://spec-india.medium.com/erp-for-manufacturing-all-you-need-to-know-6af5f850eea2", "https://medium.com/1erp/understanding-erp-systems-how-they-transform-business-operations-9b9ac543fb5a", "https://hrmuwanika.medium.com/what-is-enterprise-resource-planning-erp-7bfa1f90a0e7", "https://medium.com/1erp/what-is-erp-enterprise-resource-planning-software-87d9c3b5a07f", "https://medium.com/@robocodercorporation/what-is-the-most-important-erp-module-e727b73d3a52", "https://medium.com/@LataTewari/understanding-the-sales-cycle-and-its-different-stages-a-comprehensive-guide-247b5198441e", "https://medium.com/growthzilla/2-2-the-customer-lifecycle-6cca8d001f9f", "https://mooninvoice.medium.com/gst-inclusive-and-exclusive-definition-difference-calculation-dc6d9f4f255", "https://annisarah.medium.com/understanding-primary-and-secondary-sales-and-how-it-balances-demand-and-supply-b97648ba7e72", "https://medium.com/@mprakash7193/sales-analytics-case-study-unveiling-the-power-of-sales-analysis-dashboards-cb08f9cecd1b", "https://medium.com/@okenitap/technical-report-sales-trends-and-insights-72446b9c5d50", "https://medium.com/@tim5tsai/recursive-bom-with-routing-in-manufacturing-d2c8685314c0", "https://medium.com/@log.cryotos/what-is-work-order-six-step-guide-to-create-an-effective-work-orders-c0fb26dafb1d", "https://medium.com/@amb39305/understanding-mrp-material-requirements-planning-methodology-a-comprehensive-guide-66c0e9d2e362", "https://medium.com/@cionlabs/top-10-mrp-material-requirement-planning-that-you-should-consider-before-making-a-decision-8db51a8338e5", "https://medium.com/@ashwini.mogal18/real-time-monitoring-in-computer-integrated-manufacturing-caa748e131c3", "https://medium.com/@michaeljamesryan/optimal-use-of-wip-limits-ea2de91cfb72", "https://medium.com/agileinsider/the-benefits-of-working-with-few-items-at-a-time-b6b0c1a76bfc", "https://medium.com/agoda-engineering/a-deep-dive-into-agodas-generic-reconciliation-platform-06cab9a98145", "https://medium.com/@satyanjoyroy/a-deep-dive-into-productivity-utilisation-and-resource-overhead-reconciliation-in-the-intricate-3873201e5fc0", "https://medium.com/@BlueflameLabs/streamlining-inventory-and-purchase-requisition-processes-with-rootstock-b641c64b12ee", "https://medium.com/nanonets/understanding-the-process-of-a-requisition-order-a-guide-909837270952", "https://medium.com/@hubler/what-is-purchase-order-cycle-meaning-steps-why-automate-it-f5eca5b63896", "https://ecommerce-guru.medium.com/goods-receipt-note-grn-721889495d0b", "https://medium.com/deskera-engineering/what-are-debit-notes-credit-notes-d0c9744f97a9", "https://medium.com/@srekatpure/unlocking-the-power-of-procurement-analytics-for-supply-chain-digitization-d6a86e3f40a3", "https://medium.com/@qualio/quality-assurance-vs-quality-control-explained-5-key-differences-e73297a3a1db", "https://medium.com/data-science-collective/data-quality-checks-dqcs-a-guide-for-data-engineers-dd43cd331aa4", "https://careerist.medium.com/the-qa-process-a-beginners-guide-to-the-main-stages-steps-and-tools-of-quality-assurance-1fec422b8d5f", "https://medium.com/@TWB_BI/starting-a-data-quality-checklist-2d500e97ab5c", "https://medium.com/@vivektiwari2212/project-quality-management-75632afec454", "https://medium.com/@vaniukov.s/online-payment-gateway-integration-a-thorough-guide-993c794b65b9", "https://medium.com/@erpinformation/a-guide-to-manufacturing-execution-system-mes-50966a6d3c3d", "https://medium.com/@philips202308/what-is-enterprise-resource-planning-erp-the-erp-software-guide-6f0fe345fc78", "https://mtouqeer.medium.com/understanding-the-chart-of-accounts-your-roadmap-to-organized-financial-tracking-871aa0daf468", "https://medium.com/hitachisolutions-braintrust/chart-of-accounts-best-practice-tips-a-dynamics-consultants-perspective-30cf26d1d428", "https://medium.com/@lianabeloliver/how-the-chart-of-accounts-can-help-you-and-why-you-should-care-cd2263d30d35", "https://medium.com/@chirag.dave/payment-processing-how-does-it-work-8efef610e623", "https://medium.com/nanonets/b2b-payment-automation-guide-how-to-implement-and-maximize-the-benefits-f9311ebbf17", "https://medium.com/@siddiquiahmed/payments-ecosystem-overview-26f55f19f3c6", "https://medium.com/@shaoorwarraich/inventory-costing-methods-explained-lifo-fifo-and-weighted-average-2eda62181219", "https://muzamilaziz.medium.com/what-is-fifo-method-5c72c86aa2b1", "https://medium.com/@santosobudi.aris/mastering-cash-flow-statements-your-ultimate-guide-to-accurate-financial-reporting-part-1-a6cc6dd5770b", "https://medium.com/data-science/guide-to-financial-statement-analysis-for-beginners-835d551b8e29", "https://medium.com/@nayan.j.paul/how-to-implement-end-to-end-financial-analysis-for-a-firm-using-large-language-models-llms-and-e59dde84e6fe", "https://medium.com/@marketing-cashflo/tds-and-tcs-under-gst-a-detailed-guide-3a7a1f7a895d", "https://medium.com/@odooerpsoftware/what-makes-odoo-the-best-erp-for-manufacturing-businesses-322895720b22", "https://abhilashbhatia89.medium.com/erp-solutions-for-manufacturing-industries-in-india-1dad0da44bf9", "https://medium.com/@acgncr/explore-erp-scope-in-managing-manufacturing-processes-in-manufacturing-industry-3cdf1847a233", "https://www.syspro.com/blog/erp-for-manufacturing/future-proof-your-manufacturing-business-with-erp/", "https://www.winman.com/blog/using-erp-for-integrated-sales-management" ]

JSON_OUTPUT_FILE = "data/sales_articles.json"
PDF_OUTPUT_DIR = "data"
os.makedirs(PDF_OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.dirname(JSON_OUTPUT_FILE), exist_ok=True)

# ---------- PDF Generator ----------
def save_clean_pdf(title, author, content, path):
    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    x = 2 * cm
    y = height - 2 * cm
    line_height = 14

    def draw_wrapped_text(text, max_width=90):
        nonlocal y
        for line in wrap(text, max_width):
            c.drawString(x, y, line)
            y -= line_height
            if y < 2 * cm:
                c.showPage()
                y = height - 2 * cm

    c.setFont("Helvetica-Bold", 14)
    draw_wrapped_text(title)
    y -= 10
    c.setFont("Helvetica-Oblique", 11)
    draw_wrapped_text(f"By {author}")
    y -= 20
    c.setFont("Helvetica", 11)
    draw_wrapped_text(content)
    c.save()

# ---------- Selenium Setup ----------
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0")

    # Use your manually downloaded ChromeDriver
    chromedriver_path = "D:/chromedriver-win64/chromedriver.exe"
    service = Service(executable_path=chromedriver_path)

    return webdriver.Chrome(service=service, options=chrome_options)

# ---------- Scraper ----------
def scrape_articles():
    driver = init_driver()
    articles = []
    print("🚀 Scraping and saving articles...")

    for url in tqdm(URLS):
        try:
            driver.get(url)
            time.sleep(5)  # Wait for JS to load page

            # Scroll to bottom slowly to trigger lazy-loading
            for _ in range(3):
                driver.execute_script("window.scrollBy(0, document.body.scrollHeight/3);")
                time.sleep(2)

            html = driver.page_source

            doc = Document(html)
            title = doc.title()
            summary_html = doc.summary()
            soup = BeautifulSoup(summary_html, "html.parser")

            content_tags = soup.find_all(["h1", "h2", "p", "li"])
            content = "\n".join(tag.get_text(strip=True) for tag in content_tags if tag.get_text(strip=True))

            if not content or "Verify you are human" in content:
                raise Exception("Blocked or empty content")

            soup_all = BeautifulSoup(html, "html.parser")
            author = "Unknown"
            meta_author = soup_all.find("meta", attrs={"name": "author"})

            if isinstance(meta_author, Tag) and meta_author.has_attr("content"):
                author = meta_author["content"]

            clean_title = re.sub(r'[\\/*?:"<>|]', "", title[:50]).replace(" ", "_")
            pdf_path = os.path.join(PDF_OUTPUT_DIR, f"{clean_title}.pdf")

            articles.append({
                "url": url,
                "title": title,
                "author": author,
                "content": content
            })

            save_clean_pdf(title, author, content, pdf_path)
            print(f"📄 PDF saved: {pdf_path}")

            # Randomized delay to avoid triggering bot protection
            time.sleep(random.randint(4, 8))

        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")

    driver.quit()

    with open(JSON_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    print(f"\n✅ JSON saved to: {JSON_OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_articles()
