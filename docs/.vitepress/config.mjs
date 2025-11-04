import { defineConfig } from 'vitepress'
import footnote from 'markdown-it-footnote'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Austrian Landslide Inventory",
  description: "Documentation",
  head: [
    [
      'link', { 
        rel: 'icon', type: 'image/png',
        href: '/icons/favicon.png' 
      }
    ]
  ],
  themeConfig: {
    search: {
      provider: 'local'
    },
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/quick-start' }
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'About', link: 'introduction/index.md' },
          { text: 'Schema', link: 'introduction/schema.md' }
        ]
      },
      {
        text: 'Guide',
        items: [
          { text: 'Quick Start', link: '/quick-start' },
          { text: 'Configuration', link: '/config' }
        ]
      }
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/JakobKlotz/landslides-db' }
    ],

    footer: {
      message: 'Licensed under CC BY-SA 4.0',
      copyright: 'Jakob Klotz'
    },
  },
  markdown: {
    config: (md) => {
      md.use(footnote)
    }
  }
})
