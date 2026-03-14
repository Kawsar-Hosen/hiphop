import asyncio
import random
from datetime import datetime, timedelta, timezone
from playwright.async_api import async_playwright
from config import *

groups = {}


async def login(page):

    await page.goto("https://www.instagram.com/accounts/login/")

    await page.fill('input[name="username"]', USERNAME)
    await page.fill('input[name="password"]', PASSWORD)

    await page.click("button[type=submit]")

    await page.wait_for_selector("nav")

    print("✅ Login success")


async def send_message(page, text):

    box = await page.query_selector("textarea")

    if box:
        await box.fill(text)
        await box.press("Enter")

        print("📨 Sent:", text)


async def get_groups(page):

    await page.goto("https://www.instagram.com/direct/inbox/")

    await page.wait_for_timeout(5000)

    links = await page.query_selector_all('a[href*="/direct/t/"]')

    for l in links:

        href = await l.get_attribute("href")

        if href:

            thread = href.split("/")[-2]

            groups[thread] = {

                "last": datetime.now(timezone.utc),

                "users": []
            }

    print("📊 Groups:", len(groups))


async def monitor_group(context, thread):

    page = await context.new_page()

    await page.goto(f"https://www.instagram.com/direct/t/{thread}/")

    print("👀 Monitoring group:", thread)

    while True:

        now = datetime.now(timezone.utc)

        if now - groups[thread]["last"] > timedelta(hours=INACTIVE_HOURS):

            users = groups[thread]["users"]

            if users:

                selected = random.sample(users, min(PING_USERS, len(users)))

                mentions = " ".join([f"@{u}" for u in selected])

                await send_message(page, PING_MSG.format(mentions=mentions))

                groups[thread]["last"] = datetime.now(timezone.utc)

        await asyncio.sleep(60)


async def main():

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)

        context = await browser.new_context()

        page = await context.new_page()

        await login(page)

        await get_groups(page)

        tasks = []

        for g in groups:

            tasks.append(monitor_group(context, g))

        await asyncio.gather(*tasks)


asyncio.run(main())
