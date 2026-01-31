# Headless Commerce Migration Guide

Rule #1:
All checkout API requests in the headless system MUST include the header:
X-SDK-Version.
If this header is missing, the checkout button will appear to work, but the payment will never start.

Rule #2:
Headless webhooks use Secret Key "B".
Old hosted webhooks used Secret Key "A".
If a merchant still uses Secret Key A, webhooks will fail with 401 Unauthorized.

Rule #3:
After migration, old hosted checkout URLs no longer work.
Merchants must update their frontend to use the new Headless Checkout API.

Rule #4:
The headless API has stricter rate limits.
Too many requests can cause temporary 429 or 500 errors.
