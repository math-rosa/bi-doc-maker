# BI Doc Maker Website

Site institucional estático do BI Doc Maker.

Ele apresenta a proposta do produto, principais recursos, fluxo de uso e links para GitHub, releases e apoio ao projeto.

## Tecnologias

- HTML
- CSS
- JavaScript
- Vite

## Desenvolvimento

```powershell
npm install
npm run dev
```

## Build

```powershell
npm run build
```

O build final fica em `dist/` e não deve ser versionado no Git.

## Preview Local

```powershell
npm run preview
```

## Observações

- O site não contém backend.
- Os assets usam caminhos relativos (`base: './'`) para facilitar deploy em GitHub Pages ou subpastas.
- O app BI Doc Maker continua sendo empacotado pela raiz do projeto com `.\build-windows.ps1`.
