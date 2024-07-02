<template>
  <v-container class="pa-0">
    <v-row>
      <v-col cols="12" :md="mdSize" :lg="lgSize" v-for="({name, lineItems, offer}) in lineItemSetMaps" :key="name">
        <v-card>
          <v-card-text>
            <v-card-title v-if="!single">{{name}}</v-card-title>
            <ac-price-preview :line-items="lineItems" :username="username" :hide-hourly-form="!single"/>
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
import SubjectiveProps from '@/types/SubjectiveProps.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {computed} from 'vue'
import {ListController} from '@/store/lists/controller.ts'
import LineItem from '@/types/LineItem.ts'

declare type LineItemSetMaps = { name: string, lineItems: ListController<LineItem> | undefined, offer: boolean}[]

const props = defineProps<{lineItemSetMaps: LineItemSetMaps} & SubjectiveProps>()
const hourlyForm = useForm('hourly', {endpoint: '#', fields: {hours: {value: null}}})
const mdSize = computed(() => props.lineItemSetMaps.length > 1 ? 6 : 12)
const offerExists = computed(() => !!props.lineItemSetMaps.filter((item) => item.offer).length)
const lgSize = computed(() => {
  if (props.lineItemSetMaps.length >= 3) {
    return 4
  } else if (props.lineItemSetMaps.length === 2) {
    return 6
  }
  return 12
})
const single = computed(() => {
  return props.lineItemSetMaps.length === 1
})
</script>
