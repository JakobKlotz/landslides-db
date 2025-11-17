import { defineConfig } from 'vitepress'
import footnote from 'markdown-it-footnote'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Austrian Landslide Inventory",
  description: "Documentation",
  head: [
    [
      'link', { 
        rel: 'icon', type: 'image/ico',
        href: '/favicon.ico' 
      }
    ]
  ],
  themeConfig: {
    logo: "/favicon.ico",
    search: {
      provider: 'local'
    },
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Introduction', link: '/intro/about' },
      { text: 'Guide', link: '/guide/quick-start' }
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'About', link: '/intro/about' },
          { text: 'Schema', link: '/intro/schema' }
        ]
      },
      {
        text: 'Guide',
        items: [
          { text: 'Quick Start', link: '/guide/quick-start' },
          { text: 'Configuration', link: '/guide/config' }
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
