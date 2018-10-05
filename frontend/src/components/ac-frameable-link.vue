<template>
  <router-link :to="to" @click.native="navigate">
    <slot></slot>
  </router-link>
</template>

<script>
  export default {
    name: 'ac-frameable-link',
    props: ['to', 'iFrame'],
    methods: {
      navigate (event) {
        console.log('I ran!')
        if (this.iFrame) {
          console.log('In frame!')
          let routeData = this.$router.resolve(this.to)
          window.open(routeData.href, '_blank')
          event.preventDefault()
        }
      }
    }
  }
</script>