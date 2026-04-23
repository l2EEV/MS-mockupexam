const { chromium } = require('playwright');
const fs = require('fs');

const STAGING_URL = 'https://ms-mockupexam-puarxm166-kawins-projects-8ff2ed09.vercel.app';

async function diagnose() {
  console.log('\n' + '='.repeat(60));
  console.log('PLAYWRIGHT DIAGNOSTIC TEST');
  console.log('URL: ' + STAGING_URL);
  console.log('='.repeat(60) + '\n');

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    console.log('📡 Navigating to page...');
    await page.goto(STAGING_URL, { waitUntil: 'networkidle' });
    console.log('✅ Page navigation complete\n');

    // Check page title
    const title = await page.title();
    console.log(`📋 Page title: "${title}"\n`);

    // Wait a bit and check for console errors
    await page.waitForTimeout(2000);

    console.log('🔍 Checking for console errors/messages...');
    const consoleLogs = [];
    page.on('console', msg => {
      consoleLogs.push(`[${msg.type()}] ${msg.text()}`);
    });
    page.on('pageerror', err => {
      consoleLogs.push(`[ERROR] ${err.message}`);
    });

    // Get page HTML
    const htmlContent = await page.content();
    console.log(`📄 Page HTML size: ${htmlContent.length} characters\n`);

    // Check for login screen class
    const hasLoginScreenClass = htmlContent.includes('class="login-screen');
    console.log(`✓ Has "login-screen" class in HTML: ${hasLoginScreenClass}`);

    // Check for email input
    const hasEmailInput = htmlContent.includes('type="email"');
    console.log(`✓ Has email input in HTML: ${hasEmailInput}\n`);

    // Now try to find elements via Playwright selectors
    console.log('🎯 Testing Playwright selectors...\n');

    const selectors = [
      { name: '.login-screen', desc: 'Login screen div' },
      { name: 'input[type="email"]', desc: 'Email input' },
      { name: '#getCodeBtn', desc: 'Get Code button' },
      { name: '.login-screen.active', desc: 'Active login screen' },
      { name: 'body', desc: 'Body element' },
      { name: 'div', desc: 'Any div' },
    ];

    for (const sel of selectors) {
      try {
        const visible = await page.isVisible(sel.name);
        const count = await page.locator(sel.name).count();
        console.log(`${visible ? '✅' : '❌'} ${sel.desc}`);
        console.log(`   Selector: "${sel.name}"`);
        console.log(`   Visible: ${visible}, Count: ${count}\n`);
      } catch (e) {
        console.log(`❌ ${sel.desc}`);
        console.log(`   Selector: "${sel.name}"`);
        console.log(`   Error: ${e.message}\n`);
      }
    }

    // Take screenshot
    console.log('📸 Taking screenshot of page as seen by Playwright...');
    await page.screenshot({ path: './diagnostic-screenshot.png' });
    console.log('✅ Screenshot saved: diagnostic-screenshot.png\n');

    // Try to get visible text
    console.log('📝 Visible text on page:');
    const bodyText = await page.textContent('body');
    if (bodyText && bodyText.length > 0) {
      const preview = bodyText.substring(0, 200).replace(/\n/g, ' ');
      console.log(`   "${preview}..."\n`);
    } else {
      console.log('   (No visible text found)\n');
    }

    // Check computed styles of login screen
    console.log('🎨 Checking CSS of .login-screen element...');
    const loginScreenStyles = await page.evaluate(() => {
      const el = document.querySelector('.login-screen');
      if (!el) return 'Element not found in DOM';
      const styles = window.getComputedStyle(el);
      return {
        display: styles.display,
        visibility: styles.visibility,
        opacity: styles.opacity,
        position: styles.position,
        zIndex: styles.zIndex,
      };
    });
    console.log(JSON.stringify(loginScreenStyles, null, 2));

    // Check if JavaScript executed
    console.log('\n✅ Checking if page JavaScript executed...');
    const jsCheck = await page.evaluate(() => {
      return {
        hasWindow: typeof window !== 'undefined',
        hasDocument: typeof document !== 'undefined',
        bodyExists: document.body !== null,
        loginScreenExists: document.querySelector('.login-screen') !== null,
        emailInputExists: document.querySelector('input[type="email"]') !== null,
      };
    });
    console.log(JSON.stringify(jsCheck, null, 2));

  } catch (e) {
    console.error('❌ Diagnostic error:', e.message);
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(60));
  console.log('DIAGNOSTIC COMPLETE');
  console.log('='.repeat(60) + '\n');
}

diagnose();
