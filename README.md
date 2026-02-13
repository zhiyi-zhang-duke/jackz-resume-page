# Jack Zhang - Online Resume

A personal resume website built with [Jekyll](https://jekyllrb.com/) and hosted on [GitHub Pages](https://pages.github.com/), using the [modern-resume-theme](https://github.com/sproogen/modern-resume-theme) by sproogen.

## Live Site

https://zhiyi-zhang-duke.github.io/jackz-resume-page

## Project Structure

- `_config.yml` — Main configuration file containing all resume content (personal info, experience, education, projects, skills, etc.)
- `index.md` — Entry point that loads the theme's default layout
- `Gemfile` — Ruby/Jekyll dependencies for GitHub Pages
- `images/` — Static assets such as profile image

## How to Update

All resume content lives in `_config.yml`. Edit that file to update sections like experience, education, projects, and skills. Changes pushed to `master` will automatically rebuild and deploy via GitHub Pages.

## Local Development

To preview the site locally:

```bash
bundle install
bundle exec jekyll serve
```

Then visit `http://localhost:4000`.
