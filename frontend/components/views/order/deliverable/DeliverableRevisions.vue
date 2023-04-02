<template>
  <ac-load-section :controller="deliverable">
    <template v-slot:default>
      <router-view></router-view>
      <v-container v-if="isPath">
        <ac-load-section :controller="revisions" v-if="!deliverable.x.revisions_hidden || isSeller">
          <template v-slot:default>
          <v-row dense>
            <v-col cols="12" v-if="isSeller && !final && !archived">
              <ac-form @submit.prevent="newRevision.submitThen(()=>{})">
                <ac-form-container v-bind="newRevision.bind">
                  <v-toolbar dense color="black"><v-toolbar-title>Upload Revision</v-toolbar-title></v-toolbar>
                  <v-row no-gutters align-content="center" justify="center">
                    <div class="shrink flex text-center">
                      <ac-bound-field
                        :field="newRevision.fields.final"
                        field-type="ac-checkbox"
                        label="This is the final version"
                      />
                    </div>
                    <v-col class="text-center" cols="12">
                      <ac-bound-field :field="newRevision.fields.file" field-type="ac-uppy-file" uppy-id="new-revision-file" />
                    </v-col>
                    <v-col class="text-center">
                      <v-card-text>
                        <p>Upload your revisions here. Your customer will be notified when there is a new revision.</p>
                        <p v-if="deliverable.x.revisions_hidden"><strong>As the customer has not yet paid, they will not be able to see any revisions you have made.</strong></p>
                        <p v-if="remainingRevisions > 0">You have promised <strong>{{remainingRevisions}}</strong> more revision and the final.</p>
                        <p v-else-if="remainingRevisions <= 0"><strong>You have completed all promised revisions, but must still upload the final.</strong></p>
                        <v-alert type="warning" v-if="remainingRevisions < 0" :value="true">
                          You have uploaded {{0 - remainingRevisions}} more revision<span v-if="(0 - remainingRevisions >= 2)">s</span> than you have promised. Please be sure you are not overextending yourself. It's OK to say 'No.' <v-icon>favorite</v-icon>
                        </v-alert>
                      </v-card-text>
                    </v-col>
                  </v-row>
                </ac-form-container>
              </ac-form>
            </v-col>
            <v-col class="text-center" v-else-if="!final && !isSeller" cols="12">
              <p v-if="remainingRevisions && remainingRevisions > 0">The artist has promised <strong>{{remainingRevisions}}</strong> more revision and the final.</p>
              <p v-else-if="remainingRevisions <= 0"><strong>The artist has completed all promised revisions, but must still upload the final.</strong></p>
              <v-alert type="info" v-if="remainingRevisions < 0" :value="true">
                The artist has uploaded {{0 - remainingRevisions}} extra revision<span v-if="(0 - remainingRevisions >= 2)">s</span>.
              </v-alert>
            </v-col>
            <v-col cols="6" sm="4" v-for="(revision, index) in revisions.list" :key="revision.x.id" >
              <v-row dense>
                <v-col cols="12">
                  <router-link :to="{name: `${baseName}DeliverableRevision`, params: {...$route.params, revisionId: revision.x.id}}">
                    <ac-unread-marker :read="revision.x.read" content-type="sales.Revision">
                      <ac-asset :asset="revision.x" thumb-name="thumbnail" />
                    </ac-unread-marker>
                  </router-link>
                </v-col>
                <v-col class="text-center" cols="12" v-if="deliverable.x.final_uploaded && (index === revisions.list.length - 1)">
                  <v-chip color="yellow" icon fab light>
                    <v-icon>star</v-icon>Final</v-chip>
                </v-col>
              </v-row>
            </v-col>
          </v-row>
          </template>
        </ac-load-section>
        <v-container v-else>
          <v-row>
            <v-col>
              <v-alert type="info" prominent>
                <v-row align="center">
                  <v-col class="grow">
                    Revisions are hidden until payment is received.
                  </v-col>
                  <v-col class="shrink">
                    <v-btn :to="{name: `${baseName}DeliverablePayment`, params: {...$route.params}}">Send Payment</v-btn>
                  </v-col>
                </v-row>
              </v-alert>
            </v-col>
          </v-row>
        </v-container>
        <v-row>
          <v-row class="text-center" v-if="isBuyer && is(REVIEW)">
            <v-col cols="12" sm="6" md="3" offset-md="3" class="text-center">
              <v-btn color="primary" @click="statusEndpoint('approve')()">Approve Final</v-btn>
            </v-col>
            <v-col cols="12" sm="6" md="3" class="text-center">
              <v-btn color="danger" @click="statusEndpoint('dispute')()">File Dispute</v-btn>
            </v-col>
          </v-row>
          <v-col class="text-center" cols="12" v-if="isBuyer && is(DISPUTED)" >
            <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
              If you are able to work out your disagreement with the artist, please approve the order using the
              button below.</p>
            <ac-confirmation :action="statusEndpoint('approve')">
              <template v-slot:default="{on}">
                <v-btn color="primary" v-on="on">Approve Final</v-btn>
              </template>
            </ac-confirmation>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import DeliverableMixin from '@/components/views/order/mixins/DeliverableMixin'
import {Watch} from 'vue-property-decorator'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcDeliverableRating from '@/components/views/order/AcDeliverableRating.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import AcAsset from '@/components/AcAsset.vue'
import {FormController} from '@/store/forms/form-controller'
import Revision from '@/types/Revision'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'

@Component({
  components: {
    AcUnreadMarker,
    AcAsset,
    AcBoundField,
    AcFormContainer,
    AcForm,
    AcDeliverableRating,
    AcConfirmation,
    AcLoadSection,
  },
})
export default class DeliverableRevisions extends mixins(DeliverableMixin) {
  public newRevision: FormController = null as unknown as FormController

  public get isPath() {
    return this.$route.name === `${this.baseName}DeliverableRevisions`
  }

  public get remainingRevisions() {
    /* istanbul ignore if */
    if (!this.revisions.ready) {
      return null
    }
    return this.revisionCount - this.revisions.list.length
  }

  public get final() {
    const deliverable = this.deliverable.x
    /* istanbul ignore if */
    if (!deliverable) {
      return null
    }
    if (!deliverable.final_uploaded) {
      return null
    }
    return this.revisions.list[this.revisions.list.length - 1]
  }

  @Watch('newRevision.fields.file.value')
  public autoSubmit(val: string) {
    if (!val) {
      return
    }
    this.newRevision.submitThen((response: Revision) => {
      this.revisions.uniquePush(response)
      this.$router.push({
        name: `${this.baseName}DeliverableRevision`,
        params: {...this.$route.params, revisionId: response.id + ''},
      })
      this.deliverable.refresh()
    })
  }

  @Watch('revisions.list.length')
  public refreshDeliverable(newVal: number, oldVal: number|undefined) {
    if (oldVal === undefined) {
      return
    }
    this.deliverable.refresh()
  }

  @Watch('deliverable.x.revisions_hidden')
  public fetchRevisions(newVal: boolean|undefined, oldVal: boolean|undefined) {
    if ((oldVal === true) && (newVal === false)) {
      this.revisions.get()
    }
  }

  public created() {
    this.newRevision = this.$getForm(
      'newRevision', {
        endpoint: this.revisions.endpoint,
        fields: {
          file: {value: ''},
          final: {value: false},
        },
      },
    )
  }
}
</script>
