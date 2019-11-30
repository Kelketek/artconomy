import Vue from 'vue'
import Component from 'vue-class-component'

@Component
export default class Nav extends Vue {
  public get fullInterface() {
    return ['NewOrder', 'Shield'].indexOf(this.$route.name as string) === -1
  }
}
