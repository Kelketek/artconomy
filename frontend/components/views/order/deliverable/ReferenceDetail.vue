<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col
        cols="12"
        style="position: relative"
      >
        <v-btn
          icon
          absolute
          top
          left
          :to="backUrl"
          color="primary"
        >
          <v-icon :icon="mdiArrowLeft" />
        </v-btn>
        <ac-load-section :controller="reference">
          <template #default>
            <ac-asset
              thumb-name="gallery"
              :asset="reference.x"
              :contain="true"
              alt="Reference for order. See comments below, if available."
            />
            <v-row>
              <v-col class="text-center">
                <ac-rating-button
                  :controls="true"
                  :patcher="reference.patchers.rating"
                  :editing="true"
                  :class="{'mr-1': reference.x!.owner === rawViewerName}"
                />
                <ac-confirmation
                  v-if="reference.x!.owner === rawViewerName"
                  :action="performDelete"
                >
                  <template #default="{on}">
                    <v-btn
                      color="red"
                      variant="flat"
                      class="ml-1"
                      v-on="on"
                    >
                      <v-icon
                        left
                        :icon="mdiDelete"
                      />
                      Delete
                    </v-btn>
                  </template>
                </ac-confirmation>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </v-col>
    </v-row>
    <ac-comment-section
      :comment-list="referenceComments"
      :nesting="false"
      :locked="!isInvolved || is(DeliverableStatus.MISSED) || is(DeliverableStatus.LIMBO)"
      :guest-ok="true"
      :show-history="isArbitrator"
      :extra-data="{deliverable: deliverableId}"
    />
  </v-container>
</template>

<script setup lang="ts">
import AcAsset from '@/components/AcAsset.vue'
import {DeliverableProps, useDeliverable} from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcRatingButton from '@/components/AcRatingButton.vue'
import {markRead, updateLinked} from '@/lib/lib.ts'
import {mdiArrowLeft, mdiDelete} from '@mdi/js'
import {useSingle} from '@/store/singles/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed} from 'vue'
import {useRouter} from 'vue-router'
import {DeliverableStatus} from '@/types/enums/DeliverableStatus.ts'
import {useViewer} from '@/mixins/viewer.ts'
import type {Comment, Reference} from '@/types/main'

const props = defineProps<DeliverableProps & {referenceId: string}>()
const router = useRouter()
const {rawViewerName} = useViewer()
const {references, prefix, url, is, isInvolved, isArbitrator} = useDeliverable(props)

const reference = useSingle<Reference>(`${prefix.value}__reference${props.referenceId}`, {
  endpoint: `${url.value}references/${props.referenceId}/`,
})
reference.get().then(
    () => markRead(reference, 'sales.Reference')).then(
    () => updateLinked({
      list: references,
      key: 'reference',
      newValue: reference.x,
    }),
)
const referenceComments = useList<Comment>(`${prefix.value}__reference${props.referenceId}__comments`, {
  endpoint: `/api/lib/comments/sales.Reference/${props.referenceId}/`,
  reverse: true,
  grow: true,
  params: {size: 5},
})
referenceComments.firstRun()

const backUrl = computed(() => {
  return {
    name: `${props.baseName}DeliverableReferences`,
    params: {
      deliverableId: props.deliverableId,
      orderId: props.orderId,
    },
  }
})

const performDelete = async () => {
  return reference.delete().then(() => {
    references.reset()
    router.replace(backUrl.value)
  })
}
</script>
