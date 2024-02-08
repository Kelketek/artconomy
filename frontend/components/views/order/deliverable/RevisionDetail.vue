<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="12" style="position: relative">
        <v-btn icon absolute top left :to="backUrl" color="primary">
          <v-icon icon="mdi-arrow-left"/>
        </v-btn>
        <ac-load-section :controller="revision">
          <template v-slot:default>
            <ac-asset thumb-name="gallery" :asset="revision.x" :contain="true"/>
            <ac-form-container v-bind="approveForm.bind" v-if="revision.x">
              <v-row>
                <v-col class="text-center" cols="12" :lg="isBuyer && !isFinal ? '6' : '12'" v-if="isBuyer || archived">
                  <v-btn color="green" :href="revision.x.file.full" variant="flat" download>
                    <v-icon left icon="mdi-cloud-download"/>
                    Download
                  </v-btn>
                </v-col>
                <v-col class="text-center" cols="12" :lg="6"
                       v-if="isBuyer && !isFinal && (!archived || revision.x.approved_on)">
                  <v-btn @click="approveForm.submitThen(revision.updateX)" color="primary" variant="flat"
                         v-if="!revision.x.approved_on">
                    <v-icon left icon="mdi-check-circle"/>
                    Approve
                  </v-btn>
                  <span v-else-if="revision.x.approved_on">Approved on {{ formatDateTime(revision.x.approved_on) }}</span>
                </v-col>
                <v-col class="text-center" cols="6" lg="3" v-else-if="isSeller">
                  <v-btn icon small color="green" :href="revision.x.file.full" variant="flat" download aria-label="Download">
                    <v-icon icon="mdi-cloud-download"/>
                  </v-btn>
                </v-col>
                <v-col class="text-center" cols="6" lg="3" v-if="isSeller && isLast && !archived">
                  <v-btn icon small color="danger" class="delete-revision" @click="handleDelete"
                         aria-label="Delete Revision">
                    <v-icon icon="mdi-delete"/>
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
                    <v-icon icon="mdi-upload"/>
                    <span v-if="isSeller">View in Gallery</span><span v-else>View in Collection</span>
                  </v-btn>
                </v-col>
                <v-col class="text-center mb-2" cols="12" lg="12"
                       v-else-if="isSeller || (is(COMPLETED) && isRegistered)">
                  <v-btn color="green" block @click="prepSubmission" class="prep-submission-button" variant="elevated">
                    <v-icon icon="mdi-upload"/>
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

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcAsset from '@/components/AcAsset.vue'
import {SingleController} from '@/store/singles/controller.ts'
import Revision from '@/types/Revision.ts'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {ListController} from '@/store/lists/controller.ts'
import Deliverable from '@/types/Deliverable.ts'
import {markRead} from '@/lib/lib.ts'
import {User} from '@/store/profiles/types/User.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import Formatting from '@/mixins/formatting.ts'

@Component({
  components: {
    AcFormContainer,
    AcCommentSection,
    AcLoadSection,
    AcAsset,
  },
})
class RevisionDetail extends mixins(DeliverableMixin, Formatting) {
  @Prop()
  public revisionId!: string

  public revision!: SingleController<Revision>
  public revisionComments!: ListController<Comment>
  public approveForm!: FormController

  public get isLast() {
    if (!this.revision.x) {
      return false
    }
    const lastRevision = this.revisions.list[this.revisions.list.length - 1]
    if (!lastRevision) {
      return false
    }
    return (lastRevision.x as Revision).id === this.revision.x.id
  }

  public get backUrl() {
    return {
      name: `${this.baseName}DeliverableRevisions`,
      params: {
        deliverableId: this.deliverableId,
        orderId: this.orderId,
      },
    }
  }

  public get submissionMap(): { [key: number]: number } {
    /* istanbul ignore if */
    if (!this.revision.x) {
      return {}
    }
    const map: { [key: number]: number } = {}

    this.revision.x.submissions.map((entry) => {
      map[entry.owner_id] = entry.id
    }) // eslint-disable-line array-callback-return
    return map
  }

  public get isSubmitted() {
    return !!this.gallerySubmissionId
  }

  public get gallerySubmissionId() {
    const viewer = this.viewer as User
    /* istanbul ignore if */
    if (!this.revision.x) {
      return null
    }
    return this.submissionMap[viewer.id] || null
  }

  public get galleryLink() {
    if (!this.gallerySubmissionId) {
      return null
    }
    return {
      name: 'Submission',
      params: {submissionId: this.gallerySubmissionId + ''},
    }
  }

  public get isFinal() {
    const deliverable = this.deliverable.x as Deliverable
    return deliverable.final_uploaded && this.isLast
  }

  public prepSubmission() {
    this.addSubmission.fields.revision.update(this.revisionId)
    this.viewSettings.patchers.showAddSubmission.model = true
  }

  public handleDelete() {
    const revision = this.revision.x!
    this.revision.delete().then(() => {
      this.revisions.remove(revision)
      this.$router.replace(this.backUrl)
    })
  }

  created() {
    this.revision = this.$getSingle(`${this.prefix}__revision${this.revisionId}`, {
      endpoint: `${this.url}revisions/${this.revisionId}/`,
    })
    this.revision.get().then(
        () => markRead(this.revision, 'sales.Revision')).then(
        () => this.revisions.replace(this.revision.x as Revision),
    )
    this.approveForm = this.$getForm(`${this.prefix}__approve${this.revisionId}`, {
      endpoint: `${this.url}revisions/${this.revisionId}/approve/`,
      fields: {},
    })
    this.revisions.firstRun()
    this.revisionComments = this.$getList(`${this.prefix}__revision${this.deliverableId}__comments`, {
      endpoint: `/api/lib/comments/sales.Revision/${this.revisionId}/`,
      reverse: true,
      grow: true,
      params: {size: 5},
    })
    this.revisionComments.firstRun()
  }
}

export default toNative(RevisionDetail)
</script>
