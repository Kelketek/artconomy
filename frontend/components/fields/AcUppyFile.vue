<template>
  <v-input v-bind="passedProps" class="ac-uppy-file" v-if="uppy">
    <div class="flex flex-column">
      <div class="flex text-center" v-if="label" >
        <v-label :for="$attrs.id" :color="errorColor" :focused="errorFocused">{{label}}</v-label>
      </div>
      <div class="flex text-center" :id="uppyId" >
        <v-col class="dashboard-container" />
      </div>
      <div class="d-flex justify-center">
        <v-btn @click="reset" class="uppy-reset-button" color="secondary" v-if="value && showReset">Reset</v-btn>
        <v-btn @click="clear" class="uppy-clear-button" color="danger" v-if="value && showClear">Clear</v-btn>
      </div>
    </div>
  </v-input>
</template>

<style>
  .ac-uppy-file .v-messages {
    text-align: center;
  }
  .ac-uppy-file .uppy-Dashboard-AddFiles-title {
    color: #fff;
  }
</style>

<script lang="ts">
import Uppy, {UppyFile} from '@uppy/core'
import Dashboard from '@uppy/dashboard'
import XHRUpload from '@uppy/xhr-upload'

import Component, {mixins} from 'vue-class-component'
import {getCookie} from '@/lib/lib'
import {Prop, Watch} from 'vue-property-decorator'
import ExtendedInput from '@/components/fields/mixins/extended_input'
import {RawData} from '@/store/forms/types/RawData'
import {SingleController} from '@/store/singles/controller'
import Vue from 'vue'

declare type UppyState = Record<string, unknown>
declare type StateListener = (prevState: UppyState, nextState: UppyState, patch: Partial<UppyState>) => void

const uppyStore = (single: SingleController<UppyState>) => {
  // Custom Uppy state backend. Uppy can store/restore its state using whatever backend we like, so long as we implement
  // methods as described here: https://uppy.io/docs/stores/
  const listeners: StateListener[] = []
  return {
    getState: () => {
      const state = single.x
      if (state === undefined) {
        // We're unmounting and the single has been destroyed. The dashboard plugin has a setTimeout event that
        // expects us to still have state, so put some bogus state here to satisfy it.
        return {plugins: {Dashboard: {}}}
      }
      return state as UppyState
    },
    setState: (patch: Partial<UppyState>) => {
      if (single.x === undefined) {
        // Same problem here. Just ignore any attempts to change state if we're already done.
        return
      }
      const prevState = {...single.x}
      const nextState = {...prevState, ...patch}
      single.updateX(nextState)
      listeners.forEach((listener) => {
        listener(prevState, nextState, patch)
      })
    },
    subscribe: (listener: StateListener) => {
      listeners.push(listener)
      return () => listeners.splice(listeners.indexOf(listener), 1)
    },
  }
}

@Component
export default class AcUppyFile extends mixins(ExtendedInput) {
    @Prop({default: '/api/lib/v1/asset/'})
    public endpoint!: string

    @Prop({default: ''})
    public value!: string

    @Prop({default: true})
    public inForm!: boolean

    @Prop({default: null})
    public success!: (data: RawData) => {} | null

    @Prop({default: true})
    public showReset!: boolean

    @Prop({default: false})
    public showClear!: boolean

    @Prop({default: 1})
    public maxNumberOfFiles!: number

    // noinspection SpellCheckingInspection
    @Prop({default: true})
    public uppyId!: string

    @Prop({default: false})
    public persist!: boolean

    public uppy: Uppy = null as unknown as Uppy

    public originalState = {} as UppyState

    public uppySingle = null as unknown as SingleController<UppyState>

    public toRemove: Array<() => void> = []

    // Not sure where this is getting set. However, if I remove this boolean, test coverage plummets, so it must
    // be used somewhere. Maybe by an upstream callback?
    public unmounting = false

    @Watch('value')
    public tripReset(newVal: string, oldVal: string) {
      /* istanbul ignore if */
      if (this.unmounting) {
        return
      }
      if (!newVal && oldVal) {
        (this.uppy as Uppy).reset()
      }
    }

    public reset() {
      /* istanbul ignore if */
      if (this.unmounting) {
        return
      }
      (this.uppy as Uppy).reset()
      this.$emit('input', '')
    }

    public clear() {
      (this.uppy as Uppy).reset()
      this.$emit('input', null)
    }

    public created() {
      this.uppySingle = this.$getSingle(this.uppyId, {x: {}, endpoint: '#', persist: this.persist})
      this.originalState = {...this.uppySingle.x}
      Vue.set(this, 'uppy', new Uppy({
        id: this.uppyId,
        autoProceed: true,
        debug: false,
        store: uppyStore(this.uppySingle),
        restrictions: {
          maxFileSize: null,
          maxNumberOfFiles: this.maxNumberOfFiles,
          minNumberOfFiles: 1,
        },
      }).use(XHRUpload, {
        endpoint: this.endpoint,
        fieldName: 'files[]',
        headers: {
          'X-CSRFToken': getCookie('csrftoken') + '',
        },
      }))
    }

    public mounted() {
      this.uppy.use(Dashboard, {
        inline: true,
        target: `#${this.uppyId} .dashboard-container`,
        replaceTargetContent: true,
        note: 'Images only.',
        height: 250,
        width: 250,
        theme: 'dark',
        proudlyDisplayPoweredByUppy: false,
        showLinkToFileUploadResult: false,
        // @ts-ignore
        doneButtonHandler: null,
      })
      this.uppy.on('upload-success', (file: UppyFile, response: any) => {
        if (this.maxNumberOfFiles > 1) {
          this.$emit('input', [...this.value, response.body.id])
        } else {
          this.$emit('input', response.body.id)
        }
        if (this.success) {
          this.success(response.body)
        }
      })
      // If this component is remounted, Uppy is regenerated and we have to restore state.
      /* istanbul ignore if */
      if (Object.keys(this.originalState).length) {
        this.uppy.setState(this.originalState)
      }
    }
}
</script>

<style scoped>
  .ac-uppy-container {
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
</style>

<style src="@uppy/core/dist/style.css"></style>
<style src="@uppy/dashboard/dist/style.css"></style>

<style lang="stylus">
  .uppy-DashboardContent-bar {
    z-index: 1
  }

  .dashboard-container {
    display: flex;
    justify-content: center;

    .uppy-Root {
      font-family: 'Roboto', sans-serif
      color: unset
    }

    .uppy-Dashboard-inner {
      background-color: unset
      border-color: #5c5c5c
      /*color: unset;*/
    }

    .uppy-Dashboard-dropFilesTitle, .uppy-StatusBar-content {
      color: unset
    }

    .uppy-StatusBar {
      background-color: unset
    }

    .uppy-DashboardItem {
      border-bottom-color: #5c5c5c
    }

    .uppy-DashboardContent-bar {
      background-color: unset
      border-color: #5c5c5c
    }
  }

  .uppy-Dashboard-inner {
    min-height: 250px;
  }
</style>
