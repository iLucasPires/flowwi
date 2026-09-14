import { describe, it, expect } from 'vitest'

import { mount } from '@vue/test-utils'
import { VueQueryPlugin } from '@tanstack/vue-query'
import App from '../app/App.vue'

describe('App', () => {
  it('mounts renders properly', () => {
    const wrapper = mount(App, {
      global: {
        plugins: [VueQueryPlugin],
        stubs: {
          UApp: { template: '<div><slot /></div>' },
          'router-view': { template: '<div data-test="router-view" />' },
        },
      },
    })

    expect(wrapper.find('[data-test="router-view"]').exists()).toBe(true)
  })
})
