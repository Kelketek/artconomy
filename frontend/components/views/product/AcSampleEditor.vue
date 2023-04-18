<template>
  <fragment>
    <ac-new-submission v-if="firstUpload || newUpload" :username="username" @success="addSample" title="Upload a Sample" :value="value" @input="toggle" ref="newSubmissionForm" />
    <ac-expanded-property :value="value" :large="true" @input="toggle" class="sample-editor" ref="sampleEditor" v-else>
      <span slot="title">Change Samples</span>
      <template v-slot:default>
        <div class="stuff"></div>
        <v-row no-gutters  >
          <v-col cols="12">
            <v-tabs v-model="tab" centered>
              <v-tab href="#tab-pick-sample" class="pick-sample-tab">Manage Samples</v-tab>
              <v-tab href="#tab-add-new" class="add-new-tab">Add Sample</v-tab>
            </v-tabs>
          </v-col>
          <v-col cols="12">
            <v-tabs-items v-model="tab">
              <v-tab-item value="tab-pick-sample" eager>
                <ac-patch-field
                    field-type="ac-submission-select"
                    :patcher="product.patchers.primary_submission"
                    :list="localSamples"
                    :save-comparison="product.x.primary_submission"
                    :related="true"
                    :show-progress="true"
                    :removable="true"
                    @remove="unlinkSubmission"
                >
                </ac-patch-field>
              </v-tab-item>
              <v-tab-item value="tab-add-new" eager>
                <v-row no-gutters>
                  <v-col class="text-center" cols="12" >
                    <v-btn @click="newUpload = true" color="primary"><v-icon left>fa-upload</v-icon>Upload New Sample</v-btn>
                  </v-col>
                  <v-col class="text-center" cols="12" v-if="!art.empty" >
                    <p><strong>OR</strong></p>
                    <p>Select one of the pieces from your gallery below!</p>
                  </v-col>
                  <v-col cols="12" v-if="!art.empty">
                    <ac-paginated :list="art">
                      <v-col class="px-1" cols="6" sm="6" md="3" v-for="submission in art.list" :key="submission.id" @click.capture.stop.prevent="artToSample(submission.x)">
                        <ac-gallery-preview :submission="submission.x" class="product-sample-option" />
                      </v-col>
                    </ac-paginated>
                  </v-col>
                </v-row>
              </v-tab-item>
            </v-tabs-items>
          </v-col>
        </v-row>
      </template>
      <template v-slot:actions>
        <v-spacer />
        <v-btn color="danger" v-if="product.x.primary_submission" @click="product.patch({primary_submission: null})" class="clear-showcased">Clear Showcased Sample</v-btn>
        <v-btn color="primary" @click="toggle(false)" v-if="$vuetify.breakpoint.mdAndUp">Done</v-btn>
        <v-spacer v-if="$vuetify.breakpoint.smAndDown" />
      </template>
    </ac-expanded-property>
  </fragment>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import Subjective from '@/mixins/subjective'
import {Prop, Watch} from 'vue-property-decorator'
import {SingleController} from '@/store/singles/controller'
import Product from '@/types/Product'
import {ListController} from '@/store/lists/controller'
import {Fragment} from 'vue-frag'
import AcNewSubmission from '@/components/AcNewSubmission.vue'
import {flatten, newUploadSchema} from '@/lib/lib'
import {FormController} from '@/store/forms/form-controller'
import Submission from '@/types/Submission'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import LinkedSubmission from '@/types/LinkedSubmission'

  @Component({
    components: {
      AcLoadSection,
      AcGalleryPreview,
      AcPaginated,
      AcNewSubmission,
      AcPatchField,
      AcExpandedProperty,
      Fragment,
    },
  })
export default class AcSampleEditor extends mixins(Subjective) {
    @Prop({required: true})
    public product!: SingleController<Product>

    @Prop({required: true})
    public samples!: ListController<LinkedSubmission>

    @Prop({required: true})
    public value!: boolean

    @Prop({required: true})
    public productId!: number

    public art: ListController<Submission> = null as unknown as ListController<Submission>
    public localSamples: ListController<LinkedSubmission> = null as unknown as ListController<LinkedSubmission>
    public newSubmission: FormController = null as unknown as FormController
    public tab = 'tab-pick-sample'
    public newUpload = false

    // These two functions reference the new submission form, which is not playing nicely with other test suites, and
    // it's not clear why.
    /* istanbul ignore next */
    @Watch('value', {immediate: true})
    public uploadToggle(value: boolean) {
      if (!value) {
        this.newUpload = false
        return
      }
      this.$nextTick(() => {
        if (this.$refs.newSubmissionForm) {
          (this.$refs.newSubmissionForm as any).isArtist = true
        }
      })
    }

    /* istanbul ignore next */
    @Watch('newUpload', {immediate: true})
    public ensureArtist(value: boolean) {
      if (value) {
        this.$nextTick(() => {
          if (this.$refs.newSubmissionForm) {
            (this.$refs.newSubmissionForm as any).isArtist = true
          }
        })
      }
    }

    public get firstUpload() {
      const product = this.product.x as Product
      return (!product.primary_submission) && this.samples.empty && this.art.empty
    }

    public toggle(value: boolean) {
      this.$emit('input', value)
    }

    public artToSample(value: Submission) {
      this.localSamples.post({submission_id: value.id}).then((result: any) => {
        this.localSamples.uniquePush(result)
        this.samples.uniquePush(result)
        this.tab = 'tab-pick-sample'
        if (!(this.product.x as Product).primary_submission) {
          this.product.patch({primary_submission: result.submission.id})
        }
      })
    }

    public addSample(value: Submission) {
      this.art.uniquePush(value)
      this.localSamples.post({submission_id: value.id}).then((result: any) => {
        this.localSamples.push(result)
        this.samples.push(result)
      })
      this.tab = 'tab-pick-sample'
      this.newSubmission.reset()
      this.newUpload = false
      // @ts-ignore
      if (this.product.x.primary_submission) {
        return
      }
      // @ts-ignore
      this.product.patch({primary_submission: value.id})
    }

    public unlinkSubmission(submission: SingleController<any>) {
      const oldValue = submission.x
      const id = submission.x.submission.id
      submission.delete().then(() => {
        const existingPrimary = (this.product.x as Product).primary_submission
        // @ts-ignore
        if (existingPrimary && existingPrimary.id === id) {
          this.product.updateX({primary_submission: null})
        }
        this.samples.remove(oldValue)
        this.localSamples.remove(oldValue)
      })
    }

    public created() {
      this.localSamples = this.$getList(
        // We don't want to use the outer scope's sample list because it will paginate separately.
        `product-${this.productId}-sample-select`, {endpoint: this.product.endpoint + 'samples/'},
      )
      this.localSamples.firstRun().then(() => {
        if (this.localSamples.empty) {
          this.tab = 'tab-add-new'
        }
      })
      this.newSubmission = this.$getForm(`${flatten(this.username)}-newSubmission`, newUploadSchema(this.subjectHandler.user))
      this.art = this.$getList(`${flatten(this.username)}-art`, {
        endpoint: `/api/profiles/account/${this.username}/submissions/sample-options/`,
      })
      this.art.firstRun().catch(() => {})
    }
}
</script>
