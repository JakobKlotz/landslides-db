import { defineConfig } from 'vitepress'

// https://vitepress.dev/reference/site-config
export default defineConfig({
  base: "/landslides-db/",   // repo name see https://vitepress.dev/guide/deploy#setting-a-public-base-path
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
    // https://vitepress.dev/reference/default-theme-config
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/quick-start' }
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
    ],

    footer: {
      message: 'Licensed under CC BY-SA 4.0',
      copyright: 'Jakob Klotz'
    },
  }
})
