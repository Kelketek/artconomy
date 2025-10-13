<template>
  <v-input v-if="uppy" v-bind="passedProps" class="ac-uppy-file">
    <div class="flex flex-column">
      <div v-if="label" class="flex text-center">
        <v-label :for="attrs.id" :color="errorColor" :focused="errorFocused">
          {{ label }}
        </v-label>
      </div>
      <div :id="uppyId" class="flex text-center">
        <v-col class="dashboard-container" />
      </div>
      <div class="d-flex justify-center">
        <v-btn
          v-if="modelValue && showReset"
          class="uppy-reset-button"
          variant="flat"
          color="secondary"
          @click="reset"
        >
          Reset
        </v-btn>
        <v-btn
          v-if="modelValue && showClear"
          class="uppy-clear-button"
          variant="flat"
          color="danger"
          @click="clear"
        >
          Clear
        </v-btn>
      </div>
    </div>
  </v-input>
</template>

<script setup lang="ts">
import Uppy, { Meta, UppyFile, Body } from "@uppy/core"
import { toRaw, markRaw, ref, watch, onMounted, useAttrs } from "vue"
import Dashboard from "@uppy/dashboard"
import XHRUpload from "@uppy/xhr-upload"
import Url from "@uppy/url"

import { genId, getCookie } from "@/lib/lib.ts"
import { SingleController } from "@/store/singles/controller.ts"
import { GenericState, Listener } from "@uppy/store-default"
import { useSingle } from "@/store/singles/hooks.ts"
import {
  ExtendedInputProps,
  useExtendedInput,
} from "@/components/fields/mixins/extended_input.ts"

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
  endpoint?: string
  modelValue?: string | string[] | null
  inForm?: boolean
  showReset?: boolean
  showClear?: boolean
  maxNumberOfFiles?: number
  uppyId?: string
  persist?: boolean
}

const props = withDefaults(defineProps<AcUppyFileProps>(), {
  endpoint: "/api/lib/asset/",
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
    return ""
  },
})

const { passedProps, errorColor, errorFocused } = useExtendedInput(props)

const emit = defineEmits<{ "update:modelValue": [string | string[] | null] }>()

const originalState = ref({})

const attrs = useAttrs()

const uppySingle = useSingle(props.uppyId, {
  x: {},
  endpoint: "#",
  persist: props.persist,
})

originalState.value = { ...toRaw(uppySingle.x) }

const uppy = new Uppy({
  id: props.uppyId,
  autoProceed: true,
  debug: false,
  // @ts-expect-error Upstream type incomplete.
  store: new ArtconomyUppyStore<GenericState>(uppySingle),
  restrictions: {
    maxFileSize: null,
    maxNumberOfFiles: props.maxNumberOfFiles,
    minNumberOfFiles: 1,
  },
})
uppy.use(XHRUpload, {
  endpoint: `${window.location.origin}${props.endpoint}`,
  fieldName: "files[]",
  headers: {
    "X-CSRFToken": getCookie("csrftoken") + "",
  },
})

// Not sure where this is getting set. However, if I remove this boolean, test coverage plummets, so it must
// be used somewhere. Maybe by an upstream callback?
const unmounting = ref(false)

watch(
  () => props.modelValue,
  (newVal: string | string[] | null, oldVal: string | string[] | null) => {
    /* istanbul ignore if */
    if (unmounting.value) {
      return
    }
    if (!newVal && oldVal) {
      uppy.cancelAll()
    }
  },
)

const reset = () => {
  /* istanbul ignore if */
  if (unmounting.value) {
    return
  }
  uppy.cancelAll()
  emit("update:modelValue", "")
}

const clear = () => {
  uppy.cancelAll()
  emit("update:modelValue", null)
}

onMounted(() => {
  uppy.use(Dashboard, {
    inline: true,
    target: `#${props.uppyId} .dashboard-container`,
    replaceTargetContent: true,
    note: "Images only.",
    height: 250,
    width: 250,
    theme: "dark",
    proudlyDisplayPoweredByUppy: false,
    showLinkToFileUploadResult: false,
    doneButtonHandler: null,
  })
  const companionUrl = `${window.location.origin}/companion/`
  // Uppy's implementation of this is currently broken in Firefox. Issue link: https://github.com/transloadit/uppy/issues/5095
  if (window.chrome) {
    uppy.use(Url, {
      // @ts-expect-error Upstream type incomplete.
      target: Dashboard,
      companionUrl,
      companionCookiesRule: "include",
    })
  }
  uppy.on(
    "upload-success",
    (file: UppyFile<Meta, Body> | undefined, response: any) => {
      if (props.maxNumberOfFiles > 1) {
        emit("update:modelValue", [
          ...(props.modelValue || []),
          response.body.id,
        ])
        return
      } else {
        emit("update:modelValue", response.body.id)
      }
    },
  )
  // If this component is remounted, Uppy is regenerated, and we have to restore state.
  /* istanbul ignore if */
  if (Object.keys(originalState.value).length) {
    uppy.setState(originalState.value)
  }
})
</script>

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

<style scoped>
.ac-uppy-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
}
</style>

<style src="@uppy/core/css/style.min.css"></style>
<style src="@uppy/dashboard/css/style.min.css"></style>

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
