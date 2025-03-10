<template>
  <v-input
    v-bind="passedProps"
    class="ac-uppy-file"
  >
    <v-col
      v-if="label"
      class="text-center mb-2"
    >
      <v-label
        :for="attrs.id"
        :color="errorColor"
        :focused="errorFocused"
      >
        {{ label }}
      </v-label>
    </v-col>
    <ac-paginated
      v-if="submissionList"
      :list="submissionList"
      class="submission-list-container"
    >
      <template #default>
        <v-col
          v-for="submission in submissionList.list"
          :key="submission.x && derived(submission).id"
          cols="6"
          sm="6"
          md="3"
          class="submission-container"
        >
          <v-row
            v-if="submission.x"
            no-gutters
          >
            <v-col cols="12">
              <ac-gallery-preview
                :key="derived(submission).id"
                class="pa-1"
                :submission="derived(submission)"
                :show-footer="true"
                @click.capture.stop.prevent="select(derived(submission).id)"
              >
                <template #stats-append>
                  <v-spacer />
                  <v-col class="text-right">
                    <v-progress-circular
                      v-if="loading === derived(submission).id"
                      :color="current.colors.secondary"
                      indeterminate
                      :size="24"
                    />
                    <v-icon
                      v-if="derived(submission).id === compare"
                      color="green"
                      :icon="mdiCheckCircle"
                    />
                  </v-col>
                </template>
              </ac-gallery-preview>
            </v-col>
            <v-col
              v-if="removable"
              class="text-center"
              cols="12"
            >
              <v-btn
                color="danger"
                class="remove-submission"
                variant="flat"
                @click="emit('remove', submission)"
              >
                Unlink Sample
              </v-btn>
            </v-col>
          </v-row>
        </v-col>
      </template>
    </ac-paginated>
  </v-input>
</template>

<script setup lang="ts">
import {ListController} from '@/store/lists/controller.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {ExtendedInputProps, useExtendedInput} from '@/components/fields/mixins/extended_input.ts'
import {genId} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed, ref, useAttrs, watch} from 'vue'
import {useTheme} from 'vuetify'
import {mdiCheckCircle} from '@mdi/js'
import type {Submission} from '@/types/main'

declare interface AcSubmissionSelectProps {
  list?: ListController<Submission>,
  saveComparison?: Submission | null,
  queryEndpoint?: string,
  related?: boolean,
  removable?: boolean,
  modelValue: Submission | number | null,
}

const props = withDefaults(defineProps<AcSubmissionSelectProps & Partial<ExtendedInputProps>>(), {
  related: false,
  removable: false,
  saveComparison: null,
  queryEndpoint: '',
  label: '',
  errorMessages: () => [],
})

const {current} = useTheme()
const attrs = useAttrs()

const {passedProps, errorFocused, errorColor} = useExtendedInput(props)

const emit = defineEmits<{'update:modelValue': [value: null|number], remove: [submission: SingleController<Submission>]}>()
const listId = genId()

let submissionList: ListController<Submission>
if (props.queryEndpoint) {
  submissionList = useList(listId, {endpoint: props.queryEndpoint})
} else if (!props.list) {
  throw Error('Neither queryEndpoint nor list provided!')
} else {
  submissionList = props.list
}
submissionList.firstRun()

const compare = computed(() => {
  if (props.saveComparison) {
    return props.saveComparison && props.saveComparison.id
  }
  return props.modelValue
})

const derived = (item: SingleController<Submission>) => {
  if (props.related) {
    const submission = item as any
    return submission.x && submission.x.submission
  }
  return item.x
}

const loading = ref<number|false>(false)

watch(compare, () => loading.value = false)

const select = (id: number) => {
  if (compare.value !== id) {
    loading.value = id
  }
  emit('update:modelValue', id)
}
</script>
