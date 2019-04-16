<template>
  <v-flex class="form-container">
    <div v-if="sending" class="loading-overlay">
      <v-progress-circular
          indeterminate
          :size="70"
          :width="7"
          color="purple"
      ></v-progress-circular>
    </div>
    <v-flex :class="{'form-sending': sending}">
      <slot/>
    </v-flex>
    <template v-for="(error, index) in savedErrors">
      <v-alert value="error" type="error" :key="error" @input="(val) => {toggleError(val, index)}" dismissible>
        {{error}}
      </v-alert>
    </template>
  </v-flex>
</template>

<style scoped>
  .loading-overlay {
    position: absolute;
    display: flex;
    align-items: center;
    justify-content: center;
    top: 0;
    right: 0;
    height: 100%;
    width: 100%;
    z-index: 1;
    vertical-align: center;
    text-align: center;
  }

  .form-container {
    position: relative;
  }

  .form-sending {
    opacity: .25;
  }

  .error-right {
    float: right;
    display: inline-block
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'

  @Component
export default class AcFormContainer extends Vue {
    @Prop({default: false})
    public sending!: boolean
    @Prop({default: () => []})
    public errors!: string[]
    public savedErrors: string[] = []

    public toggleError(val: boolean, index: number) {
      /* istanbul ignore if */
      if (val) {
        return
      }
      this.savedErrors.splice(index, 1)
    }

    @Watch('errors', {deep: true})
    public saveErrors(val: string[]) {
      /* istanbul ignore if */
      if (!Array.isArray(val)) {
        return
      }
      this.savedErrors = [...val]
    }
}
</script>
