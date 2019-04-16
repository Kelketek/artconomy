<template>
  <v-container class="pa-0" :fluid="fluid">
    <v-container class="pa-0" :fluid="fluid" v-if="controller.ready && !controller.fetching">
      <!-- Always use a template tag with v-slot:default to fill this slot or else it will be evaluated by the parent. -->
      <slot></slot>
    </v-container>
    <v-container class="pa-0" v-else-if="controller.fetching">
      <slot name="loading-spinner">
        <ac-loading-spinner></ac-loading-spinner>
      </slot>
    </v-container>
    <v-container class="pa-0" v-else-if="controller.failed">
      <slot name="failure">
        <v-layout column class="failure-prompt" justify-center align-content-center align-center>
          <v-flex class="text-xs-center" align-self-center shrink>
            <slot name="failure-header">
              <p>
                <slot name="error-text">Whoops! We had an issue grabbing the information that goes here.</slot>
              </p>
            </slot>
            <v-btn @click="controller.retryGet" color="primary" class="retry-button">
              <v-icon left>refresh</v-icon>
              Retry
            </v-btn>
            <v-btn color="orange" @click="showSupport" class="support-button">
              <v-icon left>contact_support</v-icon>
              Contact Support
            </v-btn>
          </v-flex>
        </v-layout>
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
import Vue from 'vue'
import Component from 'vue-class-component'
import AcLoadingSpinner from './AcLoadingSpinner.vue'
import {SingleController} from '@/store/singles/controller'
import {ListController} from '@/store/lists/controller'
import {Prop} from 'vue-property-decorator'
  @Component({
    components: {AcLoadingSpinner},
  })
export default class AcLoadSection extends Vue {
    @Prop({required: true})
    public controller!: SingleController<any>|ListController<any>
    @Prop({default: true})
    public fluid!: boolean

    private showSupport() {
      this.$store.commit('supportDialog', true)
    }
}
</script>
