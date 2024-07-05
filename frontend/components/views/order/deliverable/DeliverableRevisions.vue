<template>
  <ac-load-section :controller="deliverable">
    <template v-slot:default>
      <router-view></router-view>
      <v-container v-if="isPath && deliverable.x">
        <ac-load-section :controller="revisions" v-if="!deliverable.x.revisions_hidden || isSeller">
          <template v-slot:default>
            <v-row v-if="isSeller && !final && !archived">
              <ac-form-dialog v-model="showNew" :large="true"
                              @submit.prevent="newRevision.submitThen(postSubmit)"
                              v-bind="newRevision.bind"
                              class="submission-uploader"
                              v-if="isRegistered" title="Upload New Revision"
              >
                <v-row>
                  <v-col class="text-center" cols="12">
                    <ac-bound-field :field="newRevision.fields.file" field-type="ac-uppy-file"
                                    uppy-id="new-revision-file"/>
                  </v-col>
                  <v-col cols="12">
                    <ac-bound-field :field="newRevision.fields.text" field-type="ac-editor"
                                    label="Comment (Optional)"
                                    :save-indicator="false"
                                    />
                  </v-col>
                  <v-col cols="12" class="text-center d-flex justify-center">
                    <div class="shrink flex text-center align-self-center">
                      <ac-bound-field
                          :field="newRevision.fields.final"
                          field-type="ac-checkbox"
                          label="This is the final version"
                      />
                    </div>
                  </v-col>
                </v-row>
              </ac-form-dialog>
              <v-col cols="12">
                <v-card-text class="text-center">
                  <p>Upload your revisions here. Your customer will be notified when there is a new
                    revision.</p>
                  <p v-if="deliverable.x.revisions_hidden"><strong>As the customer has not yet paid, they will
                    not be able to see any revisions you have made.</strong></p>
                  <p v-if="remainingRevisions > 0">You have promised <strong>{{ remainingRevisions }}</strong>
                    more revision and the final.</p>
                  <p v-else-if="remainingRevisions <= 0"><strong>You have completed all promised revisions, but
                    must still upload the final.</strong></p>
                  <v-alert type="warning" v-if="remainingRevisions < 0" :value="true">
                    You have uploaded {{ 0 - remainingRevisions }} more revision<span
                      v-if="(0 - remainingRevisions >= 2)">s</span> than you have promised. Please be sure you
                    are not overextending yourself. It's OK to say 'No.'
                    <v-icon :icon="mdiHeart"/>
                  </v-alert>
                </v-card-text>
              </v-col>
              <v-col cols="12" class="text-center">
                <v-btn color="green" @click="showNew = true">
                  <v-icon left :icon="mdiPlus" />
                  Upload Revision/WIP
                </v-btn>
              </v-col>
            </v-row>
            <v-row class="text-center" v-else-if="!final && !isSeller">
              <v-col cols="12">
                <p v-if="remainingRevisions && remainingRevisions > 0">The artist has promised
                  <strong>{{ remainingRevisions }}</strong> more revision and the final.</p>
                <p v-else-if="remainingRevisions <= 0"><strong>The artist has completed all promised revisions, but must
                  still upload the final.</strong></p>
                <v-alert type="info" v-if="remainingRevisions < 0" :value="true">
                  The artist has uploaded {{ 0 - remainingRevisions }} extra revision<span
                    v-if="(0 - remainingRevisions >= 2)">s</span>.
                </v-alert>
              </v-col>
            </v-row>
            <v-row>
              <v-col cols="6" sm="4" v-for="(revision, index) in revisions.list" :key="revision.x!.id">
                <v-row dense>
                  <v-col cols="12">
                    <router-link
                        :to="{name: `${baseName}DeliverableRevision`, params: {...route.params, revisionId: revision.x!.id}}">
                      <ac-unread-marker :read="revision.x!.read" content-type="sales.Revision">
                        <ac-asset :asset="revision.x" thumb-name="thumbnail" :alt="`Revision #${index} for order.`"/>
                      </ac-unread-marker>
                    </router-link>
                  </v-col>
                  <v-col class="text-center" cols="12"
                         v-if="deliverable.x.final_uploaded && (index === revisions.list.length - 1)">
                    <v-chip color="yellow" icon light>
                      <v-icon :icon="mdiStar"/>
                      Final
                    </v-chip>
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
                </v-row>
                <template v-slot:append>
                  <v-btn :to="{name: `${baseName}DeliverablePayment`, params: {...route.params}}" variant="flat">
                    Send Payment
                  </v-btn>
                </template>
              </v-alert>
            </v-col>
          </v-row>
        </v-container>
        <v-row>
          <v-col cols="12" v-if="isBuyer && is(DeliverableStatus.REVIEW)">
            <v-row class="text-center">
              <v-col cols="12" sm="6" md="3" offset-md="3" class="text-center">
                <v-btn color="primary" @click="statusEndpoint('approve')()" variant="flat">Approve Final</v-btn>
              </v-col>
              <v-col cols="12" sm="6" md="3" class="text-center">
                <v-btn color="danger" @click="statusEndpoint('dispute')()" variant="flat">File Dispute</v-btn>
              </v-col>
            </v-row>
          </v-col>
          <v-col class="text-center" cols="12" v-if="isBuyer && is(DeliverableStatus.DISPUTED)">
            <p><strong>Your dispute has been filed.</strong> Please stand by for further instructions.
              If you are able to work out your disagreement with the artist, please approve the order using the
              button below.</p>
            <ac-confirmation :action="statusEndpoint('approve')">
              <template v-slot:default="{on}">
                <v-btn color="primary" v-on="on" variant="flat">Approve Final</v-btn>
              </template>
            </ac-confirmation>
          </v-col>
        </v-row>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {DeliverableProps, useDeliverable} from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcAsset from '@/components/AcAsset.vue'
