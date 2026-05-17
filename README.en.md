# BI Doc Maker

> 🇧🇷 [Versão em português](README.md)

BI Doc Maker is a Windows desktop app that generates technical and executive documentation for Power BI projects saved in the `.pbip` format.

The product combines a Tauri + Svelte interface with a Python core packaged as a sidecar. All analysis runs locally: the app reads PBIP metadata, interprets the model and produces files ready for delivery, audit, governance or knowledge transfer.

## Project Overview

- Python core in `documentador_pbip.py` to read PBIP and generate the documentation.
- CLI in `documentador_core_cli.py` that exposes the core via JSON and acts as the app sidecar.
- Desktop app in `frond-end-app/` (Tauri + Svelte).
- Windows build in `build-windows.ps1` (PyInstaller + Tauri).
- Marketing site in `website/` with an example PDF document.

## Features

- Local analysis of Power BI `.pbip` projects (model, DAX, Power Query M, relationships, calculation groups, perspectives and RLS/OLS).
- **Batch mode**: pick a parent folder, the app scans subfolders and lists every PBIP found — choose which ones to document in one go.
- **Search/filter** on the project list by name or path (essential when there are many PBIPs).
- **Real-time status** during batch generation: each project shows OK or error with a tooltip explaining the failure.
- Export to Markdown (`.md`), Word (`.docx`) and printable HTML.
- HTML opens in the default browser so the user can save as PDF.
- DOCX documentation with a polished layout: cover page, table of contents, refined tables and code blocks with syntax highlighting.
- Customize the document with a title, company logo and colors.
- Configurable output folder (in **More Options**); in batch mode, all projects share a single output folder.
- Business rule inferred from Power Query M steps.
- Special `BI_DOC` comments in Power Query treated as official documentation.
- Offline technical reading for DAX expressions.
- Data dictionary and term glossary inferred from PBIP metadata.
- Mermaid diagram in Markdown and HTML output.
- Tabular list of relationships in Word.
- Modern UI with light/dark mode, visible focus and Escape key to close dialogs.
- Output automatically organized into a `Doc_BI` folder.
- Windows product that doesn't require Python installed on the client machine.

## How to Use

1. Open BI Doc Maker.
2. Pick a folder. The app **scans subfolders** looking for Power BI projects and lists every PBIP found.
3. Tick the projects you want to document (use *Select all* / *Clear* when there are many).
4. (Optional) In **More Options**, choose the output folder, formats, title, logo and colors. Without configuring, each project's documentation is saved inside the project itself.
5. Click **Generate Documentation**. The processing goes through the selected projects one by one, showing status (OK / ERROR) next to each item.

Files are saved at:

```text
<output-folder>\Doc_BI\
```

Output rules:

- **Batch (2+ projects)**: all share a single `Doc_BI` folder. Without configuring, it goes into the selected folder itself (scan root). When you configure **More Options → Output folder**, it goes into the chosen folder. Files are named `<Project>_documentacao.{md,docx,html}`.
- **Single project**: uses the output folder if configured, otherwise the project folder itself.

If you pick a single project and HTML is checked, it opens automatically in the browser when finished — from there, use the browser's print to save as PDF.

## Generated Files

- `<Project>_documentacao.md`
- `<Project>_documentacao.docx`
- `<Project>_documentacao.html`

The product does not generate a PNG of the diagram. Markdown and HTML keep the Mermaid diagram; the DOCX documents relationships in tables.

## What Gets Documented

- Report pages.
- Tables, columns, calculated columns and hierarchies.
- Measures and DAX expressions.
- DAX technical reading by category: filters, aggregations, relationships, time and logic.
- Power Query M queries, with inferred business rule and original code as technical evidence.
- Model relationships.
- **Calculation Groups** — items, precedence and dynamic format string.
- **Perspectives** — logical groupings of tables, columns and measures by audience.
- **RLS / OLS security** — roles, per-table DAX filters, column permissions and members.
- **M parameters and shared expressions** — split automatically, with type and value.
- Data dictionary and recurring terms.
- Image resources found in the project.

> Each section above only appears in the documentation when the PBIP actually contains the feature — simple projects produce clean documents, with no empty placeholders.

## BI_DOC Comments

You can enrich the documentation directly in Power Query M with special comments:

```powerquery
// BI_DOC: general query rule
// BI_DOC_ORIGEM: official source description
// BI_DOC_REGRA: validated business rule
// BI_DOC_OBSERVACAO: relevant observation
```

These comments appear above the automatic inference and help separate validated rules from heuristic reading.

## Marketing Site

The repository also includes a static site in `website/`, built with Vite, HTML, CSS and plain JavaScript.
The PDF shown in the mockup lives at `website/public/documentacao-power-bi-corporate-spend.pdf`.
Deployment to GitHub Pages is handled by the workflow `.github/workflows/pages.yml`.

