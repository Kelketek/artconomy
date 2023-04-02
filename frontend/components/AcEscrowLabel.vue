<template>
  <v-row dense>
    <v-col cols="12" v-if="escrow" class="text-center">
      <v-icon large class="green--text">fa-shield</v-icon>
    </v-col>
    <v-col cols="12" v-else-if="!upgradeAvailable" class="text-center">
      <v-icon large class="yellow--text">warning</v-icon>
    </v-col>
    <v-col cols="12" v-else class="text-center">
      <v-icon large>fa-shield</v-icon>
    </v-col>
    <v-col class="text-center" cols="12" v-if="escrow">
      <p>
        This {{name}} protected by <br />
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-col>
    <v-col class="text-center" cols="12" v-else-if="!upgradeAvailable">
      <p>
        This {{name}} is not protected by <br />
        <router-link :to="{name: 'BuyAndSell', params: {question: 'shield'}}">
          Artconomy Shield.
        </router-link>
      </p>
    </v-col>
    <v-col class="text-center" v-else>
      This product offers Artconomy Shield protection as an upgrade.
    </v-col>
  </v-row>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'
import {Prop} from 'vue-property-decorator'

@Component
export default class AcEscrowLabel extends Vue {
  @Prop({required: true})
  public escrow!: boolean

  @Prop({default: false})
  public upgradeAvailable!: boolean

  @Prop({required: true})
  public name!: string
}
</script>
