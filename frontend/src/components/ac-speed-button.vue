<template>
  <div class="speed-container">
    <div class="tooltip-holder">
      <div class="tooltip-content" :style="style"><span>{{text}}</span></div>
    </div>
    <div class="speed-button-container">
      <slot>
        <v-btn
               dark
               :color="color"
               fab
               hover
               :large="large"
               :small="small"
        >
          <v-icon>{{ icon }}</v-icon>
        </v-btn>
      </slot>
    </div>
  </div>
</template>

<style scoped>
  .tooltip-holder {
    position: absolute;
    right: 5.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-direction: column;
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
  import {genId} from '../lib'
  export default {
    name: 'ac-speed-button',
    data () {
      return {
        id: genId(),
        showTooltip: this.value
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
    },
    watch: {
      value (val) {
        this.showTooltip = false
        val && setTimeout(() => {
          this.showTooltip = true
        }, 300)
      }
    },
    props: ['icon', 'text', 'color', 'large', 'small', 'nudgeRight', 'nudgeTop'],
  }
</script>