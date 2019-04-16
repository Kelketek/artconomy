<template>
  <v-input v-bind="passedProps" class="ac-uppy-file">
    <v-flex>
      <v-flex v-if="label" text-xs-center mb-2>
        <v-label :for="$attrs.id" :color="errorColor" :focused="errorFocused">{{label}}</v-label>
      </v-flex>
      <v-flex :id="uppyId" text-xs-center>
        <v-flex class="dashboard-container"></v-flex>
      </v-flex>
      <v-flex text-xs-center>
        <v-btn @click="reset" class="uppy-reset-button" color="secondary" v-if="value && showReset">Reset</v-btn>
        <v-btn @click="clear" class="uppy-clear-button" color="danger" v-if="value && showClear">Clear</v-btn>
      </v-flex>
    </v-flex>
  </v-input>
</template>

<style>
  .ac-uppy-file .v-messages {
    text-align: center;
  }
</style>

<script lang="ts">
import Vue from 'vue'
import Uppy, {UppyFile} from '@uppy/core'
import Dashboard from '@uppy/dashboard'
import XHRUpload from '@uppy/xhr-upload'

import Component, {mixins} from 'vue-class-component'
import {genId, getCookie} from '@/lib'
import {Prop, Watch} from 'vue-property-decorator'
import ExtendedInput from '@/components/fields/mixins/extended_input'
import {RawData} from '@/store/forms/types/RawData'

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

    // noinspection SpellCheckingInspection
    public uppy: Uppy.Uppy | null = null
    // noinspection SpellCheckingInspection
    public uppyId: string = genId()

    @Watch('value')
    public tripReset(newVal: string, oldVal: string) {
      if (!newVal && oldVal) {
        (this.uppy as Uppy.Uppy).reset()
      }
    }

    public reset() {
      (this.uppy as Uppy.Uppy).reset()
      this.$emit('input', '')
    }

    public clear() {
      (this.uppy as Uppy.Uppy).reset()
      this.$emit('input', null)
    }

    private mounted() {
      Vue.set(this, 'uppy', Uppy({
        id: this.uppyId,
        autoProceed: true,
        debug: false,
        restrictions: {
          maxFileSize: null,
          maxNumberOfFiles: 1,
          minNumberOfFiles: 1,
        },
      }))
      const uppy = this.uppy as Uppy.Uppy
      uppy.use(Dashboard, {
        inline: true,
        target: `#${this.uppyId} .dashboard-container`,
        replaceTargetContent: true,
        note: 'Images only.',
        height: 250,
        width: 250,
        proudlyDisplayPoweredByUppy: false,
        showLinkToFileUploadResult: false,
      })
      uppy.use(XHRUpload, {
        endpoint: this.endpoint,
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        },
      })
      uppy.on('upload-success', (file: UppyFile, response: any) => {
        this.$emit('input', response.body.id)
        if (this.success) {
          this.success(response.body)
        }
      })
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
