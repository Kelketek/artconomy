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
              <v-icon left :icon="mdiRefresh"/>
              Retry
            </v-btn>
          </v-col>
          <v-col cols="12" align-self="center" class="shrink text-center">
            <v-btn variant="elevated" color="orange" @click="showSupport" class="support-button">
              <v-icon left :icon="mdiHelpCircleOutline"/>
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

<script setup lang="ts">
import AcLoadingSpinner from './AcLoadingSpinner.vue'
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import {mdiHelpCircleOutline, mdiRefresh} from '@mdi/js'
import {computed} from 'vue'
import {useStore} from 'vuex'

const props = withDefaults(defineProps<{
  controller: SingleController<any> | ListController<any> & { isFetchableController: true },
  fluid?: boolean,
  forceRender?: boolean,
  loadOnGrow?: boolean,
}>(), {
  forceRender: false,
  fluid: true,
  loadOnGrow: true,
})

const store = useStore()

const showSupport = () => {
  store.commit('supportDialog', true)
}

const grow = computed(() => Boolean((props.controller as ListController<any>).grow))

const growPermitting = computed(() => {
  if (props.loadOnGrow) {
    return true
  }
  const controller = props.controller as ListController<any>
  if ((props.controller as ListController<any>).grow) {
    if (controller.list.length) {
      return false
    }
  }
  return true
})
</script>