Main commands:

```powershell
cd website
npm install
npm run dev
npm run build
npm run preview
```

The site build lives in `website\dist\` and is not committed to Git.

## Tech Stack

- **Python 3**: PBIP analysis core and document generation.
- **python-docx**: Word file creation and formatting.
- **Python-Markdown**: support for Markdown/HTML generation.
- **PyInstaller**: packages the Python core as a sidecar executable.
- **Tauri v1.5**: Windows desktop shell, sidecar integration and app packaging.
- **Rust**: native layer used by Tauri.
- **Svelte 4**: desktop interface.
- **TypeScript**: interface typing.
- **Vite**: app and marketing site build.
- **Node.js 18+**: front-end build environment.
- **Mermaid**: ER diagram in Markdown and HTML.
- **Power BI PBIP / TMDL / PBIR**: formats and metadata analyzed locally.

## Development Requirements

- Windows x64.
- Python 3 available in PATH or via the `py` launcher.
- Node.js 18+.
- Stable Rust toolchain.
- Git.

The build script packages what the product needs. End users do not need Python or Node.js installed.

## Windows Build

At the repo root:

```powershell
.\build-windows.ps1
```

The script:

- creates/updates the `.product-venv` environment;
- installs Python dependencies;
- packages the `documentador-core.exe` sidecar with PyInstaller;
- copies the sidecar to `frond-end-app\src-tauri\binaries`;
- builds the Tauri app.

Installers land at:

```text
frond-end-app\src-tauri\target\release\bundle\
```

To reuse Node dependencies already installed:

```powershell
.\build-windows.ps1 -SkipNpmInstall
```

For fast local dev (skips the PyInstaller bootloader rebuild, which requires Visual Studio Build Tools):

```powershell
.\build-windows.ps1 -FastBuild
```

> ⚠️ Public releases must **never** use `-FastBuild` — the stock PyInstaller bootloader is flagged by several heuristic antivirus engines. The local rebuild changes the binary hash and clears that false detection.

## App Development

Install front-end dependencies:

```powershell
cd frond-end-app
npm install
```

Before opening Tauri in dev mode, generate the sidecar once from the root:

```powershell
cd ..
.\build-windows.ps1 -SkipNpmInstall
```

Then run:

```powershell
cd frond-end-app
npm run tauri:dev
```

## Testing the Python Core

With the packaged executable:

```powershell
.\dist\documentador-core.exe export --project "C:\path\PBIPProject" --output-dir "C:\out" --formats "md,docx,html" --json
```

During development:

```powershell
.\.product-venv\Scripts\python.exe documentador_core_cli.py export --project "C:\path\PBIPProject" --output-dir "C:\out" --formats "md,docx,html" --json
```

There's also a diagnostic command:

```powershell
.\.product-venv\Scripts\python.exe documentador_core_cli.py analyze --project "C:\path\PBIPProject" --json
```

In PowerShell, keep `--formats "md,docx,html"` quoted.

## Antivirus and Windows SmartScreen

BI Doc Maker is distributed **without an Authenticode certificate** (paid digital signature). Because the Python sidecar is packaged via PyInstaller — a technology also used by malicious programs — some antivirus tools may show warnings during install or run. **The app is safe** and runs 100% locally (it doesn't send data anywhere).

### What to expect

1. **Windows SmartScreen** on the first `.exe`: click *More info* → *Run anyway*.
2. **Avast / McAfee / Kaspersky / Trend Micro**: may flag `documentador-core.exe` (the Python sidecar). Add an exception or submit as a false positive to your vendor.

### How to verify the download integrity

Every GitHub release publishes the **SHA256** of the `.msi` in the notes. Verify with:

```powershell
Get-FileHash ".\BI Doc Maker_X.Y.Z_x64_en-US.msi" -Algorithm SHA256
```

Your local copy's hash should match the one published in the release.

### For maintainers: reducing false positives

`build-windows.ps1` already applies several mitigations automatically:

- `--noupx`: avoids the UPX packer (UPX-compressed binaries are heavily flagged).
- `--version-file version-info.txt`: embeds Windows metadata (CompanyName, FileDescription, etc.) — executables without metadata are considered suspicious.
- `Assert-LastExitCode`: fails fast on any broken step, avoiding shipping a corrupt binary.
- **Automatic PyInstaller bootloader rebuild** (run by default by `build-windows.ps1`): the stock bootloader shipped via pip has a known hash to heuristic AVs. Rebuilding locally changes the hash and the binary stops matching those signatures. Requires Visual Studio Build Tools — if absent, the build continues with a warning. To skip the rebuild for local dev, use `-FastBuild`.

#### Submitting as false positive to major antivirus engines

After every public release, submit both `.exe` files (`documentador-core.exe` and `BI Doc Maker.exe`) to the official portals:

| Vendor | Portal | Average time |
| --- | --- | --- |
| **Microsoft Defender** | [microsoft.com/wdsi/filesubmission](https://www.microsoft.com/wdsi/filesubmission) | 3-7 days |
| **Avast / AVG** | [avast.com/false-positive-file-form](https://www.avast.com/false-positive-file-form.php) | 1-3 days |
| **McAfee** | [mcafee.com/.../contact-research](https://www.mcafee.com/enterprise/en-us/threat-center/contact-research.html) | 5-14 days |
| **Kaspersky** | [kaspersky.com/false-positive](https://www.kaspersky.com/false-positive) | 3-7 days |
| **Trend Micro** | [success.trendmicro.com/.../1059565](https://success.trendmicro.com/dcx/s/solution/1059565) | 3-10 days |

Thermometer: upload the `.exe` to [VirusTotal](https://www.virustotal.com) and see how many engines flag it before and after the submissions.

**Microsoft Defender (step by step)**, for its largest reach:

1. Go to [microsoft.com/wdsi/filesubmission](https://www.microsoft.com/wdsi/filesubmission) and sign in with a Microsoft account.
2. In **Submission type**, choose **Software developer**.
3. Upload `documentador-core.exe` (extracted from the MSI or portable ZIP).
4. Leave **Detection name** blank if you don't know which detection was triggered.
5. Leave **Definition update version** blank.
6. In **Additional information**, describe: "BI Doc Maker is an open source app to document Power BI PBIP projects. Source at [github.com/math-rosa/bi-doc-maker](https://github.com/math-rosa/bi-doc-maker). PyInstaller is only used to package the Python sidecar — no malicious code. Requesting reclassification as clean."
7. Tick **I believe this file should not be detected as malware**.
8. Submit. You'll get an email with the result in 3-7 business days.
9. Repeat the upload with `BI Doc Maker.exe` (installed in `Program Files`).

#### Distribute via winget (bypasses SmartScreen)

Installations via `winget install` **do not trigger SmartScreen** because the installer is signed by the Microsoft Store pipeline. Ready-to-use manifests live in [`winget/`](winget/). See [`winget/README.md`](winget/README.md) for the submission process to `microsoft/winget-pkgs`.

Once approved, users install with:

```powershell
winget install MathRosa.BIDocMaker
```

To sign the sidecar and MSI with an Authenticode certificate (when available):

```powershell
.\build-windows.ps1 -CertificateThumbprint <CERT-SHA1>
```

The script invokes `signtool` on both binaries (sidecar + MSI) with RFC 3161 timestamp. Tauri integration can also be configured via `tauri.conf.json.bundle.windows.certificateThumbprint`.

**Roadmap**: starting from a future version, all artifacts will be signed with EV (Extended Validation) Authenticode, eliminating SmartScreen and most AV alerts.

## Recommended Validation

```powershell
.\.product-venv\Scripts\python.exe -m py_compile documentador_pbip.py documentador_core_cli.py
cd frond-end-app
npm.cmd run build
cd src-tauri
cargo check
cd ..\..\website
npm.cmd run build
```

## Main Structure

```text
.
├─ documentador_pbip.py              # Analysis and generation core
├─ documentador_core_cli.py          # CLI used as sidecar
├─ build-windows.ps1                 # Official Windows build
├─ frond-end-app/                    # Tauri + Svelte app (SVG logo in src/assets/)
└─ website/                          # Marketing site
```

## Publishing

This repository contains the source code for the product and the site. Generated artifacts, installers, virtual environments, `node_modules`, `target`, `dist` and local builds are not versioned.

The site is published automatically to GitHub Pages on push to `main`.

To produce an installable version, run:

```powershell
.\build-windows.ps1
```

Then manually publish the generated artifacts in `frond-end-app\src-tauri\target\release\bundle\` if you want to cut a release.

## Open Source Acknowledgements

BI Doc Maker stands on a strong open source base:

- [Tauri](https://tauri.app/) for the lightweight desktop runtime and native packaging.
- [Svelte](https://svelte.dev/) for the interface layer.
- [Vite](https://vitejs.dev/) for fast app and site builds.
- [Rust](https://www.rust-lang.org/) for the native layer used by Tauri.
- [Python](https://www.python.org/) for the analysis and generation core.
- [PyInstaller](https://pyinstaller.org/) for packaging the Python sidecar.
- [python-docx](https://python-docx.readthedocs.io/) for Word document generation.
- [Python-Markdown](https://python-markdown.github.io/) for Markdown and HTML support.
- [Mermaid](https://mermaid.js.org/) for ER diagrams in Markdown/HTML.

## License

Distributed under the MIT license. See `LICENSE`.
