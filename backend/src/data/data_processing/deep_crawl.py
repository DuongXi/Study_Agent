import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

# Thu thập dữ liệu từ website
async def so_tay_crawl():
    browser_conf = BrowserConfig(
        headless=False
    )
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        js_code=["""(async () => {
        await new Promise(r => setTimeout(r, 15000));
    })();"""]
    )

    async with AsyncWebCrawler(config=browser_conf) as crawler:
        result = await crawler.arun(
            url="https://sv-ctt.hust.edu.vn/#/so-tay-sv",
            config=run_conf
        )
        if result and result.success:
            print("Thu thập thành công!")
            for link in result.links['internal']:
                if "so-tay-sv/" in link['href']:
                    result = await crawler.arun(
                        url=link['href'],
                        config=run_conf
                    )
                    with open(f"{link['href'].split('/')[-1].replace('-', '_')}.txt", "w", encoding="utf-8") as f:
                        f.write("## " + result.markdown.split("##")[1])
                    print(f"Links: {link['href']}")
            print(f"URL đã thu thập: {result.url}")
        else:
            print(f"Thu thập thất bại: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(so_tay_crawl())