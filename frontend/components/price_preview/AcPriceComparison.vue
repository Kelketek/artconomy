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


<script>
import Subjective from '@/mixins/subjective'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import AcBoundField from '@/components/fields/AcBoundField'
import {toNative} from 'vue-facing-decorator'

export default {
  mixins: [toNative(Subjective)],
  components: {
    AcBoundField,
    AcPricePreview,
  },
  props: {
    username: {required: true},
    lineItemSetMaps: {required: true},
  },
  data() {
    return {
      hourlyForm: this.$getForm('hourly', {
        endpoint: '#',
        fields: {hours: {value: null}},
      }),
    }
  },
  computed: {
    mdSize() {
      if (this.lineItemSetMaps.length > 1) {
        return 6
      }
      return 12
    },
    offerExists() {
      return !!this.lineItemSetMaps.filter((item) => item.offer).length
    },
    lgSize() {
      if (this.lineItemSetMaps.length >= 3) {
        return 4
      } else if (this.lineItemSetMaps.length === 2) {
        return 6
      }
      return 12
    },
    single() {
      return this.lineItemSetMaps.length === 1
    },
  },
}
// This component, for some inexplicable reason, would not compile with the class-based invocation. It thus has the
// honor of being our first 'upgraded' component, though it's restricted to JS and the options API.
// @Component({
//   mixins: [Subjective],
//   components: {
//     AcBoundField,
//     AcPricePreview,
//   },
// })
// export default class extends Vue {
//   @Prop({required: true})
//   public lineItemSetMaps!: LineItemSetMap[]
//
//   public hourlyForm = null as unknown as FormController
//   public hours = null
//
//   public get mdSize() {
//     if (this.lineItemSetMaps.length > 1) {
//       return 6
//     }
//     return 12
//   }
//
//   public get offerExists() {
//     return !!this.lineItemSetMaps.filter((item) => item.offer).length
//   }
//
//   public get lgSize() {
//     if (this.lineItemSetMaps.length >= 3) {
//       return 4
//     } else if (this.lineItemSetMaps.length === 2) {
//       return 6
//     }
//     return 12
//   }
//
//   public get single() {
//     return this.lineItemSetMaps.length === 1
//   }
//
//   public created() {
//     this.hourlyForm = this.$getForm('hourly', {endpoint: '#', fields: {hours: {value: null}}})
//   }
// }
</script>
