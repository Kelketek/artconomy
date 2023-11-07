<template>
  <v-row class="form-container" no-gutters>
    <div v-if="sending" class="loading-overlay">
      <v-progress-circular
          indeterminate
          :size="70"
          :width="7"
          color="purple"
          v-if="showSpinner"
      />
    </div>
    <v-col :class="{'form-sending': sending}" cols="12">
      <slot/>
    </v-col>
    <template v-for="(error, index) in savedErrors" :key="index">
      <v-col cols="12">
        <v-alert :value="true" type="error" :key="error" @update:model-value="(val) => {toggleError(val, index)}"
                 closable>
          {{error}}
        </v-alert>
      </v-col>
    </template>
  </v-row>
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
import {Component, Prop, toNative, Vue, Watch} from 'vue-facing-decorator'

@Component
class AcFormContainer extends Vue {
  @Prop({default: false})
  public sending!: boolean

  @Prop({default: () => []})
  public errors!: string[]

  @Prop({default: true})
  public showSpinner!: boolean

  public savedErrors: string[] = []

  public toggleError(val: boolean, index: number) {
    /* istanbul ignore if */
    if (val) {
      return
    }
    this.savedErrors.splice(index, 1)
  }

  public mounted() {
    window._paq.push(['FormAnalytics::scanForForms', this.$el])
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

export default toNative(AcFormContainer)
</script>
