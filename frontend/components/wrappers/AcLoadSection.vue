<template>
  <v-container class="pa-0" :fluid="fluid">
    <v-container class="pa-0 loading-spinner-container" v-if="controller.fetching && growPermitting" :fluid="fluid">
      <slot name="loading-spinner">
        <ac-loading-spinner/>
      </slot>
    </v-container>
    <v-container class="pa-0" :fluid="fluid" v-if="forceRender || (controller.ready && (!controller.fetching || grow))">
      <!-- Always use a template tag with v-slot:default to fill this slot or else it will be evaluated by the parent. -->
      <slot></slot>
    </v-container>
    <v-container class="pa-0" v-else-if="controller.failed">
      <slot name="failure">
        <v-row class="failure-prompt" justify="center" align-content="center" align="center">
          <v-col class="text-center shrink" align-self="center" cols="12">
            <slot name="failure-header">
              <p>
                <slot name="error-text">Whoops! We had an issue grabbing the information that goes here.</slot>
              </p>
            </slot>
          </v-col>
          <v-col cols="12" align-self="center" class="shrink text-center">
            <v-btn variant="elevated" @click="controller.retryGet" color="primary" class="retry-button">
              <v-icon left icon="mdi-refresh"/>
              Retry
            </v-btn>
          </v-col>
          <v-col cols="12" align-self="center" class="shrink text-center">
            <v-btn variant="elevated" color="orange" @click="showSupport" class="support-button">
              <v-icon left icon="mdi-contact-support"/>
              Contact Support
            </v-btn>
          </v-col>
        </v-row>
      </slot>
    </v-container>
  </v-container>
</template>

<style>
.failure-prompt {
  min-height: 50vh;
}
</style>

<script lang="ts">
import {Component, Prop, toNative} from 'vue-facing-decorator'
import AcLoadingSpinner from './AcLoadingSpinner.vue'
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import {ArtVue} from '@/lib/lib.ts'

@Component({
  components: {AcLoadingSpinner},
})
class AcLoadSection extends ArtVue {
  @Prop({required: true})
  public controller!: SingleController<any> | ListController<any>

  @Prop({default: true})
  public fluid!: boolean

  @Prop({default: false})
  public forceRender!: boolean

  @Prop({default: true})
  public loadOnGrow!: boolean

  public prerendering = false

  public created() {
    this.prerendering = Boolean(window.PRERENDERING || 0)
    /* istanbul ignore if */
    if (!this.controller.isFetchableController) {
      console.error(JSON.stringify(this.controller))
      throw Error('HANDED AN INVALID OBJECT FOR A CONTROLLER. THIS WILL NEVER LOAD!')
    }
  }

  public showSupport() {
    this.$store.commit('supportDialog', true)
  }

  public get grow() {
    return Boolean((this.controller as ListController<any>).grow)
  }

  public get growPermitting() {
    if (this.loadOnGrow) {
      return true
    }
    const controller = this.controller as ListController<any>
    if ((this.controller as ListController<any>).grow) {
      if (controller.list.length) {
        return false
      }
    }
    return true
  }
}

export default toNative(AcLoadSection)
</script>
