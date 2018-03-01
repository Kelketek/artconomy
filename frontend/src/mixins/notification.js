export default {
  props: ['notification'],
  computed: {
    event () {
      return this.notification.event
    }
  }
}
