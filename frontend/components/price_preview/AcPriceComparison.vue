<template>
  <v-container class="pa-0">
    <v-row>
      <v-col cols="12" v-if="props.lineItemSetMaps.length > 1">
        <ac-tabs label="Compare offer" v-model="computedTab" :items="tabs" />
      </v-col>
      <v-col cols="12">
        <v-window v-model="computedTab">
          <v-window-item v-for="({name, lineItems, offer}, index) in lineItemSetMaps" :key="name" :value="index">
            <v-card>
              <v-card-text>
                <ac-price-preview :line-items="lineItems" :username="username" :hide-hourly-form="!single" :is-seller="true"/>
                <v-row no-gutters>
                  <v-col cols="12" class="text-center" v-if="offerExists">
                    <v-btn
                        :disabled="!offer" :style="`opacity: ${offer ? 1 : 0}`"
                        color="green"
                        variant="flat"
                        :to="{name: 'Upgrade', params: {username}}"
                        :aria-hidden="`${offer ? 'true' : 'false'}`">Upgrade
                    </v-btn>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-window-item>
        </v-window>
      </v-col>
    </v-row>
    <v-row>
      <v-col cols="12" v-if="!single">
        <v-card>
          <v-card-text>
            <ac-bound-field :field="hourlyForm.fields.hours" type="number" label="If I worked for this many hours..."
                            min="0" step="1"/>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>

</style>


<script setup lang="ts">
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {computed, ComputedRef, ref} from 'vue'
import {ListController} from '@/store/lists/controller.ts'

import type {LineItem, SubjectiveProps, TabSpec} from '@/types/main'
import AcTabs from '@/components/navigation/AcTabs.vue'

declare type LineItemSetMaps = { name: string, lineItems: ListController<LineItem>, offer: boolean}[]

const props = defineProps<{lineItemSetMaps: LineItemSetMaps} & SubjectiveProps>()
const hourlyForm = useForm('hourly', {endpoint: '#', fields: {hours: {value: null}}})
const offerExists = computed(() => !!props.lineItemSetMaps.filter((item) => item.offer).length)
const selectedTab = ref(0)
const computedTab = computed({
  get: () => {
    const maximum = props.lineItemSetMaps.length - 1
    if (selectedTab.value > maximum) {
      return maximum
    }
    return selectedTab.value
  },
  set: (value) => {
    selectedTab.value = value
  }
})
const tabs: ComputedRef<TabSpec[]> = computed(() => {
  return props.lineItemSetMaps.map((entry, index) => ({value: index, title: entry.name}))
})
const single = computed(() => {
  return props.lineItemSetMaps.length === 1
})
</script>
