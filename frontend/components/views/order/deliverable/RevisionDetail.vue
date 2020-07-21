<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="12" style="position: relative">
        <v-btn fab absolute top left :to="backUrl" color="primary"><v-icon>arrow_back</v-icon></v-btn>
        <ac-load-section :controller="revision">
          <template v-slot:default>
            <ac-asset thumb-name="gallery" :asset="revision.x" :contain="true" />
            <v-row>
              <v-col class="text-center" cols="12" :lg="(!escrow && isSeller) ? '6' : '12'" v-if="isBuyer || archived">
                <v-btn color="green" :href="revision.x.file.full" download><v-icon>cloud_download</v-icon>Download</v-btn>
              </v-col>
              <v-col class="text-center" cols="6" lg="3" v-else>
                <v-btn fab small color="green" :href="revision.x.file.full" download><v-icon>cloud_download</v-icon></v-btn>
              </v-col>
              <v-col class="text-center" cols="6" lg="3" v-if="isSeller && isLast && !archived">
                <v-btn fab small color="danger" @click="revision.delete().then(() => $router.replace(backUrl))"><v-icon>delete</v-icon></v-btn>
              </v-col>
              <v-col class="text-center" cols="12" lg="6" v-if="isSeller && isLast &&! isFinal && !archived">
                <v-btn color="primary" @click="statusEndpoint('complete')()">Mark Final</v-btn>
              </v-col>
              <v-col class="text-center" cols="12" lg="6" v-if="isSeller && isFinal && !(archived && escrow)">
                <v-btn color="primary" @click="statusEndpoint('reopen')()">Unmark Final</v-btn>
              </v-col>
            </v-row>
          </template>
        </ac-load-section>
      </v-col>
    </v-row>
    <ac-comment-section :commentList="revisionComments" :nesting="false" :locked="!isInvolved" :guest-ok="true" :show-history="isArbitrator" />
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcAsset from '@/components/AcAsset.vue'
import {SingleController} from '@/store/singles/controller'
import Revision from '@/types/Revision'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin'
import {Prop, Watch} from 'vue-property-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {ListController} from '@/store/lists/controller'
import Deliverable from '@/types/Deliverable'
import {markRead, updateLinked} from '@/lib/lib'

@Component({
  components: {AcCommentSection, AcLoadSection, AcAsset},
})
export default class RevisionDetail extends mixins(DeliverableMixin) {
  @Prop()
  public revisionId!: string

  public revision!: SingleController<Revision>
  public revisionComments!: ListController<Comment>

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
      params: {deliverableId: this.deliverableId, orderId: this.orderId},
    }
  }

  public get isFinal() {
    const deliverable = this.deliverable.x as Deliverable
    return deliverable.final_uploaded && this.isLast
  }

  created() {
    this.revision = this.$getSingle(`${this.prefix}__revision${this.revisionId}`, {
      endpoint: `${this.url}revisions/${this.revisionId}/`,
    })
    this.revision.get().then(
      () => markRead(this.revision, 'sales.Revision')).then(
      () => this.revisions.replace(this.revision.x as Revision),
    )
    this.revisions.firstRun()
    this.revisionComments = this.$getList(`${this.prefix}__revision${this.deliverableId}__comments`, {
      endpoint: `/api/lib/v1/comments/sales.Revision/${this.revisionId}/`,
      reverse: true,
      grow: true,
      pageSize: 5,
    })
    this.revisionComments.firstRun()
  }
}
</script>
