<template>
  <ac-load-section
    v-if="isRoute"
    :controller="deliverable"
  >
    <template #default>
      <ac-load-section :controller="characters">
        <template #default>
          <v-col
            v-if="characters.list.length"
            cols="12"
          >
            <v-card-text>
              <ac-character-display
                :controller="characters"
                :editable="false"
              />
            </v-card-text>
          </v-col>
        </template>
      </ac-load-section>
      <ac-load-section :controller="references">
        <template #default>
          <v-row class="pt-2">
            <v-col
              v-for="reference in references.list"
              :key="reference.x!.id"
              cols="6"
              sm="4"
            >
              <ac-reference
                :reference="reference.x!.reference"
                :base-name="baseName"
              />
            </v-col>
            <v-col
              v-if="isBuyer || isSeller"
              cols="12"
            >
              <ac-form @submit.prevent="newReference.submitThen(addReference)">
                <ac-form-container v-bind="newReference.bind">
                  <v-row
                    no-gutters
                    align-content="center"
                    justify="center"
                  >
                    <v-col cols="12">
                      <v-toolbar
                        density="compact"
                        color="black"
                      >
                        <v-toolbar-title>Upload Reference</v-toolbar-title>
                      </v-toolbar>
                    </v-col>
                    <v-col
                      class="text-center"
                      cols="12"
                    >
                      <ac-bound-field
                        :field="newReference.fields.file"
                        field-type="ac-uppy-file"
                        uppy-id="new-reference-file"
                      />
                    </v-col>
                    <v-col class="text-center">
                      <v-card-text>
                        <p>
                          <strong>Upload additional reference images here!</strong> References help artists see what you
                          want them to create.
                        </p>
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
  <router-view v-else />
</template>

<script setup lang="ts">
import {DeliverableProps, useDeliverable} from '@/components/views/order/mixins/DeliverableMixin.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcCharacterDisplay from '@/components/views/submission/AcCharacterDisplay.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import AcReference from '@/components/views/order/deliverable/AcReference.vue'
import {useForm} from '@/store/forms/hooks.ts'
import {computed, watch} from 'vue'
import {useRoute} from 'vue-router'
import type {RatingsValue, Reference} from '@/types/main'

const props = defineProps<DeliverableProps>()
const route = useRoute()
const {deliverable, references, characters, isBuyer, isSeller} = useDeliverable(props)
references.firstRun()

const isRoute = computed(() => {
  return route.name === `${props.baseName}DeliverableReferences`
})

/* istanbul ignore next */
const deliverableRating = deliverable.x && deliverable.x.rating
const newReference = useForm(
    'newReference', {
      endpoint: '/api/sales/references/',
      fields: {
        file: {value: ''},
        rating: {value: deliverableRating},
      },
    },
)

const addReference = (reference: Reference) => {
  references.post({reference_id: reference.id}).then(references.uniquePush)
}

watch(() => deliverable.x?.rating, (val: RatingsValue|undefined) => {
  if (val === undefined) {
    return
  }
  newReference.fields.rating.update(val)
})

watch(() => newReference.fields.file.value, (val: string) => {
  if (!val) {
    return
  }
  newReference.submitThen(addReference)
})
</script>
