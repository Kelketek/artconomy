<template>
  <ac-load-section :controller="artistProfile">
    <template v-slot:default>
      <v-card>
        <v-card-text>
          <v-container fluid class="py-0">
            <v-list-subheader>
              <strong>
                Workload
              </strong>
            </v-list-subheader>
            <v-row class="pb-4">
              <v-col cols="12" sm="6" md="3">
                <ac-patch-field
                    label="Commissions Closed"
                    field-type="v-switch"
                    hint="When on, delists all of your products, and only allows orders you've specifically
                          invoiced."
                    :persistent-hint="true"
                    :save-indicator="false"
                    color="primary"
                    :patcher="subjectHandler.artistProfile.patchers.commissions_closed"
                />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <ac-patch-field
                    label="Auto Withdraw"
                    field-type="v-switch"
                    hint="Automatically withdraws all funds you receive from commissions. You might turn this off if
                          you're switching banks."
                    :patcher="artistProfile.patchers.auto_withdraw"
                    :save-indicator="false"
                    color="primary"
                    :persistent-hint="true" />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <ac-patch-field
                    label="Public Queue"
                    field-type="v-switch"
                    hint="Allows people to see what orders you're currently working on."
                    :patcher="artistProfile.patchers.public_queue"
                    :save-indicator="false"
                    color="primary"
                    :persistent-hint="true" />
              </v-col>
              <v-col cols="12" sm="6" md="3">
                <v-row no-gutters>
                  <v-col cols="12">
                    <ac-patch-field
                        field-type="v-slider"
                        label="Slots"
                        :patcher="artistProfile.patchers.max_load"
                        :min="1"
                        step="1"
                        :max="100"
                    />
                  </v-col>
                  <v-col cols="12">
                    <div class="v-messages mb-1">
                      <div class="v-messages__message">Commissions are automatically closed when you've filled up your
                        slots.
                        You can customize an order to take multiple slots if it is especially big.
                      </div>
                    </div>
                  </v-col>
                  <v-col cols="12">
                    <ac-patch-field
                        :patcher="artistProfile.patchers.max_load"
                        class="mt-0"
                        hide-details
                        single-line
                        type="number"
                        :save-indicator="false"
                        step="1"
                    />
                  </v-col>
                </v-row>
              </v-col>
              <v-col></v-col>
            </v-row>
          </v-container>
          <v-row no-gutters>
            <v-col class="py-4" cols="12">
              <v-divider></v-divider>
            </v-col>
            <v-col cols="12">
              <ac-patch-field
                  field-type="ac-editor"
                  :patcher="artistProfile.patchers.commission_info"
                  label="Commission Info"
                  :persistent-hint="true"
                  :counter="5000"
                  hint="This information will be shown on all of your product pages. It could contain terms of service or
                  other information used to set expectations with your clients."
              >
              </ac-patch-field>
            </v-col>
          </v-row>
          <v-container>
            <v-row no-gutters>
              <v-col class="py-4" cols="12">
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <v-list-subheader>
                  <strong>I am/identify as...</strong>
                </v-list-subheader>
              </v-col>
              <v-col cols="12" sm="6">
                <ac-patch-field
                    :patcher="artistProfile.patchers.artist_of_color"
                    field-type="ac-checkbox"
                    :save-indicator="false"
                    label="An Artist of Color"
                />
              </v-col>
              <v-col cols="12" sm="6">
                <ac-patch-field
                    :patcher="artistProfile.patchers.lgbt"
                    field-type="ac-checkbox"
                    :save-indicator="false"
                    label="A member of the LGBTQ+ community"
                />
              </v-col>
              <v-col cols="12">
                <strong>...and would like to be featured in the relevant community sections.</strong>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </template>
  </ac-load-section>
</template>

<script setup lang="ts">
import {useSubject} from '@/mixins/subjective.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

import type {SubjectiveProps} from '@/types/main'

const props = defineProps<SubjectiveProps>()

const {subjectHandler} = useSubject({ props })

const artistProfile = subjectHandler.artistProfile
artistProfile.get().then()
</script>
