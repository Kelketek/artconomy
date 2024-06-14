# Artconomy

Artconomy is a platform for making art commissions safer and easier. We provide escrow services as well as a custom workflow to make managing commissions simpler. You can visit us at [Artconomy.com](https://artconomy.com/)!

## How to run this code

The codebase assumes you're running Ubuntu Linux. It should be trivially easy to add support for any other linux flavor (small modifications to the Makefile will do) since dev work happens in Docker. The target deployment OS is Ubuntu. If you want to deploy to an actual webserver, additional work will need to be done, and variables/secrets filled in.

To begin, you will need to create a file that contains local settings and development keys for various services. We've ordered these variables from 'most needed' to 'least needed' for you to develop on the platform. If you set the first one, it will probably start, at least. Create a file named `.env` in the repository root and set as many settings as you're interested in working with:
1. Create an `.env` file in the root of this repository, and add in the following variables:

```bash
# The secret key is used to encrypt/validate sessions. It must be set for the application to run.
DJANGO_SECRET_KEY=random-string-goes-here-please-change
# Set these to the public/private keys you generate from https://www.hcaptcha.com/ or else you won't  be able to register.
GR_CAPTCHA_SECRET_KEY=captcha-secret-key-goes-here
GR_CAPTCHA_PUBLIC_KEY=captcha-site-key-goes-here
# Set these values to your Stripe API keys (test env) or you will not be able
# to test shield functionality via Stripe.
STRIPE_PUBLIC_KEY=key-goes-here
STRIPE_KEY=key-goes-here
# Some third party integrations require callbacks via webhooks. You will need a publicly accessible endpoint to test these. You can use a service like ngrok to set this up, and invoke it this way once you've logged in:
# ngrok http https://artconomy.vulpinity.com --subdomain your-ngrok-subdomain
WEBHOOKS_DOMAIN=test-webhook.ngrok.io
# Set these to the ID and secret from Authorize.net. You can register for a sandbox account at https://developer.authorize.net/
AUTHORIZE_KEY=authorize-net-id-goes-here
AUTHORIZE_SECRET=authorize-net-secret-goes-here
# The following keys will prevent code dealing with bank accounts from working if not set. Register for a Dwolla API
# account by visiting https://www.dwolla.com/
DWOLLA_KEY=key-for-dwolla-API
DWOLLA_SECRET=secret-for-dwolla-api
# Check out the Dwolla API docs to figure out how to create a funding source for the main account. Once you have
# this funding source created and verified, you will need to post the API URL link here. This is the account that payments will go out from. It should be the account Authorize.net payments deposit to, unless you want to run out of money.
DWOLLA_FUNDING_SOURCE_KEY=https://api-sandbox.dwolla.com/funding-sources/uuid-goes-here
# Create a bot in Telegram using @BotFather, and generate an API token for it. This is used for 2FA and availability announcements.
TELEGRAM_BOT_USERNAME=YourBotName
TELEGRAM_BOT_KEY=token-goes-here
# Create an app in Discord's Developer Portal, and then get the Application ID and secret. On Discord's end, you'll need
# to set up a redirect URL to point to your instance's Discord authorization URL, https://artconomy.vulpinity.com/discord/auth/
DISCORD_CLIENT_KEY=1234567890
DISCORD_CLIENT_SECRET=discord-client-secret
# Create an App in Discord's Developer Portal, and then add a bot to that app. Put the bot's token here.
DISCORD_BOT_KEY=token-goes-here
# Your Discord guild ID. To get this, enable Developer mode in your Discord user settings, and then right-click on your guild and select 'Copy ID'
DISCORD_GUILD_ID=id-goes-here
```

Add the following entry to your `/etc/hosts` file (You can change this, but for the moment it's hard coded for the dev scripts, and you may need to change that in a few places):

```bash
10.5.0.3	artconomy.vulpinity.com
```
Once you have your environment file created:

```bash
make
make up
```

This will build the application container and then start the application. You should then be able to visit the local copy at https://artconomy.vulpinity.com/, which will give you a certificate error you can safely ignore. Enjoy your personal copy of Artconomy.com!
