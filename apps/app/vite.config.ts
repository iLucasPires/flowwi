import { fileURLToPath, URL } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'
import ui from '@nuxt/ui/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      vue(),
      vueJsx(),
      vueDevTools(),
      ui({
        ui: {
          colors: {
            primary: 'indigo',
            neutral: 'neutral',
          },
          modal: {
            slots: {
              header: 'border-none',
              body: 'border-none',
              content: 'sm:max-w-none',
            },
          },

          fileUpload: {
            slots: {
              base: 'bg-elevated/50 border-none!',
            },
          },

          splitter: {
            slots: {
              handle:
                'data-[orientation=horizontal]:w-px data-[orientation=vertical]:h-px bg-border transition-colors data-[state=hover]:bg-primary data-[state=drag]:bg-primary',
            },
          },
        },
        autoImport: {
          // Only framework-level globals (ref/computed/watch/useRoute/useDebounceFn/...)
          // are auto-imported. Project code (composables, types, utils, constants,
          // schemas) uses explicit imports — see AGENTS.md → Auto-imports for why.
          imports: ['@vueuse/core', 'vue', 'vue-router'],
        },
        components: {
          dts: true,
          prefix: 'C',
          // Components stay auto-registered (name = filename, prefixed `C`) — the
          // discoverability win here is worth the "where's this defined" cost, unlike
          // composables/types/utils/constants which now use explicit imports (see
          // AGENTS.md → Auto-imports).
          dirs: ['./src/app/features', './src/app/shared/components'],
        },
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    optimizeDeps: {
      include: [
        '@nuxt/ui > prosemirror-state',
        '@nuxt/ui > prosemirror-transform',
        '@nuxt/ui > prosemirror-model',
        '@nuxt/ui > prosemirror-view',
        '@nuxt/ui > prosemirror-gapcursor',
      ],
    },

    server: {
      // WSL2 doesn't reliably propagate inotify events to chokidar (native fs events
      // silently miss brand-new files, especially — hence "useDocumentRealtime is not
      // defined" right after adding a new composable file, until a full restart).
      // Polling sidesteps that at the cost of a bit of CPU.
      watch: {
        usePolling: true,
        interval: 300,
      },
      proxy: {
        '/api': {
          target: env.VITE_API_URL,
          changeOrigin: true,
        },
        '/media': {
          target: env.VITE_API_URL,
          changeOrigin: true,
        },
        '/ws': {
          target: env.VITE_API_URL,
          changeOrigin: true,
          ws: true,
        },
      },
    },
  }
})
