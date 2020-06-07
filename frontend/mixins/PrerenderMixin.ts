import Vue from 'vue'
import Component from 'vue-class-component'

@Component
export default class PrerenderMixin extends Vue {
  public prerendering = false
  public created() {
    this.prerendering = Boolean(window.PRERENDERING || 0)
  }
}
