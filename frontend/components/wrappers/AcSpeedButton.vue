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
    box-shadow: 0 3px 5px -1px rgba(0, 0, 0, .2), 0 6px 10px 0 rgba(0, 0, 0, .14), 0 1px 18px 0 rgba(0, 0, 0, .12);
    margin-right: 0;
    margin-top: .9rem;
  }
  .speed-button-container .v-btn {
    border: 3px solid #fff !important;
    border-radius: 100% !important;
  }
  .tooltip-holder .tooltip-content {
    border: 1px solid #fff !important;
    border-radius: 3px;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import {genId} from '@/lib/lib'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'

  @Component
export default class AcSpeedButton extends Vue {
    @Prop() public icon!: string
    @Prop({required: true}) public text!: string
    @Prop() public color!: string
    @Prop() public large!: boolean
    @Prop() public small!: boolean
    @Prop() public nudgeRight!: string
    @Prop() public nudgeTop!: string
    @Prop() public value!: boolean
    public id = genId()
    public showTooltip!: boolean

    public created() {
      this.showTooltip = this.value
    }

    public get style() {
      let str = ''
      if (this.nudgeRight) {
        str += `margin-right: ${this.nudgeRight};`
      }
      if (this.nudgeTop) {
        str += `margin-top: ${this.nudgeTop};`
      }
      return str
    }

    @Watch('value')
    public tooltipUpdate(val: boolean) {
      this.showTooltip = false
      if (val) {
        setTimeout(() => {
          this.showTooltip = true
        }, 300)
      }
    }
}
</script>
