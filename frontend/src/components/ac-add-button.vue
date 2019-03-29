<template>
  <div class="add-button-container">
    <div class="tooltip-holder">
      <div class="tooltip-content" :style="style"><span>{{text}}</span></div>
    </div>
    <v-btn
        dark
        color="green"
        fab
        hover
        fixed
        right
        bottom
        large
        @click="launch"
    >
      <v-icon x-large>add</v-icon>
    </v-btn>
  </div>
</template>

<style scoped>
  .tooltip-holder {
    position: fixed;
    right: 7.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    bottom: 2.5rem;
  }
  .tooltip-content {
    background-color: #424242;
    padding: .25rem .5rem;
    border-radius: 3px;
    box-shadow: 0 3px 5px -1px rgba(0,0,0,.2),0 6px 10px 0 rgba(0,0,0,.14),0 1px 18px 0 rgba(0,0,0,.12);
    margin-right: 0;
    margin-top: .9rem;
  }
</style>

<script>
  export default {
    name: 'ac-add-button',
    props: ['value', 'nudgeRight', 'nudgeTop', 'text'],
    methods: {
      launch () {
        this.$emit('input', true)
      }
    },
    computed: {
      style () {
        let string = ''
        if (this.nudgeRight) {
          string += `margin-right: ${this.nudgeRight};`
        }
        if (this.nudgeTop) {
          string += `margin-top: ${this.nudgeTop};`
        }
        return string
      }
    }
  }
</script>