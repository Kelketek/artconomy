<template>
  <v-input v-bind="passedProps" class="ac-uppy-file" v-if="uppy">
    <div class="flex flex-column">
      <div class="flex text-center" v-if="label">
        <v-label :for="$attrs.id" :color="errorColor" :focused="errorFocused">{{label}}</v-label>
      </div>
      <div class="flex text-center" :id="uppyId">
        <v-col class="dashboard-container"/>
      </div>
      <div class="d-flex justify-center">
        <v-btn @click="reset" class="uppy-reset-button" variant="flat" color="secondary" v-if="modelValue && showReset">Reset</v-btn>
        <v-btn @click="clear" class="uppy-clear-button" variant="flat" color="danger" v-if="modelValue && showClear">Clear</v-btn>
      </div>
    </div>
  </v-input>
</template>

<style>
.ac-uppy-file .v-messages {
  text-align: center;
}

.ac-uppy-file .v-input__control {
  justify-content: center;
}

.ac-uppy-file .uppy-Dashboard-AddFiles-list {
  flex: unset;
}

.ac-uppy-file .uppy-Dashboard-AddFiles-title {
  color: #fff;
}
.ac-uppy-file .uppy-Url {
  display: flex;
  flex-direction: column;
}

.ac-uppy-file .uppy-Url-input {
  margin-bottom: 1rem;
}
</style>

<script lang="ts">
import Uppy, {UppyFile} from '@uppy/core'
import {toRaw, markRaw} from 'vue'
import Dashboard from '@uppy/dashboard'
import XHRUpload from '@uppy/xhr-upload'
import Url from '@uppy/url'

import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import {genId, getCookie} from '@/lib/lib'
import ExtendedInput from '@/components/fields/mixins/extended_input'
import {SingleController} from '@/store/singles/controller'
import {GenericState, Listener} from '@uppy/store-default/src'

// Based on upstream's store. Looks like we can't use our own store directly,
// we can only make a copy and work with that. Hell knows why.
class ArtconomyUppyStore<T extends GenericState = GenericState> {

  public single: SingleController<T>

  public stateStore: T = markRaw({}) as T

  public callbacks = new Set<Listener<T>>()

  constructor(single: SingleController<T>) {
    this.single = single
  }

  public getState(): T {
    return this.state
  }

  public get state() {
    return this.stateStore
  }

  public set state(val: T) {
    this.stateStore = markRaw(val)
    this.single.setX(val)
  }

  public setState(patch?: Partial<T>): void {
    const prevState = { ...this.state }
    const nextState = { ...this.state, ...patch }

    this.state = nextState
    this.publish(prevState, nextState, patch)
  }

  public subscribe(listener: Listener<T>): () => void {
    this.callbacks.add(listener)
    return () => {
      this.callbacks.delete(listener)
    }
  }

  public publish(...args: Parameters<Listener<T>>): void {
    this.callbacks.forEach((listener) => {
      listener(...args)
    })
  }
}

@Component({emits: ['update:modelValue']})
class AcUppyFile extends mixins(ExtendedInput) {
  @Prop({default: '/api/lib/asset/'})
  public endpoint!: string

  @Prop({default: ''})
  public modelValue!: string

  @Prop({default: true})
  public inForm!: boolean

  @Prop({default: true})
  public showReset!: boolean

  @Prop({default: false})
  public showClear!: boolean

  @Prop({default: 1})
  public maxNumberOfFiles!: number

  // noinspection SpellCheckingInspection
  @Prop({default: genId})
  public uppyId!: string

  @Prop({default: false})
  public persist!: boolean

  public uppy: Uppy = null as unknown as Uppy

  public originalState = {} as GenericState

  public uppySingle = null as unknown as SingleController<GenericState>

  public toRemove: Array<() => void> = []

  // Not sure where this is getting set. However, if I remove this boolean, test coverage plummets, so it must
  // be used somewhere. Maybe by an upstream callback?
  public unmounting = false

  @Watch('modelValue')
  public tripReset(newVal: string, oldVal: string) {
    /* istanbul ignore if */
    if (this.unmounting) {
      return
    }
    if (!newVal && oldVal) {
      (this.uppy as Uppy).cancelAll()
    }
  }

  public reset() {
    /* istanbul ignore if */
    if (this.unmounting) {
      return
    }
    (this.uppy as Uppy).cancelAll()
    this.$emit('update:modelValue', '')
  }

  public clear() {
    (this.uppy as Uppy).cancelAll()
    this.$emit('update:modelValue', null)
  }

  public created() {
    this.uppySingle = this.$getSingle(this.uppyId, {
      x: {},
      endpoint: '#',
      persist: this.persist,
    })
    this.originalState = {...toRaw(this.uppySingle.x)}
    this.uppySingle.setX({})
    this.uppy = new Uppy({
      id: this.uppyId,
      autoProceed: true,
      debug: false,
      store: new ArtconomyUppyStore(this.uppySingle),
      restrictions: {
        maxFileSize: null,
        maxNumberOfFiles: this.maxNumberOfFiles,
        minNumberOfFiles: 1,
      },
    })
    this.uppy.use(XHRUpload, {
      endpoint: `${window.location.origin}${this.endpoint}`,
      fieldName: 'files[]',
      headers: {
        'X-CSRFToken': getCookie('csrftoken') + '',
      },
    })
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
    const companionUrl = `${window.location.origin}/companion`
    if (window.chrome) {
      // Uppy's implementation of this is currently broken in Firefox. Issue link: https://github.com/transloadit/uppy/issues/4909
      this.uppy.use(Url, {
        target: Dashboard,
        companionUrl,
        companionCookiesRule: 'include',
      })
    }
    this.uppy.on('upload-success', (file: UppyFile | undefined, response: any) => {
      if (this.maxNumberOfFiles > 1) {
        this.$emit('update:modelValue', [...this.modelValue, response.body.id])
        return
      } else  {
        this.$emit('update:modelValue', response.body.id)
      }
    })
    // If this component is remounted, Uppy is regenerated, and we have to restore state.
    /* istanbul ignore if */
    if (Object.keys(this.originalState).length) {
      this.uppy.setState(this.originalState)
    }
  }
}

export default toNative(AcUppyFile)
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
