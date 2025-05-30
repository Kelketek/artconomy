<template>
  <ac-new-submission
    v-if="firstUpload || newUpload"
    ref="newSubmissionForm"
    :username="username"
    :visit="false"
    title="Upload a Sample"
    :model-value="modelValue"
    :allow-multiple="true"
    @success="addSample"
    @update:model-value="toggle"
  />
  <ac-expanded-property
    v-else
    ref="sampleEditor"
    :model-value="modelValue"
    :large="true"
    class="sample-editor"
    @update:model-value="toggle"
  >
    <template #title>
      <span>Change Samples</span>
    </template>
    <template #default>
      <div class="stuff" />
      <v-row no-gutters>
        <v-col cols="12">
          <v-tabs v-model="tab" centered>
            <v-tab value="tab-pick-sample" class="pick-sample-tab">
              Manage Samples
            </v-tab>
            <v-tab value="tab-add-new" class="add-new-tab"> Add Sample </v-tab>
          </v-tabs>
        </v-col>
        <v-col cols="12">
          <v-window v-model="tab">
            <v-window-item value="tab-pick-sample" eager>
              <ac-patch-field
                v-if="localSamples"
                field-type="ac-submission-select"
                :patcher="product.patchers.primary_submission"
                :list="localSamples"
                :save-comparison="product.x!.primary_submission"
                :related="true"
                :show-progress="true"
                :removable="true"
                @remove="unlinkSubmission"
              />
            </v-window-item>
            <v-window-item value="tab-add-new" eager>
              <v-row no-gutters>
                <v-col class="text-center" cols="12">
                  <v-btn
                    color="primary"
                    variant="flat"
                    @click="newUpload = true"
                  >
                    <v-icon left :icon="mdiUpload" />
                    Upload New Sample
                  </v-btn>
                </v-col>
                <v-col v-if="!art.empty" class="text-center" cols="12">
                  <p><strong>OR</strong></p>
                  <p>Select one of the pieces from your gallery below!</p>
                </v-col>
                <v-col v-if="!art.empty" cols="12">
                  <ac-paginated :list="art">
                    <v-col
                      v-for="submission in art.list"
                      :key="submission.x!.id"
                      class="px-1"
                      cols="6"
                      sm="6"
                      md="3"
                      @click.capture.stop.prevent="artToSample(submission.x!)"
                    >
                      <ac-gallery-preview
                        :submission="submission.x!"
                        class="product-sample-option"
                      />
                    </v-col>
                  </ac-paginated>
                </v-col>
              </v-row>
            </v-window-item>
          </v-window>
        </v-col>
      </v-row>
    </template>
    <template #actions>
      <v-spacer />
      <v-btn
        v-if="product.x!.primary_submission"
        color="danger"
        class="clear-showcased"
        variant="flat"
        @click="product.patch({ primary_submission: null })"
      >
        Clear Showcased Sample
      </v-btn>
      <v-btn
        v-if="mdAndUp"
        color="primary"
        variant="flat"
        @click="toggle(false)"
      >
        Done
      </v-btn>
      <v-spacer v-if="smAndDown" />
    </template>
  </ac-expanded-property>
</template>

<script setup lang="ts">
import AcExpandedProperty from "@/components/wrappers/AcExpandedProperty.vue"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import { useSubject } from "@/mixins/subjective.ts"
import { SingleController } from "@/store/singles/controller.ts"
import { ListController } from "@/store/lists/controller.ts"
import { flatten, newUploadSchema } from "@/lib/lib.ts"
import AcPaginated from "@/components/wrappers/AcPaginated.vue"
import AcGalleryPreview from "@/components/AcGalleryPreview.vue"
import { computed, defineAsyncComponent, ref, watch } from "vue"
import { mdiUpload } from "@mdi/js"
import { useList } from "@/store/lists/hooks.ts"
import { useForm } from "@/store/forms/hooks.ts"
import { useDisplay } from "vuetify"
import type {
  LinkedSubmission,
  Product,
  SubjectiveProps,
  Submission,
} from "@/types/main"

const AcNewSubmission = defineAsyncComponent(
  () => import("@/components/AcNewSubmission.vue"),
)

const props = defineProps<
  {
    product: SingleController<Product>
    samples: ListController<LinkedSubmission>
    modelValue: boolean
    productId: number | string
  } & SubjectiveProps
>()

const { subjectHandler } = useSubject({ props })
const emit = defineEmits<{ "update:modelValue": [boolean] }>()
const tab = ref("tab-pick-sample")
const newUpload = ref(false)
const newSubmissionForm = ref<null | typeof AcNewSubmission>(null)
const { mdAndUp, smAndDown } = useDisplay()

const localSamples = useList<LinkedSubmission>(
  // We don't want to use the outer scope's sample list because it will paginate separately.
  `product-${props.productId}-sample-select`,
  { endpoint: props.product.endpoint + "samples/" },
)
localSamples.firstRun().then(() => {
  if (localSamples.empty) {
    tab.value = "tab-add-new"
  }
})

const newSubmission = useForm(
  `${flatten(props.username)}-newSubmission`,
  newUploadSchema(subjectHandler.user),
)
const art = useList<Submission>(`${flatten(props.username)}-art`, {
  endpoint: `/api/profiles/account/${props.username}/submissions/sample-options/`,
})
art.firstRun().catch(() => {})

watch(
  newSubmissionForm,
  (value) => {
    if (!value) {
      return
    }
    value.isArtist = true
  },
  { immediate: true },
)

const firstUpload = computed(() => {
  const product = props.product.x as Product
  return !product.primary_submission && props.samples.empty && art.empty
})

const toggle = (value: boolean) => emit("update:modelValue", value)

const artToSample = (value: Submission) => {
  localSamples.post({ submission_id: value.id }).then((result: any) => {
    localSamples.uniquePush(result)
    props.samples.uniquePush(result)
    tab.value = "tab-pick-sample"
    if (!(props.product.x as Product).primary_submission) {
      props.product.patch({ primary_submission: result.submission.id })
    }
  })
}

const addSample = (value: Submission) => {
  art.uniquePush(value)
  localSamples.post({ submission_id: value.id }).then((result: any) => {
    localSamples.push(result)
    const samples = props.samples
    samples.push(result)
  })
  tab.value = "tab-pick-sample"
  newSubmission.reset()
  newUpload.value = false
  if (newSubmissionForm.value) {
    newSubmissionForm.value!.isArtist = true
  }
  if (props.product.x!.primary_submission) {
    return
  }
  // @ts-expect-error Written type doesn't match read.
  return props.product.patch({ primary_submission: value.id })
}

const unlinkSubmission = (submission: SingleController<LinkedSubmission>) => {
  const oldValue = submission.x!
  const id = submission.x!.submission.id
  submission.delete().then(() => {
    const existingPrimary = (props.product.x as Product).primary_submission
    if (existingPrimary && existingPrimary.id === id) {
      props.product.updateX({ primary_submission: null })
    }
    props.samples.remove(oldValue)
    localSamples.remove(oldValue)
  })
}
</script>
