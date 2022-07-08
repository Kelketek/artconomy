<template>
  <v-row no-gutters>
    <v-col cols="12">
      <ac-gallery-preview class="pa-1" @click.capture.stop.prevent="() => false"
                          :linked="false"
                          :submission="submission.x" :show-footer="true"
                          :force-hidden="tag.x.hidden"
      />
    </v-col>
    <v-col cols="12">
      <v-btn color="primary" block @click="showSettings = true">
        Settings
      </v-btn>
      <ac-expanded-property v-model="showSettings" :large="true" :eager="false">
        <span slot="title">Edit Settings</span>
        <template v-slot:default>
          <v-col cols="12" v-if="!isOwner">
            <v-alert type="info">
              Some options are not available because you are not the submitter of this piece.
            </v-alert>
          </v-col>
          <v-row>
            <v-col cols="12" md="6">
              <ac-patch-field
                  field-type="v-checkbox"
                  label="Unlisted"
                  :persistent-hint="true"
                  hint="If checked, does not show this piece in your gallery.
              However, people with the link will still be able to view it. To nake it
              unviewable, make sure the 'private' setting is checked."
                  :patcher="tag.patchers.hidden"
              />
            </v-col>
            <v-col cols="12" md="6" class="text-center">
              <ac-confirmation :action="tag.delete">
                <template v-slot:default="confirmContext">
                  <v-btn color="danger" v-on="confirmContext.on">Untag me</v-btn>
                </template>
                <template v-slot:confirmation-text>
                  <p v-if="isOwner">
                    This piece will remain in your collection. You can retag it later.
                  </p>
                  <p v-else>
                    <strong>
                      This piece was submitted by someone else.
                      It may be difficult to find it and retag yourself again.
                    </strong>
                  </p>
                </template>
              </ac-confirmation>
              <p>Removes you as the tagged artist from this submission.</p>
            </v-col>
            <v-col cols="12" md="6">
              <ac-patch-field
                  field-type="v-checkbox"
                  label="Private"
                  :persistent-hint="true"
                  hint="If checked, this submission is hidden from view.
                  Only you and those you share it with will be able to see it."
                  :disabled="!isOwner"
                  :patcher="submission.patchers.private"
                  :save-indicator="isOwner"
              />
            </v-col>
            <v-col cols="12" md="6" class="text-center">
              <ac-confirmation :action="deleteSubmission">
                <template v-slot:default="confirmContext">
                  <v-btn color="danger" v-on="confirmContext.on" :disabled="!isOwner">Delete Submission</v-btn>
                </template>
              </ac-confirmation>
              <p>Deletes this submission.</p>
            </v-col>
            <v-col cols="12" class="text-center">
              <v-btn class="success" :to="{name: 'Submission', params: {submissionId: submission.x.id}}">Visit Submission</v-btn>
            </v-col>
          </v-row>
        </template>
      </ac-expanded-property>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Subjective from '@/mixins/subjective'
import Component, {mixins} from 'vue-class-component'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import {Prop} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import ArtistTag from '@/types/ArtistTag'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import Submission from '@/types/Submission'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
@Component({
  components: {AcConfirmation, AcPatchField, AcExpandedProperty, AcGalleryPreview},
})
export default class ArtistTagManager extends mixins(Subjective) {
  @Prop({required: true})
  public tag!: SingleController<ArtistTag>

  public submission = null as unknown as SingleController<Submission>

  public showSettings = false

  public get isOwner() {
    return this.username === this.submission.x?.owner.username
  }

  public deleteSubmission() {
    return this.submission.delete().then(() => { this.tag.deleted = true })
  }

  public created() {
    const submissionId = this.tag.x!.submission.id
    this.submission = this.$getSingle(
        `submission-${submissionId}`, {
          endpoint: `/api/profiles/v1/submission/${submissionId}/`,
          x: this.tag.x!.submission,
        },
    )
  }
}
</script>