import Revision from '@/types/Revision.ts'
import AcUnreadMarker from '@/components/AcUnreadMarker.vue'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {mdiHeart, mdiPlus, mdiStar} from '@mdi/js'
import {useForm} from '@/store/forms/hooks.ts'
import {computed, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {DeliverableStatus} from '@/types/DeliverableStatus.ts'
import {useViewer} from '@/mixins/viewer.ts'

const props = defineProps<DeliverableProps>()

const {isRegistered} = useViewer()

const {deliverable, revisions, revisionCount, statusEndpoint, isBuyer, is, isSeller, archived} = useDeliverable(props)

const showNew = ref(false)

const route = useRoute()
const router = useRouter()

const isPath = computed(() => {
  return route.name === `${props.baseName}DeliverableRevisions`
})

const newRevision = useForm(
    'newRevision', {
      endpoint: revisions.endpoint,
      fields: {
        file: {value: ''},
        final: {value: false},
        text: {value: ''}
      },
    },
)

const remainingRevisions = computed(() => {
  /* istanbul ignore if */
  if (!revisions.ready) {
    return 0
  }
  return revisionCount.value - revisions.list.length
})

const final = computed(() => {
  /* istanbul ignore if */
  if (!deliverable.x) {
    return null
  }
  if (!deliverable.x.final_uploaded) {
    return null
  }
  return revisions.list[revisions.list.length - 1]
})

const postSubmit = (response: Revision) => {
  revisions.uniquePush(response)
  router.push({
    name: `${props.baseName}DeliverableRevision`,
    params: {
      ...route.params,
      revisionId: response.id + '',
    },
  })
}

watch(() => revisions.list.length, (newVal: number, oldVal: number | null | undefined) => {
  if ([undefined, null].indexOf(oldVal as null) !== -1) {
    return
  }
  deliverable.refresh()
})

watch(() => deliverable.x?.revisions_hidden, (newVal: boolean | undefined, oldVal: boolean | undefined) => {
  if ((oldVal === true) && (newVal === false)) {
    revisions.get()
  }}
)
</script>
