import * as cheerio from 'cheerio';

import type { APIGatewayProxyHandler } from 'aws-lambda';
import fetch from 'node-fetch';

export const handler: APIGatewayProxyHandler = async (event) => {
  try {
    const parsed = JSON.parse(event.body || '{}');
    let url: string | undefined;
    if ((event as any).url) {
      url = (event as any).url;
    } else if (event.body) {
      try {
        const body = JSON.parse(event.body);
        url = body.url;
      } catch {
        return {
          statusCode: 400,
          body: JSON.stringify({ error: 'Invalid JSON body' }),
        };
      }
    } else if ((event as any).url) {
      url = (event as any).url;
    }
    if (!url) {
      return {
        statusCode: 400,
        body: JSON.stringify({ error: "Missing 'url' field in JSON body" }),
      };
    }

    if (!/^https?:\/\//i.test(url)) {
      url = `https://${url}`;
    }

    const res = await fetch(url, {
      headers: {
        'User-Agent':
          'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        Accept: 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9',
      },
    });

    const html = await res.text();
    const $ = cheerio.load(html);

    // Remove script, style, noscript, and hidden elements
    $('script, style, noscript, iframe, link, meta').remove();
    $(
      '[aria-hidden="true"], [style*="display:none"], [style*="visibility:hidden"]'
    ).remove();

    const title = $('title').text().trim();
    const description =
      $('meta[name="description"]').attr('content') ||
      $('meta[property="og:description"]').attr('content') ||
      '';

    const headings = $('h1, h2, h3')
      .map((_, el) => $(el).text().trim())
      .get()
      .filter(Boolean)
      .join(' · ');

    const bodyText = $('body').text().replace(/\s+/g, ' ').trim();

    const combinedText = [title, description, headings, bodyText]
      .filter(Boolean)
      .join(' — ')
      .slice(0, 5000);

    return {
      statusCode: 200,
      body: JSON.stringify({ text: combinedText }),
    };
  } catch (err) {
    return {
      statusCode: 500,
      body: JSON.stringify({ error: (err as Error).message }),
    };
  }
};
