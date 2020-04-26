<template>
  <div class="add-button-container d-flex d-md-none">
    <div class="tooltip-holder">
      <div class="tooltip-content" :style="style"><slot /></div>
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
    right: 7rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
    bottom: 2rem;
  }

  .tooltip-content {
    background-color: #424242;
    padding: .25rem .5rem;
    border-radius: 3px;
    box-shadow: 0 3px 5px -1px rgba(0, 0, 0, .2), 0 6px 10px 0 rgba(0, 0, 0, .14), 0 1px 18px 0 rgba(0, 0, 0, .12);
    margin-right: 0;
    margin-top: .9rem;
  }
  .add-button-container .v-btn {
    border: 3px solid #fff !important;
    border-radius: 100% !important;
  }
  .tooltip-holder .tooltip-content {
    border: 1px solid #fff !important;
    border-radius: 3px;
  }
</style>

<script>
export default {
  name: 'ac-add-button',
  props: ['value', 'nudgeRight', 'nudgeTop', 'text'],
  methods: {
    launch() {
      this.$emit('input', true)
    },
  },
  computed: {
    style() {
      let styleString = ''
      if (this.nudgeRight) {
        styleString += `margin-right: ${this.nudgeRight};`
      }
      if (this.nudgeTop) {
        styleString += `margin-top: ${this.nudgeTop};`
      }
      return styleString
    },
  },
}
</script>
