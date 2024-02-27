<template>
  <ac-load-section :controller="deliverable" v-if="isRoute">
    <template v-slot:default>
      <ac-load-section :controller="characters">
        <template v-slot:default>
          <v-col cols="12" v-if="characters.list.length">
            <v-card-text>
              <ac-character-display :controller="characters" :editable="false"/>
            </v-card-text>
          </v-col>
        </template>
      </ac-load-section>
      <ac-load-section :controller="references">
        <template v-slot:default>
          <v-row class="pt-2">
            <v-col cols="6" sm="4" v-for="reference in references.list" :key="reference.x!.id">
              <ac-reference :reference="reference.x!.reference" :base-name="baseName"/>
            </v-col>
            <v-col cols="12" v-if="isBuyer || isSeller">
              <ac-form @submit.prevent="newReference.submitThen(addReference)">
                <ac-form-container v-bind="newReference.bind">
                  <v-row no-gutters align-content="center" justify="center">
                    <v-col cols="12">
                      <v-toolbar density="compact" color="black">
                        <v-toolbar-title>Upload Reference</v-toolbar-title>
                      </v-toolbar>
                    </v-col>
                    <v-col class="text-center" cols="12">
                      <ac-bound-field :field="newReference.fields.file" field-type="ac-uppy-file"
                                      uppy-id="new-reference-file"/>
                    </v-col>
                    <v-col class="text-center">
                      <v-card-text>
                        <p><strong>Upload additional reference images here!</strong> References help artists see what you
                          want them to create.</p>
                      </v-card-text>
                    </v-col>
                  </v-row>
                </ac-form-container>
              </ac-form>
            </v-col>
          </v-row>
        </template>
      </ac-load-section>
    </template>
  </ac-load-section>
  <router-view v-else></router-view>
</template>

<script lang="ts">
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import Reference from '@/types/Reference.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import AcReference from '@/components/views/order/deliverable/AcReference.vue'

@Component({
  components: {
    AcReference,
    AcUnreadMarker,
    AcLink,
    AcBoundField,
    AcFormContainer,
    AcForm,
    AcCharacterDisplay,
    AcLoadSection,
  },
})
class DeliverableReferences extends mixins(DeliverableMixin) {
  public newReference: FormController = null as unknown as FormController

  public get isRoute() {
    return this.$route.name === `${this.baseName}DeliverableReferences`
  }

  public addReference(reference: Reference) {
    this.references.post({reference_id: reference.id}).then(this.references.uniquePush)
  }

  @Watch('deliverable.x.rating')
  public setRating(val: number) {
    this.newReference.fields.rating.update(val)
  }

  @Watch('newReference.fields.file.value')
  public autoSubmit(val: string) {
    if (!val) {
      return
    }
    this.newReference.submitThen(this.addReference)
  }

  public created() {
    this.references.firstRun()
    /* istanbul ignore next */
    const deliverableRating = this.deliverable.x && this.deliverable.x.rating
    this.newReference = this.$getForm(
        'newReference', {
          endpoint: '/api/sales/references/',
          fields: {
            file: {value: ''},
            rating: {value: deliverableRating},
          },
        },
    )
  }
}

export default toNative(DeliverableReferences)
</script>
