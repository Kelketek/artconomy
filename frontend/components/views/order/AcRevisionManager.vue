<template>
  <ac-load-section :controller="list" v-if="!order.x.revisions_hidden || isSeller">
    <v-row dense>
      <v-col cols="6" sm="4" v-for="(revision, index) in revisions" :key="revision.x.id" >
        <v-row dense>
          <v-col cols="12">
            <ac-asset :asset="revision.x" thumb-name="thumbnail" />
          </v-col>
          <v-col class="text-center" cols="6" lg="3">
            <v-btn fab small color="green" :href="revision.x.file.full" download><v-icon>cloud_download</v-icon></v-btn>
          </v-col>
          <v-col class="text-center" cols="6" lg="3" v-if="isSeller && (index + 1 === list.list.length) && !archived">
            <v-btn fab small color="danger" @click="revision.delete"><v-icon>delete</v-icon></v-btn>
          </v-col>
          <v-col class="text-center" cols="12" lg="6" v-if="isSeller && (index + 1 === list.list.length) && !archived">
            <v-btn color="primary" @click="$emit('finalize')">Mark Final</v-btn>
          </v-col>
        </v-row>
      </v-col>
      <v-col class="text-center" cols="12" v-if="final" >
        <ac-asset thumb-name="preview" :asset="final.x" :contain="true" />
        <v-row no-gutters   v-if="isSeller && !archived">
          <v-col cols="12">
            <v-btn icon color="success" :href="final.x.file.full" download><v-icon>cloud_download</v-icon></v-btn>
            <v-btn icon color="danger" @click="final.delete"><v-icon>delete</v-icon></v-btn>
            <v-btn color="primary" @click="$emit('reopen')">Unmark as Final</v-btn>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12" v-if="isSeller && !final && !archived">
        <ac-form @submit.prevent="newRevision.submitThen(()=>{})">
        <ac-form-container v-bind="newRevision.bind">
          <v-toolbar dense color="black"><v-toolbar-title>Upload Revision</v-toolbar-title></v-toolbar>
          <v-row no-gutters align-content="center" justify="center">
            <div class="shrink flex text-center">
              <ac-bound-field
                  :field="newRevision.fields.final"
                  field-type="v-checkbox"
                  label="This is the final version"
              />
            </div>
            <v-col class="text-center" cols="12">
              <ac-bound-field :field="newRevision.fields.file" field-type="ac-uppy-file" />
            </v-col>
            <v-col class="text-center">
              <v-card-text>
                <p>Upload your revisions here. Your customer will be notified when there is a new revision.</p>
                <p v-if="hidden"><strong>As the customer has not yet paid, they will not be able to see any revisions you have made.</strong></p>
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
      <v-col class="text-center" v-else-if="!final && !isSeller" >
        <p v-if="remainingRevisions && remainingRevisions > 0">The artist has promised <strong>{{remainingRevisions}}</strong> more revision and the final.</p>
        <p v-else-if="remainingRevisions <= 0"><strong>The artist has completed all promised revisions, but must still upload the final.</strong></p>
        <v-alert type="info" v-if="remainingRevisions < 0" :value="true">
          The artist has uploaded {{0 - remainingRevisions}} extra revision<span v-if="(0 - remainingRevisions >= 2)">s</span>.
        </v-alert>
      </v-col>
    </v-row>
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
import AcForm from '@/components/wrappers/AcForm.vue'
@Component({
  components: {AcForm, AcAsset, AcBoundField, AcFormContainer, AcLoadSection},
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
