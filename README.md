# Sunday Message

A simple weekly slide that displays the sermon title and scripture for the week.

## Setup

1. Upload your background image as `background.jpg` to this repo.
2. The page will automatically use it as the full-screen background.

## How It Works

Every Friday, an automated task searches Gmail for an email from Bill Secrest
with the subject "Scripture and Title", extracts the title and scripture, and
updates `index.html` with the new content.

## Deploying with GitHub Pages

1. Go to **Settings → Pages**
2. Set **Source** to `Deploy from a branch` → `main` → `/ (root)`
3. Your page will be live at `https://imrodmartin.github.io/sunday-message/`
