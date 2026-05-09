import { defineConfig } from 'vite'

export default defineConfig({
  // Garante que os assets sejam carregados usando caminhos relativos.
  // Isso é ideal para o GitHub Pages ou deploy em subpastas.
  base: './',
})
