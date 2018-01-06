export const Timer = {
  install (Vue) {
    Vue.mixin({
      data () {
        return {
          timers: {}
        }
      },
      methods: {
        $setTimer (name, func, timeout) {
          if (this.$root.timers[name]) {
            clearTimeout(this.$root.timers[name])
          }
          this.$root.timers[name] = setTimeout(func, timeout)
        },
        $clearTimer (name) {
          if (this.$root.timers[name]) {
            clearTimeout(this.$root.timers[name])
          }
        }
      }
    })
  }
}
