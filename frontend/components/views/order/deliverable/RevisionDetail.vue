<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="12" style="position: relative">
        <v-btn icon absolute top left :to="backUrl" color="primary">
          <v-icon :icon="mdiArrowLeft"/>
        </v-btn>
        <ac-load-section :controller="revision">
          <template v-slot:default>
            <ac-asset thumb-name="gallery" :asset="revision.x" :contain="true" alt="Revision for order."/>
            <ac-form-container v-bind="approveForm.bind" v-if="revision.x">
              <v-row>
                <v-col class="text-center" cols="12" :lg="isBuyer && !isFinal ? '6' : '12'" v-if="isBuyer || archived">
                  <v-btn color="green" :href="revision.x.file.full" variant="flat" download>
                    <v-icon left :icon="mdiCloudDownload"/>
                    Download
                  </v-btn>
                </v-col>
                <v-col class="text-center" cols="12" :lg="6"
                       v-if="isBuyer && !isFinal && (!archived || revision.x.approved_on)">
                  <v-btn @click="approveForm.submitThen(revision.updateX)" color="primary" variant="flat"
                         v-if="!revision.x.approved_on">
                    <v-icon left :icon="mdiCheckCircle"/>
                    Approve
                  </v-btn>
                  <span v-else-if="revision.x.approved_on">Approved on {{
                      formatDateTime(revision.x.approved_on)
                    }}</span>
                </v-col>
                <v-col class="text-center" cols="6" lg="3" v-else-if="isSeller">
                  <v-btn icon small color="green" :href="revision.x.file.full" variant="flat" download
                         aria-label="Download">
                    <v-icon :icon="mdiCloudDownload"/>
                  </v-btn>
                </v-col>
                <v-col class="text-center" cols="6" lg="3" v-if="isSeller && isLast && !archived">
                  <v-btn icon small color="danger" class="delete-revision" @click="handleDelete"
                         aria-label="Delete Revision">
                    <v-icon :icon="mdiDelete"/>
                  </v-btn>
                </v-col>
                <v-col class="text-center" cols="12" lg="6" v-if="isSeller && isLast &&! isFinal && !archived">
                  <v-btn color="primary" @click="statusEndpoint('complete')()" variant="flat">Mark Final</v-btn>
                </v-col>
                <v-col class="text-center" cols="12" lg="6" v-if="isSeller && isFinal && !(archived && escrow)">
                  <v-btn color="primary" @click="statusEndpoint('reopen')()" variant="flat">Unmark Final</v-btn>
                </v-col>
                <v-col class="'text-center" cols="12" v-if="galleryLink">
                  <v-btn color="green" block :to="galleryLink" variant="flat">
                    <v-icon :icon="mdiUpload"/>
                    <span v-if="isSeller">View in Gallery</span><span v-else>View in Collection</span>
                  </v-btn>
                </v-col>
                <v-col class="text-center mb-2" cols="12" lg="12"
                       v-else-if="isSeller || (is(DeliverableStatus.COMPLETED) && isRegistered)">
                  <v-btn color="green" block @click="prepSubmission" class="prep-submission-button" variant="elevated">
                    <v-icon :icon="mdiUpload"/>
                    <span v-if="isSeller">Add to Gallery</span><span v-else>Add to Collection</span>
                  </v-btn>
                </v-col>
              </v-row>
            </ac-form-container>
          </template>
        </ac-load-section>
      </v-col>
    </v-row>
    <ac-comment-section :commentList="revisionComments" :nesting="false" :locked="!isInvolved" :guest-ok="true"
                        :show-history="isArbitrator"/>
  </v-container>
</template>

<script setup lang="ts">
import AcAsset from '@/components/AcAsset.vue'
import Revision from '@/types/Revision.ts'
import {DeliverableProps, useDeliverable} from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Comment from '@/types/Comment.ts'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {markRead} from '@/lib/lib.ts'
import {User} from '@/store/profiles/types/User.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {mdiCloudDownload, mdiCheckCircle, mdiDelete, mdiUpload, mdiArrowLeft} from '@mdi/js'
import {useSingle} from '@/store/singles/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useRouter} from 'vue-router'
import {computed} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {formatDateTime} from '@/lib/otherFormatters.ts'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'

const props = defineProps<DeliverableProps & { revisionId: string|number }>()
const router = useRouter()
const {
  revisions,
  url,
  escrow,
  prefix,
  addSubmission,
  viewSettings,
  deliverable,
  statusEndpoint,
  isArbitrator,
  isInvolved,
  isSeller,
  isBuyer,
  archived,
  is,
} = useDeliverable(props)
const {viewer, isRegistered} = useViewer()

const revision = useSingle<Revision>(`${prefix.value}__revision${props.revisionId}`, {
  endpoint: `${url.value}revisions/${props.revisionId}/`,
})
revision.get().then(
    () => markRead(revision, 'sales.Revision')).then(
    () => revisions.replace(revision.x as Revision),
)
const approveForm = useForm(`${prefix.value}__approve${props.revisionId}`, {
  endpoint: `${url.value}revisions/${props.revisionId}/approve/`,
  fields: {},
})
revisions.firstRun()
const revisionComments = useList<Comment>(`${prefix.value}__revision${props.deliverableId}__comments`, {
  endpoint: `/api/lib/comments/sales.Revision/${props.revisionId}/`,
  reverse: true,
  grow: true,
  params: {size: 5},
})
revisionComments.firstRun()

const backUrl = computed(() => {
  return {
    name: `${props.baseName}DeliverableRevisions`,
    params: {
      deliverableId: props.deliverableId,
      orderId: props.orderId,
    },
  }
})

const handleDelete = () => {
  const currentRevision = revision.x as Revision
  revision.delete().then(() => {
    revisions.remove(currentRevision)
    router.replace(backUrl.value)
  })
}

const prepSubmission = () => {
  addSubmission.fields.revision.update(props.revisionId)
  viewSettings.patchers.showAddSubmission.model = true
}

const isLast = computed(() => {
  if (!revision.x) {
    return false
  }
  const lastRevision = revisions.list[revisions.list.length - 1]
  if (!lastRevision) {
    return false
  }
  return (lastRevision.x as Revision).id === revision.x.id
})

const isFinal = computed(() => {
  return deliverable.x?.final_uploaded && isLast.value
})

const submissionMap = computed((): { [key: number]: number } => {
  /* istanbul ignore if */
  if (!revision.x) {
    return {}
  }
  const map: { [key: number]: number } = {}

  revision.x.submissions.map((entry) => {
    map[entry.owner_id] = entry.id
  }) // eslint-disable-line array-callback-return
  return map
})

const gallerySubmissionId = computed(() => {
  /* istanbul ignore if */
  if (!revision.x) {
    return null
  }
  return submissionMap.value[(viewer.value as User).id] || null
})

const galleryLink = computed(() => {
  if (!gallerySubmissionId.value) {
    return null
  }
  return {
    name: 'Submission',
    params: {submissionId: gallerySubmissionId.value + ''},
  }
})

const isSubmitted = computed(() => {
  return !!gallerySubmissionId.value
})
</script>
