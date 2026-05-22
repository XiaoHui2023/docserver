import { defineConfig } from 'vitepress'
import { readFileSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const dir = dirname(fileURLToPath(import.meta.url))
const sidebarPath = join(dir, 'sidebar.generated.json')

function loadSidebar(): unknown[] {
  if (!existsSync(sidebarPath)) {
    return [{ text: '说明', link: '/' }]
  }
  try {
    return JSON.parse(readFileSync(sidebarPath, 'utf-8')) as unknown[]
  } catch {
    return [{ text: '说明', link: '/' }]
  }
}

export default defineConfig({
  title: '文档',
  description: '通用 VitePress 文档站',
  base: '/',
  themeConfig: {
    nav: [{ text: '首页', link: '/' }],
    sidebar: loadSidebar(),
    search: {
      provider: 'local',
    },
    socialLinks: [],
  },
})
