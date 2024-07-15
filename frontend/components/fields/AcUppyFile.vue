<template>
  <v-input v-bind="passedProps" class="ac-uppy-file" v-if="uppy">
    <div class="flex flex-column">
      <div class="flex text-center" v-if="label">
        <v-label :for="attrs.id" :color="errorColor" :focused="errorFocused">{{label}}</v-label>
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

.ac-uppy-file .uppy-StatusBar-actionBtn--done {
  display: none;
}
</style>

<script setup lang="ts">
import Uppy, {UppyFile} from '@uppy/core'
import {toRaw, markRaw, ref, watch, onMounted, useAttrs} from 'vue'
import Dashboard from '@uppy/dashboard'
import XHRUpload from '@uppy/xhr-upload'
import Url from '@uppy/url'

import {genId, getCookie} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {GenericState, Listener} from '@uppy/store-default/src'
import {useSingle} from '@/store/singles/hooks.ts'
import {ExtendedInputProps, useExtendedInput} from '@/components/fields/mixins/extended_input.ts'

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
    if (!this.single.purged) {
      this.single.setX(val)
    }
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

declare interface AcUppyFileProps extends ExtendedInputProps {
  endpoint?: string,
  modelValue: string|string[]|null,
  inForm?: boolean,
  showReset?: boolean,
  showClear?: boolean,
  maxNumberOfFiles?: number,
  uppyId?: string,
  persist?: boolean,
}

const props = withDefaults(
    defineProps<AcUppyFileProps>(),
    {
      endpoint: '/api/lib/asset/',
      inForm: true,
      showReset: true,
      showClear: false,
      maxNumberOfFiles: 1,
      uppyId: genId,
      persist: false,
      modelValue: (props) => {
        if (props.maxNumberOfFiles && props.maxNumberOfFiles > 1) {
          return []
        }
        return ''
      },
    },
)

const {passedProps, errorColor, errorFocused} = useExtendedInput(props)

const emit = defineEmits<{'update:modelValue': [string|string[]|null]}>()

const originalState = ref({})

const attrs = useAttrs()

const uppySingle = useSingle(props.uppyId, {
  x: {},
  endpoint: '#',
  persist: props.persist,
})

originalState.value = {...toRaw(uppySingle.x)}

const uppy = ref(new Uppy({
  id: props.uppyId,
  autoProceed: true,
  debug: false,
  store: new ArtconomyUppyStore(uppySingle),
  restrictions: {
    maxFileSize: null,
    maxNumberOfFiles: props.maxNumberOfFiles,
    minNumberOfFiles: 1,
  },
}))
uppy.value.use(XHRUpload, {
  endpoint: `${window.location.origin}${props.endpoint}`,
  fieldName: 'files[]',
  headers: {
    'X-CSRFToken': getCookie('csrftoken') + '',
  },
})

// Not sure where this is getting set. However, if I remove this boolean, test coverage plummets, so it must
// be used somewhere. Maybe by an upstream callback?
const unmounting = ref(false)

watch(() => props.modelValue, (newVal: string|string[]|null, oldVal: string|string[]|null) => {
  /* istanbul ignore if */
  if (unmounting.value) {
    return
  }
  if (!newVal && oldVal) {
    uppy.value.cancelAll()
  }
})

const reset = () => {
  /* istanbul ignore if */
  if (unmounting.value) {
    return
  }
  uppy.value.cancelAll()
  emit('update:modelValue', '')
}

const clear = () => {
  uppy.value.cancelAll()
  emit('update:modelValue', null)
}


onMounted(() => {
  uppy.value.use(Dashboard, {
    inline: true,
    target: `#${props.uppyId} .dashboard-container`,
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
  const companionUrl = `${window.location.origin}/companion/`
  if (window.chrome) {
    // Uppy's implementation of this is currently broken in Firefox. Issue link: https://github.com/transloadit/uppy/issues/4909
    uppy.value.use(Url, {
      target: Dashboard,
      companionUrl,
      companionCookiesRule: 'include',
    })
  }
  uppy.value.on('upload-success', (file: UppyFile | undefined, response: any) => {
    if (props.maxNumberOfFiles > 1) {
      emit('update:modelValue', [...props.modelValue || [], response.body.id])
      return
    } else  {
      emit('update:modelValue', response.body.id)
    }
  })
  // If this component is remounted, Uppy is regenerated, and we have to restore state.
  /* istanbul ignore if */
  if (Object.keys(originalState.value).length) {
    uppy.value.setState(originalState.value)
  }
})
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
