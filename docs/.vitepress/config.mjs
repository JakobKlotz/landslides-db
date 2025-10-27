import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  title: "Austrian Landslide Inventory",
  description: "Documentation",
  themeConfig: {
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/markdown-examples' }
    ],

    sidebar: [
      {
        text: 'Introduction',
        items: [
          { text: 'About', link: 'introduction/index.md'}
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
    ]
  }
})
