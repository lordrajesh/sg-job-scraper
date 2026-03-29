import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [
    tailwind({ applyBaseStyles: false }),
  ],
  output: 'static',
  base: '/hk-jobs',
  build: {
    assets: '_assets',
  },
});
