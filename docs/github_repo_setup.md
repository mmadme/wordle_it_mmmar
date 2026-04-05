# GitHub Repo Setup

Questa guida serve a trasformare `woordle_new_github` in una repository GitHub pronta per Pages.

## Cosa e' gia' stato preparato

- `README.md`
- `.gitignore`
- workflow GitHub Pages in `.github/workflows/github-pages.yml`

## Cosa pubblichera' GitHub Pages

Il workflow esegue:

```bash
python3 build_github_pages.py --api-base https://sborraparle.duckdns.org
```

e pubblica il contenuto generato in `github_pages/`.

## Procedura minima su GitHub

1. creare una nuova repository vuota
2. fare push del branch `main`
3. aprire `Settings` -> `Pages`
4. scegliere `Source: GitHub Actions`
5. attendere il primo workflow completato

## Procedura minima da terminale

Se la cartella non e' ancora una repo:

```bash
git init -b main
git add .
git commit -m "Initial GitHub-ready version"
```

Poi, quando esiste la repo remota:

```bash
git remote add origin <URL-REPO-GITHUB>
git push -u origin main
```

## Nota sull'autenticazione

La creazione della repository remota richiede una sessione GitHub valida da browser o CLI.

Se usi VS Code:

- puoi creare la repo dal pannello Source Control o dal comando `Publish to GitHub`

Se usi GitHub CLI:

```bash
gh auth login
gh repo create
```

## Riferimenti ufficiali

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
