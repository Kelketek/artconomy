<template>
  <v-container
    class="pa-0"
    :fluid="fluid"
  >
    <v-container
      v-if="controller.fetching && growPermitting"
      class="pa-0 loading-spinner-container"
      :fluid="fluid"
    >
      <slot name="loading-spinner">
        <ac-loading-spinner />
      </slot>
    </v-container>
    <v-container
      v-if="forceRender || (controller.ready && (!controller.fetching || grow))"
      class="pa-0"
      :fluid="fluid"
    >
      <!-- Always use a template tag with v-slot:default to fill this slot or else it will be evaluated by the parent. -->
      <slot />
    </v-container>
    <v-container
      v-else-if="controller.failed"
      class="pa-0"
    >
      <slot name="failure">
        <v-row
          class="failure-prompt"
          justify="center"
          align-content="center"
          align="center"
        >
          <v-col
            class="text-center shrink"
            align-self="center"
            cols="12"
          >
            <slot name="failure-header">
              <p>
                <slot name="error-text">
                  Whoops! We had an issue grabbing the information that goes here.
                </slot>
              </p>
            </slot>
          </v-col>
          <v-col
            cols="12"
            align-self="center"
            class="shrink text-center"
          >
            <v-btn
              variant="elevated"
              color="primary"
              class="retry-button"
              @click="controller.retryGet"
            >
              <v-icon
                left
                :icon="mdiRefresh"
              />
              Retry
            </v-btn>
          </v-col>
          <v-col
            cols="12"
            align-self="center"
            class="shrink text-center"
          >
            <v-btn
              variant="elevated"
              color="orange"
              class="support-button"
              @click="showSupport"
            >
              <v-icon
                left
                :icon="mdiHelpCircleOutline"
              />
              Contact Support
            </v-btn>
          </v-col>
        </v-row>
      </slot>
    </v-container>
  </v-container>
</template>

<script setup lang="ts">
import AcLoadingSpinner from './AcLoadingSpinner.vue'
import {SingleController} from '@/store/singles/controller.ts'
import {ListController} from '@/store/lists/controller.ts'
import {mdiHelpCircleOutline, mdiRefresh} from '@mdi/js'
import {computed} from 'vue'
import {useStore} from 'vuex'

const props = withDefaults(defineProps<{
  controller: SingleController<any> | ListController<any>,
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

<style>
.failure-prompt {
  min-height: 50vh;
}
</style>
