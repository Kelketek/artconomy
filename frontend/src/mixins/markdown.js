import { md } from '../lib'

export default {
  methods: {
    mdRender (text) {
      return md.render(text)
    },
    mdRenderInline (text) {
      return md.renderInline(text)
    }
  }
}
