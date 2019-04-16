<template>
  <ac-load-section :controller="list" v-if="!order.x.revisions_hidden || isSeller">
    <v-layout row wrap class="pt-2">
      <v-flex xs6 sm4 v-for="(revision, index) in revisions" :key="revision.x.id" pa-1 d-flex>
        <v-flex>
          <ac-asset :asset="revision.x" thumb-name="thumbnail"></ac-asset>
          <v-layout row wrap>
            <v-flex text-xs-center xs6 sm3>
              <v-btn icon color="green" :href="revision.x.file.full" download><v-icon>cloud_download</v-icon></v-btn>
            </v-flex>
            <v-flex text-xs-center xs6 sm3 v-if="isSeller && (index + 1 === list.list.length) && !archived">
              <v-btn icon color="danger" @click="revision.delete"><v-icon>delete</v-icon></v-btn>
            </v-flex>
            <v-flex text-xs-center xs12 sm6 v-if="isSeller && (index + 1 === list.list.length) && !archived">
              <v-btn color="primary" @click="$emit('finalize')">Mark as Final</v-btn>
            </v-flex>
          </v-layout>
        </v-flex>
      </v-flex>
      <v-flex xs12 v-if="final" text-xs-center>
        <ac-asset thumb-name="preview" :asset="final.x" :contain="true"></ac-asset>
        <v-layout row wrap v-if="isSeller && !archived">
          <v-flex xs12>
            <v-btn icon color="success" :href="final.x.file.full" download><v-icon>cloud_download</v-icon></v-btn>
            <v-btn icon color="danger" @click="final.delete"><v-icon>delete</v-icon></v-btn>
            <v-btn color="primary" @click="$emit('reopen')">Unmark as Final</v-btn>
          </v-flex>
        </v-layout>
      </v-flex>
      <v-flex xs12 v-if="isSeller && !final && !archived">
        <v-form>
        <ac-form-container :sending="newRevision.sending" :errors="newRevision.errors">
          <v-toolbar dense><v-toolbar-title>Upload Revision</v-toolbar-title></v-toolbar>
          <v-layout row align-center align-content-center justify-center column>
            <v-flex shrink text-xs-center align-self-center>
              <ac-bound-field
                  :field="newRevision.fields.final"
                  field-type="v-checkbox"
                  label="This is the final version"
              ></ac-bound-field>
            </v-flex>
            <v-flex text-xs-center>
              <ac-bound-field :field="newRevision.fields.file" field-type="ac-uppy-file"></ac-bound-field>
            </v-flex>
            <v-flex text-xs-center>
              <p>Upload your revisions here. Your customer will be notified when there is a new revision.</p>
              <p v-if="hidden"><strong>As the customer has not yet paid, they will not be able to see any revisions you have made.</strong></p>
              <p v-if="remainingRevisions > 0">You have promised <strong>{{remainingRevisions}}</strong> more revision and the final.</p>
              <p v-else-if="remainingRevisions <= 0"><strong>You have completed all promised revisions, but must still upload the final.</strong></p>
              <v-alert type="warning" v-if="remainingRevisions < 0" :value="true">
                You have uploaded {{0 - remainingRevisions}} more revision<span v-if="(0 - remainingRevisions >= 2)">s</span> than you have promised. Please be sure you are not overextending yourself. It's OK to say 'No.' <v-icon>favorite</v-icon>
              </v-alert>
            </v-flex>
          </v-layout>
        </ac-form-container>
        </v-form>
      </v-flex>
      <v-flex v-else-if="!final && !isSeller" text-xs-center>
        <p v-if="remainingRevisions && remainingRevisions > 0">The artist has promised <strong>{{remainingRevisions}}</strong> more revision and the final.</p>
        <p v-else-if="remainingRevisions <= 0"><strong>The artist has completed all promised revisions, but must still upload the final.</strong></p>
        <v-alert type="info" v-if="remainingRevisions < 0" :value="true">
          The artist has uploaded {{0 - remainingRevisions}} extra revision<span v-if="(0 - remainingRevisions >= 2)">s</span>.
        </v-alert>
      </v-flex>
    </v-layout>
  </ac-load-section>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop, Watch} from 'vue-property-decorator'
import {ListController} from '@/store/lists/controller'
import Revision from '@/types/Revision'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'
import AcAsset from '@/components/AcAsset.vue'
import {SingleController} from '@/store/singles/controller'
import Order from '@/types/Order'
@Component({
  components: {AcAsset, AcBoundField, AcFormContainer, AcLoadSection},
})
export default class AcRevisionManager extends Vue {
  @Prop({required: true})
  public list!: ListController<Revision>
  @Prop({required: true})
  public isSeller!: boolean
  @Prop({required: true})
  public hidden!: boolean
  @Prop({required: true})
  public order!: SingleController<Order>
  @Prop({required: true})
  public archived!: boolean
  @Prop({required: true})
  public revisionCount!: number
  public newRevision: FormController = null as unknown as FormController

  @Watch('newRevision.fields.file.value')
  public autoUpload(value: string) {
    if (!value) {
      return
    }
    this.newRevision.submitThen(this.list.uniquePush)
  }

  @Watch('list.list.length')
  public orderRefresh(newVal: number, oldVal: number) {
    /* istanbul ignore if */
    if (newVal === undefined) {
      return
    }
    this.order.refresh()
  }

  public get final() {
    const order = this.order.x
    /* istanbul ignore if */
    if (!order) {
      return null
    }
    if (!order.final_uploaded) {
      return null
    }
    return this.list.list[this.list.list.length - 1]
  }

  public get remainingRevisions() {
    /* istanbul ignore if */
    if (!this.list.ready) {
      return null
    }
    return this.revisionCount - this.list.list.length
  }

  public get revisions() {
    const order = this.order.x
    /* istanbul ignore if */
    if (!order) {
      return this.list.list
    }
    if (order.final_uploaded) {
      return this.list.list.slice(0, this.list.list.length - 1)
    }
    return this.list.list
  }

  public created() {
    this.newRevision = this.$getForm(
      'newRevision', {endpoint: this.list.endpoint, fields: {file: {value: ''}, final: {value: false}}},
    )
  }
}
</script>
