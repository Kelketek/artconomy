<template>
  <v-input v-bind="passedProps" class="ac-uppy-file">
    <v-col class="text-center mb-2" v-if="label">
      <v-label :for="$attrs.id" :color="errorColor" :focused="errorFocused">{{label}}</v-label>
    </v-col>
    <ac-paginated :list="submissionList" class="submission-list-container" v-if="submissionList">
      <template v-slot:default>
        <v-col cols="6" sm="6" md="3" class="submission-container" v-for="submission in submissionList.list"
               :key="submission.x && derived(submission).id">
          <v-row no-gutters v-if="submission.x">
            <v-col cols="12">
              <ac-gallery-preview class="pa-1"
                                  @click.capture.stop.prevent="select(derived(submission).id)"
                                  :key="derived(submission).id"
                                  :submission="derived(submission)" :show-footer="true"
              >
                <template v-slot:stats-append>
                  <v-spacer></v-spacer>
                  <v-col class="text-right">
                    <v-progress-circular
                        :color="$vuetify.theme.current.colors.secondary"
                        indeterminate
                        :size="24"
                        v-if="loading === derived(submission).id"
                    ></v-progress-circular>
                    <v-icon v-if="derived(submission).id === compare" color="green" :icon="mdiCheckCircle"/>
                  </v-col>
                </template>
              </ac-gallery-preview>
            </v-col>
            <v-col class="text-center" cols="12" v-if="removable">
              <v-btn @click="emit('remove', submission)" color="danger" class="remove-submission" variant="flat">Unlink Sample</v-btn>
            </v-col>
          </v-row>
        </v-col>
      </template>
    </ac-paginated>
  </v-input>
</template>

<script setup lang="ts">
import {ListController} from '@/store/lists/controller.ts'
import Submission from '@/types/Submission.ts'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {ExtendedInputProps, useExtendedInput} from '@/components/fields/mixins/extended_input.ts'
import {genId} from '@/lib/lib.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed, ref, watch} from 'vue'
import {mdiCheckCircle} from '@mdi/js'

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
//   public select(id: number) {
//     if (this.compare !== id) {
//       this.loading = id
//     }
//     this.$emit('update:modelValue', id)
//   }
// @Component({
//   components: {
//     AcGalleryPreview,
//     AcPaginated,
//     AcLoadSection,
//     AcAsset,
//   },
//   emits: ['update:modelValue', 'remove'],
// })
// class AcSubmissionSelect extends mixins(ExtendedInput) {
//   @Prop()
//   public list!: ListController<Submission>
//
//   @Prop({required: true})
//   public modelValue!: Submission | number | null
//
//   @Prop()
//   public saveComparison!: Submission | null
//
//   @Prop()
//   public queryEndpoint!: string
//
//   @Prop({default: false})
//   public related!: boolean
//
//   @Prop({default: false})
//   public removable!: boolean
//
//   public submissionList: ListController<Submission> = null as unknown as ListController<Submission>
//   public loading: number | false = false
//
//   public select(id: number) {
//     if (this.compare !== id) {
//       this.loading = id
//     }
//     this.$emit('update:modelValue', id)
//   }
//
//   @Watch('list')
//   public updateSubmissionList(controller: ListController<Submission>) {
//     /* istanbul ignore else */
//     if (controller) {
//       this.submissionList = controller
//       controller.firstRun()
//     }
//   }
//
//   @Watch('compare')
//   public stopProgress() {
//     this.loading = false
//   }
//
//   public derived(item: SingleController<Submission>) {
//     if (this.related) {
//       const submission = item as any
//       return submission.x && submission.x.submission
//     }
//     return item.x
//   }
//
//   public get compare() {
//     if (this.saveComparison !== undefined) {
//       return this.saveComparison && this.saveComparison.id
//     }
//     return this.modelValue
//   }
//
//   public created() {
//     if (this.queryEndpoint) {
//       this.submissionList = this.$getList(genId(), {endpoint: this.queryEndpoint})
//     } else {
//       this.submissionList = this.list
//     }
//     if (this.submissionList) {
//       this.submissionList.firstRun()
//     }
//   }
// }
//
// export default toNative(AcSubmissionSelect)
</script>
