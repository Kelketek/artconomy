<template>
  <v-container fluid>
    <v-row no-gutters>
      <v-col cols="12" style="position: relative">
        <v-btn icon absolute top left :to="backUrl" color="primary">
          <v-icon icon="mdi-arrow-back"/>
        </v-btn>
        <ac-load-section :controller="reference">
          <template v-slot:default>
            <ac-asset thumb-name="gallery" :asset="reference.x" :contain="true"/>
            <v-row v-if="reference.x!.owner === rawViewerName">
              <v-col class="text-center">
                <ac-confirmation :action="performDelete">
                  <template v-slot:default="{on}">
                    <v-btn color="red" v-on="on"  variant="flat">
                      <v-icon left icon="mdi-delete"/>
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
        :commentList="referenceComments"
        :nesting="false"
        :locked="!isInvolved || is(MISSED) || is(LIMBO)"
        :guest-ok="true"
        :show-history="isArbitrator"
        :extra-data="{deliverable: deliverableId}"
    />
  </v-container>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import AcAsset from '@/components/AcAsset.vue'
import {SingleController} from '@/store/singles/controller.ts'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCommentSection from '@/components/comments/AcCommentSection.vue'
import {ListController} from '@/store/lists/controller.ts'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import Reference from '@/types/Reference.ts'
import {markRead, updateLinked} from '@/lib/lib.ts'

@Component({
  components: {
    AcConfirmation,
    AcCommentSection,
    AcLoadSection,
    AcAsset,
  },
})
class referenceDetail extends mixins(DeliverableMixin) {
  @Prop()
  public referenceId!: string

  public reference!: SingleController<Reference>
  public referenceComments!: ListController<Comment>

  public get backUrl() {
    return {
      name: `${this.baseName}DeliverableReferences`,
      params: {
        deliverableId: this.deliverableId,
        orderId: this.orderId,
      },
    }
  }

  public async performDelete() {
    return this.reference.delete().then(() => {
      this.references.reset()
      this.$router.replace(this.backUrl)
    })
  }

  created() {
    this.reference = this.$getSingle(`${this.prefix}__reference${this.referenceId}`, {
      endpoint: `${this.url}references/${this.referenceId}/`,
    })
    this.reference.get().then(
        () => markRead(this.reference, 'sales.Reference')).then(
        () => updateLinked({
          list: this.references,
          key: 'reference',
          newValue: this.reference.x,
        }),
    )
    this.referenceComments = this.$getList(`${this.prefix}__reference${this.referenceId}__comments`, {
      endpoint: `/api/lib/comments/sales.Reference/${this.referenceId}/`,
      reverse: true,
      grow: true,
      params: {size: 5},
    })
    this.referenceComments.firstRun()
  }
}

export default toNative(referenceDetail)
</script>
