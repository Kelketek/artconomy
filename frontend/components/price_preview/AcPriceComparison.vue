<template>
  <v-container class="pa-0">
    <v-row>
      <v-col cols="12" :md="mdSize" :lg="lgSize" v-for="({name, lineItems, offer}) in lineItemSetMaps" :key="name">
        <v-card>
          <v-card-text>
            <v-card-title v-if="!single">{{name}}</v-card-title>
            <ac-price-preview :line-items="lineItems" :username="username" :hide-hourly-form="!single" />
            <v-row no-gutters>
              <v-col cols="12" class="text-center" v-if="offerExists">
                <v-btn
                    :disabled="!offer" :style="`opacity: ${offer ? 1 : 0}`"
                    color="green"
                    :to="{name: 'Upgrade', params: {username}}"
                    :aria-hidden="`${offer ? 'true' : 'false'}`">Upgrade</v-btn>
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
            <ac-bound-field :field="hourlyForm.fields.hours" type="number" label="If I worked for this many hours..." min="0" step="1" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {Prop} from 'vue-property-decorator'
import Subjective from '@/mixins/subjective'
import {LineItemSetMap} from '@/types/LineItemSetMap'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import {FormController} from '@/store/forms/form-controller'
import AcBoundField from '@/components/fields/AcBoundField'

@Component({
  components: {
    AcBoundField,
    AcPricePreview,
  },
})
export default class extends mixins(Subjective) {
  @Prop({required: true})
  public lineItemSetMaps!: LineItemSetMap[]

  public hourlyForm = null as unknown as FormController
  public hours = null

  public get mdSize() {
    if (this.lineItemSetMaps.length > 1) {
      return 6
    }
    return 12
  }

  public get offerExists() {
    return !!this.lineItemSetMaps.filter((item) => item.offer).length
  }

  public get lgSize() {
    if (this.lineItemSetMaps.length >= 3) {
      return 4
    } else if (this.lineItemSetMaps.length === 2) {
      return 6
    }
    return 12
  }

  public get single() {
    return this.lineItemSetMaps.length === 1
  }

  public created() {
    this.hourlyForm = this.$getForm('hourly', {endpoint: '#', fields: {hours: {value: null}}})
  }
}
</script>

<style scoped>

</style>
